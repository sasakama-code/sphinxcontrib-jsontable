"""ストリーミングExcel読み込み基盤 - 最小限実装

TDD GREENフェーズ: テストを通すための最小限実装
Task 1.1.1: ストリーミング読み込み基盤実装
"""

import gc
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Union

import pandas as pd
import psutil


@dataclass
class ChunkData:
    """チャンクデータ構造."""
    data: List[Dict[str, Any]]
    chunk_id: int
    start_row: int
    end_row: int


class StreamingExcelReader:
    """ストリーミングExcel読み込み基盤
    
    大容量Excelファイルをメモリ効率的にチャンク単位で読み込む。
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        memory_limit_mb: int = 100,
        enable_monitoring: bool = False
    ):
        """初期化
        
        Args:
            chunk_size: チャンクサイズ（行数）
            memory_limit_mb: メモリ制限（MB）
            enable_monitoring: パフォーマンス監視有効化
        """
        self.chunk_size = chunk_size
        self.memory_limit_mb = memory_limit_mb
        self.enable_monitoring = enable_monitoring
        
        # パフォーマンス監視用
        self._metrics = {
            'total_processing_time': 0.0,
            'average_chunk_time': 0.0,
            'peak_memory_usage': 0,
            'throughput_rows_per_second': 0.0,
            'total_rows_processed': 0
        }
        self._start_time = None
        self._chunk_times = []

    def configure(self, chunk_size: int = None, memory_limit_mb: int = None):
        """設定変更
        
        Args:
            chunk_size: 新しいチャンクサイズ
            memory_limit_mb: 新しいメモリ制限
        """
        if chunk_size is not None:
            self.chunk_size = chunk_size
        if memory_limit_mb is not None:
            self.memory_limit_mb = memory_limit_mb

    def get_memory_usage(self) -> int:
        """現在のメモリ使用量取得（バイト）
        
        Returns:
            メモリ使用量（バイト）
        """
        process = psutil.Process()
        return process.memory_info().rss

    def get_performance_metrics(self) -> Dict[str, float]:
        """パフォーマンスメトリクス取得
        
        Returns:
            パフォーマンス指標辞書
        """
        return self._metrics.copy()

    def read_chunks(self, file_path: Union[str, Path]) -> Iterator[ChunkData]:
        """ファイルをチャンク単位で読み込み
        
        Args:
            file_path: Excelファイルパス
            
        Yields:
            ChunkData: チャンクデータ
            
        Raises:
            FileNotFoundError: ファイルが存在しない
            MemoryError: メモリ制限超過
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if self.enable_monitoring:
            self._start_time = time.perf_counter()
        
        # 初期メモリ使用量記録（相対的制限のため）
        initial_memory = self.get_memory_usage()
        memory_limit_bytes = self.memory_limit_mb * 1024 * 1024
        
        try:
            # Excelファイル全体読み込み（最小限実装）
            df = pd.read_excel(file_path)
            total_rows = len(df)
            
            # ファイル読み込み後のメモリ使用量確認
            post_load_memory = self.get_memory_usage()
            memory_increase = post_load_memory - initial_memory
            
            # メモリ制限チェック（相対的増加量）
            if memory_increase > memory_limit_bytes:
                raise MemoryError(f"File loading memory increase {memory_increase} exceeds limit {memory_limit_bytes}")
            
            chunk_id = 0
            for start_idx in range(0, total_rows, self.chunk_size):
                chunk_start_time = time.perf_counter() if self.enable_monitoring else None
                
                end_idx = min(start_idx + self.chunk_size, total_rows)
                chunk_df = df.iloc[start_idx:end_idx]
                
                # DataFrameを辞書リストに変換
                chunk_data = chunk_df.to_dict('records')
                
                # メモリ使用量チェック（相対的増加量）
                current_memory = self.get_memory_usage()
                current_increase = current_memory - initial_memory
                if current_increase > memory_limit_bytes:
                    raise MemoryError(f"Memory increase {current_increase} exceeds limit {memory_limit_bytes}")
                
                # パフォーマンス監視
                if self.enable_monitoring:
                    chunk_time = time.perf_counter() - chunk_start_time
                    self._chunk_times.append(chunk_time)
                    self._metrics['peak_memory_usage'] = max(
                        self._metrics['peak_memory_usage'], 
                        current_memory
                    )
                
                yield ChunkData(
                    data=chunk_data,
                    chunk_id=chunk_id,
                    start_row=start_idx,
                    end_row=end_idx - 1
                )
                
                chunk_id += 1
                
                # ガベージコレクション実行
                gc.collect()
            
            # 最終メトリクス計算
            if self.enable_monitoring:
                self._calculate_final_metrics(total_rows)
                
        except Exception as e:
            if isinstance(e, (FileNotFoundError, MemoryError)):
                raise
            raise RuntimeError(f"Error reading Excel file: {e}") from e

    def _calculate_final_metrics(self, total_rows: int):
        """最終パフォーマンスメトリクス計算
        
        Args:
            total_rows: 処理した総行数
        """
        if self._start_time:
            total_time = time.perf_counter() - self._start_time
            self._metrics['total_processing_time'] = total_time
            self._metrics['total_rows_processed'] = total_rows
            
            if total_time > 0:
                self._metrics['throughput_rows_per_second'] = total_rows / total_time
            
            if self._chunk_times:
                self._metrics['average_chunk_time'] = sum(self._chunk_times) / len(self._chunk_times)

    def close(self):
        """リソースクリーンアップ
        
        現在の実装では特別なクリーンアップは不要だが、
        インターフェース互換性のために提供。
        """
        pass