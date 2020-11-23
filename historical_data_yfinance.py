#!/usr/bin/env python
# coding: utf-8

###################### Libraries ############################
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))
from common_py.yahoo.functions import *

from datetime import date
import time

if len(sys.argv) >= 2:
    restart_ticker = sys.argv[1]
    print(f"historical_data_yfinance.py: Restart ticker parameter supplied [{restart_ticker}]")
else:
    restart_ticker = ""

###################### Main program ############################
# Following function to be run every day

start_time = time.time()
try:
    if not isinstance(restart_ticker, str) or restart_ticker == "":
        drop_tables_yfinance()
    
    load_bulk_yfinance(restart_ticker = restart_ticker)
except:
    print(f"historical_data_yfinance.py: Error processing bulk yfinance library data")
    send_email(message = f"historical_data_yfinance.py: Failure in yfinance bulk stock data on [{date.today()}]",
          subject = f"historical_data_yfinance.py: Failure in yfinance bulk stock data on [{date.today()}]")
    raise

print(f"historical_data_yfinance.py: Time to run bulk yfinance data load [{time.time()-start_time}]")
send_email(message = f"historical_data_yfinance.py: Success in yfinance bulk stock data on [{date.today()}]",
      subject = f"historical_data_yfinance.py: Success in yfinance bulk stock data on [{date.today()}]")