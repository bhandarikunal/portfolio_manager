#!/usr/bin/env python
# coding: utf-8

###################### Libraries ############################
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))
from common_py.stooq.functions import *
from common_py.stock_analyzer import *
from common_py.bse.functions import *

from datetime import date


###################### Main program ############################
# Following function to be run every day
failure_flags = {}
bad_sources = []
bad_files = []

source = "stooq"
failure_flags[source] = False
try:
    bad_files_stooq = load_daily_data_stooq()
    
    if len(bad_files_stooq) > 0:
        bad_sources.append(source)
        bad_files = bad_files + bad_files_stooq
        failure_flags[source] = True
except:
    print(f"daily_stock_data.py: Error in load_daily_data_stooq")
    bad_sources.append(source)
    failure_flags[source] = True

source = "BSE"
failure_flags[source] = False
try:
    bad_files_bse = load_daily_data_bse()
    
    if len(bad_files_bse) > 0:
        bad_sources.append(source)
        bad_files = bad_files + bad_files_stooq
        failure_flags[source] = True
except:
    print(f"daily_stock_data.py: Error in load_daily_data_bse")
    bad_sources.append("BSE")
    failure_flags[source] = True

if np.any(list(failure_flags.values())):
    file_str = ""
    if len(bad_files) > 0:
        file_str = "\n\nFailed in following files:\n" + '\n'.join(bad_files)
    
    msg = f"""daily_stock_data.py: Failed in load daily stocks for [{', '.join(bad_sources)}] on [{date.today()}]
    {file_str}"""
    
    send_email(message = msg,
              subject = f"Failed in load daily stocks for [{', '.join(bad_sources)}] on [{date.today()}]"
               + file_str)
else:
    send_email(message = f"daily_stock_data.py: Load daily data successful {date.today()}",
              subject = f"Success in daily stock data on [{date.today()}]")
    
if not failure_flags["stooq"]:
    print(f"daily_stock_data.py: Calling stock analyzer for us stocks")
    
    select_tickers = get_ticker_recommendations(max_recommend=50)
    send_email(message="List of recommended possibly value stocks:",subject="Top Value Stocks",
               df=select_tickers)        
