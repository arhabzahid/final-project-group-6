from django.db import models
#django has built in authentication framework: user
#contains id, username, pw, email, first & last name
from django.contrib.auth.models import User

#models.CharField -> VARCHAR
#models.DateTimeField -> DATETIME col
#models.ForeignKey -> keys

# Create Patient database table
class Patient(models.Model):
    #each pt has 1 user account
    # on_delete = models.CASCADE -> if user is deleted so is patient
    user = models.OneToOneField(User, on_delete = models.CASCADE)

    patient_phone_number = models.CharField(max_length=20, blank = True)

    #VARCHAR(100) ins provider:
    insurance_provider = models.CharField(max_length=100, blank = True)

    #VARCHAR(100) ins number:
    insurance_number = models.CharField(max_length = 100, blank = True)

    #PMH: VARCHAR(300)
    pmh = models.CharField(max_length = 300, blank = True)

    #RX: VARCHAR(300)
    medications = models.CharField(max_length = 300, blank = True)

    #emergency contact name: VARCHAR (200)
    emergency_contact_name = models.CharField(max_length = 200, blank = True)

    #emergency contact num: VARCHAR (20)   
    emergency_contact_num = models.CharField(max_length = 20, blank = True)

    #return first & last name of pt object
    def __str__(self):
        return self.user.get_full_name()

class Provider(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    specialty = models.CharField(max_length = 150, blank = True)
    department = models.CharField(max_length = 150, blank = True)
    provider_phone_number = models.CharField(max_length=20, blank = True)
    def __str__(self):
        return self.user.get_full_name()

