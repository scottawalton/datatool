import pandas as pd
import os
import procedures

## This is the best possible method to get as many accurate matches as possible with the data provided.
## takes CheckLast as a parameter to decide whether or not to check for matches based on lastname alone

def merge(kicksiteFile, financials, checkLast=False):

    df = kicksiteFile
    fin = financials

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

            elif checkLast == True:
                match, count = check_Last(rowDF, row, count, match)
            else:
                return (match, count)

        elif checkLast == True:
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


    match = match.merge(fin, on='Match')

    match = match.sort_values('LastUpdate').groupby('Id', as_index=False).head(1)

    match.to_csv('Merge Results/' + 'Matched' + '.csv', index=False, quoting=1)

    final = match.append(df[~df['Id'].isin(match['Id'])], sort=False)

    final.to_csv('Merge Results/' + 'Complete' + '.csv', index=False, quoting=1)
