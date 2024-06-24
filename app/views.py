from .models import *
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .serializer import PatientSerializer,DepartmentSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Patient, Oncurepackages, EnteredDepartment, Department
import json

@csrf_exempt
def add_patient(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            chosen_package_id = data.get('chosen_package')
            waiting_next_package=None
            if not chosen_package_id:

                return JsonResponse({'error': 'Missing chosen_package field'}, status=400)
            try:
                chosen_package = Oncurepackages.objects.get(id=chosen_package_id)
                waiting_next_package = chosen_package
                waiting_package = Oncurepackages.objects.get(name="waiting")

            except Oncurepackages.DoesNotExist:

                return JsonResponse({'error': 'Chosen package not found'}, status=404)
            required_fields = ['name', 'age', 'contact_number', 'address', 'chosen_package']
            for field in required_fields:
                if field not in data:

                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
            # for key, value in data.items():

            first_department = get_available_department_for_package(chosen_package)
            if not first_department:

                first_department = Department.objects.filter(oncurepackage=waiting_package).first()
                chosen_package=waiting_package

                if not first_department:

                    return JsonResponse({'error': 'No available department found'}, status=404)

            patient = Patient(
                name=data.get('name'),
                age=data.get('age'),
                mobile_number=data.get('contact_number'),
                address=data.get('address'),
                coord_facilitator_id=data.get('coord_facilitator', ''),  # Default to empty string if not provided
                meals_id=data.get('meals', ''),  # Default to empty string if not provided
                chosen_package=chosen_package,  # Correctly assign the chosen package
                assigned_department=first_department,
                chosen_time=first_department.time,
                remaining_time=first_department.time,
            waiting_package=waiting_next_package
            )
            patient.save()
            EnteredDepartment.objects.create(registration=patient, department=first_department)
            return JsonResponse({'message': 'Patient added successfully!'}, status=201)
        except Exception as e:

            return JsonResponse({'error': str(e)}, status=400)
    else:

        return JsonResponse({'error': 'Invalid request method'}, status=400)


def get_available_department_for_package(package):

    departments = Department.objects.filter(oncurepackage=package)
    for department in departments:

        assigned_patients = Patient.objects.filter(assigned_department=department).count()
        if assigned_patients == 0:

            return department

    return None



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
            received_patient_id = data.get('patId')
            if not received_patient_id:
                return JsonResponse({'error': 'Missing received_patient_id field'}, status=400)
            obj = Patient.objects.get(id=received_patient_id)
            chosen_package_obj = obj.chosen_package
            chosen_package_name = chosen_package_obj.name
            package_obj = Oncurepackages.objects.get(name=chosen_package_name)
            obj2 = Department.objects.filter(oncurepackage=package_obj)

            assigned_department_obj = obj.assigned_department
            assigned_department_name = assigned_department_obj.name
            patient_serializer = PatientSerializer(obj)
            departments_serializer = DepartmentSerializer(obj2, many=True)
            department_names = list(obj2.values_list('name', flat=True))

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
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


# Update View
def packages_list(request):
    try:
        obj = Oncurepackages.objects.all()
        final = [{"id": 0, "name": "Select a Package"}]  # Initialize final list with 'Select a Package'
        for i in obj:
            final.append({"id": i.id, "name": i.name})

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

            if not patient_id:
                return JsonResponse({'error': 'Patient ID not provided'}, status=400)

            current_patient = Patient.objects.get(id=patient_id)
            chosen_package = current_patient.chosen_package
            departments = Department.objects.filter(oncurepackage=chosen_package)
            departments_list = [{"id": dept.id, "name": dept.name} for dept in departments]

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

            current_package=patient.chosen_package.name

            message = f"The patient {patient_name} is currently in package : {type(current_package)}"

            return JsonResponse({'currentid': current_package}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def next_department(request):
    if request.method == 'POST':

        try:
            data = json.loads(request.body)
            patient_id = data.get('patientId')
            chosen_package_id = data.get('chosenPackageId')
            current_department_id = data.get('currentDepartmentId')

            patient = Patient.objects.get(id=patient_id)
            patient_obj=Patient.objects.get(id=patient_id)
            chosen_package = patient.chosen_package

            try:
                current_department = Department.objects.get(name=current_department_id)
            except Department.DoesNotExist:

                return JsonResponse(
                    {'success': False, 'message': f'Department with ID {current_department_id} not found'})

            departments = Department.objects.filter(oncurepackage=chosen_package).order_by('id')

            current_index = list(departments).index(current_department)

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

                patient.save()
                EnteredDepartment.objects.create(registration=patient, department=next_department)
                return JsonResponse({'success': True, 'nextDepartment': next_department.name})
            else:
                return JsonResponse({'success': False, 'message': 'No more available departments in the package'})
        except Patient.DoesNotExist:

            return JsonResponse({'success': False, 'message': 'Patient not found'})
        except Exception as e:

            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def edit_patient(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            patient_id = data.get('patientId')

            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                return JsonResponse({'error': 'Patient not found'}, status=404)
            patient.name = data.get('name')
            patient.mobile_number = data.get('contactNumber')
            patient.address = data.get('address')
            patient.save()

            return JsonResponse({'message': 'Patient details updated successfully!'}, status=200)
        except Exception as e:

            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def delete_patient(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            patient_id = data.get('patientId')

            try:
                patient = Patient.objects.get(id=patient_id)
                patient.delete()
            except Patient.DoesNotExist:
                return JsonResponse({'error': 'Patient not found'}, status=404)

            return JsonResponse({'message': 'Patient details deleted successfully!'}, status=200)
        except Exception as e:

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
            remaining_departments = [dept for dept in remaining_departments if dept != upcoming_department and dept != current_department]

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


    return JsonResponse({'cardDetails': card_details})

@csrf_exempt
def update_departments_time(request):
    if request.method == 'POST':

        try:
            data = json.loads(request.body)
            patient_id = data.get('patientId')
            chosen_package_id = data.get('currentPackage')
            current_department_id = data.get('currentDepartmentId')
            new_time = data.get('newTime')

            try:
                patient = Patient.objects.get(
                    id=patient_id,
                    chosen_package__name=chosen_package_id,
                    current_department=current_department_id
                )
            except Patient.DoesNotExist:

                return JsonResponse(
                    {'success': False, 'message': f'Patient with chosen package {chosen_package_id} and current department {current_department_id} not found'}
                )

            patient.current_time = new_time
            patient.save()

            return JsonResponse({'success': True, 'message': 'Current time updated successfully'})
        except Exception as e:

            return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
def update_consulting_status_true(request):
    if request.method == 'POST':

        try:
            data = json.loads(request.body)
            patient_id = data.get('patientId')

            try:
                patient = Patient.objects.get(
                    id=patient_id,
                )
            except Patient.DoesNotExist:

                return JsonResponse(
                    {'success': False, 'message': f'Patient with not found'}
                )

            patient.consulting="consulting"
            patient.save()

            return JsonResponse({'success': True, 'message': 'Current patient consulting updated successfully'})
        except Exception as e:

            return JsonResponse({'success': False, 'message': str(e)})
@csrf_exempt
def update_consulting_status_false(request):
    if request.method == 'POST':

        try:
            data = json.loads(request.body)
            patient_id = data.get('patientId')

            try:
                patient = Patient.objects.get(
                    id=patient_id,
                )
            except Patient.DoesNotExist:

                return JsonResponse(
                    {'success': False, 'message': f'Patient with not found'}
                )

            patient.consulting="not consulting"
            patient.save()

            return JsonResponse({'success': True, 'message': 'Current patient consulting updated successfully'})
        except Exception as e:

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


@csrf_exempt
@api_view(['POST'])
def update_middle_timer(request):
    if request.method=="POST":
        data = json.loads(request.body)

        pat_id = data.get('patId', None)
        new_time = data.get('timer', None)

        obj=Patient.objects.get(id=pat_id)
        new_time = new_time.split(":")[1]
        new_time = int(new_time)
        obj.remaining_time=new_time
        obj.chosen_time=new_time
        obj.save()

        return Response({
            "remaining_time":new_time
        }, status=200)
    else:
        return Response({
            "NOT OKAY"
        }, status=500)


@csrf_exempt
@api_view(['POST'])
def update_next_department(request):
    if request.method == "POST":
        data = json.loads(request.body)
        pat_id = data.get('patId', None)
        pac_id = data.get('cho_pak', None)
        patient_obj = Patient.objects.get(id=pat_id)
        chosen_package_obj = Oncurepackages.objects.get(id=pac_id)
        all_departments = Department.objects.filter(oncurepackage=chosen_package_obj)
        all_department_names = list(all_departments.values_list('name', flat=True))
        visited_departments = EnteredDepartment.objects.filter(registration=patient_obj).values_list('department__name', flat=True)
        visited_department_names = list(visited_departments)
        assigned_departments = Patient.objects.values_list('assigned_department__name', flat=True)
        assigned_department_names = list(assigned_departments)
        unvisited_departments = [dept for dept in all_department_names if dept not in visited_department_names]
        next_department = None
        for department in unvisited_departments:
            if department not in assigned_department_names:
                next_department = Department.objects.get(name=department, oncurepackage=chosen_package_obj)
                break
        if len(unvisited_departments) == 0:
            return Response({
                "next_department": "FINISHED"
            }, status=200)
        patient_obj.assigned_department = next_department
        patient_obj.remaining_time=next_department.time
        patient_obj.chosen_time = next_department.time
        patient_obj.progress_bar=100
        patient_obj.save()
        EnteredDepartment.objects.create(registration=patient_obj, department=next_department)
        return Response({
            "next_department": next_department.name
        }, status=200)
    else:
        return Response({
            "message": "NOT OKAY"
        }, status=500)

@csrf_exempt
def start_timer(request):
    if request.method == "POST":
        data = json.loads(request.body)
        patient_id = data.get('patId', None)
        obj=Patient.objects.get(id=patient_id)
        obj.timer_active=True
        obj.save()
        return JsonResponse({'status': 'started'})
    else:
        return Response({
            "message": "NOT OKAY"
        }, status=500)

@csrf_exempt
def update_timer(request):
        obj = Patient.objects.all()
        for i in obj:
            if i.timer_active:
                if i.remaining_time>-1:
                    timer = i.remaining_time
                    timer = timer - 1
                    i.remaining_time = timer
                    var=timer
                    if i.progress_bar>0:
                        progress=i.progress_bar
                        new_var=var
                        new_progress=progress
                        decrement=int(new_progress/new_var)
                        new_progress=new_progress-decrement
                        progress=new_progress
                        i.progress_bar=progress
                        i.save()
                    else:
                        i.timer_active = False
                        i.save()
                else:
                    i.timer_active=False
                    i.save()
        return JsonResponse({'status': 'Updating'})

@csrf_exempt
def pause_timer(request):
    if request.method == "POST":
        data = json.loads(request.body)
        patient_id = data.get('patId', None)

        obj = Patient.objects.get(id=patient_id)
        obj.timer_active = False
        obj.save()

        return JsonResponse({'status': 'paused'})
    else:
        return Response({
            "message": "NOT OKAY"
        }, status=500)


def waiting_patients(request):
    chosen_obj = Oncurepackages.objects.get(name="waiting")
    patients = Patient.objects.filter(chosen_package=chosen_obj)
    card_details = []
    for patient in patients:
        card_details.append({
            'id': patient.id,
            'name': patient.name,
            'status': 'Waiting',
            'w_assigned_department': patient.waiting_package.name,  # Assuming you want the name of the waiting_package
        })
    return JsonResponse({'patients': card_details})

@csrf_exempt
def updatesettimer(request):
    if request.method=="POST":
        data = json.loads(request.body)
        patid=data.get('patId', None)
        time = data.get('time', None)
        patient=Patient.objects.get(id=patid)
        patient.remaining_time=time
        patient.progress_bar=100
        patient.save()
        return JsonResponse({'status':'Success'})
    else:
        return JsonResponse({'status': 'Failure'})


