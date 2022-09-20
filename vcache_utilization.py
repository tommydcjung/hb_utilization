import pandas as pd

NUM_VCACHE = 32

def parse_vcache_stat():
  df = pd.read_csv("vcache_stats.csv")
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
  total_cycle = (float(end_timestamp - start_timestamp) * NUM_VCACHE)
  start_df = df[df["global_ctr"]==start_timestamp]
  end_df   = df[df["global_ctr"]==end_timestamp]

  # assert that you grabbed correctly.
  assert len(start_df["time"]) == NUM_VCACHE
  assert len(end_df["time"]) == NUM_VCACHE

  load_cycle = float(sum(end_df["instr_ld"]) - sum(start_df["instr_ld"]))
  store_cycle = float(sum(end_df["instr_st"]) - sum(start_df["instr_st"]))
  miss_cycle = float(sum(end_df["stall_miss"]) - sum(start_df["stall_miss"]))
  stall_rsp_cycle = float(sum(end_df["stall_rsp"]) - sum(start_df["stall_rsp"]))
  idle_cycle = total_cycle - load_cycle - store_cycle - miss_cycle - stall_rsp_cycle

  print("")
  print("--------------------------------")
  print("Vcache Utilization")
  print("--------------------------------")
  print("Idle        = {:.2f} %".format(idle_cycle/total_cycle*100))
  print("Store       = {:.2f} %".format(store_cycle/total_cycle*100))
  print("Load        = {:.2f} %".format(load_cycle/total_cycle*100))
  print("Miss        = {:.2f} %".format(miss_cycle/total_cycle*100))
  print("Stall Rsp   = {:.2f} %".format(stall_rsp_cycle/total_cycle*100))
  print("--------------------------------")
  print("Utilization = {:.2f} %".format((load_cycle+store_cycle)/total_cycle*100))
  print("Busy cycles = {:.2f} %".format((load_cycle+store_cycle+miss_cycle)/total_cycle*100))
  print("--------------------------------")
  return
