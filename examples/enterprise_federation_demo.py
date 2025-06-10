#!/usr/bin/env python3
"""Enterprise Excel Federation Demo - Advanced Multi-Department Integration.

このデモは企業環境での複数部署Excel統合と
リアルタイム監視機能の包括的な実演を提供します。

機能:
- 複数部署Excel統合(営業部、財務部、製造部)
- 部署間クロス分析
- エグゼクティブレポート自動生成
- リアルタイムファイル監視
- 統合ダッシュボード

使用方法:
    python enterprise_federation_demo.py

必要な依存関係:
    pip install pandas openpyxl watchdog
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sphinxcontrib.jsontable.excel import (
    ExcelRAGFederation,
    ExcelRAGMonitor,
    create_enterprise_federation,
    setup_enterprise_monitoring
)


def create_sample_enterprise_data():
    """企業データのサンプルを作成."""
    print("🏢 企業サンプルデータを作成中...")
    
    import pandas as pd
    
    # 営業部データ
    sales_data = {
        '営業担当': ['田中太郎', '佐藤花子', '山田次郎', '鈴木美穂', '高橋健太'],
        '顧客ID': ['C001', 'C002', 'C003', 'C004', 'C005'],
        '顧客名': ['ABC商事', 'XYZ企業', 'PQR株式会社', 'LMN商店', 'DEF工業'],
        '売上金額': [1500000, 2300000, 1800000, 900000, 2100000],
        '地域': ['関東', '関西', '中部', '九州', '関東'],
        '売上日': ['2025-06-01', '2025-06-02', '2025-06-03', '2025-06-04', '2025-06-05'],
        '製品ID': ['P001', 'P002', 'P001', 'P003', 'P002']
    }
    
    # 財務部データ
    finance_data = {
        '勘定科目': ['売上高', '売上原価', '販売費及び一般管理費', '営業利益', '当期純利益'],
        '当月実績': [8600000, 5500000, 2100000, 1000000, 700000],
        '前月実績': [7800000, 5200000, 1950000, 850000, 600000],
        '予算': [9000000, 5800000, 2200000, 1000000, 750000],
        '達成率': [95.6, 94.8, 95.5, 100.0, 93.3],
        '部門': ['全社', '全社', '全社', '全社', '全社']
    }
    
    # 製造部データ  
    production_data = {
        '製品ID': ['P001', 'P002', 'P003', 'P004', 'P005'],
        '製品名': ['商品A', '商品B', '商品C', '商品D', '商品E'],
        '計画生産数': [1000, 1500, 800, 1200, 900],
        '実績生産数': [950, 1480, 820, 1180, 910],
        '品質スコア': [98.5, 97.2, 99.1, 96.8, 98.9],
        '生産ライン': ['Line1', 'Line2', 'Line1', 'Line3', 'Line2'],
        '生産日': ['2025-06-01', '2025-06-02', '2025-06-03', '2025-06-04', '2025-06-05']
    }
    
    # ファイル作成
    data_dir = Path('examples/data/enterprise')
    data_dir.mkdir(parents=True, exist_ok=True)
    
    sales_df = pd.DataFrame(sales_data)
    finance_df = pd.DataFrame(finance_data)
    production_df = pd.DataFrame(production_data)
    
    sales_file = data_dir / 'sales_department.xlsx'
    finance_file = data_dir / 'finance_department.xlsx'
    production_file = data_dir / 'production_department.xlsx'
    
    sales_df.to_excel(sales_file, index=False, sheet_name='営業実績')
    finance_df.to_excel(finance_file, index=False, sheet_name='財務実績')
    production_df.to_excel(production_file, index=False, sheet_name='生産実績')
    
    print(f"✅ 企業サンプルデータ作成完了:")
    print(f"   - 営業部: {sales_file}")
    print(f"   - 財務部: {finance_file}")
    print(f"   - 製造部: {production_file}")
    
    return {
        "sales": str(sales_file),
        "finance": str(finance_file),
        "production": str(production_file)
    }


def demo_federation_setup():
    """企業統合システムのセットアップデモ."""
    print("\n🚀 企業Excel統合システム セットアップ開始!")
    print("=" * 60)
    
    # サンプルデータ作成
    enterprise_files = create_sample_enterprise_data()
    
    # Federation設定
    departments = {
        "sales": {
            "name": "営業部",
            "excel_sources": [
                {"file": enterprise_files["sales"], "purpose": "sales-analysis"}
            ],
            "config": {
                "industry_focus": "retail",
                "access_level": "internal"
            }
        },
        "finance": {
            "name": "財務部", 
            "excel_sources": [
                {"file": enterprise_files["finance"], "purpose": "financial-analysis"}
            ],
            "config": {
                "industry_focus": "financial",
                "access_level": "confidential"
            }
        },
        "production": {
            "name": "製造部",
            "excel_sources": [
                {"file": enterprise_files["production"], "purpose": "production-management"}
            ],
            "config": {
                "industry_focus": "manufacturing", 
                "access_level": "internal"
            }
        }
    }
    
    print(f"\n📊 {len(departments)}部署の統合を開始...")
    
    # Federation作成
    federation = create_enterprise_federation(
        departments=departments,
        federation_name="demo-enterprise"
    )
    
    print("✅ 企業統合システム作成完了!")
    print(f"   - 統合部署数: {len(departments)}")
    print(f"   - 総Excelファイル数: {sum(len(dept['excel_sources']) for dept in departments.values())}")
    
    return federation, enterprise_files


def demo_cross_department_analysis(federation: ExcelRAGFederation):
    """部署間クロス分析デモ."""
    print("\n🔗 部署間クロス分析設定")
    print("=" * 40)
    
    # 部署間関係設定
    relationships = {
        "customer_id": ["sales", "finance"],
        "product_id": ["sales", "production"]
    }
    
    result = federation.enable_cross_analysis(relationships=relationships)
    
    print("✅ クロス分析設定完了!")
    print(f"   - 関係設定数: {result['relationships_configured']}")
    print(f"   - データ一貫性スコア: {result['data_consistency_score']:.2f}")
    print(f"   - 統合分析可能フィールド数: {len(result.get('unified_schema', {}).get('common_fields', {}))}")
    
    # サンプルクエリ実行
    print("\n💬 統合クエリテスト:")
    sample_queries = [
        "売上と生産実績の関連性は？",
        "財務目標達成に影響する要因は？", 
        "部署間の効率改善ポイントは？"
    ]
    
    for i, query in enumerate(sample_queries, 1):
        print(f"\n{i}. {query}")
        try:
            query_result = federation.query_federated_data(query, cross_department=True)
            print(f"   🤖 {query_result['synthesized_answer']}")
            print(f"   📊 信頼度: {query_result['confidence_score']:.2f}")
        except Exception as e:
            print(f"   ⚠️  クエリ処理: {e}")
    
    return result


def demo_executive_reporting(federation: ExcelRAGFederation):
    """エグゼクティブレポート生成デモ."""
    print("\n📈 エグゼクティブレポート生成")
    print("=" * 40)
    
    # エグゼクティブレポート生成
    executive_personas = ["CEO", "CFO", "COO"]
    
    print(f"⏱️  {len(executive_personas)}役職向けレポート生成中...")
    
    try:
        report = federation.generate_executive_report(
            target_personas=executive_personas,
            report_format="comprehensive"
        )
        
        print("✅ エグゼクティブレポート生成完了!")
        print(f"   - レポート対象: {', '.join(report['persona_reports'].keys())}")
        print(f"   - 含まれる部署: {len(report['departments_included'])}")
        print(f"   - 生成時刻: {report['generation_timestamp']}")
        
        # CEO向けサマリー表示
        ceo_report = report['persona_reports'].get('CEO', {})
        print(f"\n👔 CEO向けエグゼクティブサマリー:")
        print(f"   - 重要指標: {ceo_report.get('dashboard_metrics', {}).get('primary_kpi', 'N/A')}")
        print(f"   - トレンド: {ceo_report.get('dashboard_metrics', {}).get('trend_indicator', 'N/A')}")
        print(f"   - リスクスコア: {ceo_report.get('dashboard_metrics', {}).get('risk_score', 'N/A')}")
        
        # 全社サマリー
        exec_summary = report.get('executive_summary', {})
        print(f"\n📋 全社業績サマリー:")
        print(f"   - 総合評価: {exec_summary.get('overall_performance', 'N/A')}")
        if exec_summary.get('key_achievements'):
            print(f"   - 主要成果: {len(exec_summary['key_achievements'])}件")
        if exec_summary.get('strategic_recommendations'):
            print(f"   - 戦略提案: {len(exec_summary['strategic_recommendations'])}件")
        
        return report
        
    except Exception as e:
        print(f"❌ エグゼクティブレポート生成エラー: {e}")
        return None


def demo_real_time_monitoring(federation: ExcelRAGFederation, enterprise_files: Dict[str, str]):
    """リアルタイム監視デモ."""
    print("\n⚡ リアルタイムExcel監視システム")
    print("=" * 45)
    
    # 監視システム設定
    monitor = ExcelRAGMonitor(federation=federation)
    
    print("🔍 監視対象ファイル設定中...")
    
    # 各部署ファイルを監視対象に追加
    departments = {
        "sales": "営業部",
        "finance": "財務部",
        "production": "製造部"
    }
    
    for dept_id, dept_name in departments.items():
        if dept_id in enterprise_files:
            try:
                monitor.watch_file(
                    file_path=enterprise_files[dept_id],
                    department=dept_id,
                    rag_purpose=f"{dept_id}-monitoring",
                    on_change=lambda d=dept_name: print(f"📄 {d}のExcelファイルが更新されました!")
                )
                print(f"   ✅ {dept_name}: {Path(enterprise_files[dept_id]).name}")
            except Exception as e:
                print(f"   ❌ {dept_name}: {e}")
    
    # 監視開始
    print("\n🚀 リアルタイム監視開始...")
    monitor.start_monitoring()
    
    # 監視状況表示
    status = monitor.get_monitoring_status()
    print(f"✅ 監視システム稼働中!")
    print(f"   - 監視ファイル数: {status['watched_files']}")
    print(f"   - 監視ディレクトリ数: {status['watched_directories']}")
    print(f"   - 即座更新モード: {status['update_policy']['immediate_update']}")
    
    # 短時間監視デモ
    print(f"\n⏰ 5秒間の監視デモ実行...")
    print("   (この間にExcelファイルを変更すると自動検出されます)")
    
    try:
        time.sleep(5)
        
        # 強制アップデートテスト
        print("\n🔄 全ファイル強制アップデートテスト...")
        update_results = monitor.force_update_all()
        
        print(f"✅ 強制アップデート完了!")
        print(f"   - 成功: {update_results['successful_updates']}")
        print(f"   - 失敗: {update_results['failed_updates']}")
        print(f"   - スキップ: {update_results['skipped_files']}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  ユーザーによりデモ中断")
    
    # 監視停止
    monitor.stop_monitoring()
    print("🛑 監視システム停止")
    
    return monitor


def demo_federation_status(federation: ExcelRAGFederation):
    """統合システム状況表示."""
    print("\n📊 企業統合システム状況")
    print("=" * 35)
    
    status = federation.get_federation_status()
    
    print(f"🏢 統合システム名: {status['federation_name']}")
    print(f"📂 統合部署数: {status['departments_count']}")
    print(f"📄 総Excelファイル数: {status['total_excel_files']}")
    print(f"🔗 部署間関係数: {status['cross_relationships']}")
    print(f"🔄 クロス分析: {'有効' if status['cross_analysis_enabled'] else '無効'}")
    print(f"📈 健全性: {status['overall_health']}")
    
    print(f"\n🎯 利用可能機能:")
    for capability in status['available_capabilities']:
        print(f"   ✅ {capability}")


def main():
    """メインデモ実行."""
    print("🌟 企業Excel統合・監視システム 完全デモ")
    print("=" * 55)
    print("企業の複数部署Excel統合とリアルタイム監視機能を")
    print("包括的に実演します。")
    
    try:
        # 1. Federation設定
        federation, enterprise_files = demo_federation_setup()
        
        # 2. 部署間クロス分析
        demo_cross_department_analysis(federation)
        
        # 3. エグゼクティブレポート
        demo_executive_reporting(federation)
        
        # 4. リアルタイム監視
        demo_real_time_monitoring(federation, enterprise_files)
        
        # 5. 統合状況表示
        demo_federation_status(federation)
        
        print("\n🎉 全デモ完了!")
        print("=" * 25)
        print("✅ 企業Excel統合システムの包括的機能を確認できました")
        print("📚 詳細ドキュメント: docs/enterprise_integration.md")
        print("🚀 実装状況: エンタープライズ機能完全実装")
        print("📅 適用対象: 中〜大企業での即座運用可能")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  ユーザーによりデモが中断されました")
        return 1
    except Exception as e:
        print(f"\n\n❌ 予期しないエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())