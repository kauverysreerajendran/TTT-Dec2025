from django.urls import path
from .views import *
from . import views

urlpatterns = [ 
    path('Jig_Unloading_MainTable/', Jig_Unloading_MainTable.as_view(), name='Jig_Unloading_MainTable'),
    path('JigUnloading_Completedtable/', JigUnloading_Completedtable.as_view(), name='JigUnloading_Completedtable'),
    path('get_model_details/', get_model_details, name='get_model_details'),
    path('validate_tray_id/', validate_tray_id, name='validate_tray_id'),
    path('validate_tray_id_dynamic/', validate_tray_id_dynamic, name='validate_tray_id_dynamic'),
    # path('save_jig_unload_tray_ids/', save_jig_unload_tray_ids, name='save_jig_unload_tray_ids'),
    path('save_jig_unload_tray_ids/', views.save_jig_unload_tray_ids, name='save_jig_unload_tray_ids'),

    path('check_unload_status/', check_unload_status, name='check_unload_status'),
    path('jig_unload_view_tray_list/', JigUnloadListAPIView.as_view(), name='jig_unload_view_tray_list'),
    path('jig_after_view_tray_list/', jig_after_view_tray_list, name='jig_after_view_tray_list'),
    path('jig_after_tray_validate/', JigAfterTrayValidateAPIView.as_view(), name='jig_after_tray_validate'),
    path('get_model_images/', get_model_images, name='get_model_images'),
    path('debug_models/', debug_model_availability, name='debug_model_availability'),
    path('unload_save_hold_unhold_reason/', UnLoadSaveHoldUnholdReasonAPIView.as_view(), name='unload_save_hold_unhold_reason'),
    path('unload_save_jig_pick_remark/', UnloadJigPickRemarkAPIView.as_view(), name='unload_save_jig_pick_remark'),
    path('save_jig_unload_draft/', save_jig_unload_draft, name='save_jig_unload_draft'),
    path('load_jig_unload_draft/', load_jig_unload_draft, name='load_jig_unload_draft')
]