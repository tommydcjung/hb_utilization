#
#   energy_estimator.py 
#
#   python energy_estimator.py {rf_x} {depop} {bpath} 
#


import sys
import os
import numpy as np
import pandas as pd


NUM_TILES_X = 16
NUM_TILES_Y = 16

class EnergyEstimator:
  
  # constructor;
  def __init__(self, network_type, rf_x, depop, bpath):
    # parameters;
    self.network_type = network_type
    self.rf_x = rf_x
    self.depop = depop
    self.bpath = bpath

    # energy buckets;
    self.stall_energy = 0
    self.core_energy = 0
    self.router_energy = 0
    self.wire_energy = 0
    return


  # main func;
  def estimate(self):
    #self.parse_vanilla_stat()
    self.parse_router_stat()
    self.report()
    return


  # parse vanilla stat;
  def parse_vanilla_stat(self):
    # open csv;
    df = pd.read_csv(self.bpath + "vanilla_stats.csv")

    # stat types;
    instr_cols = list(filter(lambda x: x.startswith("instr_"), list(df)))
    instr_cols.remove("instr_total")
    stall_cols = list(filter(lambda x: x.startswith("stall_"), list(df)))
    miss_cols = list(filter(lambda x: x.startswith("miss_"), list(df)))
    miss_cols.remove("miss_icache")

    # stat counts;
    stat = {}
    for col in instr_cols:
      stat[col] = 0
    for col in stall_cols:
      stat[col] = 0
    for col in miss_cols:
      stat[col] = 0

    # go through each stat rows;
    start_count = 0
    end_count = 0
    for i in range(len(df)):
      tag_type = (df["tag"][i] & 0xc0000000) >> 30
      # kernel start;
      if tag_type == 2:
        start_count += 1
        for col in instr_cols:
          stat[col] -= df[col][i]
        for col in stall_cols:
          stat[col] -= df[col][i]
        for col in miss_cols:
          stat[col] -= df[col][i]
      # kernel end;
      elif tag_type == 3:
        end_count += 1
        for col in instr_cols:
          stat[col] += df[col][i]
        for col in stall_cols:
          stat[col] += df[col][i]
        for col in miss_cols:
          stat[col] += df[col][i]
  
    # calculate energy;
    for key in stat.keys():
      if stat[key] != 0:
        self.add_core_energy(key, stat[key])
        #print(key, stat[key])
    return

  # classify and add energy;
  def add_core_energy(self, key, count):
    # fpu
    if key in [ "instr_fadd", "instr_fmul", "instr_fsub",
                "instr_fsgnj", "instr_fsgnjn",
                "instr_fmadd",
                "instr_fcvt_s_w",
                "instr_fmv_w_x",
                "instr_fmsub",
                "instr_fle",
              ]: 
      self.core_energy += 12.482 * count
    # fdiv/fsqrt;
    elif key in ["instr_fdiv", "instr_fsqrt"]:
      self.core_energy += 89.890 * count
    # local load;
    elif key in ["instr_local_ld", "instr_local_flw"]:
      self.core_energy += 10.606 * count
    # local store;
    elif key in ["instr_local_st", "instr_local_fsw"]:
      self.core_energy += 10.606 * count
    # remote ops;
    elif key in ["instr_remote_flw_dram", "instr_remote_seq_flw_dram",
                  "instr_remote_flw_group", "instr_remote_fsw_dram",
                  "instr_remote_ld_dram", "instr_remote_seq_ld_dram",
                  "instr_remote_st_dram", "instr_amoadd", "instr_amoor"]:
      self.core_energy += 7.757 * count
    # branch;
    elif key in ["instr_beq", "instr_bne", "instr_blt", "instr_bge", "instr_bgeu", "instr_bltu",
                  "instr_jal", "instr_jalr"]:
      self.core_energy += 11.542 * count
    # ALU;
    elif key in ["instr_add", "instr_sub", "instr_or", "instr_and", "instr_sll"]:
      self.core_energy += 8.93 * count
    # alu immediate;
    elif key in ["instr_slli", "instr_addi", "instr_lui", "instr_andi", "instr_srli", "instr_srai"]:
      self.core_energy += 8.847 * count
    # MUL;
    elif key in ["instr_mul"]:
      self.core_energy += 8.59 * count
    # ignore or nop;
    elif key in ["instr_remote_st_global", "instr_fence", "instr_barsend", "instr_barrecv"]:
      self.core_energy += 7.757 * count
    # stall
    elif key in ["stall_depend_dram_load", "stall_depend_dram_seq_load",
                 "stall_depend_group_load", "stall_depend_local_load",
                 "stall_depend_imul", "stall_bypass", "stall_fence",
                 "stall_remote_req", "stall_barrier", "stall_remote_flw_wb", "stall_remote_credit",
                 "stall_depend_dram_amo", "stall_depend_fdiv", "stall_fdiv_busy", "stall_remote_ld_wb"]:
      self.stall_energy += 2.740 * count
    # branch miss;
    elif key in ["miss_bne", "miss_beq", "miss_blt", "miss_bge", "miss_bgeu", "miss_bltu"]:
      self.core_energy += (24.778-11.542) * count
    else:
      print("WARNING: unclassified key: {} {}".format(key, count))
    return


  # parse router stat;
  def parse_router_stat(self):
    # open csv;
    df = pd.read_csv(self.bpath + "router_stat.csv")

    # find start and end timestamp;
    start_timestamp = (2**32)-1
    end_timestamp = 0
    timestamps = df["global_ctr"]
    for i in range(len(timestamps)):
      timestamp = timestamps[i]
      if start_timestamp > timestamp:
        start_timestamp = timestamp
      if end_timestamp < timestamp:
        end_timestamp = timestamp

    # filter;
    start_cond = ((df["global_ctr"] == start_timestamp)
               & (df["XY_order"] == 1)
               & (df["x"] >= NUM_TILES_X)
               & (df["x"] < NUM_TILES_X*2)
               & (df["y"] >= NUM_TILES_Y)
               & (df["y"] < NUM_TILES_Y*2)
               & (df["output_dir"] != 0))
    end_cond = ((df["global_ctr"] == end_timestamp)
               & (df["XY_order"] == 1)
               & (df["x"] >= NUM_TILES_X)
               & (df["x"] < NUM_TILES_X*2)
               & (df["y"] >= NUM_TILES_Y)
               & (df["y"] < NUM_TILES_Y*2)
               & (df["output_dir"] != 0))

    start_df = df[start_cond]
    end_df   = df[end_cond]

    # count utilized;
    hor_count   = 0
    ver_count   = 0
    ruche_hor_count = 0
    ruche_ver_count = 0
    
    for i in range(len(start_df)):
      utilized = start_df["utilized"].iloc[i]
      output_dir = start_df["output_dir"].iloc[i]

      if output_dir in [1,2]:
        hor_count -= utilized
      elif output_dir in [3,4]:
        ver_count -= utilized
      elif output_dir in [5,6]:
        ruche_hor_count -= utilized
      elif output_dir in [7,8]:
        ruche_ver_count -= utilized

    for i in range(len(end_df)):
      utilized = end_df["utilized"].iloc[i]
      output_dir = end_df["output_dir"].iloc[i]

      if output_dir in [1,2]:
        hor_count += utilized
      elif output_dir in [3,4]:
        ver_count += utilized
      elif output_dir in [5,6]:
        ruche_hor_count += utilized
      elif output_dir in [7,8]:
        ruche_ver_count += utilized

    # calculate router energy;
    if self.network_type == "mesh":
      self.router_energy  = hor_count * 1.84
      self.router_energy += ver_count * 1.96
    elif self.network_type == "hruche":
      if self.depop == 1:
        self.router_energy  = hor_count * 2.06
        self.router_energy += ver_count * 2.27
        self.router_energy += ruche_hor_count * 1.79 
      else:
        self.router_energy  = hor_count * 2.24
        self.router_energy += ver_count * 2.33
        self.router_energy += ruche_hor_count * 2.09
    elif self.network_type == "fruche":
      if self.depop == 1:
        self.router_energy  = hor_count * 2.46
        self.router_energy += ver_count * 2.61
        self.router_energy += ruche_hor_count * 2.21
        self.router_energy += ruche_ver_count * 2.28
      else:
        self.router_energy  = hor_count * 2.75
        self.router_energy += ver_count * 2.72
        self.router_energy += ruche_hor_count * 2.61 
        self.router_energy += ruche_ver_count * 2.53
    elif self.network_type == "torus":
      self.router_energy  = hor_count * 3.10
      self.router_energy += ver_count * 4.03
  

    # calculate wire energy;
    if self.network_type == "hruche":
      self.wire_energy = ruche_hor_count * (self.rf_x-1) * 0.96
    elif self.network_type == "fruche":
      self.wire_energy = ruche_hor_count * (self.rf_x-1) * 0.96
      self.wire_energy = ruche_ver_count * (self.rf_x-1) * 0.96
    elif self.network_type == "torus":
      self.wire_energy = hor_count * (self.rf_x-1) * 0.96
      self.wire_energy = ver_count * (self.rf_x-1) * 0.96
  
    return


  # report text;
  def report(self):
    #print("core_energy    (uJ) = {:.2f}".format(self.core_energy / 1000000))
    #print("stall_energy   (uJ) = {:.2f}".format(self.stall_energy / 1000000))
    print("router_energy  (uJ) = {:.2f}".format(self.router_energy / 1000000))
    print("wire_energy    (uJ) = {:.2f}".format(self.wire_energy / 1000000))
    return


# main();
if __name__ == "__main__":
  network_type = sys.argv[1]
  rf_x  = int(sys.argv[2])
  depop = int(sys.argv[3])
  bpath = sys.argv[4] 
  ee = EnergyEstimator(network_type, rf_x, depop, bpath)
  ee.estimate()
