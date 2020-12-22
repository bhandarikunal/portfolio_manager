#!/usr/bin/env python
# coding: utf-8

###################### Libraries ############################
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))
from common_py.stooq.functions import *
from common_py.stock_analyzer import *
from common_py.eoddata.functions import *

from datetime import date

###################### Inputs ############################

us_meta_source = "nasdaq"

#us_source = "stooq"
us_source = "eoddata"


###################### Main program ############################
# Following function to be run every day
failure_flags = {}
bad_sources = []
bad_files = []

#Load US stocks' meta information
source = us_meta_source
try:
    load_ticker_info_nasdaq(source=source)
except:
    print(f"daily_stock_data_us.py: Error in load_ticker_info for US market using source [{source}]")
    bad_sources.append("meta_" + source)
    failure_flags["meta_" + source] = True


#Load US stocks' EOD ticker prices
#source = "stooq"
source = us_source
failure_flags[source] = False
try:
    if source == "eoddata":
        bad_files_us = load_daily_data_eoddata()
    elif source == "stooq":
        bad_files_us = load_daily_data_stooq()
    else:
        print(f"daily_stock_data_us.py: Invalid source for US market data [{source}]")
        failure_flags[source] = True
    
    if len(bad_files_us) > 0:
        bad_sources.append(source)
        bad_files = bad_files + bad_files_us
        failure_flags[source] = True
except:
    print(f"daily_stock_data_us.py: Error in load_daily_data for US market using source [{source}]")
    bad_sources.append(source)
    failure_flags[source] = True


if np.any(list(failure_flags.values())):
    file_str = ""
    if len(bad_files) > 0:
        file_str = "\n\nFailed in following files for US market:\n" + '\n'.join(bad_files)
    
    msg = f"""daily_stock_data_us.py: Failed in load daily stocks for [{', '.join(bad_sources)}] on [{date.today()}]
    {file_str}"""
    
    send_email(message = msg,
              subject = f"Failed in load daily stocks US for [{', '.join(bad_sources)}] on [{date.today()}]"
               + file_str)
else:
    send_email(message = f"daily_stock_data_us.py: Load daily US data successful {date.today()}",
              subject = f"Success in daily US stock data on [{date.today()}]")

#Analyze and generate stock recommendations
if not failure_flags[us_source]:
    print(f"daily_stock_data_us.py: Calling stock analyzer for US stocks")
    
    select_tickers = get_ticker_recommendations(max_recommend=50)
    
    for criteria, tickers in select_tickers.items():
        send_email(message=f"List of recommended possibly value stocks based on {criteria}:",
                   subject=f"US Top Value Stocks {criteria}",
                   df=tickers)
