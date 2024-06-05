from django.shortcuts import render, redirect
from .models import Registration, Department
from django.db.models import F
from django.shortcuts import get_object_or_404

ALL_DEPARTMENTS=[
    "Anthropology","Vitals","Blood Investigations","Scanning and X-Rays","Psychology","Preventive Oncology","Dental","Nutrition","Phsysiotherapy","Physician","Any Specialist"
]

def home(request):
    return render(request, 'home.html')
def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        mobile_number = request.POST.get('mobile_number')
        address = request.POST.get('address')
        coord_facilitator = request.POST.get('coord_facilitator')
        meals = request.POST.get('meals')

        # Create a new instance of the Registration model
        patient = Registration.objects.create(
            name=name,
            age=age,
            mobile_number=mobile_number,
            address=address,
            coord_facilitator=coord_facilitator,
            meals=meals,
            status="Pending",

        )

        # Find an available department
        department = get_available_department()

        if department:

            patient.assigned_department = department
            patient.current_department=department.name
            patient.save()
            department.current_patients += 1
            department.save()
            return redirect('patient_detail', pk=patient.id)
        else:
            # If no department is available, show a message
            return render(request, 'no_department_available.html')

    return render(request, 'home.html')
def get_available_department(exclude_departments=None):
    if exclude_departments is None:
        exclude_departments = []
    assigned_department_ids = Registration.objects.exclude(assigned_department=None).values_list('assigned_department_id', flat=True)
    available_departments = Department.objects.exclude(id__in=exclude_departments + list(assigned_department_ids)).filter(current_patients__lt=F('capacity'))
    if available_departments.exists():
        print("available_departments.first()",available_departments.first().name,type(available_departments.first().name))
        return available_departments.first()
    else:
        return None
def success(request):
    return render(request, 'success.html')
def medicals(request, pk):
    # Retrieve the patient object
    patient = get_object_or_404(Registration, id=pk)

    context = {
        "patient": patient
    }

    # Find an available department
    department = get_available_department()

    if department:
        # Assign the patient to the department
        patient.assigned_department = department
        patient.save()
        department.current_patients += 1
        department.save()
        return redirect('medical', pk=patient.id)
    else:
        # If no department is available, show a message
        return render(request, 'no_department_available.html')

    return render(request, 'medicals.html', context)

def patient_detail(request,pk):
    obj=Registration.objects.get(
    id=pk
    )
    context={
        "name": obj.name,
"age": obj.age,
"mobile_number": obj.mobile_number,
"address": obj.address,
"coord_facilitator": obj.coord_facilitator,
"meals": obj.meals,
        "current_department":obj.assigned_department

    }
    return render(request, 'patient_details.html', context)

def department_patient_list(request):
    departments = Department.objects.all()
    department_patient_mapping = {}
    for department in departments:
        patients = Registration.objects.filter(current_department=department)
        department_patient_mapping[department] = patients
    context = {
        'department_patient_mapping': department_patient_mapping
    }
    print("department_patient_mapping",department_patient_mapping)
    return render(request, 'department_patient_list.html', context)



def update_status(request, pk):
    if request.method == 'POST':
        patient = get_object_or_404(Registration, id=pk)
        patient.status = 'Completed'
        current_department=patient.current_department
        print("current_department",current_department)
        current_department_index=ALL_DEPARTMENTS.index(current_department)
        print("current_department_index",current_department_index)
        final_current_department_index=current_department_index+1
        print("final_current_department_index",final_current_department_index)
        patient.current_department=ALL_DEPARTMENTS[final_current_department_index]
        patient.save()
        return redirect('department_patient_list')
    else:
        return redirect('home')


