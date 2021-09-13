from django.db import models

# Create your models here.
class CrudUser(models.Model):
    name = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=100, blank=True)
    age = models.IntegerField(blank=True, null=True)
    lat = models.DecimalField( max_digits = 10, decimal_places = 4,blank=True, null=True)
    lng = models.DecimalField(max_digits = 10, decimal_places = 4,blank=True, null=True)
    
    def __str__(self):
        return self.name