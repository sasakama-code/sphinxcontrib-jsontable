#!/usr/bin/env python3
"""DataFrameサイズ問題のデバッグスクリプト"""

import os
import shutil
import tempfile

import pandas as pd
from openpyxl import Workbook

from sphinxcontrib.jsontable.core.excel_reader import ExcelReader


def main():
    # Test data setup
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "header_test.xlsx")

    data = [
        ["メタデータ", "作成日: 2025-06-13", "", ""],
        ["説明", "売上データの月次集計", "", ""],
        ["", "", "", ""],
        ["商品名", "1月売上", "2月売上", "3月売上"],
        ["商品A", "100000", "120000", "110000"],
        ["商品B", "150000", "180000", "160000"],
        ["商品C", "80000", "90000", "85000"],
    ]

    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"

    for row_idx, row_data in enumerate(data, 1):
        for col_idx, value in enumerate(row_data, 1):
            ws.cell(row=row_idx, column=col_idx, value=value)

    wb.save(file_path)
    print(f"Created Excel file with {len(data)} rows")

    # Test direct pandas read
    print("\n=== Direct pandas.read_excel ===")
    df_pandas = pd.read_excel(file_path)
    print(f"pandas DataFrame shape: {df_pandas.shape}")
    print("pandas DataFrame content:")
    for i, row in df_pandas.iterrows():
        print(f"  Row {i}: {list(row)}")

    # Test ExcelReader
    print("\n=== ExcelReader.read_workbook ===")
    excel_reader = ExcelReader()
    read_result = excel_reader.read_workbook(file_path)
    print(f"ExcelReader DataFrame shape: {read_result.dataframe.shape}")
    print("ExcelReader DataFrame content:")
    for i, row in read_result.dataframe.iterrows():
        print(f"  Row {i}: {list(row)}")

    # Test range A4:C7 against pandas DataFrame
    print("\n=== Range A4:C7 against pandas DataFrame ===")
    print("Excel rows 4-7 (1-based) = pandas rows 3-6 (0-based)")
    print(f"DataFrame has {len(df_pandas)} rows, max valid index: {len(df_pandas) - 1}")
    print("Trying to access rows 3-6...")

    try:
        range_df = df_pandas.iloc[3:7, 0:3]  # A4:C7 -> rows 3-6, cols 0-2
        print(f"Range DataFrame shape: {range_df.shape}")
        print("Range DataFrame content:")
        for i, row in range_df.iterrows():
            print(f"  Row {i}: {list(row)}")
    except Exception as e:
        print(f"Error: {e}")

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
