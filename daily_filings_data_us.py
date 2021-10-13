#!/usr/bin/env python
# coding: utf-8

###################### Libraries ############################
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))
from common_py.sec.functions import *


###################### Main program ############################

print(f"download_sec_filings.py: Calling download_sec_archive_files")

try:
    download_sec_filings()
except Exception as e:
    logger.exception(f"download_sec_filings.py: Error",
                     exc_info=True)
    send_email(message="", subject=f"Error download_sec_filings")
    raise
send_email(message="", subject=f"Success in download_sec_filings")
