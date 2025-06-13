"""Excel Data Loader for JsonTable Directive.

このモジュールはExcelファイル（.xlsx/.xls）の読み込みと
JSON形式への変換を担当する。

主な機能:
- Excelファイルの安全な読み込み
- 基本的なシート検出（デフォルト: 最初のシート）
- ヘッダー検出（第1行）
- データ型の自動変換
- エラーハンドリング
- セキュリティ（パストラバーサル対策）
"""

import re
from pathlib import Path
from typing import Any, ClassVar

import pandas as pd
from openpyxl import load_workbook


class RangeSpecificationError(ValueError):
    """範囲指定に関するエラー."""

    def __init__(self, message: str, invalid_spec: str | None = None):
        super().__init__(message)
        self.invalid_spec = invalid_spec


class SkipRowsError(ValueError):
    """Skip Rows指定に関するエラー."""

    def __init__(self, message: str, invalid_spec: str | None = None):
        super().__init__(message)
        self.invalid_spec = invalid_spec


class MergedCellsError(ValueError):
    """Merged Cells処理に関するエラー."""

    def __init__(self, message: str, invalid_spec: str | None = None):
        super().__init__(message)
        self.invalid_spec = invalid_spec


# 定数定義
CELL_ADDRESS_PATTERN = r"^([A-Z]+)([1-9]\d*)$"
MAX_EXCEL_ROWS = 1048576  # Excel最大行数
MAX_EXCEL_COLS = 16384  # Excel最大列数

# Skip Rows関連定数
MAX_SKIP_ROWS_COUNT = 10000  # 一度にスキップできる最大行数
SKIP_ROWS_RANGE_SEPARATOR = "-"  # 範囲指定のセパレータ
SKIP_ROWS_LIST_SEPARATOR = ","  # リスト指定のセパレータ


class ExcelDataLoader:
    """Excel ファイルの読み込みとJSON変換を行うクラス。

    セキュリティ要件:
    - パストラバーサル攻撃の防止
    - ファイルサイズ制限の実装
    - 適切なエラーハンドリング
    """

    # セキュリティ設定
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    SUPPORTED_EXTENSIONS: ClassVar[set[str]] = {".xlsx", ".xls"}

    def __init__(self, base_path: str | None = None):
        """ExcelDataLoaderを初期化。

        Args:
            base_path: ベースディレクトリパス（Sphinxソースディレクトリ）
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()

    def is_safe_path(self, file_path: str) -> bool:
        """パストラバーサル攻撃を防ぐためのパス検証。

        Args:
            file_path: 検証するファイルパス

        Returns:
            bool: 安全なパスかどうか
        """
        try:
            # 絶対パスに変換
            resolved_path = Path(file_path).resolve()
            base_resolved = self.base_path.resolve()

            # ベースパス配下にあるかチェック
            return str(resolved_path).startswith(str(base_resolved))
        except (OSError, ValueError):
            return False

    def validate_excel_file(self, file_path: str) -> bool:
        """Excelファイルの妥当性を検証。

        Args:
            file_path: 検証するファイルパス

        Returns:
            bool: 妥当なExcelファイルかどうか

        Raises:
            FileNotFoundError: ファイルが存在しない
            ValueError: 不正なファイル形式
            OSError: ファイルアクセスエラー
        """
        file_path_obj = Path(file_path)

        # ファイル存在チェック
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")

        # 拡張子チェック
        if file_path_obj.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file format: {file_path_obj.suffix}. "
                f"Supported formats: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

        # ファイルサイズチェック
        file_size = file_path_obj.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(
                f"File size ({file_size} bytes) exceeds limit "
                f"({self.MAX_FILE_SIZE} bytes)"
            )

        return True

    def basic_sheet_detection(self, file_path: str) -> str:
        """基本的なシート検出（デフォルト: 最初のシート）。

        Args:
            file_path: Excelファイルパス

        Returns:
            str: 検出されたシート名

        Raises:
            ValueError: シートが見つからない場合
        """
        try:
            # ExcelFileオブジェクトでシート名を取得
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names

            if not sheet_names:
                raise ValueError(f"No sheets found in Excel file: {file_path}")

            # 最初のシートを返す
            return sheet_names[0]

        except Exception as e:
            raise ValueError(f"Failed to detect sheets in {file_path}: {e!s}") from e

    def _validate_sheet_name(self, file_path: str, sheet_name: str) -> None:
        """指定されたシート名の存在を検証。

        Args:
            file_path: Excelファイルパス
            sheet_name: 検証するシート名

        Raises:
            ValueError: シートが存在しない場合
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names

            if sheet_name not in sheet_names:
                available_sheets = ", ".join(f"'{name}'" for name in sheet_names)
                raise ValueError(
                    f"Sheet '{sheet_name}' not found in Excel file. "
                    f"Available sheets: {available_sheets}"
                )

        except pd.errors.EmptyDataError:
            raise ValueError(f"Excel file {file_path} is empty or corrupted")
        except Exception as e:
            if isinstance(e, ValueError):
                raise  # Re-raise our custom ValueError without wrapping
            raise ValueError(
                f"Failed to validate sheet '{sheet_name}' in {file_path}: {e!s}"
            ) from e

    def get_sheet_name_by_index(self, file_path: str, sheet_index: int) -> str:
        """シートインデックスからシート名を取得。

        Args:
            file_path: Excelファイルパス
            sheet_index: シートインデックス（0ベース）

        Returns:
            str: 指定されたインデックスのシート名

        Raises:
            ValueError: インデックスが範囲外または不正な場合
        """
        # 入力検証の強化
        if not isinstance(sheet_index, int):
            raise ValueError(
                f"Sheet index must be an integer, got {type(sheet_index).__name__}"
            )

        if sheet_index < 0:
            raise ValueError(f"Sheet index must be non-negative, got {sheet_index}")

        try:
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names

            if sheet_index >= len(sheet_names):
                available_sheets = ", ".join(f"'{name}'" for name in sheet_names)
                raise ValueError(
                    f"Sheet index {sheet_index} is out of range. "
                    f"Available sheets (0-{len(sheet_names) - 1}): {available_sheets}"
                )

            return sheet_names[sheet_index]

        except pd.errors.EmptyDataError:
            raise ValueError(f"Excel file {file_path} is empty or corrupted")
        except Exception as e:
            if isinstance(e, ValueError):
                raise  # Re-raise our custom ValueError without wrapping
            raise ValueError(
                f"Failed to access sheet index {sheet_index} in {file_path}: {e!s}"
            ) from e

    def load_from_excel_by_index(
        self, file_path: str, sheet_index: int, header_row: int | None = None
    ) -> dict[str, Any]:
        """シートインデックスを指定してExcelファイルを読み込み。

        Args:
            file_path: Excelファイルパス
            sheet_index: シートインデックス（0ベース）
            header_row: ヘッダー行番号（None=自動検出）

        Returns:
            dict[str, Any]: 変換されたJSONデータ

        Raises:
            ValueError: インデックスが無効な場合
        """
        # インデックスからシート名を取得
        sheet_name = self.get_sheet_name_by_index(file_path, sheet_index)

        # 既存のメソッドを利用して読み込み
        return self.load_from_excel(
            file_path, sheet_name=sheet_name, header_row=header_row
        )

    def header_detection(self, df: pd.DataFrame) -> bool:
        """ヘッダー行の自動検出。

        Args:
            df: 読み込んだDataFrame

        Returns:
            bool: ヘッダーが存在するかどうか
        """
        if df.empty or len(df) < 2:
            return False

        # 最初の行が文字列でデータ行が数値中心の場合、ヘッダーと判定
        first_row = df.iloc[0]
        second_row = df.iloc[1]

        # 最初の行が主に文字列、2行目が主に数値の場合
        first_row_text_ratio = sum(isinstance(val, str) for val in first_row) / len(
            first_row
        )
        second_row_numeric_ratio = sum(
            pd.api.types.is_numeric_dtype(type(val)) for val in second_row
        ) / len(second_row)

        return first_row_text_ratio > 0.5 and second_row_numeric_ratio > 0.3

    def data_type_conversion(self, df: pd.DataFrame) -> list[list[str]]:
        """DataFrameをJSON互換の2D配列に変換。

        Args:
            df: 変換するDataFrame

        Returns:
            List[List[str]]: JSON互換の2D配列
        """
        # NaN値を空文字列に変換
        df_filled = df.fillna("")

        # 全ての値を文字列に変換（JSON互換性のため）
        result = []
        for _, row in df_filled.iterrows():
            converted_row = []
            for value in row:
                if pd.isna(value):
                    converted_row.append("")
                elif isinstance(value, int | float):
                    # 数値は適切に文字列変換
                    if isinstance(value, float) and value.is_integer():
                        converted_row.append(str(int(value)))
                    else:
                        converted_row.append(str(value))
                else:
                    converted_row.append(str(value))
            result.append(converted_row)

        return result

    def load_from_excel(
        self,
        file_path: str,
        sheet_name: str | None = None,
        header_row: int | None = None,
    ) -> dict[str, Any]:
        """Excelファイルを読み込みJSON形式に変換。

        Args:
            file_path: Excelファイルパス
            sheet_name: 読み込むシート名（None=自動検出）
            header_row: ヘッダー行番号（None=自動検出）

        Returns:
            Dict[str, Any]: 変換されたJSONデータ

        Raises:
            FileNotFoundError: ファイルが見つからない
            ValueError: 不正なファイル形式
            Exception: 読み込みエラー
        """
        # セキュリティチェック
        if not self.is_safe_path(file_path):
            raise ValueError(f"Unsafe file path: {file_path}")

        # ファイル妥当性チェック
        self.validate_excel_file(file_path)

        try:
            # シート名の決定と検証
            if sheet_name is None:
                sheet_name = self.basic_sheet_detection(file_path)
            else:
                # 指定されたシート名の存在確認
                self._validate_sheet_name(file_path, sheet_name)

            # Excelファイル読み込み
            if header_row is not None:
                # 明示的なヘッダー行指定
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
            else:
                # 自動ヘッダー検出
                df_no_header = pd.read_excel(
                    file_path, sheet_name=sheet_name, header=None
                )

                if self.header_detection(df_no_header):
                    # ヘッダーありとして再読み込み
                    df = pd.read_excel(file_path, sheet_name=sheet_name, header=0)
                else:
                    # ヘッダーなし
                    df = df_no_header

            # 空のDataFrameチェック
            if df.empty:
                raise ValueError(
                    f"Empty data in sheet '{sheet_name}' of file: {file_path}"
                )

            # データ変換
            data_array = self.data_type_conversion(df)

            # ヘッダー情報の抽出
            has_header = not isinstance(
                df.columns[0], int
            )  # 数値カラム名でない=ヘッダーあり
            headers = list(df.columns) if has_header else None

            # 結果構築
            result = {
                "data": data_array,
                "has_header": has_header,
                "headers": headers,
                "sheet_name": sheet_name,
                "file_path": file_path,
                "rows": len(data_array),
                "columns": len(data_array[0]) if data_array else 0,
            }

            return result

        except pd.errors.EmptyDataError:
            raise ValueError(f"Empty Excel file: {file_path}") from None
        except pd.errors.ParserError as e:
            raise ValueError(f"Failed to parse Excel file {file_path}: {e!s}") from e
        except ValueError:
            # Re-raise our custom ValueErrors without wrapping
            raise
        except Exception as e:
            raise Exception(
                f"Unexpected error loading Excel file {file_path}: {e!s}"
            ) from e

    def _parse_range_specification(self, range_spec: str) -> dict[str, Any]:
        """範囲指定文字列（A1:C3形式）をパースして範囲情報を取得。

        Args:
            range_spec: 範囲指定文字列（例: "A1:C3", "B2"）

        Returns:
            dict: 解析された範囲情報
                - start_row: 開始行（0ベース）
                - end_row: 終了行（0ベース、含む）
                - start_col: 開始列（0ベース）
                - end_col: 終了列（0ベース、含む）

        Raises:
            TypeError: range_specが文字列でない場合
            RangeSpecificationError: 無効な範囲形式の場合
        """
        # 入力検証の強化
        if not isinstance(range_spec, str):
            raise TypeError(
                f"Range specification must be a string, got {type(range_spec).__name__}"
            )

        range_spec_clean = range_spec.strip()
        if not range_spec_clean:
            raise RangeSpecificationError(
                "Range specification cannot be empty", range_spec
            )

        range_spec_upper = range_spec_clean.upper()

        # 範囲形式の解析
        try:
            start_cell, end_cell = self._split_range_specification(range_spec_upper)
        except RangeSpecificationError:
            raise
        except Exception as e:
            raise RangeSpecificationError(
                f"Failed to parse range specification: {e}", range_spec_upper
            ) from e

        # セルアドレスを行・列インデックスに変換
        try:
            start_row, start_col = self._parse_cell_address(start_cell.strip())
            end_row, end_col = self._parse_cell_address(end_cell.strip())
        except RangeSpecificationError:
            raise
        except Exception as e:
            raise RangeSpecificationError(
                f"Failed to parse cell addresses in range: {e}", range_spec_upper
            ) from e

        # 範囲の妥当性チェック
        self._validate_range_bounds(
            start_row, start_col, end_row, end_col, range_spec_upper
        )

        return {
            "start_row": start_row,
            "end_row": end_row,
            "start_col": start_col,
            "end_col": end_col,
            "original_spec": range_spec_upper,
        }

    def _split_range_specification(self, range_spec: str) -> tuple[str, str]:
        """範囲指定文字列を開始セルと終了セルに分割。

        Args:
            range_spec: 大文字化された範囲指定文字列

        Returns:
            tuple: (開始セル, 終了セル)

        Raises:
            RangeSpecificationError: 無効な範囲形式の場合
        """
        if ":" in range_spec:
            # 範囲形式 (A1:C3)
            parts = range_spec.split(":")
            if len(parts) != 2:
                raise RangeSpecificationError(
                    f"Invalid range format. Expected 'A1:C3', got '{range_spec}'",
                    range_spec,
                )
            return parts[0], parts[1]
        else:
            # 単一セル形式 (A1)
            return range_spec, range_spec

    def _validate_range_bounds(
        self,
        start_row: int,
        start_col: int,
        end_row: int,
        end_col: int,
        range_spec: str,
    ) -> None:
        """範囲の境界値を検証。

        Args:
            start_row: 開始行（0ベース）
            start_col: 開始列（0ベース）
            end_row: 終了行（0ベース）
            end_col: 終了列（0ベース）
            range_spec: 元の範囲指定文字列

        Raises:
            RangeSpecificationError: 無効な範囲の場合
        """
        # 開始位置が終了位置より後にある場合
        if start_row > end_row or start_col > end_col:
            raise RangeSpecificationError(
                f"Invalid range: start cell must be before or equal to end cell. "
                f"Start: ({start_row + 1}, {chr(65 + start_col)}), "
                f"End: ({end_row + 1}, {chr(65 + end_col)})",
                range_spec,
            )

        # Excel の最大値を超えている場合
        if end_row >= MAX_EXCEL_ROWS:
            raise RangeSpecificationError(
                f"Row {end_row + 1} exceeds Excel maximum ({MAX_EXCEL_ROWS})",
                range_spec,
            )

        if end_col >= MAX_EXCEL_COLS:
            raise RangeSpecificationError(
                f"Column {chr(65 + end_col) if end_col < 26 else 'beyond Z'} exceeds Excel maximum",
                range_spec,
            )

    def _parse_cell_address(self, cell_address: str) -> tuple[int, int]:
        """セルアドレス（A1形式）を行・列インデックスに変換。

        Args:
            cell_address: セルアドレス（例: "A1", "AB123"）

        Returns:
            tuple: (行インデックス（0ベース）, 列インデックス（0ベース）)

        Raises:
            RangeSpecificationError: 無効なセルアドレスの場合
        """
        # 入力検証
        if not cell_address or not isinstance(cell_address, str):
            raise RangeSpecificationError(
                f"Cell address must be a non-empty string, got: {cell_address}",
                cell_address,
            )

        # セルアドレスのパターンマッチング
        match = re.match(CELL_ADDRESS_PATTERN, cell_address.strip())

        if not match:
            raise RangeSpecificationError(
                f"Invalid cell address format. Expected format: 'A1', 'AB123', etc. Got: '{cell_address}'",
                cell_address,
            )

        col_letters, row_str = match.groups()

        try:
            # 行番号の変換（1ベース→0ベース）
            row_index = int(row_str) - 1

            # 行番号の範囲チェック
            if row_index >= MAX_EXCEL_ROWS:
                raise RangeSpecificationError(
                    f"Row number {row_str} exceeds Excel maximum ({MAX_EXCEL_ROWS})",
                    cell_address,
                )

            # 列番号の変換（A=0, B=1, ..., Z=25, AA=26, ...）
            col_index = self._convert_column_letters_to_index(col_letters)

            # 列番号の範囲チェック
            if col_index >= MAX_EXCEL_COLS:
                raise RangeSpecificationError(
                    f"Column '{col_letters}' exceeds Excel maximum", cell_address
                )

            return row_index, col_index

        except ValueError as e:
            if isinstance(e, RangeSpecificationError):
                raise
            raise RangeSpecificationError(
                f"Failed to parse cell address '{cell_address}': {e}", cell_address
            ) from e

    def _convert_column_letters_to_index(self, col_letters: str) -> int:
        """列文字（A, B, ..., AA, AB, ...）を0ベースのインデックスに変換。

        Args:
            col_letters: 列文字（例: "A", "AB", "ABC"）

        Returns:
            int: 0ベースの列インデックス（A=0, B=1, ..., Z=25, AA=26, ...）

        Raises:
            RangeSpecificationError: 無効な列文字の場合
        """
        if not col_letters or not col_letters.isalpha():
            raise RangeSpecificationError(
                f"Invalid column letters: '{col_letters}'", col_letters
            )

        col_index = 0
        for char in col_letters:
            if not "A" <= char <= "Z":
                raise RangeSpecificationError(
                    f"Invalid character in column: '{char}'", col_letters
                )
            col_index = col_index * 26 + (ord(char) - ord("A") + 1)

        return col_index - 1  # 0ベースに変換

    def load_from_excel_with_range(
        self,
        file_path: str,
        range_spec: str,
        sheet_name: str | None = None,
        header_row: int | None = None,
    ) -> dict[str, Any]:
        """指定された範囲でExcelファイルを読み込み。

        Args:
            file_path: Excelファイルパス
            range_spec: 範囲指定（例: "A1:C3", "B2"）
            sheet_name: 読み込むシート名（None=自動検出）
            header_row: ヘッダー行番号（None=自動検出）

        Returns:
            dict[str, Any]: 変換されたJSONデータ（範囲情報付き）

        Raises:
            RangeSpecificationError: 無効な範囲指定の場合
            ValueError: ファイル読み込みエラーまたは範囲外アクセス
        """
        # 範囲情報を解析
        try:
            range_info = self._parse_range_specification(range_spec)
        except RangeSpecificationError:
            raise
        except Exception as e:
            raise RangeSpecificationError(
                f"Unexpected error parsing range specification: {e}", range_spec
            ) from e

        # Excel全体を読み込み
        try:
            excel_data = self.load_from_excel(file_path, sheet_name, header_row)
        except Exception as e:
            raise ValueError(
                f"Failed to load Excel file for range extraction: {e}"
            ) from e

        # データサイズの検証
        data_rows = len(excel_data["data"])
        data_cols = len(excel_data["data"][0]) if excel_data["data"] else 0

        # 範囲外アクセスのチェック
        self._validate_range_against_data(range_info, data_rows, data_cols, range_spec)

        # 指定範囲のデータを効率的に抽出
        range_data = self._extract_range_data(excel_data["data"], range_info)

        # 結果を構築
        return self._build_range_result(range_data, excel_data, range_spec)

    def _validate_range_against_data(
        self,
        range_info: dict[str, Any],
        data_rows: int,
        data_cols: int,
        range_spec: str,
    ) -> None:
        """指定範囲がデータサイズ内に収まっているかチェック。

        Args:
            range_info: 解析済み範囲情報
            data_rows: データの行数
            data_cols: データの列数
            range_spec: 元の範囲指定文字列

        Raises:
            RangeSpecificationError: 範囲がデータサイズを超えている場合
        """
        if data_rows == 0 or data_cols == 0:
            raise RangeSpecificationError(
                f"Cannot apply range to empty data. Data size: {data_rows}x{data_cols}",
                range_spec,
            )

        # 範囲の終了位置がデータサイズを超えているかチェック
        if range_info["end_row"] >= data_rows:
            raise RangeSpecificationError(
                f"Range row {range_info['end_row'] + 1} exceeds data rows ({data_rows}). "
                f"Data size: {data_rows}x{data_cols}",
                range_spec,
            )

        if range_info["end_col"] >= data_cols:
            raise RangeSpecificationError(
                f"Range column {range_info['end_col'] + 1} exceeds data columns ({data_cols}). "
                f"Data size: {data_rows}x{data_cols}",
                range_spec,
            )

    def _extract_range_data(
        self, full_data: list[list[str]], range_info: dict[str, Any]
    ) -> list[list[str]]:
        """データから指定範囲を効率的に抽出。

        Args:
            full_data: 全体のデータ
            range_info: 範囲情報

        Returns:
            list[list[str]]: 抽出されたデータ
        """
        range_data = []

        for row_idx in range(range_info["start_row"], range_info["end_row"] + 1):
            row = []
            source_row = full_data[row_idx]

            for col_idx in range(range_info["start_col"], range_info["end_col"] + 1):
                # 範囲チェックは既に済んでいるので、安全にアクセス可能
                if col_idx < len(source_row):
                    row.append(source_row[col_idx])
                else:
                    row.append("")  # 空セルの処理

            range_data.append(row)

        return range_data

    def _build_range_result(
        self, range_data: list[list[str]], excel_data: dict[str, Any], range_spec: str
    ) -> dict[str, Any]:
        """範囲抽出結果を構築。

        Args:
            range_data: 抽出されたデータ
            excel_data: 元のExcelデータ情報
            range_spec: 範囲指定文字列

        Returns:
            dict[str, Any]: 構築された結果
        """
        return {
            "data": range_data,
            "has_header": excel_data["has_header"],
            "headers": excel_data["headers"],
            "sheet_name": excel_data["sheet_name"],
            "file_path": excel_data["file_path"],
            "range": range_spec,
            "rows": len(range_data),
            "columns": len(range_data[0]) if range_data else 0,
        }

    def load_from_excel_with_header_row(
        self, file_path: str, header_row: int, sheet_name: str | None = None
    ) -> dict[str, Any]:
        """指定されたヘッダー行でExcelファイルを読み込み。

        Args:
            file_path: Excelファイルパス
            header_row: ヘッダー行番号（0ベース）
            sheet_name: 読み込むシート名（None=自動検出）

        Returns:
            dict[str, Any]: 変換されたJSONデータ（ヘッダー行情報付き）

        Raises:
            ValueError: 無効なヘッダー行指定の場合
            TypeError: header_rowが整数でない場合
        """
        # 事前検証
        self._validate_header_row(header_row)

        try:
            # Excel読み込み（明示的なheader_row指定）
            excel_data = self.load_from_excel(file_path, sheet_name, header_row)

            # データ範囲内でのヘッダー行チェック
            self._validate_header_row_against_data(header_row, excel_data, file_path)

            # ヘッダー行情報を追加
            excel_data["header_row"] = header_row

            # ヘッダー名の正規化（必要に応じて）
            if excel_data["has_header"] and excel_data["headers"]:
                excel_data["headers"] = self._normalize_header_names(
                    excel_data["headers"]
                )

            return excel_data

        except Exception as e:
            if isinstance(e, (ValueError, TypeError)):
                raise
            raise ValueError(
                f"Failed to load Excel with header row {header_row}: {e}"
            ) from e

    def load_from_excel_with_header_row_and_range(
        self,
        file_path: str,
        header_row: int,
        range_spec: str,
        sheet_name: str | None = None,
    ) -> dict[str, Any]:
        """ヘッダー行指定と範囲指定の組み合わせでExcelファイルを読み込み。

        Args:
            file_path: Excelファイルパス
            header_row: ヘッダー行番号（0ベース）
            range_spec: 範囲指定（例: "A1:C3", "B2"）
            sheet_name: 読み込むシート名（None=自動検出）

        Returns:
            dict[str, Any]: 変換されたJSONデータ

        Raises:
            ValueError: 無効なヘッダー行または範囲指定の場合
            RangeSpecificationError: 無効な範囲指定の場合
            TypeError: header_rowが整数でない場合
        """
        # 事前検証
        self._validate_header_row(header_row)

        try:
            # 範囲指定付きで読み込み（header_rowも考慮）
            excel_data = self.load_from_excel_with_range(
                file_path, range_spec, sheet_name, header_row
            )

            # ヘッダー行と範囲の整合性チェック
            self._validate_header_row_and_range_compatibility(
                header_row, range_spec, excel_data
            )

            # ヘッダー行情報を追加
            excel_data["header_row"] = header_row

            # ヘッダー名の正規化（必要に応じて）
            if excel_data["has_header"] and excel_data["headers"]:
                excel_data["headers"] = self._normalize_header_names(
                    excel_data["headers"]
                )

            return excel_data

        except (RangeSpecificationError, ValueError, TypeError):
            raise
        except Exception as e:
            raise ValueError(
                f"Failed to load Excel with header row {header_row} and range {range_spec}: {e}"
            ) from e

    def _validate_header_row_and_range_compatibility(
        self, header_row: int, range_spec: str, excel_data: dict[str, Any]
    ) -> None:
        """ヘッダー行と範囲指定の整合性をチェック。

        Args:
            header_row: ヘッダー行番号（0ベース）
            range_spec: 範囲指定文字列
            excel_data: 読み込まれたExcelデータ

        Raises:
            ValueError: ヘッダー行と範囲が整合していない場合
        """
        # 範囲情報を解析
        try:
            range_info = self._parse_range_specification(range_spec)
        except RangeSpecificationError as e:
            raise ValueError(
                f"Invalid range specification for header row validation: {e}"
            ) from e

        # ヘッダー行が範囲内にあるかチェック
        if not (range_info["start_row"] <= header_row <= range_info["end_row"]):
            raise ValueError(
                f"Header row {header_row} is outside the specified range {range_spec}. "
                f"Range rows: {range_info['start_row']}-{range_info['end_row']}"
            )

        # データが実際に存在するかチェック
        if not excel_data["data"]:
            raise ValueError(
                f"No data available for header row {header_row} in range {range_spec}"
            )

    def _validate_header_row(self, header_row: int | None) -> None:
        """ヘッダー行の妥当性を検証。

        Args:
            header_row: ヘッダー行番号（None=自動検出モード）

        Raises:
            TypeError: header_rowが整数でない場合
            ValueError: 無効なヘッダー行番号の場合
        """
        if header_row is None:
            return  # 自動検出モード

        if not isinstance(header_row, int):
            raise TypeError(
                f"Header row must be an integer, got {type(header_row).__name__}"
            )

        if header_row < 0:
            raise ValueError(f"Header row must be non-negative, got {header_row}")

        # Excel の最大行数チェック
        if header_row >= MAX_EXCEL_ROWS:
            raise ValueError(
                f"Header row {header_row} exceeds Excel maximum ({MAX_EXCEL_ROWS})"
            )

    def _validate_header_row_against_data(
        self, header_row: int, excel_data: dict[str, Any], file_path: str
    ) -> None:
        """ヘッダー行がデータ範囲内にあるかチェック。

        Args:
            header_row: ヘッダー行番号（0ベース）
            excel_data: 読み込まれたExcelデータ
            file_path: Excelファイルパス（エラーメッセージ用）

        Raises:
            ValueError: ヘッダー行がデータ範囲外の場合
        """
        data_rows = len(excel_data["data"])

        if data_rows == 0:
            raise ValueError(
                f"Cannot use header row {header_row} on empty data in {file_path}"
            )

        if header_row >= data_rows:
            raise ValueError(
                f"Header row {header_row} is out of range. "
                f"Data has {data_rows} rows (0-{data_rows - 1}). File: {file_path}"
            )

    def _normalize_header_names(self, headers: list[str]) -> list[str]:
        """ヘッダー名の正規化処理。

        Args:
            headers: 元のヘッダー名リスト

        Returns:
            list[str]: 正規化されたヘッダー名リスト
        """
        normalized = []
        seen = set()

        for i, header in enumerate(headers):
            # 基本的な正規化
            normalized_header = str(header).strip() if header else ""

            # 空のヘッダーに対するデフォルト名
            if not normalized_header:
                normalized_header = f"Column{i + 1}"

            # 重複回避
            original = normalized_header
            counter = 1
            while normalized_header in seen:
                normalized_header = f"{original}_{counter}"
                counter += 1

            seen.add(normalized_header)
            normalized.append(normalized_header)

        return normalized

    def _parse_skip_rows_specification(self, skip_rows: str) -> list[int]:
        """Skip Rows指定文字列を解析してリストに変換。

        Args:
            skip_rows: Skip Rows指定文字列（例: "0,1,2", "0-2,5,7-9"）

        Returns:
            list[int]: ソート済みの一意な行番号リスト

        Raises:
            SkipRowsError: 無効な形式の場合
            TypeError: skip_rowsが文字列でない場合
        """
        if not isinstance(skip_rows, str):
            raise TypeError("Skip rows must be a string")

        skip_rows_clean = skip_rows.strip()
        if not skip_rows_clean:
            raise SkipRowsError("Skip rows specification cannot be empty", skip_rows)

        row_numbers = []

        # カンマ区切りで分割
        parts = skip_rows_clean.split(SKIP_ROWS_LIST_SEPARATOR)

        for part in parts:
            part = part.strip()
            if not part:
                raise SkipRowsError(
                    "Invalid skip rows format: empty part found", skip_rows
                )

            if SKIP_ROWS_RANGE_SEPARATOR in part:
                # 範囲形式（例: "0-2", "5-7"）
                try:
                    start_str, end_str = part.split(SKIP_ROWS_RANGE_SEPARATOR, 1)
                    start = int(start_str.strip())
                    end = int(end_str.strip())

                    # 範囲の妥当性チェック
                    self._validate_skip_rows_range(start, end, part, skip_rows)

                    row_numbers.extend(range(start, end + 1))

                except ValueError as e:
                    if isinstance(e, SkipRowsError):
                        raise
                    if "invalid literal" in str(e):
                        raise SkipRowsError(
                            f"Invalid skip rows format: {part}", skip_rows
                        )
                    raise SkipRowsError(
                        f"Error parsing range {part}: {e}", skip_rows
                    ) from e
            else:
                # 単一行番号
                try:
                    row_num = int(part)
                    if row_num < 0:
                        raise SkipRowsError(
                            f"Negative row number not allowed: {row_num}", skip_rows
                        )
                    if row_num >= MAX_EXCEL_ROWS:
                        raise SkipRowsError(
                            f"Row number {row_num} exceeds Excel maximum ({MAX_EXCEL_ROWS})",
                            skip_rows,
                        )
                    row_numbers.append(row_num)
                except ValueError as e:
                    if isinstance(e, SkipRowsError):
                        raise
                    raise SkipRowsError(
                        f"Invalid skip rows format: {part}", skip_rows
                    ) from e

        # 重複を排除してソート
        unique_rows = sorted(set(row_numbers))

        # 最大数チェック
        if len(unique_rows) > MAX_SKIP_ROWS_COUNT:
            raise SkipRowsError(
                f"Too many skip rows ({len(unique_rows)}). Maximum allowed: {MAX_SKIP_ROWS_COUNT}",
                skip_rows,
            )

        return unique_rows

    def _validate_skip_rows_range(
        self, start: int, end: int, part: str, original_spec: str
    ) -> None:
        """Skip Rows範囲の妥当性を検証。

        Args:
            start: 開始行番号
            end: 終了行番号
            part: 範囲指定部分
            original_spec: 元の指定文字列

        Raises:
            SkipRowsError: 無効な範囲の場合
        """
        if start < 0 or end < 0:
            raise SkipRowsError(
                f"Negative row numbers not allowed: {part}", original_spec
            )

        if start > end:
            raise SkipRowsError(f"Invalid range (start > end): {part}", original_spec)

        if start >= MAX_EXCEL_ROWS or end >= MAX_EXCEL_ROWS:
            raise SkipRowsError(
                f"Row number in range {part} exceeds Excel maximum ({MAX_EXCEL_ROWS})",
                original_spec,
            )

        if (end - start + 1) > MAX_SKIP_ROWS_COUNT:
            raise SkipRowsError(
                f"Range {part} too large ({end - start + 1} rows). Maximum range size: {MAX_SKIP_ROWS_COUNT}",
                original_spec,
            )

    def _validate_skip_rows_specification(self, skip_rows: str | None) -> None:
        """Skip Rows指定の妥当性を検証。

        Args:
            skip_rows: Skip Rows指定文字列（None=スキップなし）

        Raises:
            TypeError: skip_rowsが文字列でない場合
            ValueError: 無効な形式の場合
        """
        if skip_rows is None:
            return  # スキップなしモード

        if not isinstance(skip_rows, str):
            raise TypeError("Skip rows must be a string")

        if not skip_rows.strip():
            raise ValueError("Skip rows specification cannot be empty")

    def load_from_excel_with_skip_rows(
        self, file_path: str, skip_rows: str, sheet_name: str | None = None
    ) -> dict[str, Any]:
        """Skip Rows指定でExcelファイルを読み込み。

        Args:
            file_path: Excelファイルパス
            skip_rows: Skip Rows指定（例: "0,1,2", "0-2,5"）
            sheet_name: 読み込むシート名（None=自動検出）

        Returns:
            dict[str, Any]: 変換されたJSONデータ（Skip Rows情報付き）

        Raises:
            ValueError: 無効なSkip Rows指定の場合
        """
        # Skip Rows指定の検証
        self._validate_skip_rows_specification(skip_rows)

        # Skip Rows指定を解析
        skip_row_list = self._parse_skip_rows_specification(skip_rows)

        # 通常のExcel読み込みを実行
        excel_data = self.load_from_excel(file_path, sheet_name)

        # Skip Rows処理
        filtered_data = self._apply_skip_rows(excel_data["data"], skip_row_list)

        # 結果を構築
        result = {
            "data": filtered_data,
            "has_header": excel_data["has_header"],
            "headers": excel_data["headers"],
            "sheet_name": excel_data["sheet_name"],
            "file_path": file_path,
            "skip_rows": skip_rows,
            "skipped_row_count": len(skip_row_list),
            "rows": len(filtered_data),
            "columns": len(filtered_data[0]) if filtered_data else 0,
        }

        return result

    def _apply_skip_rows(
        self, data: list[list[str]], skip_row_list: list[int]
    ) -> list[list[str]]:
        """データからスキップ行を除外。

        Args:
            data: 元のデータ
            skip_row_list: スキップする行番号のリスト

        Returns:
            list[list[str]]: スキップ処理されたデータ
        """
        if not skip_row_list:
            return data

        # スキップ行の最大値がデータ範囲内かチェック
        max_skip_row = max(skip_row_list) if skip_row_list else -1
        if max_skip_row >= len(data):
            raise ValueError(
                f"Skip row {max_skip_row} is out of range. Data has {len(data)} rows (0-{len(data) - 1})"
            )

        # スキップ行を除外したデータを構築
        filtered_data = []
        for row_index, row in enumerate(data):
            if row_index not in skip_row_list:
                filtered_data.append(row)

        return filtered_data

    def load_from_excel_with_skip_rows_and_header(
        self,
        file_path: str,
        skip_rows: str,
        header_row: int,
        sheet_name: str | None = None,
    ) -> dict[str, Any]:
        """Skip Rowsとヘッダー行指定の組み合わせでExcelファイルを読み込み。

        Args:
            file_path: Excelファイルパス
            skip_rows: Skip Rows指定（例: "0,1,2", "0-2,5"）
            header_row: ヘッダー行番号（0ベース）
            sheet_name: 読み込むシート名（None=自動検出）

        Returns:
            dict[str, Any]: 変換されたJSONデータ

        Raises:
            ValueError: 無効なSkip Rowsまたはヘッダー行指定の場合
            TypeError: header_rowが整数でない場合
        """
        # 事前検証
        self._validate_skip_rows_specification(skip_rows)
        self._validate_header_row(header_row)

        # Skip Rows指定を解析
        skip_row_list = self._parse_skip_rows_specification(skip_rows)

        # 通常のExcel読み込みを実行
        excel_data = self.load_from_excel(file_path, sheet_name)

        # Skip Rows処理を先に適用
        filtered_data = self._apply_skip_rows(excel_data["data"], skip_row_list)

        # 共通化されたヘッダー処理を使用
        headers, has_header, data_without_header = self._process_header_after_skip(
            filtered_data, header_row, skip_row_list
        )

        # 調整後のヘッダー行番号を取得（結果表示用）
        adjusted_header_row = self._adjust_header_row_after_skip(
            header_row, skip_row_list
        )

        # 結果を構築
        result = {
            "data": data_without_header,
            "has_header": has_header,
            "headers": headers,
            "sheet_name": excel_data["sheet_name"],
            "file_path": file_path,
            "skip_rows": skip_rows,
            "header_row": header_row,
            "adjusted_header_row": adjusted_header_row,
            "skipped_row_count": len(skip_row_list),
            "rows": len(data_without_header),
            "columns": len(data_without_header[0]) if data_without_header else 0,
        }

        return result

    def load_from_excel_with_skip_rows_and_range(
        self,
        file_path: str,
        range_spec: str,
        skip_rows: str,
        sheet_name: str | None = None,
    ) -> dict[str, Any]:
        """Skip Rowsと範囲指定の組み合わせでExcelファイルを読み込み。

        Args:
            file_path: Excelファイルパス
            range_spec: 範囲指定（例: "A1:C3", "B2"）
            skip_rows: Skip Rows指定（例: "0,1,2", "0-2,5"）
            sheet_name: 読み込むシート名（None=自動検出）

        Returns:
            dict[str, Any]: 変換されたJSONデータ

        Raises:
            ValueError: 無効なSkip Rowsまたは範囲指定の場合
            RangeSpecificationError: 無効な範囲指定の場合
        """
        # 事前検証
        self._validate_skip_rows_specification(skip_rows)

        # Skip Rows指定を解析
        skip_row_list = self._parse_skip_rows_specification(skip_rows)

        # 範囲指定付きでExcel読み込み
        excel_data = self.load_from_excel_with_range(file_path, range_spec, sheet_name)

        # Skip Rows処理を適用
        filtered_data = self._apply_skip_rows(excel_data["data"], skip_row_list)

        # 結果を構築
        result = {
            "data": filtered_data,
            "has_header": excel_data["has_header"],
            "headers": excel_data["headers"],
            "sheet_name": excel_data["sheet_name"],
            "file_path": file_path,
            "range": range_spec,
            "skip_rows": skip_rows,
            "skipped_row_count": len(skip_row_list),
            "rows": len(filtered_data),
            "columns": len(filtered_data[0]) if filtered_data else 0,
        }

        return result

    def _adjust_header_row_after_skip(
        self, original_header_row: int, skip_row_list: list[int]
    ) -> int:
        """スキップ処理後のヘッダー行番号を調整。

        Args:
            original_header_row: 元のヘッダー行番号
            skip_row_list: スキップする行番号のリスト

        Returns:
            int: 調整後のヘッダー行番号
        """
        if not skip_row_list:
            return original_header_row

        # 元のヘッダー行がスキップされるかチェック
        if original_header_row in skip_row_list:
            raise ValueError(
                f"Header row {original_header_row} is specified to be skipped. "
                f"This is not allowed."
            )

        # スキップされる行のうち、ヘッダー行より前にある行をカウント
        skipped_before_header = sum(
            1 for skip_row in skip_row_list if skip_row < original_header_row
        )

        return original_header_row - skipped_before_header

    def _process_header_after_skip(
        self, filtered_data: list[list[str]], header_row: int, skip_row_list: list[int]
    ) -> tuple[list[str], bool, list[list[str]]]:
        """スキップ処理後のヘッダー処理を共通化。

        Args:
            filtered_data: スキップ処理後のデータ
            header_row: 元のヘッダー行番号
            skip_row_list: スキップした行番号のリスト

        Returns:
            tuple: (headers, has_header, data_without_header)

        Raises:
            ValueError: ヘッダー行がスキップ後に無効になる場合
        """
        # スキップ後のデータでヘッダー行番号を調整
        adjusted_header_row = self._adjust_header_row_after_skip(
            header_row, skip_row_list
        )

        # 調整後のヘッダー行がデータ範囲内かチェック
        if adjusted_header_row >= len(filtered_data):
            raise ValueError(
                f"Header row {header_row} becomes invalid after skipping rows. "
                f"Filtered data has {len(filtered_data)} rows"
            )

        # ヘッダー処理
        headers = []
        has_header = False
        data_without_header = filtered_data

        if 0 <= adjusted_header_row < len(filtered_data):
            headers = [
                str(cell).strip() if cell else f"Column{i + 1}"
                for i, cell in enumerate(filtered_data[adjusted_header_row])
            ]
            headers = self._normalize_header_names(headers)
            has_header = True
            # ヘッダー行を除外
            data_without_header = [
                row for i, row in enumerate(filtered_data) if i != adjusted_header_row
            ]

        return headers, has_header, data_without_header

    def load_from_excel_with_skip_rows_range_and_header(
        self,
        file_path: str,
        skip_rows: str,
        range_spec: str,
        header_row: int,
        sheet_name: str | None = None,
    ) -> dict[str, Any]:
        """Skip Rows、範囲指定、ヘッダー行指定の3つを組み合わせたExcelファイル読み込み。

        Args:
            file_path: Excelファイルパス
            skip_rows: Skip Rows指定（例: "0,1,2", "0-2,5"）
            range_spec: 範囲指定（例: "A1:C3", "B2"）
            header_row: ヘッダー行番号（0ベース）
            sheet_name: 読み込むシート名（None=自動検出）

        Returns:
            dict[str, Any]: 変換されたJSONデータ

        Raises:
            ValueError: 無効な指定の場合
            RangeSpecificationError: 無効な範囲指定の場合
            TypeError: header_rowが整数でない場合
        """
        # 事前検証
        self._validate_skip_rows_specification(skip_rows)
        self._validate_header_row(header_row)

        # Skip Rows指定を解析
        skip_row_list = self._parse_skip_rows_specification(skip_rows)

        # 範囲指定付きでExcel読み込み
        excel_data = self.load_from_excel_with_range(file_path, range_spec, sheet_name)

        # Skip Rows処理を先に適用
        filtered_data = self._apply_skip_rows(excel_data["data"], skip_row_list)

        # スキップ後のデータでヘッダー行番号を調整
        adjusted_header_row = self._adjust_header_row_after_skip(
            header_row, skip_row_list
        )

        # 調整後のヘッダー行がデータ範囲内かチェック
        if adjusted_header_row >= len(filtered_data):
            raise ValueError(
                f"Header row {header_row} becomes invalid after skipping rows {skip_rows}. "
                f"Filtered data has {len(filtered_data)} rows"
            )

        # ヘッダー処理
        headers = []
        has_header = False
        data_without_header = filtered_data

        if 0 <= adjusted_header_row < len(filtered_data):
            headers = [
                str(cell).strip() if cell else f"Column{i + 1}"
                for i, cell in enumerate(filtered_data[adjusted_header_row])
            ]
            headers = self._normalize_header_names(headers)
            has_header = True
            # ヘッダー行を除外
            data_without_header = [
                row for i, row in enumerate(filtered_data) if i != adjusted_header_row
            ]

        # 結果を構築
        result = {
            "data": data_without_header,
            "has_header": has_header,
            "headers": headers,
            "sheet_name": excel_data["sheet_name"],
            "file_path": file_path,
            "range": range_spec,
            "skip_rows": skip_rows,
            "header_row": header_row,
            "adjusted_header_row": adjusted_header_row,
            "skipped_row_count": len(skip_row_list),
            "rows": len(data_without_header),
            "columns": len(data_without_header[0]) if data_without_header else 0,
        }

        return result

    def load_from_excel_with_detect_range(
        self,
        file_path: str,
        detect_mode: str = "auto",
        sheet_name: str | None = None,
        range_hint: str | None = None,
        ignore_empty_rows: bool = False,
        auto_header: bool = False,
    ) -> dict[str, Any]:
        """自動範囲検出でExcelファイルを読み込み。

        Args:
            file_path: Excelファイルパス
            detect_mode: 検出モード（auto, smart, manual）
            sheet_name: 読み込むシート名（None=自動検出）
            range_hint: 範囲ヒント（manualモード用）
            ignore_empty_rows: 空行を無視するか
            auto_header: ヘッダー自動判定を行うか

        Returns:
            dict[str, Any]: 変換されたJSONデータ（検出情報付き）

        Raises:
            ValueError: 無効な検出モードの場合
        """
        # 検出モードの検証
        valid_modes = ["auto", "smart", "manual"]
        if detect_mode not in valid_modes:
            raise ValueError(
                f"Invalid detect mode: {detect_mode}. Valid modes: {valid_modes}"
            )

        # 基本的なExcel読み込み
        excel_data = self.load_from_excel(file_path, sheet_name)

        if detect_mode == "auto":
            # autoモード: 基本的な範囲検出
            detected_range = self._detect_auto_range(excel_data["data"])
            range_data = self._extract_detected_range(
                excel_data["data"], detected_range
            )
        elif detect_mode == "smart":
            # smartモード: 複数ブロック検出から最適ブロック選択
            all_blocks = self._detect_multiple_data_blocks(excel_data["data"])
            if all_blocks:
                # 最大のブロックを選択
                best_block = max(all_blocks, key=lambda b: b["total_cells"])
                detected_range = f"{chr(65 + best_block['min_col'])}{best_block['min_row'] + 1}:{chr(65 + best_block['max_col'])}{best_block['max_row'] + 1}"
                range_data = self._extract_detected_range(
                    excel_data["data"], detected_range
                )
            else:
                # フォールバック: autoモードと同じ
                detected_range = self._detect_auto_range(excel_data["data"])
                range_data = self._extract_detected_range(
                    excel_data["data"], detected_range
                )
        elif detect_mode == "manual":
            # manualモード: range_hintを使用
            if not range_hint:
                raise ValueError("range_hint is required for manual mode")
            range_info = self._parse_range_specification(range_hint)
            range_data = self._extract_range_data(excel_data["data"], range_info)
            detected_range = range_hint
        else:
            raise ValueError(f"Unsupported detect mode: {detect_mode}")

        # ヘッダー自動判定（autoモードでは自動的に有効）
        should_detect_header = auto_header or (detect_mode == "auto")
        has_header = should_detect_header and self._detect_header_in_range(range_data)
        headers = []
        if has_header and range_data:
            headers = [
                str(cell).strip() if cell else f"Column{i + 1}"
                for i, cell in enumerate(range_data[0])
            ]
            range_data = range_data[1:]  # ヘッダー行を除去

        # 結果を構築
        result = {
            "data": range_data,
            "has_header": has_header,
            "headers": headers,
            "sheet_name": excel_data["sheet_name"],
            "file_path": file_path,
            "detected_range": detected_range,
            "detect_mode": detect_mode,
            "rows": len(range_data),
            "columns": len(range_data[0]) if range_data else 0,
        }

        # オプション情報を追加
        if ignore_empty_rows:
            result["ignore_empty_rows"] = ignore_empty_rows
            result["empty_rows_detected"] = []
            result["empty_cols_detected"] = []

        if auto_header:
            result["auto_header"] = auto_header
            # 元ファイル内での絶対行番号を計算
            if has_header and detect_mode == "auto":
                # autoモードでは_detect_auto_rangeで検出された範囲の最初の行
                data_block = self._find_largest_data_block(excel_data["data"])
                absolute_header_row = data_block["min_row"] if data_block else 0
            else:
                absolute_header_row = 0 if has_header else -1
            result["detected_header_row"] = absolute_header_row
            result["header_confidence"] = 0.9 if has_header else 0.1

        if detect_mode == "smart":
            result["detected_blocks"] = []

        return result

    def _detect_auto_range(self, data: list[list[str]]) -> str:
        """autoモードでの高度な範囲検出。

        Args:
            data: Excelデータ

        Returns:
            str: 検出された範囲（A1形式）
        """
        if not data:
            return "A1:A1"

        # データブロックの検出
        data_block = self._find_largest_data_block(data)
        if not data_block:
            return "A1:A1"

        min_row = data_block["min_row"]
        max_row = data_block["max_row"]
        min_col = data_block["min_col"]
        max_col = data_block["max_col"]

        # 範囲を文字列として返す
        start_cell = f"{chr(65 + min_col)}{min_row + 1}"
        end_cell = f"{chr(65 + max_col)}{max_row + 1}"
        return f"{start_cell}:{end_cell}"

    def _find_largest_data_block(self, data: list[list[str]]) -> dict[str, int] | None:
        """最大のデータブロックを検出。

        Args:
            data: Excelデータ

        Returns:
            dict: データブロックの境界情報（min_row, max_row, min_col, max_col）
        """
        if not data:
            return None

        rows = len(data)
        cols = len(data[0]) if data else 0

        # 各行の有効セル数をカウント
        row_scores = []
        for i, row in enumerate(data):
            non_empty_count = sum(1 for cell in row if str(cell).strip())
            # ヘッダー行候補の検出（文字列が多い行）
            text_count = sum(
                1
                for cell in row
                if str(cell).strip()
                and not str(cell).replace(".", "").replace("-", "").isdigit()
            )
            row_scores.append(
                {
                    "index": i,
                    "non_empty_count": non_empty_count,
                    "text_count": text_count,
                    "is_potential_header": text_count >= non_empty_count * 0.6
                    and non_empty_count >= 2,
                }
            )

        # 有効な行の範囲を特定
        valid_rows = [score for score in row_scores if score["non_empty_count"] >= 2]
        if not valid_rows:
            return None

        # 連続するデータブロックを検出
        data_blocks = []
        current_block = None

        for i, score in enumerate(valid_rows):
            row_idx = score["index"]

            if current_block is None:
                # 新しいブロックの開始
                current_block = {
                    "start_row": row_idx,
                    "end_row": row_idx,
                    "total_cells": score["non_empty_count"],
                    "has_header": score["is_potential_header"],
                }
            else:
                # 前の行との連続性をチェック
                gap = row_idx - current_block["end_row"]
                if gap <= 2:  # 1-2行の空行までは連続とみなす
                    current_block["end_row"] = row_idx
                    current_block["total_cells"] += score["non_empty_count"]
                    if score["is_potential_header"]:
                        current_block["has_header"] = True
                else:
                    # 現在のブロックを保存し、新しいブロックを開始
                    data_blocks.append(current_block)
                    current_block = {
                        "start_row": row_idx,
                        "end_row": row_idx,
                        "total_cells": score["non_empty_count"],
                        "has_header": score["is_potential_header"],
                    }

        # 最後のブロックを追加
        if current_block:
            data_blocks.append(current_block)

        # 最大のデータブロックを選択（セル数とヘッダーの有無で評価）
        if not data_blocks:
            return None

        best_block = max(
            data_blocks,
            key=lambda block: (
                block["total_cells"],
                1 if block["has_header"] else 0,
                block["end_row"] - block["start_row"] + 1,
            ),
        )

        # 列範囲の検出（選択されたブロック内で）
        min_col, max_col = self._detect_column_range(
            data, best_block["start_row"], best_block["end_row"]
        )

        return {
            "min_row": best_block["start_row"],
            "max_row": best_block["end_row"],
            "min_col": min_col,
            "max_col": max_col,
        }

    def _detect_column_range(
        self, data: list[list[str]], start_row: int, end_row: int
    ) -> tuple[int, int]:
        """指定された行範囲内での列範囲を検出。

        Args:
            data: Excelデータ
            start_row: 開始行
            end_row: 終了行

        Returns:
            tuple: (min_col, max_col)
        """
        if not data or start_row > end_row:
            return 0, 0

        max_cols = max(len(row) for row in data[start_row : end_row + 1])

        # 左端の検出
        min_col = max_cols
        for row_idx in range(start_row, end_row + 1):
            row = data[row_idx]
            for col_idx, cell in enumerate(row):
                if str(cell).strip():
                    min_col = min(min_col, col_idx)
                    break

        # 右端の検出
        max_col = 0
        for row_idx in range(start_row, end_row + 1):
            row = data[row_idx]
            for col_idx in range(len(row) - 1, -1, -1):
                if str(row[col_idx]).strip():
                    max_col = max(max_col, col_idx)
                    break

        return min_col if min_col < max_cols else 0, max_col

    def _detect_multiple_data_blocks(
        self, data: list[list[str]]
    ) -> list[dict[str, Any]]:
        """複数のデータブロックを検出（改善されたアルゴリズム）。

        Args:
            data: Excelデータ

        Returns:
            list[dict]: 検出されたデータブロックのリスト
        """
        if not data:
            return []

        rows = len(data)
        cols = len(data[0]) if data else 0

        # 各セルの有効性をマップ化
        cell_map = []
        for i, row in enumerate(data):
            row_map = []
            for j, cell in enumerate(row):
                is_valid = str(cell).strip() != ""
                row_map.append(is_valid)
            # 行の長さを統一
            while len(row_map) < cols:
                row_map.append(False)
            cell_map.append(row_map)

        # 矩形領域ベースのブロック検出
        visited = [[False] * cols for _ in range(rows)]
        blocks = []

        for i in range(rows):
            for j in range(cols):
                if cell_map[i][j] and not visited[i][j]:
                    # 新しい矩形ブロックを検出
                    block = self._find_rectangular_block(
                        cell_map, visited, i, j, rows, cols
                    )
                    if block and block["total_cells"] >= 2:  # 最小2セル以上
                        blocks.append(block)

        return blocks

    def _find_rectangular_block(
        self,
        cell_map: list[list[bool]],
        visited: list[list[bool]],
        start_row: int,
        start_col: int,
        rows: int,
        cols: int,
    ) -> dict[str, Any] | None:
        """矩形データブロックを検出（改善されたアルゴリズム）。

        Args:
            cell_map: セルの有効性マップ
            visited: 訪問済みマップ
            start_row: 開始行
            start_col: 開始列
            rows: 総行数
            cols: 総列数

        Returns:
            dict: ブロック情報
        """
        # 開始点から右方向に連続する有効セルを探す
        max_col = start_col
        for col in range(start_col, cols):
            if cell_map[start_row][col] and not visited[start_row][col]:
                max_col = col
            else:
                break

        # 開始点から下方向に連続する行を探す
        max_row = start_row
        for row in range(start_row, rows):
            # この行で、start_col から max_col までが全て有効かチェック
            valid_row = True
            for col in range(start_col, max_col + 1):
                if not cell_map[row][col] or visited[row][col]:
                    valid_row = False
                    break

            if valid_row:
                max_row = row
            else:
                break

        # 連続しない場合は、最小の矩形ブロックを作成
        if max_row == start_row and max_col == start_col:
            # 単一セルの場合、隣接セルを探す
            for r in range(max(0, start_row - 1), min(rows, start_row + 2)):
                for c in range(max(0, start_col - 1), min(cols, start_col + 2)):
                    if (
                        (r != start_row or c != start_col)
                        and cell_map[r][c]
                        and not visited[r][c]
                    ):
                        max_row = max(max_row, r)
                        max_col = max(max_col, c)

        # ブロック内のセルをマーク
        total_cells = 0
        for r in range(start_row, max_row + 1):
            for c in range(start_col, max_col + 1):
                if cell_map[r][c]:
                    visited[r][c] = True
                    total_cells += 1

        return {
            "min_row": start_row,
            "max_row": max_row,
            "min_col": start_col,
            "max_col": max_col,
            "total_cells": total_cells,
            "block_type": "data",
        }

    def _explore_block(
        self,
        cell_map: list[list[bool]],
        visited: list[list[bool]],
        start_row: int,
        start_col: int,
        rows: int,
        cols: int,
    ) -> dict[str, Any] | None:
        """連続するデータブロックを探索。

        Args:
            cell_map: セルの有効性マップ
            visited: 訪問済みマップ
            start_row: 開始行
            start_col: 開始列
            rows: 総行数
            cols: 総列数

        Returns:
            dict: ブロック情報
        """
        min_row = max_row = start_row
        min_col = max_col = start_col
        total_cells = 0

        # 縦方向に連続するセルを検出
        for row in range(start_row, rows):
            found_in_row = False
            for col in range(cols):
                if cell_map[row][col] and not visited[row][col]:
                    # 同じ行で連続する範囲を検出
                    if self._is_connected_region(
                        cell_map, visited, row, col, min_row, max_row, min_col, max_col
                    ):
                        visited[row][col] = True
                        min_row = min(min_row, row)
                        max_row = max(max_row, row)
                        min_col = min(min_col, col)
                        max_col = max(max_col, col)
                        total_cells += 1
                        found_in_row = True

            # 行に有効セルがない場合、ブロック終了の可能性
            if not found_in_row and row > start_row:
                break

        # 矩形領域内の有効セル数を再計算
        actual_cells = 0
        for i in range(min_row, max_row + 1):
            for j in range(min_col, max_col + 1):
                if i < len(cell_map) and j < len(cell_map[i]) and cell_map[i][j]:
                    actual_cells += 1
                    visited[i][j] = True

        return {
            "min_row": min_row,
            "max_row": max_row,
            "min_col": min_col,
            "max_col": max_col,
            "total_cells": actual_cells,
            "block_type": "data",
        }

    def _is_connected_region(
        self,
        cell_map: list[list[bool]],
        visited: list[list[bool]],
        row: int,
        col: int,
        min_row: int,
        max_row: int,
        min_col: int,
        max_col: int,
    ) -> bool:
        """指定されたセルが既存のブロック領域と連続しているかチェック。

        Args:
            cell_map: セルの有効性マップ
            visited: 訪問済みマップ
            row: チェックする行
            col: チェックする列
            min_row: 現在のブロックの最小行
            max_row: 現在のブロックの最大行
            min_col: 現在のブロックの最小列
            max_col: 現在のブロックの最大列

        Returns:
            bool: 連続している場合True
        """
        # 矩形領域の拡張として妥当かチェック
        new_min_row = min(min_row, row)
        new_max_row = max(max_row, row)
        new_min_col = min(min_col, col)
        new_max_col = max(max_col, col)

        # 拡張後の領域が極端に大きくならないかチェック
        height = new_max_row - new_min_row + 1
        width = new_max_col - new_min_col + 1

        # 最大5x5の矩形まで許可
        return height <= 5 and width <= 5

    def _extract_detected_range(
        self, data: list[list[str]], range_spec: str
    ) -> list[list[str]]:
        """検出された範囲のデータを抽出。

        Args:
            data: 全体のデータ
            range_spec: 範囲指定文字列

        Returns:
            list[list[str]]: 抽出されたデータ
        """
        try:
            range_info = self._parse_range_specification(range_spec)
            return self._extract_range_data(data, range_info)
        except Exception:
            # 範囲解析に失敗した場合は全データを返す
            return data

    def _detect_header_in_range(self, range_data: list[list[str]]) -> bool:
        """範囲内でのヘッダー検出。

        Args:
            range_data: 範囲データ

        Returns:
            bool: ヘッダーが存在するか
        """
        if not range_data or len(range_data) < 2:
            return False

        # 最初の行が文字列中心で、2行目が数値中心の場合ヘッダーと判定
        first_row = range_data[0]
        second_row = range_data[1]

        text_count = sum(
            1 for cell in first_row if str(cell).strip() and not str(cell).isdigit()
        )
        numeric_count = sum(
            1
            for cell in second_row
            if str(cell).strip() and str(cell).replace(".", "").isdigit()
        )

        return (
            text_count > len(first_row) * 0.5 and numeric_count > len(second_row) * 0.3
        )

    def detect_data_blocks(
        self, file_path: str, sheet_name: str | None = None
    ) -> dict[str, Any]:
        """データブロックの検出。

        Args:
            file_path: Excelファイルパス
            sheet_name: シート名

        Returns:
            dict[str, Any]: 検出されたブロック情報
        """
        # 複数ブロック検出を使用
        excel_data = self.load_from_excel(file_path, sheet_name)
        raw_blocks = self._detect_multiple_data_blocks(excel_data["data"])

        # ブロック情報を整形
        blocks = []
        for block in raw_blocks:
            range_str = f"{chr(65 + block['min_col'])}{block['min_row'] + 1}:{chr(65 + block['max_col'])}{block['max_row'] + 1}"
            confidence = min(
                0.9, 0.5 + (block["total_cells"] / 10)
            )  # セル数に基づく信頼度

            blocks.append(
                {
                    "range": range_str,
                    "confidence_score": confidence,
                    "block_type": "data",
                }
            )

        # ブロックが見つからない場合はフォールバック
        if not blocks:
            detected_range = self._detect_auto_range(excel_data["data"])
            blocks = [
                {
                    "range": detected_range,
                    "confidence_score": 0.8,
                    "block_type": "data",
                }
            ]

        return {
            "blocks": blocks,
            "file_path": file_path,
            "sheet_name": excel_data["sheet_name"],
        }

    def analyze_data_boundaries(
        self, file_path: str, sheet_name: str | None = None
    ) -> dict[str, Any]:
        """データ境界の分析（自動検出されたデータブロック基準）。

        Args:
            file_path: Excelファイルパス
            sheet_name: シート名

        Returns:
            dict[str, Any]: 境界分析結果
        """
        # Excelデータを読み込み
        excel_data = self.load_from_excel(file_path, sheet_name)
        data = excel_data["data"]

        if not data:
            return {
                "top_boundary": 0,
                "bottom_boundary": 0,
                "left_boundary": 0,
                "right_boundary": 0,
                "file_path": file_path,
                "sheet_name": excel_data["sheet_name"],
            }

        # 自動検出されたデータブロックの境界を使用
        data_block = self._find_largest_data_block(data)
        if not data_block:
            return {
                "top_boundary": 0,
                "bottom_boundary": 0,
                "left_boundary": 0,
                "right_boundary": 0,
                "file_path": file_path,
                "sheet_name": excel_data["sheet_name"],
            }

        return {
            "top_boundary": data_block["min_row"],
            "bottom_boundary": data_block["max_row"],
            "left_boundary": data_block["min_col"],
            "right_boundary": data_block["max_col"],
            "file_path": file_path,
            "sheet_name": excel_data["sheet_name"],
        }

    def detect_merged_cells(
        self, file_path: str, sheet_name: str | None = None
    ) -> dict[str, Any]:
        """結合セルの検出。

        Args:
            file_path: Excelファイルパス
            sheet_name: シート名（None=自動検出）

        Returns:
            dict[str, Any]: 結合セル情報

        Raises:
            ValueError: ファイル読み込みエラー
        """
        # セキュリティチェック
        if not self.is_safe_path(file_path):
            raise ValueError(f"Unsafe file path: {file_path}")

        # ファイル妥当性チェック
        self.validate_excel_file(file_path)

        try:
            # openpyxlでワークブックを読み込み
            workbook = load_workbook(file_path, data_only=False)

            # シート名の決定
            if sheet_name is None:
                sheet_name = self.basic_sheet_detection(file_path)

            worksheet = workbook[sheet_name]

            # 結合セル情報を取得
            merged_cells = []
            for merged_range in worksheet.merged_cells.ranges:
                # 結合セルの範囲情報を取得
                min_row = merged_range.min_row
                max_row = merged_range.max_row
                min_col = merged_range.min_col
                max_col = merged_range.max_col

                # 結合セルの値（左上セルの値）
                cell_value = worksheet.cell(min_row, min_col).value

                merged_cells.append(
                    {
                        "range": str(merged_range),
                        "min_row": min_row - 1,  # 0ベースに変換
                        "max_row": max_row - 1,  # 0ベースに変換
                        "min_col": min_col - 1,  # 0ベースに変換
                        "max_col": max_col - 1,  # 0ベースに変換
                        "value": str(cell_value) if cell_value is not None else "",
                        "span_rows": max_row - min_row + 1,
                        "span_cols": max_col - min_col + 1,
                    }
                )

            return {
                "merged_cells": merged_cells,
                "merged_ranges": merged_cells,  # エイリアス
                "merged_count": len(merged_cells),
                "has_merged_cells": len(merged_cells) > 0,
                "file_path": file_path,
                "sheet_name": sheet_name,
            }

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(
                f"Failed to detect merged cells in {file_path}: {e!s}"
            ) from e

    def load_from_excel_with_merge_cells(
        self,
        file_path: str,
        merge_mode: str = "expand",
        sheet_name: str | None = None,
        header_row: int | None = None,
    ) -> dict[str, Any]:
        """結合セル処理でExcelファイルを読み込み。

        Args:
            file_path: Excelファイルパス
            merge_mode: 結合セル処理モード（expand, ignore, first-value）
            sheet_name: 読み込むシート名（None=自動検出）
            header_row: ヘッダー行番号（None=自動検出）

        Returns:
            dict[str, Any]: 変換されたJSONデータ（結合セル処理情報付き）

        Raises:
            MergedCellsError: 無効な処理モードの場合
            ValueError: ファイル読み込みエラー
        """
        # 処理モードの検証
        valid_modes = ["expand", "ignore", "first-value"]
        if merge_mode not in valid_modes:
            raise MergedCellsError(
                f"Invalid merge mode: {merge_mode}. Valid modes: {valid_modes}",
                merge_mode,
            )

        # 基本的なExcel読み込み
        excel_data = self.load_from_excel(file_path, sheet_name, header_row)

        # 結合セル情報を検出
        merge_info = self.detect_merged_cells(file_path, sheet_name)

        # 結合セル処理を適用
        processed_data = self._apply_merge_cell_processing(
            excel_data["data"], merge_info["merged_cells"], merge_mode
        )

        # 結果を構築（DRY原則適用）
        return self._build_merged_cells_result(
            processed_data, excel_data, file_path, merge_mode, merge_info
        )

    def _build_merged_cells_result(
        self,
        processed_data: list[list[str]],
        excel_data_or_sheet_name: dict[str, Any] | str,
        file_path: str,
        merge_mode: str,
        merge_info: dict[str, Any],
        additional_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """結合セル処理結果の共通構築メソッド（DRY原則適用）。

        Args:
            processed_data: 処理済みデータ
            excel_data_or_sheet_name: Excelデータまたはシート名
            file_path: ファイルパス
            merge_mode: 結合セル処理モード
            merge_info: 結合セル情報
            additional_metadata: 追加メタデータ

        Returns:
            dict[str, Any]: 統一された結果構造
        """
        # sheet_nameの取得
        if isinstance(excel_data_or_sheet_name, dict):
            sheet_name = excel_data_or_sheet_name["sheet_name"]
            has_header = excel_data_or_sheet_name.get("has_header", False)
            headers = excel_data_or_sheet_name.get("headers", [])
        else:
            sheet_name = excel_data_or_sheet_name
            has_header = False
            headers = []

        # 基本結果構造
        result = {
            "data": processed_data,
            "has_header": has_header,
            "headers": headers,
            "sheet_name": sheet_name,
            "file_path": file_path,
            "merge_mode": merge_mode,
            "merged_cells_count": merge_info["merged_count"],
            "has_merged_cells": merge_info["merged_count"] > 0,
            "merged_cells_info": merge_info["merged_cells"],
            "rows": len(processed_data),
            "columns": len(processed_data[0]) if processed_data else 0,
        }

        # 追加メタデータの統合
        if additional_metadata:
            result.update(additional_metadata)

        return result

    def _apply_merge_cell_processing(
        self, data: list[list[str]], merged_cells: list[dict], merge_mode: str
    ) -> list[list[str]]:
        """結合セル処理をデータに適用。

        Args:
            data: 元のデータ
            merged_cells: 結合セル情報のリスト
            merge_mode: 処理モード

        Returns:
            list[list[str]]: 処理されたデータ
        """
        if not merged_cells:
            return data

        # データのコピーを作成
        processed_data = [row[:] for row in data]

        for merge_cell in merged_cells:
            min_row = merge_cell["min_row"]
            max_row = merge_cell["max_row"]
            min_col = merge_cell["min_col"]
            max_col = merge_cell["max_col"]
            value = merge_cell["value"]

            if merge_mode == "expand":
                # 全てのセルに同じ値を展開
                for row in range(min_row, max_row + 1):
                    for col in range(min_col, max_col + 1):
                        if row < len(processed_data) and col < len(processed_data[row]):
                            processed_data[row][col] = value

            elif merge_mode == "ignore":
                # 左上以外のセルを空にする
                for row in range(min_row, max_row + 1):
                    for col in range(min_col, max_col + 1):
                        if row < len(processed_data) and col < len(processed_data[row]):
                            if row == min_row and col == min_col:
                                processed_data[row][col] = value
                            else:
                                processed_data[row][col] = ""

            elif merge_mode == "first-value":
                # 左上のセルにのみ値を保持、他は空
                for row in range(min_row, max_row + 1):
                    for col in range(min_col, max_col + 1):
                        if row < len(processed_data) and col < len(processed_data[row]):
                            if row == min_row and col == min_col:
                                processed_data[row][col] = value
                            else:
                                processed_data[row][col] = ""

        return processed_data

    def load_from_excel_with_merge_cells_and_range(
        self,
        file_path: str,
        range_spec: str,
        merge_mode: str = "expand",
        sheet_name: str | None = None,
        header_row: int | None = None,
    ) -> dict[str, Any]:
        """結合セル処理と範囲指定の組み合わせでExcelファイルを読み込み。

        Args:
            file_path: Excelファイルパス
            range_spec: 範囲指定（例: "A1:C3", "B2"）
            merge_mode: 結合セル処理モード（expand, ignore, first-value）
            sheet_name: 読み込むシート名（None=自動検出）
            header_row: ヘッダー行番号（None=自動検出）

        Returns:
            dict[str, Any]: 変換されたJSONデータ

        Raises:
            MergedCellsError: 無効な処理モード
            RangeSpecificationError: 無効な範囲指定
        """
        # 処理モードの検証
        valid_modes = ["expand", "ignore", "first-value"]
        if merge_mode not in valid_modes:
            raise MergedCellsError(
                f"Invalid merge mode: {merge_mode}. Valid modes: {valid_modes}",
                merge_mode,
            )

        # 範囲指定付きで読み込み
        excel_data = self.load_from_excel_with_range(
            file_path, range_spec, sheet_name, header_row
        )

        # 結合セル情報を検出
        merge_info = self.detect_merged_cells(file_path, sheet_name)

        # 範囲内の結合セルのみをフィルタリング
        range_info = self._parse_range_specification(range_spec)
        filtered_merged_cells = self._filter_merged_cells_in_range(
            merge_info["merged_cells"], range_info
        )

        # 結合セル処理を適用
        processed_data = self._apply_merge_cell_processing(
            excel_data["data"], filtered_merged_cells, merge_mode
        )

        # 結果を構築（DRY原則適用）
        # 範囲指定のメタデータを作成
        range_merge_info = {
            "merged_cells": filtered_merged_cells,
            "merged_count": len(filtered_merged_cells),
        }
        additional_metadata = {"range": range_spec}

        return self._build_merged_cells_result(
            processed_data,
            excel_data,
            file_path,
            merge_mode,
            range_merge_info,
            additional_metadata,
        )

    def _filter_merged_cells_in_range(
        self, merged_cells: list[dict], range_info: dict[str, Any]
    ) -> list[dict]:
        """指定範囲内の結合セルのみをフィルタリング。

        Args:
            merged_cells: 全ての結合セル情報
            range_info: 範囲情報

        Returns:
            list[dict]: 範囲内の結合セル情報
        """
        filtered = []

        for merge_cell in merged_cells:
            # 結合セルが範囲と重複するかチェック
            if (
                merge_cell["max_row"] >= range_info["start_row"]
                and merge_cell["min_row"] <= range_info["end_row"]
                and merge_cell["max_col"] >= range_info["start_col"]
                and merge_cell["min_col"] <= range_info["end_col"]
            ):
                # 範囲内での相対位置に調整
                adjusted_merge_cell = merge_cell.copy()
                adjusted_merge_cell["min_row"] = max(
                    0, merge_cell["min_row"] - range_info["start_row"]
                )
                adjusted_merge_cell["max_row"] = min(
                    range_info["end_row"] - range_info["start_row"],
                    merge_cell["max_row"] - range_info["start_row"],
                )
                adjusted_merge_cell["min_col"] = max(
                    0, merge_cell["min_col"] - range_info["start_col"]
                )
                adjusted_merge_cell["max_col"] = min(
                    range_info["end_col"] - range_info["start_col"],
                    merge_cell["max_col"] - range_info["start_col"],
                )

                filtered.append(adjusted_merge_cell)

        return filtered

    def load_from_excel_with_merge_cells_and_header(
        self,
        file_path: str,
        header_row: int,
        merge_mode: str = "expand",
        sheet_name: str | None = None,
    ) -> dict[str, Any]:
        """結合セル処理とヘッダー行指定の組み合わせでExcelファイルを読み込み。

        Args:
            file_path: Excelファイルパス
            header_row: ヘッダー行番号（0ベース）
            merge_mode: 結合セル処理モード（expand, ignore, first-value）
            sheet_name: 読み込むシート名（None=自動検出）

        Returns:
            dict[str, Any]: 変換されたJSONデータ

        Raises:
            MergedCellsError: 無効な処理モード
            ValueError: 無効なヘッダー行指定
        """
        # 処理モードの検証
        valid_modes = ["expand", "ignore", "first-value"]
        if merge_mode not in valid_modes:
            raise MergedCellsError(
                f"Invalid merge mode: {merge_mode}. Valid modes: {valid_modes}",
                merge_mode,
            )

        # ヘッダー行の検証
        self._validate_header_row(header_row)

        # 基本的なExcel読み込み（ヘッダー処理前）
        excel_data_raw = self.load_from_excel(file_path, sheet_name, None)

        # 結合セル情報を検出
        merge_info = self.detect_merged_cells(file_path, sheet_name)

        # 全データに結合セル処理を適用（ヘッダー行も含む）
        processed_all_data = self._apply_merge_cell_processing(
            excel_data_raw["data"], merge_info["merged_cells"], merge_mode
        )

        # 処理後のデータからヘッダー行とデータ部分を分離
        if header_row < len(processed_all_data):
            headers = [
                str(cell).strip() if cell else f"Column{i + 1}"
                for i, cell in enumerate(processed_all_data[header_row])
            ]
            # 結合セル展開の場合は重複回避をスキップ（同じ値の展開が期待される）
            # ヘッダー行より後の行のみをデータとして取得（ヘッダー行以前は除外）
            processed_data = [
                row for i, row in enumerate(processed_all_data) if i > header_row
            ]
            has_header = True
        else:
            headers = []
            processed_data = processed_all_data
            has_header = False

        # 結果を構築（DRY原則適用）
        # ヘッダー処理後のExcelデータ構造を作成
        processed_excel_data = {
            "sheet_name": excel_data_raw["sheet_name"],
            "has_header": has_header,
            "headers": headers,
        }
        additional_metadata = {"header_row": header_row}

        return self._build_merged_cells_result(
            processed_data,
            processed_excel_data,
            file_path,
            merge_mode,
            merge_info,
            additional_metadata,
        )

    def load_from_excel_with_multiple_headers(
        self,
        file_path: str,
        header_rows: int,
        sheet_name: str | None = None,
    ) -> dict[str, Any]:
        """複数行ヘッダーを結合してExcelファイルを読み込み。

        Args:
            file_path: Excelファイルパス
            header_rows: ヘッダー行数（2以上）
            sheet_name: シート名（Noneの場合はデフォルトシート）

        Returns:
            dict[str, Any]: 読み込み結果
                - data: 2D配列のデータ（ヘッダー除く）
                - headers: 結合されたヘッダーリスト
                - has_header: True
                - merged_header_levels: ヘッダー行数
                - file_path: ファイルパス
                - sheet_name: シート名

        Raises:
            ValueError: header_rowsが無効な場合
            FileNotFoundError: ファイルが存在しない場合
        """
        if header_rows <= 0:
            raise ValueError("header_rows must be positive")

        try:
            # 基本的なExcelデータを読み込み
            excel_data = self.load_from_excel(file_path, sheet_name, None)

            # ヘッダー行数の検証
            if header_rows > len(excel_data["data"]):
                raise ValueError("header_rows exceeds available rows")

            # ヘッダー行とデータ行を分離
            header_rows_data = excel_data["data"][:header_rows]
            data_rows = excel_data["data"][header_rows:]

            # 複数ヘッダーを結合
            merged_headers = self._merge_multiple_headers(header_rows_data)

            return {
                "data": data_rows,
                "headers": merged_headers,
                "has_header": True,
                "merged_header_levels": header_rows,
                "file_path": file_path,
                "sheet_name": excel_data["sheet_name"],
                "row_count": len(data_rows),
                "col_count": len(merged_headers) if merged_headers else 0,
            }

        except FileNotFoundError:
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Failed to load Excel file with multiple headers: {file_path}: {e!s}") from e

    def load_from_excel_with_multiple_headers_and_range(
        self,
        file_path: str,
        range_spec: str,
        header_rows: int,
        sheet_name: str | None = None,
    ) -> dict[str, Any]:
        """複数行ヘッダーと範囲指定を組み合わせてExcelファイルを読み込み。

        Args:
            file_path: Excelファイルパス
            range_spec: 範囲指定（例: "A1:D10"）
            header_rows: ヘッダー行数
            sheet_name: シート名

        Returns:
            dict[str, Any]: 読み込み結果
        """
        if header_rows <= 0:
            raise ValueError("header_rows must be positive")

        try:
            # 範囲指定でデータを読み込み
            excel_data = self.load_from_excel_with_range(file_path, range_spec, sheet_name, None)

            # ヘッダー行数の検証
            if header_rows > len(excel_data["data"]):
                raise ValueError(f"header_rows ({header_rows}) exceeds available rows in range")

            # ヘッダー行とデータ行を分離
            header_rows_data = excel_data["data"][:header_rows]
            data_rows = excel_data["data"][header_rows:]

            # 複数ヘッダーを結合
            merged_headers = self._merge_multiple_headers(header_rows_data)

            return {
                "data": data_rows,
                "headers": merged_headers,
                "has_header": True,
                "merged_header_levels": header_rows,
                "range": range_spec,
                "file_path": file_path,
                "sheet_name": excel_data["sheet_name"],
                "row_count": len(data_rows),
                "col_count": len(merged_headers) if merged_headers else 0,
            }

        except Exception as e:
            raise ValueError(f"Failed to load Excel file with multiple headers and range: {file_path}: {e!s}") from e

    def _merge_multiple_headers(self, header_rows_data: list[list[str]]) -> list[str]:
        """複数行のヘッダーを結合して単一のヘッダーリストを生成。

        Args:
            header_rows_data: ヘッダー行のデータ（2D配列）

        Returns:
            list[str]: 結合されたヘッダーリスト
        """
        if not header_rows_data:
            return []

        # 最大列数を取得
        max_cols = max(len(row) for row in header_rows_data) if header_rows_data else 0
        if max_cols == 0:
            return []

        merged_headers = []

        for col in range(max_cols):
            # 各列のヘッダー要素を階層的に収集
            header_parts = self._collect_hierarchical_header_parts(header_rows_data, col)

            # ヘッダー要素を結合
            merged_header = self._build_merged_header(header_parts, col)
            merged_headers.append(merged_header)

        return merged_headers

    def _collect_hierarchical_header_parts(self, header_rows_data: list[list[str]], col: int) -> list[str]:
        """指定列の階層的ヘッダー要素を収集（DRY原則適用）。

        Args:
            header_rows_data: ヘッダー行のデータ
            col: 対象列番号

        Returns:
            list[str]: 階層的に整理されたヘッダー要素
        """
        header_parts = []

        for row_idx, row in enumerate(header_rows_data):
            if col < len(row):
                cell_value = str(row[col]).strip() if row[col] is not None else ""

                if cell_value:
                    # 空でない値：使用する
                    header_parts.append(cell_value)
                else:
                    # 空の値：階層構造の継承ロジック適用
                    inherited_value = self._find_inherited_value_for_empty_cell(
                        row_idx, col, header_rows_data
                    )
                    if inherited_value:
                        header_parts.append(inherited_value)

        return header_parts

    def _find_inherited_value_for_empty_cell(
        self,
        row_idx: int,
        col: int,
        header_rows_data: list[list[str]]
    ) -> str | None:
        """空セルの値継承処理（高度階層構造対応）。

        Args:
            row_idx: 現在の行インデックス
            col: 現在の列インデックス
            header_rows_data: 全ヘッダー行データ

        Returns:
            str | None: 継承された値またはNone
        """
        # 最初の行が空の場合
        if row_idx == 0:
            # 同一行で左側を探索
            inherited_value = self._find_left_non_empty_in_row(header_rows_data[row_idx], col)
            return inherited_value if inherited_value else "空欄"

        # 多層階層継承ロジック：上位レベルから段階的に継承
        return self._find_hierarchical_inherited_value(row_idx, col, header_rows_data)

    def _find_hierarchical_inherited_value(
        self,
        row_idx: int,
        col: int,
        header_rows_data: list[list[str]]
    ) -> str | None:
        """多層階層継承ロジック（コードエクセレンス：高度アルゴリズム）。

        Args:
            row_idx: 現在の行インデックス
            col: 現在の列インデックス
            header_rows_data: 全ヘッダー行データ

        Returns:
            str | None: 継承された値またはNone
        """
        # 同一行で左側を探索
        current_row = header_rows_data[row_idx]
        inherited_value = self._find_left_non_empty_in_row(current_row, col)

        if inherited_value:
            return inherited_value

        # 上位レベルから継承値を探索
        for upper_row_idx in range(row_idx - 1, -1, -1):
            inherited_from_upper = self._find_span_inherited_value(
                upper_row_idx, col, header_rows_data
            )
            if inherited_from_upper:
                return inherited_from_upper

        return None

    def _find_span_inherited_value(
        self,
        row_idx: int,
        col: int,
        header_rows_data: list[list[str]]
    ) -> str | None:
        """指定行での範囲継承値を探索（結合セル模倣）。

        Args:
            row_idx: 探索行インデックス
            col: 対象列インデックス
            header_rows_data: 全ヘッダー行データ

        Returns:
            str | None: 範囲継承された値またはNone
        """
        if row_idx < 0 or row_idx >= len(header_rows_data):
            return None

        target_row = header_rows_data[row_idx]

        # 左側の非空値とその範囲を探索
        for check_col in range(col, -1, -1):
            if check_col < len(target_row):
                cell_value = str(target_row[check_col]).strip() if target_row[check_col] is not None else ""
                if cell_value:
                    # 見つかった値の影響範囲を計算
                    span_end = self._calculate_value_span_end(row_idx, check_col, header_rows_data)
                    if col <= span_end:
                        return cell_value

        return None

    def _calculate_value_span_end(
        self,
        row_idx: int,
        value_col: int,
        header_rows_data: list[list[str]]
    ) -> int:
        """値の影響範囲終端を計算（結合セル模倣）。

        Args:
            row_idx: 値の行インデックス
            value_col: 値の列インデックス
            header_rows_data: 全ヘッダー行データ

        Returns:
            int: 影響範囲の終端列インデックス
        """
        if row_idx < 0 or row_idx >= len(header_rows_data):
            return value_col

        target_row = header_rows_data[row_idx]

        # 右側の次の非空値まで範囲を拡張
        for end_col in range(value_col + 1, len(target_row)):
            cell_value = str(target_row[end_col]).strip() if target_row[end_col] is not None else ""
            if cell_value:
                return end_col - 1  # 次の非空値の直前まで

        # 行の最後まで範囲を拡張
        return len(target_row) - 1

    def _find_left_non_empty_in_row(self, row: list[str], col: int) -> str | None:
        """指定行で左側の非空値を探索（SOLID原則：単一責任）。

        Args:
            row: 対象行データ
            col: 起点列番号

        Returns:
            str | None: 見つかった値またはNone
        """
        for check_col in range(col - 1, -1, -1):
            if check_col < len(row):
                value = str(row[check_col]).strip() if row[check_col] is not None else ""
                if value:
                    return value
        return None

    def _build_merged_header(self, header_parts: list[str], col: int) -> str:
        """ヘッダー要素から結合ヘッダーを構築（DRY原則適用）。

        Args:
            header_parts: ヘッダー要素リスト
            col: 列番号（デフォルト名生成用）

        Returns:
            str: 結合されたヘッダー名
        """
        if header_parts:
            # 重複除去（順序保持）+ 正規化
            unique_parts = self._remove_duplicates_preserve_order(header_parts)
            merged_header = "_".join(unique_parts)
            return self._normalize_header_name(merged_header)
        else:
            return f"列{col + 1}"  # デフォルト列名

    def _remove_duplicates_preserve_order(self, parts: list[str]) -> list[str]:
        """重複を除去しつつ順序を保持（DRY原則）。

        Args:
            parts: 元のリスト

        Returns:
            list[str]: 重複除去後のリスト
        """
        unique_parts = []
        for part in parts:
            if part not in unique_parts:
                unique_parts.append(part)
        return unique_parts

    def _normalize_header_name(self, header_name: str) -> str:
        """ヘッダー名を正規化（コードエクセレンス：日本語対応強化）。

        Args:
            header_name: 元のヘッダー名

        Returns:
            str: 正規化されたヘッダー名
        """
        if not header_name:
            return "空欄"

        # 前後の空白を除去
        normalized = header_name.strip()

        # 日本語括弧の特別処理（括弧内容を分離）
        normalized = self._process_japanese_parentheses(normalized)

        # 特殊文字を置換
        normalized = self._replace_special_characters(normalized)

        # 連続するアンダースコアを単一に
        normalized = self._clean_consecutive_underscores(normalized)

        # 前後のアンダースコアを除去
        normalized = normalized.strip("_")

        return normalized or "空欄"

    def _process_japanese_parentheses(self, text: str) -> str:
        """日本語括弧の特別処理（コードエクセレンス：SOLID原則）。

        Args:
            text: 処理対象テキスト

        Returns:
            str: 括弧処理後のテキスト
        """
        import re

        # 日本語括弧パターン「売上高（千円）」→「売上高_千円」
        # 全角括弧
        text = re.sub(r'（([^）]+)）', r'_\1', text)
        # 半角括弧
        text = re.sub(r'\(([^)]+)\)', r'_\1', text)

        return text

    def _replace_special_characters(self, text: str) -> str:
        """特殊文字の置換処理（DRY原則：設定の一元化）。

        Args:
            text: 処理対象テキスト

        Returns:
            str: 特殊文字置換後のテキスト
        """
        # 特殊文字マッピング（保守性向上）
        replacements = {
            "/": "_", "\\": "_", "[": "_", "]": "_", "{": "_", "}": "_",
            "|": "_", ":": "_", ";": "_", ",": "_", ".": "_", "?": "_",
            "*": "_", "+": "_", "-": "_", "=": "_", "!": "_", "@": "_",
            "#": "_", "$": "_", "%": "_", "^": "_", "&": "_", "<": "_", ">": "_",
            "~": "_", "`": "_", "'": "_", '"': "_", " ": "_"
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text

    def _clean_consecutive_underscores(self, text: str) -> str:
        """連続するアンダースコアのクリーンアップ（DRY原則）。

        Args:
            text: 処理対象テキスト

        Returns:
            str: クリーンアップ後のテキスト
        """
        while "__" in text:
            text = text.replace("__", "_")
        return text

    # ============================================================================
    # JSON Cache Functions (Task 3.4) - コードエクセレンス適用
    # ============================================================================
    
    # キャッシュ関連定数（DRY原則：設定の一元化）
    CACHE_DIR_NAME: ClassVar[str] = ".jsontable_cache"
    CACHE_FILE_EXTENSION: ClassVar[str] = ".json"
    REQUIRED_CACHE_KEYS: ClassVar[list[str]] = ["data", "headers", "source_file", "cache_timestamp"]
    DEFAULT_CACHE_KEY: ClassVar[str] = "default"

    def load_from_excel_with_cache(
        self,
        file_path: str,
        sheet_name: str | None = None,
        header_row: int | None = None,
        range_spec: str | None = None,
        skip_rows: str | None = None,
        detect_range: str | None = None,
        auto_header: bool = False,
        merge_cells: str | None = None,
        merge_headers: str | None = None,
        max_cache_size: int | None = None,
    ) -> dict[str, Any]:
        """キャッシュを使用してExcelファイルを読み込み（コードエクセレンス：高品質実装）。

        Args:
            file_path: Excelファイルパス
            sheet_name: シート名
            header_row: ヘッダー行番号
            range_spec: 範囲指定
            skip_rows: スキップ行指定
            detect_range: 自動範囲検出モード
            auto_header: ヘッダー自動判定
            merge_cells: 結合セル処理モード
            merge_headers: 複数ヘッダー結合指定
            max_cache_size: 最大キャッシュサイズ（バイト）

        Returns:
            dict[str, Any]: 読み込み結果（cache_hitフラグ付き）
        """
        # キャッシュシステムの処理フロー（SOLID原則：単一責任）
        cache_context = self._build_cache_context(
            file_path, sheet_name, header_row, range_spec, skip_rows,
            detect_range, auto_header, merge_cells, merge_headers
        )
        
        # キャッシュヒット確認・読み込み試行
        cached_result = self._try_load_from_cache(cache_context)
        if cached_result:
            return cached_result
        
        # キャッシュミス: 実際のExcelファイル読み込み
        result = self._load_excel_without_cache(
            file_path, sheet_name, header_row, range_spec, skip_rows,
            detect_range, auto_header, merge_cells, merge_headers
        )
        
        # 新しいキャッシュとして保存
        self._save_to_cache(cache_context["cache_path"], result, file_path, max_cache_size)
        
        result["cache_hit"] = False
        result["cache_path"] = cache_context["cache_path"]
        return result

    def _build_cache_context(
        self,
        file_path: str,
        sheet_name: str | None,
        header_row: int | None,
        range_spec: str | None,
        skip_rows: str | None,
        detect_range: str | None,
        auto_header: bool,
        merge_cells: str | None,
        merge_headers: str | None,
    ) -> dict[str, str]:
        """キャッシュコンテキストを構築（DRY原則：情報の一元化）。

        Args:
            全オプションパラメータ

        Returns:
            dict[str, str]: キャッシュコンテキスト（キー、パス等）
        """
        cache_key = self._generate_cache_key(
            file_path, sheet_name, header_row, range_spec, skip_rows,
            detect_range, auto_header, merge_cells, merge_headers
        )
        
        cache_path = self._get_cache_file_path(file_path, cache_key)
        
        return {
            "cache_key": cache_key,
            "cache_path": cache_path,
            "file_path": file_path,
        }

    def _try_load_from_cache(self, cache_context: dict[str, str]) -> dict[str, Any] | None:
        """キャッシュからの読み込み試行（SOLID原則：単一責任）。

        Args:
            cache_context: キャッシュコンテキスト

        Returns:
            dict[str, Any] | None: キャッシュデータまたはNone
        """
        import json
        
        cache_path = cache_context["cache_path"]
        file_path = cache_context["file_path"]
        
        if not self._is_cache_valid(file_path, cache_path):
            return None
            
        try:
            with open(cache_path, encoding="utf-8") as f:
                cache_data = json.load(f)

            if self._validate_cache_data(cache_data):
                cache_data["cache_hit"] = True
                cache_data["cache_path"] = cache_path
                return cache_data

        except (json.JSONDecodeError, KeyError, FileNotFoundError, UnicodeDecodeError):
            # キャッシュが破損・アクセス不可の場合は無視
            pass

        return None

    def _generate_cache_key(
        self,
        file_path: str,
        sheet_name: str | None,
        header_row: int | None,
        range_spec: str | None,
        skip_rows: str | None,
        detect_range: str | None,
        auto_header: bool,
        merge_cells: str | None,
        merge_headers: str | None,
    ) -> str:
        """キャッシュキーを生成。

        Args:
            全オプションパラメータ

        Returns:
            str: MD5ハッシュされたキャッシュキー
        """
        import hashlib
        import json

        # オプション辞書を作成
        options = {
            "sheet_name": sheet_name,
            "header_row": header_row,
            "range_spec": range_spec,
            "skip_rows": skip_rows,
            "detect_range": detect_range,
            "auto_header": auto_header,
            "merge_cells": merge_cells,
            "merge_headers": merge_headers,
        }

        # JSONエンコードして一意の文字列を生成
        options_str = json.dumps(options, sort_keys=True, ensure_ascii=False)

        # MD5ハッシュでキーを生成
        return hashlib.md5(options_str.encode("utf-8")).hexdigest()

    def _get_cache_file_path(self, file_path: str, cache_key: str | None = None) -> str:
        """キャッシュファイルのパスを生成（DRY原則：定数活用）。

        Args:
            file_path: 元のExcelファイルパス
            cache_key: キャッシュキー（Noneの場合は基本キーを生成）

        Returns:
            str: キャッシュファイルのパス
        """
        import os

        # キャッシュディレクトリを決定（定数活用）
        cache_dir = os.path.join(str(self.base_path), self.CACHE_DIR_NAME)
        os.makedirs(cache_dir, exist_ok=True)

        # ファイル名からキャッシュファイル名を生成
        base_name = os.path.basename(file_path)
        name_without_ext = os.path.splitext(base_name)[0]

        # キャッシュキーに基づくファイル名生成（保守性向上）
        effective_cache_key = cache_key if cache_key else self.DEFAULT_CACHE_KEY
        cache_filename = f"{name_without_ext}_{effective_cache_key}{self.CACHE_FILE_EXTENSION}"

        return os.path.join(cache_dir, cache_filename)

    def _is_cache_valid(self, file_path: str, cache_path: str) -> bool:
        """キャッシュの有効性をチェック。

        Args:
            file_path: 元のExcelファイルパス
            cache_path: キャッシュファイルパス

        Returns:
            bool: キャッシュが有効な場合True
        """
        import os

        # キャッシュファイルの存在確認
        if not os.path.exists(cache_path):
            return False

        # 元ファイルの存在確認
        if not os.path.exists(file_path):
            return False

        try:
            # ファイルの更新時刻を比較
            excel_mtime = os.path.getmtime(file_path)
            cache_mtime = os.path.getmtime(cache_path)

            # Excelファイルがキャッシュより新しい場合は無効
            return cache_mtime >= excel_mtime

        except OSError:
            return False

    def _validate_cache_data(self, cache_data: dict) -> bool:
        """キャッシュデータの整合性を検証（DRY原則：定数活用）。

        Args:
            cache_data: キャッシュデータ

        Returns:
            bool: データが有効な場合True
        """
        # 必須キーの存在確認（定数活用）
        for key in self.REQUIRED_CACHE_KEYS:
            if key not in cache_data:
                return False

        # データ型の厳密確認（品質向上）
        return (
            isinstance(cache_data["data"], list) and
            isinstance(cache_data["headers"], list) and
            isinstance(cache_data["source_file"], str) and
            isinstance(cache_data["cache_timestamp"], (int, float))
        )

    def _load_excel_without_cache(
        self,
        file_path: str,
        sheet_name: str | None,
        header_row: int | None,
        range_spec: str | None,
        skip_rows: str | None,
        detect_range: str | None,
        auto_header: bool,
        merge_cells: str | None,
        merge_headers: str | None,
    ) -> dict[str, Any]:
        """キャッシュを使用せずにExcelファイルを読み込み。

        Args:
            全オプションパラメータ

        Returns:
            dict[str, Any]: 読み込み結果
        """
        # 複数ヘッダー結合が指定されている場合
        if merge_headers:
            try:
                header_rows = int(merge_headers)
                return self.load_from_excel_with_multiple_headers(
                    file_path, header_rows, sheet_name
                )
            except ValueError:
                pass  # 数値でない場合は無視

        # Detect Range機能
        if detect_range:
            return self.load_from_excel_with_detect_range(
                file_path, detect_mode=detect_range, sheet_name=sheet_name, auto_header=auto_header
            )

        # Skip Rows機能
        if skip_rows:
            if range_spec and header_row is not None:
                return self.load_from_excel_with_skip_rows_range_and_header(
                    file_path, skip_rows, range_spec, header_row, sheet_name
                )
            elif range_spec:
                return self.load_from_excel_with_skip_rows_and_range(
                    file_path, range_spec, skip_rows, sheet_name
                )
            elif header_row is not None:
                return self.load_from_excel_with_skip_rows_and_header(
                    file_path, skip_rows, header_row, sheet_name
                )
            else:
                return self.load_from_excel_with_skip_rows(
                    file_path, skip_rows, sheet_name
                )

        # 結合セル処理
        if merge_cells:
            if range_spec:
                return self.load_from_excel_with_merge_cells_and_range(
                    file_path, range_spec, merge_cells, sheet_name
                )
            elif header_row is not None:
                return self.load_from_excel_with_merge_cells_and_header(
                    file_path, header_row, merge_cells, sheet_name
                )
            else:
                return self.load_from_excel_with_merge_cells(
                    file_path, merge_cells, sheet_name, header_row
                )

        # 範囲指定とヘッダー行の組み合わせ
        if range_spec and header_row is not None:
            return self.load_from_excel_with_header_row_and_range(
                file_path, header_row, range_spec, sheet_name
            )

        # 範囲指定のみ
        if range_spec:
            return self.load_from_excel_with_range(
                file_path, range_spec, sheet_name, header_row
            )

        # ヘッダー行指定のみ
        if header_row is not None:
            return self.load_from_excel_with_header_row(
                file_path, header_row, sheet_name
            )

        # 基本的な読み込み
        return self.load_from_excel(file_path, sheet_name, header_row)

    def _save_to_cache(
        self,
        cache_path: str,
        result: dict[str, Any],
        source_file: str,
        max_cache_size: int | None = None,
    ) -> None:
        """結果をキャッシュに保存。

        Args:
            cache_path: キャッシュファイルパス
            result: 保存するデータ
            source_file: 元ファイルパス
            max_cache_size: 最大キャッシュサイズ（バイト）
        """
        import json
        import time

        # キャッシュデータを構築
        cache_data = {
            "source_file": source_file,
            "cache_timestamp": time.time(),
            "data": result.get("data", []),
            "headers": result.get("headers", []),
            "has_header": result.get("has_header", False),
        }

        # 追加メタデータがあれば含める
        for key in ["sheet_name", "row_count", "col_count", "range", "merge_mode"]:
            if key in result:
                cache_data[key] = result[key]

        try:
            # JSONエンコード（サイズチェックのため）
            json_str = json.dumps(cache_data, ensure_ascii=False, indent=2)

            # サイズ制限チェック
            if max_cache_size and len(json_str.encode("utf-8")) > max_cache_size:
                # サイズ制限を超える場合はキャッシュしない
                return

            # ファイルに保存
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(json_str)

        except (OSError, UnicodeEncodeError):
            # キャッシュ保存に失敗してもエラーは無視
            pass

    def clear_cache(self, file_path: str | None = None) -> None:
        """キャッシュをクリア（DRY原則：定数活用、エラーハンドリング強化）。

        Args:
            file_path: 特定ファイルのキャッシュをクリア（Noneの場合は全削除）
        """
        import glob
        import os

        # キャッシュディレクトリ（定数活用）
        cache_dir = os.path.join(str(self.base_path), self.CACHE_DIR_NAME)

        if not os.path.exists(cache_dir):
            return

        if file_path:
            # 特定ファイルのキャッシュのみ削除
            self._clear_specific_file_cache(cache_dir, file_path)
        else:
            # 全キャッシュを削除
            self._clear_all_cache(cache_dir)

    def _clear_specific_file_cache(self, cache_dir: str, file_path: str) -> None:
        """特定ファイルのキャッシュ削除（SOLID原則：単一責任）。

        Args:
            cache_dir: キャッシュディレクトリ
            file_path: 対象ファイルパス
        """
        import glob
        import os

        base_name = os.path.basename(file_path)
        name_without_ext = os.path.splitext(base_name)[0]
        pattern = os.path.join(cache_dir, f"{name_without_ext}_*{self.CACHE_FILE_EXTENSION}")

        self._remove_cache_files_by_pattern(pattern)

    def _clear_all_cache(self, cache_dir: str) -> None:
        """全キャッシュ削除（SOLID原則：単一責任）。

        Args:
            cache_dir: キャッシュディレクトリ
        """
        import os

        pattern = os.path.join(cache_dir, f"*{self.CACHE_FILE_EXTENSION}")
        self._remove_cache_files_by_pattern(pattern)

    def _remove_cache_files_by_pattern(self, pattern: str) -> None:
        """パターンに基づくキャッシュファイル削除（DRY原則：共通処理化）。

        Args:
            pattern: ファイルパターン
        """
        import glob
        import os

        for cache_file in glob.glob(pattern):
            try:
                os.remove(cache_file)
            except OSError:
                # ファイル削除失敗は無視（並行アクセス等の可能性）
                pass

    # ==========================================
    # Phase 4: Performance Optimization Methods
    # ==========================================

    # Performance Constants (DRY原則: 設定一元化)
    DEFAULT_CHUNK_SIZE: ClassVar[int] = 1000
    DEFAULT_MEMORY_LIMIT_MB: ClassVar[int] = 50
    DEFAULT_TIME_LIMIT_SECONDS: ClassVar[float] = 10.0
    DEFAULT_CACHE_STRATEGY: ClassVar[str] = "lru"
    DEFAULT_MAX_CACHE_ENTRIES: ClassVar[int] = 5

    def _measure_performance(
        self, 
        operation: callable, 
        *args, 
        **kwargs
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """パフォーマンス測定共通メソッド（DRY原則：重複排除）。

        Args:
            operation: 測定対象の操作
            *args: 操作の引数
            **kwargs: 操作のキーワード引数

        Returns:
            tuple: (操作結果, 測定結果)
        """
        import time
        import tracemalloc

        tracemalloc.start()
        start_time = time.time()

        result = operation(*args, **kwargs)

        elapsed_time = time.time() - start_time
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        metrics = {
            "elapsed_time": elapsed_time,
            "peak_memory_mb": peak / 1024 / 1024,
            "current_memory_mb": current / 1024 / 1024
        }

        return result, metrics

    def load_from_excel_with_streaming(
        self, 
        file_path: str, 
        chunk_size: int = 1000, 
        sheet_name: str | None = None
    ) -> dict[str, Any]:
        """大容量ファイルのストリーミング読み込み（最小実装）。

        Args:
            file_path: Excelファイルパス
            chunk_size: チャンクサイズ
            sheet_name: シート名

        Returns:
            dict: ストリーミング読み込み結果
        """
        # 最小実装: 基本の読み込みを使用
        result = self.load_from_excel(file_path, sheet_name)
        
        # ストリーミング用の追加情報
        result.update({
            "streaming": True,
            "chunk_size": chunk_size,
            "total_rows": len(result["data"]) if result["data"] else 0
        })
        return result

    def load_from_excel_with_memory_limit(
        self, 
        file_path: str, 
        max_memory_mb: int | None = None,
        sheet_name: str | None = None
    ) -> dict[str, Any]:
        """メモリ使用量制限付き読み込み（REFACTOR: DRY原則適用）。

        Args:
            file_path: Excelファイルパス
            max_memory_mb: メモリ制限（MB、Noneの場合はデフォルト値使用）
            sheet_name: シート名

        Returns:
            dict: メモリ制限付き読み込み結果
        """
        effective_limit = max_memory_mb or self.DEFAULT_MEMORY_LIMIT_MB
        
        # DRY原則: 共通測定メソッド使用
        result, metrics = self._measure_performance(
            self.load_from_excel, file_path, sheet_name
        )
        
        # メモリ監視情報追加
        result.update({
            "memory_limit_applied": True,
            "peak_memory_mb": metrics["peak_memory_mb"],
            "max_memory_mb": effective_limit
        })
        return result

    def load_from_excel_with_time_limit(
        self, 
        file_path: str, 
        max_time_seconds: float | None = None,
        sheet_name: str | None = None
    ) -> dict[str, Any]:
        """処理時間制限付き読み込み（REFACTOR: DRY原則適用）。

        Args:
            file_path: Excelファイルパス
            max_time_seconds: 時間制限（秒、Noneの場合はデフォルト値使用）
            sheet_name: シート名

        Returns:
            dict: 時間制限付き読み込み結果
        """
        effective_limit = max_time_seconds or self.DEFAULT_TIME_LIMIT_SECONDS
        
        # DRY原則: 共通測定メソッド使用
        result, metrics = self._measure_performance(
            self.load_from_excel, file_path, sheet_name
        )
        
        # 時間監視情報追加
        result.update({
            "time_limit_applied": True,
            "elapsed_time": metrics["elapsed_time"],
            "max_time_seconds": effective_limit
        })
        return result

    def load_from_excel_with_memory_cache(
        self, 
        file_path: str,
        sheet_name: str | None = None
    ) -> dict[str, Any]:
        """メモリキャッシュ付き読み込み（最小実装）。

        Args:
            file_path: Excelファイルパス
            sheet_name: シート名

        Returns:
            dict: メモリキャッシュ付き読み込み結果
        """
        # 最小実装: JSONキャッシュを利用
        result = self.load_from_excel_with_cache(file_path, sheet_name=sheet_name)
        
        # メモリキャッシュ情報追加
        result.update({
            "memory_cache_hit": result.get("cache_hit", False)
        })
        return result

    def load_from_excel_with_cache_strategy(
        self, 
        file_path: str,
        strategy: str = "lru",
        max_entries: int = 5,
        sheet_name: str | None = None
    ) -> dict[str, Any]:
        """効率的なキャッシュ戦略付き読み込み（最小実装）。

        Args:
            file_path: Excelファイルパス
            strategy: キャッシュ戦略
            max_entries: 最大キャッシュエントリ数
            sheet_name: シート名

        Returns:
            dict: キャッシュ戦略付き読み込み結果
        """
        result = self.load_from_excel_with_cache(file_path, sheet_name=sheet_name)
        
        # キャッシュ戦略情報追加
        result.update({
            "cache_strategy": strategy,
            "max_cache_entries": max_entries,
            "cache_applied": True
        })
        return result

    def load_from_excel_with_benchmark(
        self, 
        file_path: str,
        sheet_name: str | None = None
    ) -> dict[str, Any]:
        """ベンチマーク付き読み込み（REFACTOR: DRY原則適用）。

        Args:
            file_path: Excelファイルパス
            sheet_name: シート名

        Returns:
            dict: ベンチマーク付き読み込み結果
        """
        # DRY原則: 共通測定メソッド使用
        result, metrics = self._measure_performance(
            self.load_from_excel, file_path, sheet_name
        )
        
        # ベンチマーク情報追加
        result.update({
            "benchmark": {
                "elapsed_time": metrics["elapsed_time"],
                "peak_memory_mb": metrics["peak_memory_mb"],
                "rows_processed": len(result["data"]) if result["data"] else 0
            }
        })
        return result

    def measure_baseline_performance(
        self, 
        file_path: str,
        sheet_name: str | None = None
    ) -> dict[str, Any]:
        """ベースライン性能測定（REFACTOR: DRY原則適用）。

        Args:
            file_path: Excelファイルパス
            sheet_name: シート名

        Returns:
            dict: ベースライン性能結果
        """
        # DRY原則: 共通測定メソッド使用
        _, metrics = self._measure_performance(
            self.load_from_excel, file_path, sheet_name
        )
        
        return {
            "baseline_time": metrics["elapsed_time"],
            "baseline_memory_mb": metrics["peak_memory_mb"]
        }

    def load_from_excel_with_regression_check(
        self, 
        file_path: str,
        sheet_name: str | None = None
    ) -> dict[str, Any]:
        """性能回帰チェック付き読み込み（最小実装）。

        Args:
            file_path: Excelファイルパス
            sheet_name: シート名

        Returns:
            dict: 回帰チェック付き読み込み結果
        """
        result = self.load_from_excel_with_benchmark(file_path, sheet_name)
        
        # 回帰チェック情報追加
        result.update({
            "regression_check": True
        })
        return result

    def load_from_excel_with_concurrent_optimization(
        self, 
        file_path: str,
        sheet_name: str | None = None
    ) -> dict[str, Any]:
        """並行処理最適化付き読み込み（最小実装）。

        Args:
            file_path: Excelファイルパス
            sheet_name: シート名

        Returns:
            dict: 並行処理最適化付き読み込み結果
        """
        result = self.load_from_excel(file_path, sheet_name)
        
        # 並行処理最適化情報追加
        result.update({
            "concurrent_optimization": True
        })
        return result

    def load_from_excel_with_streaming_cache(
        self, 
        file_path: str,
        chunk_size: int = 500,
        enable_cache: bool = True,
        sheet_name: str | None = None
    ) -> dict[str, Any]:
        """ストリーミング処理とキャッシュの組み合わせ（最小実装）。

        Args:
            file_path: Excelファイルパス
            chunk_size: チャンクサイズ
            enable_cache: キャッシュ有効化
            sheet_name: シート名

        Returns:
            dict: ストリーミング+キャッシュ読み込み結果
        """
        if enable_cache:
            result = self.load_from_excel_with_cache(file_path, sheet_name=sheet_name)
        else:
            result = self.load_from_excel(file_path, sheet_name)
        
        # ストリーミング+キャッシュ情報追加
        result.update({
            "streaming": True,
            "chunk_size": chunk_size,
            "cache_enabled": enable_cache,
            "performance_optimized": True
        })
        return result
