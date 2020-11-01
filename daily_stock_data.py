#!/usr/bin/env python
# coding: utf-8

###################### Libraries ############################
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))
from common_py.stooq.functions import *
from common_py.bse.functions import *

from datetime import date


###################### Main program ############################
# Following function to be run every day
try:
    load_daily_data_stooq()
    load_daily_data_bse()
    send_email(message = f"Stooq: Load daily data successful {date.today()}",
              subject = f"daily stooq data {date.today()}")
except:
    send_email(message = f"Load daily data failed {date.today()}",
              subject = f"daily stooq data {date.today()}")
    raise

