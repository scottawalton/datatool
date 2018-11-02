import pandas as pd
import glob
import sys, os
import numpy as np
import procedures


def ZPfix(path_to_files=os.getcwd(), key='RecordName', **kwargs):


    path = path_to_files + '/*.csv'
    files = glob.glob(path)

    main = pd.DataFrame()

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
    bills['Total'] = bills['Total'].str.replace('\s\(prorated\)', '', regex=True)
    bills['Total'] = bills['Total'].str.replace('\s\(signup fee\)', '', regex=True)
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
