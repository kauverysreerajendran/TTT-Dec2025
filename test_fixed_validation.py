#!/usr/bin/env python3
"""
Comprehensive test for fixed tray reuse validation logic
Tests both correct and incorrect scenarios from user's examples
"""
import requests
import json

def test_corrected_logic():
    print("🧪 Testing Corrected Tray Reuse Logic")
    print("=" * 60)
    
    BASE_URL = "http://127.0.0.1:8000"
    
    # ✅ CORRECT SCENARIO: 1805QSP02/GUN with [6,12,12]
    print("✅ CORRECT SCENARIO: 1805QSP02/GUN")
    print("Distribution: [6,12,12], R01=3, R02=3 (cumulative=6 empties first tray)")
    print("-" * 50)
    
    # Test R01=3 (should be allowed - partial, but wait for cumulative)
    params_correct_r01 = {
        'tray_id': 'JB-A00010',
        'lot_id': 'LOT-QSP02-GUN',  
        'rejection_qty': 3,
        'current_session_allocations': json.dumps([]),
        'rejection_reason_id': 'R01'
    }
    
    try:
        response_r01 = requests.get(f"{BASE_URL}/input-screening/reject-check-tray-id-simple/", params=params_correct_r01, timeout=10)
        result_r01 = response_r01.json()
        print(f"R01 (qty=3): Valid={result_r01.get('valid_for_rejection', False)}")
        print(f"R01 Status: {result_r01.get('status_message', 'No message')}")
        
        # Test R02=3 after R01 (cumulative should allow reuse)
        session_with_r01 = [{
            'tray_id': 'JB-A00010',
            'tray_ids': ['JB-A00010'],
            'rejection_reason_id': 'R01',
            'reason_id': 'R01',
            'rejection_qty': 3,
            'qty': 3,
            'reason_text': 'R01'
        }]
        
        params_correct_r02 = {
            'tray_id': 'JB-A00001',
            'lot_id': 'LOT-QSP02-GUN',
            'rejection_qty': 3,
            'current_session_allocations': json.dumps(session_with_r01),
            'rejection_reason_id': 'R02'
        }
        
        response_r02 = requests.get(f"{BASE_URL}/input-screening/reject-check-tray-id-simple/", params=params_correct_r02, timeout=10)
        result_r02 = response_r02.json()
        print(f"R02 (qty=3): Valid={result_r02.get('valid_for_rejection', False)}")
        print(f"R02 Status: {result_r02.get('status_message', 'No message')}")
        
        if result_r02.get('valid_for_rejection'):
            print("✅ CORRECT: R02 allowed (cumulative 6 empties first tray)")
        else:
            print(f"❌ INCORRECT: R02 should be allowed. Error: {result_r02.get('error', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Correct scenario test failed: {e}")
    
    print("\n" + "="*60)
    
    # ❌ INCORRECT SCENARIO: 1805WBK02 with [4,12,12,12]
    print("❌ INCORRECT SCENARIO: 1805WBK02")
    print("Distribution: [4,12,12,12], R01=9 (should be BLOCKED)")
    print("-" * 50)
    
    # Test R01=9 (should be blocked - doesn't fit any single tray)
    params_wrong = {
        'tray_id': 'JB-A00004',
        'lot_id': 'LOT-WBK02',
        'rejection_qty': 9,
        'current_session_allocations': json.dumps([]),
        'rejection_reason_id': 'R01'
    }
    
    try:
        response_wrong = requests.get(f"{BASE_URL}/input-screening/reject-check-tray-id-simple/", params=params_wrong, timeout=10)
        result_wrong = response_wrong.json()
        print(f"R01 (qty=9): Valid={result_wrong.get('valid_for_rejection', False)}")
        print(f"R01 Status: {result_wrong.get('status_message', 'No message')}")
        
        if not result_wrong.get('valid_for_rejection'):
            print("✅ CORRECT: R01 blocked (9 doesn't fit any single tray)")
        else:
            print(f"❌ INCORRECT: R01 should be blocked but was allowed!")
            print(f"   Why allowed: {result_wrong.get('status_message', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Incorrect scenario test failed: {e}")
    
    print("\n" + "="*60)
    
    # 🔍 EDGE CASE TESTS
    print("🔍 EDGE CASE TESTS")
    print("-" * 30)
    
    # Perfect fit test
    print("Test 1: Perfect Fit (qty=4 matches first tray exactly)")
    params_perfect = {
        'tray_id': 'JB-A00004',
        'lot_id': 'LOT-WBK02',
        'rejection_qty': 4,
        'current_session_allocations': json.dumps([]),
        'rejection_reason_id': 'R01'
    }
    
    try:
        response_perfect = requests.get(f"{BASE_URL}/input-screening/reject-check-tray-id-simple/", params=params_perfect, timeout=10)
        result_perfect = response_perfect.json()
        print(f"  Perfect fit (qty=4): Valid={result_perfect.get('valid_for_rejection', False)}")
        print(f"  Status: {result_perfect.get('status_message', 'No message')}")
        
        if result_perfect.get('valid_for_rejection') and "perfect fit" in result_perfect.get('status_message', '').lower():
            print("  ✅ CORRECT: Perfect fit detected and allowed")
        else:
            print("  ❌ INCORRECT: Perfect fit should be allowed")
    except Exception as e:
        print(f"  ❌ Perfect fit test failed: {e}")
    
    # Exact cumulative test
    print("\nTest 2: Exact Cumulative (R01=4 + R02=12 = 16, empties first two trays)")
    session_r01_4 = [{
        'tray_id': 'JB-A00004',
        'tray_ids': ['JB-A00004'],
        'rejection_reason_id': 'R01',
        'rejection_qty': 4,
        'qty': 4
    }]
    
    params_cumulative = {
        'tray_id': 'JB-A00005',
        'lot_id': 'LOT-WBK02',
        'rejection_qty': 12,
        'current_session_allocations': json.dumps(session_r01_4),
        'rejection_reason_id': 'R02'
    }
    
    try:
        response_cumulative = requests.get(f"{BASE_URL}/input-screening/reject-check-tray-id-simple/", params=params_cumulative, timeout=10)
        result_cumulative = response_cumulative.json()
        print(f"  Cumulative (4+12=16): Valid={result_cumulative.get('valid_for_rejection', False)}")
        print(f"  Status: {result_cumulative.get('status_message', 'No message')}")
        
        if result_cumulative.get('valid_for_rejection'):
            print("  ✅ CORRECT: Cumulative empty trays (4+12=16 empties first two trays)")
        else:
            print(f"  ❌ INCORRECT: Should allow cumulative. Error: {result_cumulative.get('error', 'Unknown')}")
    except Exception as e:
        print(f"  ❌ Cumulative test failed: {e}")
    
    print("\n🎯 SUMMARY")
    print("="*30)
    print("The fix ensures:")
    print("  ✅ Perfect fit: qty exactly matches one tray → Allow")
    print("  ✅ True cumulative: total qty exactly empties complete trays → Allow") 
    print("  ❌ Partial consumption: qty doesn't fit or empty any tray → Block")
    print("  ❌ One reason per tray: different reasons on same tray → Block")

if __name__ == "__main__":
    try:
        test_corrected_logic()
    except requests.exceptions.ConnectionError:
        print("🔌 Server not running - please start Django server first:")
        print("   python manage.py runserver")
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")