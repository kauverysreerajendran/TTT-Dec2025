#!/usr/bin/env python3
"""
Test the specific scenario from the user's screenshot:
- Lot: 1805WBK02 with qty=40, distribution [4,12,12,12]
- R01: VERSION MIXUP, qty=4, using JB-A00004
- Expected: Should allow reuse because qty=4 exactly empties first tray
"""
import requests
import json

def test_perfect_fit_scenario():
    print("🧪 Testing Perfect Fit Scenario (User's Real Case)")
    print("=" * 55)
    print("Scenario: R01 with qty=4 using JB-A00004 in lot with [4,12,12,12]")
    print("Expected: Should allow reuse (perfect fit empties first tray)")
    print()
    
    # Test parameters matching user's screenshot
    params = {
        'tray_id': 'JB-A00004',
        'lot_id': 'L01-2024-001',  # Replace with actual lot if known
        'rejection_qty': 4,  # Exact match with first tray qty
        'current_session_allocations': '[]',  # Empty - first rejection
        'rejection_reason_id': 'R01'
    }
    
    try:
        response = requests.get('http://127.0.0.1:8000/input-screening/reject-check-tray-id-simple/', params=params, timeout=10)
        result = response.json()
        
        print("📋 Test Results:")
        print("-" * 30)
        print(f"✅ Response received: {response.status_code}")
        print(f"🔍 Valid for rejection: {result.get('valid_for_rejection', False)}")
        print(f"📝 Status message: {result.get('status_message', 'No message')}")
        print(f"🚨 Error (if any): {result.get('error', 'None')}")
        print()
        
        # Validation
        if result.get('valid_for_rejection'):
            print("🎉 SUCCESS: JB-A00004 reuse now ALLOWED for R01!")
            if "perfect fit" in result.get('status_message', '').lower():
                print("✨ BONUS: Perfect fit detection working!")
            print("👍 User should now see ✅ instead of ❌ Reuse restricted")
        else:
            print("❌ STILL BLOCKED: Something is still preventing reuse")
            print(f"💡 Debug info: {result}")
            
    except requests.exceptions.ConnectionError:
        print("🔌 Server not running - please start Django server first:")
        print("   python manage.py runserver")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
if __name__ == "__main__":
    test_perfect_fit_scenario()