from django.shortcuts import render, redirect, get_object_or_404
from .models import Registration, Department
def home(request):
    return render(request, 'home.html')
def register_view(request):
    if request.method == 'POST':
        try:
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
                status="Progressing",
            )
            department = get_available_department()
            if department:
                patient.assigned_department = department
                patient.current_department=department.name
                patient.save()
                department.current_patients += 1
                department.save()
                return redirect('patient_detail', pk=patient.id)
            else:
                department_obj=get_object_or_404(Department,"Anthropology")
                patient.assigned_department = department_obj
                patient.current_department = department_obj.name
                patient.save()
                department.current_patients += 1
                department.save()
                return redirect('patient_detail', pk=patient.id)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
    return render(request, 'home.html')

def success(request):
    return render(request, 'success.html')
def medicals(request, pk):
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

def get_available_department(exclude_departments=[]):
    try:
        all_departments = Department.objects.all()
        busy_departments = Registration.objects.values_list('current_department', flat=True).distinct()
        free_departments = [department for department in all_departments if department.name not in busy_departments and department.name not in exclude_departments]
        if free_departments:
            return free_departments[0]
        else:
            return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def update_status(request, pk, department):
    if request.method == 'POST':
        patient_obj = get_object_or_404(Registration, id=pk)
        department_obj = get_object_or_404(Department, id=department)
        next_department_obj = Department.objects.filter(id__gt=department).order_by('id').first()
        if not next_department_obj:
            next_department_obj = Department.objects.order_by('id').first()
        if Registration.objects.filter(current_department=next_department_obj.name, assigned_department=next_department_obj).exists():
            next_free_department = get_available_department(exclude_departments=[next_department_obj.name])
            if next_free_department:
                patient_obj.assigned_department = next_free_department
                patient_obj.current_department = next_free_department.name
                patient_obj.status = "Progressing"
            else:
                patient_obj.assigned_department = next_department_obj
                patient_obj.current_department = next_department_obj.name
                patient_obj.status = "Waiting"
        else:
            patient_obj.assigned_department = next_department_obj
            patient_obj.current_department = next_department_obj.name
            patient_obj.status = "Progressing"
        patient_obj.save()
        next_waiting_patient = Registration.objects.filter(current_department=department_obj.name, status="Waiting").first()
        if next_waiting_patient:
            next_waiting_patient.status = "Progressing"
            next_waiting_patient.save()
        return redirect('department_patient_list')
    else:
        return redirect('home')








