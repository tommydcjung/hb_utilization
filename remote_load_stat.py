import csv

def parse_remote_load_stat(filename="remote_load_trace.csv"):
  try: 
    f = open(filename, "r")
  except:
    print("{} not found.".format(filename))
    return
 
  csv_reader = csv.DictReader(f, delimiter=",")
 
  total_count = 0
  int_count = 0
  float_count = 0
  total_latency = 0
  int_latency = 0
  float_latency = 0
  
  for row in csv_reader:
    start_cycle = int(row["start_cycle"]) 
    if row["end_cycle"] != "x":
      end_cycle = int(row["end_cycle"]) 
    src_x = int(row["src_x"]) 
    src_y = int(row["src_y"]) 
    dest_x = int(row["dest_x"]) 
    dest_y = int(row["dest_y"]) 
    type0 = row["type"]
    if row["latency"] != "x":
      latency = int(row["latency"]) 
    if type0 == "int":
      total_count += 1
      total_latency += latency
      int_count += 1
      int_latency += latency
    elif type0 == "float":
      total_count += 1
      total_latency += latency
      float_count += 1
      float_latency += latency



  total_average_latency = 0 if total_count == 0 else total_latency/total_count
  int_average_latency = 0 if int_count == 0 else int_latency/int_count
  float_average_latency = 0 if float_count == 0 else float_latency/float_count
  print("--------------------------------")
  print("Remote Load Stat")
  print("--------------------------------")
  print("Int Count              = {}".format(int_count))
  print("Int Average Latency    = {:.3f}".format(int_average_latency))
  print("Float Count            = {}".format(float_count))
  print("Float Average Latency  = {:.3f}".format(float_average_latency))
  print("Total Count            = {}".format(total_count))
  print("Total Average Latency  = {:.3f}".format(total_average_latency))
  print("--------------------------------")
