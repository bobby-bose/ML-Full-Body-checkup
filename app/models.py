from django.db import models

class CoordinationFacilitators(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Meals(models.Model):
    name= models.CharField(max_length=255)

    def __str__(self):
        return self.name
class Oncurepackages(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=100)
    oncurepackage = models.ForeignKey(Oncurepackages, related_name='departments', on_delete=models.CASCADE)
    time=models.IntegerField(null=True,blank=True)
    def __str__(self):
        return self.name

class Patient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    mobile_number = models.CharField(max_length=15)
    address = models.TextField()
    coord_facilitator = models.ForeignKey(CoordinationFacilitators, on_delete=models.CASCADE, null=True, blank=True)
    meals = models.ForeignKey(Meals, on_delete=models.CASCADE, null=True, blank=True)
    chosen_package = models.ForeignKey(Oncurepackages, on_delete=models.CASCADE, null=True, blank=True)
    assigned_department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)

    timer_active = models.BooleanField(default=False)
    waiting_department=models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True,related_name='waiting_package')
    def __str__(self):
        return self.name
class Occupied_Departments(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.department.name

class Patient_Assignments(models.Model):
    patient = models.ForeignKey(Patient, related_name='patient_assignments', on_delete=models.CASCADE)
    assigned = models.ForeignKey(Department, related_name='assigned_patient_assignments', on_delete=models.CASCADE)
    waiting = models.ForeignKey(Department, related_name='waiting_patient_assignments', on_delete=models.CASCADE)
    chosen_time = models.IntegerField(null=True, blank=True)
    remaining_time = models.IntegerField(null=True, blank=True)
    progress_bar = models.IntegerField(default=100)
    remaining_departments=models.TextField(null=True, blank=True)

    def __str__(self):
        return self.patient.name

class Waiting_Departments(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.department.name

class Entered_Departments(models.Model):
    patient = models.ForeignKey(Patient, related_name='entered_departments_patients', on_delete=models.CASCADE)
    department = models.ForeignKey(Department, related_name='entered_departments_department', on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.patient.name} - Entered: {self.department.name}"
    class Meta:
        ordering = ['patient', 'department']

class Unentered_Departments(models.Model):
    patient = models.ForeignKey(Patient, related_name='unentered_departments_patients', on_delete=models.CASCADE)
    department = models.ForeignKey(Department, related_name='unentered_departments_department', on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.patient.name} - Unentered: {self.department.name}"
    class Meta:
        ordering = ['patient', 'department']

