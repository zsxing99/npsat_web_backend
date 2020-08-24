from django.contrib import admin

# Register your models here.

from . import models

admin.site.register(models.Region)
admin.site.register(models.Crop)
admin.site.register(models.CropGroup)
admin.site.register(models.MantisServer)


class ModelRunModificationInline(admin.TabularInline):
    model = models.Modification


class ModelRunAdmin(admin.ModelAdmin):
    inlines = [ModelRunModificationInline]


admin.site.register(models.ModelRun, ModelRunAdmin)
admin.site.register(models.Modification)