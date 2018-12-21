import pandas as pd

import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../datatool')))

import software
import procedures

def test_ms_fix():

    # TODO

    assert True

def test_rm_fix():

    expected =  procedures.load("expected_basic", 'tests/test_files/rm/basic')

    cleaned_data = software.RM_fix("tests/test_files/rm/basic/rm").reset_index(drop=True)

    if os.path.exists('clean_rm.csv'):
        os.remove('clean_rm.csv')
        os.remove('needs_to_be_merged_rm.csv')

    assert cleaned_data.equals(expected)

def test_rm_fix_parents():

    expected =  procedures.load("expected_parents", 'tests/test_files/rm/parents')

    cleaned_data = software.RM_fix("tests/test_files/rm/parents/rm").reset_index(drop=True)

    if os.path.exists('clean_rm.csv'):
        os.remove('clean_rm.csv')
        os.remove('needs_to_be_merged_rm.csv')

    assert cleaned_data.equals(expected)