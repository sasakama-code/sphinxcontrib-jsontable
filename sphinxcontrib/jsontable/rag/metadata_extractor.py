"""
RAGMetadataExtractor - JSONテーブルからRAG用基本メタデータを抽出

このモジュールは、JSONデータから検索・AI理解に必要な基本メタデータを抽出します。
PLaMo-Embedding-1Bとの連携に最適化された日本語特化設計です。

特徴:
- JSON Schema自動生成
- セマンティック要約作成
- 検索キーワード抽出
- エンティティマッピング
- カスタムタグ対応

Created: 2025-06-07
Author: Claude Code Assistant
"""

import hashlib
import json
import logging
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

JsonData = dict[str, Any] | list[dict[str, Any]] | list[Any]


@dataclass
class BasicMetadata:
    """基本メタデータの構造"""

    table_id: str
    schema: dict[str, Any]
    semantic_summary: str
    search_keywords: list[str]
    entity_mapping: dict[str, str]
    custom_tags: list[str]
    data_statistics: dict[str, Any]
    embedding_ready_text: str
    generation_timestamp: str


class RAGMetadataExtractor:
    """JSONテーブルからRAG用メタデータを抽出するクラス

    Phase 1のコア機能として、Phase 2のAdvancedMetadataGeneratorの
    基盤となるメタデータを提供します。
    """

    def __init__(self):
        """メタデータ抽出器を初期化"""
        self.japanese_patterns = self._init_japanese_patterns()
        self.type_inference_patterns = self._init_type_patterns()

    def _init_japanese_patterns(self) -> dict[str, list[str]]:
        """日本語認識パターンを初期化"""
        return {
            "name_indicators": [
                "名前",
                "name",
                "氏名",
                "姓名",
                "full_name",
                "fullname",
                "担当者",
                "person",
                "社員",
                "employee",
                "staff",
            ],
            "date_indicators": [
                "日付",
                "date",
                "年月日",
                "時間",
                "time",
                "datetime",
                "作成日",
                "created",
                "更新日",
                "updated",
                "登録日",
            ],
            "money_indicators": [
                "価格",
                "price",
                "金額",
                "amount",
                "料金",
                "fee",
                "cost",
                "給与",
                "salary",
                "売上",
                "sales",
                "予算",
                "budget",
            ],
            "organization_indicators": [
                "会社",
                "company",
                "部署",
                "department",
                "課",
                "section",
                "組織",
                "organization",
                "team",
                "チーム",
                "事業部",
            ],
        }

    def _init_type_patterns(self) -> dict[str, Any]:
        """型推論パターンを初期化"""
        return {
            "email_pattern": re.compile(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            ),
            "phone_pattern": re.compile(r"^(\+81|0)\d{1,4}-?\d{1,4}-?\d{3,4}$"),
            "url_pattern": re.compile(r"^https?://[^\s/$.?#].[^\s]*$"),
            "japanese_name_pattern": re.compile(r"^[一-龯]{1,4}[　\s]*[一-龯]{1,3}$"),
            "katakana_pattern": re.compile(r"^[ア-ン]+$"),
            "number_with_unit_pattern": re.compile(
                r"^\d+(\.\d+)?(円|¥|%|個|件|人|歳)$"
            ),
        }

    def extract(self, json_data: JsonData, options: dict[str, Any]) -> BasicMetadata:
        """JSONデータからRAG用基本メタデータを抽出

        Args:
            json_data: 処理対象のJSONデータ
            options: ディレクティブから渡されるオプション

        Returns:
            BasicMetadata: 抽出されたメタデータ

        Raises:
            ValueError: データ形式が不正な場合
        """
        try:
            # データの有効性チェック
            if json_data is None:
                raise ValueError("データがNullです")

            # 基本情報の生成
            table_id = self._generate_table_id(json_data, options)
            schema = self._extract_schema(json_data)
            semantic_summary = self._generate_semantic_summary(json_data, schema)
            search_keywords = self._extract_search_keywords(json_data, schema)
            entity_mapping = self._map_entities(json_data, schema)
            custom_tags = self._parse_custom_tags(options.get("metadata-tags", ""))
            data_statistics = self._calculate_basic_statistics(json_data)
            embedding_ready_text = self._prepare_embedding_text(json_data, schema)

            return BasicMetadata(
                table_id=table_id,
                schema=schema,
                semantic_summary=semantic_summary,
                search_keywords=search_keywords,
                entity_mapping=entity_mapping,
                custom_tags=custom_tags,
                data_statistics=data_statistics,
                embedding_ready_text=embedding_ready_text,
                generation_timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"メタデータ抽出エラー: {e}")
            raise ValueError(f"メタデータ抽出に失敗しました: {e}") from e

    def _generate_table_id(self, json_data: JsonData, options: dict[str, Any]) -> str:
        """テーブルの一意IDを生成"""
        # データの内容ベースでハッシュ生成
        data_str = json.dumps(json_data, ensure_ascii=False, sort_keys=True)
        data_hash = hashlib.md5(data_str.encode("utf-8")).hexdigest()[:8]

        # タイムスタンプ要素を追加
        timestamp = datetime.now().strftime("%Y%m%d")

        return f"table_{timestamp}_{data_hash}"

    def _extract_schema(self, data: JsonData) -> dict[str, Any]:
        """JSON Schemaを生成

        OpenAPIやJSONLD仕様に準拠した構造化されたスキーマを生成
        """
        if isinstance(data, list) and data:
            # 配列データの場合
            sample_item = data[0]
            if isinstance(sample_item, dict):
                properties = {}

                # 全アイテムを分析してより正確な型推論
                for key in sample_item:
                    property_info = self._analyze_property(key, data, sample_item[key])
                    properties[key] = property_info

                return {
                    "type": "array",
                    "title": "データテーブル",
                    "description": f"{len(data)}件のレコードを含むテーブル",
                    "items": {
                        "type": "object",
                        "properties": properties,
                        "required": list(sample_item.keys()),
                    },
                }
            else:
                # プリミティブ型の配列
                item_type = self._infer_type(sample_item)
                return {
                    "type": "array",
                    "title": "データリスト",
                    "description": f"{len(data)}件の{item_type}のリスト",
                    "items": {"type": item_type},
                }
        elif isinstance(data, dict):
            # オブジェクトデータの場合
            properties = {}
            for key, value in data.items():
                property_info = self._analyze_property(key, [data], value)
                properties[key] = property_info

            return {
                "type": "object",
                "title": "データオブジェクト",
                "properties": properties,
                "required": list(data.keys()),
            }
        else:
            # その他の場合
            return {
                "type": self._infer_type(data),
                "title": "データ",
                "description": "単一値データ",
            }

    def _analyze_property(
        self, key: str, data_list: list[Any], sample_value: Any
    ) -> dict[str, Any]:
        """プロパティの詳細分析"""
        base_type = self._infer_type(sample_value)
        property_info = {
            "type": base_type,
            "title": self._generate_human_readable_title(key),
            "description": self._generate_property_description(key, sample_value),
        }

        # 日本語特化の型分類
        semantic_type = self._infer_semantic_type(key, sample_value)
        if semantic_type:
            property_info["x-semantic-type"] = semantic_type

        # 値の範囲や統計を追加（数値の場合）
        if base_type in ["integer", "number"] and isinstance(data_list, list):
            stats = self._calculate_numeric_stats(key, data_list)
            if stats:
                property_info.update(stats)

        # 列挙可能な値の場合はenumを追加
        if isinstance(data_list, list) and len(data_list) > 1:
            unique_values = self._get_unique_values(key, data_list)
            if len(unique_values) <= 10 and len(unique_values) > 1:
                property_info["enum"] = unique_values
                property_info["x-enum-count"] = len(unique_values)

        return property_info

    def _infer_type(self, value: Any) -> str:
        """基本型を推論"""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, str):
            # 特殊な文字列パターンをチェック
            if self.type_inference_patterns["email_pattern"].match(value):
                return "string"  # format: email を追加可能
            elif self.type_inference_patterns["url_pattern"].match(value):
                return "string"  # format: uri を追加可能
            elif self.type_inference_patterns["number_with_unit_pattern"].match(value):
                return "string"  # 単位付き数値
            else:
                return "string"
        elif isinstance(value, list | tuple):
            return "array"
        elif isinstance(value, dict):
            return "object"
        else:
            return "string"

    def _infer_semantic_type(self, key: str, value: Any) -> str | None:
        """意味的な型を推論（日本語特化）"""
        key_lower = key.lower()

        # 名前パターン
        for pattern in self.japanese_patterns["name_indicators"]:
            if pattern in key_lower:
                if isinstance(value, str) and self.type_inference_patterns[
                    "japanese_name_pattern"
                ].match(value):
                    return "japanese_person_name"
                return "person_name"

        # 日付パターン
        for pattern in self.japanese_patterns["date_indicators"]:
            if pattern in key_lower:
                return "temporal"

        # 金額パターン
        for pattern in self.japanese_patterns["money_indicators"]:
            if pattern in key_lower:
                return "monetary"

        # 組織パターン
        for pattern in self.japanese_patterns["organization_indicators"]:
            if pattern in key_lower:
                return "organization"

        # 値の内容ベースの推論
        if isinstance(value, str):
            if self.type_inference_patterns["phone_pattern"].match(value):
                return "phone_number"
            elif self.type_inference_patterns["email_pattern"].match(value):
                return "email_address"
            elif self.type_inference_patterns["katakana_pattern"].match(value):
                return "katakana_text"

        return None

    def _generate_human_readable_title(self, key: str) -> str:
        """人間が読みやすいタイトルを生成"""
        # 一般的な変換規則
        title_mapping = {
            "id": "ID",
            "name": "名前",
            "age": "年齢",
            "email": "メールアドレス",
            "phone": "電話番号",
            "address": "住所",
            "company": "会社名",
            "department": "部署",
            "salary": "給与",
            "price": "価格",
            "date": "日付",
            "created_at": "作成日時",
            "updated_at": "更新日時",
        }

        return title_mapping.get(key.lower(), key)

    def _generate_property_description(self, key: str, sample_value: Any) -> str:
        """プロパティの説明を生成"""
        semantic_type = self._infer_semantic_type(key, sample_value)
        base_type = self._infer_type(sample_value)

        if semantic_type == "japanese_person_name":
            return "日本語の人名"
        elif semantic_type == "temporal":
            return "日付・時刻データ"
        elif semantic_type == "monetary":
            return "金額・価格データ"
        elif semantic_type == "organization":
            return "組織・部署名"
        elif base_type == "string":
            return "テキストデータ"
        elif base_type in ["integer", "number"]:
            return "数値データ"
        else:
            return f"{base_type}型のデータ"

    def _calculate_numeric_stats(
        self, key: str, data_list: list[Any]
    ) -> dict[str, Any] | None:
        """数値プロパティの統計を計算"""
        try:
            values = []
            for item in data_list:
                if isinstance(item, dict) and key in item:
                    value = item[key]
                    if isinstance(value, int | float) and value is not None:
                        values.append(value)

            if len(values) < 2:
                return None

            return {
                "minimum": min(values),
                "maximum": max(values),
                "x-average": sum(values) / len(values),
                "x-count": len(values),
            }
        except Exception:
            return None

    def _get_unique_values(self, key: str, data_list: list[Any]) -> list[Any]:
        """指定されたキーのユニークな値を取得"""
        values = []
        for item in data_list:
            if isinstance(item, dict) and key in item:
                value = item[key]
                if value is not None and value not in values:
                    values.append(value)
        return values[:10]  # 最大10個まで

    def _generate_semantic_summary(self, data: JsonData, schema: dict[str, Any]) -> str:
        """セマンティック要約を生成"""
        try:
            if isinstance(data, list):
                item_count = len(data)
                if item_count == 0:
                    return "空のデータテーブル"

                if isinstance(data[0], dict):
                    columns = list(data[0].keys())
                    main_columns = columns[:3]  # 主要なカラムのみ表示
                    column_text = "、".join(main_columns)
                    if len(columns) > 3:
                        column_text += f"など{len(columns)}カラム"

                    # データの種類を推定
                    entity_type = self._estimate_entity_type(columns)
                    if entity_type:
                        return f"{entity_type}テーブル: {item_count}件、{column_text}を含む"
                    else:
                        return f"データテーブル: {item_count}件、{column_text}を含む"
                else:
                    return f"データリスト: {item_count}件の値"
            elif isinstance(data, dict):
                keys = list(data.keys())
                key_text = "、".join(keys[:3])
                if len(keys) > 3:
                    key_text += f"など{len(keys)}項目"
                return f"データオブジェクト: {key_text}を含む"
            else:
                return "単一データ値"
        except Exception:
            return "構造化データ"

    def _estimate_entity_type(self, columns: list[str]) -> str | None:
        """カラム名から推定されるエンティティタイプ"""
        column_text = " ".join(columns).lower()

        # 従業員・人事データ
        if any(
            keyword in column_text
            for keyword in ["name", "名前", "employee", "社員", "staff", "氏名"]
        ) and any(
            keyword in column_text
            for keyword in ["salary", "給与", "department", "部署"]
        ):
            return "従業員"

        # 商品・製品データ
        if any(
            keyword in column_text
            for keyword in ["product", "商品", "price", "価格", "category", "カテゴリ"]
        ):
            return "商品"

        # 売上・取引データ
        if any(
            keyword in column_text
            for keyword in ["sales", "売上", "amount", "金額", "date", "日付"]
        ):
            return "売上"

        # 顧客データ
        if any(
            keyword in column_text
            for keyword in ["customer", "顧客", "client", "contact", "連絡先"]
        ):
            return "顧客"

        return None

    def _extract_search_keywords(
        self, data: JsonData, schema: dict[str, Any]
    ) -> list[str]:
        """検索用キーワードを抽出"""
        keywords = set()

        # スキーマベースのキーワード
        if isinstance(data, list) and data and isinstance(data[0], dict):
            # カラム名ベースのキーワード
            for key in data[0]:
                keywords.add(key)
                title = self._generate_human_readable_title(key)
                if title != key:
                    keywords.add(title)
        elif isinstance(data, list) and len(data) == 0:
            # 空リストの場合はデフォルトキーワード
            keywords.add("空データ")
            keywords.add("テーブル")

        # 値ベースのキーワード（文字列値から）
        text_values = self._extract_text_values(data)
        for value in text_values[:20]:  # 最大20個
            if isinstance(value, str) and len(value) > 1 and len(value) <= 50:
                # 日本語テキストの場合は単語分割は行わず、そのまま追加
                keywords.add(value.strip())

        # エンティティタイプベースのキーワード
        entity_type = self._estimate_entity_type(
            list(data[0].keys())
            if isinstance(data, list) and data and isinstance(data[0], dict)
            else []
        )
        if entity_type:
            keywords.add(entity_type)
            keywords.add(f"{entity_type}データ")
            keywords.add(f"{entity_type}情報")

        return list(keywords)[:50]  # 最大50個のキーワード

    def _extract_text_values(self, data: JsonData) -> list[str]:
        """データから文字列値を抽出"""
        text_values = []

        def extract_from_obj(obj: Any) -> None:
            if isinstance(obj, str):
                text_values.append(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    extract_from_obj(value)
            elif isinstance(obj, list):
                for item in obj[:10]:  # 最初の10個のみ
                    extract_from_obj(item)

        extract_from_obj(data)
        return text_values

    def _map_entities(self, data: JsonData, schema: dict[str, Any]) -> dict[str, str]:
        """エンティティマッピングを作成"""
        entity_mapping = {}

        if isinstance(data, list) and data and isinstance(data[0], dict):
            for key, value in data[0].items():
                semantic_type = self._infer_semantic_type(key, value)
                if semantic_type:
                    entity_mapping[key] = semantic_type
                else:
                    # デフォルトのマッピング
                    base_type = self._infer_type(value)
                    entity_mapping[key] = f"generic_{base_type}"

        return entity_mapping

    def _parse_custom_tags(self, tags_str: str) -> list[str]:
        """カスタムタグを解析"""
        if not tags_str:
            return []

        # コンマ、セミコロン、スペースで分割
        tags = re.split(r"[,;]\s*|\s+", tags_str.strip())
        return [tag.strip() for tag in tags if tag.strip()]

    def _calculate_basic_statistics(self, data: JsonData) -> dict[str, Any]:
        """基本統計情報を計算"""
        stats = {
            "record_count": 0,
            "column_count": 0,
            "data_types": {},
            "completeness": {},
        }

        if isinstance(data, list):
            stats["record_count"] = len(data)
            if data and isinstance(data[0], dict):
                stats["column_count"] = len(data[0].keys())

                # データ型の分布
                type_counts = Counter()
                completeness = {}

                for key in data[0]:
                    values = [item.get(key) for item in data if isinstance(item, dict)]
                    non_null_values = [v for v in values if v is not None]

                    # 完全性（非NULL率）
                    completeness[key] = (
                        len(non_null_values) / len(values) if values else 0
                    )

                    # データ型の分布
                    for value in non_null_values[:10]:  # サンプリング
                        value_type = self._infer_type(value)
                        type_counts[value_type] += 1

                stats["data_types"] = dict(type_counts)
                stats["completeness"] = completeness

        elif isinstance(data, dict):
            stats["record_count"] = 1
            stats["column_count"] = len(data.keys())

        return stats

    def _prepare_embedding_text(self, data: JsonData, schema: dict[str, Any]) -> str:
        """埋め込み用テキストを準備

        PLaMo-Embedding-1B向けに最適化されたテキスト形式を生成
        """
        text_parts = []

        # スキーマ情報
        if "title" in schema:
            text_parts.append(f"データ種別: {schema['title']}")

        if "description" in schema:
            text_parts.append(f"説明: {schema['description']}")

        # 構造情報
        if isinstance(data, list) and data:
            text_parts.append(f"レコード数: {len(data)}件")

            if isinstance(data[0], dict):
                columns = list(data[0].keys())
                text_parts.append(f"カラム: {', '.join(columns[:5])}")

                # サンプルデータ（最初の2件）
                for i, item in enumerate(data[:2]):
                    if isinstance(item, dict):
                        sample_text = self._format_record_for_embedding(item)
                        text_parts.append(f"サンプル{i + 1}: {sample_text}")

        elif isinstance(data, dict):
            sample_text = self._format_record_for_embedding(data)
            text_parts.append(f"データ: {sample_text}")

        return " | ".join(text_parts)

    def _format_record_for_embedding(self, record: dict[str, Any]) -> str:
        """レコードを埋め込み用テキストにフォーマット"""
        parts = []
        for key, value in record.items():
            if value is not None:
                # 日本語での自然な表現
                readable_key = self._generate_human_readable_title(key)
                if isinstance(value, str):
                    parts.append(f"{readable_key}={value}")
                else:
                    parts.append(f"{readable_key}={value!s}")

        return ", ".join(parts[:5])  # 最大5個のフィールド
