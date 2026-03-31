import pytest
import pandas as pd
from vt.utils import UomConverter


@pytest.fixture
def uom_data():
    return {
        "o2_pct": {
            "id": "o2_pct",
            "name": "% Saturation",
            "dispUom": "%",
            "dispS1": 0.0001,
            "dispO1": 0.0,
            "dispS2": 1.0,
            "dispO2": 0.0,
            "nDec": 1,
        },
        "celsius": {
            "id": "celsius",
            "name": "Celsius",
            "dispUom": "°C",
            "dispS1": 1.0,
            "dispO1": -32.0,
            "dispS2": 0.5555555555555556,
            "dispO2": 0.0,
            "nDec": 1,
        },
        "kelvin": {
            "id": "kelvin",
            "name": "Kelvin",
            "dispUom": "K",
            "dispS1": 1.0,
            "dispO1": -32.0,
            "dispS2": 0.5555555555555556,
            "dispO2": 273.15,
            "nDec": 1,
        },
    }


@pytest.fixture
def converter(uom_data):
    return UomConverter(uom_data)


def test_convert_o2(converter):
    # Raw value 205103.13 -> 20.5103...
    raw = 205103.13
    converted = converter.convert(raw, "o2_pct")
    assert pytest.approx(converted, 0.0001) == 20.510313

    formatted = converter.format(raw, "o2_pct")
    assert formatted == "20.5 %"


def test_convert_celsius(converter):
    # 32F -> 0C
    raw_32 = 32.0
    converted_0 = converter.convert(raw_32, "celsius")
    assert pytest.approx(converted_0) == 0.0
    assert converter.format(raw_32, "celsius") == "0.0 °C"

    # 212F -> 100C
    raw_212 = 212.0
    converted_100 = converter.convert(raw_212, "celsius")
    assert pytest.approx(converted_100) == 100.0
    assert converter.format(raw_212, "celsius") == "100.0 °C"


def test_convert_kelvin(converter):
    # 32F -> 273.15K
    raw_32 = 32.0
    converted_k = converter.convert(raw_32, "kelvin")
    assert pytest.approx(converted_k) == 273.15
    assert converter.format(raw_32, "kelvin") == "273.1 K"


def test_convert_series(converter):
    series = pd.Series([32.0, 212.0, 77.0])
    converted = converter.convert_series(series, "celsius")

    assert pytest.approx(converted[0]) == 0.0
    assert pytest.approx(converted[1]) == 100.0
    assert pytest.approx(converted[2]) == 25.0


def test_unknown_uom(converter):
    # Should return raw value and log warning
    raw = 123.45
    assert converter.convert(raw, "unknown") == raw
    assert converter.format(raw, "unknown") == "123.45"

    series = pd.Series([1.0, 2.0])
    pd.testing.assert_series_equal(converter.convert_series(series, "unknown"), series)
