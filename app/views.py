from .models import *
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .serializer import PatientSerializer,DepartmentSerializer


@csrf_exempt
def add_patient(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            print("Received data:", data)
            chosen_package_id = data.get('chosen_package')
            if not chosen_package_id:
                return JsonResponse({'error': 'Missing chosen_package field'}, status=400)
            chosen_package = Oncurepackages.objects.get(id=chosen_package_id)
            required_fields = ['name', 'age', 'contact_number', 'address', 'chosen_package']
            for field in required_fields:
                if field not in data:
                    print(f"Missing required field: {field}")
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
            for key, value in data.items():
                print(f"{key}: {value}")
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
            )
            patient.save()
            EnteredDepartment.objects.create(registration=patient, department=first_department)
            return JsonResponse({'message': 'Patient added successfully!'}, status=201)
        except Oncurepackages.DoesNotExist:
            return JsonResponse({'error': 'Chosen package not found'}, status=404)
        except Exception as e:
            print(f"Error: {e}")  # Log the exception for debugging
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Patient, Oncurepackages, Department
from .serializers import PatientSerializer

import json


@csrf_exempt
@api_view(['POST'])
def details_patient(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            print("Received data:", data)
            received_patient_id = data.get('patId')
            if not received_patient_id:
                return JsonResponse({'error': 'Missing received_patient_id field'}, status=400)

            obj = Patient.objects.get(id=received_patient_id)
            chosen_package_obj = obj.chosen_package
            chosen_package_name = chosen_package_obj.name
            print('99999999999999999999999', chosen_package_name)

            package_obj = Oncurepackages.objects.get(name=chosen_package_name)
            obj2 = Department.objects.filter(oncurepackage=package_obj)
            assigned_department_obj = obj.assigned_department
            assigned_department_name = assigned_department_obj.name
            print("111111111111", assigned_department_name)
            patient_serializer = PatientSerializer(obj)
            departments_serializer = DepartmentSerializer(obj2, many=True)
            print("DEPARTEMNT SERIALZIER",departments_serializer.data)
            department_names = list(obj2.values_list('name', flat=True))
            print("DDDDDDDDDDDDDDDDD",department_names)
            return Response({
                'message': 'Patient added successfully!',
                'data': patient_serializer.data,
                'departments': department_names,
                'assigned_dep': assigned_department_name
            }, status=200)
        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=404)
        except Oncurepackages.DoesNotExist:
            return JsonResponse({'error': 'Oncure package not found'}, status=404)
        except Department.DoesNotExist:
            return JsonResponse({'error': 'Department not found'}, status=404)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def get_available_department_for_package(package):
    try:
        all_departments = Department.objects.filter(oncurepackage=package)
        busy_departments = Patient.objects.filter(assigned_department__isnull=False).values_list('assigned_department__name', flat=True).distinct()
        free_departments = [department for department in all_departments if department.name not in busy_departments]
        if free_departments:
            return free_departments[0]  # Return the first free department
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
            message = f"TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTThe patient {patient_name} is currently in {current_department}"
            print("MESSAGE",message)
            return JsonResponse({'currentid': current_department}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def get_current_patient_package(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            patient_id = data.get('id')
            if not patient_id:
                return JsonResponse({'error': 'Package ID or Department ID not provided'}, status=400)
            patient=Patient.objects.get(id=patient_id)
            patient_name=patient.name
            print("Printed check 1")
            current_package=patient.chosen_package.name
            print("Printed Check 2")
            message = f"The patient {patient_name} is currently in package : {type(current_package)}"
            print("MESSAGE",message)
            return JsonResponse({'currentid': current_package}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def next_department(request):
    if request.method == 'POST':
        print("ENTERED THE POST METHOD OF NEXT_DEPARTMENT")
        try:
            data = json.loads(request.body)
            patient_id = data.get('patientId')
            chosen_package_id = data.get('chosenPackageId')
            current_department_id = data.get('currentDepartmentId')
            print("EACH OF THEM IS", patient_id, chosen_package_id, current_department_id)
            patient = Patient.objects.get(id=patient_id)
            patient_obj=Patient.objects.get(id=patient_id)

            chosen_package = patient.chosen_package
            print("The chosen package", chosen_package, type(chosen_package))
            try:
                current_department = Department.objects.get(name=current_department_id)
            except Department.DoesNotExist:
                print(f"Department with ID {current_department_id} does not exist.")
                return JsonResponse(
                    {'success': False, 'message': f'Department with ID {current_department_id} not found'})
            print("The current department", current_department, type(current_department))
            departments = Department.objects.filter(oncurepackage=chosen_package).order_by('id')
            print("The departments", departments, type(departments))
            current_index = list(departments).index(current_department)
            print("The current_index", current_index, type(current_index))
            print("REACHED CHECK 1")
            next_department = None
            for next_index in range(current_index + 1, len(departments)):
                potential_next_department = departments[next_index]
                if not Patient.objects.filter(assigned_department=potential_next_department,
                                              chosen_package=chosen_package).exists():
                    next_department = potential_next_department
                    break
            if next_department:
                patient.current_department = next_department.name
                patient.assigned_department = next_department

                print("THE NEXT DEPARTMENT IS", next_department)
                print("SUCCESSFULLY CHANGED THE DEPARTMENT")
                patient.save()

                EnteredDepartment.objects.create(registration=patient, department=next_department)
                return JsonResponse({'success': True, 'nextDepartment': next_department.name})
            else:
                return JsonResponse({'success': False, 'message': 'No more available departments in the package'})
        except Patient.DoesNotExist:
            print(f"Patient with ID {patient_id} does not exist.")
            return JsonResponse({'success': False, 'message': 'Patient not found'})
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def edit_patient(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            print("Received data:", data)  # Log received data for debugging
            patient_id = data.get('patientId')
            for key, value in data.items():
                print(f"{key}: {value}")
            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                return JsonResponse({'error': 'Patient not found'}, status=404)
            patient.name = data.get('name')
            patient.mobile_number = data.get('contactNumber')
            patient.address = data.get('address')
            patient.save()
            print("UPDATED SUCCESSFULLY")
            return JsonResponse({'message': 'Patient details updated successfully!'}, status=200)
        except Exception as e:
            print(f"Error: {e}")  # Log the exception for debugging
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def delete_patient(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            print("Received data:", data)  # Log received data for debugging
            patient_id = data.get('patientId')
            print("THE RECEIVED PATIENT ID IS",patient_id)
            try:
                patient = Patient.objects.get(id=patient_id)
                patient.delete()
            except Patient.DoesNotExist:
                return JsonResponse({'error': 'Patient not found'}, status=404)
            print("DELETED SUCCESSFULLY")
            return JsonResponse({'message': 'Patient details deleted successfully!'}, status=200)
        except Exception as e:
            print(f"Error: {e}")  # Log the exception for debugging
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
def decrement_time(time_str):
    time_format = "%M:%S"
    time_obj = datetime.datetime.strptime(time_str, time_format)
    total_seconds = time_obj.minute * 60 + time_obj.second
    if total_seconds > 0:
        total_seconds -= 1
    mins, secs = divmod(total_seconds, 60)
    return f"{mins}:{secs:02d}"



def get_patient_card_details(request):
    patients = Patient.objects.all()
    card_details = []
    for patient in patients:
        current_department = patient.assigned_department.name if patient.assigned_department else None
        upcoming_department = None
        departments = patient.chosen_package.departments.all().order_by('id') if patient.chosen_package else []
        current_department_found = False
        current_time = patient.remaining_time
        consulting = patient.timer_active
        updated_time = current_time  # Assume this is being updated elsewhere
        patient.current_time = updated_time
        patient.save()
        for department in departments:
            if current_department_found:
                upcoming_department = department.name
                break
            if department.name == current_department:
                current_department_found = True
        package_departments = Department.objects.filter(oncurepackage=patient.chosen_package)
        entered_departments = EnteredDepartment.objects.filter(registration=patient).values_list('department__name', flat=True)
        remaining_departments = [department.name for department in package_departments if department.name not in entered_departments]
        if upcoming_department:
            remaining_departments = [dept for dept in remaining_departments if dept != upcoming_department]
        card_details.append({
            'id': patient.id,
            'patient_name': patient.name,
            'buttonText': current_department,
            'upcoming': upcoming_department,
            'remaining_departments': remaining_departments,
            'time': updated_time,
            'consulting': consulting,
        })
    return JsonResponse({'cardDetails': card_details})

def get_patient_middle_details(request):
    patients = Patient.objects.all()
    card_details = []
    for patient in patients:
        current_department = patient.current_department
        upcoming_department = None
        departments = patient.chosen_package.departments.all().order_by('id')
        current_department_found = False
        current_time = patient.current_time
        consulting = patient.consulting
        timer = patient.timer

        # Decrement the current_time and update the patient object
        updated_time = decrement_time(current_time)
        patient.current_time = updated_time
        patient.save()
        for department in departments:
            if current_department_found:
                upcoming_department = department.name
                break
            if department.name == current_department:
                current_department_found = True
        package_departments = Department.objects.filter(oncurepackage=patient.chosen_package)
        entered_departments = EnteredDepartment.objects.filter(registration=patient).values_list('department__name',
                                                                                               flat=True)
        remaining_departments = [department.name for department in package_departments if
                                 department.name not in entered_departments]
        print("THE REMAINING DEPARTMENTS ARE", remaining_departments)
        if upcoming_department:
            remaining_departments.remove(upcoming_department)
        card_details.append({
            'id': patient.id,
            'patient_name': patient.name,
            'buttonText': current_department,
            'upcoming': upcoming_department,
            'remaining_departments': remaining_departments,
            'time': updated_time,
            'consulting': consulting,
            'timer': timer
        })
        print("THE CARD DETAILS", card_details)

    return JsonResponse({'cardDetails': card_details})

@csrf_exempt
def update_departments_time(request):
    if request.method == 'POST':
        print("ENTERED THE POST METHOD OF UPDATE DEPARTMENT TIME")
        try:
            data = json.loads(request.body)
            patient_id = data.get('patientId')
            chosen_package_id = data.get('currentPackage')
            current_department_id = data.get('currentDepartmentId')
            new_time = data.get('newTime')
            print("EACH OF THEM IS", patient_id, chosen_package_id, current_department_id,new_time)
            try:
                patient = Patient.objects.get(
                    id=patient_id,
                    chosen_package__name=chosen_package_id,
                    current_department=current_department_id
                )
            except Patient.DoesNotExist:
                print(f"Patient with chosen package {chosen_package_id} and current department {current_department_id} not found")
                return JsonResponse(
                    {'success': False, 'message': f'Patient with chosen package {chosen_package_id} and current department {current_department_id} not found'}
                )
            print("The patient", patient)
            patient.current_time = new_time
            patient.save()
            print("Updated the current time for the patient")
            return JsonResponse({'success': True, 'message': 'Current time updated successfully'})
        except Exception as e:
            print(f"Error updating current time: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
def update_consulting_status_true(request):
    if request.method == 'POST':
        print("ENTERED THE POST METHOD OF UPDATE CONSULTING TIME TO TRUE")
        try:
            data = json.loads(request.body)
            patient_id = data.get('patientId')
            print("EACH OF THEM IS", patient_id)
            try:
                patient = Patient.objects.get(
                    id=patient_id,
                )
            except Patient.DoesNotExist:
                print(f"Patient with  not found")
                return JsonResponse(
                    {'success': False, 'message': f'Patient with not found'}
                )
            print("The patient", patient)
            patient.consulting="consulting"
            patient.save()
            print("Updated the consulting for the patient")
            return JsonResponse({'success': True, 'message': 'Current patient consulting updated successfully'})
        except Exception as e:
            print(f"Error updating current time: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})
@csrf_exempt
def update_consulting_status_false(request):
    if request.method == 'POST':
        print("ENTERED THE POST METHOD OF UPDATE CONSULTING TIME TO FALSE")
        try:
            data = json.loads(request.body)
            patient_id = data.get('patientId')
            print("EACH OF THEM IS", patient_id)
            try:
                patient = Patient.objects.get(
                    id=patient_id,
                )
            except Patient.DoesNotExist:
                print(f"Patient with  not found")
                return JsonResponse(
                    {'success': False, 'message': f'Patient with not found'}
                )
            print("The patient", patient)
            patient.consulting="not consulting"
            patient.save()
            print("Updated the consulting for the patient to false")
            return JsonResponse({'success': True, 'message': 'Current patient consulting updated successfully'})
        except Exception as e:
            print(f"Error updating current time: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})

def get_patients(request):
    patients = Patient.objects.all()
    patients_list = list(patients.values())
    return JsonResponse(patients_list, safe=False)
@csrf_exempt
def get_current_patient_time(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            patient_id = data.get('id')
            if not patient_id:
                return JsonResponse({'error': 'Package ID or Department ID not provided'}, status=400)
            patient=Patient.objects.get(id=patient_id)
            time=patient.current_time
            print("THE CURRENT TIMEEEEEEEEEEEE",time)
            return JsonResponse({'time': time}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def decrement_time_middle(time_str):
    """Decrement the MM:SS time string by one second."""
    time_format = "%M:%S"
    time_obj = datetime.datetime.strptime(time_str, time_format)
    total_seconds = time_obj.minute * 60 + time_obj.second
    if total_seconds > 0:
        total_seconds -= 1
    mins, secs = divmod(total_seconds, 60)
    return f"{mins}:{secs:02d}"

@method_decorator(csrf_exempt, name='dispatch')
class GetTimer(View):
    def post(self, request):
        data = json.loads(request.body)
        patient_id = data.get('patientId', None)
        try:
            patient = Patient.objects.get(id=patient_id)
            current_time = patient.remaining_time
            if current_time > 0:
                current_time -= 1
                patient.remaining_time = current_time
                patient.save()
            else:
                current_time = 0  # ensure timer does not go below 0
            return JsonResponse({'timer': current_time})
        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class UpdateTimer(View):
    def post(self, request):
        data = json.loads(request.body)
        pat_id = data.get('patId', None)
        timer_value = data.get('timer', None)
        print("1")
        if pat_id is None or timer_value is None:
            return JsonResponse({'status': 'error', 'message': 'Patient ID and timer value are required'}, status=400)
        try:
            print("2")
            patient = Patient.objects.get(id=pat_id)
            print("3")
            print("QQQQQQQQQQQQ",patient.name)
            patient.chosen_time = timer_value.split(':')[1]
            patient.remaining_time=timer_value.split(':')[1]
            print("FFFFFFFFFFFFFFFFFFFFFFF",timer_value.split(':')[1])
            patient.save()
            return JsonResponse({'status': 'success'})
        except Patient.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Patient not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
@method_decorator(csrf_exempt, name='dispatch')
class UpdateMiddleTimer(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            pat_id = data.get('patientId', None)
            new_time = data.get('newTime', None)
            if new_time is not None:
                new_time = new_time.split(":")[1]
                new_time = int(new_time)
            if pat_id is None or new_time is None:
                return JsonResponse({'status': 'error', 'message': 'Invalid data provided'}, status=400)
            try:
                patient = Patient.objects.get(id=pat_id)
                patient.remaining_time = new_time
                patient.save()
            except Patient.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Patient not found'}, status=404)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
@csrf_exempt
@api_view(['POST'])
def update_middle_timer(request):
    if request.method=="POST":
        data = json.loads(request.body)
        print("{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{[[[[")
        pat_id = data.get('patId', None)
        new_time = data.get('timer', None)
        print("&&&&&&&&&&&&&&&",pat_id,new_time)
        obj=Patient.objects.get(id=pat_id)
        new_time = new_time.split(":")[1]
        new_time = int(new_time)
        obj.remaining_time=new_time
        obj.chosen_time=new_time
        obj.save()
        print("UPDATED THE MIDDLE TIMER")
        return Response({
            "remaining_time":new_time
        }, status=200)
    else:
        return Response({
            "NOT OKAY"
        }, status=500)

@csrf_exempt
@api_view(['POST'])
def update_each_second(request):
    if request.method=="POST":
        data = json.loads(request.body)
        print("3333333333333")
        pat_id = data.get('patId', None)
        print("!!!!!!!!!!!!",pat_id)
        obj=Patient.objects.get(id=pat_id)
        new_time=obj.remaining_time
        new_time=new_time-1
        obj.remaining_time=new_time
        obj.save()
        print("UPDATED each second to ",new_time)
        return Response({
            "updated_time":new_time
        }, status=200)
    else:
        return Response({
            "NOT OKAY"
        }, status=500)

# @csrf_exempt
# @api_view(['POST'])
# def update_next_department(request):
#     if request.method=="POST":
#         data = json.loads(request.body)
#         print("@@@@@@")
#         pat_id = data.get('patId', None)
#         pac_id=data.get('cho_pak',None)
#         patient_obj=Patient.objects.get(id=pat_id)
#         chosen_package_obj=Oncurepackages.objects.get(id=pac_id)
#         print("%%%%%%%%%%%%%",pat_id,'^^^^^^^^^^^^',pac_id)
#         obj=Patient.objects.get(id=pat_id)
#         curent_department=obj.remaining_time
#         print("CURRENT DEPARTMENT",curent_department)
#         obj2 = EnteredDepartment.objects.filter(registration=patient_obj).values_list('department__name', flat=True)
#         visited_department_list = list(obj2)
#         print("ALL THE VISITED DEPARTMENT LISTS ",visited_department_list)
#         obj3 = Department.objects.filter(oncurepackage=chosen_package_obj).values_list('name', flat=True)
#         all_department_list = list(obj3)
#         print("ALL  DEPARTMENT LISTS ", all_department_list)
#         visited_department_list=set(visited_department_list)
#         all_department_list=set(all_department_list)
#         unvisited_department_list = list(visited_department_list.symmetric_difference(all_department_list))
#         assigned_departments = Patient.objects.values_list('assigned_department__name', flat=True)
#         assigned_departments_list = list(assigned_departments)
#         print("ALL ENGAGED DEPARTMENTS ", assigned_departments_list)
#         print("ALL THE UNVISITED DEPARTMENT LISTS ", unvisited_department_list)
#         return Response({
#             "department_list":unvisited_department_list
#         }, status=200)
#     else:
#         return Response({
#             "NOT OKAY"
#         }, status=500)

@csrf_exempt
@api_view(['POST'])
def update_next_department(request):
    if request.method == "POST":
        data = json.loads(request.body)
        pat_id = data.get('patId', None)
        pac_id = data.get('cho_pak', None)
        patient_obj = Patient.objects.get(id=pat_id)
        chosen_package_obj = Oncurepackages.objects.get(id=pac_id)
        obj = Patient.objects.get(id=pat_id)

        visited_departments = set(EnteredDepartment.objects.filter(registration=patient_obj).values_list('department__name', flat=True))
        all_departments = list(Department.objects.filter(oncurepackage=chosen_package_obj).values_list('name', flat=True))
        assigned_departments = set(Patient.objects.values_list('assigned_department__name', flat=True).exclude(id=pat_id))
        unvisited_department_list = [department for department in all_departments if department not in visited_departments and department not in assigned_departments]
        print("THE IMMMMMMMMMMMMMMMMMMMMMMM", unvisited_department_list[0])
        new_department_obj=Department.objects.get(name=unvisited_department_list[0])
        obj.assigned_department=new_department_obj
        obj.save()
        print("The ",obj.name," chnaged to",obj.assigned_department)
        return Response({
            "next_department": unvisited_department_list[0]
        }, status=200)




