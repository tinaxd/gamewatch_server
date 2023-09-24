from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.Screenshot)
admin.site.register(models.OW2UniqueUser)
admin.site.register(models.OW2UserImage)
