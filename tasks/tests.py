import pytest
from django.test import TestCase
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase
from .models import TaskGroupTemplate, TaskPlannerSettings
from .forms import TaskGroupCreationForm


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
def planner_settings(db, wagtail_site):
    """Create TaskPlannerSettings for testing"""
    settings = TaskPlannerSettings.objects.create(
        site=wagtail_site,
        tokens='SKU, VARIETYNAME',
        parent_task_title='',
        description=''
    )
    return settings


@pytest.fixture
def empty_planner_settings(db, wagtail_site):
    """Create TaskPlannerSettings with no tokens"""
    settings = TaskPlannerSettings.objects.create(
        site=wagtail_site,
        tokens='',
        parent_task_title='',
        description=''
    )
    return settings


@pytest.fixture
def task_group_template(db, wagtail_site, planner_settings):
    """Create a TaskGroupTemplate for testing"""
    root_page = Page.objects.get(id=1)

    template = TaskGroupTemplate(
        title='Test Chilli Template',
        slug='test-chilli',
        description='',
        tasks=[
            {
                'type': 'task',
                'value': {
                    'title': 'Sow {SKU}',
                    'labels': 'sow, planting',
                    'subtasks': []
                }
            },
            {
                'type': 'task',
                'value': {
                    'title': 'Harvest {VARIETYNAME}',
                    'labels': 'harvest',
                    'subtasks': [
                        {
                            'title': '{SKU} checked in',
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
def empty_template(db, wagtail_site, empty_planner_settings):
    """Create a TaskGroupTemplate with no tokens in settings"""
    root_page = Page.objects.get(id=1)

    template = TaskGroupTemplate(
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
class TestTaskGroupCreationForm:
    """Tests for TaskGroupCreationForm"""

    def test_form_init_without_template_id(self):
        """Form should initialize with task_group_template and description fields"""
        form = TaskGroupCreationForm()

        assert 'task_group_template' in form.fields
        assert 'description' in form.fields
        assert len(form.fields) == 2

    def test_form_init_with_template_id(self, task_group_template, wagtail_site):
        """Form should create dynamic token fields when template_id provided"""
        form = TaskGroupCreationForm(template_id=task_group_template.id, site=wagtail_site)

        assert 'task_group_template' in form.fields
        assert 'description' in form.fields
        assert 'token_SKU' in form.fields
        assert 'token_VARIETYNAME' in form.fields
        assert len(form.fields) == 4

    def test_dynamic_field_labels(self, task_group_template, wagtail_site):
        """Dynamic token fields should have correct labels"""
        form = TaskGroupCreationForm(template_id=task_group_template.id, site=wagtail_site)

        assert form.fields['token_SKU'].label == 'SKU'
        assert form.fields['token_VARIETYNAME'].label == 'VARIETYNAME'

    def test_dynamic_field_required(self, task_group_template, wagtail_site):
        """Dynamic token fields should be required"""
        form = TaskGroupCreationForm(template_id=task_group_template.id, site=wagtail_site)

        assert form.fields['token_SKU'].required is True
        assert form.fields['token_VARIETYNAME'].required is True

    def test_form_with_invalid_template_id(self, wagtail_site):
        """Form should handle invalid template_id gracefully"""
        form = TaskGroupCreationForm(template_id=99999, site=wagtail_site)

        # Should only have base fields, no dynamic token fields added
        assert 'task_group_template' in form.fields
        assert 'description' in form.fields
        assert len(form.fields) == 2

    def test_form_with_empty_tokens(self, empty_template, wagtail_site):
        """Form should handle template with no tokens in settings"""
        form = TaskGroupCreationForm(template_id=empty_template.id, site=wagtail_site)

        # Should only have base fields
        assert 'task_group_template' in form.fields
        assert 'description' in form.fields
        assert len(form.fields) == 2

    def test_form_validation_success(self, task_group_template, wagtail_site):
        """Form should validate successfully with correct data"""
        form = TaskGroupCreationForm(
            data={
                'task_group_template': task_group_template.id,
                'token_SKU': 'CH001',
                'token_VARIETYNAME': 'Habanero'
            },
            template_id=task_group_template.id,
            site=wagtail_site
        )

        assert form.is_valid()

    def test_form_validation_missing_token(self, task_group_template, wagtail_site):
        """Form should fail validation when token value missing"""
        form = TaskGroupCreationForm(
            data={
                'task_group_template': task_group_template.id,
                'token_SKU': 'CH001',
                # missing token_VARIETYNAME
            },
            template_id=task_group_template.id,
            site=wagtail_site
        )

        assert not form.is_valid()
        assert 'token_VARIETYNAME' in form.errors

    def test_get_token_values(self, task_group_template, wagtail_site):
        """get_token_values should extract token values correctly"""
        form = TaskGroupCreationForm(
            data={
                'task_group_template': task_group_template.id,
                'token_SKU': 'CH001',
                'token_VARIETYNAME': 'Habanero'
            },
            template_id=task_group_template.id,
            site=wagtail_site
        )

        assert form.is_valid()
        token_values = form.get_token_values()

        assert token_values == {
            'SKU': 'CH001',
            'VARIETYNAME': 'Habanero'
        }

    def test_get_token_values_empty(self):
        """get_token_values should return empty dict for form without tokens"""
        form = TaskGroupCreationForm()
        token_values = form.get_token_values()

        assert token_values == {}

    def test_get_token_values_before_validation(self, task_group_template, wagtail_site):
        """get_token_values should return empty dict before form validation"""
        form = TaskGroupCreationForm(template_id=task_group_template.id, site=wagtail_site)
        token_values = form.get_token_values()

        assert token_values == {}

    def test_queryset_only_live_templates(self, task_group_template):
        """Form should only show live templates in queryset"""
        form = TaskGroupCreationForm()
        queryset = form.fields['task_group_template'].queryset

        # Should only include live templates
        assert task_group_template in queryset

        # Unpublish template
        task_group_template.unpublish()

        # Create new form and check queryset
        form2 = TaskGroupCreationForm()
        queryset2 = form2.fields['task_group_template'].queryset

        assert task_group_template not in queryset2

    def test_template_field_populated_with_template_id(self, task_group_template, wagtail_site):
        """Form should pre-populate task_group_template field when template_id provided"""
        form = TaskGroupCreationForm(template_id=task_group_template.id, site=wagtail_site)

        # Should have initial value set
        assert form.fields['task_group_template'].initial == task_group_template

    def test_template_field_not_populated_without_template_id(self):
        """Form should not pre-populate task_group_template field when no template_id"""
        form = TaskGroupCreationForm()

        # Should not have initial value
        assert form.fields['task_group_template'].initial is None


@pytest.mark.django_db
class TestTaskPlannerSettings:
    """Tests for TaskPlannerSettings model"""

    def test_get_token_list_with_tokens(self, wagtail_site):
        """get_token_list should parse comma-separated tokens"""
        settings = TaskPlannerSettings.objects.create(
            site=wagtail_site,
            tokens='SKU, VARIETYNAME, COLOR'
        )

        token_list = settings.get_token_list()

        assert token_list == ['SKU', 'VARIETYNAME', 'COLOR']

    def test_get_token_list_strips_whitespace(self, wagtail_site):
        """get_token_list should strip whitespace from tokens"""
        settings = TaskPlannerSettings.objects.create(
            site=wagtail_site,
            tokens='  SKU  ,   VARIETYNAME   ,COLOR'
        )

        token_list = settings.get_token_list()

        assert token_list == ['SKU', 'VARIETYNAME', 'COLOR']

    def test_get_token_list_empty_string(self, wagtail_site):
        """get_token_list should return empty list for empty tokens"""
        settings = TaskPlannerSettings.objects.create(
            site=wagtail_site,
            tokens=''
        )

        token_list = settings.get_token_list()

        assert token_list == []

    def test_get_token_list_whitespace_only(self, wagtail_site):
        """get_token_list should return empty list for whitespace-only tokens"""
        settings = TaskPlannerSettings.objects.create(
            site=wagtail_site,
            tokens='   ,  ,  '
        )

        token_list = settings.get_token_list()

        assert token_list == []
