import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'watchcase_tracker.settings')
django.setup()

from Jig_Loading.models import JigLoadingMaster
from modelmasterapp.models import ModelMaster, ModelMasterCreation, TotalStockModel

# Get the lot data
tsm = TotalStockModel.objects.filter(lot_id='LID231220251013180015').first()
mmc = tsm.batch_id
mm = mmc.model_stock_no

print(f"Looking for JigLoadingMaster with model_stock_no = {mm} (id: {mm.id})")

# Try direct match
jlm = JigLoadingMaster.objects.filter(model_stock_no=mm).first()
print(f"Found by direct match: {jlm}")

if not jlm:
    print("Trying by model_no...")
    jlm2 = JigLoadingMaster.objects.filter(model_stock_no__model_no=mm.model_no).first()
    print(f"Found by model_no: {jlm2}")

# Show all JigLoadingMaster entries
print("\nAll JigLoadingMaster entries:")
for jlm_entry in JigLoadingMaster.objects.all():
    print(f"  JLM id: {jlm_entry.id}, ModelMaster id: {jlm_entry.model_stock_no.id}, model_no: {jlm_entry.model_stock_no.model_no}")

print(f"\nTarget ModelMaster id: {mm.id}, model_no: {mm.model_no}")