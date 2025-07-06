"""ファイルレベルキャッシュテスト

TDD REDフェーズ: 失敗するテストを先に作成
Task 1.2.1: キャッシュ基盤アーキテクチャ
"""

import hashlib
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

# REDフェーズ: 存在しないクラスをインポート（意図的にエラー）
try:
    from sphinxcontrib.jsontable.core.file_level_cache import (
        FileLevelCache,
        CacheKey,
        CacheEntry,
        CacheConfiguration
    )
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False


class TestFileLevelCache:
    """ファイルレベルキャッシュテスト
    
    TDD REDフェーズ: キャッシュ基盤機能が存在しないため、
    これらのテストは意図的に失敗する。
    """

    def setup_method(self):
        """各テストメソッドの前に実行される設定."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """各テストメソッドの後に実行されるクリーンアップ."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_excel_file(self, filename: str = "test_cache.xlsx", rows: int = 1000) -> Path:
        """テスト用Excelファイル作成
        
        Args:
            filename: ファイル名
            rows: 行数
            
        Returns:
            Path: 作成されたファイルのパス
        """
        file_path = self.temp_dir / filename
        
        data = {
            'ID': [f"ID{i:04d}" for i in range(rows)],
            'Name': [f"Name_{i}" for i in range(rows)],
            'Value': [i * 10.5 for i in range(rows)],
            'Category': [f"Category_{i % 10}" for i in range(rows)]
        }
        
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)
        
        return file_path

    @pytest.mark.performance
    def test_file_cache_basic_operations(self):
        """ファイルキャッシュ基本操作テスト
        
        RED: FileLevelCacheクラスが存在しないため失敗する
        期待動作:
        - キャッシュの基本CRUD操作
        - ファイルベースのキャッシュキー生成
        - キャッシュヒット・ミスの適切な処理
        - メモリ効率的なキャッシュ管理
        """
        # テストファイル作成
        test_file = self.create_test_excel_file()
        
        # キャッシュ初期化
        cache_config = CacheConfiguration(
            max_cache_size=10,
            max_memory_mb=100,
            enable_compression=True,
            enable_persistence=False,
            cache_directory=self.temp_dir / "cache"
        )
        
        file_cache = FileLevelCache(cache_config)
        
        # キャッシュキー生成テスト
        cache_key = file_cache.generate_cache_key(
            file_path=test_file,
            processing_options={
                'sheet_name': 'Sheet1',
                'header_row': 0,
                'data_range': 'A1:D1000'
            }
        )
        
        assert isinstance(cache_key, CacheKey)
        assert cache_key.file_path == str(test_file)
        assert cache_key.file_hash is not None
        assert cache_key.options_hash is not None
        assert cache_key.unique_key is not None
        
        # 初期状態でキャッシュミス確認
        cached_data = file_cache.get(cache_key)
        assert cached_data is None
        assert file_cache.is_cache_hit(cache_key) is False
        
        # テストデータ作成
        test_data = {
            'processed_data': [{'ID': 'ID0001', 'Name': 'Name_1', 'Value': 10.5}],
            'metadata': {'rows': 1000, 'columns': 4, 'processing_time': 1.5}
        }
        
        # キャッシュ保存テスト
        cache_entry = file_cache.put(cache_key, test_data)
        assert isinstance(cache_entry, CacheEntry)
        assert cache_entry.cache_key == cache_key
        assert cache_entry.data == test_data
        assert cache_entry.created_at > 0
        assert cache_entry.accessed_at > 0
        assert cache_entry.access_count == 1
        
        # キャッシュヒット確認
        cached_data = file_cache.get(cache_key)
        assert cached_data is not None
        assert cached_data == test_data
        assert file_cache.is_cache_hit(cache_key) is True
        
        # キャッシュ統計確認
        cache_stats = file_cache.get_cache_statistics()
        assert cache_stats['total_entries'] == 1
        assert cache_stats['cache_hits'] == 1
        assert cache_stats['cache_misses'] == 1
        assert cache_stats['hit_ratio'] == 0.5
        assert cache_stats['memory_usage_mb'] > 0

    @pytest.mark.performance
    def test_cache_key_generation_unique(self):
        """キャッシュキー生成ユニーク性テスト
        
        RED: CacheKeyクラスが存在しないため失敗する
        期待動作:
        - ファイル内容変更時のキー変更
        - オプション変更時のキー変更
        - 同一条件での同一キー生成
        - ハッシュ衝突回避
        """
        # 異なるファイル作成
        file1 = self.create_test_excel_file("file1.xlsx", 100)
        file2 = self.create_test_excel_file("file2.xlsx", 200)
        
        cache_config = CacheConfiguration()
        file_cache = FileLevelCache(cache_config)
        
        options1 = {'sheet_name': 'Sheet1', 'header_row': 0}
        options2 = {'sheet_name': 'Sheet1', 'header_row': 1}
        
        # 異なるファイルで異なるキー生成確認
        key1_file1 = file_cache.generate_cache_key(file1, options1)
        key1_file2 = file_cache.generate_cache_key(file2, options1)
        assert key1_file1.unique_key != key1_file2.unique_key
        
        # 異なるオプションで異なるキー生成確認
        key1_opt1 = file_cache.generate_cache_key(file1, options1)
        key1_opt2 = file_cache.generate_cache_key(file1, options2)
        assert key1_opt1.unique_key != key1_opt2.unique_key
        
        # 同一条件で同一キー生成確認
        key1_same1 = file_cache.generate_cache_key(file1, options1)
        key1_same2 = file_cache.generate_cache_key(file1, options1)
        assert key1_same1.unique_key == key1_same2.unique_key
        
        # ファイル変更時のキー変更確認
        time.sleep(0.1)  # ファイル更新時間差を作る
        
        # ファイル内容変更
        new_data = pd.DataFrame({'ID': ['NEW001'], 'Value': [999]})
        new_data.to_excel(file1, index=False)
        
        key1_modified = file_cache.generate_cache_key(file1, options1)
        assert key1_modified.unique_key != key1_same1.unique_key

    @pytest.mark.performance
    def test_cache_validity_file_modification(self):
        """キャッシュ有効性・ファイル更新検証テスト
        
        RED: ファイル更新検証機能が存在しないため失敗する
        期待動作:
        - ファイル更新時の自動キャッシュ無効化
        - 修正時間ベースの有効性判定
        - 整合性保証メカニズム
        """
        test_file = self.create_test_excel_file()
        original_mtime = test_file.stat().st_mtime
        
        cache_config = CacheConfiguration(enable_file_modification_check=True)
        file_cache = FileLevelCache(cache_config)
        
        options = {'sheet_name': 'Sheet1'}
        cache_key = file_cache.generate_cache_key(test_file, options)
        
        # 初期データをキャッシュ
        original_data = {'data': 'original_content', 'timestamp': original_mtime}
        file_cache.put(cache_key, original_data)
        
        # キャッシュヒット確認
        cached_data = file_cache.get(cache_key)
        assert cached_data == original_data
        assert file_cache.is_cache_valid(cache_key) is True
        
        # ファイル更新
        time.sleep(0.1)
        updated_data = pd.DataFrame({'ID': ['UPDATED'], 'Value': [123]})
        updated_data.to_excel(test_file, index=False)
        
        # ファイル更新後のキャッシュ無効化確認
        assert file_cache.is_cache_valid(cache_key) is False
        
        # 無効キャッシュからのデータ取得確認
        cached_data_after_update = file_cache.get(cache_key)
        assert cached_data_after_update is None  # 無効化により None 返却
        
        # 新しいキャッシュキー生成・保存
        new_cache_key = file_cache.generate_cache_key(test_file, options)
        assert new_cache_key.unique_key != cache_key.unique_key
        
        new_data = {'data': 'updated_content', 'timestamp': test_file.stat().st_mtime}
        file_cache.put(new_cache_key, new_data)
        
        # 新キャッシュからのデータ取得確認
        new_cached_data = file_cache.get(new_cache_key)
        assert new_cached_data == new_data

    @pytest.mark.performance
    def test_lru_cache_eviction_policy(self):
        """LRUキャッシュ削除ポリシーテスト
        
        RED: LRU削除機能が存在しないため失敗する
        期待動作:
        - キャッシュサイズ制限の遵守
        - 最近最少使用アイテムの自動削除
        - アクセス時間更新メカニズム
        """
        # 小さなキャッシュサイズで制限テスト
        cache_config = CacheConfiguration(
            max_cache_size=3,
            lru_eviction_enabled=True
        )
        file_cache = FileLevelCache(cache_config)
        
        # 複数ファイル・キャッシュエントリ作成
        files_and_keys = []
        for i in range(5):
            test_file = self.create_test_excel_file(f"file_{i}.xlsx", 100)
            cache_key = file_cache.generate_cache_key(test_file, {'index': i})
            test_data = {'file_index': i, 'data': f'content_{i}'}
            
            file_cache.put(cache_key, test_data)
            files_and_keys.append((test_file, cache_key, test_data))
            
            time.sleep(0.01)  # LRU順序確保のための時間差
        
        # キャッシュサイズ制限確認（3つまで）
        cache_stats = file_cache.get_cache_statistics()
        assert cache_stats['total_entries'] == 3
        
        # 古いエントリ（0, 1）が削除され、新しいエントリ（2, 3, 4）が保持確認
        oldest_file, oldest_key, oldest_data = files_and_keys[0]
        assert file_cache.get(oldest_key) is None  # 削除済み
        
        second_oldest_file, second_oldest_key, second_oldest_data = files_and_keys[1]
        assert file_cache.get(second_oldest_key) is None  # 削除済み
        
        # 最新エントリは保持確認
        for i in range(2, 5):
            _, cache_key, expected_data = files_and_keys[i]
            cached_data = file_cache.get(cache_key)
            assert cached_data == expected_data
        
        # アクセスによるLRU順序変更テスト
        # 中間エントリにアクセス
        middle_file, middle_key, middle_data = files_and_keys[2]
        accessed_data = file_cache.get(middle_key)
        assert accessed_data == middle_data
        
        # 新しいエントリ追加
        new_file = self.create_test_excel_file("new_file.xlsx", 100)
        new_key = file_cache.generate_cache_key(new_file, {'index': 999})
        new_data = {'file_index': 999, 'data': 'new_content'}
        file_cache.put(new_key, new_data)
        
        # アクセスしたエントリは保持、アクセスしていないエントリが削除確認
        assert file_cache.get(middle_key) is not None  # アクセス済みで保持
        assert file_cache.get(new_key) is not None  # 新規追加で保持

    @pytest.mark.performance
    def test_cache_performance_improvement(self):
        """キャッシュパフォーマンス改善効果テスト
        
        RED: パフォーマンス測定機能が存在しないため失敗する
        期待動作:
        - キャッシュ使用時の処理時間短縮
        - メモリ使用量最適化
        - 大容量ファイルでの効果確認
        """
        # 大きなテストファイル作成
        large_file = self.create_test_excel_file("large_test.xlsx", 5000)
        
        cache_config = CacheConfiguration(
            max_cache_size=5,
            max_memory_mb=50,
            enable_performance_tracking=True
        )
        file_cache = FileLevelCache(cache_config)
        
        options = {'sheet_name': 'Sheet1', 'header_row': 0}
        cache_key = file_cache.generate_cache_key(large_file, options)
        
        # 初回読み込み時間測定（キャッシュなし）
        start_time = time.perf_counter()
        
        # 模擬的な重い処理（実際にはExcel処理）
        df = pd.read_excel(large_file)
        processed_data = {
            'data': df.to_dict('records')[:100],  # サンプルデータ
            'metadata': {
                'total_rows': len(df),
                'columns': list(df.columns),
                'processing_timestamp': time.time()
            }
        }
        
        first_load_time = time.perf_counter() - start_time
        
        # キャッシュに保存
        file_cache.put(cache_key, processed_data)
        
        # キャッシュからの読み込み時間測定
        start_time = time.perf_counter()
        cached_data = file_cache.get(cache_key)
        cache_load_time = time.perf_counter() - start_time
        
        # パフォーマンス改善確認
        assert cached_data is not None
        assert cached_data == processed_data
        assert cache_load_time < first_load_time  # キャッシュの方が高速
        
        # 改善率計算
        improvement_ratio = first_load_time / cache_load_time
        assert improvement_ratio > 2.0  # 最低2倍以上の高速化
        
        # パフォーマンス統計確認
        perf_stats = file_cache.get_performance_statistics()
        assert 'cache_hit_time_avg' in perf_stats
        assert 'cache_miss_time_avg' in perf_stats
        assert 'improvement_ratio' in perf_stats
        assert perf_stats['improvement_ratio'] >= 2.0
        
        print(f"Cache performance improvement: {improvement_ratio:.1f}x faster")

    @pytest.mark.performance  
    def test_compressed_cache_storage(self):
        """圧縮キャッシュ保存テスト
        
        RED: 圧縮キャッシュ機能が存在しないため失敗する
        期待動作:
        - データ圧縮による保存容量削減
        - 圧縮・展開の透明性
        - 圧縮率とパフォーマンスのバランス
        """
        test_file = self.create_test_excel_file("compression_test.xlsx", 2000)
        
        # 圧縮有効キャッシュ
        compressed_config = CacheConfiguration(
            enable_compression=True,
            compression_level=6,
            compression_algorithm='gzip'
        )
        compressed_cache = FileLevelCache(compressed_config)
        
        # 圧縮無効キャッシュ（比較用）
        uncompressed_config = CacheConfiguration(enable_compression=False)
        uncompressed_cache = FileLevelCache(uncompressed_config)
        
        # 大きなテストデータ作成
        df = pd.read_excel(test_file)
        large_data = {
            'full_data': df.to_dict('records'),
            'metadata': {
                'description': 'Large dataset for compression testing' * 100,
                'processing_info': {'step_' + str(i): f'data_{i}' * 50 for i in range(100)}
            }
        }
        
        cache_key = compressed_cache.generate_cache_key(test_file, {'compression_test': True})
        
        # 圧縮キャッシュ保存
        compressed_cache.put(cache_key, large_data)
        
        # 非圧縮キャッシュ保存  
        uncompressed_cache.put(cache_key, large_data)
        
        # 圧縮効果確認
        compressed_stats = compressed_cache.get_cache_statistics()
        uncompressed_stats = uncompressed_cache.get_cache_statistics()
        
        compressed_size = compressed_stats['memory_usage_mb']
        uncompressed_size = uncompressed_stats['memory_usage_mb']
        
        compression_ratio = uncompressed_size / compressed_size
        assert compression_ratio > 1.5  # 最低50%以上の圧縮効果
        
        # データ整合性確認（圧縮・展開による劣化なし）
        compressed_retrieved = compressed_cache.get(cache_key)
        uncompressed_retrieved = uncompressed_cache.get(cache_key)
        
        assert compressed_retrieved == uncompressed_retrieved == large_data
        
        # 圧縮統計確認
        compression_stats = compressed_cache.get_compression_statistics()
        assert compression_stats['compression_ratio'] >= 1.5
        assert compression_stats['compression_time_ms'] > 0
        assert compression_stats['decompression_time_ms'] > 0
        
        print(f"Compression ratio: {compression_ratio:.1f}x size reduction")

    @pytest.mark.performance
    def test_cache_memory_efficiency(self):
        """キャッシュメモリ効率性テスト
        
        RED: メモリ効率管理機能が存在しないため失敗する
        期待動作:
        - メモリ制限値の厳守
        - 効率的メモリ使用量監視
        - メモリ不足時の適切な対応
        """
        # 厳しいメモリ制限設定
        memory_config = CacheConfiguration(
            max_memory_mb=10,  # 10MB制限
            memory_monitoring_enabled=True,
            memory_cleanup_threshold=8,  # 8MB超過で cleanup
            enable_automatic_cleanup=True
        )
        file_cache = FileLevelCache(memory_config)
        
        # メモリ使用量テスト用データ作成
        test_files = []
        for i in range(10):
            file_path = self.create_test_excel_file(f"memory_test_{i}.xlsx", 500)
            test_files.append(file_path)
        
        # キャッシュ使用量監視
        cached_count = 0
        for i, test_file in enumerate(test_files):
            cache_key = file_cache.generate_cache_key(test_file, {'index': i})
            
            # 大きなデータ作成
            df = pd.read_excel(test_file)
            large_data = {
                'data': df.to_dict('records'),
                'extra_data': [f'extra_{j}' * 100 for j in range(100)]
            }
            
            # キャッシュ保存
            try:
                file_cache.put(cache_key, large_data)
                cached_count += 1
                
                # メモリ使用量確認
                cache_stats = file_cache.get_cache_statistics()
                current_memory = cache_stats['memory_usage_mb']
                
                # メモリ制限遵守確認
                assert current_memory <= memory_config.max_memory_mb * 1.1  # 10%マージン
                
            except MemoryError:
                # メモリ不足時の適切なエラー
                break
        
        # 実際にいくつかキャッシュされたことを確認
        assert cached_count >= 3  # 最低3つはキャッシュできること
        
        # メモリ統計詳細確認
        memory_stats = file_cache.get_memory_statistics()
        assert memory_stats['memory_limit_mb'] == 10
        assert memory_stats['current_usage_mb'] <= 10
        assert memory_stats['cleanup_triggered_count'] >= 0
        assert memory_stats['memory_efficiency_ratio'] >= 0.8  # 80%以上の効率

    @pytest.mark.performance
    def test_cache_integration_full_pipeline(self):
        """キャッシュ統合・全パイプラインテスト
        
        RED: 統合キャッシュ機能が存在しないため失敗する
        期待動作:
        - 実際のExcel処理パイプラインとの統合
        - エンドツーエンドパフォーマンス改善
        - 複数処理オプションでのキャッシュ効果
        """
        # 複数シート・複雑オプションのテストファイル
        test_file = self.create_test_excel_file("integration_test.xlsx", 1500)
        
        # 統合キャッシュ設定
        integration_config = CacheConfiguration(
            max_cache_size=20,
            max_memory_mb=200,
            enable_compression=True,
            enable_performance_tracking=True,
            enable_file_modification_check=True,
            lru_eviction_enabled=True
        )
        file_cache = FileLevelCache(integration_config)
        
        # 異なる処理オプションでのキャッシュテスト
        test_scenarios = [
            {'sheet_name': 'Sheet1', 'header_row': 0, 'range': 'A1:D1000'},
            {'sheet_name': 'Sheet1', 'header_row': 0, 'range': 'A1:D500'},
            {'sheet_name': 'Sheet1', 'header_row': 1, 'range': 'A1:D1000'},
            {'sheet_name': 'Sheet1', 'header_row': 0, 'range': 'B2:C800'},
        ]
        
        processing_times = []
        
        for i, scenario in enumerate(test_scenarios):
            cache_key = file_cache.generate_cache_key(test_file, scenario)
            
            # 初回処理時間測定
            start_time = time.perf_counter()
            
            # 実際のExcel処理シミュレーション
            df = pd.read_excel(test_file)
            processed_result = {
                'processed_data': df.head(100).to_dict('records'),
                'scenario': scenario,
                'processing_metadata': {
                    'total_rows': len(df),
                    'scenario_index': i,
                    'timestamp': time.time()
                }
            }
            
            processing_time = time.perf_counter() - start_time
            processing_times.append(processing_time)
            
            # キャッシュ保存
            file_cache.put(cache_key, processed_result)
            
            # 即座にキャッシュからの読み込みテスト
            start_time = time.perf_counter()
            cached_result = file_cache.get(cache_key)
            cache_time = time.perf_counter() - start_time
            
            # データ整合性確認
            assert cached_result == processed_result
            
            # パフォーマンス改善確認
            assert cache_time < processing_time
            improvement = processing_time / cache_time
            assert improvement > 3.0  # 3倍以上の高速化
        
        # 統合統計確認
        integration_stats = file_cache.get_integration_statistics()
        assert integration_stats['total_scenarios_cached'] == len(test_scenarios)
        assert integration_stats['average_improvement_ratio'] >= 3.0
        assert integration_stats['cache_hit_ratio'] >= 0.0  # 初回なのでヒット率は低い
        
        # 全体パフォーマンス統計
        overall_stats = file_cache.get_cache_statistics()
        assert overall_stats['total_entries'] == len(test_scenarios)
        assert overall_stats['memory_usage_mb'] > 0
        assert overall_stats['compression_enabled'] is True
        
        print(f"Integration test: {len(test_scenarios)} scenarios cached successfully")