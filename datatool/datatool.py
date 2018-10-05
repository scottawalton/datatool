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
    parser.add_argument('-W', '--whitespace',help="Preserve whitespace")
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

        df = procedures.load(args.filename, args.filepath)
        df2 = procedures.load('Prospects.csv', args.filepath)
        df3 = procedures.load('memberships.csv', args.filepath)

        df = df.append(df2, sort=False)

        procedures.clean_phones(df, phones=' Phone')
        procedures.clean_phones(df, phones=' Phone Alt.')
        df[' Program'] = df[' Program'].str.replace('Program: ', '')
        df.columns = df.columns.str.strip()


        procedures.fix_zp_dates(df, 'Birthdate')
        procedures.fix_zp_dates(df, 'Enrollment Date')

        df['Full Name'] = df['First Name'] +' ' +  df['Last Name']

        df3.sort_values('CustNum', inplace=True, ascending=False)

        df3 = df3.groupby(['First Name','Last Name'], as_index=False).head(1)

        df3.to_csv('mems_' + args.filename + '.csv', index=False, quoting=1)

        adults = pd.DataFrame()
        parents = pd.DataFrame()

        test = df3.iloc[23]
        for i in df['Mother'].str.upper().tolist():
            if not(isinstance(i, float)):
                for index, row in df3.iterrows():
                    if row['First Name'].upper() in i and row['Last Name'].upper() in i:
                        parents = parents.append(row)

        for i in df['Father'].str.upper().tolist():
            if not(isinstance(i, float)):
                for index, row in df3.iterrows():
                    if row['First Name'].upper() in i and row['Last Name'].upper() in i:
                        parents = parents.append(row)

        for i in df['Full Name'].str.upper().tolist():
            if not(isinstance(i, float)):
                for index, row in df3.iterrows():
                    if row['First Name'].upper() in i and row['Last Name'].upper() in i:
                        adults = adults.append(row)

        remainder = df3.loc[~df3['CustNum'].isin(parents['CustNum'])]
        remainder = remainder.loc[~remainder['CustNum'].isin(adults['CustNum'])]

        # for index, row in df3.iterrows():
        #
        #     if (s for s in df['Mother'].str.upper().tolist() if row['First Name'].upper() in s and row['Last Name'].upper() in s):
        #         parents = parents.append(row)
        #
        #     elif (s for s in df['Father'].str.upper().tolist() if row['First Name'].upper() in s and row['Last Name'].upper() in s):
        #         parents = parents.append(row)
        #
        #     elif (s for s in df['Full Name'].str.upper().tolist() if (row['First Name'].upper() in s) and (row['Last Name'].upper() in s)):
        #         adults = adults.append(row)


        parents.drop_duplicates(inplace=True)



        test = pd.merge(df, df3, on='Phone').reset_index()
        test = test[pd.notnull(test['Phone'])]

        test.to_csv('test' + '.csv', index=False, quoting=1)

        adults.to_csv('adults' + '.csv', index=False, quoting=1)
        parents.to_csv('parents' + '.csv', index=False, quoting=1)
        remainder.to_csv('remainder' + '.csv', index=False, quoting=1)



        #
        # procedures.fix_ranks(df)
        # procedures.strip_whitespace(fin)
        #
        # fin['LastUpdate'] = pd.to_datetime(fin['LastUpdate'])
        # fin['FirstName'] = fin['FirstName'].str.upper()
        # fin['LastName'] = fin['LastName'].str.upper()
        #
        # fin = fin.sort_values('LastUpdate', ascending=False).groupby(['FirstName', 'LastName'], as_index=False).head(1)
        #
        # adults = pd.DataFrame(columns=fin.columns.values)
        # parents = pd.DataFrame(columns=fin.columns.values)
        #
        # for index, row in fin.iterrows():
        #     if row['FirstName'] in df['First Name'].str.upper().tolist():
        #         if row['LastName'] in df['Last Name'].str.upper().tolist():
        #             adults = adults.append(row)
        #         elif row['LastName'] in df['Middle Name'].str.upper().tolist():
        #             adults = adults.append(row)
        #     else:
        #         for i in df['Guardians'].str.upper().tolist():
        #             if not(isinstance(i, float)):
        #                 if row['FirstName'] in i and row['LastName'] in i:
        #                     parents = parents.append(row)
        #
        #                 elif df['Last Name'].str.upper().tolist().count(row['LastName']) == 1:
        #                     parents = parents.append(row)
        #
        #                 else:
        #                     ## This slows everything down to snail speed, but its fine for now
        #                     for x in df['Guardian 2'].str.upper().tolist():
        #                         if not(isinstance(x, float)):
        #                             if row['FirstName'] in x and row['LastName'] in x:
        #                                 parents = parents.append(row)
        #
        #
        # fin = fin.loc[~fin['CustNum'].isin(adults['CustNum'])]
        #
        # fin = fin.loc[~fin['CustNum'].isin(parents['CustNum'])]
        #
        # print('\a')



        # leadKrav = procedures.load('Lead-Krav-Maga.csv', args.filepath)
        # leadKidsFit = procedures.load('Lead-Kids_Fitness.csv', args.filepath)
        # leadKidsKrav = procedures.load('Lead_Kids_Krav-Maga.csv', args.filepath)
        # leadFit = procedures.load('Fitness Leads_1.csv', args.filepath)
        # alumni = procedures.load('Alumni List_1.csv', args.filepath)
        #
        # moreThan2 = pd.DataFrame(columns=leadFit.columns.values)
        #
        # dataframes = [leadKrav, leadKidsFit, leadKidsKrav, leadFit]
        #
        # for i in dataframes:
        #     for index, row in i.iterrows():
        #         print(dataframes.remove(i))
        #         for df in dfs:
        #             if row in df:
        #                 moreThan2 = moreThan2.append(row)



        # Apply changes as specified by args

        if args.noranks:
            procedures.fix_ranks(df, args.ranks, args.programs)

        if args.whitespace:
            procedures.strip_whitespace(df)

        # Handle RainMaker files

        if args.type == 'RM':
            df = software.rm.RMfix(df)

        # Output file
        df.to_csv('clean_' + args.filename + '.csv', index=False, quoting=1)
        #fin.to_csv('financials_' + args.filename + '.csv', index=False, quoting=1)
