import numpy as np
for random_id in range(1):
    for void_limit in np.linspace(-1.0, -0.5, 51):
        for knot_limit in np.linspace(0.5, 1.0, 51):
            comm = "python ../py/make_web_catalog.py --posfile ../data/TCW/pos/fof_catalog_200Mpc512_xyz.dat"
            comm += " --pairfile ../data/TCW/web/random_{:03d}_fof_catalog_200Mpc512_xyz_fof_catalog_200Mpc512_xyz_pairs.dat".format(random_id)
            comm += " --countfile ../data/TCW/web/random_{:03d}_fof_catalog_200Mpc512_xyz_fof_catalog_200Mpc512_xyz_nconnections.dat".format(random_id)
            comm += " --catalogfile ../data/TCW/parameter_search/web{:d}_{:d}_random_{:03d}_fof_catalog_200Mpc512_xyz.csv".format(int(void_limit*100), int(knot_limit*100), random_id)
            comm += " --voidlimit  {} --knotlimit {} ".format(void_limit, knot_limit)
            print(comm)
