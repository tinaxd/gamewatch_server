from django.contrib import admin

from . import models

# Register your models here.
admin.register(models.Screenshot)
admin.register(models.OW2UniqueUser)
admin.register(models.OW2UserImage)
