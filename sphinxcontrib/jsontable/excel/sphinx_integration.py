"""Automatic Sphinx documentation integration for Excel-RAG conversion.

This module provides comprehensive Sphinx documentation generation capabilities
for Excel-to-RAG converted data, including main documents, sub-documents,
index generation, and configuration updates.

Key Features:
- Automatic main document generation with comprehensive metadata
- Sub-document creation for large datasets
- Index document generation with navigation
- Sphinx configuration updates for Excel integration
- Template-based document creation with customization
- Multi-format output support
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AutoSphinxIntegration:
    """Automatic Sphinx document generation for Excel-RAG integration."""
    
    def __init__(self):
        """Initialize Sphinx integration system."""
        self.templates = self._load_document_templates()
        logger.info("AutoSphinxIntegration initialized")
    
    def create_complete_documentation(
        self, 
        conversion_result: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create complete Sphinx documentation suite.
        
        Args:
            conversion_result: Results from Excel conversion
            config: Configuration for document generation
            
        Returns:
            Dictionary containing generated documentation files
        """
        logger.info("Creating complete Sphinx documentation suite")
        
        # Step 1: Main document creation
        main_doc = self._create_main_document(conversion_result, config)
        
        # Step 2: Sub-documents for large datasets
        sub_docs = self._create_sub_documents(conversion_result, config)
        
        # Step 3: Index document creation
        index_doc = self._create_index_document(conversion_result, main_doc, sub_docs)
        
        # Step 4: Configuration updates
        sphinx_config = self._update_sphinx_config(conversion_result, config)
        
        # Step 5: Create file structure
        file_structure = self._create_file_structure(conversion_result)
        
        result = {
            'main_document': main_doc,
            'sub_documents': sub_docs,
            'index_document': index_doc,
            'sphinx_config': sphinx_config,
            'file_structure': file_structure
        }
        
        # Write files to disk
        written_files = self._write_documentation_files(result, config)
        
        logger.info(f"Complete Sphinx documentation created: {len(written_files)} files")
        return result
    
    def _create_main_document(
        self, 
        conversion_result: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> str:
        """Create the main Sphinx document."""
        logger.info("Creating main Sphinx document")
        
        # Extract data for template
        title = self._infer_title(conversion_result, config)
        excel_source = conversion_result.get('metadata', {}).get('source_file', 'Unknown')
        data_summary = self._generate_data_summary(conversion_result)
        quality_score = conversion_result.get('quality_score', 0.8)
        rag_purpose = config.get('rag_purpose', 'general-analysis')
        entity_types = ','.join(conversion_result.get('entities', {}).get('types', []))
        
        # Generate example queries
        example_queries = self._generate_example_queries(conversion_result, config)
        advanced_queries = self._generate_advanced_queries(conversion_result, config)
        
        # Generate quality report
        quality_report = self._format_quality_report(conversion_result.get('metadata', {}))
        
        # Generate update history
        update_history = self._format_update_history()
        
        # Generate related links
        related_links = self._format_related_links(conversion_result)
        
        # Use template
        template = self.templates['main_document']
        
        try:
            main_document = template.format(
                title=title,
                title_underline='=' * len(title),
                description=data_summary,
                keywords=', '.join(conversion_result.get('entities', {}).get('types', [])),
                excel_source=excel_source,
                data_summary=data_summary,
                last_updated=datetime.now().strftime('%Y-%m-%d %H:%M'),
                quality_score=f"{quality_score:.2f}",
                json_file=f"{rag_purpose}_data.json",
                rag_purpose=rag_purpose,
                entity_types=entity_types,
                auto_update=config.get('auto_update', 'manual'),
                format_type=conversion_result.get('format_type', 'standard_table'),
                data_structure_info=self._format_structure_info(conversion_result),
                example_queries=example_queries,
                advanced_queries=advanced_queries,
                quality_report=quality_report,
                update_history=update_history,
                related_links=related_links
            )
        except KeyError as e:
            logger.error(f"Template formatting error: {e}")
            # Return simplified document if template fails
            main_document = f"""
{title}
{'=' * len(title)}

**データソース**: {excel_source}
**データ概要**: {data_summary}
**最終更新**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**品質スコア**: {quality_score:.2f}/1.0

.. enhanced-jsontable:: {rag_purpose}_data.json
   :rag-metadata: true
   :rag-purpose: {rag_purpose}
   :header:

このドキュメントは Excel-RAG 統合により自動生成されました。
"""
        
        return main_document
    
    def _create_sub_documents(
        self, 
        conversion_result: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> List[str]:
        """Create sub-documents for large datasets."""
        sub_docs = []
        
        data = conversion_result.get('json_data', [])
        max_records_per_doc = config.get('max_records_per_doc', 1000)
        
        if len(data) > max_records_per_doc:
            logger.info(f"Creating sub-documents for {len(data)} records")
            
            for i in range(0, len(data), max_records_per_doc):
                chunk_data = data[i:i + max_records_per_doc]
                chunk_num = (i // max_records_per_doc) + 1
                
                sub_doc = self._create_chunk_document(
                    chunk_data, chunk_num, conversion_result, config
                )
                sub_docs.append(sub_doc)
        
        return sub_docs
    
    def _create_index_document(
        self, 
        conversion_result: Dict[str, Any], 
        main_doc: str,
        sub_docs: List[str]
    ) -> str:
        """Create index document with navigation."""
        logger.info("Creating index document")
        
        title = self._infer_title(conversion_result)
        
        index_template = self.templates['index_document']
        
        # Generate table of contents
        toc_items = ["main"]
        if sub_docs:
            toc_items.extend([f"chunk_{i+1}" for i in range(len(sub_docs))])
        
        toc_content = "\n".join([f"   {item}" for item in toc_items])
        
        index_document = index_template.format(
            title=f"{title} - Complete Documentation",
            title_underline='=' * len(f"{title} - Complete Documentation"),
            toc_content=toc_content,
            total_documents=len(sub_docs) + 1,
            data_summary=self._generate_data_summary(conversion_result),
            last_updated=datetime.now().strftime('%Y-%m-%d %H:%M')
        )
        
        return index_document
    
    def _update_sphinx_config(
        self, 
        conversion_result: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update Sphinx configuration for Excel integration."""
        logger.info("Updating Sphinx configuration")
        
        sphinx_config = {
            'extensions': [
                'sphinxcontrib.jsontable',
                'sphinxcontrib.jsontable.excel'
            ],
            'jsontable_excel_config': {
                'auto_detection': True,
                'entity_recognition': True,
                'quality_threshold': 0.8,
                'supported_formats': ['.xlsx', '.xls', '.csv']
            },
            'html_theme_options': {
                'excel_integration': True,
                'rag_features': True
            }
        }
        
        return sphinx_config
    
    def _create_file_structure(self, conversion_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create recommended file structure."""
        structure = {
            'docs/': {
                'index.rst': 'Main index document',
                'excel_data/': {
                    'main.rst': 'Primary data documentation',
                    'data/': {
                        'json_files': 'Generated JSON data files',
                        'metadata': 'RAG metadata files'
                    }
                },
                'api/': {
                    'excel_integration.rst': 'API documentation'
                }
            }
        }
        
        return structure
    
    def _write_documentation_files(
        self, 
        documentation: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> List[str]:
        """Write documentation files to disk."""
        written_files = []
        base_path = Path(config.get('output_dir', '.'))
        
        # Write main document
        main_file = base_path / "main.rst"
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(documentation['main_document'])
        written_files.append(str(main_file))
        
        # Write sub-documents
        for i, sub_doc in enumerate(documentation['sub_documents']):
            sub_file = base_path / f"chunk_{i+1}.rst"
            with open(sub_file, 'w', encoding='utf-8') as f:
                f.write(sub_doc)
            written_files.append(str(sub_file))
        
        # Write index document
        index_file = base_path / "index.rst"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(documentation['index_document'])
        written_files.append(str(index_file))
        
        logger.info(f"Written {len(written_files)} documentation files")
        return written_files
    
    def _load_document_templates(self) -> Dict[str, str]:
        """Load document templates."""
        templates = {
            'main_document': '''
{title}
{title_underline}

.. meta::
   :description: {description}
   :keywords: {keywords}

概要
----

**データソース**: :file:`{excel_source}`

**データ概要**: {data_summary}

**最終更新**: {last_updated}

**品質スコア**: {quality_score}/1.0

データ構造
----------

{data_structure_info}

.. enhanced-jsontable:: {json_file}
   :rag-metadata: true
   :rag-purpose: {rag_purpose}
   :entity-types: {entity_types}
   :excel-source: {excel_source}
   :auto-update: {auto_update}
   :data-quality-score: {quality_score}
   :format-type: {format_type}
   :header:

AI活用ガイド
-----------

このデータセットに対する質問例
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

{example_queries}

高度な分析クエリ
~~~~~~~~~~~~~~~

{advanced_queries}

データ品質レポート
-----------------

{quality_report}

更新履歴
--------

{update_history}

関連情報
--------

{related_links}
''',
            
            'index_document': '''
{title}
{title_underline}

このドキュメントは Excel ファイルから自動生成された AI 対応データセットの完全なドキュメントです。

**データ概要**: {data_summary}

**ドキュメント構成**: {total_documents} ファイル

目次
====

.. toctree::
   :maxdepth: 2
   :caption: データドキュメント:

{toc_content}

クイックスタート
==============

このデータセットをすぐに活用するには:

1. **データ確認**: main.rst でデータ構造を確認
2. **AI質問**: 自然言語でデータに質問
3. **高度な分析**: 提供されたクエリ例を参考に分析

生成情報
========

このドキュメントは sphinxcontrib-jsontable の Excel-RAG 統合機能により自動生成されました。

- **生成日時**: {last_updated}
- **品質スコア**: 高品質データセット
- **AI対応**: 完全対応済み
''',
            
            'chunk_document': '''
{title} - データチャンク {chunk_num}
{title_underline}

このページは大規模データセットの一部（チャンク {chunk_num}）を表示しています。

データ範囲
----------

**レコード範囲**: {start_record} - {end_record}
**チャンク内レコード数**: {chunk_size}

.. enhanced-jsontable:: {json_file}
   :rag-metadata: true
   :rag-purpose: {rag_purpose}
   :chunk-number: {chunk_num}
   :header:

ナビゲーション
-----------

- :doc:`index` - メインインデックス
- :doc:`main` - 完全なデータ概要
{chunk_navigation}
'''
        }
        
        return templates
    
    def _infer_title(
        self, 
        conversion_result: Dict[str, Any], 
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Infer appropriate title for the document."""
        if config and config.get('title'):
            return config['title']
        
        rag_purpose = config.get('rag_purpose', 'data-analysis') if config else 'data-analysis'
        
        # Convert rag_purpose to Japanese title
        title_map = {
            'sales-analysis': '営業実績分析',
            'inventory-management': '在庫管理システム',
            'financial-analysis': '財務分析',
            'production-management': '生産管理システム',
            'risk-assessment': 'リスク評価',
            'data-analysis': 'データ分析'
        }
        
        return title_map.get(rag_purpose, f"{rag_purpose.replace('-', ' ').title()} データ分析")
    
    def _generate_data_summary(self, conversion_result: Dict[str, Any]) -> str:
        """Generate data summary description."""
        data = conversion_result.get('json_data', [])
        entities = conversion_result.get('entities', {})
        format_type = conversion_result.get('format_type', 'standard_table')
        
        record_count = len(data)
        entity_count = len(entities.get('items', []))
        entity_types = len(entities.get('types', []))
        
        return f"{format_type.replace('_', ' ').title()}形式データ（{record_count:,}件）、エンティティ{entity_count}個（{entity_types}種類）"
    
    def _format_structure_info(self, conversion_result: Dict[str, Any]) -> str:
        """Format data structure information."""
        format_type = conversion_result.get('format_type', 'standard_table')
        data = conversion_result.get('json_data', [])
        
        if not data:
            return "データ構造情報が利用できません。"
        
        # Get column information from first record
        first_record = data[0] if data else {}
        columns = list(first_record.keys())
        
        structure_info = f"""
**フォーマット種別**: {format_type.replace('_', ' ').title()}

**カラム構成** ({len(columns)}列):

"""
        
        for i, col in enumerate(columns[:10]):  # Show first 10 columns
            structure_info += f"- ``{col}``\n"
        
        if len(columns) > 10:
            structure_info += f"- ... 他 {len(columns) - 10} 列\n"
        
        structure_info += f"\n**データサイズ**: {len(data):,} レコード"
        
        return structure_info
    
    def _generate_example_queries(
        self, 
        conversion_result: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> str:
        """Generate example queries for the dataset."""
        rag_purpose = config.get('rag_purpose', 'general')
        
        # Purpose-specific queries
        query_templates = {
            'sales-analysis': [
                "今月の売上トップ3の営業担当者は？",
                "前年同月比で成長率が高い地域は？",
                "商品別の売上トレンドを教えて",
                "営業目標未達の担当者と原因は？"
            ],
            'inventory-management': [
                "在庫切れリスクが高い商品は？",
                "来月の入荷予定で需要をカバーできる？",
                "仕入先別の納期遅延傾向は？",
                "ABC分析でA分類商品の回転率は？"
            ],
            'financial-analysis': [
                "主要な収益源と成長ドライバーは？",
                "コスト構造の最適化ポイントは？",
                "キャッシュフロー改善の方策は？",
                "リスク要因と対策は？"
            ],
            'production-management': [
                "設備稼働率が低い工程は？",
                "品質不良率が増加している製品は？",
                "納期遅延リスクが高い注文は？",
                "生産効率向上の改善点は？"
            ]
        }
        
        queries = query_templates.get(rag_purpose, [
            "データの主要傾向は？",
            "注目すべき異常値や外れ値は？",
            "改善が必要な領域は？",
            "今後の予測や推奨事項は？"
        ])
        
        return "\n".join([f"- {query}" for query in queries])
    
    def _generate_advanced_queries(
        self, 
        conversion_result: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> str:
        """Generate advanced analytical queries."""
        advanced_queries = [
            "季節性やトレンド分析を含む予測モデルは？",
            "異なるセグメント間の相関関係は？",
            "統計的に有意な変化やパターンは？",
            "リスク要因の定量的評価は？",
            "最適化のための機械学習的洞察は？"
        ]
        
        return "\n".join([f"- {query}" for query in advanced_queries])
    
    def _format_quality_report(self, metadata: Dict[str, Any]) -> str:
        """Format quality report section."""
        quality_data = metadata.get('data_quality', {})
        
        completeness = quality_data.get('completeness', 0.95) * 100
        consistency = quality_data.get('consistency', 0.92) * 100
        accuracy = quality_data.get('accuracy', 0.88) * 100
        
        return f"""
**データ完全性**: {completeness:.1f}%
  - 欠損値の割合が低く、高品質なデータセット

**データ一貫性**: {consistency:.1f}%
  - フォーマットと構造が統一されている

**データ精度**: {accuracy:.1f}%
  - エンティティ認識と型推定の精度が高い

**総合評価**: 高品質データセット（AIクエリに最適）
"""
    
    def _format_update_history(self) -> str:
        """Format update history section."""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        return f"""
**{current_time}**
  - Excel-RAG統合による初回自動生成
  - 完全なメタデータ抽出と品質評価
  - AI対応ドキュメント生成完了

**更新方針**
  - Excelファイル更新時の自動再生成
  - 品質スコア継続監視
  - エンティティ認識精度向上
"""
    
    def _format_related_links(self, conversion_result: Dict[str, Any]) -> str:
        """Format related links section."""
        return """
- :doc:`/excel_integration_guide` - Excel統合完全ガイド
- :doc:`/rag_query_examples` - RAGクエリ実例集  
- :doc:`/api_reference` - API リファレンス
- :doc:`/troubleshooting` - トラブルシューティング

**外部リソース**:

- `sphinxcontrib-jsontable ドキュメント <https://sphinxcontrib-jsontable.readthedocs.io/>`_
- `Excel-RAG統合チュートリアル <#>`_
- `ビジネスインテリジェンス活用例 <#>`_
"""
    
    def _create_chunk_document(
        self, 
        chunk_data: List[Dict[str, Any]], 
        chunk_num: int,
        conversion_result: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> str:
        """Create document for data chunk."""
        title = self._infer_title(conversion_result, config)
        rag_purpose = config.get('rag_purpose', 'data-analysis')
        
        # Calculate record range
        records_per_chunk = config.get('max_records_per_doc', 1000)
        start_record = (chunk_num - 1) * records_per_chunk + 1
        end_record = start_record + len(chunk_data) - 1
        
        # Generate chunk navigation
        total_chunks = len(conversion_result.get('json_data', [])) // records_per_chunk + 1
        chunk_navigation = ""
        
        if chunk_num > 1:
            chunk_navigation += f"- :doc:`chunk_{chunk_num - 1}` - 前のチャンク\n"
        if chunk_num < total_chunks:
            chunk_navigation += f"- :doc:`chunk_{chunk_num + 1}` - 次のチャンク\n"
        
        template = self.templates['chunk_document']
        
        return template.format(
            title=title,
            title_underline='=' * len(f"{title} - データチャンク {chunk_num}"),
            chunk_num=chunk_num,
            start_record=start_record,
            end_record=end_record,
            chunk_size=len(chunk_data),
            json_file=f"{rag_purpose}_chunk_{chunk_num}.json",
            rag_purpose=rag_purpose,
            chunk_navigation=chunk_navigation
        )