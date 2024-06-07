from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField(default=10)
    current_patients = models.IntegerField(default=0)
    status=models.CharField(max_length=255,default="Free")

    def __str__(self):
        return self.name

class Registration(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    mobile_number = models.CharField(max_length=15)
    address = models.TextField()
    coord_facilitator = models.CharField(max_length=255)
    meals = models.CharField(max_length=255)
    assigned_department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    status=models.CharField(max_length=255,null=True,blank=True)
    current_department=models.CharField(max_length=255,null=True,blank=True)


    def __str__(self):
        return self.name










