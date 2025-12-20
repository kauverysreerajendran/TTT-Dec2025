#!/usr/bin/env python3
"""
Test script for "one reason per tray" validation logic
Tests the scenario where only one rejection reason should be allowed per tray
unless cumulative effect creates empty trays
"""
import requests
import json

def test_one_reason_per_tray():
    print("🧪 Testing 'One Reason Per Tray' Validation Logic")
    print("=" * 60)
    print("Scenario: R01 qty=1, then R02 qty=1 (both want JB-A00004)")
    print("Distribution: [4,12,12,12] - Total 1+1=2 doesn't empty tray")
    print("Expected: R01 allowed, R02 blocked (different reason, no empty tray)")
    print()
    
    BASE_URL = "http://127.0.0.1:8000"
    
    # Test Case 1: R01 with qty=1 (should be allowed - first use)
    print("Test Case 1: R01 with qty=1 using JB-A00004")
    session_allocations_empty = []
    params_r01 = {
        'tray_id': 'JB-A00004',
        'lot_id': 'L01-2024-001',  
        'rejection_qty': 1,
        'current_session_allocations': json.dumps(session_allocations_empty),
        'rejection_reason_id': 'R01'
    }
    
    try:
        response_r01 = requests.get(f"{BASE_URL}/input-screening/reject-check-tray-id-simple/", params=params_r01, timeout=10)
        result_r01 = response_r01.json()
        print(f"  ✅ Response: {response_r01.status_code}")
        print(f"  🔍 Valid: {result_r01.get('valid_for_rejection', False)}")
        print(f"  📝 Status: {result_r01.get('status_message', 'No message')}")
        if not result_r01.get('valid_for_rejection'):
            print(f"  🚨 Error: {result_r01.get('error', 'None')}")
        print()
    except Exception as e:
        print(f"  ❌ R01 Test failed: {e}")
        return
    
    # Test Case 2: R02 with qty=1, after R01 allocation (should be blocked - different reason)
    print("Test Case 2: R02 with qty=1 wanting to reuse JB-A00004")
    session_allocations_with_r01 = [
        {
            'tray_id': 'JB-A00004',
            'tray_ids': ['JB-A00004'],
            'rejection_reason_id': 'R01',
            'reason_id': 'R01',
            'rejection_qty': 1,
            'qty': 1,
            'reason_text': 'R01'
        }
    ]
    params_r02 = {
        'tray_id': 'JB-A00004',
        'lot_id': 'L01-2024-001',
        'rejection_qty': 1,
        'current_session_allocations': json.dumps(session_allocations_with_r01),
        'rejection_reason_id': 'R02'
    }
    
    try:
        response_r02 = requests.get(f"{BASE_URL}/input-screening/reject-check-tray-id-simple/", params=params_r02, timeout=10)
        result_r02 = response_r02.json()
        print(f"  ✅ Response: {response_r02.status_code}")
        print(f"  🔍 Valid: {result_r02.get('valid_for_rejection', False)}")
        print(f"  📝 Status: {result_r02.get('status_message', 'No message')}")
        print(f"  🚨 Error: {result_r02.get('error', 'None')}")
        print()
    except Exception as e:
        print(f"  ❌ R02 Test failed: {e}")
        return
    
    # Test Case 3: Test cumulative empty tray scenario (should allow different reason)
    print("Test Case 3: R02 with qty=3 after R01 qty=3 (cumulative 6 empties first tray)")
    session_allocations_with_r01_qty3 = [
        {
            'tray_id': 'JB-A00001',
            'tray_ids': ['JB-A00001'],
            'rejection_reason_id': 'R01',
            'reason_id': 'R01',
            'rejection_qty': 3,
            'qty': 3,
            'reason_text': 'R01'
        }
    ]
    params_cumulative = {
        'tray_id': 'JB-A00001',
        'lot_id': 'L01-2024-001',  # Lot with [6,12,12] distribution
        'rejection_qty': 3,
        'current_session_allocations': json.dumps(session_allocations_with_r01_qty3),
        'rejection_reason_id': 'R02'
    }
    
    try:
        response_cumulative = requests.get(f"{BASE_URL}/input-screening/reject-check-tray-id-simple/", params=params_cumulative, timeout=10)
        result_cumulative = response_cumulative.json()
        print(f"  ✅ Response: {response_cumulative.status_code}")
        print(f"  🔍 Valid: {result_cumulative.get('valid_for_rejection', False)}")
        print(f"  📝 Status: {result_cumulative.get('status_message', 'No message')}")
        if not result_cumulative.get('valid_for_rejection'):
            print(f"  🚨 Error: {result_cumulative.get('error', 'None')}")
        print()
    except Exception as e:
        print(f"  ❌ Cumulative Test failed: {e}")
    
    # Validation Results
    print("🎯 Validation Results:")
    print("-" * 40)
    
    # R01 should be allowed (first use)
    if result_r01.get('valid_for_rejection'):
        print("✅ R01: Correctly ALLOWED (first use of tray)")
    else:
        print("❌ R01: Should be allowed but was blocked")
    
    # R02 should be blocked (different reason, no empty tray)
    if not result_r02.get('valid_for_rejection'):
        if "different rejection reason" in result_r02.get('error', '').lower():
            print("✅ R02: Correctly BLOCKED (different reason, no empty tray)")
        else:
            print(f"⚠️ R02: Blocked but wrong reason: {result_r02.get('error', 'Unknown')}")
    else:
        print("❌ R02: Should be blocked but was allowed")
    
    # Cumulative should be allowed (empties tray)
    if result_cumulative.get('valid_for_rejection'):
        print("✅ Cumulative: Correctly ALLOWED (empty tray override)")
    else:
        print("❌ Cumulative: Should be allowed but was blocked")
    
    print("\n📋 Summary:")
    print(f"   One reason per tray rule: {'✅ Working' if not result_r02.get('valid_for_rejection') else '❌ Failed'}")
    print(f"   Empty tray override: {'✅ Working' if result_cumulative.get('valid_for_rejection') else '❌ Failed'}")

if __name__ == "__main__":
    try:
        test_one_reason_per_tray()
    except requests.exceptions.ConnectionError:
        print("🔌 Server not running - please start Django server first:")
        print("   python manage.py runserver")
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")