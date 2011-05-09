from django.db import models

# Create your models here.
class Decision(models.Model):
    short_name = models.CharField(max_length=255)
    decided_date = models.DateField(null=True)
    effective_date = models.DateField(null=True)
    review_date = models.DateField(null=True)
    expiry_date = models.DateField(null=True)
    budget = models.TextField()
    people = models.TextField()
    description = models.TextField()
    concerns = models.TextField()