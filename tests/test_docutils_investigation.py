#!/usr/bin/env python3
"""
docutilsノード構造の実際の調査
TableBuilderの動作とノード構造を詳細に理解するため
"""

from docutils import nodes

from sphinxcontrib.jsontable.directives import TableBuilder


def investigate_table_structure():
    """TableBuilderが生成するノード構造の詳細調査"""

    # テストデータ
    test_data = [
        ["名前", "年齢", "部署"],  # ヘッダー
        ["田中太郎", "30", "開発部"],
        ["佐藤花子", "25", "営業部"],
    ]

    # TableBuilderでテーブル生成
    builder = TableBuilder()
    table_node = builder.build(test_data, has_header=True)

    # ノード構造の詳細出力
    print("=== Table Node Structure Investigation ===")
    print(f"Table type: {type(table_node)}")
    print(f"Table attributes: {table_node.attributes}")
    print(f"Table classes: {table_node.attributes.get('classes', [])}")

    # 子ノードの調査
    print("\n=== Child Nodes ===")
    for i, child in enumerate(table_node.children):
        print(
            f"Child {i}: {type(child)} - {child.tagname if hasattr(child, 'tagname') else 'no tagname'}"
        )

        if isinstance(child, nodes.tgroup):
            print(f"  tgroup attributes: {child.attributes}")
            print(f"  tgroup cols: {child.get('cols', 'not set')}")

            # tgroupの子ノード
            for j, tgroup_child in enumerate(child.children):
                print(
                    f"    tgroup child {j}: {type(tgroup_child)} - {tgroup_child.tagname if hasattr(tgroup_child, 'tagname') else 'no tagname'}"
                )

                if isinstance(tgroup_child, nodes.thead):
                    print(f"      thead attributes: {tgroup_child.attributes}")
                    # ヘッダー行の調査
                    for k, row in enumerate(tgroup_child.children):
                        if isinstance(row, nodes.row):
                            print(
                                f"        header row {k} attributes: {row.attributes}"
                            )
                            for idx, entry in enumerate(row.children):
                                if isinstance(entry, nodes.entry):
                                    print(
                                        f"          header entry {idx}: {entry.attributes}"
                                    )
                                    # paragraph内容
                                    for para in entry.children:
                                        if isinstance(para, nodes.paragraph):
                                            print(
                                                f"            text: '{para.astext()}'"
                                            )

                elif isinstance(tgroup_child, nodes.tbody):
                    print(f"      tbody attributes: {tgroup_child.attributes}")
                    # ボディ行の調査（最初の行のみ）
                    if tgroup_child.children:
                        first_row = tgroup_child.children[0]
                        if isinstance(first_row, nodes.row):
                            print(
                                f"        first row attributes: {first_row.attributes}"
                            )
                            for idx, entry in enumerate(first_row.children):
                                if isinstance(entry, nodes.entry):
                                    print(f"          entry {idx}: {entry.attributes}")


def test_custom_attributes():
    """カスタム属性付与のテスト"""

    print("\n=== Custom Attributes Test ===")

    test_data = [["テストデータ"]]
    builder = TableBuilder()
    table_node = builder.build(test_data, has_header=False)

    # カスタム属性の付与テスト
    print("Before adding custom attributes:")
    print(f"  attributes: {table_node.attributes}")

    # 様々な方法でカスタム属性を追加
    table_node.attributes["data-source"] = "test"
    table_node.attributes["data-rag-enabled"] = "true"
    table_node.attributes["data-metadata"] = '{"type": "test", "rows": 1}'

    # classesの追加
    if "classes" not in table_node.attributes:
        table_node.attributes["classes"] = []
    table_node.attributes["classes"].extend(["rag-enabled", "json-table"])

    print("After adding custom attributes:")
    print(f"  attributes: {table_node.attributes}")
    print(f"  classes: {table_node.attributes.get('classes', [])}")

    # ネストしたカスタム属性のテスト
    tgroup = table_node.children[0] if table_node.children else None
    if tgroup:
        tgroup.attributes["data-structure-level"] = "column-group"
        print(
            f"  tgroup custom attribute: {tgroup.attributes.get('data-structure-level')}"
        )


def test_rag_metadata_attachment():
    """RAGメタデータ付与の実践テスト"""

    print("\n=== RAG Metadata Attachment Test ===")

    # サンプルJSONデータシミュレーション
    sample_json_metadata = {
        "source_file": "employees.json",
        "schema": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "department": {"type": "string"},
                },
            },
        },
        "row_count": 2,
        "columns": ["name", "age", "department"],
    }

    test_data = [
        ["name", "age", "department"],
        ["田中太郎", "30", "開発部"],
        ["佐藤花子", "25", "営業部"],
    ]

    builder = TableBuilder()
    table_node = builder.build(test_data, has_header=True)

    # RAGメタデータの付与
    import json

    rag_metadata = {
        "data-source-type": "json",
        "data-source-file": sample_json_metadata["source_file"],
        "data-row-count": str(sample_json_metadata["row_count"]),
        "data-column-count": str(len(sample_json_metadata["columns"])),
        "data-schema": json.dumps(sample_json_metadata["schema"], ensure_ascii=False),
        "data-rag-version": "1.0",
        "data-generator": "sphinxcontrib-jsontable-rag",
    }

    # メタデータ適用
    table_node.attributes.update(rag_metadata)
    table_node.attributes.setdefault("classes", []).extend(
        ["rag-enhanced", "json-source"]
    )

    print("RAG Enhanced Table Attributes:")
    for key, value in table_node.attributes.items():
        if key.startswith("data-"):
            if len(str(value)) > 100:
                print(f"  {key}: {str(value)[:100]}...")
            else:
                print(f"  {key}: {value}")

    print(f"Classes: {table_node.attributes.get('classes', [])}")


if __name__ == "__main__":
    investigate_table_structure()
    test_custom_attributes()
    test_rag_metadata_attachment()
    print("\n=== Investigation Complete ===")
