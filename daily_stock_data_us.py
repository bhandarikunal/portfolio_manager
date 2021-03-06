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

us_holiday_source = "nyse"

us_meta_source = "nasdaq"

#us_source = "stooq"
us_source = "eoddata"


###################### Main program ############################
# Following function to be run every day
failure_flags = {}
bad_sources = []
bad_files = []


#Load US stocks' holidays information
source = us_holiday_source
meta_info = "holi_"
source = meta_info + source
failure_flags[source] = False
try:
    load_holidays_nyse()
except Exception as e:
    print(f"daily_stock_data_us.py: Error [{e.args[0]}] in load_holidays_nyse for US market using source [{source}]")
    bad_sources.append(source)
    failure_flags[source] = True


#Load US stocks' meta information
source = us_meta_source
meta_info = "meta_"
source = meta_info + source
failure_flags[source] = False
try:
    load_ticker_info_nasdaq()
except Exception as e:
    print(f"daily_stock_data_us.py: Error [{e.args[0]}] in load_ticker_info_nasdaq for US market using source [{source}]")
    bad_sources.append(source)
    failure_flags[source] = True


#Load US stocks' etf information
source = us_meta_source
meta_info = "etf_"
source = meta_info + source
failure_flags[source] = False
try:
    load_ticker_is_etf_nasdaq()
except Exception as e:
    print(f"daily_stock_data_us.py: Error [{e.args[0]}] in load_ticker_is_etf_nasdaq for US market using source [{source}]")
    bad_sources.append(source)
    failure_flags[source] = True


#Load US stocks' EOD ticker prices
#source = "stooq"
source = us_source
failure_flags[source] = False
try:
    if source == "eoddata":
        bad_files_us = call_and_monitor(load_daily_data_eoddata)
    elif source == "stooq":
        bad_files_us = call_and_monitor(load_daily_data_stooq)
    else:
        print(f"daily_stock_data_us.py: Invalid source for US market data [{source}]")
        failure_flags[source] = True
    
    if len(bad_files_us) > 0:
        bad_sources.append(source)
        bad_files = bad_files + bad_files_us
        failure_flags[source] = True
except Exception as e:
    print(f"daily_stock_data_us.py: Error [{e.args[0]}] in load_daily_data for US market using source [{source}]")
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
print(f"daily_stock_data_us.py: Calling stock analyzer for US stocks")

moving_averages=(200,100)
ma_success = True
try:
    create_moving_averages(moving_averages = moving_averages)
except Exception as e:
    print(f"daily_stock_data_us.py: Error [{e.args[0]}] in create moving averages")
    send_email(message="", subject=f"Error creating moving averages")
    ma_success = False

if ma_success:
    try:
        load_top_tickers()
    except Exception as e:
        print(f"daily_stock_data_us.py: Error [{e.args[0]}] loading top tickers")
        send_email(message="", subject=f"Error loading top tickers")


try:
    load_future_earnings_yahoo()
except Exception as e:
    print(f"daily_stock_data_us.py: Error [{e.args[0]}] loading earnings calendar")
    send_email(message="", subject=f"Error loading earnings calendar")


for fn in [2,1]:
    failed_to_recommend = False
    try:
        if fn == 1:
            if not ma_success:
                print(f"daily_stock_data_us.py: Skipping stock recommendations 2 due to failed create MA")
                continue
            select_tickers = get_ticker_recommendations_2(moving_averages=moving_averages,
                                                          max_recommend=100,
                                                          create_ma_table=False
                                                         )
        elif fn == 2:
            select_tickers = get_ticker_recommendations(ma=moving_averages, max_recommend=100)
    except Exception as e:
        print(f"daily_stock_data_us.py: Error [{e.args[0]}] in getting stock recommendations")
        failed_to_recommend = True

    if not failed_to_recommend:
        for criteria, tickers in select_tickers.items():
            send_email(message=f"List of recommended possibly value stocks based on {criteria}:",
                       subject=f"US Top Value Stocks {criteria}",
                       df=tickers)
    else:
        send_email(message="", subject=f"Failed in US Top Value Stocks")

archive_top_tickers()
