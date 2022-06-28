import argparse
import numpy as np


def make_random(datafile, randomfile, geometry, seed):
    data = np.loadtxt(datafile)
    print(np.shape(data))
    pos_x = data[:,0]
    pos_y = data[:,1]
    pos_z = data[:,2]
    
    n_points = len(pos_x)
    random_pos_x = np.zeros(n_points)
    random_pos_y = np.zeros(n_points)
    random_pos_z = np.zeros(n_points)
    
    np.random.seed(seed)
    
    if geometry == 'cube':
        min_x, min_y, min_z = min(pos_x), min(pos_y), min(pos_z)
        max_x, max_y, max_z = max(pos_x), max(pos_y), max(pos_z)
        delta_x = max_x - min_x
        delta_y = max_y - min_y 
        delta_z = max_z - min_z
    
        random_pos_x = np.random.random(n_points)*delta_x + min_x
        random_pos_y = np.random.random(n_points)*delta_y + min_y
        random_pos_z = np.random.random(n_points)*delta_z + min_z

        print(min_x)
    else:
        print('WARNING. Geometry not implemented. Filling all data with zeroes')
        
    random_data = np.array([random_pos_x, random_pos_y, random_pos_z])
    np.savetxt(randomfile, random_data.T)

    
        
def main():
    parser = argparse.ArgumentParser()
    
    
    parser.add_argument(
        "--datafile", help="input data catalog", type=str, default=None, required=True,
    )
    
    parser.add_argument(
        "--randomfile", help="output random catalog", type=str, default=None, required=True,
    )
    
    parser.add_argument(
        "--geometry", help="random catalog geometry", type=str, default=None, required=True,
    )
    
    parser.add_argument(
        "--seed",
        help="random seed",
        type=int,
        default=42,
        required=False,
    )
    
    args = parser.parse_args()
    
    print(args)
    make_random(args.datafile, args.randomfile, args.geometry, args.seed)
    
if __name__ == "__main__":
    main()