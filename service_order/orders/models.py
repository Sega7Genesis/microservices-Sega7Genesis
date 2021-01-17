from django.db import models


# Create your models here.
class Order(models.Model):
    item_uid = models.UUIDField()
    order_date = models.DateTimeField()
    order_uid = models.UUIDField(unique=True)
    status = models.CharField(max_length=255)
    user_uid = models.UUIDField()
