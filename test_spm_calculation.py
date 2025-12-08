"""
SPM計算のテストスクリプト
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from decimal import Decimal

def test_spm_calculation():
    """SPM計算のテスト"""
    
    # テストケース: SPM60で7時間20分（440分）
    spm = 60  # 1分間に60個
    safety_factor = Decimal("0.7")
    minutes = 440  # 7時間20分
    
    # 実効SPM
    effective_spm = spm * safety_factor
    print(f"SPM: {spm}")
    print(f"安全係数: {safety_factor}")
    print(f"実効SPM: {effective_spm}")
    print(f"加工時間: {minutes}分（{minutes//60}時間{minutes%60}分）")
    
    # 数量計算
    quantity = int(float(effective_spm) * minutes)
    print(f"\n計算結果:")
    print(f"数量 = {minutes}分 × {effective_spm} = {quantity}個")
    
    # 逆算して確認
    calculated_minutes = float(Decimal(quantity) / effective_spm)
    print(f"\n逆算確認:")
    print(f"時間 = {quantity}個 ÷ {effective_spm} = {calculated_minutes:.2f}分")
    print(f"= {int(calculated_minutes//60)}時間{int(calculated_minutes%60)}分")
    
    # 期待値
    expected_quantity = 440 * 60 * 0.7
    print(f"\n期待値: {expected_quantity:.0f}個")
    print(f"一致: {'✓' if abs(quantity - expected_quantity) < 1 else '✗'}")

if __name__ == '__main__':
    test_spm_calculation()
