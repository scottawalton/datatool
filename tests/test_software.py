import pandas as pd

import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../datatool')))

import software
import procedures

def test_ms_fix():

    # TODO

    assert True

def test_rm_fix():

    data = procedures.load("rm", 'tests/test_files/rm')
    expected =  procedures.load("expected_basic", 'tests/test_files/rm')

    cleaned_data = software.RM_fix(data).reset_index(drop=True)

    assert cleaned_data.equals(expected)

def test_rm_fix_parents():

    data = procedures.load("rm", 'tests/test_files/rm')
    parents = procedures.load("parents", 'tests/test_files/rm')
    expected =  procedures.load("expected_parents", 'tests/test_files/rm')

    cleaned_data = software.RM_fix(data, parents=parents).reset_index(drop=True)

    assert cleaned_data.equals(expected)