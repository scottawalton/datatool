import pandas as pd
import glob
import sys, os
import numpy as np
import re

def RMfix(df):

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

        match = re.match('(.*/\d?\d)/(\d)(\d)([\s|$])', str(x))

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

    return df
