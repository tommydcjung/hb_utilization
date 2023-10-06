import dram_utilization as dr
import vcache_utilization as vc
import core_utilization as core
import wh_link_utilization as wh
#import router_utilization as rtr
#import remote_load_stat as rl

import os
import sys

os.chdir(sys.argv[1])

dram_stat = dr.parse_dram_stat()
dr.print_dram_stat(dram_stat)

vc_stat = vc.parse_vcache_stat()
if vc_stat is not None:
  vc.print_vcache_stat(vc_stat)

core_stat = core.parse_vanilla_stat()
core.print_vanilla_stat(core_stat)
core.summarize_core_stall(core_stat)

#wh.parse_wh_link_stat()
#rtr.parse_router_stat()
#rl.parse_remote_load_stat()
