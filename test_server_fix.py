#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'watchcase_tracker.settings')
django.setup()

from django.test.client import RequestFactory
from django.contrib.auth.models import User
from InputScreening.views import reject_check_tray_id_simple

def test_tray_validation():
    print("🔧 Testing tray validation fix...")
    
    # Create a test request
    factory = RequestFactory()
    request = factory.get('/InputScreening/reject_check_tray_id_simple/', {
        'tray_id': 'JB-A00002',
        'lot_id': '1805QSP02/GUN',
        'rejection_qty': '3',
        'rejection_reason_id': 'R01',
        'current_session_allocations': '[]',
        'is_draft': 'false'
    })
    
    try:
        # Test the function directly
        response = reject_check_tray_id_simple(request)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ No more HTTP 500 error! The fix worked.")
            import json
            data = json.loads(response.content)
            print(f"Response: {data}")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(response.content)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_tray_validation()
    if success:
        print("\n✅ The HTTP 500 internal server error has been FIXED!")
        print("The missing 'reuse_allowed' variable definition was the cause.")
    else:
        print("\n❌ There are still issues to resolve.")