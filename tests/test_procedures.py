import pandas as pd
import datatool.procedures


def test_fix_ranks_basic():
    test_data = datatool.procedures.load("test_data", 'tests/test_files')
    result = datatool.procedures.fix_ranks(test_data, ranks='Ranks', programs='Programs')

    assert result.at[0, 'Krav Maga'] == 'Black Belt'

def test_fix_ranks_commas():
    test_data = datatool.procedures.load("test_data", 'tests/test_files')
    result = datatool.procedures.fix_ranks(test_data, ranks='Ranks', programs='Programs')

    assert result.at[1, 'Shav Tata'] == 'Red Belt'

def test_clean_phones():
    test_data = datatool.procedures.load("test_data", 'tests/test_files')
    result = datatool.procedures.clean_phones(test_data, 'Phones')

    assert result.at[0, 'Phones'] == '9543600101'

def test_split_phones():
    test_data = datatool.procedures.load("test_data", 'tests/test_files')
    test_data = datatool.procedures.split_phones(test_data, 'Phones')

    assert test_data.at[0, 'Mobile'] == '9543600101'

def test_split_emails():
    test_data = datatool.procedures.load("test_data", 'tests/test_files')
    test_data = datatool.procedures.split_emails(test_data, 'Emails')

    assert test_data.at[1, 'Email 2'] == 'superemail@gmail.com'

def test_fix_dates_basic():
    test_data = datatool.procedures.load("test_data", 'tests/test_files')
    test_data = datatool.procedures.fix_dates(test_data, 'Dates')

    assert test_data.at[0, 'Dates'] == '01-13-2018'

def test_fix_dates_global_to_us():
    test_data = datatool.procedures.load("test_data", 'tests/test_files')
    test_data = datatool.procedures.fix_dates(test_data, 'Dates')

    assert test_data.at[1, 'Dates'] == '12-13-2018'

def test_fix_dates_slash_to_dashes():
    test_data = datatool.procedures.load("test_data", 'tests/test_files')
    test_data = datatool.procedures.fix_dates(test_data, 'Dates')

    assert test_data.at[2, 'Dates'] == '12-31-2018'

def test_strip_whitespace_tabs_and_spaces():
    test_data = datatool.procedures.load("test_data", 'tests/test_files')
    test_data = datatool.procedures.strip_whitespace(test_data, 'String')

    assert test_data.at[0, 'String'] == 'hello World'

def test_strip_whitespace_newline():
    test_data = datatool.procedures.load("test_data", 'tests/test_files')
    test_data = datatool.procedures.strip_whitespace(test_data, 'String')

    assert test_data.at[1, 'String'] == 'hello  World'

def test_drop_quote_rows():
    test_data = datatool.procedures.load("test_data", 'tests/test_files')
    test_data = datatool.procedures.drop_quote_rows(test_data)

    for i in test_data.columns.values:
        result = test_data[i].str.contains('"', na=False).any()

    assert ~result

def test_tidy_split():
    test_data = datatool.procedures.load("test_data", 'tests/test_files')
    test_data = datatool.procedures.tidy_split(test_data, column="String", sep=", ")

    assert test_data.at[5, 'String'] == "blue world"
    
