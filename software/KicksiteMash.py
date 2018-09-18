import pandas as pd 
import glob
import sys, os
import numpy as np


def KicksiteMash(path_to_files=os.getcwd(), key='Id', **kwargs):


    path = path_to_files + '/*.csv'
    files = glob.glob(path)

    main = pd.DataFrame()

    for i in files:
        if "Active" in i:
            active = pd.read_csv(i, index_col=None, dtype=object)

        if "Frozen" in i:
            frozen = pd.read_csv(i, index_col=None, dtype=object)


        if "recurring" in i:
            billing = pd.read_csv(i, index_col=None, dtype=object)

        if "Prospect" in i:
            prospects = pd.read_csv(i, index_col=None, dtype=object)

        if "families" in i:
            fam  = pd.read_csv(i, index_col=None, dtype=object)

        if "Inactive" in i:
            inactive  = pd.read_csv(i, index_col=None, dtype=object)

    # Rename for merge

    #con.rename(columns={'Inquiry Date': 'Date Added'}, inplace=True)
    #ranks.rename(columns={'Person': 'Full Name'}, inplace=True)

    # Drop columns we can't use

    active.drop(['Age', 'Send SMS', 'SMS Phone Carrier', 'Inactivated on', 'Full Address'], axis=1, inplace=True, errors='ignore')

    inactive.drop(['Age', 'Send SMS', 'SMS Phone Carrier', 'Full Address'], axis=1, inplace=True, errors='ignore')

    prospects.drop(['Age', 'Send SMS', 'SMS Phone Carrier', 'Follow-up Reminder', 'Full Address'], axis=1, inplace=True, errors='ignore')

    frozen.drop(['Age', 'Send SMS', 'SMS Phone Carrier', 'Full Address'], axis=1, inplace=True, errors='ignore')

    # Clean up
        
    ## Prospects ##
    #contactTypes = {'trial': 'T', "archived": "FP"}

    #prospects['Prospect Status'] = prospects['Prospect Status'].map(contactTypes)

    #genders = {'Female': 'F', "Male": "M"}

    #prospects['Gender'] = prospects['Gender'].map(genders)

    ## Active ##

    # all sheets 
    sheets = [active, prospects, frozen, inactive]
    for sheet in sheets:
        sheet['Gender'].replace({'Female': 'F', 'Male':"M"}, inplace=True)
        if 'Guardians' in sheet.columns.values:
            sheet['Guardians', 'Guardian 2', 'Guardian 3'] = sheet['Guardians'].apply(lambda x: (pd.Series(x.split(',')) if(pd.notnull(x)) else continue))

    



    # Merge files


    # Output files

    try:
        os.mkdir('clean')
    except Exception:
        pass

    active.name = 'Active'
    billing.name = 'Memberships'
    inactive.name = 'Inactive'
    frozen.name = 'Frozen'
    prospects.name = 'Prospects'
    #complete.name = 'Complete_File'

    for i in [*sheets, billing]:

        i.to_csv('clean/' + i.name + '.csv', quoting=1, index=False)
