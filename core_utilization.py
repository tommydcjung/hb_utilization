import pandas as pd


def parse_vanilla_stat(filename="vanilla_stats.csv"):
  try:
    df = pd.read_csv(filename)
  except:
    print("{} not found.".format(filename))
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

  return curr_stat
  

def print_vanilla_stat(stat):
  print("")
  print("--------------------------------")
  print("Core Utilization")

  print("--------------------------------")
  keys = list(stat.keys())
  stall_cols = list(filter(lambda x: x.startswith("stall"), keys))
  for col in stall_cols:
    print("{:<{w1}} = {:<{w2}} ({:.2f} %)".format(col, stat[col], stat[col]/stat["total_cycle"]*100, w1=30, w2=12))
  print("{:<{w1}} = {:<{w2}} ({:.2f} %)".format("Total Stall", stat["total_stall_cycle"], stat["total_stall_cycle"]/stat["total_cycle"]*100, w1=30, w2=12))

  print("--------------------------------")
  bubble_cols = list(filter(lambda x: x.startswith("bubble"), keys))
  for col in bubble_cols:
    print("{:<{w1}} = {:<{w2}} ({:.2f} %)".format(col, stat[col], stat[col]/stat["total_cycle"]*100, w1=30, w2=12))
  print("{:<{w1}} = {:<{w2}} ({:.2f} %)".format("Total Bubble", stat["total_bubble_cycle"], stat["total_bubble_cycle"]/stat["total_cycle"]*100, w1=30, w2=12))

  print("--------------------------------")
  print("Utilization   = {:.2f} %".format(stat["util_pct"]))
  print("--------------------------------")
  print("Runtime       = {} cycles".format(stat["runtime"]))
  print("--------------------------------")
