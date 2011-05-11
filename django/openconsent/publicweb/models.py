from django.db import models
import tinymce.models
import tinymce.widgets

# Create your models here.
class Decision(models.Model):
    short_name = models.CharField(max_length=255)
    decided_date = models.DateField(null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    review_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    budget = models.TextField(blank=True)
    people = models.TextField(blank=True)
    description = tinymce.models.HTMLField(blank=True)
    concerns = models.TextField(blank=True)