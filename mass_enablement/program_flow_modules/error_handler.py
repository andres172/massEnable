# -*- coding: utf-8 -*-
import sys
from utility_modules import file_utility as fu


def error(error_message):
    fu.printi(1, error_message)
    fu.printi(0, "***** MASS ENABLEMENT SCRIPT EXIT *****")
    sys.exit()
