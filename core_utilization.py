import pandas as pd


FILENAME = "vanilla_stats.csv"

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
  bubble_cycle = 0
  stall_cycle = 0

  # calculate cycle
  for i in range(len(tags)):
    tag = tags[i]
    timestamp = timestamps[i]
    tag_type = (0xc0000000 & tag) >> 30

    instr_total = df["instr_total"][i]

    # kernel start
    if tag_type == 2:
      total_cycle -= timestamp
      instr_cycle -= instr_total
      for col in bubble_cols:
        bubble_cycle -= df[col][i]
      for col in stall_cols:
        stall_cycle  -= df[col][i]
      
    # kernel end
    elif tag_type == 3:
      total_cycle += timestamp
      instr_cycle += instr_total
      for col in bubble_cols:
        bubble_cycle += df[col][i]
      for col in stall_cols:
        stall_cycle  += df[col][i]
  
  
  print("")
  print("--------------------------------")
  print("Core Utilization")
  print("--------------------------------")
  print("Stall         = {:.2f} %".format(stall_cycle/total_cycle*100))
  print("Bubble        = {:.2f} %".format(bubble_cycle/total_cycle*100))
  print("--------------------------------")
  print("Utilization   = {:.2f} %".format(instr_cycle/total_cycle*100))
  print("--------------------------------")
