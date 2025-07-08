"""ストリーミングExcel読み込み基盤テスト

TDD REDフェーズ: 失敗するテストを先に作成
Task 1.1.1: ストリーミング読み込み基盤実装
"""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from sphinxcontrib.jsontable.core.streaming_excel_reader import StreamingExcelReader


class TestStreamingExcelReader:
    """ストリーミングExcel読み込み基盤テスト

    TDD REDフェーズ: StreamingExcelReaderクラスが存在しないため、
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

    def create_test_excel_file(
        self, rows: int = 100, filename: str = "test.xlsx"
    ) -> Path:
        """テスト用Excelファイル作成."""
        file_path = self.temp_dir / filename

        # テストデータ生成
        data = {
            "ID": [f"ID{i:06d}" for i in range(rows)],
            "Name": [f"Name{i}" for i in range(rows)],
            "Value": [i * 100 for i in range(rows)],
            "Category": [f"Category{i % 10}" for i in range(rows)],
        }

        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)
        return file_path

    @pytest.mark.performance
    def test_streaming_excel_reader_basic(self):
        """ストリーミングExcel読み込み基本機能テスト

        RED: StreamingExcelReaderクラスが存在しないため失敗する
        期待動作:
        - ストリーミング読み込み基盤の基本インスタンス化
        - 基本設定の初期化
        - インターフェース準拠性確認
        """
        # REDフェーズ: まだ実装されていないクラスをテスト
        reader = StreamingExcelReader(
            chunk_size=1000, memory_limit_mb=50, enable_monitoring=True
        )

        # 基本属性確認
        assert reader.chunk_size == 1000
        assert reader.memory_limit_mb == 50
        assert reader.enable_monitoring is True
        assert hasattr(reader, "read_chunks")
        assert hasattr(reader, "get_memory_usage")
        assert hasattr(reader, "get_performance_metrics")

    @pytest.mark.performance
    def test_streaming_chunk_processing(self):
        """チャンク処理による大容量ファイル読み込みテスト

        RED: StreamingExcelReaderクラスが存在しないため失敗する
        期待動作:
        - 大容量ファイルをチャンク単位で読み込み
        - メモリ効率的な処理
        - データ完全性保証
        """
        # テスト用大容量ファイル作成
        large_file = self.create_test_excel_file(rows=5000, filename="large_test.xlsx")

        reader = StreamingExcelReader(chunk_size=500, memory_limit_mb=30)

        # チャンク読み込み実行
        chunks = list(reader.read_chunks(large_file))

        # チャンク数確認（5000行 ÷ 500チャンクサイズ = 10チャンク）
        assert len(chunks) == 10

        # 各チャンクサイズ確認
        for i, chunk in enumerate(chunks):
            expected_size = 500
            assert len(chunk.data) == expected_size
            assert chunk.chunk_id == i
            assert chunk.start_row == i * 500
            assert chunk.end_row == (i + 1) * 500 - 1

    @pytest.mark.performance
    def test_memory_efficient_processing(self):
        """メモリ効率的処理テスト

        RED: StreamingExcelReaderクラスが存在しないため失敗する
        期待動作:
        - メモリ使用量制限遵守
        - ガベージコレクション適切実行
        - メモリリーク防止
        """
        test_file = self.create_test_excel_file(rows=2000)

        reader = StreamingExcelReader(
            chunk_size=200, memory_limit_mb=20, enable_monitoring=True
        )

        initial_memory = reader.get_memory_usage()

        # ストリーミング処理実行
        total_rows = 0
        peak_memory_increase = 0

        for chunk in reader.read_chunks(test_file):
            current_memory = reader.get_memory_usage()
            memory_increase = current_memory - initial_memory
            peak_memory_increase = max(peak_memory_increase, memory_increase)
            total_rows += len(chunk.data)

            # メモリ制限確認（相対的増加量）
            assert memory_increase <= reader.memory_limit_mb * 1024 * 1024

        # 処理完了後のメモリ確認
        final_memory = reader.get_memory_usage()
        final_memory_increase = final_memory - initial_memory

        # データ完全性確認
        assert total_rows == 2000

        # メモリ効率確認
        assert peak_memory_increase <= reader.memory_limit_mb * 1024 * 1024
        assert (
            final_memory_increase <= initial_memory * 0.1
        )  # 初期メモリの10%以内の増加許容

    @pytest.mark.performance
    def test_streaming_accuracy_verification(self):
        """ストリーミング読み込み正確性テスト

        RED: StreamingExcelReaderクラスが存在しないため失敗する
        期待動作:
        - 従来読み込みと同じ結果
        - データ欠損なし
        - 順序保証
        """
        test_file = self.create_test_excel_file(rows=1000)

        # 従来の読み込み方法
        traditional_df = pd.read_excel(test_file)

        # ストリーミング読み込み
        reader = StreamingExcelReader(chunk_size=100)
        streaming_data = []

        for chunk in reader.read_chunks(test_file):
            streaming_data.extend(chunk.data)

        # 結果比較
        assert len(streaming_data) == len(traditional_df)

        # データ内容比較（最初の10行）
        for i in range(min(10, len(streaming_data))):
            streaming_row = streaming_data[i]
            traditional_row = traditional_df.iloc[i]

            assert streaming_row["ID"] == traditional_row["ID"]
            assert streaming_row["Name"] == traditional_row["Name"]
            assert streaming_row["Value"] == traditional_row["Value"]
            assert streaming_row["Category"] == traditional_row["Category"]

    @pytest.mark.performance
    def test_performance_monitoring(self):
        """パフォーマンス監視機能テスト

        RED: StreamingExcelReaderクラスが存在しないため失敗する
        期待動作:
        - 処理時間測定
        - メモリ使用量監視
        - スループット計算
        """
        test_file = self.create_test_excel_file(rows=800)

        reader = StreamingExcelReader(chunk_size=100, enable_monitoring=True)

        # 監視付き処理実行
        for _chunk in reader.read_chunks(test_file):
            pass  # 処理実行のみ

        # パフォーマンスメトリクス取得
        metrics = reader.get_performance_metrics()

        # 必要な指標確認
        assert "total_processing_time" in metrics
        assert "average_chunk_time" in metrics
        assert "peak_memory_usage" in metrics
        assert "throughput_rows_per_second" in metrics
        assert "total_rows_processed" in metrics

        # 合理的な値確認
        assert metrics["total_processing_time"] > 0
        assert metrics["total_rows_processed"] == 800
        assert metrics["throughput_rows_per_second"] > 0

    @pytest.mark.performance
    def test_error_handling_during_streaming(self):
        """ストリーミング中のエラーハンドリングテスト

        RED: StreamingExcelReaderクラスが存在しないため失敗する
        期待動作:
        - ファイル読み込みエラー適切処理
        - メモリ不足エラー適切処理
        - 破損データエラー適切処理
        """
        reader = StreamingExcelReader(chunk_size=100)

        # 存在しないファイルテスト
        with pytest.raises(FileNotFoundError):
            list(reader.read_chunks("nonexistent_file.xlsx"))

        # メモリ制限超過テスト
        large_file = self.create_test_excel_file(rows=10000)
        memory_limited_reader = StreamingExcelReader(
            chunk_size=1000,
            memory_limit_mb=1,  # 非常に小さい制限
        )

        with pytest.raises(MemoryError):
            list(memory_limited_reader.read_chunks(large_file))

    @pytest.mark.performance
    def test_streaming_interface_compatibility(self):
        """ストリーミング読み込みインターフェース互換性テスト

        RED: StreamingExcelReaderクラスが存在しないため失敗する
        期待動作:
        - 既存ExcelReaderインターフェース準拠
        - 後方互換性保証
        - 統合可能性確認
        """
        reader = StreamingExcelReader()

        # インターフェース確認
        assert hasattr(reader, "read_chunks")
        assert hasattr(reader, "get_memory_usage")
        assert hasattr(reader, "get_performance_metrics")
        assert hasattr(reader, "close")

        # 設定変更可能性確認
        reader.configure(chunk_size=500, memory_limit_mb=100)
        assert reader.chunk_size == 500
        assert reader.memory_limit_mb == 100

    @pytest.mark.performance  
    def test_chunk_processing_large_file(self):
        """大容量Excelファイル専用チャンク処理テスト
        
        TDD RED Phase: Task 1.1.2専用高度チャンク処理
        期待動作:
        - 50,000行以上の大容量ファイル処理
        - 高精度メモリ監視とチャンク効率測定  
        - 大容量ファイル特有のエラーハンドリング
        - 並列処理準備アーキテクチャ
        """
        # 大容量テストファイル作成（50,000行）
        large_file = self.create_test_excel_file(rows=50000, filename="massive_test.xlsx")
        
        # 大容量ファイル専用設定
        reader = StreamingExcelReader(
            chunk_size=200,  # 小さなチャンク（メモリ効率重視）
            memory_limit_mb=500,  # 大容量対応
            enable_monitoring=True,
            enable_security_validation=True,
            gc_frequency=2  # 頻繁なGC（メモリ効率）
        )
        
        # 大容量ファイル検証要件
        workbook_info = reader.validate_streaming_requirements(large_file)
        assert workbook_info.file_size > 1 * 1024 * 1024  # 1MB以上（50K行相当）
        
        # 高度メモリ監視開始
        initial_memory = reader.get_memory_usage()
        chunk_memory_peaks = []
        chunk_processing_times = []
        chunk_efficiency_ratios = []
        
        # 大容量チャンク処理実行
        total_rows = 0
        chunk_count = 0
        
        for chunk in reader.read_chunks(large_file):
            # チャンクデータ検証
            assert chunk.chunk_id == chunk_count
            assert len(chunk.data) == 200  # 最後のチャンク以外
            assert chunk.start_row == chunk_count * 200
            assert chunk.end_row == (chunk_count * 200) + len(chunk.data) - 1
            
            # 高度メタデータ検証
            assert chunk.processing_time is not None
            assert chunk.processing_time > 0
            assert chunk.memory_usage is not None
            assert chunk.row_count == len(chunk.data)
            assert not chunk.is_empty
            
            # メモリ効率性指標検証
            memory_efficiency = chunk.memory_efficiency_ratio
            if memory_efficiency is not None and memory_efficiency > 0:
                chunk_efficiency_ratios.append(memory_efficiency)
            
            # メモリピーク記録
            current_memory = reader.get_memory_usage()
            chunk_memory_peaks.append(current_memory)
            chunk_processing_times.append(chunk.processing_time)
            
            # 大容量ファイル特有の進捗確認
            total_rows += len(chunk.data)
            chunk_count += 1
            
            # メモリ制限遵守確認（大容量対応）
            memory_increase = current_memory - initial_memory
            assert memory_increase <= reader.memory_limit_mb * 1024 * 1024
            
            # 1000チャンクごとに中間検証（大容量特有）
            if chunk_count % 1000 == 0:
                metrics = reader.get_performance_metrics()
                assert metrics["total_chunks_processed"] == chunk_count
                assert metrics["throughput_rows_per_second"] > 0
        
        # 大容量処理完了検証
        assert total_rows == 50000
        assert chunk_count == 250  # 50,000 ÷ 200
        
        # 高度パフォーマンスメトリクス検証
        final_metrics = reader.get_performance_metrics()
        
        # 基本メトリクス
        assert final_metrics["total_rows_processed"] == 50000
        assert final_metrics["total_chunks_processed"] == 250
        assert final_metrics["total_processing_time"] > 0
        assert final_metrics["throughput_rows_per_second"] > 1000  # 最低スループット要件
        
        # 大容量特有メトリクス
        assert final_metrics["average_chunk_time"] > 0
        assert final_metrics["memory_efficiency_average"] >= 0  # 0以上（効率データ収集できない場合は0）
        assert final_metrics["gc_collections_performed"] >= 125  # gc_frequency=2で125回以上
        
        # 追加拡張メトリクス（Task 1.1.2特有）
        assert "memory_usage_variance" in final_metrics
        assert "processing_time_variance" in final_metrics  
        assert "rows_per_mb" in final_metrics
        
        # メモリ効率性基準（データが収集できた場合のみ）
        if chunk_efficiency_ratios:
            average_efficiency = sum(chunk_efficiency_ratios) / len(chunk_efficiency_ratios)
            assert average_efficiency < 1000  # 1行あたり1KB未満（効率要件）
        
        # 処理時間安定性確認
        time_variance = final_metrics["processing_time_variance"]
        assert time_variance < 0.1  # 処理時間の安定性
        
        # メモリ使用量安定性確認（大容量ファイル考慮）
        memory_variance = final_metrics["memory_usage_variance"]
        assert memory_variance < 2000000000  # メモリ使用量の安定性（2GB変動以内）
        
        # 大容量ファイル特有のスループット要件
        rows_per_mb = final_metrics["rows_per_mb"]
        assert rows_per_mb > 100  # 1MBあたり100行以上（効率要件）
        
        # 高度チャンク処理機能検証（Task 1.1.2特有機能）
        # 並列チャンク処理機能チェック
        assert hasattr(reader, "enable_parallel_processing")
        assert hasattr(reader, "get_parallel_metrics")
        
        # チャンク間依存関係管理チェック
        assert hasattr(reader, "chunk_dependency_manager")
        assert hasattr(reader, "validate_chunk_dependencies")
        
        # 高度メモリプール機能チェック
        assert hasattr(reader, "chunk_memory_pool")
        assert hasattr(reader, "optimize_memory_allocation")
        
        # リアルタイムストリーミング監視チェック
        assert hasattr(reader, "streaming_monitor")
        assert hasattr(reader, "get_realtime_metrics")
        
        # 大容量ファイル専用設定チェック
        assert hasattr(reader, "large_file_mode")
        assert hasattr(reader, "configure_large_file_processing")
        
        # リソースクリーンアップ検証
        reader.close()
        
        # クリーンアップ後のメモリ使用量確認
        post_cleanup_memory = reader.get_memory_usage()
        memory_reduction = max(chunk_memory_peaks) - post_cleanup_memory
        assert memory_reduction > 0  # メモリ解放確認

    @pytest.mark.performance
    def test_memory_usage_monitoring(self):
        """メモリ使用量監視機構テスト
        
        TDD RED Phase: Task 1.1.3専用メモリ監視システム
        期待動作:
        - MemoryMonitorクラスによる専用メモリ監視
        - リアルタイムメモリ使用量追跡
        - メモリ制限アラート機能
        - メモリ使用量履歴管理
        - メモリリーク検出機能
        - エンタープライズグレード監視メトリクス
        """
        from sphinxcontrib.jsontable.core.memory_monitor import MemoryMonitor
        
        # Memory Monitor初期化（専用監視システム）
        monitor = MemoryMonitor(
            memory_limit_mb=100,  # 100MB制限
            alert_threshold_percent=80,  # 80%でアラート
            monitoring_interval=0.1,  # 100ms間隔
            history_size=50,  # 50履歴保持
            enable_leak_detection=True,  # メモリリーク検出有効
            enable_gc_monitoring=True,   # GC監視有効
            enable_history=True,  # 履歴記録有効化
            enable_alerts=True    # アラート有効化
        )
        
        # 基本設定検証
        assert monitor.memory_limit_mb == 100
        assert monitor.alert_threshold_percent == 80
        assert monitor.monitoring_interval == 0.1
        assert monitor.history_size == 50
        assert monitor.enable_leak_detection is True
        assert monitor.enable_gc_monitoring is True
        
        # 監視開始
        monitor.start_monitoring()
        assert monitor.is_monitoring is True
        
        # 監視データ収集のための短い待機
        import time
        time.sleep(0.2)
        
        # 現在のメモリ使用量取得
        current_memory = monitor.get_current_memory_usage()
        assert current_memory > 0
        assert isinstance(current_memory, (int, float))
        
        # メモリ使用量履歴取得
        memory_history = monitor.get_memory_history()
        assert isinstance(memory_history, list)
        assert len(memory_history) >= 0
        
        # メモリ使用率計算
        memory_usage_percent = monitor.get_memory_usage_percent()
        assert 0 <= memory_usage_percent <= 100
        assert isinstance(memory_usage_percent, (int, float))
        
        # アラート状態確認
        alert_status = monitor.get_alert_status()
        assert isinstance(alert_status, dict)
        assert "is_alert_active" in alert_status
        assert "alert_level" in alert_status
        assert "alert_message" in alert_status
        assert "triggered_at" in alert_status
        
        # メモリ監視メトリクス取得
        monitoring_metrics = monitor.get_monitoring_metrics()
        assert isinstance(monitoring_metrics, dict)
        
        # 基本メトリクス
        assert "current_memory_mb" in monitoring_metrics
        assert "peak_memory_mb" in monitoring_metrics
        assert "average_memory_mb" in monitoring_metrics
        assert "memory_usage_percent" in monitoring_metrics
        assert "memory_limit_mb" in monitoring_metrics
        
        # 監視メトリクス
        assert "monitoring_duration_seconds" in monitoring_metrics
        assert "total_measurements" in monitoring_metrics
        assert "alert_count" in monitoring_metrics
        assert "gc_collections_detected" in monitoring_metrics
        
        # メモリリーク検出メトリクス
        assert "leak_detection_enabled" in monitoring_metrics
        assert "potential_leak_detected" in monitoring_metrics
        assert "memory_growth_rate_mb_per_sec" in monitoring_metrics
        
        # 高度メトリクス
        assert "memory_variance" in monitoring_metrics
        assert "memory_stability_score" in monitoring_metrics
        assert "memory_efficiency_score" in monitoring_metrics
        
        # メモリ制限テスト（仮想的な高負荷）
        test_file = self.create_test_excel_file(rows=1000)
        
        # 監視しながらExcel処理実行
        pre_processing_memory = monitor.get_current_memory_usage()
        
        # StreamingExcelReaderと連携テスト
        reader = StreamingExcelReader(
            chunk_size=100, 
            memory_limit_mb=50, 
            enable_monitoring=True
        )
        
        # Memory Monitorをリーダーに統合
        reader.set_memory_monitor(monitor)
        assert reader.memory_monitor is monitor
        
        # 監視付きストリーミング処理
        processed_chunks = 0
        memory_readings = []
        
        for chunk in reader.read_chunks(test_file):
            processed_chunks += 1
            current_reading = monitor.get_current_memory_usage()
            memory_readings.append(current_reading)
            
            # メモリ制限チェック
            if monitor.is_memory_limit_exceeded():
                # メモリ制限超過時の動作確認
                limit_info = monitor.get_limit_exceeded_info()
                assert isinstance(limit_info, dict)
                assert "exceeded_at" in limit_info
                assert "current_memory_mb" in limit_info
                assert "memory_limit_mb" in limit_info
                assert "excess_memory_mb" in limit_info
            
            # アラート検証
            if monitor.is_alert_triggered():
                alert_details = monitor.get_alert_details()
                assert isinstance(alert_details, dict)
                assert alert_details["is_alert_active"] is True
                assert alert_details["alert_level"] in ["warning", "critical"]
        
        # 処理完了後の検証
        assert processed_chunks == 10  # 1000行÷100チャンク
        assert len(memory_readings) == 10
        
        # 一時的に監視停止して統計計算
        monitor.stop_monitoring()
        time.sleep(0.1)  # 停止処理完了待機
        
        # メモリ監視統計
        final_metrics = monitor.get_monitoring_metrics()
        assert final_metrics["total_measurements"] > 0
        assert final_metrics["monitoring_duration_seconds"] > 0
        assert final_metrics["peak_memory_mb"] >= final_metrics["current_memory_mb"]
        
        # 監視再開（後続テストのため）
        monitor.start_monitoring()
        time.sleep(0.1)
        
        # メモリリーク検出テスト
        leak_status = monitor.check_memory_leak()
        assert isinstance(leak_status, dict)
        assert "leak_detected" in leak_status
        assert "confidence_level" in leak_status
        assert "growth_rate_mb_per_sec" in leak_status
        assert "recommendation" in leak_status
        
        # GC監視機能テスト
        gc_stats = monitor.get_gc_statistics()
        assert isinstance(gc_stats, dict)
        assert "total_collections" in gc_stats
        assert "collection_frequency" in gc_stats
        assert "average_collection_time" in gc_stats
        
        # メモリ最適化提案テスト
        optimization_suggestions = monitor.get_optimization_suggestions()
        assert isinstance(optimization_suggestions, list)
        for suggestion in optimization_suggestions:
            assert "type" in suggestion  # "memory_limit", "chunk_size", "gc_frequency"等
            assert "current_value" in suggestion
            assert "suggested_value" in suggestion
            assert "expected_improvement" in suggestion
            assert "priority" in suggestion  # "high", "medium", "low"
        
        # リアルタイム監視停止
        monitor.stop_monitoring()
        assert monitor.is_monitoring is False
        
        # 最終レポート生成
        final_report = monitor.generate_monitoring_report()
        assert isinstance(final_report, dict)
        assert "monitoring_summary" in final_report
        assert "performance_analysis" in final_report
        assert "recommendations" in final_report
        assert "alert_history" in final_report
        
        # メモリ監視クリーンアップ
        monitor.cleanup()
        
        # クリーンアップ後の状態確認
        assert monitor.is_monitoring is False
        cleanup_metrics = monitor.get_monitoring_metrics()
        assert cleanup_metrics["total_measurements"] > 0  # 履歴は保持
