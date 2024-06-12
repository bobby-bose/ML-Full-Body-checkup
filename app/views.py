import json

from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render
from .models import *
from django.http import HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
def home(request):
    return render(request, 'home.html')

def get_available_department_for_package(package):
    departments = Department.objects.filter(package=package)
    for department in departments:
        if not department.current_patient:  # Assuming each department has a `current_patient` field
            return department
    return None
def register_view(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            age = request.POST.get('age')
            mobile_number = request.POST.get('mobile_number')
            address = request.POST.get('address')
            coord_facilitator = request.POST.get('coord_facilitator')
            meals = request.POST.get('meals')
            chosen_package_id = request.POST.get('chosen_package')

            # Get the chosen package
            chosen_package = Oncurepackages.objects.get(id=chosen_package_id)

            # Create a new instance of the Patient model
            patient = Patient.objects.create(
                name=name,
                age=age,
                mobile_number=mobile_number,
                address=address,
                coord_facilitator=coord_facilitator,
                meals=meals,
                chosen_package=chosen_package,
                status="Progressing",
            )

            # Record the entry into the first department of the chosen package
            first_department = get_available_department_for_package(chosen_package)
            if first_department:
                patient.assigned_department = first_department
                patient.current_department = first_department.name
                patient.save()

                # Record the entry into the department
                EnteredDepartment.objects.create(registration=patient, department=first_department)

                return redirect('patient_detail', pk=patient.id)
            else:
                # Handle case when no department is available
                return HttpResponseServerError("No available department for the chosen package.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return HttpResponseServerError("An unexpected error occurred. Please try again later.")
    else:
        oncurepackages = Oncurepackages.objects.all()
        return render(request, 'home.html', {'oncurepackages': oncurepackages})


def success(request):
    return render(request, 'success.html')
def medicals(request, pk):
    patient = get_object_or_404(Patient, id=pk)
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
    obj=Patient.objects.get(
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
    selected_package_id = request.GET.get('package_id')
    packages = Oncurepackages.objects.all()

    if selected_package_id:
        selected_package = get_object_or_404(Oncurepackages, id=selected_package_id)
        departments = Department.objects.filter(oncurepackage=selected_package)
    else:
        selected_package = None
        departments = Department.objects.all()

    department_patient_mapping = {}
    for department in departments:
        patients = Patient.objects.filter(assigned_department=department, chosen_package=department.oncurepackage)
        department_patient_mapping[department] = patients

    context = {
        'packages': packages,
        'selected_package': selected_package,
        'department_patient_mapping': department_patient_mapping
    }
    return render(request, 'department_patient_list.html', context)


def get_available_department_for_package(package):
    try:
        all_departments = Department.objects.filter(oncurepackage=package)
        busy_departments = Patient.objects.values_list('current_department', flat=True).distinct()
        free_departments = [department for department in all_departments if department.name not in busy_departments]
        if free_departments:
            return free_departments[0]
        else:
            return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


from .models import EnteredDepartment


def update_status(request, pk, department):
    if request.method == 'POST':
        patient_obj = get_object_or_404(Patient, id=pk)
        department_obj = get_object_or_404(Department, id=department)
        next_department_obj = Department.objects.filter(
            oncurepackage=patient_obj.chosen_package, id__gt=department).order_by('id').first()

        if not next_department_obj:
            next_department_obj = Department.objects.filter(oncurepackage=patient_obj.chosen_package).order_by(
                'id').first()

        if Patient.objects.filter(current_department=next_department_obj.name,
                                  assigned_department=next_department_obj).exists():
            next_free_department = get_available_department_for_package(patient_obj.chosen_package)
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
        EnteredDepartment.objects.create(registration=patient_obj, department=next_department_obj)

        next_waiting_patient = Patient.objects.filter(current_department=department_obj.name,
                                                      status="Waiting").first()
        if next_waiting_patient:
            next_waiting_patient.status = "Progressing"
            next_waiting_patient.save()
        return redirect('department_patient_list')
    else:
        return redirect('home')


def patient_department_history(request):
    entered_departments = EnteredDepartment.objects.all()
    patient_department_mapping = {}
    for entry in entered_departments:
        patient_name = entry.patient.name
        department_name = entry.department.name
        if patient_name not in patient_department_mapping:
            patient_department_mapping[patient_name] = [department_name]
        else:
            patient_department_mapping[patient_name].append(department_name)
    return render(request, 'patient_department_history.html', {'patient_department_mapping': patient_department_mapping})


def remaining_departments(request):
    patients = Registration.objects.all()
    all_departments = Department.objects.all()
    patient_remaining_departments = {}
    for patient in patients:
        entered_departments = EnteredDepartment.objects.filter(patient=patient).values_list('department__name',
                                                                                            flat=True)
        remaining_departments = [department for department in all_departments if
                                 department.name not in entered_departments]
        patient_remaining_departments[patient] = remaining_departments

    context = {
        'patient_remaining_departments': patient_remaining_departments,
    }
    return render(request, 'remaining_departments.html', context)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from .models import Patient
from .serializers import PatientSerializer

class PatientListView(APIView):
    def get(self, request):
        patients = Patient.objects.all()
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)

class PatientDetailView(RetrieveAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    lookup_field = 'id'  # Assuming you're using 'id' as the lookup field


@csrf_exempt
def add_patient(request):
    if request.method == 'POST':
        print("ENTERED THE POST METHODS")
        try:
            print("ENTERED THE TRY METHODS")
            data = json.loads(request.body.decode('utf-8'))
            print("Received data:", data)  # Log received data for debugging

            patient = Patient(
                name=data.get('name'),
                age=data.get('age'),
                mobile_number=data.get('contact_number'),
                address=data.get('address'),
                coord_facilitator=data.get('coord_facilitator', ''),  # Default to empty string if not provided
                meals=data.get('meals', ''),  # Default to empty string if not provided
                chosen_package_id=data.get('chosen_package'),  # Assuming the package ID is sent in the request
                assigned_department_id=data.get('assigned_department'),
                # Assuming the department ID is sent in the request
                status=data.get('status', ''),  # Default to empty string if not provided
                current_department=data.get('current_department', '')  # Default to empty string if not provided
            )
            patient.save()
            return JsonResponse({'message': 'Patient added successfully!'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

# Update View
class PatientUpdateView(UpdateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    lookup_field = 'id'  # Assuming you're using 'id' as the lookup field

# Delete View
class PatientDeleteView(DestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    lookup_field = 'id'  # Assuming you're using 'id' as the lookup field

