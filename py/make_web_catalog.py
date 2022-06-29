import argparse
import numpy as np
import sys
sys.setrecursionlimit(2000)


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
        print('friends', friends)
        for friend in friends:
            group.append(friend)
            group.extend(find_friends(friend, all_ids, pair_ids, included_ids))
    
        group = list(set(group))
        group.sort()
        return group
    
    
    
def find_fof_groups(pairs):
    pairs = np.int_(pairs)
    print(pairs)
    groups = {}
    group_id = 0
    all_ids = list(np.sort(np.unique(pairs.flatten())))
    n_points = len(all_ids)
    #print(n_points)
    print('points to be grouped',n_points)
    included_ids = list(np.zeros(n_points, dtype=int))

    n_total = 0
    for first_id in [all_ids[0]]:
        fof_ids = find_friends(first_id, all_ids, pairs, included_ids)
        if len(fof_ids):
            print(first_id, len(fof_ids))
            n_total += len(fof_ids)
            groups[group_id] = fof_ids
            group_id += 1
            
    # sanity check
    assert n_total == n_points
    return groups

def make_catalog(posfile, pairfile, webfile, catalogfile, webtype):
    web_types = {"void":0, "sheet":1, "filament":2, "peak":3}
    web_type_id = web_types[webtype]

    pos = np.loadtxt(posfile)
    pos = pos[:,0:3]
    pairs = np.loadtxt(pairfile)
    web = np.loadtxt(webfile)
    
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
    print(pairs)

    fof_groups = find_fof_groups(pairs)
    print(fof_groups)
    
def main():
    parser = argparse.ArgumentParser()
    
    
    parser.add_argument(
        "--posfile", help="input 3D positions", type=str, default=None, required=True,
    )
    
    parser.add_argument(
        "--pairfile", help="input pair file", type=str, default=None, required=True,
    )
    
    parser.add_argument(
        "--webfile", help="input web classification file", type=str, default=None, required=True,
    )
    
    parser.add_argument(
        "--webtype", help="webtype to build the catalog", type=str, default=None, required=True,
    )
    
    parser.add_argument(
        "--catalogfile", help="outputfile for the web catalog", type=str, default=None, required=True,
    )
    
    args = parser.parse_args()
    
    make_catalog(args.posfile, args.pairfile, args.webfile, args.catalogfile, args.webtype)
    
if __name__ == "__main__":
    main()
