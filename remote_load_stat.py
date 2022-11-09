
FILENAME = "profile.log"


def parse_remote_load_stat():
  try: 
    f = open(FILENAME, "r")
  except:
    print("{} not found.".format(FILENAME))
    return
  
  count = 0
  latency = 0

  lines = f.readlines()
  for line in lines:
    stripped = line.strip()
    if stripped.startswith("remote_load_start,"):
      words = stripped.split(",")
      count -= int(words[3])
      latency -= int(words[4])
    elif stripped.startswith("remote_load_end,"):
      words = stripped.split(",")
      count += int(words[3])
      latency += int(words[4])


  average_latency = 0 if count == 0 else latency/count
  print("--------------------------------")
  print("Remote Load Stat")
  print("--------------------------------")
  print("Count            = {}".format(count))
  print("Average Latency  = {:.3f}".format(average_latency))
  print("--------------------------------")
