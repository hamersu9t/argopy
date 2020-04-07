#!/bin/env python
# -*coding: UTF-8 -*-

import pytest
import argopy

def test_invalid_dataset():
    with pytest.raises(ValueError):
        argopy.tutorial.open_dataset('invalid_dataset')

def test_localftp_dataset():
    ftproot, flist = argopy.tutorial.open_dataset('localftp')
    assert isinstance(ftproot, str) == True
    assert isinstance(flist, list) == True

def test_weekly_index_dataset():
    txtfile = argopy.tutorial.open_dataset('weekly_index_prof')
    assert isinstance(txtfile, str) == True

def test_weekly_index_dataset():
    txtfile = argopy.tutorial.open_dataset('global_index_prof')
    assert isinstance(txtfile, str) == True
