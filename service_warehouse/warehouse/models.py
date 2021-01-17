from django.db import models


# Create your models here.
class Items(models.Model):
    available_count = models.IntegerField()
    model = models.CharField(max_length=255)
    size = models.CharField(max_length=255)


class OrderItem(models.Model):
    canceled = models.BooleanField()
    order_item_uid = models.UUIDField(unique=True)
    order_uid = models.UUIDField()
    item_id = models.IntegerField()
