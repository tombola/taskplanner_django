from django.db import models

from todosync.models import BaseParentTask


class CropTask(BaseParentTask):
    """Parent task for crop-related task groups."""

    sku = models.CharField(
        max_length=100,
        help_text="Product SKU"
    )

    variety_name = models.CharField(
        max_length=200,
        help_text="Variety name"
    )

    bed = models.CharField(
        max_length=100,
        blank=True,
        help_text="Bed location for this crop"
    )

    class Meta:
        verbose_name = 'Crop Task'
        verbose_name_plural = 'Crop Tasks'

    @classmethod
    def get_token_field_names(cls):
        return ['sku', 'variety_name', 'bed']

    def get_parent_task_title(self):
        return f"Plant {self.variety_name}"

    def get_description(self):
        return f"SKU: {self.sku}, Bed: {self.bed}"


class BiennialCropTask(CropTask):
    """Parent task for biennial crop task groups."""

    bed_second_year = models.CharField(
        max_length=100,
        blank=True,
        help_text="Bed location for second year growth"
    )

    class Meta:
        verbose_name = 'Biennial Crop Task'
        verbose_name_plural = 'Biennial Crop Tasks'

    @classmethod
    def get_token_field_names(cls):
        return ['sku', 'variety_name', 'bed', 'bed_second_year']
