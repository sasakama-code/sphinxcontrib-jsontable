"""Phase 2: Range Specification機能の簡略化されたTDDテスト.

Task 2.2: `:range:` オプション実装の未実装機能確認テスト
"""

import pytest

def test_range_functionality_not_implemented():
    """Range機能が未実装であることを確認するテスト（RED段階）。"""
    
    # ExcelDataLoaderをインポートして未実装メソッドをチェック
    try:
        from sphinxcontrib.jsontable.excel_data_loader import ExcelDataLoader
        loader = ExcelDataLoader()
        
        # load_from_excel_with_range メソッドが存在しないことを確認
        assert not hasattr(loader, 'load_from_excel_with_range'), \
            "load_from_excel_with_range method should not exist yet (RED phase)"
        
        # _parse_range_specification メソッドが存在しないことを確認
        assert not hasattr(loader, '_parse_range_specification'), \
            "_parse_range_specification method should not exist yet (RED phase)"
        
        print("✅ RED段階確認: Range Specification機能は未実装")
        
    except ImportError:
        pytest.skip("Excel support not available")

def test_directive_range_option_not_implemented():
    """JsonTableDirectiveで:range:オプションが未実装であることを確認。"""
    
    try:
        from sphinxcontrib.jsontable.directives import JsonTableDirective
        
        # option_specに'range'が存在しないことを確認
        assert 'range' not in JsonTableDirective.option_spec, \
            "Range option should not exist yet (RED phase)"
        
        print("✅ RED段階確認: :range:オプションは未実装")
        
    except ImportError:
        pytest.skip("Excel support not available")

if __name__ == "__main__":
    test_range_functionality_not_implemented()
    test_directive_range_option_not_implemented()
    print("🔴 RED段階完了: Range Specification機能は未実装のため、GREEN段階に進みます")