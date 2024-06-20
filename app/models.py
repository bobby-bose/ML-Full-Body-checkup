from django.db import models

class Oncurepackages(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CoordinationFacilitators(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100)
    oncurepackage = models.ForeignKey(Oncurepackages, related_name='departments', on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.name} ({self.oncurepackage.name})"
class Meals(models.Model):
    name= models.CharField(max_length=255)

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
    chosen_time = models.IntegerField(null=True, blank=True)
    remaining_time = models.IntegerField(null=True, blank=True)
    timer_active = models.BooleanField(default=False)
    def __str__(self):
        return self.name


class EnteredDepartment(models.Model):
    registration = models.ForeignKey(Patient, related_name='entered_departments', on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    entered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.registration.name} entered {self.department.name} on {self.entered_at}"



