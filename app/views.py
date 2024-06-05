from django.shortcuts import render, redirect
from .models import Registration, Department
from django.shortcuts import get_object_or_404









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


def get_available_department():
    try:
        def get_all_departments():
            result = []
            obj = Department.objects.all()
            for i in obj:
                result.append(i.name)
            print("Results", result)
            return result

        def get_all_busydepartments():
            result = []
            obj = Registration.objects.all()
            for i in obj:
                result.append(i.current_department)
            print("Busy Departments===>", result)
            return result

        def get_free_departments():
            result = [department for department in ALL_DEPARTMENTS if department not in BUSY_DEPARTMENTS]
            print("THE FREE DEPARTMENTS", result)
            return result

        ALL_DEPARTMENTS = get_all_departments()

        BUSY_DEPARTMENTS = get_all_busydepartments()
        GET_FREE_DEPARTMENTS=get_free_departments()
        obj=get_object_or_404(Department,name=GET_FREE_DEPARTMENTS[0])
        return obj

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
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



from django.http import Http404

from django.http import Http404
from django.db import transaction



from django.http import Http404

def update_status(request, pk, department):
    if request.method == 'POST':
        print("the patient id is", pk)
        print("tHE department id is", department)
        patient_obj = get_object_or_404(Registration, id=pk)
        department_obj = get_object_or_404(Department, id=department)



        next_department_obj = Department.objects.filter(id__gt=department).order_by('id').first()
        if not next_department_obj:
            next_department_obj = Department.objects.order_by('id').first()

        patient_obj.assigned_department = next_department_obj
        patient_obj.current_department = next_department_obj.name
        patient_obj.save()

        return redirect('department_patient_list')
    else:
        return redirect('home')






