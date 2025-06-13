"""JsonTableDirectiveのExcel統合テスト."""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
import pandas as pd
from docutils import nodes
from sphinx.util.docutils import docutils_namespace

# Excel対応がある場合のみテストを実行
try:
    from sphinxcontrib.jsontable.excel_data_loader import ExcelDataLoader
    from sphinxcontrib.jsontable.directives import JsonTableDirective
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


@pytest.mark.skipif(not EXCEL_AVAILABLE, reason="Excel support not available")
class TestExcelIntegration:
    """JsonTableDirectiveのExcel統合テスト。"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される。"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """各テストメソッドの後に実行される。"""
        # 一時ディレクトリのクリーンアップ
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_excel(self, filename: str, data: list, has_header: bool = True) -> str:
        """テスト用Excelファイルを作成。
        
        Args:
            filename: ファイル名(.xlsxを含む)
            data: 書き込むデータ(2D list)
            has_header: ヘッダー行があるかどうか
            
        Returns:
            str: 作成されたファイルのパス
        """
        file_path = os.path.join(self.temp_dir, filename)
        
        if has_header:
            df = pd.DataFrame(data[1:], columns=data[0])
        else:
            df = pd.DataFrame(data)
        
        df.to_excel(file_path, index=False, header=has_header)
        return file_path
    
    def create_mock_env(self):
        """Sphinx環境のモックを作成。"""
        class MockConfig:
            jsontable_max_rows = 10000
        
        class MockEnv:
            def __init__(self, srcdir):
                self.srcdir = srcdir
                self.config = MockConfig()
        
        return MockEnv(self.temp_dir)
    
    def test_excel_file_detection(self):
        """Excelファイル検出のテスト。"""
        # テストデータ作成
        test_data = [
            ["Name", "Age", "City"],
            ["Alice", "25", "Tokyo"],
            ["Bob", "30", "Osaka"]
        ]
        excel_path = self.create_test_excel("test.xlsx", test_data)
        
        # ディレクティブインスタンス作成
        env = self.create_mock_env()
        
        with docutils_namespace():
            directive = JsonTableDirective(
                name="jsontable",
                arguments=[os.path.basename(excel_path)],
                options={"header": True},
                content=[],
                lineno=1,
                content_offset=0,
                block_text="",
                state=None,
                state_machine=None
            )
            directive.env = env
            directive.excel_loader = ExcelDataLoader(self.temp_dir)
            
            # JSON形式に変換されたデータを確認
            json_data = directive._load_json_data()
            
            assert isinstance(json_data, list)
            assert len(json_data) == 2
            assert json_data[0]["Name"] == "Alice"
            assert json_data[0]["Age"] == "25"
            assert json_data[1]["Name"] == "Bob"
    
    def test_excel_without_header(self):
        """ヘッダーなしExcelファイルのテスト。"""
        test_data = [
            ["Alice", "25", "Tokyo"],
            ["Bob", "30", "Osaka"]
        ]
        excel_path = self.create_test_excel("test_no_header.xlsx", test_data, False)
        
        env = self.create_mock_env()
        
        with docutils_namespace():
            directive = JsonTableDirective(
                name="jsontable",
                arguments=[os.path.basename(excel_path)],
                options={},
                content=[],
                lineno=1,
                content_offset=0,
                block_text="",
                state=None,
                state_machine=None
            )
            directive.env = env
            directive.excel_loader = ExcelDataLoader(self.temp_dir)
            
            # 2D配列形式のデータを確認
            json_data = directive._load_json_data()
            
            assert isinstance(json_data, list)
            assert len(json_data) == 2
            assert json_data[0] == ["Alice", "25", "Tokyo"]
            assert json_data[1] == ["Bob", "30", "Osaka"]
    
    def test_json_compatibility(self):
        """JSON形式との互換性テスト。"""
        # 同じデータをExcel形式とJSON形式で作成
        test_data = [
            ["Name", "Age", "City"],
            ["Alice", "25", "Tokyo"],
            ["Bob", "30", "Osaka"]
        ]
        
        # Excelファイル作成
        excel_path = self.create_test_excel("test.xlsx", test_data)
        
        # JSONファイル作成
        json_data = [
            {"Name": "Alice", "Age": "25", "City": "Tokyo"},
            {"Name": "Bob", "Age": "30", "City": "Osaka"}
        ]
        json_path = os.path.join(self.temp_dir, "test.json")
        import json as json_module
        with open(json_path, "w") as f:
            json_module.dump(json_data, f)
        
        env = self.create_mock_env()
        
        # Excelからの読み込み
        with docutils_namespace():
            excel_directive = JsonTableDirective(
                name="jsontable",
                arguments=[os.path.basename(excel_path)],
                options={"header": True},
                content=[],
                lineno=1,
                content_offset=0,
                block_text="",
                state=None,
                state_machine=None
            )
            excel_directive.env = env
            excel_directive.excel_loader = ExcelDataLoader(self.temp_dir)
            
            excel_json_data = excel_directive._load_json_data()
        
        # JSONからの読み込み
        with docutils_namespace():
            json_directive = JsonTableDirective(
                name="jsontable",
                arguments=[os.path.basename(json_path)],
                options={"header": True},
                content=[],
                lineno=1,
                content_offset=0,
                block_text="",
                state=None,
                state_machine=None
            )
            json_directive.env = env
            
            json_json_data = json_directive._load_json_data()
        
        # 両方のデータが同じ構造であることを確認
        assert len(excel_json_data) == len(json_json_data)
        assert excel_json_data[0]["Name"] == json_json_data[0]["Name"]
        assert excel_json_data[0]["Age"] == json_json_data[0]["Age"]
    
    def test_error_handling(self):
        """エラーハンドリングのテスト。"""
        env = self.create_mock_env()
        
        # 存在しないExcelファイル
        with docutils_namespace():
            directive = JsonTableDirective(
                name="jsontable",
                arguments=["nonexistent.xlsx"],
                options={},
                content=[],
                lineno=1,
                content_offset=0,
                block_text="",
                state=None,
                state_machine=None
            )
            directive.env = env
            directive.excel_loader = ExcelDataLoader(self.temp_dir)
            
            with pytest.raises(FileNotFoundError):
                directive._load_json_data()
    
    def test_xlsx_and_xls_support(self):
        """xlsx と xls 両方の対応テスト。"""
        test_data = [
            ["Name", "Age"],
            ["Alice", "25"],
            ["Bob", "30"]
        ]
        
        env = self.create_mock_env()
        
        # .xlsx ファイルのテスト
        xlsx_path = self.create_test_excel("test.xlsx", test_data)
        
        with docutils_namespace():
            directive = JsonTableDirective(
                name="jsontable",
                arguments=[os.path.basename(xlsx_path)],
                options={"header": True},
                content=[],
                lineno=1,
                content_offset=0,
                block_text="",
                state=None,
                state_machine=None
            )
            directive.env = env
            directive.excel_loader = ExcelDataLoader(self.temp_dir)
            
            xlsx_data = directive._load_json_data()
            assert len(xlsx_data) == 2
            assert xlsx_data[0]["Name"] == "Alice"
        
        # .xls ファイルのテスト（パンダスがサポートしている場合）
        try:
            xls_path = os.path.join(self.temp_dir, "test.xls")
            df = pd.DataFrame(test_data[1:], columns=test_data[0])
            df.to_excel(xls_path, index=False, engine='xlwt')
            
            with docutils_namespace():
                directive = JsonTableDirective(
                    name="jsontable",
                    arguments=[os.path.basename(xls_path)],
                    options={"header": True},
                    content=[],
                    lineno=1,
                    content_offset=0,
                    block_text="",
                    state=None,
                    state_machine=None
                )
                directive.env = env
                directive.excel_loader = ExcelDataLoader(self.temp_dir)
                
                xls_data = directive._load_json_data()
                assert len(xls_data) == 2
                assert xls_data[0]["Name"] == "Alice"
        
        except ImportError:
            # xlwt が利用できない場合はスキップ
            pytest.skip("xlwt not available for .xls file testing")


@pytest.mark.skipif(EXCEL_AVAILABLE, reason="Test Excel unavailable error")
def test_excel_support_unavailable():
    """Excel機能が利用できない場合のエラーテスト。"""
    # この場合は実際のテストは困難なため、
    # フラグによる条件分岐のテストのみ
    assert EXCEL_AVAILABLE is False