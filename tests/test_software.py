import pandas as pd

import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../datatool')))

import software
import procedures

def test_ms_fix():

    # TODO

    assert True

def test_rm_fix():

    expected =  procedures.load("expected_basic", 'tests/test_files/rm')

    cleaned_data = software.RM_fix("tests/test_files/rm/rm").reset_index(drop=True)

    assert cleaned_data.equals(expected)

def test_rm_fix_parents():

    expected =  procedures.load("expected_parents", 'tests/test_files/rm')

    cleaned_data = software.RM_fix("tests/test_files/rm/rm", parents="tests/test_files/rm/parents").reset_index(drop=True)

    assert cleaned_data.equals(expected)