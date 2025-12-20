#!/usr/bin/env python3
"""
Test script for cumulative tray reuse validation logic
Tests the scenario where R01: 3 + R02: 3 = 6 total should empty first tray
"""
import requests
import json

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_LOT_ID = "L01-2024-001"  # Use your real lot ID
TEST_TRAY_ID = "JB-A00001"    # Use your real tray ID

def test_cumulative_validation():
    """Test the cumulative validation scenario"""
    print("🧪 Testing Cumulative Tray Reuse Validation")
    print("=" * 50)
    
    # Test Case 1: R01 with qty=3 (should be blocked initially)
    print("Test Case 1: R01 with qty=3")
    session_allocations_r01 = []
    params_r01 = {
        'tray_id': TEST_TRAY_ID,
        'lot_id': TEST_LOT_ID, 
        'rejection_qty': 3,
        'current_session_allocations': json.dumps(session_allocations_r01),
        'rejection_reason_id': 'R01'
    }
    
    try:
        response_r01 = requests.get(f"{BASE_URL}/inputscreening/reject_check_tray_id_simple/", params=params_r01)
        result_r01 = response_r01.json()
        print(f"R01 Result: {result_r01}")
        print(f"R01 Valid: {result_r01.get('valid_for_rejection', False)}")
        print(f"R01 Status: {result_r01.get('status_message', 'Unknown')}")
        print()
    except Exception as e:
        print(f"❌ R01 Test failed: {e}")
        return
    
    # Test Case 2: R02 with qty=3, after R01 allocation (should be allowed due to cumulative effect)
    print("Test Case 2: R02 with qty=3 after R01 allocation")
    session_allocations_r02 = [
        {
            'reason_text': 'VERSION MIXUP',
            'qty': 3,
            'tray_ids': [TEST_TRAY_ID],
            'tray_id': TEST_TRAY_ID
        }
    ]
    params_r02 = {
        'tray_id': TEST_TRAY_ID,
        'lot_id': TEST_LOT_ID,
        'rejection_qty': 3,
        'current_session_allocations': json.dumps(session_allocations_r02),
        'rejection_reason_id': 'R02'
    }
    
    try:
        response_r02 = requests.get(f"{BASE_URL}/input-screening/reject-check-tray-id-simple/", params=params_r02)
        result_r02 = response_r02.json()
        print(f"R02 Result: {result_r02}")
        print(f"R02 Valid: {result_r02.get('valid_for_rejection', False)}")
        print(f"R02 Status: {result_r02.get('status_message', 'Unknown')}")
        print()
    except Exception as e:
        print(f"❌ R02 Test failed: {e}")
        return
    
    # Validation
    print("🎯 Validation Results:")
    print("-" * 30)
    
    if result_r02.get('valid_for_rejection', False):
        print("✅ SUCCESS: R02 reuse allowed with cumulative effect!")
        print("   Expected: R01(3) + R02(3) = 6 empties first tray [6,12,12] → [0,12,12]")
        if "cumulative" in result_r02.get('status_message', '').lower():
            print("✅ BONUS: Status message indicates cumulative logic worked!")
    else:
        print("❌ FAILED: R02 should be allowed due to cumulative empty tray effect")
        print(f"   Error: {result_r02.get('error', 'Unknown error')}")
    
    print("\n📋 Test Summary:")
    print(f"   R01 (qty=3): {'✅ Handled' if response_r01.status_code == 200 else '❌ Failed'}")
    print(f"   R02 (qty=3): {'✅ Allowed' if result_r02.get('valid_for_rejection') else '❌ Blocked'}")
    
if __name__ == "__main__":
    test_cumulative_validation()