from .models import *
import datetime
from .serializer import PatientSerializer,DepartmentSerializer
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Patient, Oncurepackages, Department
from .serializers import PatientSerializer
import json
from .utilities import *







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
            assignments=Patient_Assignments.objects.get(patient=obj)
            remaining_time_minutes=assignments.remaining_minutes
            remaining_time_seconds=assignments.remaining_second
            assigned_department_name=assignments.assigned.name
            progress_bar=assignments.progress_bar
            patient_serializer = PatientSerializer(obj)
            department_names = list(obj2.values_list('name', flat=True))
            return Response({
                'message': 'Patient added successfully!',
                'data': patient_serializer.data,
                'remaining_time_minutes':remaining_time_minutes,
                'remaining_time_seconds':remaining_time_seconds,
                'departments': department_names,
                'assigned_dep': assigned_department_name,
                'progress_bar':progress_bar
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
        avoid=["waiting","FINISHED"]
        for i in obj:
            if i.name in avoid:
                pass
            else:
                final.append({"id": i.id, "name": i.name})
        print("PACKAGES ",final)
        return JsonResponse({'list': final}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def coordinationfacilitator_list(request):
    try:
        obj=CoordinationFacilitators.objects.all()
        final = [{"id": 0, "name": "Select a CF"}]
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
        final = [{"id": 0, "name": "Select a Meals"}]
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
            current_department=patient.current_department
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
            print("rrrrrrrrrrrrr")
            data = json.loads(request.body.decode('utf-8'))
            print("data",data)
            patient_id = data.get('patientId')
            print("patient_id", patient_id)
            try:
                patient = Patient.objects.get(id=patient_id)
                patient_assignments = Patient_Assignments.objects.filter(patient=patient)
                occupied_departments_to_delete = []
                for assignment in patient_assignments:
                    if assignment.assigned:
                        occupied_departments_to_delete.append(assignment.assigned)
                    if assignment.waiting:
                        occupied_departments_to_delete.append(assignment.waiting)
                patient.delete()
                patient_count=Patient.objects.all().count()
                if patient_count:
                    pass
                else:
                    obj=Waiting_Departments.objects.all()
                    obj.delete()
                    obj2=Occupied_Departments.objects.all()
                    obj2.delete()
                    obj3=Unentered_Departments.objects.all()
                    obj3.delete()
                for assignment in patient_assignments:
                    assignment.delete()
                for department in occupied_departments_to_delete:
                    try:
                        occupied_department = Occupied_Departments.objects.get(department=department)
                        occupied_department.delete()
                    except Occupied_Departments.DoesNotExist:
                        continue
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

@csrf_exempt
def get_patient_card_details(request):
        patients = Patient.objects.all()
        card_details = []
        for patient in patients:
            patient_id = patient.id
            patient_name = patient.name
            patient_assignment_object = Patient_Assignments.objects.get(patient=patient)
            current_department = patient_assignment_object.assigned
            next_department=patient_assignment_object.waiting
            next_dept_minutes=Department.objects.get(name=next_department.name).remaining_minutes
            next_dept_seconds = Department.objects.get(name=next_department.name).remaining_seconds
            updated_time_minutes = patient_assignment_object.remaining_minutes
            updated_time_seconds = patient_assignment_object.remaining_second
            total_minutes=patient_assignment_object.total_minute
            total_seconds=patient_assignment_object.total_second
            total_time=str(total_minutes)+" : "+str(total_seconds)
            buttonText1 = str(current_department.name)+"      ["+str(updated_time_minutes)+" : "+str(updated_time_seconds)+"]"
            buttonText2 = str(next_department.name) + "       [" + str(next_dept_minutes)+" : "+str(next_dept_seconds)+"]"
            card_details.append({
                'id': patient_id,
                'patient_name': patient_name,
                'total_time':total_time,
                'buttonText1': buttonText1,
                'buttonText2': 'Upcoming',
                'buttonText3': buttonText2,
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
        new_time = new_time.split(":")[1]
        new_time = int(new_time)
        obj=Patient.objects.get(id=pat_id)
        patient_assignment_obj=Patient_Assignments.objects.get(patient=obj)
        patient_assignment_obj.remaining_time=new_time
        patient_assignment_obj.chosen_time = new_time
        patient_assignment_obj.save()
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
def start_timer(request):
    print("ENTERED START TIMER")
    if request.method == "POST":
        print("ENTERED START TIMER POST")
        data = json.loads(request.body)
        patient_id = data.get('patId', None)
        print("ENTERED START TIMER PATIENT ID",patient_id)
        try:
            patient = Patient.objects.get(id=patient_id)
            patient.timer_active = True
            patient.save()
            print("Successfully changed")
            return JsonResponse({'status': 'started'})
        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=404)
    else:
        return JsonResponse({
            "error": "Method not allowed"
        }, status=405)

@csrf_exempt
def fulltimer(request):
    obj = Patient.objects.all()
    for patient in obj:
        ass = Patient_Assignments.objects.get(patient=patient)
        seconds = ass.total_second
        minutes = ass.total_minute
        seconds += 1
        if seconds >= 60:
            seconds = 0
            minutes += 1
        ass.total_second = seconds
        ass.total_minute = minutes
        ass.save()
    return JsonResponse({'status': 'Updating'})

import time
@csrf_exempt
def update_timer(request):
    patients = Patient.objects.all().filter(timer_active=True)
    print("PATIENTS",patients)
    for patient in patients:
        try:
            patient_assignment_obj = Patient_Assignments.objects.get(patient=patient)
            total_seconds = patient_assignment_obj.total_second + 1
            if total_seconds == 60:
                total_minutes = patient_assignment_obj.total_minute + 1
                patient_assignment_obj.total_minute = total_minutes
                patient_assignment_obj.total_second = 0
            else:
                patient_assignment_obj.total_second = total_seconds
            if patient.timer_active:
                if patient_assignment_obj.remaining_second == 0:
                    patient_assignment_obj.remaining_minutes -= 1
                    patient_assignment_obj.remaining_second = 59  # Corrected for countdown
                else:
                    patient_assignment_obj.remaining_second -= 1
            patient_assignment_obj.save()
        except Patient_Assignments.DoesNotExist:
            continue
    return JsonResponse({'status': 'Updating'})


@csrf_exempt
@api_view(['POST'])
def pause_timer(request):
    if request.method == "POST":
        data = json.loads(request.body)
        patient_id = data.get('patId', None)
        try:
            patient = Patient.objects.get(id=patient_id)
            patient.timer_active = False
            patient.save()
            return JsonResponse({'status': 'started'})
        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=404)
    else:
        return JsonResponse({
            "error": "Method not allowed"
        }, status=405)

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
        patient_assignment_obj = Patient_Assignments.objects.get(patient=patient)
        patient_assignment_obj.remaining_minutes=time
        patient_assignment_obj.remaining_second=60
        patient_assignment_obj.progress_bar=100
        patient_assignment_obj.save()
        return JsonResponse({'status':'Success'})
    else:
        return JsonResponse({'status': 'Failure'})

def removeallassigned():
    obj=Department.objects.all()
    for i in obj:
        i.is_assigned=False
        i.save()

def removeallwaiting():
    obj=Department.objects.all()
    for i in obj:
        i.is_waiting=False
        i.save()

