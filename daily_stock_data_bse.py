#!/usr/bin/env python
# coding: utf-8

###################### Libraries ############################
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))
from common_py.bse.functions import *

from datetime import date


###################### Main program ############################
# Following function to be run every day
create_table_bse()
load_data_bulk_bse(expand_path("~/Downloads/BSEEquityData.csv"))
