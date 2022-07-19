import argparse
import numpy as np
import sys
import pandas as pd
sys.setrecursionlimit(20000)


def web_classification(n_data, n_random):
    assert len(n_data) == len(n_random)
    n_points = len(n_data)
    r_values = (n_data-n_random)/(n_data+n_random)
    web_class = np.zeros(n_points, dtype=int)
    lower_limit = -0.90
    upper_limit = 0.90
    is_void = r_values <= lower_limit
    is_sheet = (r_values > lower_limit) & (r_values<=0.0)
    is_filament = (r_values>0.0) & (r_values <= upper_limit)
    is_peak = (r_values > upper_limit)
    web_class[is_void] = 0
    web_class[is_sheet] = 1
    web_class[is_filament] = 2
    web_class[is_peak] = 3
    return web_class  

def find_friends(first_id, all_ids, pair_ids, included_ids):
    group = []
    #print(first_id) 
    #print(all_ids)
    loc = np.where(all_ids==first_id)[0][0]
    #print('firstid', first_id, 'loc', loc)
    if included_ids[loc] == 1: # caso base, el punto ya esta incluido
        return group
    else:
        # si no esta incluido, lo incluyo
        group.append(first_id)
        included_ids[loc] = 1
    
        # ahora busco los amigos
        friends = []
        friends += list(pair_ids[pair_ids[:,0]==first_id,1])
        friends += list(pair_ids[pair_ids[:,1]==first_id,0])
        #print('friends', friends)
        for friend in friends:
            group.append(friend)
            group.extend(find_friends(friend, all_ids, pair_ids, included_ids))
    
        group = list(set(group))
        group.sort()
        return group
    
def find_fof_groups(pairs):
    pairs = np.int_(pairs)
    #print(pairs)
    groups = {}
    group_id = 0
    all_ids = list(np.sort(np.unique(pairs.flatten())))
    n_points = len(all_ids)
    #print(n_points)
    print('points to be grouped',n_points)
    included_ids = list(np.zeros(n_points, dtype=int))

    n_total = 0
    for first_id in all_ids:
        fof_ids = find_friends(first_id, all_ids, pairs, included_ids)
        if len(fof_ids):
            #if len(fof_ids)>8:
            #    print(first_id, len(fof_ids))
            n_total += len(fof_ids)
            groups[group_id] = fof_ids
            group_id += 1
            
    # sanity check
    assert n_total == n_points
    return groups

def inertia_tensor(x, y, z):
    r = np.sqrt(x**2 + y**2 + z**2)
    I = np.ones((3,3))
    
    I[0,0] = np.sum(r**2 - x*x)
    I[1,1] = np.sum(r**2 - y*y)
    I[2,2] = np.sum(r**2 - z*z)
    
    I[0,1] = -np.sum(x*y)
    I[1,0] = I[0,1]
    
    I[0,2] = -np.sum(x*z)
    I[2,0] = I[0,2]
    
    I[1,2] = -np.sum(y*z)
    I[2,1] = I[1,2]
    
    values, vectors = np.linalg.eig(I)
    ii = np.argsort(-values)
    #print(values[ii])
    return np.sqrt(values[ii]), vectors[:,ii]

def compute_group_properties(groups, positions):
    props = {}
    props['N'] = []
    props['MEAN_X'] = []; props['MEAN_Y'] = []; props['MEAN_Z'] = []
    props['SIGMA_X'] = []; props['SIGMA_Y'] = []; props['SIGMA_Z'] = []
    props['SIGMA_R'] = []
    props['LAMBDA_1'] = []; props['LAMBDA_2'] = []; props['LAMBDA_3'] = []
    props['EIGEN_1'] = []; props['EIGEN_2'] = []; props['EIGEN_3'] = []
    
    for i in groups.keys():
        x = positions[groups[i],0]
        y = positions[groups[i],1]
        z = positions[groups[i],2]
        r = np.sqrt(x**2 + y**2 + z**2)
        
        props['N'].append(len(groups[i]))
        props['SIGMA_R'].append(np.std(r))
        props['MEAN_X'].append(np.mean(x))
        props['MEAN_Y'].append(np.mean(y))
        props['MEAN_Z'].append(np.mean(z))
        props['SIGMA_X'].append(np.std(x))
        props['SIGMA_Y'].append(np.std(y))
        props['SIGMA_Z'].append(np.std(z))        

        values, vectors = inertia_tensor(x,y,z)
        props['LAMBDA_1'].append(values[0])
        props['LAMBDA_2'].append(values[1])
        props['LAMBDA_3'].append(values[2])
        props['EIGEN_1'].append(vectors[:,0])
        props['EIGEN_2'].append(vectors[:,1])
        props['EIGEN_3'].append(vectors[:,2])

    return props

def make_catalog(posfile, pairfile, countfile, catalogfile, webtype):
    extension = pairfile[-4:]
    webfile = pairfile.replace('_pairs'+extension, '_nconnections'+extension)
    print(webfile)
    
    web_types = {"void":0, "sheet":1, "filament":2, "peak":3}
    web_type_id = web_types[webtype]

    pos = np.loadtxt(posfile)
    pos = pos[:,0:3]
    pairs = np.loadtxt(pairfile)
    counts = np.loadtxt(countfile)
    
    web = web_classification(counts[:,0], counts[:,1])
    
    #web = np.loadtxt(webfile)
    
    n_points = len(pos)
    
    print(np.shape(pos))
    print(np.shape(pairs), type(pairs))
    print(np.shape(web))

    # sanity checks
    assert len(pos) == len(web)
    assert pairs.max() < len(pos)
    assert pairs.min() >= 0
    
    # only keep information about the IDS with the webtype we care
    ids = np.arange(n_points)
    
    is_web_type = (web==web_type_id)
    print('Keeping {} points of type {}'.format(np.count_nonzero(is_web_type), webtype))
    
    type_ids = ids[is_web_type]    
    is_web_type_pair = np.isin(pairs[:,0], type_ids) & np.isin(pairs[:,1], type_ids)
    pairs = pairs[is_web_type_pair,:]
    print('Keeping {} pairs of type {}'.format(len(pairs), webtype))
    #print(pairs)

    fof_groups = find_fof_groups(pairs)
    
    n_fof_groups = len(fof_groups)
    print('Found {} groups'.format(n_fof_groups))
    
    group_properties = compute_group_properties(fof_groups, pos)
    
    #print(group_properties)
    group_df = pd.DataFrame.from_dict(group_properties)
    group_df.to_csv(catalogfile, index=False)
    #print(fof_groups)
    
def main():
    parser = argparse.ArgumentParser()
    
    
    parser.add_argument(
        "--posfile", help="input 3D positions", type=str, default=None, required=True,
    )
    
    parser.add_argument(
        "--pairfile", help="input pair file", type=str, default=None, required=True,
    )
    
    parser.add_argument(
        "--countfile", help="input link count file", type=str, default=None, required=True,
    )
    
    parser.add_argument(
        "--webtype", help="webtype to build the catalog", type=str, default=None, required=True,
    )
    
    parser.add_argument(
        "--catalogfile", help="outputfile for the web catalog", type=str, default=None, required=True,
    )
    
    args = parser.parse_args()
    
    make_catalog(args.posfile, args.pairfile, args.countfile, args.catalogfile, args.webtype)
    
if __name__ == "__main__":
    main()
