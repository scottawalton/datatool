"""
datatool - to make cleaning data easier and faster,

Created by: Scott Walton
"""

import os
import re
import glob
import datetime
import itertools

import numpy as np
import pandas as pd

import procedures

#region Software Exports
def ASF_fix(path=os.getcwd(), key="ASF ACCT#", **kwargs):


    path = path + '/*.CSV'
    files = glob.glob(path)

    # Load Files in ------------------------------------------------------------

    for i in files:
        if "CLC" in i:
            clc = pd.read_csv(i, index_col=None, dtype=object,
                    names = ["CLUB","ASF ACCT#","MBR SEQ #","FIRST NAME","LAST NAME","DOB","ALT / BARCD #"])
        if "CLM" in i:
            clm = pd.read_csv(i, index_col=None, dtype=object,
                    names = ["CLUB","STATUS CODE","ASF ACCT#","FIRST NAME","LAST NAME",
                    "STREET","CITY","STATE","ZIP","HOME PHONE","WORK PHONE","GENDER","SOCIAL SEC#",
                    "DOB","OCCUPATION","SLSPRSN","DWN PMT","TOTAL BAL","PMT AMT","# OF PMTS",
                    "# OF PMTS MADE","1ST DUE","SIGN DTE","REMAINING BAL","STRT DTE","EXP DTE",
                    "LAST PAID DATE","NXT PMT DUE","RNWL # OF MOS","RNWL PMT AMT","RNWL CASH/PIF AMT",
                    "BANK RT#","BANK ACCT#","CHK/SAV","CC#","CC HOLDER NAME","CC EXP","CARD CODE",
                    "NXT NOTICE DTE","EMAIL","ALT/BARCODE #","RENWL CODE","AUTO RNW M2M: X=No - E/O/S=Yes",
                    "RNWL 1ST DUE (0 IF ALRDY RNWD)","PMT FREQ","CELL PHONE","REMARKS","BLANK"])
        if "EMR" in i:
            emr = pd.read_csv(i, index_col=None, dtype=object,
                    names = ["ASF ACCT#","LAST NME","FIRST NME","RLTNSHP","HOME PHN","WRK PHN",
                    "LAST NME 2","FIRST NME 2","RLTNSHP 2","HOME PHN 2","WRK PHN 2"])
        if "NOT" in i:
            note = pd.read_csv(i, index_col=None, dtype=object,
                    names = ["ASF ACCT#","NOTE DATE","NOTE TIME","N/A","EMPLOYEE","NOTE"])
        if "REC" in i:
            rec = pd.read_csv(i, index_col=None, dtype=object,
                    names = ["CLUB","ASF ACCT#","RCRD DTE","STATUS","PMT TERM","NUM PMTS",
                    "PMT AMT","EXP DATE","PMTS MADE","NEXT DUE","INTERVAL","DESCRIPTION","CC/ACCT NUM",
                    "CC EXP","ROUTING","CKG/SVGS ACCT","PT SESS","SEQ NUM"])

    #Clean files up ------------------------------------------------------------

    #Notes Clean
    note['NOTE'] = note['NOTE'].str.strip()
    note = note.groupby('ASF ACCT#').agg({'NOTE':' - '.join}).reset_index()

    #Main Clean
    clm = clm.drop(["CLUB", "SLSPRSN", "DWN PMT", "TOTAL BAL","LAST PAID DATE",
    "RNWL # OF MOS","RNWL PMT AMT","RNWL CASH/PIF AMT", "NXT NOTICE DTE",
    "RENWL CODE","AUTO RNW M2M: X=No - E/O/S=Yes","RNWL 1ST DUE (0 IF ALRDY RNWD)",
    "REMARKS","BLANK"], axis=1)

    replacements = {'P': 'PIF', 'C': 'X', 'R':'X', 'Z': 'X', 'M': 'Inactive', 'V': 'CC',
        'I':'CC', 'E': 'EFT', 'F': 'EFT', 'A': 'In House', 'B': 'In House'}

    clm['STATUS CODE'] = clm['STATUS CODE'].map(replacements)

    #Emergency Contacts Clean
    # Change this to clean all columns vvvvv
    emr['ASF ACCT#'] = emr['ASF ACCT#'].str.strip()
    # Concat all cols to one - Emergency

    #Memberships Clean
    rec = rec.drop(['CLUB'], axis=1)
    # need info to be copied from main contact, but retain info on this one. right merge


    #Merge files together ------------------------------------------------------

    needs_merge = [emr, note]
    # CLC is not included because it needs to be merged separatly and then appended
    complete = clm

    for x in needs_merge:
        x.set_index("ASF ACCT#")
        complete = pd.merge(complete, x, on=key, how='left')

    print(complete['RLTNSHP 2'])

    additional = pd.merge(complete, clc, on="ASF ACCT#", how='right')
    complete = complete.append(additional, sort=False)

    return complete.to_csv('complete.csv', quoting=1)

def KS_fix(path_to_files=os.getcwd(), key='Id', **kwargs):


    path = path_to_files + '/*.csv'
    files = glob.glob(path)

    for i in files:
        if "Active" in i:
            active = pd.read_csv(i, index_col=None, dtype=object)
        else:
            active = pd.DataFrame()

        if "Frozen" in i:
            frozen = pd.read_csv(i, index_col=None, dtype=object)
        else:
            frozen = pd.DataFrame()

        if "recurring" in i:
            billing = pd.read_csv(i, index_col=None, dtype=object)
        else:
            billing = pd.DataFrame()

        if "Prospect" in i:
            prospects = pd.read_csv(i, index_col=None, dtype=object)
        else:
            prospects= pd.DataFrame()

        if "families" in i:
            fam  = pd.read_csv(i, index_col=None, dtype=object, names=['Family', 'Members', 'Created', 'Edit'])
        else:
            fam = pd.DataFrame()

        if "Inactive" in i:
            inactive  = pd.read_csv(i, index_col=None, dtype=object)
        else:
            inactive = pd.DataFrame()


    # Drop columns we can't use

    active.drop(['Age', 'Send SMS', 'SMS Phone Carrier', 'Inactivated on', 'Full Address', 'Converted to student on'], axis=1, inplace=True, errors='ignore')

    inactive.drop(['Age', 'Send SMS', 'SMS Phone Carrier', 'Full Address','Inactivated on', 'Converted to student on'], axis=1, inplace=True, errors='ignore')

    prospects.drop(['Age', 'Send SMS', 'SMS Phone Carrier', 'Follow-up Reminder', 'Full Address'], axis=1, inplace=True, errors='ignore')

    frozen.drop(['Age', 'Send SMS', 'SMS Phone Carrier', 'Full Address'], axis=1, inplace=True, errors='ignore')

    # Clean up

    ## Prospects ##

    if prospects != pd.DataFrame():
        contactTypes = {'trial': 'T', "archived": "P"}
        prospects['Prospect Status'] = prospects['Prospect Status'].map(contactTypes)
        prospects.rename(columns={'Prospect Status': 'Contact Type', 'Prospect Source': 'Source', 'Phone': 'Mobile'}, inplace=True)

    ## Frozen ##

    if frozen != pd.DataFrame():
        frozen.drop(['Frozen','Frozen on','Freeze Until'], axis=1, inplace=True)
        active = active.append(frozen, sort=False)

    ## Active ##

    if active != pd.DataFrame():
        contactTypes = {'Yes': 'S', "No": "F"}
        active['Active'] = active['Active'].map(contactTypes)
        active.rename(columns={'Active': 'Contact Type', 'Student Source': 'Source'}, inplace=True)

    ## Inactive ##

    if inactive != pd.DataFrame():
        inactive['Active'].replace({'No': 'F', 'Yes':"A"}, inplace=True)
        inactive.rename(columns={'Active': 'Contact Type','Student Source': 'Source'}, inplace=True)
        active = active.append(inactive, sort=False)

    ## Families ##

    if fam != pd.DataFrame():
        fam.drop(['Edit', 'Created'], inplace=True, axis=1)
        index = len(fam.index.values)
        for rowIndex, row in fam.iterrows():
            if not(isinstance(row['Members'], float)) and '\n' in row['Members']:
                members = row['Members'].split('\n')
                for member in members:
                    index += 1
                    fam.loc[index] = [row['Family'], member]
            fam.drop(rowIndex, inplace=True)

        fam['Members'] = fam['Members'].str.extract(r'(.*)\s\d+',expand=True)

    ## Memberships ##

    # split famliy memberships into individuals based on family file

    if fam != pd.DataFrame() and billing != pd.DataFrame():
        fam_billing = billing[pd.isnull(billing['Billable first name'])]
        billing = billing[pd.notnull(billing['Billable first name'])]
        billing['Members'] = billing['Billable first name'] + ' ' + billing['Billable last name']
        fam_billing.rename(columns={'Billable last name': 'Family'}, inplace=True)
        fam_billing = fam_billing.merge(fam, on='Family')
        billing = billing.append(fam_billing, sort=False)

        billing = billing.sort_values('Status').drop_duplicates(subset=['Members'],keep='first')

        billing.drop(['Inactivated Date','Auto Inactivated', 'Consecutive Declines',
            'Last Declined Date', 'Days until next charge', 'Billable first name',
            'Billable last name', 'Family'], axis=1, inplace=True)


    # All Sheets
    sheets = [active, prospects]
    for sheet in sheets:

        if 'Gender' in sheet.columns.values:
            sheet['Gender'].replace({'Female': 'F', 'Male':"M"}, inplace=True)

        if 'Guardians' in sheet.columns.values:
            vals = sheet['Guardians'].str.split(',', 1, expand=True)
            vals.columns = ['Guardian 1', 'Guardian 2']
            sheet['Guardian 1'], sheet['Guardian 2'] = vals['Guardian 1'], vals['Guardian 2']
            sheet.drop(['Guardians'], axis=1, inplace=True)

        if 'Phone Numbers' in sheet.columns.values:
            procedures.split_phones(sheet, 'Phone Numbers')
            sheet.drop(['Phone Numbers'], axis=1, inplace=True)

        if 'Emails' in sheet.columns.values:
            procedures.split_emails(sheet, 'Emails')
            if 'Email' in sheet.columns.values:
                sheet.drop(['Emails'], axis=1, inplace=True)

        phone_cols = ['Mobile', 'Mobile 2', 'Mobile 3', 'Home', 'SMS Phone', 'Phone Number']
        for phone in phone_cols:
            if phone in sheet.columns.values:
                procedures.clean_phones(sheet, phone)

        if 'Current Ranks' in sheet.columns.values and 'Programs' in sheet.columns.values:
            procedures.fix_ranks(sheet, ranks='Current Ranks', programs='Programs')

    ## Merge files ##

    complete = pd.DataFrame()
    for i in sheets:
        complete = complete.append(i, sort=False)

    complete['Members'] = complete['First Name'] + (" " + complete['Last Name'] if len(complete['Last Name']) != 0 else "")
    complete = complete.merge(billing, on='Members', how='left')

    ## Output files ##

    try:
        os.mkdir('clean')
    except Exception:
        pass

    active.name = 'Active'
    billing.name = 'Memberships'
    fam.name = 'Families'
    inactive.name = 'Inactive'
    frozen.name = 'Frozen'
    prospects.name = 'Prospects'
    complete.name = 'Complete_File'

    for i in [*sheets, billing, fam, complete]:

        i.to_csv('clean/' + i.name + '.csv', quoting=1, index=False)

def MS_fix(holder="students", path_to_files=os.getcwd(), **kwargs):

    path = path_to_files + '/*.csv'
    files = glob.glob(path)

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

def MB_fix(path_to_files=os.getcwd(), key='MBSystemID', **kwargs):

    path = path_to_files + '/*.csv'
    files = glob.glob(path)


    for i in files:

        if "Clients" in i:
            con = pd.read_csv(i, index_col=None, dtype=object)

        if "Notes" in i:
            notes = pd.read_csv(i, index_col=None, dtype=object)

        if "CreditCards" in i:
            fin = pd.read_csv(i, index_col=None, dtype=object)

        if "ClientRelationships" in i:
            rel = pd.read_csv(i, index_col=None, dtype=object)

        if "ClientAutopayContract" in i:
            mem = pd.read_csv(i, index_col=None, dtype=object)

        if 'CustomFields' in i:
            cus = pd.read_csv(i, index_col=None, dtype=object)

        if 'ClientIndexes' in i:
            ind = pd.read_csv(i, index_col=None, dtype=object)


    # Drop columns we can't use

    con.drop(['SpiritName', 'Dear', 'ForeignZip', 'Pager', 'FaxNumber',
     'CurrentSeries', 'BrochRequest', 'Parent', 'Location',
     'LoginName', 'Password', 'FirstClass', 'IPaddress','wspending', 'VerificationInfo',
     'SecretWord','SecretClue','SendMeReminders','Deleted','LiabilityRelease','LiabilityAgreementDate',
     'TrainerID', 'IsCompany','ExpectedIncome', 'Suspended', 'SuspendToDate','ShipAddress',
     'ShipPostalCode', 'SuspendFromDate','FirstContactDate','CloseDate','ExpectedCloseDate',
     'CloseProbability','RepID','BakCloseDate', 'RepID2','RepID3','OnlineSignUp','ShipCity','ShipState',
     'XRegionCopy','FirstClassDate','FirstApptDate','RepID4','RepID5','RepID6','ProspectStage',
     'InsuranceCompany','InsurancePolicyNum', 'CCExpireEmailSent','RefusedEmail','CloseEmailSent',
     'CloseFollowupEmailSent','ApptGenderPrefMale','MobileProvider','AutomatedContactMethod',
     'AllowMissingBillingAlert','Is3rdParty','CreatedBy', 'DeactivatedTime','StatusID','ShipCountry',
     'RewardsOptIn','AllowAccountPurchases','MergeTimeStamp','MergeEmpID','MergeClientID',
     'AccountPaymentsAllowed', 'AutoPayLimit', 'FirstVisitApptEmailSent','FirstVisitResEmailSent',
     'ReactivatedTime','LockerNo','IsSystem','MeasurementsTaken', 'LiabilityRelBy','LiabilityAgreementDate1',
     'ReferrerID','Longitude','Latitude','LockerDate','LastFormulaNotes','MBFVisitorID','ChangePassword',
     'ModifiedBy','Modified','PasswordChangeKey','EmailStatus','ConvertedDate', 'QBOID', 'HomeStudio', 'Height',
     'Bust','Waist','Hip','Girth','Inseam','Head','Shoe','Tights', 'BirthdayEmailSent', 'SourceID', 'LastClass'], axis=1, inplace=True)

    fin.drop(['BillingStreetAddress','BillingCity','BillingState','BillingZip', 'BarcodeID'], axis=1, inplace=True)

    rel.drop(['RelationID','BarcodeID1', 'BarcodeID2'], axis=1, inplace=True)

    mem.drop(['PayerBarcodeID','PayerLastName','PayerFirstName', 'TerminationDate',
    'RunDateTime', 'Contract Agreement Date', 'LocationName', 'AutoPayItemDescription'], axis=1, inplace=True)

    cus.drop(['FirstName', 'LastName', 'BarcodeID'], axis=1, inplace=True)

    notes.drop(['FirstName', 'LastName'], axis=1, inplace=True)



    # Clean Up

    ind = ind[ind['IndexName'].str.contains('Belt')]

    ind.drop(['BarcodeID', 'FirstName','LastName'], axis=1, inplace=True)

    ind = ind[ind['IndexValue'].str.contains('Yes')]

    # Custom Fields clean up

    procedures.fix_ranks(cus, ranks='CustomFieldValue', programs='CustomField')
    for i in cus['CustomField'].unique().tolist():
        cus = cus.groupby('MBSystemID', as_index=False).sum()

    cus.drop(['CustomFieldValue','CustomField', 'BarcodeID','FirstName','LastName'], axis=1, inplace=True, errors='ignore')

    # Membership file cleanup
    cols = mem.columns.values
    mem['ScheduleDate'] = pd.to_datetime(mem['ScheduleDate'])

    # ------ Super slow solution -------- open to suggestions here
    # Grabs the closest payment entry from each of a Contact's Memberships

    new_mem = []

    for name, group in mem.groupby('MBSystemID'):

        # group is the member

        for subname, subgroup in group.groupby(['Contract Start Date','Contract End Date']):

            # subgroup is the membership payments

            tempFuture = pd.DataFrame(columns=mem.columns.values)
            tempPast = pd.DataFrame(columns=mem.columns.values)

            for index, row in subgroup.iterrows():

                # row is the payment

                # Removes payments that were deleted

                if row['ContractDeleted'] == 'True':
                    break

                # Sorts the payments into future or past, based on today
                # We do this so we can have the payment CLOSEST to today that has not passed

                if row['ScheduleDate'].date() > datetime.date.today():
                    tempFuture = tempFuture.append(row)

                elif row['ScheduleDate'].date() < datetime.date.today():
                    tempPast = tempPast.append(row)

            # Need to use if statements to see if the membership is in the future/past

            if len(tempFuture.index) != 0:

                tempFuture['Payments Remaining'] = tempFuture.shape[0]
                mostRecent = tempFuture.sort_values('ScheduleDate', ascending=True).head(1).values.tolist()
                mostRecent = list(itertools.chain.from_iterable(mostRecent))
                if mostRecent != []:
                    new_mem.append(mostRecent)

                    ## NEED TO REVIEW ^^^^

            else:

                tempFuture['Payments Remaining'] = '0'
                mostRecent = tempPast.sort_values('ScheduleDate', ascending=False).head(1).values.tolist()
                mostRecent = list(itertools.chain.from_iterable(mostRecent))
                if mostRecent != []:
                    new_mem.append(mostRecent)


    # Create new Memberships DB from New_Mem

    pr = ['Payments Remaining']
    cols = np.append(cols, pr)
    mem = pd.DataFrame(new_mem, columns=cols)

    # -------- End slow solution -----------------------------------

    # Basic cleanup to make import more manageable

    mem['Amount'] = mem['Amount'].str.replace(r'00$', '')
    mem['PaymentMethod'] = mem['PaymentMethod'].str.replace('Credit Card', 'CC')
    mem['PaymentMethod'] = mem['PaymentMethod'].str.replace('ACH', 'EFT')
    mem['PaymentMethod'] = mem['PaymentMethod'].str.replace('Debit Account', 'CC')
    mem.drop(['ContractDeleted','RecLastname','RecFirstname', 'BarcodeID', 'AutopayDeleted'], axis=1, inplace=True)
    mem.rename(columns={'ContractName': 'Current Program'}, inplace=True)

    # Get Most recent Membership by Start Date -- we can only import primary memberships at this time :(

    mem['Contract Start Date'] = pd.to_datetime(mem['Contract Start Date'])
    mem = mem.sort_values('Contract Start Date', ascending=False).groupby('MBSystemID').head(1)

    # Clean Contacts up

    con.rename(columns={'Male': 'Gender'}, inplace=True)
    con['Gender'] = con['Gender'].map({'True':'M', 'False': 'F'})

    con.rename(columns={'ReferredBy': 'Source'}, inplace=True)

    # Clean notes up

    notes.dropna(subset=['Notes'], inplace=True)
    notes = notes.groupby('MBSystemID').agg({'Notes':' - '.join}).reset_index()
    procedures.strip_whitespace(notes, column='Notes')
    # Financials cleanup

    fin.rename(columns={'ClientID': 'MBSystemID'}, inplace=True)
    fin['IsSavingsAcct'] = fin['IsSavingsAcct'].map({'True':'S', 'False': 'C'})

    # Relationships cleanup

    rel.rename(columns={'MBSystemID1': 'MBSystemID'}, inplace=True)
    rel['Relationships'] = rel['RelName1'] + ': ' + rel['FirstName2'] + ' ' + rel['LastName2']
    rel = rel.groupby('MBSystemID').agg({'Relationships':' -- '.join}).reset_index()


    # Merge files

    needs_merge = [mem, fin, rel, notes, cus, ind]
    complete = con

    for i in needs_merge:
        complete = pd.merge(complete, i, on='MBSystemID', how='left')

    # Drops empty columns
    complete.dropna(how='all', axis='columns', inplace=True)

    # Create Contact Type column

    complete['Contact Type'] = ''
    complete['Contract End Date'] = complete['Contract End Date'].astype('datetime64')
    for index, row in complete.iterrows():
        if row['IsProspect'] == 'True':
            complete.at[index, 'Contact Type'] = 'P'
        elif row['Inactive'] == 'True':
            complete.at[index, 'Contact Type'] = 'F'
        elif pd.notna(row['Contract End Date']):
            if row['Contract End Date'] < datetime.datetime.today():
                complete.at[index, 'Contact Type'] = 'F'
            else:
                complete.at[index, 'Contact Type'] = 'S'
        else:
            complete.at[index, 'Contact Type'] = 'P'

    for index, row in complete.iterrows():
        if row['Autorenewing'] == 'True' and pd.notna(row['Contract End Date']):
            complete.at[index, 'Contract End Date'] = '2099-12-31'
            complete.at[index, 'Payments Remaining'] = '9999'

    complete.drop(['Autorenewing', 'Inactive', 'IsProspect', 'ID'], axis=1, inplace=True)

    complete['Billing Company'] = np.where(complete['PaymentMethod'].notnull(), 'autoCharge', '')
    complete['Payment Frequency'] = np.where(complete['PaymentMethod'].notnull(), '30', '')
    complete.drop_duplicates(inplace=True)

    # Output files

    try:
        os.mkdir('clean')
    except Exception:
        pass

    con.name = 'Contacts'
    mem.name = 'Memberships'
    fin.name = 'Financials'
    rel.name = 'Relationships'
    cus.name = 'Custom Fields'
    notes.name = 'Notes'
    ind.name = 'Ranks'
    complete.name = 'Complete_File'

    for i in [con, mem, fin, rel, cus, notes, ind, complete]:

        i.to_csv('clean/' + i.name + '.csv', quoting=1, index=False)

    # An alert to let you know when it is finished (because it takes forever)

    print('\a')

def PM_fix(path_to_files=os.getcwd(), key='RecordName', **kwargs):


    path = path_to_files + '/*.csv'
    files = glob.glob(path)


    for i in files:
        if "Contacts" in i:
            con = pd.read_csv(i, index_col=None, dtype=object)
            con.name = 'Contacts'

        if "Finance" in i:
            fin = pd.read_csv(i, index_col=None, dtype=object)
            fin.name = 'Financials'

        if "Promotions" in i:
            ranks = pd.read_csv(i, index_col=None, dtype=object)
            ranks.name = 'Ranks'

        if "Trans" in i:
            mem = pd.read_csv(i, index_col=None, dtype=object)
            mem.name = 'Memberships'


    # Rename for merge

    ranks.rename(columns={'ContactId': 'RecordName'}, inplace=True)
    mem.rename(columns={'ContactRecord': 'RecordName'}, inplace=True)
    mem.rename(columns={'PaymentPattern': 'Frequency', 'Processor': 'Billing Company'}, inplace=True)

    # Drop columns we can' use

    con.drop(['LeadLeadAge', 'MissedPayment', 'FullNameSimple', 'BecameClient', 'BecameFormerClient',
    'ContactedDate', 'Featured', 'StripesAwarded', 'ClassesSinceLastExam', 'PointstoBlackBelt',
    'Medical', 'InfoDueby', 'NeedInfo', 'MiddleName', 'Employer', 'Age', 'IsPrimaryContactForAccount',
    'Rating', 'ImportId', 'Description','EnrollmentDate', 'CancelledDate','AltId','LastExam'
    'Call2Date','Call2Completed','Call4Date','Call4Completed','Call6Date','Call6Completed','MembershipExpiry',
    'LeadRating','LeadStatus','LastPromotion','Transferredto','LastExam','Call2Date'], axis=1, inplace=True, errors='ignore')

    ranks.drop(['PromotionId', 'ClassesAttended', 'NextRankPromotionDate', 'IsRankReady', 'ClassesSinceLastRankPromotion', 'CurrentStripe',
    'NextStripePromotionDate', 'NextStripe', 'DaysSinceRankPromoted', 'RankOrder', 'FullNameSimple'], axis=1, inplace=True, errors='ignore')

    fin.drop(['FinanceInfoRecordName', 'Street', 'City', 'PostalCode', 'BankNumber','Student Last Name','Student First Name'], axis=1, inplace=True, errors='ignore')

    mem.drop(['Finance Info Record', 'Transaction Record', 'TotalAmount', 'RemainingBalance', 'DelinquentAmount',
    'OnHold', 'FirstPayment', 'FinalPayment', 'Ongoing', 'SubTotal', 'TAXONE', 'Tax', 'DelinquentSince',
    'ForfeitedAmount', 'ResumeDate', 'Renewal', 'SessionsPurchased', 'DownPayment', 'DurationDays', 'LastName',
    'FirstName', 'NextPaymentAmount', 'CancellationDate','Notes'], axis=1, inplace=True, errors='ignore')


    # clean contacts

    con['Type'].replace({'Lead': 'P', 'Former student':"F", 'Active student': 'S'}, inplace=True)
    con['PrimaryPhone'].replace({'Primary Phone': 'Mobile', 'Home ': 'Home'}, inplace=True)
    procedures.fix_ranks(con, ranks='PrimaryNumber', programs='PrimaryPhone')
    procedures.fix_ranks(con, ranks='SecondaryNumber', programs='SecondaryPhone')
    con.drop(['PrimaryNumber', 'PrimaryPhone', 'SecondaryPhone', 'SecondaryNumber'], axis=1, inplace=True)
    for i in ['Work', 'Mobile', 'Home']:
        procedures.clean_phones(con, i)

    con.rename(columns={'BecameLead': 'Date Added', 'PerfectScanID': 'Alternate ID (Scan)', 'CampaignName': 'Source'}, inplace=1)

    con['Source'] = np.where((con['Source'].isnull()) & (con['ReferedBy'].notnull()), 'Referral', con['Source'])


    # clean up financials // sort down to most recent & reliable card, keep only that ContactRecord

    numcols = ['CreditCardNumber', 'ExpiryMonth', 'ExpiryYear', 'AccountNumber', 'RoutingNumber']

    for i in numcols:
        fin[i] = fin[i].str.replace(r'[^0-9]', '')
        fin[i].replace('', np.nan, inplace=True)

    fin.sort_values(['RecordName', 'Status', 'Default', 'ExpiryYear', 'ExpiryMonth'],ascending=[True, False, False, False, False], inplace=True)

    fin = fin.groupby('RecordName', as_index=False).nth(0)
    fin.name = 'Financials'

    # fix ranks columns

    procedures.fix_ranks(ranks, ranks='Rank', programs='Program')
    ranks.sort_values(['RecordName','ProgramEnrollmentDate'], ascending=[True, False], inplace=True)
    ranks.drop(['Rank', 'Program', 'ProgramEnrollmentDate'], axis=1, inplace=True)


    ColDict = {}
    for i in ranks.columns:
        ColDict[i] = 'first'

        # Replace empty strings with Nan
    ranks.replace('', np.nan, inplace=True)

    ranks = ranks.groupby('RecordName').agg(ColDict)
    ranks.name = 'Ranks'

    # clean up Memberships file // sort down to most recent active membership

    mem.sort_values(['RecordName', 'MembershipStatus', 'Membership Activate'],ascending=[True, True, False], inplace=True)

    mem = mem.groupby('RecordName', as_index=False).nth(0)
    mem.name = 'Memberships'

    mem['Billing Company'].replace({'Billing Direct': 'autoCharge', 'In-House':"In House"}, inplace=True)

    mem['Frequency'].replace({'Monthly': '30', 'Paid In Full': '0'}, inplace=True)

    mem['Billing Company'] = np.where((mem['Transaction Status'] == 'Completed') & (mem['MembershipStatus'] == 'Active'), 'PIF', mem['Billing Company'])

    mem['Membership Expiry'] = np.where(mem['Membership Expiry'].isnull(), '12-31-2099', mem['Membership Expiry'])

    # Merge files

    needs_merge = [mem, fin, ranks]
    complete = con

    for x in needs_merge:
        x.set_index('RecordName')
        complete = pd.merge(complete, x, on=key, how='left')



    complete.name = 'Complete_File'

    # decide payment method
    complete['Payment Method'] = np.where(complete['Billing Company'] =='In House','In House',
                                        np.where(complete['Billing Company'] == 'PIF','PIF',
                                            np.where(complete['AccountNumber'].notnull(),'EFT',
                                                    np.where(complete['CreditCardNumber'].notnull(),'CC', ''))))


    try:
        os.mkdir('clean')
    except Exception:
        pass


    for i in [mem, fin, ranks, con, complete]:

        i.to_csv('clean/' + i.name + '.csv', quoting=1, index=False)

def RM_fix(df, parents=None):

    # Fix Billing Companys and Payment Methods

    replacements = {'ON HOLD': 'autoCharge','autoCollect': 'autoCharge',
                    'Family Membership': 'Family Membership', 'In House': 'In House',
                    'PIF': 'PIF', 'autoCollect_ONHOLD': 'autoCharge'}

    df['Billing_Company'] = df['Billing_Company'].map(replacements)

    def fill_null():

        if pmt:
            df.iloc[index]['Payment_Method'] = 'PIF'
            if pmt_date:
                df.iloc[index]['next_payment_due'] = '12/31/2099'
            if pmt_amt:
                df.iloc[index]['Tuition_Amount'] = '0'
            if pmt_freq:
                df.iloc[index]['PaymentFrequency'] = '0'

    # Fix for Family Memberships

    for index, x in df['Billing_Company'].iteritems():

        # Find all relevant null values

        pmt = pd.isnull(df.iloc[index]['Payment_Method'])
        pmt_date = pd.isnull(df.iloc[index]['next_payment_due'])
        pmt_amt = pd.isnull(df.iloc[index]['Tuition_Amount'])
        pmt_freq = pd.isnull(df.iloc[index]['PaymentFrequency'])
        strt_date = pd.isnull(df.iloc[index]['Current_Program_Start_Date'])

        if x == 'Family Membership':

            df.iloc[index]['Billing_Company'] = 'PIF'
            x = 'PIF'

            if strt_date:

                # Matches Start Date with owner of Family Membership

                # Check 5 cells below and 5 cells above for Surname, Address, and Program match

                indexRange = [i for i in range(index-5, index+5)]
                for i in indexRange:

                    match = (df.iloc[i]['Address_1'] == df.iloc[index]['Address_1'] and
                             df.iloc[i]['Last_Name'] == df.iloc[index]['Last_Name'] and
                             df.iloc[i]['Current_Program'] == df.iloc[index]['Current_Program'] and
                             df.iloc[i]['Current_Program_Expires'] == df.iloc[index]['Current_Program_Expires'])


                    if match:
                        df.iloc[index]['Current_Program_Start_Date'] = df.iloc[i]['Current_Program_Start_Date']
                        fill_null()

                    else:
                        fill_null()


        if x == 'PIF':

            fill_null()



    # Fix Expire Dates before 1/1/2000

    for index, x in df['Current_Program_Expires'].iteritems():

        match = re.match(r'(.*/\d?\d)/(\d)(\d)([\s|$])', str(x))

        if match is not None:
            if int(match.group(2)) >= 5 or x == '1/1/00 0:00':
                # Correct Date is newDate, but since it would be in the 1900's, insert forever
                newDate = str(match.group(1)) + "/19" + str(match.group(2)) + str(match.group(3)) + str(match.group(4))
                forever = "12/31/2099"
                df.iloc[index]['Current_Program_Expires'] = forever
            elif int(match.group(2)) < 5:
                newDate = str(match.group(1)) + "/20" + str(match.group(2)) + str(match.group(3)) + str(match.group(4))
                df.iloc[index]['Current_Program_Expires'] = newDate


    # Drop extra columns

    df = df.drop(['Age', 'Total_Contract_Amount', 'Down_Payment', 'Total_Financed', 'Number_of_Installments',
                'First_Payment_Due_Date', 'last_payment_date', 'Date_to_Take_Payment', 'Middle_Init'], axis=1)

    df.dropna(how='all', axis='columns', inplace=True)

    # This should have been included -- may need to revise the entire procedure for optmization

    df['Billing_Company'] = np.where((df['Payment_Method'] == 'In House') & (df['Billing_Company'].isnull()), 'In House', df['Billing_Company'])
    df['Billing_Company'] = np.where((df['Payment_Method'] == 'PIF') & (df['Billing_Company'].isnull()), 'PIF', df['Billing_Company'])

    df.dropna(how='all', inplace=True, axis=1)

    if isinstance(parents, pd.DataFrame):
        df = df.merge(parents, on='ID', how='left')
        df.drop_duplicates(inplace=True)

    df.to_csv('clean_' + 'RM' + '.csv', index=False, quoting=1)

def ZP_fix(path_to_files=os.getcwd(), key='RecordName', **kwargs):


    path = path_to_files + '/*.csv'
    files = glob.glob(path)


    for i in files:
        if "People" in i:
            con = pd.read_csv(i, index_col=None, dtype=object)


        if "Membership" in i:
            mem = pd.read_csv(i, index_col=None, dtype=object)


        if "Attendance" in i:
            ranks = pd.read_csv(i, index_col=None, dtype=object)

        if "Bill" in i:
            bills = pd.read_csv(i, index_col=None, dtype=object)



    # Rename for merge

    con.rename(columns={'Inquiry Date': 'Date Added'}, inplace=True)
    ranks.rename(columns={'Person': 'Full Name'}, inplace=True)

    # Drop columns we can't use

    con.drop(['Family', 'Age', 'Prospect Status', 'Prospect Status (sub)', 'Interest',
     'Prospect Priority', 'Sales Rep', 'Primary Instructor', 'Primary Location', 'Trial End Date',
     'Signup Date', 'Days as Prospect', 'Days Since Att.', 'First Att. Date', 'Att. Last 30 Days',
     'Att. Total', 'Has Password?', 'Signed Documents'], axis=1, inplace=True)

    mem.drop(['Has Been Renewed', 'Renewal Type', 'Drop Date', 'Drop Reason', 'Drop Reason (sub)',
     'Drop Comments', 'Months', 'Signup Fee', 'Autopay?', 'People (count)', 'Shared?', 'Att. Remaining',
     'Att. Limit Type', 'Att. Limit', 'Att. Total', 'Enrollments', 'Primary Location', 'Income Category',
     'Tax2?', 'Taxable?'], axis=1, inplace=True, errors='ignore')

    ranks.drop(['Reservation Date', 'Session Type', 'Attendance Type',
      'Location', 'Staff Member', 'Rsvp', 'Att. Last 30 Days', 'Att. Since Last Test',
      'Class Notes', 'Membership', 'Membership Label', 'Begin Date', 'End Date'], axis=1, inplace=True)

    bills.drop(['Paid By Staff', 'Sales Rep', 'Income Category', 'Paid Date', 'Paid Month',
      'Paid On Time', 'Unit Count', 'Unit Price', 'Discount Total', 'After Discounts', 'Taxable?', 'Tax Amt',
      'Tax 2?', 'Tax 2 Amt', 'Amount Due', 'Amount Paid', 'Amount Unpaid', 'First Name', 'Last Name'], axis=1, inplace=True)

    # Clean Up

    # Need this to group by

    for a in [mem, con]:
        for index, x in a.iterrows():
            x = str(a.iloc[index]['First Name']) + " " + str(a.iloc[index]['Last Name'])
            a.set_value(index, 'Full Name', x)

    # Ranks - If last attendance date = date: preserve, else, drop

    ranks = ranks[(ranks['Last Att. Date'] == ranks['Date']) & (ranks['Att.'] == 'Yes')]
    ranks['Check In Date'] = ranks['Date'] + " " + ranks['Time']
    ranks['Check In Date'] = pd.to_datetime(ranks['Check In Date'])
    ranks = ranks.sort_values('Check In Date', ascending=False).groupby('Full Name', as_index=False).head(1)

    mem['Installment Plan'].replace({'Every Month': '30', 'Single Payment': '0', 'Every 1 Week': '7'}, inplace=True)

    # Mems - Find duplicates based of name + last attendance date - keep one iwht highest number
    mem = mem.sort_values('Number', ascending=False).groupby(['Full Name', 'Last Att. Date'], as_index=False).head(1)
    mem['Payment Amount'] = mem['Payment Amount'].replace(r'^\$', '', regex=True)

    # Bills

    bills['Number'] = bills['Description'].str.extract(r'#(\d+)', expand=False)
    bills = bills[(bills['Purchase Type'] == 'Membership') & (bills['Number'].notnull())]
    bills = bills.sort_values('Bill #', ascending=True).groupby('Number', as_index=False).head(1)
    bills['Drop Me'], bills['Installments'] = bills['Notes'].str.split('l ', 1).str
    bills['Paid'], bills['Total'] = bills['Installments'].str.split('/', 1).str
    bills['Total'] = bills['Total'].str.replace(r'\s\(prorated\)', '', regex=True)
    bills['Total'] = bills['Total'].str.replace(r'\s\(signup fee\)', '', regex=True)
    bills['Paid'] = np.where(bills['Paid'] == np.nan, '0', bills['Paid'])
    bills['Total'] = np.where(bills['Total'] == np.nan, '0', bills['Total'])
    bills['Installments Remaining'] = np.where((bills['Total'].notna()) & (bills['Paid'].notna()),
                                                bills['Total'].astype(float) - bills['Paid'].astype(float),
                                                np.nan)
    bills['Installments Remaining'] = np.where(bills['Status'] == 'UNPAID',
                                    bills['Installments Remaining'].astype(float) + 1,
                                    bills['Installments Remaining'])

    for i, row in bills.iterrows():
        if (row['Installments Remaining'] == np.nan) and (row['Mbr. Status'] == 'COMPLETED'):
            bills.iloc[i]['Installments Remaining'] = '0'


    bills.drop(['Drop Me', 'Installments', 'Total', 'Paid', 'Description', 'Status', 'Purchase Type', 'Description', 'Notes', 'Subtotal'], inplace=True, axis=1)
    bills.rename(columns={'Due Date': 'Next Payment Due Date'}, inplace=True)

    # Merge based on


    # Merge files

    colsToUse = mem.columns.difference(con.columns).tolist()
    colsToUse.extend(['Last Att. Date', 'Full Name'])
    complete = pd.merge(con, mem[colsToUse], on=['Last Att. Date', 'Full Name'], how='left')


    colsToUse = ranks.columns.difference(complete.columns).tolist()
    colsToUse.extend(['Last Att. Date', 'Full Name'])
    complete = pd.merge(complete, ranks[colsToUse], on=['Last Att. Date', 'Full Name'], how='left').drop_duplicates()

    colsToUse = bills.columns.difference(complete.columns).tolist()
    colsToUse.append('Number')
    complete = pd.merge(complete, bills[colsToUse], on='Number', how='left')

    cols = ['Birth Date', 'Mbr. Begin Date', 'Date Added', 'Last Att. Date', 'Mbr. End Date', 'First Bill Due', 'Next Payment Due Date']
    for x in cols:
        if x in complete.columns.values:
            complete[x] = pd.to_datetime(complete[x])
            complete[x].dt.strftime('%m-%d-%Y').astype(str)

    phones = ['Home Phone','Cell Phone', 'Phone']
    for phone in phones:
        if phone in complete.columns.values:
            complete[phone] = complete[phone].replace(r'[^0-9]','', regex=True)

    replacements = {'Prospect': 'P','Alumni': 'F',
                    'Student': 'S', np.nan: 'P'}

    complete['Status'] = complete['Status'].map(replacements)

    complete['Next Payment Due Date'] = complete['Next Payment Due Date'].combine_first(complete['First Bill Due'])
    complete['Installments Remaining'] = complete['Installments Remaining'].combine_first(complete['# of Installments'])

    complete.drop(['Birth Month','First Bill Due', '# of Installments','Birth Day','Interest (sub)','Referred By','Last Updated','Last Log Entry',
    'Tracking Source','Tracking Name','Tracking Medium','Tracking Keywords', 'Primary Location','Signup Fee?',
    'Autopay Account','Autopay Approved By','Autopay Approved Date','Time','Type','Weekday','Long Date','Check In Date',
    'Date','Date / Time','BirthDate','Att.','Validated?','Primary Instructor','Prospect Priority','Prospect Status',
    'Prospect Status (sub)','Sales Rep','Acct Name','Age','Auto Renew','Autopay Available?'], axis=1, inplace=True, errors='ignore')

    complete.dropna(how='all', inplace=True, axis=1)

    # Output files

    try:
        os.mkdir('clean')
    except Exception:
        pass

    con.name = 'Contacts'
    mem.name = 'Memberships'
    ranks.name = 'Ranks'
    bills.name = 'Bills'
    complete.name = 'Complete_File'

    for i in [con, mem, ranks, bills, complete]:

        i.to_csv('clean/' + i.name + '.csv', quoting=1, index=False)
#endregion

#region Software Merges
def merge_KS_SP(kicksiteFile, solupayFile, checkLast=False):
    ## This is the best possible method to get as many accurate matches as possible with the data provided.
    ## takes CheckLast as a parameter to decide whether or not to check for matches based on lastname alone

    df = kicksiteFile
    fin = solupayFile

    # makes file to output results to -- we make it early becasue we're outputting files sporadically
    try:
        os.mkdir('Merge Results')
    except Exception:
        pass

    procedures.strip_whitespace(fin)
    fin['LastUpdate'] = pd.to_datetime(fin['LastUpdate'])
    fin['FirstName'] = fin['FirstName'].str.upper()
    fin['LastName'] = fin['LastName'].str.upper()
    fin = fin.sort_values('LastUpdate', ascending=False).groupby(['FirstName', 'LastName'], as_index=False).head(1)

    match = pd.DataFrame(columns=df.columns.values)
    fin.to_csv('Merge Results/' + 'Clean_Financials'+ '.csv', index=False, quoting=1)
    count = 0

    ## Usually a bad idea. Only enable if you know what you're doings
    def check_Last(rowDF, row, count, match):

        if not(isinstance(rowDF['Last Name'], float)):

            if row['LastName'].upper() in rowDF['Last Name'].upper():

                count += 1
                rowDF['Match'] = row['FirstName'].upper() + row['LastName'].upper()
                rowDF['MatchType'] = 'last'
                match = match.append(rowDF)
                print(str(count) + '-- LASTNAME')
                return (match, count)

        else:
            return (match, count)

        return (match, count)

    def check_Mem(rowDF, row, count, match, checkLast):

        if not(isinstance(rowDF['Members'], float)):

            if row['FirstName'].upper() in rowDF['Members'].upper() and row['LastName'].upper() in rowDF['Members'].upper():

                count += 1
                rowDF['Match'] = row['FirstName'].upper() + row['LastName'].upper()
                match = match.append(rowDF)
                print(str(count) + '-- MEM')
                return match, count

            elif checkLast:
                match, count = check_Last(rowDF, row, count, match)
            else:
                return (match, count)

        elif checkLast:
            match, count = check_Last(rowDF, row, count, match)
        else:
            return (match, count)

        return (match, count)

    def check_G1(rowDF, row, count, match, checkLast):

        if not(isinstance(rowDF['Guardian 1'], float)):

            if row['FirstName'].upper() in rowDF['Guardian 1'].upper() and row['LastName'].upper() in rowDF['Guardian 1'].upper():

                count += 1
                rowDF['Match'] = row['FirstName'].upper() + row['LastName'].upper()
                match = match.append(rowDF)
                print(str(count) + '-- G1')
                return (match, count)

            elif row['LastName'].upper() in rowDF['Last Name'].upper() and row['FirstName'].upper() in rowDF['Guardian 1'].upper():

                count += 1
                rowDF['Match'] = row['FirstName'].upper() + row['LastName'].upper()
                match = match.append(rowDF)
                print(str(count) + '-- G1LN')
                return (match, count)

            else:
                match, count = check_G2(rowDF, row, count, match, checkLast)

        else:
            match, count = check_G2(rowDF, row, count, match, checkLast)

        return (match, count)


    def check_G2(rowDF, row, count, match, checkLast):

        if not(isinstance(rowDF['Guardian 2'], float)):

            if row['FirstName'].upper() in rowDF['Guardian 2'].upper() and row['LastName'].upper() in rowDF['Guardian 2'].upper():

                count += 1
                rowDF['Match'] = row['FirstName'].upper() + row['LastName'].upper()
                match = match.append(rowDF)
                print(str(count) + '-- G2')
                return (match, count)

            else:
                match, count = check_Mem(rowDF, row, count, match, checkLast)
        else:
            match, count = check_Mem(rowDF, row, count, match, checkLast)

        return (match, count)

    for indexDF, rowDF in df.iterrows():
        for index, row in fin.iterrows():
            match, count = check_G1(rowDF, row, count, match, checkLast)

    match = match[match['Contact Type'] == 'S']
    needs_match = df[~df.index.isin(match.index)]
    needs_match = needs_match[needs_match['Contact Type'] == 'S']
    needs_match['Match'] = ''

    for i, x in needs_match.iterrows():
        if not(isinstance(x['Family Name'], float)):
            fam = match[match['Family Name'] == x['Family Name']].reset_index()
            first_not_null = fam.apply(lambda series: series.first_valid_index())
            if not np.isnan(first_not_null['Match']):
                print('MATCH ---' + fam.iloc[int(first_not_null['Match'])]['Match'] + ' -- ' + x['Id'])
                needs_match.at[i, ['Match']] = fam.iloc[int(first_not_null['Match'])]['Match']

    new = needs_match[needs_match['Match'].notnull()]
    needs_match = needs_match[needs_match['Match'] == '']
    needs_match.to_csv('Merge Results/' + 'Needs_Match' + '.csv', index=False, quoting=1)

    match = match.append(new)

    fin['Match'] = fin['FirstName'].str.upper() + fin['LastName'].str.upper()

    if checkLast:
        lastNameCounts = fin['LastName'].value_counts()
        IneligibleLastNames = lastNameCounts[lastNameCounts > 1]

        match = match[~((match['MatchType'] == 'last') & (match['Last Name'].str.upper().isin(IneligibleLastNames.index.values)))]

    match = match.merge(fin, on='Match')

    match = match.sort_values('LastUpdate').groupby('Id', as_index=False).head(1)

    match.to_csv('Merge Results/' + 'Matched' + '.csv', index=False, quoting=1)

    final = match.append(df[~df['Id'].isin(match['Id'])], sort=False)

    final.to_csv('Merge Results/' + 'Complete' + '.csv', index=False, quoting=1)

#endregion