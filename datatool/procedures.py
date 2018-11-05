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

def load(filename, filepath=os.getcwd()):
    """
    Loads the given filename found at filepath with the preferred options.

        :param filename: 
            The name of the file.
        :param filepath: 
            The path of the file.
    
    Returns:
        Pandas DataFrame
    """

    path = filepath + '/' + filename

    while True:
        try:
            df = pd.read_csv(path, index_col=None, dtype=object)
            return df
        except:
            df = pd.read_csv(path, index_col=None, dtype=object, encoding="ISO-8859-1" )
            return df

def csv_from_excel(path=os.getcwd()):
    """
    Converts all xls files at the given path to CSV files and outputs them into a directory named after the file.
    If the xls file has sheets, those are also outputted to the new directory.
        :param path=os.getcwd(: 
            The path to the xls file(s).
    """
    path = path + '/*.xls*'
    files = glob.glob(path)

    for i in files:
        file = os.path.basename(i)
        filename = os.path.splitext(file)[0]
        xls_file = pd.ExcelFile(i, index_col=None, dtype=object)
        if len(xls_file.sheet_names) > 1:
            try:
                os.mkdir(filename)
            except:
                print('Could not create directory to output to.')
                pass
            for i in xls_file.sheet_names:
                file = pd.read_excel(xls_file, i, index_col=None, dtype=object)
                file.to_csv(filename + '/' + i + '.csv', quoting=csv.QUOTE_ALL, index = False)

        else:
            file = xls_file.parse()
            file.to_csv( filename + '.csv',quoting=csv.QUOTE_ALL, index = False)

def fix_ranks(df, ranks='Current Ranks', programs='Programs'):
    """
    Distributes values in ranks column into columns created based on unique values in programs column.

        :param df:
            The dataframe to perform the operation on.
        :param ranks: 
            The values that need to be distributed.
        :param programs: 
            The values to create columns of.
    
    Returns:
        Pandas DataFrame
    """

    # Create columns based on unique program values
    if programs in df:
        uniquePrograms = set(df[programs].unique())
        if np.nan in uniquePrograms:
            uniquePrograms.remove(np.nan)
        for value in uniquePrograms.copy():
            valList = value.split(', ')
            if len(valList) > 1:
                for commaSplitValue in value.split(', '):
                    if commaSplitValue not in uniquePrograms:
                        uniquePrograms.add(commaSplitValue)
                uniquePrograms.remove(value)

        for x in uniquePrograms:
            if x not in df.columns.values:
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


    # Get rid of 'nan' in cells
    df[df == 'nan'] = np.nan
    return df

def split_phones(df, column):
    """
    Distributes the values in the phones column based on the identifier given in parentheses into either Home, Mobile, or Work.

        :param df: 
            The dataframe to perform the operation on.
        :param phones: 
            The column with phones to split.
    
        :return:
            Pandas DataFrame
    """

    df['Work'] = df[column].str.extract(r'(...-...-....)\(W\)',expand=True)
    df['Mobile'] = df[column].str.extract(r'(...-...-....)\(M\)',expand=True)
    df['Mobile 2'] = df[column].str.extract(r'...-...-....\(M\).*?(...-...-....)\(M\)',expand=True)
    df['Mobile 3'] = df[column].str.extract(r'...-...-....\(M\).*?...-...-....\(M\).*?(...-...-....)\(M\)',expand=True)
    df['Home'] = df[column].str.extract(r'(...-...-....)\(H\)',expand=True)
    df['Mobile_'] = df[column].str.extract(r'(...-...-....)\(C\)',expand=True)
    df['Mobile 2_'] = df[column].str.extract(r'...-...-....\(C\).*?(...-...-....)\(C\)',expand=True)
    df['Mobile 3_'] = df[column].str.extract(r'...-...-....\(C\).*?...-...-....\(C\).*?(...-...-....)\(C\)',expand=True)
    df['Mobile'] = df['Mobile'].combine_first(df['Mobile_'])
    df['Mobile 2'] = df['Mobile 2'].combine_first(df['Mobile 2_'])
    df['Mobile 3'] = df['Mobile 3'].combine_first(df['Mobile 3_'])
    df = df.drop([column, 'Mobile_', 'Mobile 2_', 'Mobile 3_'], axis=1)
    df = clean_phones(df, ['Mobile', 'Mobile 2', 'Mobile 3', 'Work', 'Home'])
    return df

def clean_phones(df, column='Phone'):
    """
    Removes everything but numeric characters from phone column.
        :param df: 
            The dataframe to perform the operation on.
        :param column: 
            The column to perform the operation on. (accepts lists)
        :return:
            Pandas DataFrame
    """

    if type(column) is list:
        for x in column:
            df[x] = df[x].replace(r'[^0-9]','', regex=True)
        return df
    else:
        df[column] = df[column].replace(r'[^0-9]','', regex=True)
        return df

def split_emails(df, column):
    """
    Splits the comma separated values in the emails column into a maximum of 3 different columns.

        :param df: 
            The dataframe to perform the operation on.
        :param column: 
            The column to split.
        :return:
            Pandas DataFrame
    """

    df['Email'] = df[column].str.extract(r'(.*?@.*?\....),?',expand=True)
    df['Email 2'] = df[column].str.extract(r'.*@.*\....,\s?(.*@.*\....)',expand=True)
    df['Email 3'] = df[column].str.extract(r'.*@.*\....,\s?.*@.*\....,\s?(.*@.*\....)',expand=True)
    return df

def fix_dates(df, column=None):
    """
    Converts almost any date format to MM/DD/YYYY.

        :param df: 
            The dataframe to perform the operation on.
        :param column: 
            The column to convert dates on. (accepts lists)
        
    Returns:
        Pandas DataFrame
    """
    if type(column) == list:
        for x in column:
            df[x] = pd.to_datetime(df[x])
            df[x] = df[x].dt.strftime('%m-%d-%Y')
        return df
    else:
        df[column] = pd.to_datetime(df[column])
        df[column] = df[column].dt.strftime('%m-%d-%Y')
        return df

def strip_whitespace(df, column=None):
    """
    Removes all leading and trailing whitespace. Replaces all newlines, 
    carriage returns, and invisible tab-breaks with a space. \n
    If a column isn't specified, it acts on the entire dataframe.

        :param df: 
            The dataframe to perform the operation on.
        :param phones: 
            The column to perform the operation on. (accepts lists)

    Returns:
        Pandas DataFrame
    """

    c = column

    if c == None:
        for c in df.columns:
            if df[c].dtypes == object:
                df[c] = pd.core.strings.str_strip(df[c])
                df[c] = df[c].str.replace('\n', '')
                df[c] = df[c].str.replace(r'\r',' ', regex=True)
                df[c] = df[c].str.replace(r'\n',' ', regex=True)
                df[c] = df[c].str.replace(r'\v',' ', regex=True)
    elif type(c) == list:
        for x in c:
            if df[x].dtypes == object:
                df[x] = pd.core.strings.str_strip(df[x])
                df[x] = df[x].str.replace(r'\r',' ', regex=True)
                df[x] = df[x].str.replace(r'\n',' ', regex=True)
                df[x] = df[x].str.replace(r'\v',' ', regex=True)

    else:
        if df[c].dtypes == object:
            df[c] = pd.core.strings.str_strip(df[c])
            df[c] = df[c].str.replace(r'\r',' ', regex=True)
            df[c] = df[c].str.replace(r'\n',' ', regex=True)
            df[c] = df[c].str.replace(r'\v',' ', regex=True)

    return df

def tidy_split(df, column='Members', sep=', '):
    """
    Splits a column of comma separated values into their own rows with values
    identical to the original.

        :param df: 
            The dataframe to perform the operation on.

        :param column='Members': 
            The column of values to split.

        :param sep=' ': 
            The separator

    Returns:
        Pandas DataFrame
    """

    indexes = []
    new_values = []
    for i, presplit in enumerate(df[column].astype(str)):
        for value in presplit.split(sep):
            indexes.append(i)
            new_values.append(value)
    new_df = df.iloc[indexes, :].copy() # the .copy() Prevents a warning
    new_df[column] = new_values
    df = new_df.reset_index(drop=True)
    return df

def drop_quote_rows(df):
    """
    Iterates over a dataframe and drops all rows that contain quotes as part of the string.

        :param df: 
            The dataframe to perform the operation on.

    Returns:
        Pandas DataFrame
    """

    for i in df.columns.values:
        if df[i].dtype != 'datetime64[ns]' and df[i].dtype != 'float64':
            df = df[~df[i].str.contains('"', na=False)]
    return df
