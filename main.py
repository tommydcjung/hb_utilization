import dram_utilization as dr
import vcache_utilization as vc

import os
import sys
os.chdir(sys.argv[1])

dr.parse_dram_stat()
vc.parse_vcache_stat()
