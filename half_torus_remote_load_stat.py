
import csv
import sys
import os
from statistics import mean

NX = 32
NY = 16


def half_torus_delay(src_x, dest_x, dy):
  src_base_x = src_x - NX
  src_torus_x = (src_base_x/2) if (src_base_x % 2 == 0) else (NX-1-(src_base_x/2))
  dest_base_x = dest_x - NX
  dest_torus_x = (dest_base_x/2) if (dest_base_x % 2 == 0) else (NX-1-(dest_base_x/2))
  cw_dist = (dest_torus_x - src_torus_x) if (dest_torus_x > src_torus_x) else (NX + dest_torus_x - src_torus_x)
  ccw_dist = (NX-cw_dist) % NX
  x_delay = min(cw_dist, ccw_dist)
  return (2*dy) + (2*x_delay)

def parse_remote_load_stat(filename="remote_load_trace.csv"):
  # parse csv;
  try: 
    f = open(filename, "r")
  except:
    print("{} not found.".format(filename))
    return
  csv_reader = csv.DictReader(f, delimiter=",")
 
  int_delays = []
  con_delays = []
  total_delays  = []
  
  for row in csv_reader:
    src_x = int(row["src_x"]) 
    src_y = int(row["src_y"]) 
    dest_x = int(row["dest_x"]) 
    dest_y = int(row["dest_y"]) 
    dy = abs(src_y-dest_y)
    latency = int(row["latency"])
    #if row["type"] == "int":
    #  continue
    # calculate intrinsic delay;
    int_delay = 3
    int_delay += half_torus_delay(src_x, dest_x, dy)
    # congestion delay
    con_delay = latency - int_delay
    if con_delay < 0:
      print("src_x    = {}".format(src_x))
      print("src_y    = {}".format(src_y))
      print("dest_x   = {}".format(dest_x))
      print("dest_y   = {}".format(dest_y))
      print("latency  = {}".format(latency))
      print("int_delay= {}".format(int_delay))
      print("con_delay= {}".format(con_delay))
      print("++++++++++")


    total_delays.append(latency)
    int_delays.append(int_delay)
    con_delays.append(con_delay)


  # average;
  int_mean = mean(int_delays)
  con_mean = mean(con_delays)
  total_mean = mean(total_delays)
  
  #print("mean total      delay = {}".format(total_mean))
  print("mean intrinsic  delay = {:.2f}".format(int_mean))
  print("mean congestion delay = {:.2f}".format(con_mean))


# main
if __name__ == "__main__":
  os.chdir(sys.argv[1])
  parse_remote_load_stat()
