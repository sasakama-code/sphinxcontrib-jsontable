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

    def create_test_excel_file(self, rows: int = 100, filename: str = "test.xlsx") -> Path:
        """テスト用Excelファイル作成."""
        file_path = self.temp_dir / filename
        
        # テストデータ生成
        data = {
            'ID': [f"ID{i:06d}" for i in range(rows)],
            'Name': [f"Name{i}" for i in range(rows)], 
            'Value': [i * 100 for i in range(rows)],
            'Category': [f"Category{i % 10}" for i in range(rows)]
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
            chunk_size=1000,
            memory_limit_mb=50,
            enable_monitoring=True
        )
        
        # 基本属性確認
        assert reader.chunk_size == 1000
        assert reader.memory_limit_mb == 50
        assert reader.enable_monitoring is True
        assert hasattr(reader, 'read_chunks')
        assert hasattr(reader, 'get_memory_usage')
        assert hasattr(reader, 'get_performance_metrics')

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
            chunk_size=200,
            memory_limit_mb=20,
            enable_monitoring=True
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
        assert final_memory_increase <= initial_memory * 0.1  # 初期メモリの10%以内の増加許容

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
            
            assert streaming_row['ID'] == traditional_row['ID']
            assert streaming_row['Name'] == traditional_row['Name']
            assert streaming_row['Value'] == traditional_row['Value']
            assert streaming_row['Category'] == traditional_row['Category']

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
        
        reader = StreamingExcelReader(
            chunk_size=100,
            enable_monitoring=True
        )
        
        # 監視付き処理実行
        for _chunk in reader.read_chunks(test_file):
            pass  # 処理実行のみ
        
        # パフォーマンスメトリクス取得
        metrics = reader.get_performance_metrics()
        
        # 必要な指標確認
        assert 'total_processing_time' in metrics
        assert 'average_chunk_time' in metrics
        assert 'peak_memory_usage' in metrics
        assert 'throughput_rows_per_second' in metrics
        assert 'total_rows_processed' in metrics
        
        # 合理的な値確認
        assert metrics['total_processing_time'] > 0
        assert metrics['total_rows_processed'] == 800
        assert metrics['throughput_rows_per_second'] > 0

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
            memory_limit_mb=1  # 非常に小さい制限
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
        assert hasattr(reader, 'read_chunks')
        assert hasattr(reader, 'get_memory_usage')
        assert hasattr(reader, 'get_performance_metrics')
        assert hasattr(reader, 'close')
        
        # 設定変更可能性確認
        reader.configure(chunk_size=500, memory_limit_mb=100)
        assert reader.chunk_size == 500
        assert reader.memory_limit_mb == 100