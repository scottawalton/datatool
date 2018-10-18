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


def csv_from_excel(path_to_files=os.getcwd()):

    path = path_to_files + '/*.xls*'
    files = glob.glob(path)

    for i in files:
        file = os.path.basename(i)
        filename = os.path.splitext(file)[0]
        xls_file = pd.ExcelFile(i, index_col=None, dtype=object)
        if len(xls_file.sheet_names) > 1:
            try:
                os.mkdir(filename)
            except:
                print('blahhhh')
                pass
            for i in xls_file.sheet_names:
                file = pd.read_excel(xls_file, i, index_col=None, dtype=object)
                file.to_csv(filename + '/' + i + '.csv', quoting=csv.QUOTE_ALL, index = False)

        else:
            print(len(xls_file.sheet_names))
            xls_file.to_csv('clean/' + filename + '.csv',quoting=csv.QUOTE_ALL, index = False)


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
        # testing including in the if, after the loop
        for x in list:
            if x in df.columns.values:
                print( x + ' column already exists')
            else:
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
                df.at[index, col] = rank

        # No commas

        else:
            if df.at[index, col].notnull():
                print('value already exists: ' + df.loc[index, col])
            else:
                df.set_value(index, new_col, x)

    # Get rid of 'nan'

    df[df == 'nan'] = np.nan


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

# Remove non numberic characters from phone numbers

def clean_phones(df, phones='Phone'):
    df[phones] = df[phones].replace(r'[^0-9]','', regex=True)
    print('Successfully cleaned ' + phones + ' column')

def split_emails(df, emails):

    # Split Emails from one column to three

    df['Email 1'] = df['Emails'].str.extract('(.*?@.*?\....),?',expand=True)
    df['Email 2'] = df['Emails'].str.extract('.*@.*\....,\s(.*@.*\....)',expand=True)
    df['Email 3'] = df['Emails'].str.extract('.*@.*\....,\s.*@.*\....,\s(.*@.*\....)',expand=True)

def fix_zp_dates(df, col=None):
    if col == None:
        cols = ['Birth Date', 'Inquiry Date', 'Last Att. Date']
        for x in cols:
            df[x] = pd.to_datetime(df[x])
            df[x].dt.strftime('%m-%d-%Y').astype(str)
    else:
        x = col
        df[x] = pd.to_datetime(df[x])
        df[x].dt.strftime('%m-%d-%Y').astype(str)

def strip_whitespace(df, column=None):

    # Strips all leading whitespace and newline chars
    c = column

    if c == None:
        for c in df.columns:
            if df[c].dtypes == object:
                df[c] = pd.core.strings.str_strip(df[c])
                df[c] = df[c].str.replace('\n', '')
                df[c] = df[c].str.replace(r'\r',' ', regex=True)
                df[c] = df[c].str.replace(r'\n',' ', regex=True)
                df[c] = df[c].str.replace(r'\v',' ', regex=True)
    else:
        if df[c].dtypes == object:
            df[c] = pd.core.strings.str_strip(df[c])
            df[c] = df[c].str.replace(r'\r',' ', regex=True)
            df[c] = df[c].str.replace(r'\n',' ', regex=True)
            df[c] = df[c].str.replace(r'\v',' ', regex=True)


    return df

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




def probably_useless(df, df2, index):

    # Takes two files with a unique identifier, prioritizes one and merges the data together where it can.

        df.set_index(index, inplace=True)
        df2.set_index(index, inplace=True)

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
