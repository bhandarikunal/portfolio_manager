#!/usr/bin/env python
# coding: utf-8

###################### Libraries ############################
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))
from common_py.stooq.functions import *

from datetime import date


###################### Main program ############################
# Following function to be run every day
try:
    load_historical_data_stooq_high_mem()
    send_email(message = "Stooq: Success in load historical data",
              subject = f"historical stooq data {date.today()}")
except:
    send_email(message = "Stooq: Failure in load historical data",
              subject = f"historical stooq data {date.today()}")
    raise

