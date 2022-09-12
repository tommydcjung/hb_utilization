class DramStat:
  def __init__(self, timestamp, tag, channel_id, idle, read, write):
    self.timestamp = timestamp
    self.tag = tag
    self.channel_id = channel_id
    self.idle = idle
    self.read = read
    self.write = write

  def get_tag_type(self):
    return (self.tag & 0xc0000000) >> 30

def parse_dram_stat():
  bg_stats = []
  with open("blood_graph_stat.log") as f:
    header = f.readline()
    lines = f.readlines()
    for line in lines:
      words = line.strip().split(",")
      timestamp =   int(words[0])
      tag =         int(words[1])
      channel_id =  int(words[2])
      idle =        int(words[3])
      read =        int(words[4])
      write =       int(words[5])
      bg_stat = DramStat(timestamp, tag, channel_id, idle, read, write) 
      bg_stats.append(bg_stat)

  
  start_bg_stat = None
  start_timestamp = (2**32)-1
  end_bg_stat = None
  end_timestamp = 0

  for bg_stat in bg_stats:
    tag_type = bg_stat.get_tag_type()

    # kernel start tag
    if tag_type == 2:
      if start_timestamp > bg_stat.timestamp:
        start_timestamp = bg_stat.timestamp
        start_bg_stat = bg_stat
    # kernel end tag
    elif tag_type == 3:
      if end_timestamp < bg_stat.timestamp:
        end_timestamp = bg_stat.timestamp
        end_bg_stat = bg_stat



  # calculate utilization
  total_cycle = float(end_timestamp - start_timestamp)
  idle_cycle = float(end_bg_stat.idle - start_bg_stat.idle)
  read_cycle = float(end_bg_stat.read - start_bg_stat.read)
  write_cycle = float(end_bg_stat.write - start_bg_stat.write)
  stall_cycle = float(total_cycle - idle_cycle - read_cycle - write_cycle)
  print("--------------------------------")
  print("DRAM Utilization")
  print("--------------------------------")
  print("Idle        = {:.2f} %".format(idle_cycle/total_cycle*100))
  print("Stall       = {:.2f} %".format(stall_cycle/total_cycle*100))
  print("Read        = {:.2f} %".format(read_cycle/total_cycle*100))
  print("Write       = {:.2f} %".format(write_cycle/total_cycle*100))
  print("--------------------------------")
  print("Utilization = {:.2f} %".format((read_cycle+write_cycle)/total_cycle*100))
  print("--------------------------------")
