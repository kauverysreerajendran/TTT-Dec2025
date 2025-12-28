#!/usr/bin/env python
"""
Debug script to understand why lot_id lookup is failing
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('a:\\Workspace\\Watchcase Tracker Titan')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'watchcase_tracker.settings')
django.setup()

# Now import Django models
from modelmasterapp.models import TotalStockModel, ModelMaster
from Recovery_DP.models import RecoveryStockModel
from Jig_Loading.models import JigLoadingMaster

def debug_lot_id_lookup():
    """Debug why lot_id lookup is failing"""
    
    print("=== Debugging Lot ID Lookup ===")
    
    # Get a sample lot_id
    sample_stock = TotalStockModel.objects.filter(
        model_stock_no__model_no='1805'
    ).first()
    
    if not sample_stock:
        print("❌ No TotalStockModel found for model 1805")
        return
    
    print(f"📦 Sample lot_id: {sample_stock.lot_id}")
    print(f"   Model field type: {type(sample_stock.model_stock_no)}")
    print(f"   Model value: {sample_stock.model_stock_no}")
    print(f"   Model ID: {sample_stock.model_stock_no.id if sample_stock.model_stock_no else 'None'}")
    print(f"   Model No: {sample_stock.model_stock_no.model_no if sample_stock.model_stock_no else 'None'}")
    
    # Try the lookup that's failing
    print(f"\\n🔍 Testing JigLoadingMaster lookup:")
    jig_master = JigLoadingMaster.objects.filter(model_stock_no=sample_stock.model_stock_no).first()
    
    if jig_master:
        print(f"   ✅ Found: {jig_master}")
        print(f"   ✅ Capacity: {jig_master.jig_capacity}")
    else:
        print(f"   ❌ Not found")
        print(f"   🔍 Let's check all JigLoadingMaster records:")
        
        all_jig_masters = JigLoadingMaster.objects.all()
        for jm in all_jig_masters:
            print(f"      {jm.model_stock_no.id} -> {jm.model_stock_no.model_no} - {jm.jig_capacity}")
        
        print(f"\\n   🔍 Comparing IDs:")
        print(f"      TotalStock model_stock_no.id: {sample_stock.model_stock_no.id}")
        for jm in all_jig_masters:
            if jm.model_stock_no.model_no == '1805':
                print(f"      JigMaster model_stock_no.id: {jm.model_stock_no.id}")
                if jm.model_stock_no.id == sample_stock.model_stock_no.id:
                    print(f"      ✅ IDs match! This should work")
                else:
                    print(f"      ❌ IDs don't match")\n\nif __name__ == \"__main__\":\n    debug_lot_id_lookup()