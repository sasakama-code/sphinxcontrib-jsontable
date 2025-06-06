RAG統合テスト例
================

この例では、新しい ``enhanced-jsontable`` ディレクティブのRAG機能をテストします。

従来のjsontableディレクティブ
-----------------------------

.. jsontable:: data/sample_users.json
   :header:

RAG機能付きjsontableディレクティブ
----------------------------------

基本的なRAG機能
~~~~~~~~~~~~~~~

.. enhanced-jsontable:: rag_test.json
   :header:
   :rag-enabled:

セマンティックチャンク機能付き
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. enhanced-jsontable:: rag_test.json
   :header:
   :rag-enabled:
   :semantic-chunks:
   :chunk-size: 2
   :metadata-tags: employee-data,test-table

インラインJSONでのRAG機能
~~~~~~~~~~~~~~~~~~~~~~~~~

.. enhanced-jsontable::
   :header:
   :rag-enabled:
   :semantic-chunks:
   :metadata-tags: product-catalog

   [
     {"product": "ノートPC", "price": 80000, "category": "電子機器", "stock": 15},
     {"product": "デスク", "price": 25000, "category": "家具", "stock": 8},
     {"product": "椅子", "price": 15000, "category": "家具", "stock": 12},
     {"product": "モニター", "price": 30000, "category": "電子機器", "stock": 20}
   ]

設定オプション説明
------------------

enhanced-jsontable ディレクティブの主要オプション:

:rag-enabled: RAG機能を有効化
:semantic-chunks: セマンティックチャンク生成を有効化
:chunk-size: チャンクあたりの行数（デフォルト: 10）
:metadata-tags: カスタムタグ（CSS class として出力）
:metadata-export: メタデータエクスポートファイルパス

後方互換性
----------

既存の ``jsontable`` ディレクティブは完全に互換性を保持:

.. jsontable:: rag_test.json
   :header:
   :limit: 2