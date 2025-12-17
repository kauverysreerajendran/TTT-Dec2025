from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from modelmasterapp.models import *
from Recovery_DP.models import *
from django.core.paginator import Paginator

class ReportsView(TemplateView):
    template_name = "ModelMaster/Report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch all model_no values from ModelMaster
        context['model_list'] = ModelMaster.objects.values_list('model_no', flat=True)

        # Get filter parameters
        lot_id = self.request.GET.get('lot_id')
        batch_id = self.request.GET.get('batch_id')
        model_no = self.request.GET.get('model_no')
        department = self.request.GET.get('department')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        # Get batch details data
        batch_details = self.get_batch_details_data(
            lot_id, batch_id, model_no, department, date_from, date_to
        )

        # Add pagination for batch tracking table
        page_number = self.request.GET.get('page', 1)
        paginator = Paginator(batch_details, 10)  # 10 rows per page
        page_obj = paginator.get_page(page_number)
        
        context['page_obj'] = page_obj
        context['batch_details'] = page_obj.object_list
        
        # Preserve filter parameters for pagination links
        context['lot_id'] = lot_id
        context['batch_id'] = batch_id
        context['model_no'] = model_no
        context['department'] = department
        context['date_from'] = date_from
        context['date_to'] = date_to

        return context

    def get_batch_details_data(self, lot_id, batch_id, model_no, department, date_from, date_to):
        """Get batch details data for pagination"""
        result = []

        # Department mapping from filter values to actual process module names
        department_mapping = {
            'day-planning': 'Day Planning',
            'input-screening': 'Input Screening',
            'brass-qc': 'Brass QC',
            'brass-audit': 'Brass Audit',
            'iqf': 'IQF',
            'recovery-day-planning': 'Recovery Day Planning',
            'recovery-input-screening': 'Recovery Input Screening',
            'recovery-brass-qc': 'Recovery Brass QC',
            'recovery-brass-audit': 'RecoveryBrass Audit',
            'recovery-iqf': 'Recovery IQF',
            'jig-loading': 'JIG Loading',
            'inprocess-inspection': 'Inprocess Inspection',
            'jig-unloading': 'Jig Unloading',
            'nickel-inspection': 'Nickel Inspection',
            'nickel-audit': 'Nickel Audit',
            'spider-spindle': 'Spider Loading'
        }

        # Special handling for Day Planning department
        if department == 'day-planning':
            # Get data from ModelMasterCreation table where Moved_to_D_Picker is FALSE
            master_objs = ModelMasterCreation.objects.filter(Moved_to_D_Picker=False)
            recovery_master_objs = RecoveryMasterCreation.objects.filter(Moved_to_D_Picker=False)
            
            # Apply additional filters
            if lot_id:
                master_objs = master_objs.filter(lot_id=lot_id)
                recovery_master_objs = recovery_master_objs.filter(lot_id=lot_id)
            if batch_id:
                master_objs = master_objs.filter(batch_id=batch_id)
                recovery_master_objs = recovery_master_objs.filter(batch_id=batch_id)
            if model_no:
                master_objs = master_objs.filter(model_stock_no__model_no=model_no)
                recovery_master_objs = recovery_master_objs.filter(model_stock_no__model_no=model_no)
            
            # Apply date filters
            if date_from:
                master_objs = master_objs.filter(date_time__date__gte=date_from)
                recovery_master_objs = recovery_master_objs.filter(date_time__date__gte=date_from)
            if date_to:
                master_objs = master_objs.filter(date_time__date__lte=date_to)
                recovery_master_objs = recovery_master_objs.filter(date_time__date__lte=date_to)
            
            # Process ModelMasterCreation records
            for master_obj in master_objs:
                result.append({
                    'batch_id': master_obj.batch_id,
                    'onboard_date': master_obj.date_time.strftime('%Y-%m-%d'),
                    'model_no': master_obj.model_stock_no.model_no,
                    'version': master_obj.version.version_name,
                    'quantity': master_obj.total_batch_quantity,
                    'current_stage': "Day Planning",
                    'status': "Yet To Start",
                })
            
            # Process RecoveryMasterCreation records
            for recovery_master_obj in recovery_master_objs:
                result.append({
                    'batch_id': recovery_master_obj.batch_id,
                    'onboard_date': recovery_master_obj.date_time.strftime('%Y-%m-%d'),
                    'model_no': recovery_master_obj.model_stock_no.model_no,
                    'version': recovery_master_obj.version.version_name,
                    'quantity': recovery_master_obj.total_batch_quantity,
                    'current_stage': "Recovery Day Planning",
                    'status': "Yet To Start",
                })
            
            return result

        # Handle "All Departments" and "All Models" case - show all data
        if (not department or department == 'all') and not lot_id and not batch_id:
            # Get all data from both sources
            
            # 1. Get Day Planning data from ModelMasterCreation (Moved_to_D_Picker = False)
            master_objs = ModelMasterCreation.objects.filter(Moved_to_D_Picker=False)
            recovery_master_objs = RecoveryMasterCreation.objects.filter(Moved_to_D_Picker=False)
            
            # 2. Get all other department data from TotalStockModel and RecoveryStockModel
            stock_objs = TotalStockModel.objects.all()
            recovery_stock_objs = RecoveryStockModel.objects.all()
            
            # Apply model filter if specified
            if model_no:
                master_objs = master_objs.filter(model_stock_no__model_no=model_no)
                recovery_master_objs = recovery_master_objs.filter(model_stock_no__model_no=model_no)
                stock_objs = stock_objs.filter(model_stock_no__model_no=model_no)
                recovery_stock_objs = recovery_stock_objs.filter(model_stock_no__model_no=model_no)
            
            # Apply date filters
            if date_from or date_to:
                if date_from:
                    master_objs = master_objs.filter(date_time__date__gte=date_from)
                    recovery_master_objs = recovery_master_objs.filter(date_time__date__gte=date_from)
                    stock_objs = stock_objs.filter(batch_id__in=ModelMasterCreation.objects.filter(date_time__date__gte=date_from).values_list('id', flat=True))
                    recovery_stock_objs = recovery_stock_objs.filter(batch_id__in=RecoveryMasterCreation.objects.filter(date_time__date__gte=date_from).values_list('id', flat=True))
                if date_to:
                    master_objs = master_objs.filter(date_time__date__lte=date_to)
                    recovery_master_objs = recovery_master_objs.filter(date_time__date__lte=date_to)
                    stock_objs = stock_objs.filter(batch_id__in=ModelMasterCreation.objects.filter(date_time__date__lte=date_to).values_list('id', flat=True))
                    recovery_stock_objs = recovery_stock_objs.filter(batch_id__in=RecoveryMasterCreation.objects.filter(date_time__date__lte=date_to).values_list('id', flat=True))
            
            # Process Day Planning records from ModelMasterCreation
            for master_obj in master_objs:
                result.append({
                    'batch_id': master_obj.batch_id,
                    'onboard_date': master_obj.date_time.strftime('%Y-%m-%d'),
                    'model_no': master_obj.model_stock_no.model_no,
                    'version': master_obj.version.version_name,
                    'quantity': master_obj.total_batch_quantity,
                    'current_stage': "Day Planning",
                    'status': "Yet To Start",
                })
            
            # Process Recovery Day Planning records from RecoveryMasterCreation
            for recovery_master_obj in recovery_master_objs:
                result.append({
                    'batch_id': recovery_master_obj.batch_id,
                    'onboard_date': recovery_master_obj.date_time.strftime('%Y-%m-%d'),
                    'model_no': recovery_master_obj.model_stock_no.model_no,
                    'version': recovery_master_obj.version.version_name,
                    'quantity': recovery_master_obj.total_batch_quantity,
                    'current_stage': "Recovery Day Planning",
                    'status': "Yet To Start",
                })
            
            # Process other department records from TotalStockModel
            for stock_obj in stock_objs:
                batch_obj = ModelMasterCreation.objects.filter(lot_id=stock_obj.lot_id).first()
                current_stage = stock_obj.last_process_module or ''
                last_process_module = stock_obj.last_process_module or ''
                status = "Yet To Start"
                if current_stage == "Day Planning" and batch_obj and batch_obj.Moved_to_D_Picker:
                    status = "Released"
                elif last_process_module == "Input Screening" and stock_obj.ip_person_qty_verified:
                    status = "Released"
                elif current_stage == "Brass QC" and stock_obj.brass_qc_accepted_qty_verified:
                    status = "Released"
                elif current_stage == "Brass Audit" and stock_obj.brass_audit_accepted_qty_verified:
                    status = "Released"
                elif current_stage == "IQF" and stock_obj.iqf_accepted_qty_verified:
                    status = "Released"
                result.append({
                    'batch_id': batch_obj.batch_id if batch_obj else '',
                    'onboard_date': batch_obj.date_time.strftime('%Y-%m-%d') if batch_obj else '',
                    'model_no': stock_obj.model_stock_no.model_no,
                    'version': stock_obj.version.version_name,
                    'quantity': stock_obj.total_stock,
                    'current_stage': current_stage,
                    'status': status,
                })

            # Process other department records from RecoveryStockModel
            for r_stock_obj in recovery_stock_objs:
                r_batch_obj = RecoveryMasterCreation.objects.filter(lot_id=r_stock_obj.lot_id).first()
                current_stage = r_stock_obj.last_process_module or ''
                last_process_module = r_stock_obj.last_process_module or ''
                status = "Yet To Start"
                if current_stage == "Recovery Day Planning" and r_batch_obj and r_batch_obj.Moved_to_D_Picker:
                    status = "Released"
                elif last_process_module == "Recovery Input Screening" and r_stock_obj.ip_person_qty_verified:
                    status = "Released"
                elif current_stage == "Recovery Brass QC" and r_stock_obj.brass_qc_accepted_qty_verified:
                    status = "Released"
                elif current_stage == "RecoveryBrass Audit" and r_stock_obj.brass_audit_accepted_qty_verified:
                    status = "Released"
                elif current_stage == "Recovery IQF" and r_stock_obj.iqf_accepted_qty_verified:
                    status = "Released"
                result.append({
                    'batch_id': r_batch_obj.batch_id if r_batch_obj else '',
                    'onboard_date': r_batch_obj.date_time.strftime('%Y-%m-%d') if r_batch_obj else '',
                    'model_no': r_stock_obj.model_stock_no.model_no,
                    'version': r_stock_obj.version.version_name,
                    'quantity': r_stock_obj.total_stock,
                    'current_stage': current_stage,
                    'status': status,
                })
            
            return result

        # Regular filtering logic for specific departments/filters
        stock_objs = TotalStockModel.objects.all()
        recovery_stock_objs = RecoveryStockModel.objects.all()
        batch_obj = None
        recovery_batch_obj = None

        # Apply filters
        if lot_id:
            stock_objs = stock_objs.filter(lot_id=lot_id)
            recovery_stock_objs = recovery_stock_objs.filter(lot_id=lot_id)
        elif batch_id:
            batch_obj = ModelMasterCreation.objects.filter(batch_id=batch_id)
            recovery_batch_obj = RecoveryMasterCreation.objects.filter(batch_id=batch_id)
            
            # Apply date filters to batch objects
            if date_from:
                batch_obj = batch_obj.filter(date_time__date__gte=date_from)
                recovery_batch_obj = recovery_batch_obj.filter(date_time__date__gte=date_from)
            if date_to:
                batch_obj = batch_obj.filter(date_time__date__lte=date_to)
                recovery_batch_obj = recovery_batch_obj.filter(date_time__date__lte=date_to)
                
            batch_obj = batch_obj.first()
            recovery_batch_obj = recovery_batch_obj.first()
            
            if batch_obj:
                stock_objs = stock_objs.filter(batch_id=batch_obj.id)
            else:
                stock_objs = TotalStockModel.objects.none()
            if recovery_batch_obj:
                recovery_stock_objs = recovery_stock_objs.filter(batch_id=recovery_batch_obj.id)
            else:
                recovery_stock_objs = RecoveryStockModel.objects.none()
            # If not found in TotalStockModel, show ModelMasterCreation info
            if batch_obj and not stock_objs.exists():
                # Check if department filter matches
                if not department or department_mapping.get(department) == "Day Planning":
                    result.append({
                        'batch_id': batch_obj.batch_id,
                        'onboard_date': batch_obj.date_time.strftime('%Y-%m-%d'),
                        'model_no': batch_obj.model_stock_no.model_no,
                        'version': batch_obj.version.version_name,
                        'quantity': batch_obj.total_batch_quantity,
                        'current_stage': "Day Planning",
                        'status': "Yet To Start",
                    })
            # If not found in RecoveryStockModel, show RecoveryMasterCreation info
            if recovery_batch_obj and not recovery_stock_objs.exists():
                # Check if department filter matches
                if not department or department_mapping.get(department) == "Recovery Day Planning":
                    result.append({
                        'batch_id': recovery_batch_obj.batch_id,
                        'onboard_date': recovery_batch_obj.date_time.strftime('%Y-%m-%d'),
                        'model_no': recovery_batch_obj.model_stock_no.model_no,
                        'version': recovery_batch_obj.version.version_name,
                        'quantity': recovery_batch_obj.total_batch_quantity,
                        'current_stage': "Recovery Day Planning",
                        'status': "Yet To Start",
                    })
        
        if model_no:
            stock_objs = stock_objs.filter(model_stock_no__model_no=model_no)
            recovery_stock_objs = recovery_stock_objs.filter(model_stock_no__model_no=model_no)

        # Apply date filters to stock objects by joining with ModelMasterCreation
        if date_from or date_to:
            if date_from:
                stock_objs = stock_objs.filter(batch_id__in=ModelMasterCreation.objects.filter(date_time__date__gte=date_from).values_list('id', flat=True))
                recovery_stock_objs = recovery_stock_objs.filter(batch_id__in=RecoveryMasterCreation.objects.filter(date_time__date__gte=date_from).values_list('id', flat=True))
            if date_to:
                stock_objs = stock_objs.filter(batch_id__in=ModelMasterCreation.objects.filter(date_time__date__lte=date_to).values_list('id', flat=True))
                recovery_stock_objs = recovery_stock_objs.filter(batch_id__in=RecoveryMasterCreation.objects.filter(date_time__date__lte=date_to).values_list('id', flat=True))

        # Apply department filter
        if department and department in department_mapping:
            department_name = department_mapping[department]
            stock_objs = stock_objs.filter(last_process_module=department_name)
            recovery_stock_objs = recovery_stock_objs.filter(last_process_module=department_name)

        # --- Normal Stock Rows ---
        for stock_obj in stock_objs:
            batch_obj = ModelMasterCreation.objects.filter(lot_id=stock_obj.lot_id).first()
            current_stage = stock_obj.last_process_module or ''
            last_process_module = stock_obj.last_process_module or ''
            status = "Yet To Start"
            if current_stage == "Day Planning" and batch_obj and batch_obj.Moved_to_D_Picker:
                status = "Released"
            elif last_process_module == "Input Screening" and stock_obj.ip_person_qty_verified:
                status = "Released"
            elif current_stage == "Brass QC" and stock_obj.brass_qc_accepted_qty_verified:
                status = "Released"
            elif current_stage == "Brass Audit" and stock_obj.brass_audit_accepted_qty_verified:
                status = "Released"
            elif current_stage == "IQF" and stock_obj.iqf_accepted_qty_verified:
                status = "Released"
            result.append({
                'batch_id': batch_obj.batch_id if batch_obj else '',
                'onboard_date': batch_obj.date_time.strftime('%Y-%m-%d') if batch_obj else '',
                'model_no': stock_obj.model_stock_no.model_no,
                'version': stock_obj.version.version_name,
                'quantity': stock_obj.total_stock,
                'current_stage': current_stage,
                'status': status,
            })

        # --- Recovery Stock Rows ---
        for r_stock_obj in recovery_stock_objs:
            r_batch_obj = RecoveryMasterCreation.objects.filter(lot_id=r_stock_obj.lot_id).first()
            current_stage = r_stock_obj.last_process_module or ''
            last_process_module = r_stock_obj.last_process_module or ''
            status = "Yet To Start"
            if current_stage == "Recovery Day Planning" and r_batch_obj and r_batch_obj.Moved_to_D_Picker:
                status = "Released"
            elif last_process_module == "Recovery Input Screening" and r_stock_obj.ip_person_qty_verified:
                status = "Released"
            elif current_stage == "Recovery Brass QC" and r_stock_obj.brass_qc_accepted_qty_verified:
                status = "Released"
            elif current_stage == "RecoveryBrass Audit" and r_stock_obj.brass_audit_accepted_qty_verified:
                status = "Released"
            elif current_stage == "Recovery IQF" and r_stock_obj.iqf_accepted_qty_verified:
                status = "Released"
            result.append({
                'batch_id': r_batch_obj.batch_id if r_batch_obj else '',
                'onboard_date': r_batch_obj.date_time.strftime('%Y-%m-%d') if r_batch_obj else '',
                'model_no': r_stock_obj.model_stock_no.model_no,
                'version': r_stock_obj.version.version_name,
                'quantity': r_stock_obj.total_stock,
                'current_stage': current_stage,
                'status': status,
            })

        return result


# Keep the AJAX endpoints for filters that still use JavaScript
def get_batch_details(request):
    """AJAX endpoint for JavaScript filters"""
    lot_id = request.GET.get('lot_id')
    batch_id = request.GET.get('batch_id')
    model_no = request.GET.get('model_no')
    department = request.GET.get('department')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Pagination parameters (for JavaScript-based pagination if needed)
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    
    # Use the same method from ReportsView
    reports_view = ReportsView()
    result = reports_view.get_batch_details_data(
        lot_id, batch_id, model_no, department, date_from, date_to
    )
    
    return JsonResponse(result, safe=False)


from django.http import JsonResponse
from collections import Counter

def get_stage_counts(request):
    model_no = request.GET.get('model_no')
    department = request.GET.get('department')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    stage_counts = Counter()
    
    # Department mapping from filter values to actual process module names
    department_mapping = {
        'day-planning': 'Day Planning',
        'input-screening': 'Input Screening',
        'brass-qc': 'Brass QC',
        'brass-audit': 'Brass Audit',
        'iqf': 'IQF',
        'recovery-day-planning': 'Recovery Day Planning',
        'recovery-input-screening': 'Recovery Input Screening',
        'recovery-brass-qc': 'Recovery Brass QC',
        'recovery-brass-audit': 'RecoveryBrass Audit',
        'recovery-iqf': 'Recovery IQF',
        'jig-loading': 'JIG Loading',
        'inprocess-inspection': 'Inprocess Inspection',
        'jig-unloading': 'Jig Unloading',
        'nickel-inspection': 'Nickel Inspection',
        'nickel-audit': 'Nickel Audit',
        'spider-spindle': 'Spider Loading'
    }
    
    # Special handling for Day Planning department
    if department == 'day-planning':
        # Get data from ModelMasterCreation and RecoveryMasterCreation tables where Moved_to_D_Picker is FALSE
        master_objs = ModelMasterCreation.objects.filter(Moved_to_D_Picker=False)
        recovery_master_objs = RecoveryMasterCreation.objects.filter(Moved_to_D_Picker=False)
        
        if model_no:
            master_objs = master_objs.filter(model_stock_no__model_no=model_no)
            recovery_master_objs = recovery_master_objs.filter(model_stock_no__model_no=model_no)
        
        # Apply date filters
        if date_from:
            master_objs = master_objs.filter(date_time__date__gte=date_from)
            recovery_master_objs = recovery_master_objs.filter(date_time__date__gte=date_from)
        if date_to:
            master_objs = master_objs.filter(date_time__date__lte=date_to)
            recovery_master_objs = recovery_master_objs.filter(date_time__date__lte=date_to)
        
        # For Day Planning stage, next stage would typically be Input Screening
        for obj in master_objs:
            stage_counts["Input Screening"] += 1
            
        # For Recovery Day Planning stage, next stage would typically be Recovery Input Screening  
        for obj in recovery_master_objs:
            stage_counts["Recovery Input Screening"] += 1
            
        return JsonResponse(stage_counts, safe=False)
    
    # Handle "All Departments" case - show all stages
    if not department or department == 'all':
        # Always show data even if no model is selected
        if not model_no:
            # No model filter, show all data from all tables
            
            # Day Planning data from ModelMasterCreation
            master_objs = ModelMasterCreation.objects.filter(Moved_to_D_Picker=False)
            recovery_master_objs = RecoveryMasterCreation.objects.filter(Moved_to_D_Picker=False)
            
            # All other data from stock tables
            total_stock_objs = TotalStockModel.objects.all()
            recovery_stock_objs = RecoveryStockModel.objects.all()
        else:
            # Model filter applied, show all data for that model
            master_objs = ModelMasterCreation.objects.filter(Moved_to_D_Picker=False, model_stock_no__model_no=model_no)
            recovery_master_objs = RecoveryMasterCreation.objects.filter(Moved_to_D_Picker=False, model_stock_no__model_no=model_no)
            total_stock_objs = TotalStockModel.objects.filter(model_stock_no__model_no=model_no)
            recovery_stock_objs = RecoveryStockModel.objects.filter(model_stock_no__model_no=model_no)
        
        # Apply date filters
        if date_from or date_to:
            if date_from:
                master_objs = master_objs.filter(date_time__date__gte=date_from)
                recovery_master_objs = recovery_master_objs.filter(date_time__date__gte=date_from)
                total_stock_objs = total_stock_objs.filter(batch_id__in=ModelMasterCreation.objects.filter(date_time__date__gte=date_from).values_list('id', flat=True))
                recovery_stock_objs = recovery_stock_objs.filter(batch_id__in=RecoveryMasterCreation.objects.filter(date_time__date__gte=date_from).values_list('id', flat=True))
            if date_to:
                master_objs = master_objs.filter(date_time__date__lte=date_to)
                recovery_master_objs = recovery_master_objs.filter(date_time__date__lte=date_to)
                total_stock_objs = total_stock_objs.filter(batch_id__in=ModelMasterCreation.objects.filter(date_time__date__lte=date_to).values_list('id', flat=True))
                recovery_stock_objs = recovery_stock_objs.filter(batch_id__in=RecoveryMasterCreation.objects.filter(date_time__date__lte=date_to).values_list('id', flat=True))
        
        # Count Day Planning stages
        for obj in master_objs:
            stage_counts["Input Screening"] += 1
        for obj in recovery_master_objs:
            stage_counts["Recovery Input Screening"] += 1
            
        # Count other stages
        for obj in total_stock_objs:
            stage = obj.next_process_module or "Unknown"
            stage_counts[stage] += 1
        for obj in recovery_stock_objs:
            stage = obj.next_process_module or "Unknown"
            stage_counts[stage] += 1
            
        return JsonResponse(stage_counts, safe=False)
    
    # If model is provided but specific department is selected
    if model_no:
        # Get querysets
        total_stock_objs = TotalStockModel.objects.filter(model_stock_no__model_no=model_no)
        recovery_stock_objs = RecoveryStockModel.objects.filter(model_stock_no__model_no=model_no)
        
        # Apply date filters by joining with ModelMasterCreation
        if date_from or date_to:
            if date_from:
                total_stock_objs = total_stock_objs.filter(batch_id__in=ModelMasterCreation.objects.filter(date_time__date__gte=date_from).values_list('id', flat=True))
                recovery_stock_objs = recovery_stock_objs.filter(batch_id__in=RecoveryMasterCreation.objects.filter(date_time__date__gte=date_from).values_list('id', flat=True))
            if date_to:
                total_stock_objs = total_stock_objs.filter(batch_id__in=ModelMasterCreation.objects.filter(date_time__date__lte=date_to).values_list('id', flat=True))
                recovery_stock_objs = recovery_stock_objs.filter(batch_id__in=RecoveryMasterCreation.objects.filter(date_time__date__lte=date_to).values_list('id', flat=True))
        
        # Apply department filter if specified
        if department and department in department_mapping:
            department_name = department_mapping[department]
            total_stock_objs = total_stock_objs.filter(last_process_module=department_name)
            recovery_stock_objs = recovery_stock_objs.filter(last_process_module=department_name)
        
        # Count stages in TotalStockModel
        for obj in total_stock_objs:
            stage = obj.next_process_module or "Unknown"
            stage_counts[stage] += 1
        # Count stages in RecoveryStockModel
        for obj in recovery_stock_objs:
            stage = obj.next_process_module or "Unknown"
            stage_counts[stage] += 1
            
    # Fallback: if no specific filters and no data found, show all available stages
    if not stage_counts and not model_no and (not department or department == 'all'):
        # Show all available data as fallback
        all_total_stock = TotalStockModel.objects.all()
        all_recovery_stock = RecoveryStockModel.objects.all()
        all_master = ModelMasterCreation.objects.filter(Moved_to_D_Picker=False)
        all_recovery_master = RecoveryMasterCreation.objects.filter(Moved_to_D_Picker=False)
        
        for obj in all_master:
            stage_counts["Input Screening"] += 1
        for obj in all_recovery_master:
            stage_counts["Recovery Input Screening"] += 1
        for obj in all_total_stock:
            stage = obj.next_process_module or "Unknown"
            stage_counts[stage] += 1
        for obj in all_recovery_stock:
            stage = obj.next_process_module or "Unknown"
            stage_counts[stage] += 1
            
    return JsonResponse(stage_counts, safe=False)