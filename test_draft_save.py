import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'watchcase_tracker.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
import json

# Create a test client
client = Client()

# Test data for draft save based on the real data we saw in the logs
test_data = {
    "is_draft": True,
    "jig_qr_id": "",  # Empty for draft
    "faulty_slots": 0,
    "empty_slots": 0,
    "total_cases_loaded": 58,
    "plating_stock_numbers": ["1805NAR02"],
    "lot_ids": ["LID231220251013180015"],
    "lot_id_quantities": {"LID231220251013180015": 58},
    "primary_lot_id": "LID231220251013180015",
    "delink_tray_data": [
        {
            "tray_id": "",
            "lot_id": "LID231220251013180015", 
            "expected_usage": 10,
            "backend_optimal": False
        }
    ],
    "half_filled_tray_data": []
}

print("Testing draft save functionality...")
print(f"Sending data: {json.dumps(test_data, indent=2)}")

try:
    response = client.post('/jig_loading/save_jig_details/', 
                          data=json.dumps(test_data),
                          content_type='application/json')
    
    print(f"Response status code: {response.status_code}")
    
    if hasattr(response, 'content'):
        response_content = response.content.decode('utf-8')
        print(f"Response content: {response_content}")
        
        try:
            response_json = json.loads(response_content)
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
        except json.JSONDecodeError:
            print("Response is not valid JSON")
    
    if response.status_code == 200:
        print("✅ Draft save test PASSED!")
    else:
        print("❌ Draft save test FAILED!")
        
except Exception as e:
    print(f"❌ Error testing draft save: {e}")

# Test with another lot ID to verify multiple lots work
test_data2 = {
    "is_draft": True,
    "jig_qr_id": "",
    "faulty_slots": 0,
    "empty_slots": 0, 
    "total_cases_loaded": 40,
    "plating_stock_numbers": ["1805NAK02"],
    "lot_ids": ["LID231220251013310016"],
    "lot_id_quantities": {"LID231220251013310016": 40},
    "primary_lot_id": "LID231220251013310016",
    "delink_tray_data": [],
    "half_filled_tray_data": []
}

print("\n" + "="*50)
print("Testing second lot ID for draft save...")

try:
    response2 = client.post('/jig_loading/save_jig_details/', 
                           data=json.dumps(test_data2),
                           content_type='application/json')
    
    print(f"Response status code: {response2.status_code}")
    
    if hasattr(response2, 'content'):
        response_content2 = response2.content.decode('utf-8')
        print(f"Response content: {response_content2}")
        
        try:
            response_json2 = json.loads(response_content2)
            print(f"Response JSON: {json.dumps(response_json2, indent=2)}")
        except json.JSONDecodeError:
            print("Response is not valid JSON")
    
    if response2.status_code == 200:
        print("✅ Second draft save test PASSED!")
    else:
        print("❌ Second draft save test FAILED!")
        
except Exception as e:
    print(f"❌ Error testing second draft save: {e}")

print("\nTesting completed!")