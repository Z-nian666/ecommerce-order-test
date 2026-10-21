'''from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.CharField(max_length=11, null=True, blank=True, verbose_name="手机号")

    class Meta:
        db_table = "user"
        verbose_name = "用户"
'''