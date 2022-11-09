import dram_utilization as dr
import vcache_utilization as vc
import core_utilization as core
import wh_link_utilization as wh
import router_utilization as rtr
import remote_load_stat as rl

import os
import sys

os.chdir(sys.argv[1])

dr.parse_dram_stat()
vc.parse_vcache_stat()
core.parse_vanilla_stat()
wh.parse_wh_link_stat()
rtr.parse_router_stat()
rl.parse_remote_load_stat()
