import pandas as pd

NUM_VCACHE = 32

def parse_vcache_stat(filename="vcache_stats.csv"):
  try:
    df = pd.read_csv(filename)
  except:
    print("{} not found.".format(filename))
    return

  tags = df["tag"]
  timestamps = df["global_ctr"]

  # find start and end timestamp
  start_timestamp = (2**32)-1
  end_timestamp = 0
  for i in range(len(tags)):
    tag = tags[i]
    timestamp = timestamps[i]
    tag_type = (0xc0000000 & tag) >> 30

    # kernel start
    if tag_type == 2:
      if start_timestamp > timestamp:
        start_timestamp = timestamp
    # kernel end
    elif tag_type == 3:
      if end_timestamp < timestamp:
        end_timestamp = timestamp

  # calculate cycles
  start_df = df[df["global_ctr"]==start_timestamp]
  end_df   = df[df["global_ctr"]==end_timestamp]
  assert len(start_df["time"]) == len(end_df["time"])
  NUM_VCACHE = len(start_df["time"])
  total_cycle = (float(end_timestamp - start_timestamp) * NUM_VCACHE)

  load_cycle = float(sum(end_df["instr_ld"]) - sum(start_df["instr_ld"]))
  store_cycle = float(sum(end_df["instr_st"]) - sum(start_df["instr_st"]))
  miss_cycle = float(sum(end_df["stall_miss"]) - sum(start_df["stall_miss"]))
  stall_rsp_cycle = float(sum(end_df["stall_rsp"]) - sum(start_df["stall_rsp"]))
  idle_cycle = total_cycle - load_cycle - store_cycle - miss_cycle - stall_rsp_cycle

  # vcache stat
  vcache_stat = {}
  vcache_stat["total"] = total_cycle
  vcache_stat["load"] = load_cycle
  vcache_stat["store"] = store_cycle
  vcache_stat["miss"] = miss_cycle
  vcache_stat["stall_rsp"] = stall_rsp_cycle
  vcache_stat["idle"] = idle_cycle
  return vcache_stat

def print_vcache_stat(stat):
  print("")
  print("--------------------------------")
  print("Vcache Utilization")
  print("--------------------------------")
  print("Idle        = {:.2f} %".format(stat["idle"]/stat["total"]*100))
  print("Store       = {:.2f} %".format(stat["store"]/stat["total"]*100))
  print("Load        = {:.2f} %".format(stat["load"]/stat["total"]*100))
  print("Miss        = {:.2f} %".format(stat["miss"]/stat["total"]*100))
  print("Stall Rsp   = {:.2f} %".format(stat["stall_rsp"]/stat["total"]*100))
  print("--------------------------------")
  print("Utilization = {:.2f} %".format((stat["store"]+stat["load"])/stat["total"]*100))
  print("Busy cycles = {:.2f} %".format((stat["store"]+stat["load"]+stat["miss"])/stat["total"]*100))
  print("--------------------------------")
  return
