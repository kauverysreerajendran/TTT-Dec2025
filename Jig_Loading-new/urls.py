from django.urls import path
from . import views
from .views import *
urlpatterns = [
    path('JigView/', JigView.as_view(), name='JigView'),
    path('JigCompletedTable/', JigCompletedTable.as_view(), name='JigCompletedTable'),
    path('tray-info/', TrayInfoView.as_view(), name='tray_info'),
    path('tray-validate/', TrayValidateAPIView.as_view(), name='tray_validate'),
    path('jig-add-modal-data/', JigAddModalDataView.as_view(), name='jig_add_modal_data'),
    path('delink-table/', DelinkTableAPIView.as_view(), name='delink_table_api'),
    path('validate-tray-id/', views.validate_tray_id, name='validate_tray_id'),
    path('manual-draft/', JigLoadingManualDraftAPIView.as_view(), name='jig_loading_manual_draft'),
    path('manual-draft-fetch/', JigLoadingManualDraftFetchAPIView.as_view(), name='jig_loading_manual_draft_fetch'),
    path('validate-lock-jig-id/', views.validate_lock_jig_id, name='validate_lock_jig_id'),
    path('jig-save/', JigSaveAPIView.as_view(), name='jig_save'),
    path('hold-row/', views.hold_row, name='hold_row'),
    path('release-row/', views.release_row, name='release_row'),
    path('save-jig-remark/', views.save_jig_remark, name='save_jig_remark'),
    path('add-model-filter/', AddModelFilterAPIView.as_view(), name='add_model_filter'),




]