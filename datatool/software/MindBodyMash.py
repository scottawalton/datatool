import pandas as pd
import glob
import sys, os
import numpy as np
import datetime
from itertools import chain
import procedures

def MBfix(path_to_files=os.getcwd(), key='MBSystemID', **kwargs):

    path = path_to_files + '/*.csv'
    files = glob.glob(path)

    main = pd.DataFrame()

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

#        if "ClientPricingOption" in i:
#            mem2 = pd.read_csv(i, index_col=None, dtype=object)


    # Need to implement Custom Fields file import (orignal transfer didn't require)


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

#    mem2.drop(['BarcodeID','Returned', 'Duration', 'DurationUnit', 'PaymentDataID', 'ItemType',
#    'NumClasses', 'PaymentAmount', 'Program/Service Category', 'FirstName', 'LastName'], axis=1, inplace=True)



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
                mostRecent = list(chain.from_iterable(mostRecent))
                if mostRecent != []:
                    new_mem.append(mostRecent)

                    ## NEED TO REVIEW ^^^^

            else:

                tempFuture['Payments Remaining'] = '0'
                mostRecent = tempPast.sort_values('ScheduleDate', ascending=False).head(1).values.tolist()
                mostRecent = list(chain.from_iterable(mostRecent))
                if mostRecent != []:
                    new_mem.append(mostRecent)



                    ## NEED TO REVIEW ^^^^

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
