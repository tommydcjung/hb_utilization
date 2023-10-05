import pandas as pd

FP_INSTR_TYPES = [
  "instr_fadd",
  "instr_fsub",

  "instr_fmul",
  "instr_fmadd",
  "instr_fmsub",
  "instr_fnmadd",
  "instr_fnmsub",

  "instr_fdiv",
  "instr_fsqrt",
  
]

def parse_vanilla_stat(filename="vanilla_stats.csv"):
  try:
    df = pd.read_csv(filename)
  except:
    print("{} not found.".format(filename))
    return None

  tags = df["tag"]
  timestamps = df["global_ctr"]
  
  bubble_cols = list(filter(lambda x: x.startswith("bubble_"), list(df)))
  stall_cols = list(filter(lambda x: x.startswith("stall_"), list(df)))
  instr_cols = list(filter(lambda x: x.startswith("instr_"), list(df)))
  instr_cols.remove("instr_total")
  #print(bubble_cols)
  #print(stall_cols)
  total_cycle = 0
  instr_cycle = 0
  total_bubble_cycle = 0
  total_stall_cycle = 0
  fp_instr_executed = 0

  # for each bubble and stall type
  each_bubble_cycle = {}
  each_stall_cycle = {}
  each_instr_cycle = {}
  for col in bubble_cols:
    each_bubble_cycle[col] = 0
  for col in stall_cols:
    each_stall_cycle[col] = 0
  for col in instr_cols:
    each_instr_cycle[col] = 0

  
  # calculate cycle
  start_count = 0
  end_count = 0
  start_timestamp = (2**32)-1
  end_timestamp = 0
  for i in range(len(tags)):
    tag = tags[i]
    timestamp = timestamps[i]
    tag_type = (0xc0000000 & tag) >> 30

    instr_total = df["instr_total"][i]
    fp_instr_total = 0
    for fpt in FP_INSTR_TYPES:
      fp_instr_total += df[fpt][i]

    # kernel start
    if tag_type == 2:
      start_count += 1
      if timestamp < start_timestamp:
        start_timestamp = timestamp
      total_cycle -= timestamp
      instr_cycle -= instr_total
      fp_instr_executed -= fp_instr_total
      for col in bubble_cols:
        total_bubble_cycle     -= df[col][i]
        each_bubble_cycle[col] -= df[col][i]
      for col in stall_cols:
        total_stall_cycle      -= df[col][i]
        each_stall_cycle[col]  -= df[col][i]
      for col in instr_cols:
        each_instr_cycle[col] -= df[col][i]
      
    # kernel end
    elif tag_type == 3:
      end_count += 1
      if timestamp > end_timestamp:
        end_timestamp = timestamp
      total_cycle += timestamp
      instr_cycle += instr_total
      fp_instr_executed += fp_instr_total
      for col in bubble_cols:
        total_bubble_cycle += df[col][i]
        each_bubble_cycle[col] += df[col][i]
      for col in stall_cols:
        total_stall_cycle  += df[col][i]
        each_stall_cycle[col]  += df[col][i]
      for col in instr_cols:
        each_instr_cycle[col] += df[col][i]

  if (start_count == 0) or (start_count != end_count):
    print("Error: vanilla_stat start and end count do not match or exist.", start_count, end_count)
    return None

  # build stat dict
  curr_stat = {}
  curr_stat["runtime"] = end_timestamp - start_timestamp
  curr_stat["util_pct"] = instr_cycle/total_cycle*100
  curr_stat["total_cycle"] = total_cycle
  curr_stat["total_stall_cycle"] = total_stall_cycle
  curr_stat["total_bubble_cycle"] = total_bubble_cycle
  for col in stall_cols:
    curr_stat[col] = each_stall_cycle[col]
  for col in bubble_cols:
    curr_stat[col] = each_bubble_cycle[col]
  for col in instr_cols:
    curr_stat[col] = each_instr_cycle[col]

  curr_stat["non_fp_instr_exec"] = instr_cycle-fp_instr_executed
  curr_stat["fp_instr_exec"] = fp_instr_executed
  curr_stat["total_instr_exec"] = instr_cycle
  
  return curr_stat
  

def print_vanilla_stat(stat):
  print("")
  print("--------------------------------")
  print("Core Utilization")

  print("--------------------------------")
  keys = list(stat.keys())
  stall_cols = list(filter(lambda x: x.startswith("stall"), keys))
  for col in stall_cols:
    if stat[col] != 0:
      print("{:<{w1}} = {:<{w2}} ({:.2f} %)".format(col, stat[col], stat[col]/stat["total_cycle"]*100, w1=30, w2=12))
  print("{:<{w1}} = {:<{w2}} ({:.2f} %)".format("Total Stall", stat["total_stall_cycle"], stat["total_stall_cycle"]/stat["total_cycle"]*100, w1=30, w2=12))

  print("--------------------------------")
  bubble_cols = list(filter(lambda x: x.startswith("bubble"), keys))
  for col in bubble_cols:
    if stat[col] != 0:
      print("{:<{w1}} = {:<{w2}} ({:.2f} %)".format(col, stat[col], stat[col]/stat["total_cycle"]*100, w1=30, w2=12))
  print("{:<{w1}} = {:<{w2}} ({:.2f} %)".format("Total Bubble", stat["total_bubble_cycle"], stat["total_bubble_cycle"]/stat["total_cycle"]*100, w1=30, w2=12))

  print("--------------------------------")
  instr_cols = list(filter(lambda x: x.startswith("instr"), keys))
  for col in instr_cols:
    if stat[col] != 0:
      print("{:<{w1}} = {:<{w2}} ({:.2f} %)".format(col.replace("instr_", ""), stat[col], stat[col]/stat["total_instr_exec"]*100, w1=30, w2=12))
      
  #print("Non-FP  Instr Executed   = {:<{w}}".format(stat["non_fp_instr_exec"], w=12))
  #print("FP      Instr Executed   = {:<{w}}".format(stat["fp_instr_exec"], w=12))
  print("Total Instr Executed   = {:<{w}}".format(stat["total_instr_exec"], w=12))
  print("--------------------------------")
  print("Utilization   = {:.2f} %".format(stat["util_pct"]))
  print("--------------------------------")
  print("Runtime       = {} cycles".format(stat["runtime"]))
  print("--------------------------------")
