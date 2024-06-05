from django.urls import path
from .views import *

urlpatterns = [
    path('',register_view,name='registration'),
path('home/',home,name='home'),
    path('success/',success,name='success'),
path('medicals/<int:pk>',medicals,name='medicals'),
path('patient_detail/<int:pk>',patient_detail,name='patient_detail'),
path('list/',department_patient_list,name='department_patient_list'),
path('update_status/<int:pk>/<int:department>/', update_status, name='update_status')

]
