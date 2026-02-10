from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import CropTask


class CropTaskViewSet(SnippetViewSet):
    model = CropTask
    icon = "list-ul"
    menu_label = "Crop Tasks"
    menu_order = 200
    add_to_admin_menu = True
    add_to_settings_menu = False
    list_display = ["variety_name", "sku", "bed", "todo_id", "completed", "todo_section_id", "created_at"]
    list_filter = ["variety_name", "bed", "created_at"]
    search_fields = ["sku", "variety_name", "bed"]
    inspect_view_enabled = True
    inspect_view_fields = [
        "sku",
        "variety_name",
        "bed",
        "todo_id",
        "template",
        "created_at",
    ]


register_snippet(CropTask, viewset=CropTaskViewSet)
