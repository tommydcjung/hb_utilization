import pandas as pd


FILENAME = "vanilla_stats.csv"

STALL_LIST = [
  "stall_depend_dram_load",
  "stall_depend_group_load",
  "stall_depend_global_load",
  "stall_depend_idiv",
  "stall_depend_fdiv",
  "stall_depend_local_load",
  "stall_depend_imul",
  "stall_amo_aq",
  "stall_amo_rl",
  "stall_bypass",
  "stall_lr_aq",
  "stall_fence",
  "stall_remote_req",
  "stall_remote_credit",
  "stall_fdiv_busy",
  "stall_idiv_busy",
  "stall_barrier",
  "stall_remote_ld_wb",
  "stall_ifetch_wait",
  "stall_remote_flw_wb"
]
BUBBLE_LIST = [
  "bubble_branch_miss",
  "bubble_jalr_miss",
  "bubble_icache_miss"
]

def parse_vanilla_stat():
  try:
    df = pd.read_csv(FILENAME)
  except:
    print("{} not found.".format(FILENAME))
    return

  tags = df["tag"]
  timestamps = df["global_ctr"]
  
  bubble_cols = list(filter(lambda x: x.startswith("bubble_"), list(df)))
  stall_cols = list(filter(lambda x: x.startswith("stall_"), list(df)))
  #print(bubble_cols)
  #print(stall_cols)
  total_cycle = 0
  instr_cycle = 0
  total_bubble_cycle = 0
  total_stall_cycle = 0

  # for each bubble and stall type
  each_bubble_cycle = {}
  each_stall_cycle = {}
  for col in bubble_cols:
    each_bubble_cycle[col] = 0
  for col in stall_cols:
    each_stall_cycle[col] = 0

  # calculate cycle
  start_timestamp = (2**32)-1
  end_timestamp = 0
  for i in range(len(tags)):
    tag = tags[i]
    timestamp = timestamps[i]
    tag_type = (0xc0000000 & tag) >> 30

    instr_total = df["instr_total"][i]

    # kernel start
    if tag_type == 2:
      if timestamp < start_timestamp:
        start_timestamp = timestamp
      total_cycle -= timestamp
      instr_cycle -= instr_total
      for col in bubble_cols:
        total_bubble_cycle     -= df[col][i]
        each_bubble_cycle[col] -= df[col][i]
      for col in stall_cols:
        total_stall_cycle      -= df[col][i]
        each_stall_cycle[col]  -= df[col][i]
      
    # kernel end
    elif tag_type == 3:
      if timestamp > end_timestamp:
        end_timestamp = timestamp
      total_cycle += timestamp
      instr_cycle += instr_total
      for col in bubble_cols:
        total_bubble_cycle += df[col][i]
        each_bubble_cycle[col] += df[col][i]
      for col in stall_cols:
        total_stall_cycle  += df[col][i]
        each_stall_cycle[col]  += df[col][i]
  
  
  print("")
  print("--------------------------------")
  print("Core Utilization")

  print("--------------------------------")
  for col in stall_cols:
    print("{:<{w1}} = {:<{w2}} ({:.2f} %)".format(col, each_stall_cycle[col], each_stall_cycle[col]/total_cycle*100, w1=30, w2=12))
  print("{:<{w1}} = {:<{w2}} ({:.2f} %)".format("Total Stall", total_stall_cycle, total_stall_cycle/total_cycle*100, w1=30, w2=12))

  print("--------------------------------")
  for col in bubble_cols:
    print("{:<{w1}} = {:<{w2}} ({:.2f} %)".format(col, each_bubble_cycle[col], each_bubble_cycle[col]/total_cycle*100, w1=30, w2=12))
  print("{:<{w1}} = {:<{w2}} ({:.2f} %)".format("Total Bubble", total_bubble_cycle, total_bubble_cycle/total_cycle*100, w1=30, w2=12))

  print("--------------------------------")
  print("Utilization   = {:.2f} %".format(instr_cycle/total_cycle*100))
  print("--------------------------------")
  print("Runtime       = {} cycles".format(end_timestamp - start_timestamp))
  print("--------------------------------")
