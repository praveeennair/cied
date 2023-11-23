from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from core.constants import OrderStatus

class CustomQuerySet(models.query.QuerySet):
    def update(self, *args, **kwargs):
        if 'udate' not in kwargs and self.model._meta.get_field('udate'):
            kwargs['udate'] = timezone.localtime(timezone.now())
        return super().update(**kwargs)


class CIEDModelManager(models.Manager.from_queryset(CustomQuerySet)):
    pass


class TimeStampedModel(models.Model):
    class Meta(object):
        abstract = True

    cdate = models.DateTimeField(auto_now_add=True)
    udate = models.DateTimeField(auto_now=True)

    objects = CIEDModelManager()

    def save(self, *args, **kwargs):
        if kwargs and kwargs.get('update_fields'):
            if 'udate' not in kwargs['update_fields']:
                kwargs['update_fields'].append("udate")
        super(TimeStampedModel, self).save(*args, **kwargs)


class Product(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=False, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    # TODO:  Add added_by

    class Meta:
        db_table = 'products'


class DeliveryAgent(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_blocked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'delivery_agents'


class Customer(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_blocked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'customer'


class Order(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default=OrderStatus.PENDING)

    class Meta:
        db_table = 'orders'

class OTPRequests(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    otp_token = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = 'otp_request'

