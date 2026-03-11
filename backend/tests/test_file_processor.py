"""Tests for the file processor service."""

import pytest
from app.services.file_processor import parse_sales_data


SAMPLE_CSV = (
    b"Date,Product_Category,Region,Units_Sold,Unit_Price,Revenue,Status\n"
    b"2024-01-01,Electronics,North,100,50.0,5000.0,Completed\n"
    b"2024-01-02,Clothing,South,200,30.0,6000.0,Completed\n"
    b"2024-01-03,Electronics,East,150,50.0,7500.0,Pending\n"
)


def test_parse_csv():
    result = parse_sales_data(SAMPLE_CSV, "test.csv")
    assert result["rows"] == 3
    assert "Revenue" in result["columns"]
    assert "raw_text" in result
    assert result["stats"]["total_revenue"] == 18500.0


def test_parse_csv_region_breakdown():
    result = parse_sales_data(SAMPLE_CSV, "test.csv")
    stats = result["stats"]
    assert "revenue_by_region" in stats
    assert stats["revenue_by_region"]["East"] == 7500.0


def test_parse_empty_file():
    with pytest.raises(ValueError, match="no data rows"):
        parse_sales_data(b"Col1,Col2\n", "empty.csv")


def test_parse_invalid_file():
    with pytest.raises(ValueError, match="Could not parse"):
        parse_sales_data(b"\x00\x01\x02\x03", "bad.csv")
