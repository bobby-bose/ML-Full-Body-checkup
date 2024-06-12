from django.urls import path
from .views import *

urlpatterns = [
    path('',register_view,name='registration'),
path('home/',home,name='home'),
    path('success/',success,name='success'),
path('medicals/<int:pk>',medicals,name='medicals'),
path('patient_detail/<int:pk>',patient_detail,name='patient_detail'),
path('list/',department_patient_list,name='department_patient_list'),
path('update_status/<int:pk>/<int:department>/', update_status, name='update_status'),
path('patient_departments/', patient_department_history, name='patient_department_history'),
path('remaining_departments/', remaining_departments, name='remaining_departments'),
    path('api/patients/', PatientListView.as_view(), name='patient-list'),
    path('api/patients/<int:id>/', PatientDetailView.as_view(), name='patient-detail'),
    path('api/patients/add/', add_patient, name='add_patient'),
path('api/packages/list/', packages_list, name='packages_list'),
path('api/coordinationfacilitator/list/', coordinationfacilitator_list, name='coordinationfacilitator_list'),
path('api/meals/list/', meals_list, name='meals_list'),
path('api/departments/list/', departments_list, name='departments_list'),
]
