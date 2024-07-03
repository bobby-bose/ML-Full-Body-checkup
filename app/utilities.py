from .models import *
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse

from .update_department import get_free_department



def get_all_free_departments(package):
    obj=Patient_Assignments.objects.all()
    not_free=[]
    free=[]
    for i in obj:
        not_free.append(i.assigned)
        not_free.append(i.waiting)
    all=Department.objects.all().filter(oncurepackage=package)
    for i in all:
        if i not in not_free:
            free.append(i)
    return free

def get_first_not_null_waiting():
    obj = Patient_Assignments.objects.all()
    waiting_obj = Department.objects.get(name='waiting')
    free=[]
    for i in obj:
        if i.waiting != waiting_obj:
            free.append({'id':i.id,'waiting':i.waiting})
    return free

def get_waiting_department_id_based_on_time():
    obj=Patient_Assignments.objects.all()
    result=[]
    min_id=None
    for i in obj:
        check = check_if_department_based_on_time_already_exist(i.assigned)
        if check:
            print("YESSSSSSSSSSSSSSS",i.assigned,"already exists in the List")
            pass
        else:
            minutes = i.remaining_minutes
            seconds = i.remaining_second
            total_seconds = (minutes * 60) + seconds
            result.append({'id': i.id, 'total_seconds': total_seconds})
    min_entry = min(result, key=lambda x: x['total_seconds'])
    min_id = min_entry['id']
    return min_id

def check_if_department_based_on_time_already_exist(dept):
    obj=Patient_Assignments.objects.filter(is_waiting=True)
    obj_list =list(obj)
    assigned_values = [assignment.assigned for assignment in obj_list]
    print("11111111111111111111111111111111",assigned_values)
    print("333333333333333333333333333333333",dept)
    if dept in assigned_values:
        return True
    else:
        return False


def free_department_based_on_time_for_update(patient):
    result=[]
    all_departments=Department.objects.all()
    for i in all_departments:
        check=check_if_patient_has_already_entered_that_department(patient,i)
        if check:
            pass
        else:
            result.append({"id":i.id,"remaining_time":i.remaining_minutes})
    min_item = min(result, key=lambda x: x["remaining_time"])
    min_id = min_item["id"]
    free_department=Department.objects.get(id=min_id)
    return free_department




def check_if_patient_has_already_entered_that_department(patient,department):
    entered_departments = []
    all_entered = Entered_Departments.objects.all().filter(patient=patient)
    for i in all_entered:
        entered_departments.append(i.department)
    if department in entered_departments:
        return True
    else:
        return False






@csrf_exempt
def update_next_department(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            patient_id = data.get('patId')
            package_id = data.get('cho_pak')
            patient_object = Patient.objects.get(id=patient_id)
            package_object = Oncurepackages.objects.get(id=package_id)
            patient_assigned_object = Patient_Assignments.objects.get(patient=patient_object)
            finished_object = Department.objects.get(name="FINISHED")
            waiting_object = Department.objects.get(name="waiting")
            total_entered_count = Entered_Departments.objects.all().filter(patient=patient_object).count()
            total_departments_count = Department.objects.all().filter(oncurepackage=package_object).count()
            if total_departments_count == total_entered_count:
                return JsonResponse({'success': True, 'next_department': 'FINISHED'})
            if patient_assigned_object.waiting == waiting_object:
                    just_checking=get_free_department(package_object, patient_object)
                    if just_checking==waiting_object:
                        return JsonResponse({'success': True, 'next_department': 'WAITING'})
                    patient_assigned_object.assigned=just_checking
                    patient_assigned_object.chosen_time=just_checking.remaining_minutes
                    patient_assigned_object.remaining_minutes=just_checking.remaining_minutes
                    patient_assigned_object.assigned=just_checking
                    Entered_Departments.objects.create(patient=patient_object,department=just_checking)
                    patient_assigned_object.save()
            else:
                Waiting_Departments.objects.create(department=patient_assigned_object.assigned)
                patient_assigned_object.assigned = patient_assigned_object.waiting
                patient_assigned_object.chosen_time = patient_assigned_object.waiting.remaining_minutes
                patient_assigned_object.remaining_minutes = patient_assigned_object.waiting.remaining_minutes
                Entered_Departments.objects.create(patient=patient_object, department=patient_assigned_object.assigned)
                next_department = get_free_department(package_object, patient_object)
                if next_department is None:
                    print("The next department is None, setting to waiting_object")
                    next_department = waiting_object
                patient_assigned_object.waiting = next_department
                patient_assigned_object.chosen_time = next_department.remaining_minutes
                patient_assigned_object.save()
                return JsonResponse({'success': True, 'next_department': 'SUCCESS'})
        except Exception as e:
            print("The Exception is ", e)
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def add_patient(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            chosen_package_id = data.get('chosen_package')
            waiting_obj=Department.objects.get(name='waiting')
            if not chosen_package_id:
                return JsonResponse({'error': 'Missing chosen_package field'}, status=400)
            try:
                chosen_package = Oncurepackages.objects.get(id=chosen_package_id)
            except Oncurepackages.DoesNotExist:
                return JsonResponse({'error': 'Chosen package not found'}, status=404)
            required_fields = ['name', 'age', 'contact_number', 'address', 'chosen_package']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
            patient = Patient(
                name=data.get('name'),
                age=data.get('age'),
                mobile_number=data.get('contact_number'),
                address=data.get('address'),
                coord_facilitator_id=data.get('coord_facilitator', ''),  # Default to empty string if not provided
                meals_id=data.get('meals', ''),  # Default to empty string if not provided
                chosen_package=chosen_package,  # Correctly assign the chosen package
            )
            patient.save()
            departments = get_all_free_departments(chosen_package)
            one=None
            two=None
            if len(departments)==0:
                bobby=get_first_not_null_waiting()
                if len(bobby)==0:
                    id=get_waiting_department_id_based_on_time()
                    obj=Patient_Assignments.objects.get(id=id)
                    current=obj.assigned
                    one=current
                    patient_assignments = Patient_Assignments(
                        patient=patient,
                        assigned=one,
                        waiting=waiting_obj,
                        chosen_time=one.remaining_minutes,
                        remaining_minutes=one.remaining_minutes,
                        remaining_second=one.remaining_seconds,
                        is_waiting=True
                    )
                    patient_assignments.save()
                    return JsonResponse({'message': 'Patient added successfully!'}, status=201)
                else:
                    one = get_first_not_null_waiting()[0]["waiting"]
                    id = get_first_not_null_waiting()[0]["id"]
                    obj = Patient_Assignments.objects.get(id=id)
                    obj.waiting = waiting_obj
                    obj.save()
                two=waiting_obj
            elif len(departments) == 1:
                one=departments[0]
                two=waiting_obj
            else:
                one=departments[0]
                two=departments[1]
            patient_assignments=Patient_Assignments(
                patient=patient,
                assigned=one,
                waiting=two,
                chosen_time=one.remaining_minutes,
            remaining_minutes=one.remaining_minutes,
                remaining_second=one.remaining_seconds
            )
            patient_assignments.save()
            Occupied_Departments.objects.create(department=one)
            Entered_Departments.objects.create(patient=patient,department=one)
            return JsonResponse({'message': 'Patient added successfully!'}, status=201)
        except Exception as e:
            print("THE ERRRR",e)
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def Entered_and_Unentered(patient,chosen_package):
    entered_department_ids = Entered_Departments.objects.filter(patient=patient).values_list('department_id', flat=True)
    all_department_ids = Department.objects.filter(oncurepackage=chosen_package).values_list('id', flat=True)
    print("all_department_ids",all_department_ids)
    print("entered_department_ids",entered_department_ids)
    unentered_department_ids = set(all_department_ids) - set(entered_department_ids)
    Unentered_Departments.objects.all().filter(patient=patient).delete()
    for department_id in unentered_department_ids:
        Unentered_Departments.objects.create(patient=patient, department_id=department_id)


def get_all_busy_departments():
    obj=Patient_Assignments.objects.all()
    busy=[]
    for i in obj:
        busy.append(i.assigned)
    return busy

def get_all_waiting_departments():
    obj=Patient_Assignments.objects.all()
    waiting=[]
    for i in obj:
        waiting.append(i.waiting)
    return waiting

from django.shortcuts import render
def all_occupied_html(request):
    obj = Patient_Assignments.objects.all()
    busy = []
    waiting = []
    for i in obj:
        busy.append(i.assigned)
        waiting.append(i.waiting)
    full = busy + waiting
    context = {'full': full}
    return render(request, 'all_occupied.html', context)

def all_occupied():
    obj = Patient_Assignments.objects.all()
    busy = []
    waiting = []
    for i in obj:
        busy.append(i.assigned)
        waiting.append(i.waiting)
    full = busy + waiting
    return full

def department_list(request):
    obj=Oncurepackages.objects.get(name="Wellcure Complete Assessment")
    departments = Department.objects.all().filter(oncurepackage=obj)
    return render(request, 'new/dep.html', {'departments': departments})



