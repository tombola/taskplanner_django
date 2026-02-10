import pytest
from django.contrib.contenttypes.models import ContentType
from wagtail.models import Page, Site

from todosync.forms import BaseTaskGroupCreationForm
from todosync.models import BaseTaskGroupTemplate, TaskSyncSettings

from .models import BiennialCropTask, CropTask


@pytest.fixture
def wagtail_site(db):
    """Get or create a Wagtail site with root page"""
    root_page = Page.objects.get(id=1)
    site, created = Site.objects.get_or_create(
        hostname='localhost',
        defaults={
            'root_page': root_page,
            'is_default_site': True
        }
    )
    return site


@pytest.fixture
def sync_settings(db, wagtail_site):
    """Create TaskSyncSettings for testing"""
    settings, _ = TaskSyncSettings.objects.get_or_create(
        site=wagtail_site,
        defaults={'todoist_project_id': ''}
    )
    return settings


@pytest.fixture
def crop_task_ct(db):
    """Get ContentType for CropTask"""
    return ContentType.objects.get_for_model(CropTask)


@pytest.fixture
def biennial_ct(db):
    """Get ContentType for BiennialCropTask"""
    return ContentType.objects.get_for_model(BiennialCropTask)


@pytest.fixture
def task_group_template(db, wagtail_site, sync_settings, crop_task_ct):
    """Create a BaseTaskGroupTemplate with task_type=CropTask for testing"""
    root_page = Page.objects.get(id=1)

    template = BaseTaskGroupTemplate(
        title='Test Chilli Template',
        slug='test-chilli',
        description='',
        task_type=crop_task_ct,
        tasks=[
            {
                'type': 'task',
                'value': {
                    'title': 'Sow {sku}',
                    'labels': 'sow, planting',
                    'subtasks': []
                }
            },
            {
                'type': 'task',
                'value': {
                    'title': 'Harvest {variety_name}',
                    'labels': 'harvest',
                    'subtasks': [
                        {
                            'title': '{sku} checked in',
                            'labels': 'processing'
                        }
                    ]
                }
            }
        ],
        live=True
    )

    root_page.add_child(instance=template)
    template.save_revision().publish()

    return template


@pytest.fixture
def empty_template(db, wagtail_site, sync_settings):
    """Create a BaseTaskGroupTemplate with no task_type"""
    root_page = Page.objects.get(id=1)

    template = BaseTaskGroupTemplate(
        title='Empty Template',
        slug='empty-template',
        description='',
        tasks=[],
        live=True
    )

    root_page.add_child(instance=template)
    template.save_revision().publish()

    return template


@pytest.mark.django_db
class TestCropTaskModel:
    """Tests for CropTask model"""

    def test_get_token_field_names(self):
        assert CropTask.get_token_field_names() == ['sku', 'variety_name', 'bed']

    def test_get_token_values(self):
        task = CropTask(sku='CH001', variety_name='Habanero', bed='A1')
        assert task.get_token_values() == {
            'sku': 'CH001',
            'variety_name': 'Habanero',
            'bed': 'A1',
        }

    def test_get_parent_task_title(self):
        task = CropTask(variety_name='Habanero')
        assert task.get_parent_task_title() == 'Plant Habanero'

    def test_get_description(self):
        task = CropTask(sku='CH001', bed='A1')
        assert task.get_description() == 'SKU: CH001, Bed: A1'


@pytest.mark.django_db
class TestBiennialCropTaskModel:
    """Tests for BiennialCropTask model"""

    def test_get_token_field_names(self):
        assert BiennialCropTask.get_token_field_names() == [
            'sku', 'variety_name', 'bed', 'bed_second_year'
        ]

    def test_get_token_values(self):
        task = BiennialCropTask(
            sku='PA001', variety_name='Parsley', bed='B2', bed_second_year='C3'
        )
        assert task.get_token_values() == {
            'sku': 'PA001',
            'variety_name': 'Parsley',
            'bed': 'B2',
            'bed_second_year': 'C3',
        }


@pytest.mark.django_db
class TestBaseTaskGroupTemplate:
    """Tests for BaseTaskGroupTemplate model methods"""

    def test_get_parent_task_model(self, task_group_template):
        assert task_group_template.get_parent_task_model() is CropTask

    def test_get_parent_task_model_none(self, empty_template):
        assert empty_template.get_parent_task_model() is None

    def test_get_token_field_names(self, task_group_template):
        assert task_group_template.get_token_field_names() == ['sku', 'variety_name', 'bed']

    def test_get_token_field_names_no_task_type(self, empty_template):
        assert empty_template.get_token_field_names() == []

    def test_get_effective_project_id_from_template(self, task_group_template, wagtail_site):
        task_group_template.todoist_project_id = '12345'
        assert task_group_template.get_effective_project_id(wagtail_site) == '12345'

    def test_get_effective_project_id_fallback_to_settings(
        self, task_group_template, wagtail_site, sync_settings
    ):
        task_group_template.todoist_project_id = ''
        sync_settings.todoist_project_id = '99999'
        sync_settings.save()
        assert task_group_template.get_effective_project_id(wagtail_site) == '99999'

    def test_get_effective_project_id_empty(self, task_group_template, wagtail_site):
        task_group_template.todoist_project_id = ''
        assert task_group_template.get_effective_project_id(wagtail_site) == ''


@pytest.mark.django_db
class TestTaskGroupCreationForm:
    """Tests for BaseTaskGroupCreationForm"""

    def test_form_init_without_template_id(self):
        form = BaseTaskGroupCreationForm()
        assert 'task_group_template' in form.fields
        assert 'description' in form.fields
        assert len(form.fields) == 2

    def test_form_init_with_template_id(self, task_group_template):
        form = BaseTaskGroupCreationForm(template_id=task_group_template.id)
        assert 'task_group_template' in form.fields
        assert 'description' in form.fields
        assert 'token_sku' in form.fields
        assert 'token_variety_name' in form.fields
        assert 'token_bed' in form.fields
        assert len(form.fields) == 5

    def test_dynamic_field_labels(self, task_group_template):
        form = BaseTaskGroupCreationForm(template_id=task_group_template.id)
        assert form.fields['token_sku'].label == 'Sku'
        assert form.fields['token_variety_name'].label == 'Variety Name'
        assert form.fields['token_bed'].label == 'Bed'

    def test_dynamic_field_required(self, task_group_template):
        """sku and variety_name are required (blank=False), bed is optional (blank=True)"""
        form = BaseTaskGroupCreationForm(template_id=task_group_template.id)
        assert form.fields['token_sku'].required is True
        assert form.fields['token_variety_name'].required is True
        assert form.fields['token_bed'].required is False

    def test_form_with_invalid_template_id(self):
        form = BaseTaskGroupCreationForm(template_id=99999)
        assert len(form.fields) == 2

    def test_form_with_no_task_type(self, empty_template):
        form = BaseTaskGroupCreationForm(template_id=empty_template.id)
        assert len(form.fields) == 2

    def test_form_validation_success(self, task_group_template):
        form = BaseTaskGroupCreationForm(
            data={
                'task_group_template': task_group_template.id,
                'token_sku': 'CH001',
                'token_variety_name': 'Habanero',
                'token_bed': 'A1',
            },
            template_id=task_group_template.id,
        )
        assert form.is_valid()

    def test_form_validation_missing_required_token(self, task_group_template):
        form = BaseTaskGroupCreationForm(
            data={
                'task_group_template': task_group_template.id,
                'token_sku': 'CH001',
                # missing token_variety_name (required)
            },
            template_id=task_group_template.id,
        )
        assert not form.is_valid()
        assert 'token_variety_name' in form.errors

    def test_form_validation_optional_field_omitted(self, task_group_template):
        """bed is optional so form should be valid without it"""
        form = BaseTaskGroupCreationForm(
            data={
                'task_group_template': task_group_template.id,
                'token_sku': 'CH001',
                'token_variety_name': 'Habanero',
            },
            template_id=task_group_template.id,
        )
        assert form.is_valid()

    def test_get_token_values(self, task_group_template):
        form = BaseTaskGroupCreationForm(
            data={
                'task_group_template': task_group_template.id,
                'token_sku': 'CH001',
                'token_variety_name': 'Habanero',
                'token_bed': 'A1',
            },
            template_id=task_group_template.id,
        )
        assert form.is_valid()
        assert form.get_token_values() == {
            'sku': 'CH001',
            'variety_name': 'Habanero',
            'bed': 'A1',
        }

    def test_get_token_values_empty(self):
        form = BaseTaskGroupCreationForm()
        assert form.get_token_values() == {}

    def test_queryset_only_live_templates(self, task_group_template):
        form = BaseTaskGroupCreationForm()
        queryset = form.fields['task_group_template'].queryset
        assert task_group_template in queryset

        task_group_template.unpublish()
        form2 = BaseTaskGroupCreationForm()
        assert task_group_template not in form2.fields['task_group_template'].queryset

    def test_template_field_populated_with_template_id(self, task_group_template):
        form = BaseTaskGroupCreationForm(template_id=task_group_template.id)
        assert form.fields['task_group_template'].initial == task_group_template
