from django.db import models

from todosync.models import BaseParentTask, BaseTaskGroupTemplate


class CropTask(BaseParentTask):
    """Parent task for crop-related task groups."""

    crop = models.CharField(max_length=200, blank=True, help_text="Crop name (e.g., Tomato, Lettuce)")

    sku = models.CharField(max_length=100, help_text="Product SKU")

    variety_name = models.CharField(max_length=200, help_text="Variety name")

    bed = models.CharField(max_length=100, blank=True, help_text="Bed location for this crop")

    class Meta:
        verbose_name = "Crop Task"
        verbose_name_plural = "Crop Tasks"

    @classmethod
    def get_token_field_names(cls):
        return ["crop", "sku", "variety_name", "bed"]

    def get_parent_task_title(self):
        return f"Plant {self.variety_name}"

    def get_description(self):
        return f"Crop: {self.crop}\nVariety: {self.variety_name}\nSKU: {self.sku}\nBed: {self.bed}"


class CropTaskGroupTemplate(BaseTaskGroupTemplate):
    """Task group template for crop-related tasks."""

    parent_task_class = CropTask

    class Meta:
        verbose_name = "Crop Task Group Template"
        verbose_name_plural = "Crop Task Group Templates"


class BiennialCropTask(CropTask):
    """Parent task for biennial crop task groups."""

    bed_second_year = models.CharField(max_length=100, blank=True, help_text="Bed location for second year growth")

    class Meta:
        verbose_name = "Biennial Crop Task"
        verbose_name_plural = "Biennial Crop Tasks"

    @classmethod
    def get_token_field_names(cls):
        return ["sku", "variety_name", "bed", "bed_second_year"]
