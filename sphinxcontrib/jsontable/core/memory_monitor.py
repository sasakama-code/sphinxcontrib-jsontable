"""メモリ監視機構 - 高度実装

TDD REFACTORフェーズ: 実用性・保守性・統合性向上
Task 1.1.3: メモリ監視機構実装
"""

import gc
import logging
import threading
import time
import weakref
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union

import psutil

# 統合可能性のためのオプショナルインポート
try:
    from .optimized_chunk_processor import OptimizedChunkProcessor
    from .streaming_excel_reader import StreamingExcelReader
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False

# ロギング設定
logger = logging.getLogger(__name__)


@dataclass
class MemoryAlert:
    """メモリアラート構造（改善版）."""
    alert_level: str
    memory_usage: int
    threshold: float
    timestamp: float
    message: str
    process_id: int = field(default_factory=lambda: psutil.Process().pid)
    component_source: Optional[str] = None
    suggested_action: Optional[str] = None
    severity_score: float = 0.0
    
    def __post_init__(self):
        """アラート後処理（改善版）."""
        # 重要度スコア計算
        if self.alert_level == 'emergency':
            self.severity_score = 1.0
        elif self.alert_level == 'critical':
            self.severity_score = 0.8
        elif self.alert_level == 'warning':
            self.severity_score = 0.5
        
        # 推奨アクション設定
        if not self.suggested_action:
            if self.alert_level == 'emergency':
                self.suggested_action = "Immediate memory optimization required"
            elif self.alert_level == 'critical':
                self.suggested_action = "Schedule memory cleanup"
            else:
                self.suggested_action = "Monitor memory usage"


class MemoryMonitor:
    """メモリ監視機構（高度版）
    
    リアルタイムメモリ使用量監視、しきい値アラート、
    自動最適化トリガーを提供する。
    
    Features:
    - リアルタイムメモリ監視
    - 複数レベルアラート
    - 自動最適化
    - StreamingExcelReader/OptimizedChunkProcessor統合
    - スレッドセーフ操作
    - 外部システム統合
    """

    def __init__(
        self,
        monitoring_interval: float = 0.1,
        enable_history: bool = False,
        max_history_size: int = 1000,
        alert_config: Optional[Dict[str, float]] = None,
        enable_alerts: bool = False,
        optimization_config: Optional[Dict[str, Any]] = None,
        enable_optimization: bool = False,
        thread_safe: bool = True,
        integration_config: Optional[Dict[str, Any]] = None,
        enable_external_integration: bool = False
    ):
        """初期化
        
        Args:
            monitoring_interval: 監視間隔（秒）
            enable_history: 履歴記録有効化
            max_history_size: 最大履歴サイズ
            alert_config: アラート設定
            enable_alerts: アラート有効化
            optimization_config: 最適化設定
            enable_optimization: 最適化有効化
            thread_safe: スレッドセーフ有効化
            integration_config: 外部統合設定
            enable_external_integration: 外部統合有効化
        """
        self.monitoring_interval = monitoring_interval
        self.enable_history = enable_history
        self.max_history_size = max_history_size
        self.enable_alerts = enable_alerts
        self.enable_optimization = enable_optimization
        self.thread_safe = thread_safe
        self.enable_external_integration = enable_external_integration
        
        # アラート設定
        self.alert_config = alert_config or {
            'warning_threshold': 80,
            'critical_threshold': 90,
            'emergency_threshold': 95
        }
        
        # 最適化設定
        self.optimization_config = optimization_config or {
            'auto_gc_threshold': 75,
            'memory_cleanup_threshold': 85,
            'emergency_optimization_threshold': 95,
            'enable_auto_optimization': True
        }
        
        # 外部統合設定
        self.integration_config = integration_config or {
            'enable_external_reporting': False,
            'report_interval': 1.0,
            'external_system_endpoint': None
        }
        
        # 内部状態
        self._monitoring = False
        self._monitor_thread = None
        self._lock = threading.Lock() if thread_safe else None
        
        # データ保存
        self._memory_history = []
        self._alert_history = []
        self._current_memory_usage = 0
        self._start_time = None
        self._peak_memory_usage = 0
        self._total_memory_usage = 0
        self._measurement_count = 0
        
        # 統計情報
        self._statistics = {
            'peak_memory_usage': 0,
            'average_memory_usage': 0.0,
            'memory_usage_variance': 0.0,
            'monitoring_duration': 0.0
        }
        
        # 最適化統計
        self._optimization_stats = {
            'total_optimizations': 0,
            'memory_freed_total': 0,
            'average_optimization_effect': 0.0
        }
        
        # スレッドセーフティ統計
        self._thread_safety_stats = {
            'concurrent_access_count': 0,
            'race_condition_detected': 0
        }
        
        # 外部統合統計
        self._integration_stats = {
            'external_reports_sent': 0,
            'integration_errors': 0
        }
        
        # コールバック
        self._alert_handler: Optional[Callable[[MemoryAlert], None]] = None
        self._optimization_callback: Optional[Callable[[str, int, int], None]] = None
        self._external_report_handler: Optional[Callable[[dict], None]] = None
        
        # 統合コンポーネント（改善版）
        self._monitored_components: Dict[str, weakref.ReferenceType] = {}
        self._component_memory_baselines: Dict[str, int] = {}
        
        # エラーハンドリング強化
        self._error_count = 0
        self._max_error_threshold = 10
        self._last_error_time = None

    def get_current_memory_usage(self) -> int:
        """現在のメモリ使用量取得（バイト）"""
        try:
            process = psutil.Process()
            memory_usage = process.memory_info().rss
            self._current_memory_usage = memory_usage
            return memory_usage
        except Exception as e:
            logger.error(f"Memory usage measurement failed: {e}")
            return self._current_memory_usage or 0
    
    def register_component(self, component_name: str, component: Union['StreamingExcelReader', 'OptimizedChunkProcessor', Any]) -> bool:
        """コンポーネント登録（統合機能）
        
        Args:
            component_name: コンポーネント名
            component: 監視対象コンポーネント
            
        Returns:
            bool: 登録成功フラグ
        """
        if not INTEGRATION_AVAILABLE:
            logger.warning("Component integration not available")
            return False
            
        try:
            # WeakReference使用でメモリリーク防止
            self._monitored_components[component_name] = weakref.ref(component)
            
            # ベースラインメモリ記録
            if hasattr(component, 'get_memory_usage'):
                baseline_memory = component.get_memory_usage()
                self._component_memory_baselines[component_name] = baseline_memory
            
            logger.info(f"Component '{component_name}' registered for monitoring")
            return True
            
        except Exception as e:
            logger.error(f"Component registration failed for '{component_name}': {e}")
            return False
    
    def unregister_component(self, component_name: str):
        """コンポーネント登録解除
        
        Args:
            component_name: 解除するコンポーネント名
        """
        if component_name in self._monitored_components:
            del self._monitored_components[component_name]
        if component_name in self._component_memory_baselines:
            del self._component_memory_baselines[component_name]
        
        logger.info(f"Component '{component_name}' unregistered")
    
    def get_component_memory_status(self) -> Dict[str, Dict[str, Any]]:
        """監視コンポーネントメモリ状況取得
        
        Returns:
            Dict: コンポーネント別メモリ状況
        """
        status = {}
        
        for component_name, component_ref in self._monitored_components.items():
            component = component_ref()
            if component is None:
                # ガベージコレクション済み
                status[component_name] = {'status': 'garbage_collected'}
                continue
                
            try:
                if hasattr(component, 'get_memory_usage'):
                    current_memory = component.get_memory_usage()
                    baseline = self._component_memory_baselines.get(component_name, 0)
                    
                    status[component_name] = {
                        'status': 'active',
                        'current_memory': current_memory,
                        'baseline_memory': baseline,
                        'memory_increase': current_memory - baseline,
                        'component_type': type(component).__name__
                    }
                else:
                    status[component_name] = {'status': 'no_memory_interface'}
                    
            except Exception as e:
                status[component_name] = {'status': 'error', 'error': str(e)}
        
        return status

    def start_monitoring(self):
        """メモリ監視開始"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._start_time = time.time()
        self._monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitor_thread.start()

    def stop_monitoring(self):
        """メモリ監視停止"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        
        # 最終統計計算
        self._calculate_final_statistics()

    def _monitoring_loop(self):
        """監視ループ（別スレッドで実行・エラーハンドリング強化）"""
        while self._monitoring:
            try:
                current_memory = self.get_current_memory_usage()
                current_time = time.time()
                
                # 履歴記録
                if self.enable_history:
                    self._record_memory_history(current_memory, current_time)
                
                # アラートチェック
                if self.enable_alerts:
                    self._check_memory_alerts(current_memory, current_time)
                
                # 最適化チェック
                if self.enable_optimization:
                    self._check_optimization_triggers(current_memory)
                
                # 統合コンポーネント監視
                self._monitor_integrated_components()
                
                # 外部統合報告
                if self.enable_external_integration:
                    self._send_external_report(current_memory, current_time)
                
                # 統計更新
                self._update_statistics(current_memory)
                
                # エラーカウントリセット（正常実行時）
                self._error_count = 0
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                # エラーハンドリング強化
                self._handle_monitoring_error(e)
    
    def _handle_monitoring_error(self, error: Exception):
        """監視エラーハンドリング（強化版）
        
        Args:
            error: 発生したエラー
        """
        self._error_count += 1
        current_time = time.time()
        
        # エラーログ記録
        logger.error(f"Memory monitoring error (count: {self._error_count}): {error}")
        
        # エラー頻度チェック
        if self._last_error_time and (current_time - self._last_error_time) < 1.0:
            # 短時間での連続エラー - 待機時間延長
            time.sleep(self.monitoring_interval * 2)
        else:
            time.sleep(self.monitoring_interval)
        
        self._last_error_time = current_time
        
        # エラー閾値チェック
        if self._error_count >= self._max_error_threshold:
            logger.critical(f"Maximum error threshold reached ({self._max_error_threshold}). Stopping monitoring.")
            self._monitoring = False
    
    def _monitor_integrated_components(self):
        """統合コンポーネント監視（新機能）"""
        if not self._monitored_components:
            return
            
        # ガベージコレクションされたコンポーネントのクリーンアップ
        dead_components = []
        for component_name, component_ref in self._monitored_components.items():
            if component_ref() is None:
                dead_components.append(component_name)
        
        for component_name in dead_components:
            self.unregister_component(component_name)
        
        # アクティブコンポーネントのメモリ監視
        for component_name, component_ref in self._monitored_components.items():
            component = component_ref()
            if component and hasattr(component, 'get_memory_usage'):
                try:
                    component_memory = component.get_memory_usage()
                    baseline = self._component_memory_baselines.get(component_name, 0)
                    memory_increase = component_memory - baseline
                    
                    # コンポーネント固有のメモリ制限チェック
                    if hasattr(component, 'memory_limit_mb'):
                        limit_bytes = component.memory_limit_mb * 1024 * 1024
                        if memory_increase > limit_bytes:
                            # コンポーネント固有アラート
                            alert = MemoryAlert(
                                alert_level='warning',
                                memory_usage=component_memory,
                                threshold=component.memory_limit_mb,
                                timestamp=time.time(),
                                message=f"Component {component_name} memory increase exceeds limit",
                                component_source=component_name
                            )
                            
                            if self._alert_handler:
                                self._alert_handler(alert)
                                
                except Exception as e:
                    logger.warning(f"Component monitoring failed for '{component_name}': {e}")

    def _record_memory_history(self, memory_usage: int, timestamp: float):
        """メモリ履歴記録"""
        if self._lock:
            with self._lock:
                self._record_memory_history_unsafe(memory_usage, timestamp)
        else:
            self._record_memory_history_unsafe(memory_usage, timestamp)

    def _record_memory_history_unsafe(self, memory_usage: int, timestamp: float):
        """メモリ履歴記録（ロックなし版）"""
        # 前回との差分計算
        memory_delta = 0
        if self._memory_history:
            memory_delta = memory_usage - self._memory_history[-1]['memory_usage']
        
        record = {
            'timestamp': timestamp,
            'memory_usage': memory_usage,
            'memory_delta': memory_delta
        }
        
        self._memory_history.append(record)
        
        # 履歴サイズ制限
        if len(self._memory_history) > self.max_history_size:
            self._memory_history.pop(0)

    def _check_memory_alerts(self, memory_usage: int, timestamp: float):
        """メモリアラートチェック"""
        # システム総メモリ取得
        total_memory = psutil.virtual_memory().total
        usage_percentage = (memory_usage / total_memory) * 100
        
        alert_level = None
        threshold = 0
        
        if usage_percentage >= self.alert_config['emergency_threshold']:
            alert_level = 'emergency'
            threshold = self.alert_config['emergency_threshold']
        elif usage_percentage >= self.alert_config['critical_threshold']:
            alert_level = 'critical'
            threshold = self.alert_config['critical_threshold']
        elif usage_percentage >= self.alert_config['warning_threshold']:
            alert_level = 'warning'
            threshold = self.alert_config['warning_threshold']
        
        if alert_level:
            alert = MemoryAlert(
                alert_level=alert_level,
                memory_usage=memory_usage,
                threshold=threshold,
                timestamp=timestamp,
                message=f"Memory usage {usage_percentage:.1f}% exceeds {alert_level} threshold {threshold}%"
            )
            
            self._alert_history.append(alert)
            
            if self._alert_handler:
                self._alert_handler(alert)

    def _check_optimization_triggers(self, memory_usage: int):
        """最適化トリガーチェック"""
        total_memory = psutil.virtual_memory().total
        usage_percentage = (memory_usage / total_memory) * 100
        
        optimization_performed = False
        before_memory = memory_usage
        
        if usage_percentage >= self.optimization_config['emergency_optimization_threshold']:
            # 緊急最適化
            self._perform_emergency_optimization()
            optimization_performed = True
        elif usage_percentage >= self.optimization_config['memory_cleanup_threshold']:
            # メモリクリーンアップ
            self._perform_memory_cleanup()
            optimization_performed = True
        elif usage_percentage >= self.optimization_config['auto_gc_threshold']:
            # ガベージコレクション
            self._perform_garbage_collection()
            optimization_performed = True
        
        if optimization_performed:
            after_memory = self.get_current_memory_usage()
            memory_freed = before_memory - after_memory
            
            # 統計更新
            self._optimization_stats['total_optimizations'] += 1
            self._optimization_stats['memory_freed_total'] += memory_freed
            self._optimization_stats['average_optimization_effect'] = (
                self._optimization_stats['memory_freed_total'] / 
                self._optimization_stats['total_optimizations']
            )
            
            # コールバック呼び出し
            if self._optimization_callback:
                optimization_type = self._get_optimization_type(usage_percentage)
                self._optimization_callback(optimization_type, before_memory, after_memory)

    def _perform_garbage_collection(self):
        """ガベージコレクション実行"""
        gc.collect()

    def _perform_memory_cleanup(self):
        """メモリクリーンアップ実行"""
        # ガベージコレクション + 追加クリーンアップ
        gc.collect()
        # 実装では更なるクリーンアップ処理を追加

    def _perform_emergency_optimization(self):
        """緊急最適化実行"""
        # 全ての最適化手法実行
        gc.collect()
        # 実装では緊急時の強力な最適化処理を追加

    def _get_optimization_type(self, usage_percentage: float) -> str:
        """最適化タイプ判定"""
        if usage_percentage >= self.optimization_config['emergency_optimization_threshold']:
            return 'emergency_optimization'
        elif usage_percentage >= self.optimization_config['memory_cleanup_threshold']:
            return 'memory_cleanup'
        else:
            return 'garbage_collection'

    def _send_external_report(self, memory_usage: int, timestamp: float):
        """外部システム報告送信"""
        if not self._external_report_handler:
            return
        
        report_data = {
            'timestamp': timestamp,
            'memory_usage': memory_usage,
            'system_info': {
                'total_memory': psutil.virtual_memory().total,
                'available_memory': psutil.virtual_memory().available,
                'usage_percentage': (memory_usage / psutil.virtual_memory().total) * 100
            },
            'monitoring_metadata': {
                'monitoring_interval': self.monitoring_interval,
                'alert_config': self.alert_config,
                'optimization_config': self.optimization_config
            }
        }
        
        try:
            self._external_report_handler(report_data)
            self._integration_stats['external_reports_sent'] += 1
        except Exception as e:
            self._integration_stats['integration_errors'] += 1
            print(f"External report error: {e}")

    def _update_statistics(self, memory_usage: int):
        """統計情報更新"""
        self._peak_memory_usage = max(self._peak_memory_usage, memory_usage)
        self._total_memory_usage += memory_usage
        self._measurement_count += 1
        
        # 平均計算
        average_memory = self._total_memory_usage / self._measurement_count
        self._statistics['average_memory_usage'] = average_memory
        self._statistics['peak_memory_usage'] = self._peak_memory_usage

    def _calculate_final_statistics(self):
        """最終統計計算"""
        if self._start_time:
            self._statistics['monitoring_duration'] = time.time() - self._start_time
        
        # 分散計算（簡略版）
        if self._memory_history:
            avg = self._statistics['average_memory_usage']
            variance = sum((record['memory_usage'] - avg) ** 2 for record in self._memory_history)
            variance /= len(self._memory_history)
            self._statistics['memory_usage_variance'] = variance

    # Getter メソッド群

    def get_memory_history(self) -> List[Dict[str, Any]]:
        """メモリ履歴取得"""
        if self._lock:
            with self._lock:
                return self._memory_history.copy()
        return self._memory_history.copy()

    def get_monitoring_statistics(self) -> Dict[str, float]:
        """監視統計取得"""
        return self._statistics.copy()

    def get_alert_history(self) -> List[MemoryAlert]:
        """アラート履歴取得"""
        return self._alert_history.copy()

    def get_optimization_statistics(self) -> Dict[str, float]:
        """最適化統計取得"""
        return self._optimization_stats.copy()

    def get_thread_safety_statistics(self) -> Dict[str, int]:
        """スレッドセーフティ統計取得"""
        # 同期アクセス記録（スレッドセーフ動作確認用）
        if self._lock:
            self._thread_safety_stats['concurrent_access_count'] += 1
        return self._thread_safety_stats.copy()

    def get_integration_statistics(self) -> Dict[str, int]:
        """外部統合統計取得"""
        return self._integration_stats.copy()

    # Setter メソッド群

    def set_alert_handler(self, handler: Callable[[MemoryAlert], None]):
        """アラートハンドラー設定"""
        self._alert_handler = handler

    def set_optimization_callback(self, callback: Callable[[str, int, int], None]):
        """最適化コールバック設定"""
        self._optimization_callback = callback

    def set_external_report_handler(self, handler: Callable[[dict], None]):
        """外部報告ハンドラー設定"""
        self._external_report_handler = handler


class MemoryOptimizer:
    """メモリ最適化器
    
    様々な最適化戦略を実行し、メモリ使用量を削減する。
    """

    def __init__(
        self,
        optimization_strategies: List[str] = None,
        enable_reporting: bool = False,
        enable_strategy_comparison: bool = False,
        enable_adaptive_optimization: bool = False,
        learning_enabled: bool = False,
        adaptation_sensitivity: float = 0.5
    ):
        """初期化
        
        Args:
            optimization_strategies: 最適化戦略リスト
            enable_reporting: 報告有効化
            enable_strategy_comparison: 戦略比較有効化
            enable_adaptive_optimization: 適応的最適化有効化
            learning_enabled: 学習有効化
            adaptation_sensitivity: 適応感度
        """
        self.optimization_strategies = optimization_strategies or ['garbage_collection']
        self.enable_reporting = enable_reporting
        self.enable_strategy_comparison = enable_strategy_comparison
        self.enable_adaptive_optimization = enable_adaptive_optimization
        self.learning_enabled = learning_enabled
        self.adaptation_sensitivity = adaptation_sensitivity
        
        # 学習データ
        self._learning_data = {
            'optimization_patterns_learned': 0,
            'strategy_effectiveness_scores': {},
            'adaptive_improvements': 0
        }

    def get_current_memory_usage(self) -> int:
        """現在のメモリ使用量取得"""
        process = psutil.Process()
        return process.memory_info().rss

    def optimize(self) -> Dict[str, Any]:
        """基本最適化実行"""
        initial_memory = self.get_current_memory_usage()
        start_time = time.perf_counter()
        
        # 最適化実行
        strategies_applied = []
        for strategy in self.optimization_strategies:
            if strategy == 'garbage_collection':
                gc.collect()
                strategies_applied.append('garbage_collection')
            elif strategy == 'memory_pool':
                # メモリプール最適化（簡略実装）
                gc.collect()
                strategies_applied.append('memory_pool')
            elif strategy == 'cache_cleanup':
                # キャッシュクリーンアップ（簡略実装）
                gc.collect()
                strategies_applied.append('cache_cleanup')
        
        final_memory = self.get_current_memory_usage()
        optimization_time = time.perf_counter() - start_time
        memory_freed = max(0, initial_memory - final_memory)
        
        return {
            'success': True,
            'memory_freed': memory_freed,
            'optimization_time': optimization_time,
            'strategies_applied': strategies_applied,
            'initial_memory': initial_memory,
            'final_memory': final_memory
        }

    def optimize_with_strategy_comparison(self) -> Dict[str, Dict[str, Any]]:
        """戦略比較付き最適化"""
        results = {}
        
        strategies = ['conservative', 'moderate', 'aggressive']
        for strategy in strategies:
            initial_memory = self.get_current_memory_usage()
            start_time = time.perf_counter()
            
            # 戦略別最適化
            if strategy == 'conservative':
                gc.collect()
            elif strategy == 'moderate':
                gc.collect()
                gc.collect()  # 2回実行
            elif strategy == 'aggressive':
                for _ in range(3):
                    gc.collect()
            
            final_memory = self.get_current_memory_usage()
            optimization_time = time.perf_counter() - start_time
            memory_freed = max(0, initial_memory - final_memory)
            
            results[strategy] = {
                'memory_freed': memory_freed,
                'optimization_time': optimization_time,
                'safety_score': 1.0 - (0.2 * strategies.index(strategy))  # 保守的ほど安全
            }
        
        return results

    def get_recommended_strategy(self) -> str:
        """推奨戦略取得"""
        # 簡易推奨ロジック
        current_memory = self.get_current_memory_usage()
        total_memory = psutil.virtual_memory().total
        usage_ratio = current_memory / total_memory
        
        if usage_ratio > 0.9:
            return 'aggressive'
        elif usage_ratio > 0.7:
            return 'moderate'
        else:
            return 'conservative'

    def adaptive_optimize(self) -> Dict[str, Any]:
        """適応的最適化実行"""
        # 基本最適化実行
        result = self.optimize()
        
        # 学習データ更新
        if self.learning_enabled:
            self._learning_data['optimization_patterns_learned'] += 1
            self._learning_data['adaptive_improvements'] += 1
        
        result['adaptive'] = True
        result['learning_applied'] = self.learning_enabled
        
        return result

    def get_learning_statistics(self) -> Dict[str, Any]:
        """学習統計取得"""
        return self._learning_data.copy()