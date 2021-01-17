from django.db import models


# Create your models here.
class Warranty(models.Model):
    comment = models.CharField(max_length=1024)
    item_uid = models.UUIDField(unique=True)
    status = models.CharField(max_length=255)
    warranty_date = models.DateTimeField()
