"""Phase 3: JSON Caching機能のTDDテスト.

Task 3.4: `:json-cache:` オプション実装のテスト
- キャッシュファイル生成
- 更新時刻ベース判定
- ファイル変更検出
- キャッシュ無効化
"""

import json
import os
import shutil
import tempfile
import time

import pytest
from openpyxl import Workbook

# Excel対応がある場合のみテストを実行
try:
    from sphinxcontrib.jsontable.excel_data_loader import ExcelDataLoader

    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


@pytest.mark.skipif(not EXCEL_AVAILABLE, reason="Excel support not available")
class TestJSONCache:
    """Phase 3: JSON Caching機能のテスト."""

    def setup_method(self):
        """各テストメソッドの前に実行される."""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = ExcelDataLoader(self.temp_dir)

    def teardown_method(self):
        """各テストメソッドの後に実行される."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_excel(self) -> str:
        """テスト用のExcelファイルを作成.

        Returns:
            str: 作成されたファイルのパス
        """
        file_path = os.path.join(self.temp_dir, "cache_test.xlsx")

        wb = Workbook()
        ws = wb.active

        # ヘッダー行
        ws["A1"] = "商品名"
        ws["B1"] = "価格"
        ws["C1"] = "在庫"

        # データ行
        ws["A2"] = "商品A"
        ws["B2"] = "1000"
        ws["C2"] = "10"

        ws["A3"] = "商品B"
        ws["B3"] = "2000"
        ws["C3"] = "5"

        wb.save(file_path)
        return file_path

    def test_cache_file_creation(self):
        """キャッシュファイル作成テスト（未実装なので失敗する）."""
        excel_path = self.create_test_excel()

        # 最初の読み込みでキャッシュファイルが作成される
        result = self.loader.load_from_excel_with_cache(excel_path)

        # キャッシュファイルの存在確認（実際に使用されたパスを取得）
        cache_path = result["cache_path"]
        assert os.path.exists(cache_path)

        # キャッシュファイルの内容確認
        with open(cache_path, encoding="utf-8") as f:
            cache_data = json.load(f)

        assert cache_data["source_file"] == excel_path
        assert "data" in cache_data
        assert "headers" in cache_data
        assert "cache_timestamp" in cache_data
        assert cache_data["data"] == result["data"]
        assert cache_data["headers"] == result["headers"]

    def test_cache_hit_performance(self):
        """キャッシュヒット時のパフォーマンステスト（未実装なので失敗する）."""
        excel_path = self.create_test_excel()

        # 最初の読み込み（キャッシュ作成）
        start_time = time.time()
        result1 = self.loader.load_from_excel_with_cache(excel_path)
        first_load_time = time.time() - start_time

        # 二回目の読み込み（キャッシュからの読み込み）
        start_time = time.time()
        result2 = self.loader.load_from_excel_with_cache(excel_path)
        cache_load_time = time.time() - start_time

        # キャッシュからの読み込みの方が高速であることを確認
        assert cache_load_time < first_load_time

        # データが同一であることを確認
        assert result1["data"] == result2["data"]
        assert result1["headers"] == result2["headers"]
        assert result2["cache_hit"] == True

    def test_cache_invalidation_on_file_change(self):
        """ファイル変更時のキャッシュ無効化テスト（未実装なので失敗する）."""
        excel_path = self.create_test_excel()

        # 最初の読み込み（キャッシュ作成）
        result1 = self.loader.load_from_excel_with_cache(excel_path)
        cache_path = result1["cache_path"]

        # キャッシュの更新時刻を取得
        cache_mtime_1 = os.path.getmtime(cache_path)

        # 少し待ってからExcelファイルを変更
        time.sleep(1.0)

        # Excelファイルを変更
        wb = Workbook()
        ws = wb.active
        ws["A1"] = "商品名"
        ws["B1"] = "価格"
        ws["C1"] = "在庫"
        ws["A2"] = "新商品"  # データを変更
        ws["B2"] = "3000"
        ws["C2"] = "15"
        wb.save(excel_path)

        # 再読み込み（キャッシュ無効化・再作成）
        result2 = self.loader.load_from_excel_with_cache(excel_path)

        # キャッシュが更新されていることを確認
        cache_mtime_2 = os.path.getmtime(cache_path)
        assert cache_mtime_2 > cache_mtime_1

        # 変更されたデータが反映されていることを確認（data[1][0]は最初のデータ行の1列目）
        assert result2["data"][1][0] == "新商品"
        assert result2["cache_hit"] == False

    def test_cache_with_options(self):
        """オプション付きでのキャッシュテスト（未実装なので失敗する）."""
        excel_path = self.create_test_excel()

        # ヘッダー行指定でキャッシュ
        result1 = self.loader.load_from_excel_with_cache(excel_path, header_row=0)

        # 同じオプションでキャッシュヒット
        result2 = self.loader.load_from_excel_with_cache(excel_path, header_row=0)

        # 異なるオプションで別キャッシュ
        result3 = self.loader.load_from_excel_with_cache(excel_path, header_row=None)

        assert result2["cache_hit"] == True
        assert result3["cache_hit"] == False  # 別オプションなのでキャッシュミス
        assert result1["headers"] == result2["headers"]
        assert result1["headers"] != result3.get("headers", [])

    def test_cache_file_path_generation(self):
        """キャッシュファイルパス生成テスト（未実装なので失敗する）."""
        excel_path = self.create_test_excel()

        # キャッシュファイルパスの生成
        cache_path = self.loader._get_cache_file_path(excel_path)

        # 期待されるパス構造
        expected_dir = os.path.join(self.temp_dir, ".jsontable_cache")
        assert cache_path.startswith(expected_dir)
        assert cache_path.endswith(".json")

        # ファイル名がExcelファイル名に基づいていることを確認
        excel_basename = os.path.basename(excel_path)
        assert excel_basename.replace(".xlsx", "") in cache_path

    def test_cache_with_range_option(self):
        """範囲指定オプションでのキャッシュテスト（未実装なので失敗する）."""
        excel_path = self.create_test_excel()

        # 範囲指定でキャッシュ
        result1 = self.loader.load_from_excel_with_cache(excel_path, range_spec="A1:B3")

        # 同じ範囲指定でキャッシュヒット
        result2 = self.loader.load_from_excel_with_cache(excel_path, range_spec="A1:B3")

        # 異なる範囲指定で別キャッシュ
        result3 = self.loader.load_from_excel_with_cache(excel_path, range_spec="A1:C3")

        assert result2["cache_hit"] == True
        assert result3["cache_hit"] == False
        assert len(result1["data"][0]) == 2  # A:B列
        assert len(result3["data"][0]) == 3  # A:C列

    def test_cache_cleanup(self):
        """キャッシュクリーンアップテスト（未実装なので失敗する）."""
        excel_path = self.create_test_excel()

        # キャッシュファイル作成
        result = self.loader.load_from_excel_with_cache(excel_path)
        cache_path = result["cache_path"]
        assert os.path.exists(cache_path)

        # キャッシュクリーンアップ
        self.loader.clear_cache(excel_path)
        assert not os.path.exists(cache_path)

    def test_cache_corruption_recovery(self):
        """キャッシュファイル破損時の回復テスト（未実装なので失敗する）."""
        excel_path = self.create_test_excel()

        # 正常なキャッシュ作成
        result1 = self.loader.load_from_excel_with_cache(excel_path)
        cache_path = result1["cache_path"]

        # キャッシュファイルを破損
        with open(cache_path, "w") as f:
            f.write("broken json content")

        # 破損キャッシュからの回復
        result2 = self.loader.load_from_excel_with_cache(excel_path)

        # 新しいキャッシュが作成されることを確認
        assert result2["cache_hit"] == False
        assert result1["data"] == result2["data"]

    def test_concurrent_cache_access(self):
        """並行キャッシュアクセステスト（未実装なので失敗する）."""
        excel_path = self.create_test_excel()

        # 事前にキャッシュファイルを作成しておく
        initial_result = self.loader.load_from_excel_with_cache(excel_path)
        assert initial_result["cache_hit"] == False

        import concurrent.futures
        import threading

        results = []
        errors = []
        lock = threading.Lock()

        def load_with_cache():
            try:
                result = self.loader.load_from_excel_with_cache(excel_path)
                with lock:
                    results.append(result)
            except Exception as e:
                with lock:
                    errors.append(e)

        # 複数スレッドで同時アクセス
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(load_with_cache) for _ in range(5)]
            concurrent.futures.wait(futures)

        # エラーが発生しないことを確認
        assert len(errors) == 0, f"Concurrent cache access errors: {errors}"
        assert len(results) == 5

        # キャッシュが事前に作成されているので、すべてキャッシュヒットするはず
        cache_hits = [r.get("cache_hit", False) for r in results]
        assert all(cache_hits), f"All cache hits expected, but got: {cache_hits}"

    def test_cache_size_limit(self):
        """キャッシュサイズ制限テスト（未実装なので失敗する）."""
        # 大きなExcelファイルを作成
        file_path = os.path.join(self.temp_dir, "large_cache_test.xlsx")
        wb = Workbook()
        ws = wb.active

        # 大量のデータを作成
        for i in range(1000):
            ws[f"A{i + 1}"] = f"データ{i}"
            ws[f"B{i + 1}"] = f"値{i}"

        wb.save(file_path)

        # キャッシュサイズ制限の設定
        max_cache_size = 1024 * 1024  # 1MB
        result = self.loader.load_from_excel_with_cache(
            file_path, max_cache_size=max_cache_size
        )

        cache_path = self.loader._get_cache_file_path(file_path)
        if os.path.exists(cache_path):
            cache_size = os.path.getsize(cache_path)
            # キャッシュサイズが制限を大幅に超えていないことを確認
            assert cache_size < max_cache_size * 2, (
                f"Cache size {cache_size} exceeds limit"
            )


if __name__ == "__main__":
    # スタンドアロンテスト実行
    pytest.main([__file__, "-v"])
