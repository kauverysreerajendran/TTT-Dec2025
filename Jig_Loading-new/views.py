from django.views.generic import *
from modelmasterapp.models import *
from .models import Jig, JigLoadingMaster, JigLoadTrayId, JigDetails, JigLoadingManualDraft
from rest_framework.decorators import *
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from math import ceil
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import logging
import json




# Jig Loading Pick Table - Main View (display completed batch from Brass Audit Complete table)


@method_decorator(login_required, name='dispatch') 
class JigView(TemplateView):
    template_name = "JigLoading/Jig_Picktable.html"
    
    # No of Trays Calculation
    def get_tray_capacity(stock):
        # Try batch first
        if stock.batch_id and getattr(stock.batch_id, 'tray_capacity', None):
            return stock.batch_id.tray_capacity
        # Try model_master
        if stock.model_stock_no and getattr(stock.model_stock_no, 'tray_capacity', None):
            return stock.model_stock_no.tray_capacity
        # Try tray_type
        if stock.batch_id and hasattr(stock.batch_id, 'tray_type') and stock.batch_id.tray_type:
            try:
                tray_type_obj = TrayType.objects.get(tray_type=stock.batch_id.tray_type)
                return tray_type_obj.tray_capacity
            except TrayType.DoesNotExist:
                pass
        # Try JigLoadingMaster
        jig_master = JigLoadingMaster.objects.filter(model_stock_no=stock.model_stock_no).first()
        if jig_master and getattr(jig_master, 'tray_capacity', None):
            return jig_master.tray_capacity
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Only show lots NOT completed (do not change row order)
        total_stock_qs = (
            TotalStockModel.objects.filter(brass_audit_accptance=True, Jig_Load_completed=False)
            | TotalStockModel.objects.filter(brass_audit_few_cases_accptance=True, Jig_Load_completed=False)
            | TotalStockModel.objects.filter(brass_audit_rejection=True, Jig_Load_completed=False)
        )

        master_data = []
        for stock in total_stock_qs:
            plating_stk_no = (
                getattr(stock.batch_id, 'plating_stk_no', None)
                or getattr(stock.model_stock_no, 'plating_stk_no', None)
            )
            polishing_stk_no = (
                getattr(stock.batch_id, 'polishing_stk_no', None)
                or getattr(stock.model_stock_no, 'polishing_stk_no', None)
            )

            tray_capacity = JigView.get_tray_capacity(stock)
            jig_type = ''
            jig_capacity = ''
            if stock.model_stock_no:
                jig_master = JigLoadingMaster.objects.filter(model_stock_no=stock.model_stock_no).first()
                if jig_master:
                    jig_type = jig_master.jig_type
                    jig_capacity = jig_master.jig_capacity

            lot_qty = stock.total_stock or 0
            no_of_trays = 0
            if tray_capacity and tray_capacity > 0:
                no_of_trays = (lot_qty // tray_capacity) + (1 if lot_qty % tray_capacity else 0)

            # --- Fix: Use jig_draft for correct lot status ---
            if getattr(stock, 'released_flag', False):
                lot_status = 'Yet to Released'
                lot_status_class = 'lot-status-yet-released'
            elif getattr(stock, 'jig_draft', False):
                lot_status = 'Draft'
                lot_status_class = 'lot-status-draft'
            else:
                lot_status = 'Yet to Start'
                lot_status_class = 'lot-status-yet'

            # --- Process Status logic ---
            if lot_status == 'Draft':
                process_status = 'Loading'
                process_status_class = 'process-status-half-filled'
            else:
                process_status = 'Pending'
                process_status_class = 'process-status-pending'

            master_data.append({
                'batch_id': stock.batch_id.batch_id if stock.batch_id else '',
                'stock_lot_id': stock.lot_id,
                'model_stock_no__model_no': stock.model_stock_no.model_no if stock.model_stock_no else '',
                'plating_stk_no': plating_stk_no,
                'polishing_stk_no': polishing_stk_no,
                'plating_color': stock.plating_color.plating_color if stock.plating_color else '',
                'polish_finish': stock.polish_finish.polish_finish if stock.polish_finish else '',
                'version__version_internal': stock.version.version_internal if stock.version else '',
                'no_of_trays': no_of_trays,
                'display_qty': lot_qty,
                'jig_capacity': jig_capacity if jig_capacity else '',
                'jig_type': jig_type,
                'model_images': [img.master_image.url for img in stock.model_stock_no.images.all()] if stock.model_stock_no else [],
                'brass_audit_last_process_date_time': stock.brass_audit_last_process_date_time,
                'last_process_module': stock.last_process_module,
                'lot_status': lot_status,
                'lot_status_class': lot_status_class,
                'process_status': process_status,
                'process_status_class': process_status_class,
                # Add jig hold/release fields for persistent state
                'jig_hold_lot': getattr(stock, 'jig_hold_lot', False),
                'jig_holding_reason': getattr(stock, 'jig_holding_reason', ''),
                'jig_release_reason': getattr(stock, 'jig_release_reason', ''),
            })
        context['master_data'] = master_data
        return context 





# Tray Info API View
class TrayInfoView(APIView):
    def get(self, request, *args, **kwargs):
        lot_id = request.GET.get('lot_id')
        batch_id = request.GET.get('batch_id')
        trays = TrayId.objects.filter(lot_id=lot_id, batch_id__batch_id=batch_id).values('tray_id', 'tray_quantity')
        tray_list = [{'tray_id': t['tray_id'], 'tray_quantity': t['tray_quantity']} for t in trays]
        return Response({'trays': tray_list})
       
# Tray Validation API View   
class TrayValidateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        batch_id = request.data.get('batch_id')
        lot_id = request.data.get('lot_id')
        tray_ids = request.data.get('tray_ids', [])
        if not batch_id or not lot_id:
            return Response({'validated': False, 'message': 'batch_id and lot_id required'}, status=status.HTTP_400_BAD_REQUEST)

        allocated_trays = JigLoadTrayId.objects.filter(
            lot_id=lot_id,
            batch_id__batch_id=batch_id
        ).values_list('tray_id', flat=True)
        allocated_tray_set = set(str(t) for t in allocated_trays)
        scanned_tray_set = set(str(t) for t in tray_ids)

        if not allocated_tray_set:
            return Response({'validated': False, 'message': 'No allocated trays found for this batch.'}, status=status.HTTP_400_BAD_REQUEST)

        if not scanned_tray_set.issubset(allocated_tray_set):
            invalid = scanned_tray_set - allocated_tray_set
            return Response({
                'validated': False,
                'message': f'Tray IDs not allocated: {", ".join(invalid)}',
                'allocated_trays': list(allocated_tray_set),
                'scanned_trays': list(scanned_tray_set)
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({'validated': True, 'message': 'Tray validation successful'}, status=status.HTTP_200_OK)


# Class for "Add Model" button data
class JigAddModalDataView(TemplateView):
    """
    Comprehensive modal data preparation for "Add Jig" functionality.
    Handles all data selection, calculation, and validation logic.
    """
    def get(self, request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        batch_id = request.GET.get('batch_id')
        lot_id = request.GET.get('lot_id')
        jig_qr_id = request.GET.get('jig_qr_id')
        
        logger.info(f"🔍 JigAddModal: Processing batch_id={batch_id}, lot_id={lot_id}, jig_qr_id={jig_qr_id}")
        
        # Fetch TotalStockModel for batch/lot
        stock = get_object_or_404(TotalStockModel, lot_id=lot_id)
        batch = stock.batch_id
        model_master = batch.model_stock_no if batch else None
        
        # Comprehensive plating_stk_no resolution logic
        plating_stk_no = self._resolve_plating_stock_number(batch, model_master)
        
        # Comprehensive data preparation
        modal_data = self._prepare_modal_data(request, batch, model_master, stock, jig_qr_id, lot_id)

        # Enhanced logging for debugging
        logger.info(f"📊 Modal data prepared: plating_stk_no={plating_stk_no}, jig_type={modal_data.get('jig_type')}, jig_capacity={modal_data.get('jig_capacity')}")
        
        return JsonResponse({
            'form_title': f"Jig Loading / Plating Stock No: {plating_stk_no or 'N/A'}",
            'jig_id': jig_qr_id,
            'nickel_bath_type': modal_data.get('nickel_bath_type'),
            'tray_type': modal_data.get('tray_type'),
            'broken_buildup_hooks': modal_data.get('broken_buildup_hooks'),
            'empty_hooks': modal_data.get('empty_hooks'),
            'loaded_cases_qty': modal_data.get('loaded_cases_qty'),
            'jig_capacity': modal_data.get('jig_capacity'),
            'jig_type': modal_data.get('jig_type'),
            'loaded_hooks': modal_data.get('loaded_hooks'),
            'add_model_enabled': modal_data.get('add_model_enabled'),
            'can_save': modal_data.get('can_save'),
            'model_images': modal_data.get('model_images'),
            'delink_table': modal_data.get('delink_table'),
            'logs': modal_data.get('logs'),
            'no_of_cycle': modal_data.get('no_of_cycle'),
            'plating_stk_no': plating_stk_no,
            'modal_validation': modal_data.get('modal_validation'),
            'ui_config': modal_data.get('ui_config')
        })
    
    def _resolve_plating_stock_number(self, batch, model_master):
        """
        Centralized plating stock number resolution logic.
        Priority: ModelMasterCreation.plating_stk_no -> ModelMaster.plating_stk_no
        """
        plating_stk_no = ''
        if batch and batch.plating_stk_no:
            plating_stk_no = batch.plating_stk_no
        elif batch and batch.model_stock_no and batch.model_stock_no.plating_stk_no:
            plating_stk_no = batch.model_stock_no.plating_stk_no
        return plating_stk_no
    
    def _prepare_modal_data(self, request, batch, model_master, stock, jig_qr_id, lot_id):
        """
        Comprehensive modal data preparation including all calculations and validations.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Initialize all modal data variables
        modal_data = {
            'nickel_bath_type': None,
            'tray_type': 'Normal',
            'broken_buildup_hooks': 0,
            'empty_hooks': 0,
            'loaded_cases_qty': 0,
            'jig_capacity': 0,
            'jig_type': None,
            'loaded_hooks': 0,
            'add_model_enabled': False,
            'model_images': [],
            'delink_table': [],
            'no_of_cycle': 1,
            'modal_validation': {},
            'ui_config': {},
            'can_save': False,
        }
        
        # Get jig details if exists
        jig_details = JigDetails.objects.filter(jig_qr_id=jig_qr_id, lot_id=lot_id).first()
        
        # Fetch Jig Type and Capacity from JigLoadingMaster
        if model_master:
            jig_master = JigLoadingMaster.objects.filter(model_stock_no=model_master).first()
            if jig_master:
                modal_data['jig_type'] = jig_master.jig_type
                modal_data['jig_capacity'] = jig_master.jig_capacity

        # Set tray type from batch
        modal_data['tray_type'] = batch.tray_type if batch else 'Normal'

        # Nickel Bath Type and jig calculations
        if jig_details:
            modal_data['nickel_bath_type'] = jig_details.ep_bath_type
            modal_data['broken_buildup_hooks'] = jig_details.faulty_slots
            modal_data['loaded_cases_qty'] = jig_details.loaded_quantity
            modal_data['loaded_hooks'] = jig_details.loaded_quantity
            modal_data['empty_hooks'] = modal_data['jig_capacity'] - modal_data['loaded_cases_qty'] if modal_data['jig_capacity'] else 0
            modal_data['no_of_cycle'] = jig_details.no_of_cycle
        else:
            # Auto-fill for new entries with comprehensive defaults
            modal_data['nickel_bath_type'] = "Bright"  # Default
            modal_data['loaded_cases_qty'] = stock.total_stock
            modal_data['loaded_hooks'] = stock.total_stock
            modal_data['empty_hooks'] = modal_data['jig_capacity'] - modal_data['loaded_cases_qty'] if modal_data['jig_capacity'] else 0
            modal_data['no_of_cycle'] = 1

        # Model Images preparation with validation
        modal_data['model_images'] = self._prepare_model_images(model_master)

        # Add Model button logic with validation
        modal_data['add_model_enabled'] = modal_data['empty_hooks'] > 0
        
        
        # Save button logic: Enable only if empty_hooks == 0
        modal_data['can_save'] = (modal_data['empty_hooks'] == 0)

        # Delink Table preparation (existing tray data)
        modal_data['delink_table'] = self._prepare_existing_delink_table(lot_id, batch)

        # Modal validation rules - separate for draft and final save
        modal_data['modal_validation'] = self._prepare_modal_validation(modal_data, is_draft=False)
        modal_data['modal_validation_draft'] = self._prepare_modal_validation(modal_data, is_draft=True)

        # UI Configuration for frontend rendering
        modal_data['ui_config'] = self._prepare_ui_configuration(modal_data)

        # Comprehensive calculation logs
        modal_data['logs'] = {
            'batch_id': batch.batch_id if batch else None,
            'lot_id': lot_id,
            'jig_qr_id': jig_qr_id,
            'jig_type': modal_data['jig_type'],
            'jig_capacity': modal_data['jig_capacity'],
            'loaded_cases_qty': modal_data['loaded_cases_qty'],
            'loaded_hooks': modal_data['loaded_hooks'],
            'empty_hooks': modal_data['empty_hooks'],
            'broken_buildup_hooks': modal_data['broken_buildup_hooks'],
            'nickel_bath_type': modal_data['nickel_bath_type'],
            'delink_table': modal_data['delink_table'],
            'model_images': modal_data['model_images'],
            'add_model_enabled': modal_data['add_model_enabled'],
            'can_save': modal_data['can_save'],
            'user': request.user.username,
            'calculation_timestamp': timezone.now().isoformat(),
            'tray_type': modal_data['tray_type']
        }

        logger.info(f"🎯 Modal data prepared with {len(modal_data['model_images'])} images, {len(modal_data['delink_table'])} existing trays")
        
        return modal_data
    
    def _prepare_model_images(self, model_master):
        """
        Prepare model images data with proper structure for frontend consumption.
        """
        model_image_data = []
        if model_master and model_master.images.exists():
            for image in model_master.images.all():
                model_image_data.append({
                    'url': image.master_image.url,
                    'model_no': model_master.model_no,
                    'image_id': image.id,
                    'alt_text': f"Model {model_master.model_no} Image"
                })
        return model_image_data
    
    def _prepare_existing_delink_table(self, lot_id, batch):
        """
        Prepare existing delink table data (for display only, not calculation).
        """
        tray_ids = JigLoadTrayId.objects.filter(lot_id=lot_id, batch_id=batch).order_by('date')
        delink_table = []
        for idx, tray in enumerate(tray_ids):
            delink_table.append({
                's_no': idx + 1,
                'tray_id': tray.tray_id,
                'tray_qty': tray.tray_quantity,
                'date_created': tray.date.isoformat() if tray.date else None,
                'is_existing': True
            })
        return delink_table
    
    def _prepare_modal_validation(self, modal_data, is_draft=False):
        """
        Prepare validation rules and constraints for modal data.
        Args:
            modal_data: Dictionary containing modal data
            is_draft: Boolean indicating if this is draft validation (True) or final save validation (False)
        """
        validation = {
            'jig_capacity_valid': modal_data['jig_capacity'] > 0,
            'loaded_cases_valid': modal_data['loaded_cases_qty'] > 0,
            'hooks_balance_valid': modal_data['loaded_hooks'] + modal_data['empty_hooks'] == modal_data['jig_capacity'],
            'broken_hooks_valid': modal_data['broken_buildup_hooks'] >= 0,
            'nickel_bath_valid': modal_data['nickel_bath_type'] in ['Bright', 'Satin', 'Matt'],
            'has_model_images': len(modal_data['model_images']) > 0,
            'can_add_model': modal_data['add_model_enabled'],
        }
        
        # Draft validation: More lenient - allow empty hooks
        if is_draft:
            validation['empty_hooks_zero'] = True  # Always pass for drafts
            
            # For drafts, require at least one input (jig_id, broken_buildup_hooks, loaded_cases_qty, or any tray data)
            has_jig_id = bool(modal_data.get('jig_qr_id', '').strip())
            has_broken_hooks = modal_data.get('broken_buildup_hooks', 0) > 0
            has_loaded_cases = modal_data.get('loaded_cases_qty', 0) > 0
            has_tray_data = bool(modal_data.get('delink_table', []))  # Check if any tray data exists
            
            validation['has_minimal_input'] = has_jig_id or has_broken_hooks or has_loaded_cases or has_tray_data
            
            # Draft overall validity: only check if minimal input exists
            validation['overall_valid'] = validation['has_minimal_input']
            
            if not validation['has_minimal_input']:
                validation['empty_hooks_error'] = "At least enter Jig Id or Tray Id or cancel the form"
        else:
            # Final save validation: Strict - require empty hooks to be zero
            validation['empty_hooks_zero'] = (modal_data['empty_hooks'] == 0)
            validation['overall_valid'] = all([
                validation['jig_capacity_valid'],
                validation['loaded_cases_valid'],
                validation['hooks_balance_valid'],
                validation['broken_hooks_valid'],
                validation['nickel_bath_valid'],
                validation['empty_hooks_zero'],
            ])
            if not validation['empty_hooks_zero']:
                validation['empty_hooks_error'] = (
                    "Loaded Cases Qty must equal Jig Capacity. Use 'Add Model' to fill empty hooks with relevant tray allocation."
                )
        
        return validation
    
    def _prepare_ui_configuration(self, modal_data):
        """
        Prepare UI configuration for optimal frontend rendering.
        """
        return {
            'show_model_images': len(modal_data['model_images']) > 0,
            'enable_add_model': modal_data['add_model_enabled'],
            'show_cycle_info': modal_data['no_of_cycle'] > 1,
            'highlight_empty_hooks': modal_data['empty_hooks'] > 0,
            'show_broken_hooks_warning': modal_data['broken_buildup_hooks'] > 0,
            'readonly_fields': ['empty_hooks', 'loaded_cases_qty', 'jig_capacity'],
            'required_fields': ['jig_id', 'nickel_bath_type'],
            'validation_enabled': True
        }

# Tray ID Validation - Delink Table View
@api_view(['GET'])
def validate_tray_id(request):
    tray_id = request.GET.get('tray_id')
    batch_id = request.GET.get('batch_id')
    if not tray_id or not batch_id:
        return Response({'valid': False, 'message': 'Tray ID and Batch ID required'}, status=400)
    exists = JigLoadTrayId.objects.filter(tray_id=tray_id, batch_id__batch_id=batch_id).exists()
    if exists:
        return Response({'valid': True})
    else:
        return Response({'valid': False, 'message': 'Tray ID not found for this batch.'}, status=404)

# Add Jig Btn - Delink Table View
class DelinkTableAPIView(APIView):
    """
    Returns tray rows for Delink Table based on tray type, lot qty, and jig capacity.
    Calculates number of trays needed for scanning based on loaded cases qty and tray capacity.
    """
    def get(self, request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        batch_id = request.GET.get('batch_id')
        lot_id = request.GET.get('lot_id')
        jig_qr_id = request.GET.get('jig_qr_id', None)

        if not batch_id or not lot_id:
            logger.info("❌ Missing parameters: batch_id or lot_id")
            return Response({'error': 'batch_id and lot_id required'}, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"🔍 Processing delink table for batch_id: {batch_id}, lot_id: {lot_id}")

        # Get TotalStockModel for loaded cases qty
        try:
            stock = TotalStockModel.objects.get(lot_id=lot_id)
            loaded_cases_qty = stock.total_stock or 0
            logger.info(f"📊 Loaded cases qty from TotalStockModel: {loaded_cases_qty}")
        except TotalStockModel.DoesNotExist:
            logger.error(f"❌ TotalStockModel not found for lot_id: {lot_id}")
            return Response({'error': 'Stock record not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get batch/model info for tray type and jig capacity
        try:
            batch = ModelMasterCreation.objects.get(batch_id=batch_id)
            model_master = batch.model_stock_no
            logger.info(f"📦 Found batch: {batch_id}, model: {model_master}")
        except ModelMasterCreation.DoesNotExist:
            logger.error(f"❌ ModelMasterCreation not found for batch_id: {batch_id}")
            return Response({'error': 'Batch not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get tray type and capacity
        tray_type_name = batch.tray_type or "Normal"  # Default to Normal if not set
        try:
            tray_type_obj = TrayType.objects.get(tray_type=tray_type_name)
            tray_capacity = tray_type_obj.tray_capacity
            logger.info(f"🗂️ Tray type: {tray_type_name}, capacity: {tray_capacity}")
        except TrayType.DoesNotExist:
            logger.warning(f"⚠️ TrayType '{tray_type_name}' not found, using default capacity 12")
            tray_capacity = 12  # Default tray capacity

        # Get jig capacity from JigLoadingMaster
        jig_capacity = 0
        if model_master:
            try:
                jig_master = JigLoadingMaster.objects.get(model_stock_no=model_master)
                jig_capacity = jig_master.jig_capacity
                logger.info(f"🔧 Jig capacity from JigLoadingMaster: {jig_capacity}")
            except JigLoadingMaster.DoesNotExist:
                logger.warning(f"⚠️ JigLoadingMaster not found for model: {model_master}")
                jig_capacity = loaded_cases_qty  # Use loaded cases qty as fallback
                logger.warning(f"⚠️ JigLoadingMaster not found for model: {model_master}")
                jig_capacity = loaded_cases_qty  # Use loaded cases qty as fallback

        # Calculate actual quantity needed (minimum of loaded cases and jig capacity)
        actual_qty = min(loaded_cases_qty, jig_capacity) if jig_capacity > 0 else loaded_cases_qty
        logger.info(f"🧮 Calculation: loaded_cases_qty={loaded_cases_qty}, jig_capacity={jig_capacity}, actual_qty={actual_qty}")

        # Calculate number of trays needed
        if tray_capacity > 0 and actual_qty > 0:
            num_trays = ceil(actual_qty / tray_capacity)
        else:
            num_trays = 0
        
        logger.info(f"📝 Number of trays needed: {num_trays}")

        # Check for existing tray IDs for this lot
        existing_trays = JigLoadTrayId.objects.filter(
            lot_id=lot_id, 
            batch_id=batch
        ).order_by('date')
        
        logger.info(f"🗃️ Found {existing_trays.count()} existing trays for lot_id: {lot_id}")

        # Generate tray rows for delink table
        rows = []
        remaining_qty = actual_qty
        
        for i in range(num_trays):
            s_no = i + 1
            
            # Calculate quantity for this tray
            if i == num_trays - 1:  # Last tray gets remaining quantity
                tray_qty = remaining_qty
            else:  # Full tray
                tray_qty = min(tray_capacity, remaining_qty)
            
            # Check if we have existing tray data
            existing_tray = None
            if i < existing_trays.count():
                existing_tray = existing_trays[i]
            
            if existing_tray:
                tray_id = existing_tray.tray_id
                tray_quantity = existing_tray.tray_quantity
                placeholder = f"Existing: {tray_id}"
                readonly = True
                logger.info(f"📋 Row {s_no}: Using existing tray {tray_id} with qty {tray_quantity}")
            else:
                tray_id = ""  # Empty for scanning
                tray_quantity = tray_qty
                placeholder = f"Scan Tray ID ({tray_qty} pcs)"
                readonly = False
                logger.info(f"📋 Row {s_no}: New tray needed with qty {tray_qty}")
            
            rows.append({
                's_no': s_no,
                'tray_id': tray_id,
                'tray_quantity': tray_quantity,
                'placeholder': placeholder,
                'readonly': readonly
            })
            
            remaining_qty -= tray_qty
            if remaining_qty <= 0:
                break

        logger.info(f"✅ Generated {len(rows)} delink table rows")
        logger.info(f"📊 Final calculation summary - tray_type: {tray_type_name}, tray_capacity: {tray_capacity}, actual_qty: {actual_qty}, num_trays: {num_trays}")

        return Response({
            'tray_rows': rows,
            'tray_type': tray_type_name,
            'tray_capacity': tray_capacity,
            'actual_qty': actual_qty,
            'loaded_cases_qty': loaded_cases_qty,
            'jig_capacity': jig_capacity,
            'num_trays': num_trays,
            'calculation_details': {
                'formula': f'ceil({actual_qty} / {tray_capacity}) = {num_trays} trays',
                'constraint': f'actual_qty = min(loaded_cases_qty={loaded_cases_qty}, jig_capacity={jig_capacity})',
                'tray_distribution': [row['tray_quantity'] for row in rows]
            }
        }, status=status.HTTP_200_OK)


# Manual Draft - Save/Update View


class JigLoadingManualDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        batch_id = request.data.get('batch_id')
        lot_id = request.data.get('lot_id')
        draft_data = request.data.get('draft_data')
        user = request.user

        logger.info(f"🔍 Draft request: user={user.username}, batch_id={batch_id}, lot_id={lot_id}")

        # --- Fix: For draft, require at least one input ---
        if not batch_id or not lot_id:
            logger.error(f"❌ Missing required fields: batch_id={batch_id}, lot_id={lot_id}")
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if at least one input is entered for draft
        jig_id = draft_data.get('jig_id', '').strip() if draft_data else ''
        broken_buildup_hooks = int(draft_data.get('broken_buildup_hooks', 0)) if draft_data else 0
        trays = draft_data.get('trays', []) if draft_data else []
        tray_ids = [tray.get('tray_id', '').strip() for tray in trays if tray.get('tray_id', '').strip()]
        
        if not any([jig_id, broken_buildup_hooks > 0, tray_ids]):
            logger.error("❌ At least enter Jig Id or Tray Id or cancel the form")
            return Response({'error': 'At least enter Jig Id or Tray Id or cancel the form'}, status=status.HTTP_400_BAD_REQUEST)

        obj, created = JigLoadingManualDraft.objects.update_or_create(
            batch_id=batch_id,
            lot_id=lot_id,
            user=user,
            defaults={'draft_data': draft_data}
        )

        # --- Update only the correct TotalStockModel ---
        try:
            stock = TotalStockModel.objects.get(batch_id__batch_id=batch_id, lot_id=lot_id)
            stock.jig_draft = True
            stock.save()
            logger.info(f"💾 Successfully updated lot status to Draft for batch_id={batch_id}, lot_id={lot_id}")
        except TotalStockModel.DoesNotExist:
            logger.error(f"❌ No TotalStockModel for lot_id={lot_id}, batch_id={batch_id}")
            return Response({'error': 'Stock record not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # --- Update Jig table with draft info ---
        jig_id = draft_data.get('jig_id')
        if jig_id:
            jig_obj, _ = Jig.objects.get_or_create(jig_qr_id=jig_id)
            jig_obj.drafted = True
            jig_obj.current_user = user
            jig_obj.locked_at = timezone.now()
            jig_obj.batch_id = batch_id
            jig_obj.save()
            logger.info(f"💾 Jig {jig_id} marked as drafted for batch {batch_id} by {user.username}")

        logger.info(f"✅ Draft saved successfully for batch_id={batch_id}, lot_id={lot_id}")
        return Response({'success': True, 'created': created, 'updated_at': obj.updated_at})





# Manual Draft - Retrieve View
class JigLoadingManualDraftFetchAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        batch_id = request.GET.get('batch_id')
        lot_id = request.GET.get('lot_id')
        user = request.user
        try:
            draft = JigLoadingManualDraft.objects.get(batch_id=batch_id, lot_id=lot_id, user=user)
            return Response({'success': True, 'draft_data': draft.draft_data})
        except JigLoadingManualDraft.DoesNotExist:
            return Response({'success': False, 'draft_data': None})
        

@api_view(['POST'])
def validate_lock_jig_id(request):
    logger = logging.getLogger(__name__)
    try:
        # Check authentication first
        if not request.user.is_authenticated:
            logger.warning("❌ User not authenticated")
            return JsonResponse({'valid': False, 'message': 'Authentication required'}, status=401)
        
        logger.info(f"🚀 API CALLED - validate_lock_jig_id by user: {request.user.username}")
        
        jig_id = request.data.get('jig_id', '').strip()
        batch_id = request.data.get('batch_id', '').strip()
        jig_type = request.data.get('jig_type', '').strip()
        user = request.user
        
        logger.info(f"📊 Request data: jig_id={jig_id}, batch_id={batch_id}, jig_type={jig_type}, user={user.username}")

        # Basic validation - check if jig_id is provided
        if not jig_id or len(jig_id) > 9:
            logger.info("⚠️ Basic validation failed: length check")
            return JsonResponse({'valid': False, 'message': 'Jig ID must be <= 9 characters.'}, status=200)

        # FIRST: Check for existing drafted jigs before format validation
        drafted_jig_current_batch = Jig.objects.filter(
            jig_qr_id=jig_id, drafted=True, batch_id=batch_id
        ).first()

        logger.info(f"🔍 Drafted jig current batch query result: {drafted_jig_current_batch}")

        if drafted_jig_current_batch:
            # If same user and same batch, allow
            if drafted_jig_current_batch.current_user == user:
                logger.info("✅ Same user, same batch - allowing")
                return JsonResponse({'valid': True, 'message': 'Jig ID is drafted by you for this batch.'}, status=200)
            else:
                logger.info(f"❌ Different user for same batch: {drafted_jig_current_batch.current_user.username}")
                return JsonResponse({'valid': False, 'message': f'Jig ID is being used by {drafted_jig_current_batch.current_user.username}.'}, status=200)

        # If not drafted for this batch, check if drafted for any other batch
        drafted_jig_other_batch = Jig.objects.filter(
            jig_qr_id=jig_id, drafted=True
        ).exclude(batch_id=batch_id).first()

        logger.info(f"🔍 Drafted jig other batch query result: {drafted_jig_other_batch}")

        if drafted_jig_other_batch:
            # If same user but different batch, restrict with correct message
            if drafted_jig_other_batch.current_user == user:
                logger.info(f"🎯 FOUND: Same user ({user.username}) but different batch - returning 'Already drafted for diff batch'")
                return JsonResponse({'valid': False, 'message': 'Already drafted for diff batch'}, status=200)
            # If different user, restrict
            else:
                logger.info(f"❌ Different user for different batch: {drafted_jig_other_batch.current_user.username}")
                return JsonResponse({'valid': False, 'message': f'Jig ID is being used by {drafted_jig_other_batch.current_user.username}.'}, status=200)

        # SECOND: Only after checking existing drafts, validate format for new jigs
        # Fetch jig capacity for this batch
        jig_capacity = None
        try:
            batch_obj = ModelMasterCreation.objects.get(batch_id=batch_id)
            model_master = batch_obj.model_stock_no
            jig_master = JigLoadingMaster.objects.filter(model_stock_no=model_master).first()
            if jig_master:
                jig_capacity = jig_master.jig_capacity
            logger.info(f"📏 Jig capacity found: {jig_capacity}")
        except ModelMasterCreation.DoesNotExist:
            logger.error(f"❌ Batch not found: {batch_id}")
            return JsonResponse({'valid': False, 'message': 'Batch not found.'}, status=200)

        # Check Jig ID format (must match Jig Capacity prefix for new jigs)
        expected_prefix = f"J{int(jig_capacity):03d}" if jig_capacity is not None else None
        expected_length = 9  # Example: J098-0001

        if expected_prefix and not jig_id.startswith(expected_prefix):
            logger.info(f"❌ Format validation failed: expected {expected_prefix}, got {jig_id}")
            return JsonResponse({'valid': False, 'message': f'Jig ID must start with {expected_prefix}.'}, status=200)

        # --- JIG ID Prefix/Suffix Validation ---
        if len(jig_id) < expected_length:
            logger.info(f"❌ Jig ID incomplete: got {jig_id} (length {len(jig_id)})")
            return JsonResponse({'valid': False, 'message': f'Enter full Jig ID ({expected_length} characters).'}, status=200)
        # --- END BLOCK ---

        # If not drafted/locked, show available message
        logger.info("✅ Jig ID is available")
        return JsonResponse({'valid': True, 'message': 'Jig ID is available to use'}, status=200)
        
    except Exception as e:
        logger.error(f"💥 Exception in validate_lock_jig_id: {e}")
        return JsonResponse({'valid': False, 'message': 'Internal server error'}, status=200)

# Jig Save API View & Move to Complete Table if valid
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class JigSaveAPIView(APIView):
    """
    API endpoint for saving Jig details to complete table
    """
    
    def get_tray_capacity(stock):
        # Try batch first
        if stock.batch_id and getattr(stock.batch_id, 'tray_capacity', None):
            return stock.batch_id.tray_capacity
        # Try model_master
        if stock.model_stock_no and getattr(stock.model_stock_no, 'tray_capacity', None):
            return stock.model_stock_no.tray_capacity
        # Try tray_type
        if stock.batch_id and hasattr(stock.batch_id, 'tray_type') and stock.batch_id.tray_type:
            try:
                tray_type_obj = TrayType.objects.get(tray_type=stock.batch_id.tray_type)
                return tray_type_obj.tray_capacity
            except TrayType.DoesNotExist:
                pass
        # Try JigLoadingMaster
        jig_master = JigLoadingMaster.objects.filter(model_stock_no=stock.model_stock_no).first()
        if jig_master and getattr(jig_master, 'tray_capacity', None):
            return jig_master.tray_capacity
        return None 
    
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body.decode('utf-8'))
            
            # Extract required fields
            batch_id = data.get('batch_id', '').strip()
            lot_id = data.get('lot_id', '').strip()
            jig_qr_id = data.get('jig_qr_id', '').strip()
            
            if not all([batch_id, lot_id, jig_qr_id]):
                return JsonResponse({
                    'success': False, 
                    'error': 'Missing required fields: batch_id, lot_id, jig_qr_id'
                }, status=400)

            # Get batch and jig information
            try:
                batch_obj = ModelMasterCreation.objects.get(batch_id=batch_id)
                model_master = batch_obj.model_stock_no
                jig_master = JigLoadingMaster.objects.filter(model_stock_no=model_master).first()
                
                if not jig_master:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Jig master configuration not found'
                    }, status=400)
                    
            except ModelMasterCreation.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'error': 'Batch not found'
                }, status=400)

            # Create or update Jig Details record
            jig_detail_data = {
                'jig_qr_id': jig_qr_id,
                'jig_type': jig_master.jig_type,
                'jig_capacity': jig_master.jig_capacity,
                'total_cases_loaded': data.get('total_cases_loaded', 0),
                'empty_slots': data.get('empty_slots', 0),
                'faulty_slots': data.get('faulty_slots', 0),
                'no_of_model_cases': data.get('model_numbers', []),
                'new_lot_ids': data.get('lot_ids', []),
                'lot_id_quantities': data.get('lot_id_quantities', {}),
                'lot_id': lot_id,
                'draft_save': False,  # Final save
                'created_by': request.user,
                'ep_bath_type': 'Bright',  # Default value
                'plating_color': 'Default',  # Default value
                'forging': jig_master.forging_info,
            }
            
            # Save JigDetails
            jig_detail = JigDetails.objects.create(**jig_detail_data)

            # --- Mark TotalStockModel as completed ---
            try:
                stock = TotalStockModel.objects.get(lot_id=lot_id)
                stock.Jig_Load_completed = True
                stock.save()
            except TotalStockModel.DoesNotExist:
                pass  # Optionally log error

            # Update Jig status - mark as loaded and clear locks
            jig_obj, _ = Jig.objects.get_or_create(jig_qr_id=jig_qr_id)
            jig_obj.is_loaded = True
            jig_obj.current_user = None
            jig_obj.locked_at = None
            jig_obj.drafted = False
            jig_obj.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Jig Saved Successfully',
                'jig_id': jig_detail.id,
                'redirect_url': '/jig_loading/JigCompletedTable/'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f'Failed to save jig: {str(e)}'
            }, status=500)

# Row Hold Toggle - Jig Loading Table View

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def hold_row(request):
    batch_id = request.data.get('batch_id')
    lot_id = request.data.get('lot_id')
    remark = request.data.get('remark')
    user = request.user

    try:
        stock = TotalStockModel.objects.get(batch_id__batch_id=batch_id, lot_id=lot_id)
        stock.jig_hold_lot = True
        stock.jig_holding_reason = remark
        stock.save()
        return JsonResponse({'success': True, 'holding_reason': stock.jig_holding_reason})
    except TotalStockModel.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Row not found'}, status=404)

# Row Release Toggle  - Jig Loading Table View
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def release_row(request):
    batch_id = request.data.get('batch_id')
    lot_id = request.data.get('lot_id')
    remark = request.data.get('remark')
    user = request.user

    try:
        stock = TotalStockModel.objects.get(batch_id__batch_id=batch_id, lot_id=lot_id)
        stock.jig_hold_lot = False
        stock.jig_release_lot = True
        stock.jig_release_reason = remark
        stock.save()
        return JsonResponse({'success': True, 'release_reason': stock.jig_release_reason})
    except TotalStockModel.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Row not found'}, status=404)

# Remark / Chat View - Jig Loading Table View
@csrf_exempt
def save_jig_remark(request):
    if request.method == "POST":
        lot_id = request.POST.get("lot_id")
        remark = request.POST.get("remark")
        if not lot_id or not remark:
            return JsonResponse({"success": False, "error": "Missing lot_id or remark"}, status=400)
        try:
            stock = TotalStockModel.objects.get(lot_id=lot_id)
            stock.jig_pick_remarks = remark
            stock.save()
            return JsonResponse({"success": True})
        except TotalStockModel.DoesNotExist:
            return JsonResponse({"success": False, "error": "Lot not found"}, status=404)
    return JsonResponse({"success": False, "error": "Invalid method"}, status=405)

# Add Model Button - Logic
@method_decorator(login_required, name='dispatch')
class AddModelFilterAPIView(APIView):
    """
    Returns filtered models for Add Model button:
    - Different Model No
    - Same Plating Color
    - Same Polish Finish  
    - Same Jig Type
    - Any Version (irrespective)
    """
    def get(self, request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        current_model_no = request.GET.get('model_no')
        plating_color = request.GET.get('plating_color')
        polish_finish = request.GET.get('polish_finish')
        jig_type = request.GET.get('jig_type')
        batch_id = request.GET.get('batch_id')
        
        logger.info(f"🔍 Add Model Filter: model_no={current_model_no}, plating_color={plating_color}, polish_finish={polish_finish}, jig_type={jig_type}")

        if not all([current_model_no, plating_color, polish_finish, jig_type]):
            return JsonResponse({'error': 'Missing required parameters', 'models': []})

        try:
            # Filter TotalStockModel records that match criteria
            # Same model_no, plating_color, polish_finish, and jig_type but different batch/lot
            stock_records = TotalStockModel.objects.filter(
                model_stock_no__model_no=current_model_no,
                plating_color__plating_color=plating_color,
                polish_finish__polish_finish=polish_finish,
                total_stock__gt=0,
                Jig_Load_completed=False
            ).select_related('model_stock_no', 'batch_id', 'plating_color', 'polish_finish')
            
            # Exclude the current batch to show other lots/batches with same characteristics
            if batch_id:
                stock_records = stock_records.exclude(batch_id__batch_id=batch_id)

            # Filter by jig type using JigLoadingMaster
            filtered = []
            for stock in stock_records:
                if stock.model_stock_no:
                    jig_master = JigLoadingMaster.objects.filter(model_stock_no=stock.model_stock_no).first()
                    if jig_master and jig_master.jig_type == jig_type:
                        filtered.append({
                            'model_no': stock.model_stock_no.model_no,
                            'plating_color': plating_color,
                            'polish_finish': polish_finish,
                            'jig_type': jig_type,
                            'version': getattr(stock.model_stock_no, 'version', ''),
                            'qty': stock.total_stock,
                            'lot_id': stock.lot_id,
                            'batch_id': stock.batch_id.batch_id if stock.batch_id else '',
                            'plating_stk_no': (
                                getattr(stock.batch_id, 'plating_stk_no', None) or 
                                getattr(stock.model_stock_no, 'plating_stk_no', None) or ''
                            ),
                        })
            
            logger.info(f"📊 Found {len(filtered)} matching models for Add Model")
            return JsonResponse({'models': filtered})
            
        except Exception as e:
            logger.error(f"❌ Error in AddModelFilterAPIView: {str(e)}")
            return JsonResponse({'error': str(e), 'models': []})

# Jig Loading Complete Table - Main View 
class JigCompletedTable(TemplateView):
    template_name = "JigLoading/Jig_CompletedTable.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        completed_qs = TotalStockModel.objects.filter(Jig_Load_completed=True)
        completed_data = []
        for stock in completed_qs:
            plating_stk_no = (
                getattr(stock.batch_id, 'plating_stk_no', None)
                or getattr(stock.model_stock_no, 'plating_stk_no', None)
            )
            polishing_stk_no = (
                getattr(stock.batch_id, 'polishing_stk_no', None)
                or getattr(stock.model_stock_no, 'polishing_stk_no', None)
            )
            tray_capacity = JigView.get_tray_capacity(stock)
            jig_type = ''
            jig_capacity = ''
            if stock.model_stock_no:
                jig_master = JigLoadingMaster.objects.filter(model_stock_no=stock.model_stock_no).first()
                if jig_master:
                    jig_type = jig_master.jig_type
                    jig_capacity = jig_master.jig_capacity

            lot_qty = stock.total_stock or 0
            no_of_trays = 0
            if tray_capacity and tray_capacity > 0:
                no_of_trays = (lot_qty // tray_capacity) + (1 if lot_qty % tray_capacity else 0)

            # Fetch JigDetails for this lot (for Jig ID, loaded date, etc.)
            jig_detail = JigDetails.objects.filter(lot_id=stock.lot_id).order_by('-date_time').first()

            completed_data.append({
                'batch_id': stock.batch_id.batch_id if stock.batch_id else '',
                'jig_loaded_date_time': (
                    jig_detail.jig_loaded_date_time
                    if jig_detail and jig_detail.jig_loaded_date_time
                    else (jig_detail.date_time if jig_detail else '')
                ),
                'lot_id': stock.lot_id,
                'lot_plating_stk_nos': plating_stk_no or 'No Plating Stock No',
                'lot_polishing_stk_nos': polishing_stk_no or 'No Polishing Stock No',
                'plating_color': stock.plating_color.plating_color if stock.plating_color else '',
                'polish_finish': stock.polish_finish.polish_finish if stock.polish_finish else '',
                'lot_version_names': stock.version.version_internal if stock.version else '',
                'tray_type': getattr(stock.batch_id, 'tray_type', ''),
                'tray_capacity': getattr(stock.batch_id, 'tray_capacity', ''),
                'calculated_no_of_trays': no_of_trays,
                'total_cases_loaded': jig_detail.total_cases_loaded if jig_detail else '',
                'jig_type': jig_type,
                'jig_capacity': jig_capacity,
                'jig_qr_id': jig_detail.jig_qr_id if jig_detail else '',
                'jig_loaded_date_time': jig_detail.jig_loaded_date_time if jig_detail else '',
                'model_images': [img.master_image.url for img in stock.model_stock_no.images.all()] if stock.model_stock_no else [],
                'audio_remark': getattr(jig_detail, 'pick_remarks', ''),
                'IP_jig_pick_remarks': getattr(jig_detail, 'IP_jig_pick_remarks', ''),
            })
        context['jig_details'] = completed_data
        return context