from django.contrib import admin

# Register your models here.

from .models import County, Crop, CropGroup

admin.site.register(County)
admin.site.register(Crop)
admin.site.register(CropGroup)