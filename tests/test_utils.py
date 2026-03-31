import pytest
import pandas as pd
from vt.utils import UomConverter

@pytest.fixture
def uom_data():
    return {
        "o2_id": {
            "id": "o2_id",
            "name": "% Saturation",
            "dispUom": "%",
            "dispS1": 0.0001,
            "dispO1": 0.0,
            "dispS2": 1.0,
            "dispO2": 0.0,
            "nDec": 1
        },
        "celsius_id": {
            "id": "celsius_id",
            "name": "Celsius",
            "dispUom": "°C",
            "dispS1": 1.0,
            "dispO1": -32.0,
            "dispS2": 0.5555555555555556,
            "dispO2": 0.0,
            "nDec": 1
        }
    }

@pytest.fixture
def converter(uom_data):
    return UomConverter(uom_data)

def test_convert_by_id(converter):
    raw = 205103.13
    assert pytest.approx(converter.convert(raw, "o2_id"), 0.0001) == 20.510313

def test_convert_by_name(converter):
    raw = 205103.13
    # Look up by "name"
    assert pytest.approx(converter.convert(raw, "% Saturation"), 0.0001) == 20.510313
    # Case insensitive
    assert pytest.approx(converter.convert(raw, "% saturation"), 0.0001) == 20.510313

def test_convert_by_display_unit(converter):
    raw = 205103.13
    # Look up by "dispUom"
    assert pytest.approx(converter.convert(raw, "%"), 0.0001) == 20.510313

def test_convert_celsius_by_name(converter):
    # 32F -> 0C
    assert pytest.approx(converter.convert(32.0, "Celsius")) == 0.0
    assert converter.format(32.0, "Celsius") == "0.0 °C"

def test_convert_series_by_name(converter):
    series = pd.Series([32.0, 212.0])
    converted = converter.convert_series(series, "Celsius")
    assert pytest.approx(converted[0]) == 0.0
    assert pytest.approx(converted[1]) == 100.0
