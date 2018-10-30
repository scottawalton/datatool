import pandas as pd
import glob
import sys, os
import numpy as np
import procedures

def PMfix(path_to_files=os.getcwd(), key='RecordName', **kwargs):


    path = path_to_files + '/*.csv'
    files = glob.glob(path)

    main = pd.DataFrame()

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
