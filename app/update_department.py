from .models import Department, Occupied_Departments, Entered_Departments,Waiting_Departments,Patient_Assignments
def get_free_department(package, patient):
    result = None
    waiting_object = Department.objects.get(name="waiting")
    print(f"Waiting Department: {waiting_object}")
    all = list(Department.objects.filter(oncurepackage=package).values_list('id', flat=True))
    print(f"All Departments in Package: {all}")
    waiting = list(Waiting_Departments.objects.values_list('department__id', flat=True))
    print(f"Departments in Waiting: {waiting}")
    patient_assignments_assigned = list(Patient_Assignments.objects.values_list('assigned__id', flat=True))
    patient_assignments_waiting = list(Patient_Assignments.objects.values_list('waiting__id', flat=True))
    print(f"Assigned Departments: {patient_assignments_assigned}")
    print(f"Waiting Departments: {patient_assignments_waiting}")
    busy = patient_assignments_assigned + patient_assignments_waiting
    print(f"(Assigned + Waiting)Busy Departments: {busy}")
    busy = set(busy)
    all = set(all)
    free = list(all.symmetric_difference(busy))
    print(f"Free Departments: {free}")
    for dept in waiting:
        if check_if_already_entered(patient, dept):
            print(f"This department ({dept}) is already entered, skipping it")
        else:
            result = Department.objects.get(id=dept)
            Waiting_Departments.objects.get(department=result).delete()
            break
    if not result:
        for dept in free:
            if check_if_already_entered(patient, dept):
                print(f"This department ({dept}) is already entered, skipping it")
            else:
                result = Department.objects.get(id=dept)
                break
    if not result:
        result = waiting_object
    print(f"THE RETURNED is {result}")
    return result

def check_if_already_entered(patient,result):
    entered = list(Entered_Departments.objects.all().filter(patient=patient).values_list('department__id', flat=True))
    if result in entered:
        print("This department is already entered,skipping it")
        return True
    else:
        return False



