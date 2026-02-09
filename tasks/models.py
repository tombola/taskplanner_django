from django.db import models
from todosync.models import BaseTaskGroupTemplate
from wagtail.admin.panels import FieldPanel


class CropTaskTemplate(BaseTaskGroupTemplate):
    """Crop-specific task template with bed location"""

    bed = models.CharField(
        max_length=100,
        blank=True,
        help_text="Bed location for this crop"
    )

    content_panels = BaseTaskGroupTemplate.content_panels + [
        FieldPanel('bed'),
    ]

    class Meta:
        verbose_name = 'Crop Task Template'
        verbose_name_plural = 'Crop Task Templates'


class BiennialCropTaskTemplate(CropTaskTemplate):
    """Biennial crop template - extends CropTaskTemplate with second-year bed"""

    bed_second_year = models.CharField(
        max_length=100,
        blank=True,
        help_text="Bed location for second year growth"
    )

    content_panels = CropTaskTemplate.content_panels + [
        FieldPanel('bed_second_year'),
    ]

    class Meta:
        verbose_name = 'Biennial Crop Task Template'
        verbose_name_plural = 'Biennial Crop Task Templates'
