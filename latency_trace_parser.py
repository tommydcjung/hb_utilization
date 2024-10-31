# network latency trace parser;
#


import sys
import os
import numpy as np


NUM_TILES_X = 16
NUM_TILES_Y = 16


class LatencyParser:

  def __init__(self, bpath, network_type, rf=None, depop=None):
    self.bpath = bpath
    self.network_type = network_type
    self.rf = rf
    self.depop = depop
    print("network_type={}".format(network_type))
    print("rf={}".format(rf))
    print("depop={}".format(depop))
    # vc_y = 0, north
    # vc_y = 1, south
    self.arr_size = NUM_TILES_X*NUM_TILES_Y*NUM_TILES_X*2
    self.tile_fwd_count = np.zeros(self.arr_size)
    self.vc_fwd_count   = np.zeros(self.arr_size)
    self.vc_rev_count   = np.zeros(self.arr_size)
    self.tile_rev_count = np.zeros(self.arr_size)
    return


  def get_idx(self, tile_x, tile_y, vc_x, vc_y):
    vc_y0 = 0 if (vc_y == NUM_TILES_Y-1) else 1
    vc_id = (NUM_TILES_X * vc_y0) + (vc_x - NUM_TILES_X)
    base_tile_x = tile_x - NUM_TILES_X
    base_tile_y = tile_y - NUM_TILES_Y
    tile_id = (base_tile_y*NUM_TILES_X) + base_tile_x
    return (tile_id*2*NUM_TILES_X) + vc_id


  def parse_count_csv(self, csvfile, arr):
    with open(csvfile) as f0:
      lines = f0.readlines()
      for line in lines:
        stripped = line.strip()
        words = stripped.split(",")
        tile_x = int(words[0])+NUM_TILES_X
        tile_y = int(words[1])+NUM_TILES_Y
        vc_x = int(words[2])+NUM_TILES_X
        vc_y = int(words[3])
        count  = int(words[4])
        idx = self.get_idx(tile_x, tile_y, vc_x, vc_y)
        arr[idx] = count
    return




  # mesh latency;
  def get_mesh_latency(self, src_x, src_y, dest_x, dest_y):
    return abs(dest_y-src_y) + abs(dest_x-src_x)


  # half ruche latency;
  def get_half_ruche_latency(self, src_x, src_y, dest_x, dest_y):
    latency = 0
    x_dist = abs(src_x-dest_x)
    if self.depop == 1:
      while x_dist !=  0:
        if x_dist > self.rf:
          x_dist -= self.rf
          latency += 1
        else:
          x_dist -= 1
          latency += 1
    else:
      while x_dist !=  0:
        if x_dist >= self.rf:
          x_dist -= self.rf
          latency += 1
        else:
          x_dist -= 1
          latency += 1

    y_dist = abs(src_y-dest_y)
    return latency + y_dist

  # full ruche latency;
  def get_full_ruche_latency(self, src_x, src_y, dest_x, dest_y):
    latency = 0
    x_dist = abs(src_x-dest_x)
    y_dist = abs(src_y-dest_y)

    if self.depop == 1:
      while x_dist !=  0:
        if x_dist > self.rf:
          x_dist -= self.rf
          latency += 1
        else:
          x_dist -= 1
          latency += 1
    else:
      while x_dist !=  0:
        if x_dist >= self.rf:
          x_dist -= self.rf
          latency += 1
        else:
          x_dist -= 1
          latency += 1

    if self.depop == 1:
      while y_dist !=  0:
        if y_dist > self.rf:
          y_dist -= self.rf
          latency += 1
        else:
          y_dist -= 1
          latency += 1
    else:
      while y_dist !=  0:
        if y_dist >= self.rf:
          y_dist -= self.rf
          latency += 1
        else:
          y_dist -= 1
          latency += 1

    return latency


  # Torus latency X;
  def get_torus_latency_x(self, src, dst):
    base_src = src - (NUM_TILES_X)
    base_dst = dst - (NUM_TILES_X)
    torus_src = base_src / 2 if (base_src % 2 == 0) else (NUM_TILES_X - (base_src/2))
    torus_dst = base_dst / 2 if (base_dst % 2 == 0) else (NUM_TILES_X - (base_dst/2))
    ccw_dist = (torus_src-torus_dst) % NUM_TILES_X
    cw_dist  = (torus_dst-torus_src) % NUM_TILES_X
    return min(cw_dist, ccw_dist)

  # Torus latency Y;
  def get_torus_latency_y(self, src, dst):
    base_src = src - (NUM_TILES_Y-2)
    base_dst = dst - (NUM_TILES_Y-2)
    torus_src = base_src / 2 if (base_src % 2 == 0) else (NUM_TILES_Y+4 - (base_src/2))
    torus_dst = base_dst / 2 if (base_dst % 2 == 0) else (NUM_TILES_Y+4 - (base_dst/2))
    ccw_dist = (torus_src-torus_dst) % (NUM_TILES_Y+4)
    cw_dist  = (torus_dst-torus_src) % (NUM_TILES_Y+4)
    return min(cw_dist, ccw_dist)

  # Torus latency;
  def get_torus_latency(self, src_x, src_y, dest_x, dest_y):
    x_latency = self.get_torus_latency_x(src_x, dest_x)
    y_latency = self.get_torus_latency_y(src_y, dest_y)
    return x_latency + y_latency




  def parse(self):
    # parse nt_latency.txt;
    with open("nt_latency.txt") as f:
      average_latency = float(f.readline())
      print("Total Average Latency        = {:.2f}".format(average_latency))

    # parse tile_fwd_count.csv
    self.parse_count_csv("tile_fwd_count.csv", self.tile_fwd_count)
    self.parse_count_csv("vc_fwd_count.csv", self.vc_fwd_count)
    self.parse_count_csv("vc_rev_count.csv", self.vc_rev_count)
    self.parse_count_csv("tile_rev_count.csv", self.tile_rev_count)


    # Sanity check;
    for tile_x in range(NUM_TILES_X):
      for tile_y in range(NUM_TILES_Y):
        for vc_x in range(NUM_TILES_X):
          for vc_y in range(2):
            vc_id = (vc_y * NUM_TILES_X) + vc_x
            tile_id = (tile_y * NUM_TILES_X) + tile_x
            idx = (tile_id*NUM_TILES_X*2) + vc_id
            if self.vc_fwd_count[idx] != self.tile_fwd_count[idx]:
              print("fwd count mismatch")
            if self.vc_rev_count[idx] != self.tile_rev_count[idx]:
              print("rev count mismatch")
            if self.tile_fwd_count[idx] != self.vc_rev_count[idx]:
              print("fwd and rev count mismatch")




    # calculate intrinsic latency;
    total_int_latency = 0
    total_count = 0
    for tile_x in range(NUM_TILES_X, 2*NUM_TILES_X):
      for tile_y in range(NUM_TILES_Y, 2*NUM_TILES_Y):
        for vc_x in range(NUM_TILES_X, 2*NUM_TILES_X):
          for vc_y in [NUM_TILES_Y-1, NUM_TILES_Y*2]:
            idx = self.get_idx(tile_x, tile_y, vc_x, vc_y)
            fwd_count = self.tile_fwd_count[idx]
            rev_count = self.vc_rev_count[idx]
            if self.network_type == "mesh":
              lat = self.get_mesh_latency(tile_x,tile_y,vc_x,vc_y)
            elif self.network_type == "hruche":
              lat = self.get_half_ruche_latency(tile_x,tile_y,vc_x,vc_y)
            elif self.network_type == "fruche":
              lat = self.get_full_ruche_latency(tile_x,tile_y,vc_x,vc_y)
            elif self.network_type == "torus":
              lat = self.get_torus_latency(tile_x,tile_y,vc_x,vc_y)
            total_int_latency += lat * (fwd_count+rev_count)
            total_count += (fwd_count+rev_count)
              
    average_int_latency = total_int_latency / total_count;


    print("Average int latency          = {:.2f}".format(average_int_latency))
    print("Average congestion latency   = {:.2f}".format(average_latency-average_int_latency))
    return




if __name__ == "__main__":
  bpath = sys.argv[1]
  network_type = sys.argv[2] # mesh, hruche, fruche, torus;

  os.chdir(bpath)

  if network_type in ["hruche", "fruche"]:
    rf = int(sys.argv[3])
    depop = int(sys.argv[4])
    lp = LatencyParser(bpath, network_type, rf, depop)
  else:    
    lp = LatencyParser(bpath, network_type)
    
  lp.parse()
