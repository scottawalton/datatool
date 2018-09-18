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



def load(filename, filepath):

    # Load single file in

    data = filepath + '/' + filename
    while True:
        try:
            df = pd.read_csv(data, index_col=None, dtype=object)
            return df
        except:
            df = pd.read_csv(data, index_col=None, dtype=object, encoding="ISO-8859-1" )
            return df

def split_phones(df, phones):

    # Split Phones from one column to four

    df['Mobile'] = df['Phone Numbers'].str.extract('(...-...-....)\(M\)',expand=True)
    df['Mobile 2'] = df['Phone Numbers'].str.extract('...-...-....\(M\).*?(...-...-....)\(M\)',expand=True)
    df['Mobile 3'] = df['Phone Numbers'].str.extract('...-...-....\(M\).*?...-...-....\(M\).*?(...-...-....)\(M\)',expand=True)
    df['Home'] = df['Phone Numbers'].str.extract('(...-...-....)\(H\)',expand=True)
    df['Mobile'] = df['Phone Numbers'].str.extract('(...-...-....)\(C\)',expand=True)
    df['Mobile 2'] = df['Phone Numbers'].str.extract('...-...-....\(C\).*?(...-...-....)\(C\)',expand=True)
    df['Mobile 3'] = df['Phone Numbers'].str.extract('...-...-....\(C\).*?...-...-....\(C\).*?(...-...-....)\(C\)',expand=True)
    df = df.drop('Phone Numbers', 1)

def split_emails(df, emails):

    # Split Emails from one column to three

    df['Email 1'] = df['Emails'].str.extract('(.*?@.*?\....),?',expand=True)
    df['Email 2'] = df['Emails'].str.extract('.*@.*\....,\s(.*@.*\....)',expand=True)
    df['Email 3'] = df['Emails'].str.extract('.*@.*\....,\s.*@.*\....,\s(.*@.*\....)',expand=True)



def strip_whitespace(df):

    # Strips all leading whitespace and newline chars

    for c in df.columns:
        if df[c].dtypes == object:
            df[c] = pd.core.strings.str_strip(df[c])
            df[c] = df[c].str.replace('\n', '')



def fix_ranks(df, ranks='Current Ranks', programs='Programs'):

    # Create columns based on unique program values

    if programs in df:
        list = []
        for x in df[programs].unique():
            if type(x) == float and np.isnan(x):
                pass
            else:
                y = []
                y = x.split(', ')
                for z in y:
                    if z not in list:
                        list.append(z)

    for x in list:
        df[x] = ""

    # Assign Ranks to respective columns

    for index, x in df[ranks].iteritems():

        new_col = str(df.iloc[index][programs])
        x = str(x)

        # If there are commas

        if ',' in new_col or x:
            new_col = new_col.split(', ')
            x = x.split(', ')

            for rank, col in zip(x, new_col):
                df.set_value(index, col, rank)

        # No commas

        else:
           df.set_value(index, new_col, x)

    # Get rid of 'nan'

    df[df == 'nan'] = np.nan


# If members are given in a comma seperated list, seperate into seperate columns

def tidy_split(df, column='Members', sep=', ', keep=False):
    indexes = list()
    new_values = list()
    df = df.dropna(subset=[column])
    for i, presplit in enumerate(df[column].astype(str)):
        values = presplit.split(sep)
        if keep and len(values) > 1:
            indexes.append(i)
            new_values.append(presplit)
        for value in values:
            indexes.append(i)
            new_values.append(value)
    new_df = df.iloc[indexes, :].copy()
    new_df[column] = new_values
    df = new_df
    return df


# Remove non numberic characters from phone numbers

def clean_phones(df, phones):
    df[phones] = df[phones].replace(r'[^0-9]','', regex=True)
    print(df[phones])


def fix_zp_dates(df):
    cols = ['Birth Date', 'Mbr. Begin Date', 'Date Added', 'Last Att. Date', 'Mbr. End Date', 'First Bill Due', 'Next Payment Due Date']
    for x in cols:
        df[x] = pd.to_datetime(df[x])
        df[x].dt.strftime('%m-%d-%Y').astype(str)

def probably_useless(df, df2):

    # Takes two files with a unique identifier, prioritizes one and merges the data together where it can.

        df.set_index('MBSystemID', inplace=True)
        df2.set_index('MBSystemID', inplace=True)

        intersect_MB = pd.DataFrame(columns=df.columns.values)
        intersect_RM = pd.DataFrame(columns=df.columns.values)
        outer = pd.DataFrame(columns=df.columns.values)

        for index, row in df.iterrows():
            if index in df2.index.values and index not in intersect_MB.index.values:
                intersect_MB = intersect_MB.append(row)
            elif index not in outer.index.values:
                outer = outer.append(row)

        for index, row in df2.iterrows():
            if index in df.index.values and index not in intersect_RM.index.values:
                intersect_RM = intersect_RM.append(row)
            elif not index in outer.index.values:
                outer = outer.append(row)

        priority = intersect_RM.combine_first(intersect_MB)
        for i in outer.index.values:
            if i in priority.index.values:
                print('what')
        df = priority.append(outer)


def csv_from_excel(path_to_files=os.getcwd()):

    path = path_to_files + '/*.xls*'
    files = glob.glob(path)

    for i in files:
        file = os.path.basename(i)
        filename = os.path.splitext(file)[0]
        xls_file = pd.read_excel(i, index_col=None, dtype=object)
        xls_file.to_csv(filename + '.csv',quoting=csv.QUOTE_ALL, index = False)




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

        df.to_csv('clean_' + args.filename, index=True, quoting=1)
