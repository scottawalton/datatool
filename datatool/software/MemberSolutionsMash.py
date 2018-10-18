import pandas as pd
import glob
import sys, os
import numpy as np
import procedures

def MSfix(holder="students", path_to_files=os.getcwd(), **kwargs):

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

    ### Students ###

    # Drop columns we can't use

    students.drop([ 'A/R start date','A/R # of payments','A/R cancellation notice',
                    'A/R payment amount', 'Cancel Notice', 'original_payment_term',
                    'sales_tax','down_payment', 'transfer amount', 'service_charge',
                    'outstanding_balance', 'balance', 'cash_price', 'first_payment_due'], axis=1, inplace=True)

    # Splits the semi-colon seperated members column into rows of their own
    students = procedures.tidy_split(students, sep='; ')

    # Removes all non-numeric characters from phone columns
    procedures.clean_phones(students, 'home phone')
    procedures.clean_phones(students, 'work phone')
    procedures.clean_phones(students, 'cell phone')

    # Rename columns for clarity
    students.rename(columns={'Cycle Frequency': 'Payment Frequency', 'eft type': 'C or S',
                            'Buyer last name': 'Parent Last Name', 'Buyer first name': 'Parent First Name',
                            'Pay Source': 'Payment Method'}, inplace=True)

    # Translate Payment Frequency to be importable
    students['Payment Frequency'].replace({'Monthly': '30', 'Weekly': '7', 'Every 2 weeks': '14',
                                            '24 Months': '830', 'Semi-Annual': '180'}, inplace=True)
    # Translate ACH account type to be importable
    students['C or S'].replace('Checking Debit', 'C', inplace=True)

    # Fill ongoing until cancellation members' expiration dates with 12/31/99
    students['service_expiration'] = np.where((students['Account Type'] == 'Ongoing') & (students['service_expiration'].isnull()),
                                                '12/31/2099', students['service_expiration'])

    # Get most recent membership group
    students['Acc#'], students['Mem#'] = students['MSIAccount#'].str.split('-', 1).str
    students['Mem#'] = pd.to_numeric(students['Mem#'])
    studentsMax = students.sort_values('Mem#', ascending=False).groupby('Acc#').head(1)

    # Drops all but most recent membership group
    students = students[students['MSIAccount#'].isin(studentsMax['MSIAccount#'])]

    # Translate contact types to be importable
    students['Account Status'].replace({'Active': 'S', 'Returned': 'F', 'Default': 'F' ,
                                        'Inactive': 'I', 'Complimentary': 'O'}, inplace=True)

    # Translate payment methods to be importable
    students['Payment Method'].replace({'Visa': 'CC', 'Discover': 'CC', 'Mastercard': 'CC',
                                        'Statement': 'In House', 'AMEX': 'CC'}, inplace=True)
    # Create Billing Company column based on payment methods
    students['Billing Company'] = np.where(students['Payment Method'] == 'CC', 'autoCharge',
                                        np.where(students['Payment Method'] == 'EFT', 'autoCharge',
                                            np.where(students['Payment Method'] == 'In House', 'In House', '')))

    # Creates Installments Remaining column based on amount left to finance & payment amount
    students['payments paid'].fillna(int(0), inplace=True)
    students['tmp'] = np.where(students['Amount due'].astype(float) == 0, '1', students['Amount due'])
    students['Installments Remaining'] = round((students['amount_financed'].astype(float) - \
                                                students['payments paid'].astype(float)) / students['tmp'].astype(float))
    students.drop('tmp', axis=1, inplace=True)

    # Corrects remaining installments for ongoing memberships to 9999
    students['Installments Remaining'] = np.where(students['Account Type'] == 'Ongoing', '9999', students['Installments Remaining'])

    # Fill in blank Program names
    students['Program'].fillna('Basic Membership', inplace=True)

    # If we are using the Students as membership holders:
    if holder == 'students':
        students['parent?'] = ''
        for i, row in students.iterrows():

            # Check for Parents who are also Students
            if row['Parent Last Name'].upper() in row['Members'].upper() and row['Parent First Name'].upper() in row['Members'].upper():
                print('Found Parent -- ' + row['Members'])
                students.at[i, 'parent?'] = True

        membershipHolders = pd.DataFrame()
        membershipParticipants = pd.DataFrame()

        # Split students up into groups based on account
        for name, group in students.groupby('MSIAccount#', as_index=False):

            # Take parent to be membership holder
            if True in group['parent?'].values:

                membershipHolders = membershipHolders.append(group[group['parent?'] == True], sort=False)
                membershipParticipants = membershipParticipants.append(group[group['parent?'] != True], sort=False)

            # Arbitrarily take first student to be membership holder
            else:

                membershipHolders = membershipHolders.append(group.iloc[0], sort=False)
                membershipParticipants = membershipParticipants.append(group.iloc[1:], sort=False)

        # Drop the membership from the participants so we don't have duplicate memberships
        membershipParticipants.drop(['Billing Company','Installments Remaining', 'Program','Payment Frequency',
                                'due_date','service_begin','service_expiration', 'Amount due'], axis=1, inplace=True)

        # Combine the two groups back together
        students = membershipHolders.append(membershipParticipants, sort=False)

    ### Payments ###

    ### Notes ###

    # Drops empty notes
    notes = notes[notes['Remarks/Amount'].notnull()]

    # Strips whitespace
    notes['Remarks/Amount'] = notes['Remarks/Amount'].str.strip()

    # Merges all account notes into one line, for importability
    notes['Acc#'], notes['Mem#'] = notes['MSIAccount#'].str.split('-', 1).str
    notes = notes.groupby('Acc#').agg({'Remarks/Amount':' -- '.join}).reset_index()

    ### Merge files ###

    complete = students
    complete = complete.merge(notes, on='Acc#', how='left')


    ### Output files ###

    try:
        os.mkdir('clean')
    except Exception:
        pass

    students.name = 'Contacts'
    notes.name = 'Notes'
    payments.name = 'Payments'
    complete.name = 'Complete'

    for i in [students, notes, payments, complete]:

        i.to_csv('clean/' + i.name + '.csv', quoting=1, index=False)
