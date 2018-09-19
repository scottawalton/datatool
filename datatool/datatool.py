import pandas as pd
import glob
import sys, os
import numpy as np
import argparse
import re
import software
import datetime
import xlrd
import csv
import procedures

# If called as executable

if __name__ == '__main__':

    # Handle arguments

    parser = argparse.ArgumentParser(description="Cleans up Spark's csv files")
    parser.add_argument('-r', '--ranks', type=str, default='Current Ranks', metavar='', help='Name of Rank column')
    parser.add_argument('-E', '--emails', type=str, default='Emails', metavar='', help='Name of Emails column')
    parser.add_argument('-P', '--phones', type=str, default='Phone Numbers', metavar='', help='Name of Phone Numbers column')
    parser.add_argument('-M', '--members_col', type=str, default='Members', metavar='', help='Name of Members column')
    parser.add_argument('-p', '--programs', type=str, default='Programs', metavar='', help='Name of Program column')
    parser.add_argument('-f', '--filepath', default=os.getcwd(), type=str, metavar='', help='Path to file')
    parser.add_argument('-R', '--noranks', action='store_true',help="Preserve ranks")
    parser.add_argument('-W', '--whitespace', action='store_false',help="Preserve whitespace")
    parser.add_argument('-t', '--type', type=str, metavar='', choices=['RM','KS', 'PM', 'MB', 'ASF', 'ZP'],help='Type of data file, e.g. RM, PM')
    parser.add_argument('-e', '--extract', action='store_false', help='Convert from Excel to CSV')
    parser.add_argument('filename', help='Csv file to clean')
    args = parser.parse_args()

    # Handle multiple file software specific exports

    if args.type == 'ZP':
        software.zp.ZPfix()

    elif args.type == 'PM':
        software.pm.PMfix()

    elif args.type == 'MB':
        software.mb.MBfix()

    elif args.type == 'KS':
        software.ks.KicksiteMash()

    elif args.type == 'ASF':
        software.asf.ASFfix()

    elif args.extract == False:
        csv_from_excel(path_to_files=os.getcwd())

    # Handle single file exports and Rainmaker files

    elif args.type is None or args.type == 'RM':

        # Add ability to parse filename + make it required


        # Load in file specified by filename

        df = load(args.filename, args.filepath)


        # Apply changes as specified by args

        if args.noranks:
            fix_ranks(df, args.ranks, args.programs)

        if args.whitespace:
            strip_whitespace(df)

        # Handle RainMaker files

        if args.type == 'RM':
            df = software.rm.RMfix(df)


        # Output file

        df.to_csv('clean_' + args.filename, index=False, quoting=1)
