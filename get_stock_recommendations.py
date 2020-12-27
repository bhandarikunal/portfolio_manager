#!/usr/bin/env python
# coding: utf-8

###################### Libraries ############################
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))
from common_py.functions import *
from common_py.stock_analyzer import *

from datetime import date

###################### Inputs ############################

###################### Main program ############################
failed_to_recommend = False
try:
    #select_tickers = get_ticker_recommendations(ma=(200,100), max_recommend=50)
    select_tickers = get_ticker_recommendations_2(moving_averages=(200,100),
                                                  max_recommend=50,
                                                  create_ma_table=False
                                                 )
except:
    failed_to_recommend = True
    print(f"daily_stock_data_us.py: Failed in getting stock recommendations")
    #raise

if not failed_to_recommend:
    for criteria, tickers in select_tickers.items():
        send_email(message=f"List of recommended possibly value stocks based on {criteria}:",
                   subject=f"US Top Value Stocks {criteria}",
                   df=tickers)
else:
    send_email(message="", subject=f"Failed in US Top Value Stocks")
    raise
