import sys, os

start = int(sys.argv[1])
end = int(sys.argv[2])

with open('../../args-y6.txt') as t:
    TILES = [a.split(' ')[0] for a in t.readlines()[:]] #Split string to get only the tilename, and no seeds
    TILES = TILES[::-1] #Dhayaa reverses tiles and runs from last to first. Sid goes from first to last.

with open('./do_Imsims_DES_%d_%d' % (start, end), 'w') as f:
    
    for k, tile in enumerate(TILES):
        
        
        if (k < start) | (k >= end): continue


        #2 regular +/- runs and 10 redshift runs.
        g1_arr       = [0.02, -0.02] + [0.02]*10
        g1_other_arr = [0]*2 + [-0.02]*10
        zlow_arr     = [0]*2 + [0.0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7]
        zhigh_arr    = [6]*2 + [0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 6.0]

        m = 0 #Number keeps track of how many runs you've submitted for this tile
        for g1, g1_other, zlow, zhigh in zip(g1_arr, g1_other_arr, zlow_arr, zhigh_arr):

            run_name = "g1_slice=%0.2f__g2_slice=0.00__g1_other=%0.2f__g2_other=0.00__zlow=%0.1f__zhigh=%0.1f" % (g1, g1_other, zlow, zhigh)
            args = {'g1' : g1, 'g1_other' : g1_other, 'zlow' : zlow, 'zhigh' : zhigh, 'tile' : tile, 'run_name' : run_name, 'config' : 'fiducial.yaml'}
        
            f.write('./jobsub %(tile)s 36 360 20 300 0 %(g1)0.2f %(g1_other)0.2f %(zlow)0.2f %(zhigh)0.2f %(config)s %(run_name)s\n' % args)
            
            m += 1

            if m == 2: break #Break if we hit 2 runs. So only +/- used

