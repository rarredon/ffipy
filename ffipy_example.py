#!/bin/python
# ------------------------------------------------------------------------------
# Purpose: an example for using the ffipy interface with FFIEC site
# Usage: python ffipy_example.py
# Author: Ryan Arredondo (ryan.c.arredondo@gmail.com)
# Date: 06/10/2017
# ------------------------------------------------------------------------------

from ffipy import FFIEC_Client


def main():
    client = FFIEC_Client()

    # Initialize variables for data pull
    ds_name = 'Call'    # Pull Call report data
    end_date = '3/31/2017'  # Pull data in reporting pd ending 3/31/17
    fiID_type = 'ID_RSSD'  # Type of financial inst identifier
    fiID = 64150    # Indentifier for Wyomin Bank and Trust
    fmt = 'PDF'  # Pull report as PDF
    outfile = 'test.pdf'  # Output file path
    return_result = False  # If True, method returns the data

    # Get report
    client.retrieve_facsimile(ds_name=ds_name, reporting_pd_end=end_date,
                              fiID_type=fiID_type, fiID=fiID,
                              facsimile_fmt=fmt, outfile=outfile,
                              return_result=False)


if __name__ == '__main__':
    main()
