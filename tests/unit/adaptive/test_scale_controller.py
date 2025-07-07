"""スケールアップ・ダウン制御テストケース

Task 3.2.4: スケールアップ・ダウン制御実装 - TDD RED Phase

スケールアップ・ダウン制御・ScaleController実装確認:
1. 動的スケーリング制御ロジック・スケールアップ・ダウン判定
2. 安全性機構・フェイルセーフ・過度スケーリング防止機能
3. リソース最適化・コスト効率・負荷適応スケーリング
4. AutoScalingManager統合・LoadDetectionEngine連携
5. 企業グレードスケーリング制御・安定性・効率・信頼性
6. 分散環境対応・高可用性・協調スケーリング品質保証

CLAUDE.md Code Excellence Compliance:
- TDD原則: RED→GREEN→REFACTOR厳格遵守
- 単一責任原則: スケールアップ・ダウン制御専用テスト
- SOLID原則: 拡張性・保守性重視
- パフォーマンス考慮: スケーリング制御効率・応答性重視
"""

import time

import pytest

from sphinxcontrib.jsontable.adaptive.scale_controller import (
    ScaleController,
)

# テスト期待値設定
SCALING_CONTROL_EFFECTIVENESS_TARGET = 0.90  # 90%以上スケーリング制御効果
SAFETY_MECHANISM_RELIABILITY_TARGET = 0.95  # 95%以上安全機構信頼性
RESOURCE_OPTIMIZATION_EFFICIENCY_TARGET = 0.88  # 88%以上リソース最適化効率
SCALING_RESPONSE_TIME_TARGET = 60  # 60ms以下スケーリング制御応答時間
ENTERPRISE_GRADE_SCALING_QUALITY_TARGET = 0.96  # 96%以上企業グレードスケーリング品質
DISTRIBUTED_COORDINATION_EFFECTIVENESS_TARGET = 0.92  # 92%以上分散協調効果


@pytest.fixture
def scale_controller():
    """スケールアップ・ダウン制御コントローラー"""
    return {"controller": ScaleController()}


@pytest.fixture
def mock_current_scaling_metrics():
    """モック現在スケーリングメトリクス"""
    return {
        "current_instance_count": 8,
        "current_cpu_utilization_percent": 75.5,
        "current_memory_utilization_percent": 68.2,
        "current_network_utilization_percent": 62.0,
        "current_load_score": 0.72,
        "current_response_time_ms": 180,
        "current_throughput_rps": 520,
        "current_error_rate_percent": 2.1,
        "current_queue_depth": 45,
        "scaling_history": [
            {"timestamp": "2025-01-01T10:00:00", "action": "scale_up", "instances": 6},
            {"timestamp": "2025-01-01T10:15:00", "action": "scale_up", "instances": 8},
        ],
        "last_scaling_time": "2025-01-01T10:15:00",
    }


@pytest.fixture
def mock_scaling_targets():
    """モックスケーリング目標"""
    return {
        "target_cpu_utilization_percent": 70.0,
        "target_memory_utilization_percent": 65.0,
        "target_response_time_ms": 150,
        "target_throughput_rps": 600,
        "target_error_rate_percent": 1.5,
        "scaling_thresholds": {
            "scale_up_cpu_threshold": 80.0,
            "scale_down_cpu_threshold": 50.0,
            "scale_up_memory_threshold": 75.0,
            "scale_down_memory_threshold": 45.0,
        },
        "safety_limits": {
            "min_instances": 2,
            "max_instances": 50,
            "max_scaling_per_hour": 10,
            "cooldown_period_minutes": 5,
        },
    }


@pytest.fixture
def mock_load_detection_data():
    """モック負荷検出データ"""
    return {
        "load_trend": "increasing",
        "predicted_load_spike": True,
        "load_severity": "high",
        "estimated_duration_minutes": 30,
        "resource_pressure_points": ["cpu", "memory"],
        "scaling_urgency": "medium",
        "load_pattern_type": "sustained",
        "ml_prediction_confidence": 0.89,
        "scaling_recommendation": "scale_up",
        "recommended_instance_count": 12,
    }


class TestScaleController:
    """スケールアップ・ダウン制御コントローラーテストクラス"""

    def test_dynamic_scaling_control_logic(
        self,
        scale_controller,
        mock_current_scaling_metrics,
        mock_scaling_targets,
    ):
        """動的スケーリング制御ロジック確認

        現在のスケーリング状況と目標に基づいて
        動的にスケーリング判定・制御を行う機能を確認する。

        期待動作:
        - スケーリング制御効果90%以上
        - CPU・メモリ・ネットワーク負荷適応制御
        - リアルタイムスケーリング判定
        - インテリジェント制御ロジック
        """
        result = scale_controller["controller"].execute_dynamic_scaling_control(
            {
                "enable_dynamic_control": True,
                "realtime_scaling_judgment": True,
                "load_adaptive_scaling": True,
                "intelligent_control_logic": True,
                "multi_resource_consideration": True,
                "current_metrics": mock_current_scaling_metrics,
                "scaling_targets": mock_scaling_targets,
            }
        )

        assert result.scaling_control_success
        assert result.dynamic_judgment_active
        assert result.load_adaptive_control_enabled

        control_metrics = result.scaling_control_metrics
        assert (
            control_metrics.scaling_control_effectiveness
            >= SCALING_CONTROL_EFFECTIVENESS_TARGET
        )
        assert control_metrics.cpu_scaling_control_quality >= 0.92  # 92%以上CPU制御品質
        assert (
            control_metrics.memory_scaling_control_quality >= 0.88
        )  # 88%以上メモリ制御品質
        assert (
            control_metrics.network_scaling_control_quality >= 0.85
        )  # 85%以上ネットワーク制御品質

    def test_scale_up_decision_logic(
        self,
        scale_controller,
        mock_current_scaling_metrics,
        mock_load_detection_data,
    ):
        """スケールアップ判定ロジック確認

        負荷増加・リソース不足状況を検出し
        適切なスケールアップ判定を行う機能を確認する。

        期待動作:
        - スケールアップ判定精度92%以上
        - 負荷予測ベース判定
        - リソース不足検出・対応
        - 最適インスタンス数算出
        """
        high_load_metrics = {
            **mock_current_scaling_metrics,
            "current_cpu_utilization_percent": 85.0,  # 高CPU負荷
            "current_memory_utilization_percent": 78.0,  # 高メモリ負荷
            "current_response_time_ms": 250,  # 高応答時間
            "current_queue_depth": 120,  # 高キュー深度
        }

        result = scale_controller["controller"].determine_scale_up_decision(
            {
                "enable_scale_up_judgment": True,
                "load_prediction_based_decision": True,
                "resource_shortage_detection": True,
                "optimal_instance_calculation": True,
                "proactive_scaling_enabled": True,
                "current_metrics": high_load_metrics,
                "load_detection_data": mock_load_detection_data,
            }
        )

        assert result.scale_up_decision_success
        assert result.scale_up_recommended
        assert result.optimal_instance_count_calculated

        scale_up_metrics = result.scale_up_decision_metrics
        assert scale_up_metrics.scale_up_judgment_accuracy >= 0.92  # 92%以上判定精度
        assert (
            scale_up_metrics.load_prediction_integration_quality >= 0.89
        )  # 89%以上予測統合品質
        assert (
            scale_up_metrics.resource_shortage_detection_accuracy >= 0.94
        )  # 94%以上不足検出精度
        assert (
            scale_up_metrics.instance_calculation_precision >= 0.87
        )  # 87%以上インスタンス計算精度

    def test_scale_down_decision_logic(
        self, scale_controller, mock_current_scaling_metrics
    ):
        """スケールダウン判定ロジック確認

        負荷減少・リソース余剰状況を検出し
        安全なスケールダウン判定を行う機能を確認する。

        期待動作:
        - スケールダウン判定精度90%以上
        - リソース余剰検出・活用
        - 安全性考慮スケールダウン
        - コスト最適化効果
        """
        low_load_metrics = {
            **mock_current_scaling_metrics,
            "current_cpu_utilization_percent": 35.0,  # 低CPU負荷
            "current_memory_utilization_percent": 28.0,  # 低メモリ負荷
            "current_response_time_ms": 80,  # 低応答時間
            "current_queue_depth": 5,  # 低キュー深度
            "stable_period_minutes": 20,  # 安定期間
        }

        result = scale_controller["controller"].determine_scale_down_decision(
            {
                "enable_scale_down_judgment": True,
                "resource_surplus_detection": True,
                "safety_consideration_scaling": True,
                "cost_optimization_mode": True,
                "stability_period_validation": True,
                "current_metrics": low_load_metrics,
            }
        )

        assert result.scale_down_decision_success
        assert result.scale_down_recommended
        assert result.cost_optimization_effective

        scale_down_metrics = result.scale_down_decision_metrics
        assert (
            scale_down_metrics.scale_down_judgment_accuracy >= 0.90
        )  # 90%以上判定精度
        assert (
            scale_down_metrics.resource_surplus_detection_accuracy >= 0.93
        )  # 93%以上余剰検出精度
        assert (
            scale_down_metrics.safety_consideration_score >= 0.96
        )  # 96%以上安全性考慮スコア
        assert (
            scale_down_metrics.cost_optimization_effectiveness >= 0.88
        )  # 88%以上コスト最適化効果

    def test_safety_mechanism_failsafe_control(
        self, scale_controller, mock_current_scaling_metrics, mock_scaling_targets
    ):
        """安全機構・フェイルセーフ制御確認

        過度なスケーリング防止・安全制御機構で
        システム安定性を保証する機能を確認する。

        期待動作:
        - 安全機構信頼性95%以上
        - 過度スケーリング防止
        - フェイルセーフ機能動作
        - システム安定性保証
        """
        extreme_scaling_request = {
            **mock_current_scaling_metrics,
            "requested_instance_count": 100,  # 極端な要求
            "scaling_rate_per_minute": 20,  # 高速スケーリング要求
            "emergency_scaling_mode": True,
            "safety_override_request": False,
        }

        result = scale_controller["controller"].enforce_safety_mechanisms(
            {
                "enable_safety_mechanisms": True,
                "excessive_scaling_prevention": True,
                "failsafe_control_active": True,
                "system_stability_priority": True,
                "safety_limit_enforcement": True,
                "scaling_request": extreme_scaling_request,
                "safety_limits": mock_scaling_targets["safety_limits"],
            }
        )

        assert result.safety_mechanism_success
        assert result.excessive_scaling_prevented
        assert result.failsafe_control_activated

        safety_metrics = result.safety_mechanism_metrics
        assert (
            safety_metrics.safety_mechanism_reliability
            >= SAFETY_MECHANISM_RELIABILITY_TARGET
        )
        assert (
            safety_metrics.excessive_scaling_prevention_rate >= 0.98
        )  # 98%以上過度防止率
        assert (
            safety_metrics.failsafe_activation_accuracy >= 0.96
        )  # 96%以上フェイルセーフ精度
        assert (
            safety_metrics.system_stability_guarantee >= 0.99
        )  # 99%以上システム安定性保証

    def test_resource_optimization_efficiency(
        self, scale_controller, mock_current_scaling_metrics
    ):
        """リソース最適化効率確認

        CPU・メモリ・ネットワークリソースの
        最適化・効率的活用を行う機能を確認する。

        期待動作:
        - リソース最適化効率88%以上
        - 多次元リソース最適化
        - 効率的リソース配分
        - コスト効率最大化
        """
        resource_optimization_config = {
            **mock_current_scaling_metrics,
            "optimization_targets": [
                "cpu_efficiency",
                "memory_efficiency",
                "network_efficiency",
                "cost_efficiency",
            ],
            "resource_allocation_strategy": "intelligent_optimization",
            "efficiency_improvement_goal": 0.25,  # 25%効率改善目標
            "cost_reduction_target": 0.15,  # 15%コスト削減目標
        }

        result = scale_controller["controller"].optimize_resource_efficiency(
            {
                "enable_resource_optimization": True,
                "multi_dimensional_optimization": True,
                "intelligent_resource_allocation": True,
                "cost_efficiency_maximization": True,
                "efficiency_monitoring_active": True,
                "resource_config": resource_optimization_config,
            }
        )

        assert result.resource_optimization_success
        assert result.multi_dimensional_optimization_active
        assert result.cost_efficiency_maximized

        optimization_metrics = result.resource_optimization_metrics
        assert (
            optimization_metrics.overall_resource_efficiency
            >= RESOURCE_OPTIMIZATION_EFFICIENCY_TARGET
        )
        assert (
            optimization_metrics.cpu_resource_optimization >= 0.90
        )  # 90%以上CPU最適化
        assert (
            optimization_metrics.memory_resource_optimization >= 0.88
        )  # 88%以上メモリ最適化
        assert (
            optimization_metrics.cost_efficiency_improvement >= 0.85
        )  # 85%以上コスト効率改善

    def test_auto_scaling_manager_integration(
        self,
        scale_controller,
        mock_current_scaling_metrics,
        mock_load_detection_data,
    ):
        """AutoScalingManager統合確認

        AutoScalingManagerとの統合で
        統一的なスケーリング制御を実現する機能を確認する。

        期待動作:
        - AutoScalingManager統合効果92%以上
        - 負荷検出連携スケーリング制御
        - 統一スケーリング戦略実行
        - エンドツーエンド制御品質
        """
        result = scale_controller["controller"].integrate_with_auto_scaling_manager(
            {
                "enable_auto_scaling_integration": True,
                "load_detection_integration": True,
                "unified_scaling_strategy": True,
                "end_to_end_control_quality": True,
                "intelligent_coordination": True,
                "current_metrics": mock_current_scaling_metrics,
                "load_detection_data": mock_load_detection_data,
            }
        )

        assert result.auto_scaling_integration_success
        assert result.load_detection_integration_active
        assert result.unified_strategy_execution_enabled

        integration_metrics = result.auto_scaling_integration_metrics
        assert (
            integration_metrics.auto_scaling_manager_integration_effectiveness >= 0.92
        )  # 92%以上統合効果
        assert (
            integration_metrics.load_detection_integration_quality >= 0.94
        )  # 94%以上負荷検出統合品質
        assert (
            integration_metrics.unified_strategy_execution_quality >= 0.90
        )  # 90%以上統一戦略実行品質
        assert (
            integration_metrics.end_to_end_control_coherence >= 0.88
        )  # 88%以上エンドツーエンド制御整合性

    def test_scaling_monitoring_feedback(
        self, scale_controller, mock_current_scaling_metrics
    ):
        """スケーリング監視・フィードバック確認

        スケーリング動作の継続監視と
        フィードバック・改善を行う機能を確認する。

        期待動作:
        - スケーリング監視効果94%以上
        - リアルタイム監視・追跡
        - フィードバック・改善ループ
        - 継続的最適化
        """
        result = scale_controller["controller"].monitor_scaling_performance(
            {
                "enable_scaling_monitoring": True,
                "realtime_performance_tracking": True,
                "feedback_improvement_loop": True,
                "continuous_optimization": True,
                "intelligent_monitoring": True,
                "monitoring_baseline": mock_current_scaling_metrics,
            }
        )

        assert result.scaling_monitoring_success
        assert result.realtime_tracking_active
        assert result.feedback_loop_operational

        monitoring_metrics = result.scaling_monitoring_metrics
        assert (
            monitoring_metrics.scaling_monitoring_effectiveness >= 0.94
        )  # 94%以上監視効果
        assert (
            monitoring_metrics.realtime_tracking_accuracy >= 0.96
        )  # 96%以上リアルタイム追跡精度
        assert (
            monitoring_metrics.feedback_improvement_quality >= 0.91
        )  # 91%以上フィードバック改善品質
        assert (
            monitoring_metrics.continuous_optimization_score >= 0.89
        )  # 89%以上継続最適化スコア

    def test_distributed_scaling_coordination(
        self, scale_controller, mock_current_scaling_metrics
    ):
        """分散スケーリング協調確認

        分散環境での協調スケーリングと
        ノード間整合性・協調制御を確認する。

        期待動作:
        - 分散協調効果92%以上
        - ノード間整合性・協調制御
        - 分散環境高可用性スケーリング
        - クラスタ全体最適化
        """
        distributed_config = {
            **mock_current_scaling_metrics,
            "cluster_nodes": 12,
            "node_scaling_status": [
                {"node_id": "node-1", "instances": 4, "utilization": 0.75},
                {"node_id": "node-2", "instances": 6, "utilization": 0.68},
                {"node_id": "node-3", "instances": 5, "utilization": 0.82},
            ],
            "inter_node_coordination": True,
            "cluster_load_balancing": True,
            "distributed_consistency": True,
        }

        result = scale_controller["controller"].coordinate_distributed_scaling(
            {
                "enable_distributed_coordination": True,
                "inter_node_consistency": True,
                "cluster_optimization_mode": True,
                "distributed_high_availability": True,
                "intelligent_cluster_management": True,
                "distributed_config": distributed_config,
            }
        )

        assert result.distributed_coordination_success
        assert result.inter_node_consistency_maintained
        assert result.cluster_optimization_enabled

        distributed_metrics = result.distributed_coordination_metrics
        assert (
            distributed_metrics.distributed_coordination_effectiveness
            >= DISTRIBUTED_COORDINATION_EFFECTIVENESS_TARGET
        )
        assert (
            distributed_metrics.inter_node_consistency_quality >= 0.95
        )  # 95%以上ノード間整合性品質
        assert (
            distributed_metrics.cluster_optimization_score >= 0.88
        )  # 88%以上クラスタ最適化スコア
        assert (
            distributed_metrics.distributed_high_availability_level >= 0.999
        )  # 99.9%以上分散高可用性

    def test_enterprise_grade_scaling_quality(
        self, scale_controller, mock_current_scaling_metrics
    ):
        """企業グレードスケーリング品質確認

        企業グレード品質基準を満たす
        スケーリング制御品質を確認する。

        期待動作:
        - 企業グレードスケーリング品質96%以上
        - 監査・コンプライアンス対応
        - SLA・可用性保証スケーリング
        - エンタープライズ運用品質
        """
        enterprise_config = {
            **mock_current_scaling_metrics,
            "sla_requirements": {
                "scaling_availability": 0.999,
                "scaling_response_time_ms": 50,
                "scaling_accuracy": 0.95,
            },
            "compliance_standards": ["SOC2", "ISO27001", "PCI-DSS"],
            "audit_logging_enabled": True,
            "enterprise_monitoring": True,
            "business_continuity_mode": True,
        }

        result = scale_controller["controller"].ensure_enterprise_scaling_quality(
            {
                "enable_enterprise_quality": True,
                "sla_compliance_enforcement": True,
                "audit_trail_generation": True,
                "compliance_verification": True,
                "business_continuity_assurance": True,
                "enterprise_config": enterprise_config,
            }
        )

        assert result.enterprise_quality_verified
        assert result.sla_compliance_confirmed
        assert result.audit_trail_generated

        quality_metrics = result.enterprise_scaling_quality_metrics
        assert (
            quality_metrics.enterprise_grade_scaling_score
            >= ENTERPRISE_GRADE_SCALING_QUALITY_TARGET
        )
        assert quality_metrics.sla_compliance_rate >= 0.999  # 99.9%以上SLA準拠率
        assert quality_metrics.audit_completeness >= 0.96  # 96%以上監査完全性
        assert (
            quality_metrics.business_continuity_score >= 0.95
        )  # 95%以上事業継続性スコア

    def test_scaling_control_performance(
        self, scale_controller, mock_current_scaling_metrics
    ):
        """スケーリング制御パフォーマンス確認

        スケーリング制御のパフォーマンスと
        応答時間・効率性を確認する。

        期待動作:
        - スケーリング制御応答時間60ms以下
        - 制御オーバーヘッド最小化
        - 高効率スケーリング制御
        - リアルタイム制御性能
        """
        start_time = time.time()

        result = scale_controller["controller"].verify_scaling_control_performance(
            {
                "enable_performance_verification": True,
                "target_response_time_ms": SCALING_RESPONSE_TIME_TARGET,
                "minimize_control_overhead": True,
                "high_efficiency_scaling_control": True,
                "realtime_control_requirement": True,
            }
        )

        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000

        assert result.performance_verification_success
        assert result.response_time_compliant
        assert result.overhead_minimized

        # パフォーマンス確認
        performance_metrics = result.scaling_control_performance_metrics
        assert performance_metrics.response_time_ms <= SCALING_RESPONSE_TIME_TARGET
        assert (
            performance_metrics.control_overhead_percent <= 2.5
        )  # 2.5%以下制御オーバーヘッド
        assert performance_metrics.scaling_control_efficiency >= 0.96  # 96%以上制御効率
        assert (
            performance_metrics.realtime_control_score >= 0.98
        )  # 98%以上リアルタイム制御性能

    def test_scaling_control_foundation_establishment(
        self, scale_controller, mock_current_scaling_metrics
    ):
        """スケーリング制御基盤確立確認

        スケールアップ・ダウン制御基盤の確立と
        企業グレード品質・運用準備完了を確認する。

        期待動作:
        - 全スケーリング制御機能統合動作
        - 基盤確立・運用準備完了
        - 企業グレードスケーリング制御品質達成
        - 継続改善基盤確立
        """
        result = scale_controller["controller"].establish_scaling_control_foundation(
            {
                "verify_all_scaling_features": True,
                "establish_control_foundation": True,
                "validate_overall_scaling_quality": True,
                "ensure_enterprise_grade_scaling": True,
                "confirm_operational_readiness": True,
            }
        )

        assert result.foundation_establishment_success
        assert result.all_scaling_features_integrated
        assert result.operational_readiness_confirmed

        # 基盤品質確認
        foundation_quality = result.scaling_foundation_quality
        assert foundation_quality.overall_scaling_quality >= 0.97
        assert foundation_quality.integration_completeness >= 0.98
        assert foundation_quality.system_coherence_score >= 0.95
        assert foundation_quality.enterprise_grade_foundation

        # 全体効果確認
        overall_effect = result.overall_scaling_effect
        assert overall_effect.scaling_foundation_established
        assert overall_effect.intelligent_scaling_maximized
        assert overall_effect.enterprise_quality_guaranteed


class TestScaleControllerEdgeCases:
    """スケールアップ・ダウン制御エッジケーステスト"""

    def test_extreme_load_fluctuation_handling(self, scale_controller):
        """極端負荷変動処理確認"""
        # 極端な負荷変動でも安定してスケーリング制御できることを確認
        extreme_fluctuation = {
            "load_spike_magnitude": 15.0,  # 15倍負荷急増
            "load_drop_magnitude": 0.1,  # 90%負荷急減
            "fluctuation_frequency_per_minute": 5,  # 高頻度変動
            "unpredictable_pattern": True,
            "emergency_control_required": True,
        }

        result = scale_controller["controller"].execute_dynamic_scaling_control(
            {
                "enable_dynamic_control": True,
                "extreme_fluctuation_handling": True,
                "emergency_control_mode": True,
                "current_metrics": extreme_fluctuation,
            }
        )

        # 極端変動でも安定して制御
        assert hasattr(result, "scaling_control_success")

    def test_resource_constraint_scaling_optimization(self, scale_controller):
        """リソース制約スケーリング最適化確認"""
        # リソース制約下でも効率的にスケーリング最適化できることを確認
        constrained_resources = {
            "available_instances_limit": 5,  # 限定インスタンス
            "cpu_quota_limit_cores": 8,  # CPU制限
            "memory_quota_limit_gb": 16,  # メモリ制限
            "network_bandwidth_limit_mbps": 500,  # ネットワーク制限
            "budget_constraints": True,
        }

        result = scale_controller["controller"].optimize_resource_efficiency(
            {
                "enable_resource_optimization": True,
                "resource_constraint_aware": True,
                "efficient_utilization_mode": True,
                "resource_config": constrained_resources,
            }
        )

        assert result.resource_optimization_success
        assert (
            result.resource_optimization_metrics.overall_resource_efficiency
            >= 0.80  # 制約下でも80%以上
        )

    def test_multi_tier_application_scaling(self, scale_controller):
        """マルチティアアプリケーションスケーリング確認"""
        # 複数ティア構成でのスケーリング協調を確認
        multi_tier_config = {
            "application_tiers": ["web", "api", "database", "cache"],
            "tier_dependencies": {
                "web": ["api"],
                "api": ["database", "cache"],
                "database": [],
                "cache": [],
            },
            "tier_scaling_ratios": {
                "web": 1.0,
                "api": 0.8,
                "database": 0.3,
                "cache": 0.5,
            },
            "inter_tier_coordination": True,
        }

        result = scale_controller["controller"].coordinate_distributed_scaling(
            {
                "enable_distributed_coordination": True,
                "multi_tier_coordination": True,
                "dependency_aware_scaling": True,
                "distributed_config": multi_tier_config,
            }
        )

        assert result.distributed_coordination_success
        assert (
            result.distributed_coordination_metrics.distributed_coordination_effectiveness
            >= 0.88  # マルチティアでも88%以上
        )


if __name__ == "__main__":
    pytest.main([__file__])
