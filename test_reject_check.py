#!/usr/bin/env python
"""
Test script for reject_check_tray_id_simple function
Tests the exact quantity match requirement for tray reuse during rejection.
"""

import os
import sys
import django
from django.conf import settings
from django.test import RequestFactory
from django.http import JsonResponse
import json
from unittest.mock import Mock, patch, MagicMock

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'watchcase_tracker.settings')
django.setup()

# Import the function and models
from InputScreening.views import reject_check_tray_id_simple
from InputScreening.models import IPTrayId, IP_Rejected_TrayScan
from modelmasterapp.models import TrayId

def create_mock_tray_id(tray_id, lot_id, tray_quantity=14, new_tray=False, delink_tray=False):
    """Create a mock TrayId object"""
    mock_tray = Mock(spec=TrayId)
    mock_tray.tray_id = tray_id
    mock_tray.lot_id = lot_id
    mock_tray.tray_quantity = tray_quantity
    mock_tray.new_tray = new_tray
    mock_tray.delink_tray = delink_tray
    mock_tray.tray_type = 'Normal'
    mock_tray.tray_capacity = 30
    return mock_tray

def create_mock_ip_tray(tray_id, lot_id, tray_quantity=14, rejected_tray=False, IP_tray_verified=True):
    """Create a mock IPTrayId object"""
    mock_tray = Mock(spec=IPTrayId)
    mock_tray.tray_id = tray_id
    mock_tray.lot_id = lot_id
    mock_tray.tray_quantity = tray_quantity
    mock_tray.rejected_tray = rejected_tray
    mock_tray.IP_tray_verified = IP_tray_verified
    mock_tray.new_tray = False
    mock_tray.delink_tray = False
    mock_tray.tray_type = 'Normal'
    mock_tray.tray_capacity = 30
    return mock_tray

def test_reject_check_tray_id_simple():
    """Test the reject_check_tray_id_simple function"""

    print("=== Testing reject_check_tray_id_simple function ===\n")

    # Test data setup
    lot_id = '2648WAA02'
    tray_id = 'NB-A00001'
    rejection_qty = 7  # Should fail - not exact match
    rejection_qty_exact = 14  # Should pass - exact match

    # Create mock trays
    mock_tray_id_obj = create_mock_tray_id(tray_id, lot_id, tray_quantity=14)
    mock_ip_tray_obj = create_mock_ip_tray(tray_id, lot_id, tray_quantity=14)

    # Mock the database queries
    with patch('InputScreening.views.TrayId.objects') as mock_trayid_manager, \
         patch('InputScreening.views.IPTrayId.objects') as mock_iptray_manager, \
         patch('InputScreening.views.IP_Rejected_TrayScan.objects') as mock_rejected_manager, \
         patch('InputScreening.views.validate_tray_type_compatibility') as mock_validate_type, \
         patch('InputScreening.views.get_available_quantities_with_session_allocations') as mock_get_available:

        # Setup TrayId mock
        mock_trayid_queryset = Mock()
        mock_trayid_queryset.first.return_value = mock_tray_id_obj
        mock_trayid_manager.filter.return_value = mock_trayid_queryset

        # Setup IPTrayId mock with side_effect
        def iptray_filter_side_effect(**kwargs):
            mock_queryset = Mock()
            if 'lot_id' in kwargs and 'rejected_tray' in kwargs:
                # tray_objs = IPTrayId.objects.filter(lot_id=current_lot_id, rejected_tray=False)
                # Make it iterable
                mock_queryset.__iter__ = Mock(return_value=iter([mock_ip_tray_obj]))
                return mock_queryset
            elif 'tray_id' in kwargs and 'lot_id' in kwargs:
                # tray_obj = IPTrayId.objects.filter(tray_id=tray_id, lot_id=current_lot_id).first()
                mock_queryset.first.return_value = mock_ip_tray_obj
                return mock_queryset
            elif 'tray_id' in kwargs and 'delink_tray' in kwargs:
                # tray_obj_delinked = IPTrayId.objects.filter(tray_id=tray_id, delink_tray=True).first()
                mock_queryset.first.return_value = None
                return mock_queryset
            else:
                mock_queryset.first.return_value = None
                return mock_queryset
        
        mock_iptray_manager.filter.side_effect = iptray_filter_side_effect

        # Setup IP_Rejected_TrayScan mock
        mock_rejected_queryset = Mock()
        mock_rejected_queryset.exclude.return_value.exists.return_value = False
        mock_rejected_manager.filter.return_value = mock_rejected_queryset

        mock_validate_type.return_value = {
            'is_compatible': True,
            'scanned_tray_type': 'Normal',
            'expected_tray_type': 'Normal'
        }
        mock_get_available.return_value = ([16, 14], None)  # Available quantities

        # Create request factory
        factory = RequestFactory()

        print("Test 1: Rejection qty=7, Tray qty=14 (should fail - not exact match)")
        # Test with rejection_qty=7 (should fail)
        request = factory.get(f'/reject_check_tray_id_simple/?tray_id={tray_id}&lot_id={lot_id}&rejection_qty={rejection_qty}&current_session_allocations=[]&rejection_reason_id=1&is_draft=false')
        response = reject_check_tray_id_simple(request)
        response_data = json.loads(response.content)

        print(f"Response: {response_data}")
        print(f"Valid for rejection: {response_data.get('valid_for_rejection')}")
        print(f"Status message: {response_data.get('status_message')}")
        if not response_data.get('valid_for_rejection'):
            print(f"Error: {response_data.get('error')}")

        assert not response_data.get('valid_for_rejection'), "Should not allow reuse when qty doesn't match"
        assert 'exact' in response_data.get('error', '').lower(), "Should mention exact match requirement"

        print("\n✅ Test 1 PASSED: Correctly rejected non-exact match\n")

        print("Test 2: Rejection qty=14, Tray qty=14 (should pass - exact match)")
        # Test with rejection_qty=14 (should pass)
        request = factory.get(f'/reject_check_tray_id_simple/?tray_id={tray_id}&lot_id={lot_id}&rejection_qty={rejection_qty_exact}&current_session_allocations=[]&rejection_reason_id=1&is_draft=false')
        response = reject_check_tray_id_simple(request)
        response_data = json.loads(response.content)

        print(f"Response: {response_data}")
        print(f"Valid for rejection: {response_data.get('valid_for_rejection')}")
        print(f"Status message: {response_data.get('status_message')}")

        assert response_data.get('valid_for_rejection'), "Should allow reuse when qty matches exactly"
        assert 'exact' in response_data.get('status_message', '').lower() or 'match' in response_data.get('status_message', '').lower(), "Should indicate exact match"

        print("\n✅ Test 2 PASSED: Correctly allowed exact match\n")

    print("=== All tests passed! ===")
    print("\nBug Analysis:")
    print("- Before fix: The function likely allowed reuse for any quantity less than or equal to tray capacity")
    print("- After fix: Now requires exact quantity match for tray reuse during rejection")
    print("- This prevents partial reuse of trays, ensuring trays are either fully used or not used for rejection")

if __name__ == '__main__':
    test_reject_check_tray_id_simple()