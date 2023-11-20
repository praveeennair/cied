from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

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
