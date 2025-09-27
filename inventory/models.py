from django.db import models
from cloudinary.models import CloudinaryField

class Item(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100)
    expiry_date = models.DateField(null=True, blank=True)
    image = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return self.name

class Stock(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    custom_name = models.CharField(max_length=200, blank=True)
    quantity = models.IntegerField()
    out_quantity = models.IntegerField(default=0, blank=True)
    stock_in_date = models.DateField()
    stock_out_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.custom_name:
            return f"{self.custom_name} - {self.quantity}"
        return f"{self.item.name} - {self.quantity}"
