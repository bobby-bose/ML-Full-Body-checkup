from .models import Department, Occupied_Departments, Entered_Departments,Waiting_Departments,Patient_Assignments
from django.shortcuts import render
def patient_assignments_list(request):
    assignments = Patient_Assignments.objects.all()
    return render(request, 'new/pat_ass_list.html', {'assignments': assignments})
def waiting_departments_list(request):
    waiting_departments = Waiting_Departments.objects.all()
    return render(request, 'new/wat_dep_list.html', {'waiting_departments': waiting_departments})
def entered_departments_list(request):
    entered_departments = Entered_Departments.objects.all()
    return render(request, 'new/ent_dep.html', {'entered_departments': entered_departments})

