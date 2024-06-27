from .models import *
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
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

def for_update(package):
    all_departments = Department.objects.all().filter(oncurepackage=package)
    all_assigned = get_all_busy_departments()
    all_tobe_assigned = get_all_waiting_departments()
    all_waiting = Waiting_Departments.objects.all()
    all_assigned = list(all_assigned)
    all_tobe_assigned = list(all_tobe_assigned)
    all_waiting = list(all_waiting)
    not_free = all_assigned + all_waiting + all_tobe_assigned
    free = list(all_departments)
    available_departments = [item for item in free if item not in not_free]
    return available_departments

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
            if patient_assigned_object.waiting==finished_object:
                print("TTTTTTTTTTTTTTTTTTTTTTTT")
                print("TTTTTTTTTTTTTTTTTTTTTTTT")
                print("TTTTTTTTTTTTTTTTTTTTTTTT")
                print("TTTTTTTTTTTTTTTTTTTTTTTT")
                print("TTTTTTTTTTTTTTTTTTTTTTTT")
                print("TTTTTTTTTTTTTTTTTTTTTTTT")
                print("TTTTTTTTTTTTTTTTTTTTTTTT")
                return JsonResponse({'success': False, 'next_department': 'FINISHED'})
            earlier_assigned_department=patient_assigned_object.assigned
            earlier_waiting_department = patient_assigned_object.waiting
            patient_assigned_object.assigned=earlier_waiting_department
            departments=for_update(package_object)
            patient_assigned_object.waiting=departments[0]
            patient_assigned_object.save()
            Waiting_Departments.objects.create(department=earlier_assigned_department)



            #
            #
            #
            # # Changes start
            # # assign waiting to assigned
            # print("assign waiting to assigned")
            # patient_assigned_object.assigned=patient_assigned_object.waiting
            # # add waiting to entered
            # print("add waiting to entered")
            # Entered_Departments.objects.create(patient=patient_object, department=patient_assigned_object.waiting)
            # # add waiting to occupied
            # print("add waiting to occupied")
            # # Occupied_Departments.objects.create(department=patient_assigned_object.waiting)
            # # add earlier assigned to Waiting_departments model
            # print("add earlier assigned to Waiting_departments model")
            # Waiting_Departments.objects.create(department=earlier_assigned_department)
            # # Take earlier assigned from Occupied-departments and delete it
            # print("Take earlier assigned from Occupied-departments and delete it")
            # Occupied_Departments.objects.get(department=earlier_assigned_department).delete()
            # all_departments = Department.objects.all().filter(oncurepackage=package_object)
            # all_occupied = Occupied_Departments.objects.all()
            # print("CHECK 1")
            # all_waiting = Waiting_Departments.objects.all()
            # occupied_departments = [occupied.department for occupied in all_occupied]
            # waiting_departments = [waiting.department for waiting in all_waiting]
            # combined_departments = occupied_departments + waiting_departments
            # combined_departments = list(set(combined_departments))
            # print("combined_department",combined_departments)
            # departments_to_remove = []
            # for department in all_departments:
            #     if department in combined_departments:
            #         departments_to_remove.append(department)
            # remaining_departments = [department for department in all_departments if
            #                          department not in departments_to_remove]
            # print("remaining_departments",remaining_departments)
            # if len(remaining_departments):
            #     print("yes remaining_departments")
            #     patient_assigned_object.waiting=remaining_departments[0]
            #     patient_assigned_object.save()
            #     Occupied_Departments.objects.create(department=remaining_departments[0])
            # else:
            #     print("no remaining_departments")
            #     patient_assigned_object.waiting = finished_object
            #     patient_assigned_object.save()
            #     Occupied_Departments.objects.create(department=finished_object)

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
                waiting=departments[1]
            )
            patient_assignments.save()
            Entered_Departments.objects.create(patient=patient,department=departments[0])
            Entered_Departments.objects.create(patient=patient, department=departments[1])
            Entered_and_Unentered(patient, chosen_package)
            get_all_busy_departments()
            get_all_waiting_departments()
            # Occupied_Departments.objects.create(department=departments[0])
            # Occupied_Departments.objects.create(department=departments[1])
            return JsonResponse({'message': 'Patient added successfully!'}, status=201)
        except Exception as e:
            print("THE ERRRR",e)
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def Entered_and_Unentered(patient,chosen_package):
    entered_department_ids = Entered_Departments.objects.filter(patient=patient).values_list('department_id', flat=True)
    # Get all department IDs
    all_department_ids = Department.objects.filter(oncurepackage=chosen_package).values_list('id', flat=True)
    # Find department IDs not entered by the patient
    print("all_department_ids",all_department_ids)
    print("entered_department_ids",entered_department_ids)
    unentered_department_ids = set(all_department_ids) - set(entered_department_ids)
    # Add the unentered departments to unentered_obj for the patient
    Unentered_Departments.objects.all().filter(patient=patient).delete()
    for department_id in unentered_department_ids:
        Unentered_Departments.objects.create(patient=patient, department_id=department_id)


def get_all_busy_departments():
    obj=Patient_Assignments.objects.all()
    busy=[]
    for i in obj:
        busy.append(i.assigned)
    print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",busy)
    return busy

def get_all_waiting_departments():
    obj=Patient_Assignments.objects.all()
    waiting=[]
    for i in obj:
        waiting.append(i.waiting)
    print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB", waiting)
    return waiting


