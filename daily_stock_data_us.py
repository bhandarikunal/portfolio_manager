#!/usr/bin/env python
# coding: utf-8

###################### Libraries ############################
import sys
import os
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
)

from common_py.nyse.functions import *
from common_py.nasdaq.functions import *
from common_py.yahoo.functions import *
from common_py.stooq.functions import *
from common_py.eoddata.functions import *
from common_py.zacks.functions import *
from common_py.stock_functions import *
from common_py.stock_analyzer import *

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
    logger.warning("Error - Unable to load holiday information "
                + "for US market using source "
                + f"[{source}]", exc_info = True)
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
    logger.warning("Error loading meta information about tickers "
                + f"for US market using source [{source}]", exc_info = True)
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
    logger.warning("Error loading ticker to ETF map using source "
                + f"[{source}]", exc_info = True)
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
        logger.warning(f"Error - Invalid source for US market data [{source}]",
                    exc_info = True)
        failure_flags[source] = True
    
    if len(bad_files_us) > 0:
        bad_sources.append(source)
        bad_files = bad_files + bad_files_us
        failure_flags[source] = True
except Exception as e:
    logger.warning("Error loading new stock price data "
                + f"[{source}]", exc_info = True)
    bad_sources.append(source)
    failure_flags[source] = True


if np.any(list(failure_flags.values())):
    file_str = ""
    if len(bad_files) > 0:
        file_str = "\n\nFailed in following files for US market:\n" \
                   '\n'.join(bad_files)
    
    msg = "daily_stock_data_us.py: Failed in load daily stocks for " \
          f"[{', '.join(bad_sources)}] on [{date.today()}] {file_str}"
    
    send_email(message = msg,
              subject = "Failed in load daily stocks US for " \
                        f"[{', '.join(bad_sources)}] on [{date.today()}]"
                        + file_str)
else:
    send_email(message = "daily_stock_data_us.py: Load daily US data "
                         + f"successful {date.today()}",
              subject = f"Success in daily US stock data on [{date.today()}]")

#Analyze and generate stock recommendations
logger.info("daily_stock_data_us.py: Calling stock analyzer for US stocks")

#moving_averages=(1400,700,350,200,100)
moving_averages=(500,200,100)
ma_success = True
try:
    create_moving_averages(moving_averages = moving_averages)
except Exception as e:
    logger.warning("Error creating moving averages", exc_info = True)
    send_email(message="", subject="Error creating moving averages")
    ma_success = False

if ma_success:
    try:
        load_top_tickers_zacks()
    except Exception as e:
        logger.warning("Error loading top tickers based on ETFs",
                    exc_info = True)
        send_email(message="", subject="Error loading top ETF tickers")

try:
    load_future_earnings_yahoo()
except Exception as e:
    logger.warning("Error loading earnings calendar", exc_info = True)
    send_email(message="", subject="Error loading earnings calendar")

for fn in [3]:
    failed_to_recommend = False
    
    fn_desc = "proper_ma" if fn == 1 else \
              "basic_ma" if fn == 2 else "big_cap_ma_no_ch"
    
    try:
        if fn == 1:
            if not ma_success:
                logger.warning("daily_stock_data_us.py: Skipping stock "
                            + "recommendations 2 due to failed create MA")
                continue
            select_tickers = get_ticker_recommendations_2(
                    moving_averages=moving_averages,
                    max_recommend=100,
                    create_ma_table=False
            )
        elif fn == 2:
            select_tickers = get_ticker_recommendations(ma=moving_averages,
                                                        max_recommend=100)
        elif fn == 3:
            select_tickers = get_ticker_recommendations_2(
                moving_averages=moving_averages,
                max_recommend=100,
                create_ma_table=False,
                min_price=10,
                avg_vol=1e6,
                mcap_mil=20000,
                china_flag=False,
                big_cap_mcap_mil=200000,
                p_upside=0.20
            )            
    except Exception as e:
        logger.warning("Error getting stock recommendations", exc_info = True)
        failed_to_recommend = True

    if not failed_to_recommend:
        for criteria, tickers in select_tickers.items():
            send_email(message="List of recommended possibly value "
                               + f"stocks based on {criteria}:",
                       subject=f"US Top Value Stocks {criteria} {fn_desc}",
                       df=tickers)
    else:
        send_email(message="", subject="Failed in US Top Value Stocks")

archive_top_tickers()
