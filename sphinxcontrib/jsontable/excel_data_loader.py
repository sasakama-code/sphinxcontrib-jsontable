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

from pathlib import Path
from typing import Any

import pandas as pd


class ExcelDataLoader:
    """Excel ファイルの読み込みとJSON変換を行うクラス。

    セキュリティ要件:
    - パストラバーサル攻撃の防止
    - ファイルサイズ制限の実装
    - 適切なエラーハンドリング
    """

    # セキュリティ設定
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    SUPPORTED_EXTENSIONS = {'.xlsx', '.xls'}

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
            raise ValueError(f"Unsupported file format: {file_path_obj.suffix}. "
                           f"Supported formats: {', '.join(self.SUPPORTED_EXTENSIONS)}")

        # ファイルサイズチェック
        file_size = file_path_obj.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(f"File size ({file_size} bytes) exceeds limit "
                           f"({self.MAX_FILE_SIZE} bytes)")

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
            raise ValueError(f"Failed to detect sheets in {file_path}: {e!s}")

    def get_sheet_name_by_index(self, file_path: str, sheet_index: int) -> str:
        """シートインデックスからシート名を取得。

        Args:
            file_path: Excelファイルパス
            sheet_index: シートインデックス（0ベース）

        Returns:
            str: 指定されたインデックスのシート名

        Raises:
            ValueError: インデックスが範囲外の場合
        """
        if sheet_index < 0:
            raise ValueError("Sheet index must be non-negative")

        try:
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names

            if sheet_index >= len(sheet_names):
                raise ValueError(f"Sheet index {sheet_index} is out of range. Available sheets: {len(sheet_names)}")

            return sheet_names[sheet_index]

        except Exception as e:
            raise ValueError(f"Failed to get sheet name by index {sheet_index} in {file_path}: {e!s}")

    def load_from_excel_by_index(self, file_path: str,
                                sheet_index: int,
                                header_row: int | None = None) -> dict[str, Any]:
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
        return self.load_from_excel(file_path, sheet_name=sheet_name, header_row=header_row)

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
        first_row_text_ratio = sum(isinstance(val, str) for val in first_row) / len(first_row)
        second_row_numeric_ratio = sum(pd.api.types.is_numeric_dtype(type(val))
                                     for val in second_row) / len(second_row)

        return first_row_text_ratio > 0.5 and second_row_numeric_ratio > 0.3

    def data_type_conversion(self, df: pd.DataFrame) -> list[list[str]]:
        """DataFrameをJSON互換の2D配列に変換。

        Args:
            df: 変換するDataFrame

        Returns:
            List[List[str]]: JSON互換の2D配列
        """
        # NaN値を空文字列に変換
        df_filled = df.fillna('')

        # 全ての値を文字列に変換（JSON互換性のため）
        result = []
        for _, row in df_filled.iterrows():
            converted_row = []
            for value in row:
                if pd.isna(value):
                    converted_row.append('')
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

    def load_from_excel(self, file_path: str,
                       sheet_name: str | None = None,
                       header_row: int | None = None) -> dict[str, Any]:
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
            # シート名の決定
            if sheet_name is None:
                sheet_name = self.basic_sheet_detection(file_path)

            # Excelファイル読み込み
            if header_row is not None:
                # 明示的なヘッダー行指定
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
            else:
                # 自動ヘッダー検出
                df_no_header = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

                if self.header_detection(df_no_header):
                    # ヘッダーありとして再読み込み
                    df = pd.read_excel(file_path, sheet_name=sheet_name, header=0)
                else:
                    # ヘッダーなし
                    df = df_no_header

            # 空のDataFrameチェック
            if df.empty:
                raise ValueError(f"Empty data in sheet '{sheet_name}' of file: {file_path}")

            # データ変換
            data_array = self.data_type_conversion(df)

            # ヘッダー情報の抽出
            has_header = not isinstance(df.columns[0], int)  # 数値カラム名でない=ヘッダーあり
            headers = list(df.columns) if has_header else None

            # 結果構築
            result = {
                'data': data_array,
                'has_header': has_header,
                'headers': headers,
                'sheet_name': sheet_name,
                'file_path': file_path,
                'rows': len(data_array),
                'columns': len(data_array[0]) if data_array else 0
            }

            return result

        except pd.errors.EmptyDataError:
            raise ValueError(f"Empty Excel file: {file_path}")
        except pd.errors.ParserError as e:
            raise ValueError(f"Failed to parse Excel file {file_path}: {e!s}")
        except Exception as e:
            raise Exception(f"Unexpected error loading Excel file {file_path}: {e!s}")
