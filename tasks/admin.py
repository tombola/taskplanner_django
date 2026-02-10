from django.contrib import admin

from .models import BiennialCropTask, CropTask


@admin.register(CropTask)
class CropTaskAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'sku', 'variety_name', 'bed', 'todoist_id', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['template', 'todoist_id', 'sku', 'variety_name', 'bed', 'created_at']

    def has_add_permission(self, request):
        return False


@admin.register(BiennialCropTask)
class BiennialCropTaskAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'sku', 'variety_name', 'bed', 'bed_second_year', 'todoist_id', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['template', 'todoist_id', 'sku', 'variety_name', 'bed', 'bed_second_year', 'created_at']

    def has_add_permission(self, request):
        return False
