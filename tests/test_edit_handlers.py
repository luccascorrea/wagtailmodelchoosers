from django.contrib.auth import get_user_model
from django.db import models
from django.forms import Media
from django.test import TestCase, override_settings

try:
    from wagtail.models import Page
except ImportError:
    from wagtail.core.models import Page

from core.models import SimplePage

from wagtailmodelchoosers.edit_handlers import (
    ChildModelComparison,
    InlineModelPanel,
    ModelChooserPanel,
    ModelComparison,
    RemoteModelChooserPanel,
)
from wagtailmodelchoosers.widgets import ModelChooserWidget, RemoteModelChooserWidget

TEST_MODEL_CHOOSERS_OPTIONS = {
    'core_page': {
        'content_type': 'wagtailcore.Page',
        'display': 'title',
    },
    'user_chooser': {
        'content_type': 'auth.User',
        'display': 'username',
    },
    'remote_test': {
        'remote_endpoint': 'http://example.com/api',
        'display': 'name',
    }
}


@override_settings(MODEL_CHOOSERS_OPTIONS=TEST_MODEL_CHOOSERS_OPTIONS)
class TestEditHandlers(TestCase):
    def setUp(self):
        # SimplePage has the 'owner' ForeignKey field pointing to User
        self.model = SimplePage

    def test_model_chooser_panel_init_and_bind(self):
        panel = ModelChooserPanel('owner', 'core_page')
        self.assertEqual(panel.field_name, 'owner')
        self.assertEqual(panel.chooser, 'core_page')
        self.assertEqual(panel.label, 'core_page')

        # Bind to model
        if hasattr(panel, 'bind_to_model'):
            bound_panel = panel.bind_to_model(self.model)
        else:
            bound_panel = panel.bind_to(model=self.model)

        self.assertEqual(bound_panel.model, self.model)
        self.assertEqual(bound_panel.target_model(), get_user_model())

    def test_model_chooser_panel_form_options(self):
        panel = ModelChooserPanel('owner', 'core_page')
        if hasattr(panel, 'bind_to_model'):
            bound_panel = panel.bind_to_model(self.model)
        else:
            bound_panel = panel.bind_to(model=self.model)

        # In Wagtail 3.0, we use get_form_options.
        # In Wagtail 2.x, we used widget_overrides.
        if hasattr(bound_panel, 'get_form_options'):
            opts = bound_panel.get_form_options()
            widget = opts['widgets']['owner']
        else:
            widgets_dict = bound_panel.widget_overrides()
            widget = widgets_dict['owner']

        self.assertTrue(isinstance(widget, ModelChooserWidget))
        self.assertEqual(widget.chooser, 'core_page')

    def test_model_chooser_panel_clone(self):
        panel = ModelChooserPanel('owner', 'core_page')
        cloned = panel.clone()
        self.assertEqual(cloned.field_name, 'owner')
        self.assertEqual(cloned.chooser, 'core_page')

    def test_model_chooser_panel_with_icon_and_base_form_class(self):
        panel = ModelChooserPanel('owner', 'core_page', icon='user', heading='Owner Heading')
        self.assertEqual(getattr(panel, 'icon', None), 'user')
        self.assertEqual(panel.heading, 'Owner Heading')
        cloned = panel.clone()
        self.assertEqual(getattr(cloned, 'icon', None), 'user')
        self.assertEqual(cloned.heading, 'Owner Heading')

    def test_model_chooser_panel_clone_kwargs(self):
        panel = ModelChooserPanel('owner', 'core_page', icon='snippet', heading='Custom')
        if hasattr(panel, 'clone_kwargs'):
            kwargs = panel.clone_kwargs()
            self.assertEqual(kwargs['field_name'], 'owner')
            self.assertEqual(kwargs['chooser'], 'core_page')
            self.assertEqual(kwargs['icon'], 'snippet')
            self.assertEqual(kwargs['heading'], 'Custom')

    def test_remote_model_chooser_panel(self):
        panel = RemoteModelChooserPanel('owner', 'remote_test')
        self.assertEqual(panel.field_name, 'owner')
        self.assertEqual(panel.chooser, 'remote_test')

        if hasattr(panel, 'bind_to_model'):
            bound_panel = panel.bind_to_model(self.model)
        else:
            bound_panel = panel.bind_to(model=self.model)

        if hasattr(bound_panel, 'get_form_options'):
            opts = bound_panel.get_form_options()
            widget = opts['widgets']['owner']
        else:
            widgets_dict = bound_panel.widget_overrides()
            widget = widgets_dict['owner']

        self.assertTrue(isinstance(widget, RemoteModelChooserWidget))
        self.assertEqual(widget.chooser, 'remote_test')

    def test_remote_model_chooser_panel_clone(self):
        panel = RemoteModelChooserPanel('owner', 'remote_test')
        cloned = panel.clone()
        self.assertEqual(cloned.field_name, 'owner')
        self.assertEqual(cloned.chooser, 'remote_test')

    def test_remote_model_chooser_panel_with_icon(self):
        panel = RemoteModelChooserPanel('owner', 'remote_test', icon='doc-full', heading='Remote Heading')
        self.assertEqual(getattr(panel, 'icon', None), 'doc-full')
        self.assertEqual(panel.heading, 'Remote Heading')
        cloned = panel.clone()
        self.assertEqual(getattr(cloned, 'icon', None), 'doc-full')
        self.assertEqual(cloned.heading, 'Remote Heading')

    def test_remote_model_chooser_panel_clone_kwargs(self):
        panel = RemoteModelChooserPanel('owner', 'remote_test', icon='link', heading='Remote')
        if hasattr(panel, 'clone_kwargs'):
            kwargs = panel.clone_kwargs()
            self.assertEqual(kwargs['field_name'], 'owner')
            self.assertEqual(kwargs['chooser'], 'remote_test')
            self.assertEqual(kwargs['icon'], 'link')
            self.assertEqual(kwargs['heading'], 'Remote')

    def test_model_chooser_panel_read_only(self):
        panel = ModelChooserPanel('selected_user', 'user_chooser', read_only=True)
        self.assertTrue(panel.read_only)

        if hasattr(panel, 'bind_to_model'):
            bound_panel = panel.bind_to_model(self.model)
        else:
            bound_panel = panel.bind_to(model=self.model)

        self.assertEqual(bound_panel.get_form_options(), {})

        # Verify clone preserves read_only
        cloned = panel.clone()
        self.assertTrue(cloned.read_only)
        if hasattr(panel, 'clone_kwargs'):
            self.assertTrue(panel.clone_kwargs()['read_only'])

    def test_model_chooser_panel_attrs(self):
        attrs = {'data-custom': 'val', 'class': 'custom-class'}
        panel = ModelChooserPanel('owner', 'core_page', attrs=attrs)
        self.assertEqual(panel.attrs, attrs)

        cloned = panel.clone()
        self.assertEqual(cloned.attrs, attrs)
        if hasattr(panel, 'clone_kwargs'):
            self.assertEqual(panel.clone_kwargs()['attrs'], attrs)

    def test_model_chooser_panel_format_value_for_display(self):
        User = get_user_model()
        user, _ = User.objects.get_or_create(username='paneluser', email='paneluser@example.com')
        panel = ModelChooserPanel('selected_user', 'user_chooser')
        if hasattr(panel, 'bind_to_model'):
            panel = panel.bind_to_model(self.model)
        else:
            panel = panel.bind_to(model=self.model)

        # Instance value
        self.assertEqual(panel.format_value_for_display(user), 'paneluser')

        # PK value
        self.assertEqual(panel.format_value_for_display(user.pk), 'paneluser')

        # None and empty
        self.assertEqual(panel.format_value_for_display(None), '')
        self.assertEqual(panel.format_value_for_display(''), '')

        # Non-existent PK fallback
        self.assertEqual(panel.format_value_for_display(99999), '99999')

    def test_remote_model_chooser_panel_read_only(self):
        panel = RemoteModelChooserPanel('owner', 'remote_test', read_only=True)
        self.assertTrue(panel.read_only)

        if hasattr(panel, 'bind_to_model'):
            bound_panel = panel.bind_to_model(self.model)
        else:
            bound_panel = panel.bind_to(model=self.model)

        self.assertEqual(bound_panel.get_form_options(), {})

        # Verify clone preserves read_only
        cloned = panel.clone()
        self.assertTrue(cloned.read_only)
        if hasattr(panel, 'clone_kwargs'):
            self.assertTrue(panel.clone_kwargs()['read_only'])

    def test_remote_model_chooser_panel_attrs(self):
        attrs = {'data-remote': 'true'}
        panel = RemoteModelChooserPanel('owner', 'remote_test', attrs=attrs)
        self.assertEqual(panel.attrs, attrs)

        cloned = panel.clone()
        self.assertEqual(cloned.attrs, attrs)
        if hasattr(panel, 'clone_kwargs'):
            self.assertEqual(panel.clone_kwargs()['attrs'], attrs)

    def test_remote_model_chooser_panel_format_value_for_display(self):
        panel = RemoteModelChooserPanel('owner', 'remote_test')

        # Dict value
        self.assertEqual(panel.format_value_for_display({'name': 'Remote Item'}), 'Remote Item')

        # JSON string value
        self.assertEqual(panel.format_value_for_display('{"name": "Remote Item"}'), 'Remote Item')

        # Plain string value fallback
        self.assertEqual(panel.format_value_for_display('plain text'), 'plain text')

        # None and empty
        self.assertEqual(panel.format_value_for_display(None), '')
        self.assertEqual(panel.format_value_for_display(''), '')

    def test_inline_model_panel(self):
        # We can instantiate InlineModelPanel. It inherits from InlinePanel.
        panel = InlineModelPanel('simple_children', panels=[])
        self.assertEqual(panel.relation_name, 'simple_children')
        self.assertTrue(panel.is_relation)

        # Clone kwargs check
        kwargs = panel.clone_kwargs()
        self.assertEqual(kwargs['relation_name'], 'simple_children')


class TestComparisons(TestCase):
    def test_model_comparison_many_to_one(self):
        class MockField(models.ManyToOneRel):
            def __init__(self):
                pass

            def get_accessor_name(self):
                return 'mock_accessor'

        class MockObj:
            def __init__(self, val):
                self.val = val

            @property
            def mock_accessor(self):
                outer_val = self.val

                class MockAll:
                    def all(self):
                        return outer_val

                return MockAll()

        field = MockField()
        obj_a = MockObj([1, 2])
        obj_b = MockObj([2, 3])
        comparison = ModelComparison(field, obj_a, obj_b)
        self.assertEqual(comparison.get_items(), ([1, 2], [2, 3]))
        self.assertEqual(comparison.get_item_display(1), '1')

    def test_model_comparison_other_fields(self):
        class MockField(models.Field):
            model = Page
            attname = 'mock_field'

        class MockObj:
            mock_field = 'test'

        field = MockField()
        obj_a = MockObj()
        obj_b = MockObj()
        # Should delegate to M2MFieldComparison
        comparison = ModelComparison(field, obj_a, obj_b)
        self.assertEqual(comparison.field, field)

    def test_model_comparison_htmldiff_identical(self):
        class MockField(models.Field):
            model = Page
            attname = 'mock_field'

        class MockObj:
            mock_field = ['item1', 'item2']

        field = MockField()
        obj_a = MockObj()
        obj_b = MockObj()
        comparison = ModelComparison(field, obj_a, obj_b)
        diff = comparison.htmldiff()
        self.assertIn('item1', str(diff))
        self.assertIn('item2', str(diff))

    def test_child_model_comparison_init(self):
        class MockField:
            def get_accessor_name(self):
                return 'children'

        class MockObj:
            def __init__(self, items):
                self._items = items

            @property
            def children(self):
                items = self._items

                class MockAll:
                    def all(self):
                        return items

                return MockAll()

        field = MockField()
        obj_a = MockObj(['a1', 'a2'])
        obj_b = MockObj(['b1'])
        child_comp = ChildModelComparison(field, [], obj_a, obj_b)
        self.assertEqual(list(child_comp.val_a), ['a1', 'a2'])
        self.assertEqual(list(child_comp.val_b), ['b1'])
