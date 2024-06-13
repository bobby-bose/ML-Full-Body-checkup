import json

from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render
from .models import *
from django.http import HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
def home(request):
    return render(request, 'home.html')


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
        try:
            data = json.loads(request.body.decode('utf-8'))
            print("Received data:", data)  # Log received data for debugging

            chosen_package_id = data.get('chosen_package')
            if not chosen_package_id:
                return JsonResponse({'error': 'Missing chosen_package field'}, status=400)

            chosen_package = Oncurepackages.objects.get(id=chosen_package_id)

            # Ensure all required fields are present and log them
            required_fields = ['name', 'age', 'contact_number', 'address', 'chosen_package']
            for field in required_fields:
                if field not in data:
                    print(f"Missing required field: {field}")
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

            # Log all the received fields
            for key, value in data.items():
                print(f"{key}: {value}")

            # Get the first available department for the chosen package
            first_department = get_available_department_for_package(chosen_package)
            if not first_department:
                return JsonResponse({'error': 'No available department for the chosen package'}, status=400)

            patient = Patient(
                name=data.get('name'),
                age=data.get('age'),
                mobile_number=data.get('contact_number'),
                address=data.get('address'),
                coord_facilitator_id=data.get('coord_facilitator', ''),  # Default to empty string if not provided
                meals_id=data.get('meals', ''),  # Default to empty string if not provided
                chosen_package=chosen_package,  # Correctly assign the chosen package
                assigned_department=first_department,
                current_department=first_department.name,
                status=data.get('status', 'Progressing')  # Default to 'Progressing' if not provided
            )
            patient.save()

            # Record the entry into the department
            EnteredDepartment.objects.create(registration=patient, department=first_department)

            return JsonResponse({'message': 'Patient added successfully!'}, status=201)
        except Oncurepackages.DoesNotExist:
            return JsonResponse({'error': 'Chosen package not found'}, status=404)
        except Exception as e:
            print(f"Error: {e}")  # Log the exception for debugging
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

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


# Update View
def packages_list(request):
    try:
        obj=Oncurepackages.objects.all()
        final=[]
        for i in obj:
            final.append({"id":i.id,"name":i.name})
        print("The final list of the packages_list")
        print(final)
        return JsonResponse({'list': final}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def coordinationfacilitator_list(request):
    try:
        obj=CoordinationFacilitators.objects.all()
        final=[]
        for i in obj:
            final.append({"id":i.id,"name":i.name})
        # print("The final list of the coordination facilitator")
        # print(final)
        return JsonResponse({'list': final}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def meals_list(request):
    try:
        obj=Meals.objects.all()
        final=[]
        for i in obj:
            final.append({"id":i.id,"name":i.name})
        # print("The final list of the Meals")
        # print(final)
        return JsonResponse({'list': final}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def departments_list(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            patient_id = data.get('patientId')
            print("THE PATIENT ID IS", patient_id)
            if not patient_id:
                return JsonResponse({'error': 'Patient ID not provided'}, status=400)
            print("THE DEPARTMENTS LIST IS ACTIVATED")
            current_patient = Patient.objects.get(id=patient_id)
            chosen_package = current_patient.chosen_package
            departments = Department.objects.filter(oncurepackage=chosen_package)
            departments_list = [{"id": dept.id, "name": dept.name} for dept in departments]
            print("The Department list is", departments_list)
            return JsonResponse({'list': departments_list}, status=200)
        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=404)
        except Oncurepackages.DoesNotExist:
            return JsonResponse({'error': 'Package not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


@csrf_exempt
def get_patient_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            package_id = data.get('package_id')
            department_id = data.get('department_id')

            if not package_id or not department_id:
                return JsonResponse({'error': 'Package ID or Department ID not provided'}, status=400)

            package = Oncurepackages.objects.get(id=package_id)
            department = Department.objects.get(id=department_id)

            message = f"The patient is currently in {department.name} department of the {package.name} package."
            print("MESSAGE",message)
            return JsonResponse({'message': message}, status=200)
        except Oncurepackages.DoesNotExist:
            return JsonResponse({'error': 'Package not found'}, status=404)
        except Department.DoesNotExist:
            return JsonResponse({'error': 'Department not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)



@csrf_exempt
def get_current_patient_department(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            patient_id = data.get('id')
            if not patient_id:
                return JsonResponse({'error': 'Package ID or Department ID not provided'}, status=400)
            patient=Patient.objects.get(id=patient_id)
            patient_name=patient.name
            current_department=patient.current_department
            message = f"The patient {patient_name} is currently in {current_department}"
            print("MESSAGE",message)
            return JsonResponse({'currentid': current_department}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)