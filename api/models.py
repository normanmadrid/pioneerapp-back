from django.db import models

# Create your models here.
class Message(models.Model):
    description = models.TextField()

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    cuisine = models.CharField(max_length=50)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    price = models.PositiveSmallIntegerField
    operating_hours = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"