import requests
import pytest
from nbp_change import calc_statistics, get_courses
from _pytest.monkeypatch import MonkeyPatch
import json


class mock_class():
    def json(a):
        dct = {"table":"A","currency":"dolar amerykański","code":"USD",
               "rates":[{"no":"234/A/NBP/2021","effectiveDate":"2021-12-03","mid":4.0653},
                        {"no":"235/A/NBP/2021","effectiveDate":"2021-12-06","mid":4.0619},
                        {"no":"236/A/NBP/2021","effectiveDate":"2021-12-07","mid":4.0788},
                        {"no":"237/A/NBP/2021","effectiveDate":"2021-12-08","mid":4.0710},
                        {"no":"238/A/NBP/2021","effectiveDate":"2021-12-09","mid":100}]}
        return dct 

def test_calc_statistics():
    monkeypatch = MonkeyPatch()
    def mock_get(*args, **kwargs):
        r = mock_class()
        return r
    monkeypatch.setattr(requests, "get", mock_get)
    
    r = calc_statistics(['USD'], 5)
    
    assert r["USD"] == {"change": 100/4.0653, "course": 100,"full_name": "dolar amerykański"}