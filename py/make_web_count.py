import argparse
import numpy as np
import scipy.spatial as spatial
import itertools
import os


def make_count(datafile, randomfile, inputdir, outputdir):
    extension = datafile[-4:]
    intermediate_datafile = datafile[:-4] + '_' + randomfile[:-4] + '_nconnections' + extension
    print(intermediate_datafile)
    
    pairs_datafile = datafile[:-4] + '_' + randomfile[:-4] + '_pairs' + extension
    print(pairs_datafile)
    
    intermediate_randomfile = randomfile[:-4] + '_' + datafile[:-4] + '_nconnections' + extension
    print(intermediate_randomfile)
    
    pairs_randomfile = randomfile[:-4] + '_' + datafile[:-4] + '_pairs' + extension
    print(pairs_randomfile)
    
    data = np.loadtxt(os.path.join(inputdir, datafile))
    data = data[:,0:3]
    random = np.loadtxt(os.path.join(inputdir, randomfile))
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

    np.savetxt(os.path.join(outputdir, intermediate_datafile), count_data.T, fmt="%d %d")
    np.savetxt(os.path.join(outputdir, intermediate_randomfile), count_random.T,  fmt="%d %d")

    is_pairs_data = (unique_pairs[:,0]<n_d) & (unique_pairs[:,1]<n_d)
    is_pairs_random = (unique_pairs[:,0]>=n_d) & (unique_pairs[:,1]>=n_d)
    pairs_data = unique_pairs[is_pairs_data,:]
    pairs_random = unique_pairs[is_pairs_random,:]-n_d
    
    
    np.savetxt(os.path.join(outputdir, pairs_datafile), pairs_data, fmt="%d %d")
    np.savetxt(os.path.join(outputdir, pairs_randomfile), pairs_random,  fmt="%d %d")
    
    #web_class_data = web_classification(n_to_data[:n_d], n_to_random[:n_d] , n_d)
    #web_class_random = web_classification(n_to_data[n_d:], n_to_random[n_d:], n_d)
    
    #np.savetxt(outputdatafile, web_class_data, fmt="%d")
    #np.savetxt(outputrandomfile, web_class_random,  fmt="%d")
    

def main():
    parser = argparse.ArgumentParser()
    
    
    parser.add_argument(
        "--datafile", help="input data catalog", type=str, default=None, required=True,
    )
    
    parser.add_argument(
        "--randomfile", help="input random catalog", type=str, default=None, required=True,
    )
    
    parser.add_argument(
        "--inputdir", help="input directory", type=str, default=None, required=True,
    )
    
    parser.add_argument(
        "--outputdir", help="output directory", type=str, default=None, required=True,
    )
    
#    parser.add_argument(
#        "--outputdatafile", help="output classification file for the input data catalog", type=str, default=None, required=True,
#    )
    
 #   parser.add_argument(
 #       "--outputrandomfile", help="output classification file for the input random catalog", type=str, default=None, required=True,
 #   )
  
    
    args = parser.parse_args()
    
    make_count(args.datafile, args.randomfile, args.inputdir, args.outputdir)
    
if __name__ == "__main__":
    main()
