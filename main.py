import dram_utilization as dr
import vcache_utilization as vc
import core_utilization as core
import wh_link_utilization as wh

import os
import sys
os.chdir(sys.argv[1])

dr.parse_dram_stat()
vc.parse_vcache_stat()
core.parse_vanilla_stat()
wh.parse_wh_link_stat()
