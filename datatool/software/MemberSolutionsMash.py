import pandas as pd
import glob
import sys, os
import numpy as np
import procedures

def MSfix(path_to_files=os.getcwd(), **kwargs):

    path = path_to_files + '/*.csv'
    files = glob.glob(path)

    main = pd.DataFrame()

    for i in files:
        if "accounts" in i:
            students = pd.read_csv(i, index_col=None, dtype=object)

        if "notes" in i:
            notes = pd.read_csv(i, index_col=None, dtype=object)

        if "payments" in i:
            payments = pd.read_csv(i, index_col=None, dtype=object)


    # Drop columns we can't use

    students.drop([ 'A/R start date','A/R # of payments','A/R cancellation notice',
                    'A/R payment amount', 'Cancel Notice', 'Pay Source', 'original_payment_term',
                    'sales_tax','down_payment', 'transfer amount', 'service_charge',
                    'outstanding_balance', 'balance', 'cash_price', 'first_payment_due'], axis=1, inplace=True)

    # Clean up

    ## Students ##

    students = procedures.tidy_split(students, sep='; ')

    procedures.clean_phones(students, 'home phone')
    procedures.clean_phones(students, 'work phone')
    procedures.clean_phones(students, 'cell phone')

    students.rename(columns={'Cycle Frequency': 'Payment Frequency', 'eft type': 'C or S',
                            'Buyer last name': 'Parent Last Name', 'Buyer first name': 'Parent First Name'}, inplace=True)

    students['Payment Frequency'].replace('Monthly', '30', inplace=True)
    students['C or S'].replace('Checking Debit', 'C', inplace=True)


    students['service_expiration'] = np.where((students['Account Type'] == 'Ongoing') & (students['service_expiration'].isnull()),
                                                '12/31/2099', students['service_expiration'])




    ## Payments ##

    ## Notes ##
    notes = notes[notes['Remarks/Amount'].notnull()]
    notes['Remarks/Amount'] = notes['Remarks/Amount'].str.strip()
    notes = notes.groupby('MSIAccount#').agg({'Remarks/Amount':' -- '.join}).reset_index()

    ## Merge files ##

    # complete = pd.DataFrame()
    # for i in sheets:
    #     complete = complete.append(i, sort=False)
    #
    # complete['Members'] = complete['First Name'] + (" " + complete['Last Name'] if len(complete['Last Name']) != 0 else "")
    # complete = complete.merge(billing, on='Members', how='left')

    ## Output files ##

    try:
        os.mkdir('clean')
    except Exception:
        pass

    students.name = 'Contacts'
    notes.name = 'Notes'
    payments.name = 'Payments'

    for i in [students, notes, payments]:

        i.to_csv('clean/' + i.name + '.csv', quoting=1, index=False)
