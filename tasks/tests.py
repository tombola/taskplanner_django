import pytest

from todosync.forms import BaseTaskGroupCreationForm
from todosync.models import BaseTaskGroupTemplate, TaskSyncSettings

from .models import BiennialCropTask, CropTask, CropTaskGroupTemplate


@pytest.fixture
def sync_settings(db):
    """Create TaskSyncSettings singleton for testing"""
    return TaskSyncSettings.load()


@pytest.fixture
def task_group_template(db, sync_settings):
    """Create a CropTaskGroupTemplate for testing"""
    return CropTaskGroupTemplate.objects.create(
        title="Test Chilli Template",
        description="",
        tasks=[
            {"title": "Sow {sku}", "labels": "sow, planting", "subtasks": []},
            {
                "title": "Harvest {variety_name}",
                "labels": "harvest",
                "subtasks": [{"title": "{sku} checked in", "labels": "processing"}],
            },
        ],
    )


@pytest.fixture
def empty_template(db, sync_settings):
    """Create a BaseTaskGroupTemplate with no parent_task_class"""
    return BaseTaskGroupTemplate.objects.create(
        title="Empty Template",
        description="",
        tasks=[],
    )


@pytest.mark.django_db
class TestCropTaskModel:
    """Tests for CropTask model"""

    def test_get_token_field_names(self):
        assert CropTask.get_token_field_names() == ["crop", "sku", "variety_name", "bed"]

    def test_get_token_values(self):
        task = CropTask(crop="Chilli", sku="CH001", variety_name="Habanero", bed="A1")
        assert task.get_token_values() == {
            "crop": "Chilli",
            "sku": "CH001",
            "variety_name": "Habanero",
            "bed": "A1",
        }

    def test_get_parent_task_title(self):
        task = CropTask(variety_name="Habanero")
        assert task.get_parent_task_title() == "Plant Habanero"

    def test_get_description(self):
        task = CropTask(crop="Chilli", sku="CH001", variety_name="Habanero", bed="A1")
        assert task.get_description() == "Crop: Chilli\nVariety: Habanero\nSKU: CH001\nBed: A1"


@pytest.mark.django_db
class TestBiennialCropTaskModel:
    """Tests for BiennialCropTask model"""

    def test_get_token_field_names(self):
        assert BiennialCropTask.get_token_field_names() == ["sku", "variety_name", "bed", "bed_second_year"]

    def test_get_token_values(self):
        task = BiennialCropTask(sku="PA001", variety_name="Parsley", bed="B2", bed_second_year="C3")
        assert task.get_token_values() == {
            "sku": "PA001",
            "variety_name": "Parsley",
            "bed": "B2",
            "bed_second_year": "C3",
        }


@pytest.mark.django_db
class TestBaseTaskGroupTemplate:
    """Tests for BaseTaskGroupTemplate model methods"""

    def test_get_parent_task_model(self, task_group_template):
        assert task_group_template.get_parent_task_model() is CropTask

    def test_get_parent_task_model_none(self, empty_template):
        assert empty_template.get_parent_task_model() is None

    def test_get_token_field_names(self, task_group_template):
        assert task_group_template.get_token_field_names() == ["crop", "sku", "variety_name", "bed"]

    def test_get_token_field_names_no_parent_task_class(self, empty_template):
        assert empty_template.get_token_field_names() == []

    def test_get_effective_project_id_from_template(self, task_group_template):
        task_group_template.project_id = "12345"
        assert task_group_template.get_effective_project_id() == "12345"

    def test_get_effective_project_id_fallback_to_settings(self, task_group_template, sync_settings):
        task_group_template.project_id = ""
        sync_settings.default_project_id = "99999"
        sync_settings.save()
        assert task_group_template.get_effective_project_id() == "99999"

    def test_get_effective_project_id_empty(self, task_group_template):
        task_group_template.project_id = ""
        assert task_group_template.get_effective_project_id() == ""


@pytest.mark.django_db
class TestTaskGroupCreationForm:
    """Tests for BaseTaskGroupCreationForm"""

    def test_form_init_without_template_id(self):
        form = BaseTaskGroupCreationForm()
        assert "task_group_template" in form.fields
        assert "description" in form.fields
        assert len(form.fields) == 2

    def test_form_init_with_template_id(self, task_group_template):
        form = BaseTaskGroupCreationForm(template_id=task_group_template.id)
        assert "task_group_template" in form.fields
        assert "description" in form.fields
        assert "token_crop" in form.fields
        assert "token_sku" in form.fields
        assert "token_variety_name" in form.fields
        assert "token_bed" in form.fields
        assert len(form.fields) == 6

    def test_dynamic_field_labels(self, task_group_template):
        form = BaseTaskGroupCreationForm(template_id=task_group_template.id)
        assert form.fields["token_crop"].label == "Crop"
        assert form.fields["token_sku"].label == "Sku"
        assert form.fields["token_variety_name"].label == "Variety Name"
        assert form.fields["token_bed"].label == "Bed"

    def test_dynamic_field_required(self, task_group_template):
        """sku and variety_name are required (blank=False), crop and bed are optional (blank=True)"""
        form = BaseTaskGroupCreationForm(template_id=task_group_template.id)
        assert form.fields["token_crop"].required is False
        assert form.fields["token_sku"].required is True
        assert form.fields["token_variety_name"].required is True
        assert form.fields["token_bed"].required is False

    def test_form_with_invalid_template_id(self):
        form = BaseTaskGroupCreationForm(template_id=99999)
        assert len(form.fields) == 2

    def test_form_with_no_parent_task_class(self, empty_template):
        form = BaseTaskGroupCreationForm(template_id=empty_template.id)
        assert len(form.fields) == 2

    def test_form_validation_success(self, task_group_template):
        form = BaseTaskGroupCreationForm(
            data={
                "task_group_template": task_group_template.id,
                "token_crop": "Chilli",
                "token_sku": "CH001",
                "token_variety_name": "Habanero",
                "token_bed": "A1",
            },
            template_id=task_group_template.id,
        )
        assert form.is_valid()

    def test_form_validation_missing_required_token(self, task_group_template):
        form = BaseTaskGroupCreationForm(
            data={
                "task_group_template": task_group_template.id,
                "token_sku": "CH001",
                # missing token_variety_name (required)
            },
            template_id=task_group_template.id,
        )
        assert not form.is_valid()
        assert "token_variety_name" in form.errors

    def test_form_validation_optional_field_omitted(self, task_group_template):
        """bed is optional so form should be valid without it"""
        form = BaseTaskGroupCreationForm(
            data={
                "task_group_template": task_group_template.id,
                "token_sku": "CH001",
                "token_variety_name": "Habanero",
            },
            template_id=task_group_template.id,
        )
        assert form.is_valid()

    def test_get_token_values(self, task_group_template):
        form = BaseTaskGroupCreationForm(
            data={
                "task_group_template": task_group_template.id,
                "token_crop": "Chilli",
                "token_sku": "CH001",
                "token_variety_name": "Habanero",
                "token_bed": "A1",
            },
            template_id=task_group_template.id,
        )
        assert form.is_valid()
        assert form.get_token_values() == {
            "crop": "Chilli",
            "sku": "CH001",
            "variety_name": "Habanero",
            "bed": "A1",
        }

    def test_get_token_values_empty(self):
        form = BaseTaskGroupCreationForm()
        assert form.get_token_values() == {}

    def test_queryset_includes_all_templates(self, task_group_template):
        form = BaseTaskGroupCreationForm()
        queryset = form.fields["task_group_template"].queryset
        assert task_group_template in queryset

    def test_template_field_populated_with_template_id(self, task_group_template):
        form = BaseTaskGroupCreationForm(template_id=task_group_template.id)
        assert form.fields["task_group_template"].initial == task_group_template
