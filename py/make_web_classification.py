import argparse
import numpy as np
import scipy.spatial as spatial
import itertools

def web_classification(n_data, n_random, n_points):
    r_values = (n_data-n_random)/(n_data+n_random)
    web_class = np.zeros(n_points, dtype=np.int)
    is_void = r_values <= -0.50
    is_sheet = (r_values > -0.50) & (r_values<=0.0)
    is_filament = (r_values>0.0) & (r_values<=0.50)
    is_peak = (r_values>0.50)
    web_class[is_void] = 0
    web_class[is_sheet] = 1
    web_class[is_filament] = 2
    web_class[is_peak] = 3
    return web_class
    

def make_classification(datafile, randomfile, outputdatafile, outputrandomfile):
    extension = datafile[-4:]
    intermediate_datafile = datafile.replace(extension, '_n_connections'+extension)
    print(intermediate_datafile)
    
    extension = datafile[-4:]
    pairs_datafile = datafile.replace(extension, '_pairs'+extension)
    print(pairs_datafile)
    
    extension = randomfile[-4:]
    intermediate_randomfile = randomfile.replace(extension, '_n_connections'+extension)
    print(intermediate_randomfile)
    
    extension = datafile[-4:]
    pairs_randomfile = randomfile.replace(extension, '_pairs'+extension)
    print(pairs_randomfile)
    
    data = np.loadtxt(datafile)
    data = data[:,0:3]
    random = np.loadtxt(randomfile)
    random = random[:,0:3]
    
    n_d = len(data)
    n_r = len(random)
    
    print("n_data {} from {}".format(n_d, datafile))
    print("n_random {} from {}".format(n_r, randomfile))

    assert n_d == n_r
    
    all_points = np.vstack([data, random])

    tri = spatial.Delaunay(all_points)
    
    n_simplices = len(tri.simplices)
    print("{} n_simplices in Delaunay triangulation".format(n_simplices))
    
    all_pairs = []
    for simplex in tri.simplices:
        a = list(itertools.combinations(simplex,2))
        l = list(map(list, a))
        l = list(map(np.sort, l))
        l = list(map(list, l))
        all_pairs.append(l)
        
    all_pairs = np.vstack(all_pairs)
    print('all_pairs', np.shape(all_pairs))
    unique_pairs = np.unique(all_pairs, axis=0)
    print('unique_pairs', np.shape(unique_pairs))
    
    n_to_random = np.zeros(n_d+n_r)
    n_to_data = np.zeros(n_d+n_r)

    for p in unique_pairs:
        a = p[0]
        b = p[1]
        a_is_data = True
        b_is_data = True
        if a>=n_d:
            a_is_data = False
        if b>=n_d:
            b_is_data = False
        
        if a_is_data:
            n_to_data[b] +=1 
        else:
            n_to_random[b] +=1
    
        if b_is_data:
            n_to_data[a] +=1 
        else:
            n_to_random[a] +=1
            
    
    count_data = np.array([n_to_data[:n_d], n_to_random[:n_d]])
    count_random = np.array([n_to_data[n_d:], n_to_random[n_d:]])

    np.savetxt(intermediate_datafile, count_data.T, fmt="%d %d")
    np.savetxt(intermediate_randomfile, count_random.T,  fmt="%d %d")

    is_pairs_data = (unique_pairs[:,0]<n_d) & (unique_pairs[:,1]<n_d)
    is_pairs_random = (unique_pairs[:,0]>=n_d) & (unique_pairs[:,1]>=n_d)
    pairs_data = unique_pairs[is_pairs_data,:]
    pairs_random = unique_pairs[is_pairs_random,:]-n_d
    
    
    np.savetxt(pairs_datafile, pairs_data, fmt="%d %d")
    np.savetxt(pairs_randomfile, pairs_random,  fmt="%d %d")
    
    web_class_data = web_classification(n_to_data[:n_d], n_to_random[:n_d] , n_d)
    web_class_random = web_classification(n_to_data[n_d:], n_to_random[n_d:], n_d)
    
    np.savetxt(outputdatafile, web_class_data, fmt="%d")
    np.savetxt(outputrandomfile, web_class_random,  fmt="%d")
    

def main():
    parser = argparse.ArgumentParser()
    
    
    parser.add_argument(
        "--datafile", help="input data catalog", type=str, default=None, required=True,
    )
    
    parser.add_argument(
        "--randomfile", help="output random catalog", type=str, default=None, required=True,
    )
    
    parser.add_argument(
        "--outputdatafile", help="output classification file for the input data catalog", type=str, default=None, required=True,
    )
    
    parser.add_argument(
        "--outputrandomfile", help="output classification file for the input random catalog", type=str, default=None, required=True,
    )
  
    
    args = parser.parse_args()
    
    make_classification(args.datafile, args.randomfile, args.outputdatafile, args.outputrandomfile)
    
if __name__ == "__main__":
    main()