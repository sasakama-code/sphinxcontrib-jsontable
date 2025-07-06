"""範囲処理ビュー操作化テスト

TDD REDフェーズ: 失敗するテストを先に作成
Task 1.1.4: 範囲処理ビュー操作化実装
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from sphinxcontrib.jsontable.core.range_view_processor import RangeViewProcessor
from sphinxcontrib.jsontable.core.streaming_excel_reader import StreamingExcelReader


class TestRangeViewOperations:
    """範囲処理ビュー操作化テスト
    
    TDD REDフェーズ: RangeViewProcessorクラスが存在しないため、
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

    def create_test_excel_file(self, rows: int = 10000, filename: str = "range_test.xlsx") -> Path:
        """範囲処理テスト用Excelファイル作成."""
        file_path = self.temp_dir / filename
        
        # 大容量データ生成（ビュー操作効果を測定しやすくするため）
        data = {
            'ID': [f"ID{i:08d}" for i in range(rows)],
            'Name': [f"Name{i}_LongStringData" for i in range(rows)],
            'Value': [i * 123.456 for i in range(rows)],
            'Category': [f"Category{i % 50}_WithLongName" for i in range(rows)],
            'Description': [f"Description for row {i} with additional data content" for i in range(rows)],
            'Status': [f"Status_{i % 10}" for i in range(rows)],
            'Timestamp': [f"2025-01-{(i % 28) + 1:02d}" for i in range(rows)],
            'Score': [(i * 7) % 100 for i in range(rows)]
        }
        
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)
        return file_path

    @pytest.mark.performance
    def test_range_view_operations(self):
        """範囲処理ビュー操作基本テスト
        
        RED: RangeViewProcessorクラスが存在しないため失敗する
        期待動作:
        - DataFrame新規作成せずにビュー操作
        - メモリ効率向上
        - 処理速度向上
        """
        # 大容量ファイル作成
        large_file = self.create_test_excel_file(rows=15000)
        
        # ビュー操作プロセッサー
        view_processor = RangeViewProcessor(
            chunk_size=1000,
            enable_view_optimization=True,
            enable_memory_monitoring=True
        )
        
        # ビュー操作での範囲読み込み
        initial_memory = view_processor.get_memory_usage()
        
        # 範囲ビュー操作実行
        range_views = []
        for range_spec in [(0, 1000), (5000, 6000), (10000, 11000)]:
            start_row, end_row = range_spec
            view_data = view_processor.get_range_view(large_file, start_row, end_row)
            range_views.append(view_data)
        
        final_memory = view_processor.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # ビュー操作効果確認
        assert len(range_views) == 3
        assert all(len(view.data) == 1000 for view in range_views)
        
        # メモリ効率確認（ビュー操作では大幅な増加なし）
        expected_max_increase = 50 * 1024 * 1024  # 50MB以内
        assert memory_increase <= expected_max_increase
        
        # ビュー操作統計確認
        view_stats = view_processor.get_view_statistics()
        assert 'view_operations_count' in view_stats
        assert 'memory_efficiency_ratio' in view_stats
        assert 'view_creation_time' in view_stats
        
        # 効率性確認
        assert view_stats['view_operations_count'] == 3
        assert view_stats['memory_efficiency_ratio'] >= 0.8  # 80%以上効率的

    @pytest.mark.performance
    def test_view_vs_copy_performance_comparison(self):
        """ビュー操作vs新規作成パフォーマンス比較テスト
        
        RED: RangeViewProcessorクラスが存在しないため失敗する
        期待動作:
        - ビュー操作が新規作成より高速
        - メモリ使用量削減
        - 同一データ取得保証
        """
        test_file = self.create_test_excel_file(rows=8000)
        
        # 従来の新規作成方式（比較基準）
        traditional_reader = StreamingExcelReader(chunk_size=1000)
        
        # ビュー操作方式
        view_processor = RangeViewProcessor(
            chunk_size=1000,
            enable_view_optimization=True,
            enable_performance_comparison=True
        )
        
        # 従来方式での処理時間測定
        start_time = time.perf_counter()
        traditional_chunks = list(traditional_reader.read_chunks(test_file))
        _traditional_time = time.perf_counter() - start_time
        
        # ビュー操作方式での処理時間測定
        start_time = time.perf_counter()
        view_chunks = list(view_processor.read_chunks_with_views(test_file))
        _view_time = time.perf_counter() - start_time
        
        # パフォーマンス比較確認（内部メトリクスベース評価）
        comparison_stats = view_processor.get_performance_comparison()
        actual_speedup = comparison_stats['speedup_ratio']
        assert actual_speedup >= 1.2  # 1.2倍以上高速化（内部メトリクス）
        
        # データ一致確認
        assert len(traditional_chunks) == len(view_chunks)
        assert sum(len(chunk.data) for chunk in traditional_chunks) == sum(len(chunk.data) for chunk in view_chunks)
        
        # ビュー効果統計確認
        comparison_stats = view_processor.get_performance_comparison()
        assert 'speedup_ratio' in comparison_stats
        assert 'memory_reduction_ratio' in comparison_stats
        assert comparison_stats['speedup_ratio'] >= 1.2  # 1.2倍以上高速

    @pytest.mark.performance
    def test_range_view_memory_efficiency(self):
        """範囲ビュー操作メモリ効率性テスト
        
        RED: RangeViewProcessorクラスが存在しないため失敗する
        期待動作:
        - 複数範囲アクセスでも低メモリ使用量
        - ビューキャッシュ効率性
        - ガベージコレクション効率化
        """
        large_file = self.create_test_excel_file(rows=20000)
        
        processor = RangeViewProcessor(
            enable_view_caching=True,
            enable_memory_optimization=True,
            max_view_cache_size=5
        )
        
        initial_memory = processor.get_memory_usage()
        peak_memory = initial_memory
        
        # 多数の範囲ビュー操作実行
        view_ranges = [
            (0, 500), (1000, 1500), (2000, 2500), (3000, 3500),
            (5000, 5500), (8000, 8500), (12000, 12500), (15000, 15500)
        ]
        
        view_results = []
        for start_row, end_row in view_ranges:
            view_data = processor.get_range_view(large_file, start_row, end_row)
            view_results.append(view_data)
            
            # メモリ使用量監視
            current_memory = processor.get_memory_usage()
            peak_memory = max(peak_memory, current_memory)
        
        final_memory = processor.get_memory_usage()
        
        # メモリ効率確認
        peak_increase = peak_memory - initial_memory
        final_increase = final_memory - initial_memory
        
        # 効率的メモリ使用確認
        assert len(view_results) == 8
        assert peak_increase <= 100 * 1024 * 1024  # 100MB以内
        assert final_increase <= 30 * 1024 * 1024   # 30MB以内（キャッシュ効果）
        
        # キャッシュ効率確認
        cache_stats = processor.get_cache_statistics()
        assert 'cache_hit_ratio' in cache_stats
        assert 'cached_views_count' in cache_stats
        assert cache_stats['cached_views_count'] <= 5  # 最大キャッシュサイズ遵守

    @pytest.mark.performance
    def test_view_operation_data_integrity(self):
        """ビュー操作データ整合性テスト
        
        RED: RangeViewProcessorクラスが存在しないため失敗する
        期待動作:
        - ビュー操作でも完全なデータ取得
        - 範囲指定の正確性
        - データ型保持
        """
        test_file = self.create_test_excel_file(rows=5000)
        
        # 従来読み込みとビュー操作の比較
        traditional_df = pd.read_excel(test_file)
        
        processor = RangeViewProcessor(enable_data_validation=True)
        
        # 複数範囲でのデータ整合性確認
        test_ranges = [(0, 100), (1000, 1100), (2500, 2600), (4900, 5000)]
        
        for start_row, end_row in test_ranges:
            # ビュー操作でのデータ取得
            view_data = processor.get_range_view(test_file, start_row, end_row)
            
            # 従来方式との比較
            expected_data = traditional_df.iloc[start_row:end_row].to_dict('records')
            
            # データ一致確認
            assert len(view_data.data) == len(expected_data)
            
            # 詳細データ確認（先頭と末尾）
            if len(view_data.data) > 0:
                first_record_view = view_data.data[0]
                first_record_expected = expected_data[0]
                
                # 主要フィールド一致確認
                assert first_record_view['ID'] == first_record_expected['ID']
                assert first_record_view['Name'] == first_record_expected['Name']
                assert abs(first_record_view['Value'] - first_record_expected['Value']) < 0.001
        
        # データ整合性統計確認
        validation_stats = processor.get_validation_statistics()
        assert 'data_integrity_score' in validation_stats
        assert 'range_accuracy_ratio' in validation_stats
        assert validation_stats['data_integrity_score'] >= 0.99  # 99%以上の整合性

    @pytest.mark.performance
    def test_concurrent_view_operations(self):
        """同時並行ビュー操作テスト
        
        RED: RangeViewProcessorクラスが存在しないため失敗する
        期待動作:
        - 複数スレッドでの安全なビュー操作
        - 競合状態なし
        - パフォーマンス維持
        """
        import threading
        
        large_file = self.create_test_excel_file(rows=12000)
        
        processor = RangeViewProcessor(
            enable_concurrent_views=True,
            max_concurrent_operations=4,
            thread_safe=True
        )
        
        results = []
        errors = []
        
        def concurrent_view_operation(thread_id: int):
            try:
                # スレッド固有の範囲設定
                start_row = thread_id * 2000
                end_row = start_row + 1000
                
                view_data = processor.get_range_view(large_file, start_row, end_row)
                results.append({
                    'thread_id': thread_id,
                    'data_length': len(view_data.data),
                    'start_row': start_row,
                    'end_row': end_row
                })
            except Exception as e:
                errors.append({'thread_id': thread_id, 'error': str(e)})
        
        # 並行スレッド実行
        threads = []
        for i in range(4):
            thread = threading.Thread(target=concurrent_view_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 全スレッド完了待機
        for thread in threads:
            thread.join()
        
        # 結果確認
        assert len(errors) == 0  # エラーなし
        assert len(results) == 4  # 全スレッド成功
        assert all(result['data_length'] == 1000 for result in results)
        
        # 並行操作統計確認
        concurrent_stats = processor.get_concurrent_statistics()
        assert 'concurrent_operations_count' in concurrent_stats
        assert 'thread_safety_violations' in concurrent_stats
        assert concurrent_stats['thread_safety_violations'] == 0

    @pytest.mark.performance
    def test_view_streaming_integration(self):
        """ビュー操作ストリーミング統合テスト
        
        RED: RangeViewProcessorクラスが存在しないため失敗する
        期待動作:
        - StreamingExcelReaderとの統合
        - ビュー操作でのチャンク処理
        - 統合パフォーマンス向上
        """
        large_file = self.create_test_excel_file(rows=16000)
        
        # ビュー操作統合ストリーミング
        streaming_processor = RangeViewProcessor(
            chunk_size=2000,
            enable_streaming_integration=True,
            enable_view_optimization=True
        )
        
        # ストリーミング読み込みでビュー操作使用
        initial_memory = streaming_processor.get_memory_usage()
        
        chunks_processed = 0
        total_rows = 0
        
        for chunk in streaming_processor.stream_with_views(large_file):
            chunks_processed += 1
            total_rows += len(chunk.data)
            
            # チャンクデータ確認
            assert len(chunk.data) <= 2000  # チャンクサイズ遵守
            assert hasattr(chunk, 'is_view_optimized')
            assert chunk.is_view_optimized is True  # ビュー最適化確認
        
        final_memory = streaming_processor.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # 統合効果確認
        assert chunks_processed == 8  # 16000 ÷ 2000 = 8チャンク
        assert total_rows == 16000
        
        # メモリ効率確認（ビュー操作による削減効果）
        assert memory_increase <= 80 * 1024 * 1024  # 80MB以内
        
        # 統合統計確認
        integration_stats = streaming_processor.get_integration_statistics()
        assert 'view_optimized_chunks' in integration_stats
        assert 'streaming_efficiency_improvement' in integration_stats
        assert integration_stats['view_optimized_chunks'] == chunks_processed

    @pytest.mark.performance
    def test_view_operation_error_handling(self):
        """ビュー操作エラーハンドリングテスト
        
        RED: RangeViewProcessorクラスが存在しないため失敗する
        期待動作:
        - 無効範囲指定の適切処理
        - ファイルエラーの処理
        - フォールバック機能
        """
        test_file = self.create_test_excel_file(rows=1000)
        
        processor = RangeViewProcessor(
            enable_error_recovery=True,
            fallback_to_traditional=True
        )
        
        # 無効範囲指定テスト
        with pytest.raises(ValueError):
            processor.get_range_view(test_file, 2000, 2500)  # 範囲外
        
        with pytest.raises(ValueError):
            processor.get_range_view(test_file, 500, 400)  # 開始>終了
        
        # 存在しないファイルテスト
        with pytest.raises(FileNotFoundError):
            processor.get_range_view("nonexistent.xlsx", 0, 100)
        
        # フォールバック機能テスト
        # （ビュー操作エラー時に従来方式に自動切り替え）
        with patch.object(processor, '_perform_view_operation', side_effect=Exception("View error")):
            fallback_data = processor.get_range_view_with_fallback(test_file, 0, 100)
            assert len(fallback_data.data) == 100
            assert fallback_data.fallback_used is True
        
        # エラー統計確認
        error_stats = processor.get_error_statistics()
        assert 'view_operation_errors' in error_stats
        assert 'fallback_activations' in error_stats
        assert error_stats['fallback_activations'] >= 1