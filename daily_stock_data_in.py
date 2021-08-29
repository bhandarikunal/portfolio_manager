#!/usr/bin/env python
# coding: utf-8

###################### Libraries ############################
import sys
import os
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
)
from common_py.bse.functions import *

from datetime import date

###################### Inputs ############################

in_source = "bse"


###################### Main program ############################
# Following function to be run every day
failure_flags = {}
bad_sources = []
bad_files = []


#Load IN stocks' holidays information
source = in_source
meta_info = "holi_"
source = meta_info + source
failure_flags[source] = False
try:
    load_holidays_bse()
except Exception as e:
    logger.warn("Error loading BSE holidays for IN market " \
                f"using source [{source}]", exc_info=True)
    bad_sources.append(source)
    failure_flags[source] = True


#Load IN stocks' meta information
source = in_source
meta_info = "meta_"
source = meta_info + source
failure_flags[source] = False
try:
    load_ticker_info_bse()
except Exception as e:
    logger.warn("Error loading BSE ticker meta information", exc_info=True)
    bad_sources.append(source)
    failure_flags[source] = True


#Load IN stocks' daily prices
source = in_source
failure_flags[source] = False
try:
    if source == "bse":
        bad_files_in = load_daily_data_bse()
    else:
        logger.warn("Error - Invalid source for daily stock price data " \
                    f"for IN market [{source}]", exc_info=True)
        failure_flags[source] = True
    
    if len(bad_files_in) > 0:
        bad_sources.append(source)
        bad_files = bad_files + bad_files_in
        failure_flags[source] = True
except Exception as e:
    logger.warn("Error loading IN market stock price data " \
                f"using source [{source}]", exc_info=True)
    bad_sources.append(source)
    failure_flags[source] = True


#Send email notification about success / failure
if np.any(list(failure_flags.values())):
    file_str = ""
    if len(bad_files) > 0:
        file_str = "\n\nFailed in following files for IN market:\n" \
                   '\n'.join(bad_files)
    
    msg = "daily_stock_data_in.py: Failed in load daily IN stocks for " \
          f"[{', '.join(bad_sources)}] on [{date.today()}] {file_str}"
    
    send_email(message = msg,
              subject = "Failed in load daily IN stocks for " \
                        f"[{', '.join(bad_sources)}] on [{date.today()}]"
                        + file_str)
else:
    send_email(message = "daily_stock_data_in.py: Load daily IN data " \
                         f"successful {date.today()}",
              subject = f"Success in daily IN stock data on [{date.today()}]")

