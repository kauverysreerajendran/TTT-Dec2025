# Initialize Django
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'watchcase_tracker.settings')
django.setup()

# Import all apps
from modelmasterapp.management.commands.load_trays import Command as LoadTraysCommand
from adminportal import views as adminportal_views
from DayPlanning import views as dayplanning_views
from InputScreening import views as inputscreening_views
from Brass_QC import views as brass_qc_views
from BrassAudit import views as brass_audit_views
from IQF import views as iqf_views
from Jig_Loading import views as jig_loading_views
from Jig_Unloading import views as jig_unloading_views
from JigUnloading_Zone2 import views as jig_unloading_zone2_views
from Inprocess_Inspection import views as inprocess_inspection_views
from Nickel_Inspection import views as nickel_inspection_views
from nickel_inspection_zone_two import views as nickel_inspection_zone_two_views
from Nickel_Audit import views as nickel_audit_views
from Spider_Spindle import views as spider_spindle_views
from Spider_Spindle_zone_two import views as spider_spindle_zone_two_views
from nickel_audit_zone_two import views as nickel_audit_zone_two_views
from Recovery_DP import views as recovery_dp_views
from Recovery_IS import views as recovery_is_views
from Recovery_Brass_QC import views as recovery_brass_qc_views
from Recovery_BrassAudit import views as recovery_brass_audit_views
from Recovery_IQF import views as recovery_iqf_views
from ReportsModule import views as reports_module_views

# Add any additional imports or logic here