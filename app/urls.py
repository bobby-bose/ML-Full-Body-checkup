from django.urls import path
from .views import *

urlpatterns = [
    path('api/patients/add/', add_patient, name='add_patient'),
path('api/patients/edit/', edit_patient, name='edit_patient'),
path('api/patient/details/', details_patient, name='details_patient'),
path('api/patients/delete/', delete_patient, name='delete_patient'),
path('api/packages/list/', packages_list, name='packages_list'),
path('api/coordinationfacilitator/list/', coordinationfacilitator_list, name='coordinationfacilitator_list'),
path('api/meals/list/', meals_list, name='meals_list'),
path('api/departments/list/', departments_list, name='departments_list'),
path('api/patient/status/', get_patient_status, name='get_patient_status'),
path('api/departments/next/', next_department, name='next_department'),
path('api/departments/current/', get_current_patient_department, name='get_current_patient'),
path('api/packages/current/', get_current_patient_package, name='get_current_patient_package'),
path('api/time/current/', get_current_patient_time, name='get_current_patient_time'),
    path('api/patient-card-details/', get_patient_card_details, name='patient_card_details'),
path('api/patients/', get_patients, name='get_patients'),
path('api/departments/time/update/', update_departments_time, name='update_departments_time'),
    path('api/update_middle_timer/', update_middle_timer, name='update_middle_timer'),
path('api/update_next_department/', update_next_department, name='update_next_department'),
path('api/start_timer/', start_timer, name='start_timer'),
    path('api/pause_timer/', pause_timer, name='pause_timer'),
path('api/update_timer/', update_timer, name='update_timer'),
path('api/updatesettimer/', updatesettimer, name='updatesettimer'),
]
