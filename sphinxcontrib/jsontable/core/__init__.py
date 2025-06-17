"""
Core processing components for Excel file handling.

This module provides core functionality that was previously
embedded within the monolithic ExcelDataLoader class.
"""

from .range_parser import IRangeParser, RangeInfo, RangeParser

__all__ = [
    'IRangeParser',
    'RangeParser',
    'RangeInfo'
]