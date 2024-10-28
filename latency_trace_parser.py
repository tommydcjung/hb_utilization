# network latency trace parser;
#


import sys
import os
import numpy as np


NUM_TILES_X = 16
NUM_TILES_Y = 8
POD_ORIGIN_X = NUM_TILES_X
POD_ORIGIN_Y = NUM_TILES_Y


class LatencyParser:

  def __init__(self, bpath, network_type, rf=None, depop=None):
    self.bpath = bpath
    self.network_type = network_type
    self.rf = rf
    self.depop = depop
    print("network_type={}".format(network_type))
    # vc_y = 0, north
    # vc_y = 1, south
    self.tile_fwd_table = np.zeros((NUM_TILES_X, NUM_TILES_Y, NUM_TILES_X, 2), dtype=np.uint64)
    self.tile_fwd_count = np.zeros((NUM_TILES_X, NUM_TILES_Y, NUM_TILES_X, 2), dtype=np.uint64)
    self.vc_fwd_table = np.zeros((NUM_TILES_X, NUM_TILES_Y, NUM_TILES_X, 2), dtype=np.uint64)
    self.vc_fwd_count = np.zeros((NUM_TILES_X, NUM_TILES_Y, NUM_TILES_X, 2), dtype=np.uint64)
    self.vc_rev_table = np.zeros((NUM_TILES_X, 2, NUM_TILES_X, NUM_TILES_Y), dtype=np.uint64)
    self.vc_rev_count = np.zeros((NUM_TILES_X, 2, NUM_TILES_X, NUM_TILES_Y), dtype=np.uint64)
    self.tile_rev_table = np.zeros((NUM_TILES_X, 2, NUM_TILES_X, NUM_TILES_Y), dtype=np.uint64)
    self.tile_rev_count = np.zeros((NUM_TILES_X, 2, NUM_TILES_X, NUM_TILES_Y), dtype=np.uint64)
    return

  def parse_tile_fwd(self, timestamp, tile_x, tile_y, vc_x, vc_y):
    self.tile_fwd_table[tile_x,tile_y,vc_x,vc_y] += timestamp
    self.tile_fwd_count[tile_x,tile_y,vc_x,vc_y] += 1
    return

  def parse_vc_fwd(self, timestamp, tile_x, tile_y, vc_x, vc_y):
    self.vc_fwd_table[tile_x,tile_y,vc_x,vc_y] += timestamp
    self.vc_fwd_count[tile_x,tile_y,vc_x,vc_y] += 1
    return

  def parse_vc_rev(self, timestamp, vc_x, vc_y, tile_x, tile_y):
    self.vc_rev_table[vc_x,vc_y,tile_x,tile_y] += timestamp
    self.vc_rev_count[vc_x,vc_y,tile_x,tile_y] += 1
    return

  def parse_tile_rev(self, timestamp, vc_x, vc_y, tile_x, tile_y):
    self.tile_rev_table[vc_x,vc_y,tile_x,tile_y] += timestamp
    self.tile_rev_count[vc_x,vc_y,tile_x,tile_y] += 1
    return


  def parse_line(self, line):
    words = line.split(",")
    trace_type = words[0]
    timestamp = int(words[1])
    src_x   = int(words[2])
    src_y   = int(words[3])
    dest_x  = int(words[4])
    dest_y  = int(words[5])
    if trace_type == "tile_fwd":
      tile_x = src_x - NUM_TILES_X
      tile_y = src_y - NUM_TILES_Y
      vc_x = dest_x - NUM_TILES_X 
      vc_y =  0 if dest_y == (NUM_TILES_Y-1) else 1
      self.parse_tile_fwd(timestamp, tile_x, tile_y, vc_x, vc_y)
    elif trace_type == "vc_fwd":
      tile_x = src_x - NUM_TILES_X
      tile_y = src_y - NUM_TILES_Y
      vc_x = dest_x - NUM_TILES_X 
      vc_y =  0 if dest_y == (NUM_TILES_Y-1) else 1
      self.parse_vc_fwd(timestamp, tile_x, tile_y, vc_x, vc_y)
    elif trace_type == "vc_rev":
      vc_x = src_x - NUM_TILES_X 
      vc_y =  0 if src_y == (NUM_TILES_Y-1) else 1
      tile_x = dest_x - NUM_TILES_X
      tile_y = dest_y - NUM_TILES_Y
      self.parse_vc_rev(timestamp, vc_x, vc_y, tile_x, tile_y)
    elif trace_type == "tile_rev":
      vc_x = src_x - NUM_TILES_X 
      vc_y =  0 if src_y == (NUM_TILES_Y-1) else 1
      tile_x = dest_x - NUM_TILES_X
      tile_y = dest_y - NUM_TILES_Y
      self.parse_tile_rev(timestamp, vc_x, vc_y, tile_x, tile_y)
    return

  def get_mesh_latency(self, src_x, src_y, dest_x, dest_y):
    return abs(dest_y-src_y) + abs(dest_x-src_x)


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

  def get_torus_latency_x(self, src, dst):
    base_src = src - (NUM_TILES_X)
    base_dst = dst - (NUM_TILES_X)
    torus_src = base_src / 2 if (base_src % 2 == 0) else (NUM_TILES_X - (base_src/2))
    torus_dst = base_dst / 2 if (base_dst % 2 == 0) else (NUM_TILES_X - (base_dst/2))
    ccw_dist = (torus_src-torus_dst) % NUM_TILES_X
    cw_dist  = (torus_dst-torus_src) % NUM_TILES_X
    return min(cw_dist, ccw_dist)

  def get_torus_latency_y(self, src, dst):
    base_src = src - (NUM_TILES_Y-2)
    base_dst = dst - (NUM_TILES_Y-2)
    torus_src = base_src / 2 if (base_src % 2 == 0) else (NUM_TILES_Y+4 - (base_src/2))
    torus_dst = base_dst / 2 if (base_dst % 2 == 0) else (NUM_TILES_Y+4 - (base_dst/2))
    ccw_dist = (torus_src-torus_dst) % (NUM_TILES_Y+4)
    cw_dist  = (torus_dst-torus_src) % (NUM_TILES_Y+4)
    return min(cw_dist, ccw_dist)


  def get_torus_latency(self, src_x, src_y, dest_x, dest_y):
    x_latency = self.get_torus_latency_x(src_x, dest_x)
    y_latency = self.get_torus_latency_y(src_y, dest_y)
    return x_latency + y_latency

  def parse(self):
    with open("run.log") as f:
      for line in f.readlines():
        stripped = line.strip()
        if (stripped.startswith("tile_fwd") or stripped.startswith("vc_fwd") or
            stripped.startswith("vc_rev") or stripped.startswith("tile_rev")):
          self.parse_line(stripped)


    # fwd latency (sanity check);
    for tile_x in range(NUM_TILES_X):
      for tile_y in range(NUM_TILES_Y):
        for vc_x in range(NUM_TILES_X):
          for vc_y in range(2):
            if self.vc_fwd_count[tile_x,tile_y,vc_x,vc_y] != self.tile_fwd_count[tile_x,tile_y,vc_x,vc_y]:
              print("mismatch")

    # rev latency (sanity check);
    for tile_x in range(NUM_TILES_X):
      for tile_y in range(NUM_TILES_Y):
        for vc_x in range(NUM_TILES_X):
          for vc_y in range(2):
            if self.vc_rev_count[vc_x,vc_y,tile_x,tile_y] != self.tile_rev_count[vc_x,vc_y,tile_x,tile_y]:
              print("mismatch")

    if np.sum(self.tile_fwd_count) != np.sum(self.vc_rev_count):
      print("mismatch")

    # fwd latency.
    fwd_latency = 0
    for tile_x in range(NUM_TILES_X):
      for tile_y in range(NUM_TILES_Y):
        for vc_x in range(NUM_TILES_X):
          for vc_y in range(2):
            fwd_latency += self.vc_fwd_table[tile_x,tile_y,vc_x,vc_y]
            fwd_latency -= self.tile_fwd_table[tile_x,tile_y,vc_x,vc_y]

    
    # rev latency.
    rev_latency = 0
    for tile_x in range(NUM_TILES_X):
      for tile_y in range(NUM_TILES_Y):
        for vc_x in range(NUM_TILES_X):
          for vc_y in range(2):
            rev_latency -= self.vc_rev_table[vc_x,vc_y,tile_x,tile_y]
            rev_latency += self.tile_rev_table[vc_x,vc_y,tile_x,tile_y]

    total_latency = (fwd_latency+rev_latency)/np.sum(self.vc_fwd_count)/2
    print("total latency        = {}".format((fwd_latency+rev_latency)/np.sum(self.vc_fwd_count)/2))


    # calculate intrinsic latency;
    int_latency = 0
    if self.network_type == "mesh":
      for tile_x in range(NUM_TILES_X):
        for tile_y in range(NUM_TILES_Y):
          for vc_x in range(NUM_TILES_X):
            for vc_y in range(2):
              int_latency += self.get_mesh_latency(tile_x,tile_y,vc_x,vc_y) * self.tile_fwd_count[tile_x,tile_y,vc_x,vc_y]
              int_latency += self.get_mesh_latency(tile_x,tile_y,vc_x,vc_y) * self.vc_rev_count[vc_x,vc_y,tile_x,tile_y]
      int_latency /= (2*np.sum(self.tile_fwd_count))
    elif self.network_type == "hruche":
      for tile_x in range(NUM_TILES_X):
        for tile_y in range(NUM_TILES_Y):
          for vc_x in range(NUM_TILES_X):
            for vc_y in range(2):
              int_latency += self.get_half_ruche_latency(tile_x,tile_y,vc_x,vc_y) * self.tile_fwd_count[tile_x,tile_y,vc_x,vc_y]
              int_latency += self.get_half_ruche_latency(tile_x,tile_y,vc_x,vc_y) * self.vc_rev_count[vc_x,vc_y,tile_x,tile_y]
      int_latency /= (2*np.sum(self.tile_fwd_count))
    elif self.network_type == "fruche":
      for tile_x in range(NUM_TILES_X):
        for tile_y in range(NUM_TILES_Y):
          for vc_x in range(NUM_TILES_X):
            for vc_y in range(2):
              int_latency += self.get_half_ruche_latency(tile_x,tile_y,vc_x,vc_y) * self.tile_fwd_count[tile_x,tile_y,vc_x,vc_y]
              int_latency += self.get_half_ruche_latency(tile_x,tile_y,vc_x,vc_y) * self.vc_rev_count[vc_x,vc_y,tile_x,tile_y]
      int_latency /= (2*np.sum(self.tile_fwd_count))
    elif self.network_type == "torus":
      for tile_x in range(NUM_TILES_X):
        for tile_y in range(NUM_TILES_Y):
          for vc_x in range(NUM_TILES_X):
            for vc_y in range(2):
              int_latency += self.get_torus_latency(tile_x,tile_y,vc_x,vc_y) * self.tile_fwd_count[tile_x,tile_y,vc_x,vc_y]
              int_latency += self.get_torus_latency(tile_x,tile_y,vc_x,vc_y) * self.vc_rev_count[vc_x,vc_y,tile_x,tile_y]
      int_latency /= (2*np.sum(self.tile_fwd_count))

    print("int latency          = {}".format(int_latency))
    print("congestion latency   = {}".format(total_latency-int_latency))
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
