import pandas as pd
import glob
import sys, os

def ASFfix(path_to_files=os.getcwd(), key="ASF ACCT#", **kwargs):


    path = path_to_files + '/*.CSV'
    files = glob.glob(path)

    # Load Files in ------------------------------------------------------------

    for i in files:
        if "ARF" in i:
            arf = pd.read_csv(i, index_col=None, dtype=object,
                    names = ["BANK ACCT/CC#","RECORD DATE","CC EXP","BANK RT#","ASF ACCT#","CLUB#",
                    "PMT AMT","TRANS DTE","REJECT REASON","REJECT ERROR","DUE DATE","DESCRIPTN","NAME",
                    "RECRRNG ID","CHKG/SAVGS","TYPE","STATUS","INT FLAG","NUM PT SESS"])
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
#    need info to be copied from main contact, but retain info on this one. right merge


    #Merge files together ------------------------------------------------------

    needs_merge = [emr, note]
    # CLC is not included because it needs to be merged seperatly and then appended
    complete = clm

    for x in needs_merge:
        x.set_index("ASF ACCT#")
        complete = pd.merge(complete, x, on=key, how='left')

    print(complete['RLTNSHP 2'])

    additional = pd.merge(complete, clc, on="ASF ACCT#", how='right')
    complete = complete.append(additional, sort=False)

    return complete.to_csv('complete.csv', quoting=1)
