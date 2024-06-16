from django.urls import path
from .views import *

urlpatterns = [
    # path('',register_view,name='registration'),
path('home/',home,name='home'),
    path('success/',success,name='success'),
path('medicals/<int:pk>',medicals,name='medicals'),
path('patient_detail/<int:pk>',patient_detail,name='patient_detail'),
path('list/',department_patient_list,name='department_patient_list'),
path('update_status/<int:pk>/<int:department>/', update_status, name='update_status'),
path('patient_departments/', patient_department_history, name='patient_department_history'),
path('remaining_departments/', remaining_departments, name='remaining_departments'),

    path('api/patients/add/', add_patient, name='add_patient'),
path('api/patients/edit/', edit_patient, name='edit_patient'),
path('api/patients/delete/', delete_patient, name='delete_patient'),
path('api/packages/list/', packages_list, name='packages_list'),
path('api/coordinationfacilitator/list/', coordinationfacilitator_list, name='coordinationfacilitator_list'),
path('api/meals/list/', meals_list, name='meals_list'),
path('api/departments/list/', departments_list, name='departments_list'),
path('api/patient/status/', get_patient_status, name='get_patient_status'),
path('api/departments/next/', next_department, name='next_department'),
path('api/departments/current/', get_current_patient_department, name='get_current_patient'),
    path('api/patient-card-details/', get_patient_card_details, name='patient_card_details'),

]
