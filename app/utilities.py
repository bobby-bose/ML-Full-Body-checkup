from .models import *
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse

def for_add(package):
    all_departments = Department.objects.all().filter(oncurepackage=package)
    all_assigned = get_all_busy_departments()
    all_tobe_assigned = get_all_waiting_departments()
    all_waiting=Waiting_Departments.objects.all()
    all_assigned = list(all_assigned)
    all_tobe_assigned = list(all_tobe_assigned)
    all_waiting = list(all_waiting)
    not_free=all_assigned+all_waiting+all_tobe_assigned
    free=list(all_departments)
    available_departments = [item for item in free if item not in not_free]
    waiting_delete=Waiting_Departments.objects.all().filter(department=available_departments[0])
    if waiting_delete:
        waiting_delete.delete()
    return available_departments

def for_update(patient,package):
    final=[]
    # get all the free departments
    unentered_departments = Unentered_Departments.objects.filter(patient=patient)
    departments = [ud.department for ud in unentered_departments]
    # make sure In free departments NO OCCUPIED DEPARTMENTS
    occupied=all_occupied()
    final=[dep for dep in departments if dep not in occupied]
    return final

@csrf_exempt
def update_next_department(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            patient_id = data.get('patId')
            package_id = data.get('cho_pak')
            patient_object=Patient.objects.get(id=patient_id)
            package_object=Oncurepackages.objects.get(id=package_id)
            patient_assigned_object=Patient_Assignments.objects.get(patient=patient_object)
            finished_object = Department.objects.get(name="FINISHED")
            waiting_object = Department.objects.get(name="waiting")
            total_departments_count = Department.objects.all().filter(oncurepackage=package_object).count()
            total_department_patient_entered_count = Entered_Departments.objects.all().filter(
                patient=patient_object).count()
            departments = for_update(patient_object, package_object)
            if total_departments_count>total_department_patient_entered_count:
                if len(departments):
                    patient_assigned_object.assigned=patient_assigned_object.waiting
                    patient_assigned_object.waiting=departments[0]
                    patient_assigned_object.save()
                    Entered_Departments.objects.create(patient=patient_object, department=departments[0])
                    Unentered_Departments.objects.get(patient=patient_object, department=departments[0]).delete()
                    return JsonResponse({'success': True, 'message': 'Success'})
                else:
                    if patient_assigned_object.waiting==waiting_object:
                        return JsonResponse({'success': False, 'next_department': 'WAITING'})
                    patient_assigned_object.assigned = patient_assigned_object.waiting
                    patient_assigned_object.waiting = waiting_object
                    patient_assigned_object.save()
                    return JsonResponse({'success': True, 'message': 'Success'})
            if total_departments_count==total_department_patient_entered_count:
                return JsonResponse({'success': False, 'next_department': 'FINISHED'})
            # if patient_assigned_object.waiting.name=="waiting":
            #     return JsonResponse({'success': False, 'next_department': 'WAITING'})
            # if total_departments_count == total_department_patient_entered_count:
            #     return JsonResponse({'success': False, 'next_department': 'FINISHED'})
            # else:
            #     remaining_departments = []
            #     patient_entered = Entered_Departments.objects.all().filter(patient=patient_object)
            #     entered_depart = []
            #     for i in patient_entered:
            #         entered_depart.append(i.department)
            #     total_departments = Department.objects.all().filter(oncurepackage=package_object)
            #     for i in total_departments:
            #         if i not in entered_depart:
            #             remaining_departments.append(i)
            # earlier_assigned_department=patient_assigned_object.assigned
            # earlier_waiting_department = patient_assigned_object.waiting
            # patient_assigned_object.assigned=earlier_waiting_department
            # departments=for_update(patient_object,package_object)
            # if len(departments):
            #     pass
            # else:
            #     waiting_obj=Department.objects.get(name="FINISHED")
            #     patient_assigned_object.waiting=waiting_obj
            #     patient_assigned_object.save()
            #     return JsonResponse({'success': False, 'message': 'Invalid request method'})
            # patient_assigned_object.waiting=departments[0]
            # Entered_Departments.objects.create(patient=patient_object, department=departments[0])
            # patient_assigned_object.save()
            # Unentered_Departments.objects.get(patient=patient_object, department=departments[0]).delete()
        except Exception as e:
            print("The Exception is ",e)
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def add_patient(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            chosen_package_id = data.get('chosen_package')
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
            departments = for_add(chosen_package)
            print("#################",departments)
            patient_assignments=Patient_Assignments(
                patient=patient,
                assigned=departments[0],
                waiting=departments[1],
                chosen_time=departments[0].time,
            remaining_time=departments[0].time
            )
            patient_assignments.save()
            Entered_Departments.objects.create(patient=patient,department=departments[0])
            Entered_Departments.objects.create(patient=patient, department=departments[1])
            Entered_and_Unentered(patient, chosen_package)
            get_all_busy_departments()
            get_all_waiting_departments()
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



