from __future__ import absolute_import, unicode_literals

import uuid
from unittest.mock import patch

from django.test import TestCase
from django.urls.exceptions import NoReverseMatch

try:
    from wagtail.models import Page
except ImportError:
    from wagtail.core.models import Page

from core.models import SimpleModel, SimplePage

from wagtailmodelchoosers import widgets


class TestModelChooserWidget(TestCase):
    def setUp(self):
        self.root_page = Page.objects.get(id=2)

        # Add child page
        self.child_page = SimplePage(
            title="foobarbaz",
            content="hello",
        )
        self.root_page.add_child(instance=self.child_page)

    def get_widget_options(self):
        return {
            'display': 'title',
            'list_display': [{'name': 'title', 'label': 'Title'}],
            'pk_name': 'id',
            'chooser': 'test_chooser',
            'has_list_filter': False,
            'adjustable_filter_type': False,
            'search_fields': [],
        }

    def test_get_target_model_string(self):
        widget = widgets.ModelChooserWidget('wagtailcore.Page', **self.get_widget_options())
        model = widget.target_model()
        self.assertEqual(model.__class__, Page)

    def test_get_target_model_class(self):
        widget = widgets.ModelChooserWidget(Page, **self.get_widget_options())
        model = widget.target_model()
        self.assertEqual(model.__class__, Page)

    def test_get_instance_none_value(self):
        widget = widgets.ModelChooserWidget(Page, **self.get_widget_options())
        self.assertFalse(widget.get_instance(''))

    def test_get_instance_page_value(self):
        widget = widgets.ModelChooserWidget(Page, **self.get_widget_options())
        self.assertEqual(widget.get_instance(2), self.root_page)

    def test_get_instance_no_page_value_is_none(self):
        widget = widgets.ModelChooserWidget(Page, **self.get_widget_options())
        self.assertEqual(widget.get_instance(999), None)

    def test_url_builder(self):
        widget = widgets.ModelChooserWidget(Page, **self.get_widget_options())
        url = widget.get_endpoint()
        self.assertEqual(url, '/admin/modelchoosers/api/v1/model/test_chooser')

    def test_get_internal_value(self):
        id_ = uuid.uuid4()

        class Stub:
            pk = None

        stub = Stub()
        stub.pk = id_
        widget = widgets.ModelChooserWidget(Page, **self.get_widget_options())
        value = widget.get_internal_value(stub)
        self.assertEqual(value, str(id_))

    def test_get_js_init_data(self):
        widget = widgets.ModelChooserWidget(Page, **self.get_widget_options())
        data = widget.get_js_init_data('field-1', None, self.root_page)
        expected_data = {
            'label': 'Page',
            'required': True,
            'initial_display_value': 'Welcome to your new Wagtail site!',
            'initial_thumbnail': None,
            'thumbnail': None,
            'display': 'title',
            'list_display': [{'name': 'title', 'label': 'Title'}],
            'has_list_filter': False,
            'adjustable_filter_type': False,
            'endpoint': '/admin/modelchoosers/api/v1/model/test_chooser',
            'edit_endpoint': '/admin/pages/0/edit/',
            'filters_endpoint': '/admin/modelchoosers/api/v1/filters/test_chooser/',
            'pk_name': 'id',
        }

        self.assertEqual(data, expected_data)

    def test_get_js_init_data_non_page_model(self):
        opts = self.get_widget_options()
        opts['chooser'] = 'custom_chooser'
        widget = widgets.ModelChooserWidget(SimpleModel, **opts)
        data = widget.get_js_init_data('field-2', None, None)
        self.assertIsNone(data['edit_endpoint'])
        self.assertEqual(data['label'], 'SimpleModel')

    def test_render_js_init(self):
        widget = widgets.ModelChooserWidget(Page, **self.get_widget_options())
        js_init = widget.render_js_init('field-1', None, self.root_page)

        expected_pattern = (
            r'^'                                        # Start of line
            r'wagtailModelChoosers.initModelChooser\('  # Function name
            r'".+"'                                     # First argument, the field id (a string)
            r', '                                       # Comma and space between arguments
            r'.+'                                       # Second argument, the data (an object)
            r'\)'                                       # End of function
            r'$'                                        # End of line
        )

        self.assertRegex(js_init, expected_pattern)

    def test_render_html(self):
        widget = widgets.ModelChooserWidget(Page, **self.get_widget_options())
        html = widget.render_html('test', None, {})
        self.assertIn('<input type="hidden" value="" name="test" >', html)

    def test_render_html_with_value(self):
        widget = widgets.ModelChooserWidget(Page, **self.get_widget_options())
        html = widget.render_html('test', self.root_page, {})
        self.assertIn('<input type="hidden" value="2" name="test" >', html)

    def test_get_edit_endpoint_can_edit_false(self):
        opts = self.get_widget_options()
        opts['can_edit'] = False
        widget = widgets.ModelChooserWidget(Page, **opts)
        self.assertIsNone(widget.get_edit_endpoint())

    @patch('wagtailmodelchoosers.widgets.reverse')
    def test_get_edit_endpoint_snippet_viewset(self, mock_reverse):
        def fake_reverse(name, args=None, kwargs=None):
            if name == 'wagtailsnippets_wagtailcore_page:edit':
                return f'/admin/snippets/{args[0]}/'
            raise NoReverseMatch()

        mock_reverse.side_effect = fake_reverse
        widget = widgets.ModelChooserWidget(Page, **self.get_widget_options())
        self.assertEqual(widget.get_edit_endpoint(), '/admin/snippets/0/')

    @patch('wagtailmodelchoosers.widgets.reverse')
    def test_get_edit_endpoint_snippet_generic(self, mock_reverse):
        def fake_reverse(name, args=None, kwargs=None):
            if name == 'wagtailsnippets_wagtailcore_page:edit':
                raise NoReverseMatch()
            if name == 'wagtailsnippets:edit':
                return f'/admin/snippets/{args[0]}/{args[1]}/{args[2]}/'
            raise NoReverseMatch()

        mock_reverse.side_effect = fake_reverse
        widget = widgets.ModelChooserWidget(Page, **self.get_widget_options())
        self.assertEqual(widget.get_edit_endpoint(), '/admin/snippets/wagtailcore/page/0/')

    @patch('wagtailmodelchoosers.widgets.reverse')
    def test_get_edit_endpoint_model_viewset_default_name(self, mock_reverse):
        def fake_reverse(name, args=None, kwargs=None):
            if name == 'page:edit':
                return f'/admin/page/edit/{args[0]}/'
            raise NoReverseMatch()

        mock_reverse.side_effect = fake_reverse
        widget = widgets.ModelChooserWidget(Page, **self.get_widget_options())
        self.assertEqual(widget.get_edit_endpoint(), '/admin/page/edit/0/')

    @patch('wagtailmodelchoosers.widgets.reverse')
    def test_get_edit_endpoint_model_viewset_app_prefixed(self, mock_reverse):
        def fake_reverse(name, args=None, kwargs=None):
            if name == 'wagtailcore_page:edit':
                return f'/admin/wagtailcore_page/edit/{args[0]}/'
            raise NoReverseMatch()

        mock_reverse.side_effect = fake_reverse
        widget = widgets.ModelChooserWidget(Page, **self.get_widget_options())
        self.assertEqual(widget.get_edit_endpoint(), '/admin/wagtailcore_page/edit/0/')

    @patch('wagtailmodelchoosers.widgets.reverse')
    def test_get_edit_endpoint_page_subclass(self, mock_reverse):
        def fake_reverse(name, args=None, kwargs=None):
            if name == 'wagtailadmin_pages:edit':
                return f'/admin/pages/{args[0]}/edit/'
            raise NoReverseMatch()

        mock_reverse.side_effect = fake_reverse
        widget = widgets.ModelChooserWidget(Page, **self.get_widget_options())
        self.assertEqual(widget.get_edit_endpoint(), '/admin/pages/0/edit/')

    @patch('wagtailmodelchoosers.widgets.reverse')
    def test_get_edit_endpoint_modeladmin_fallback(self, mock_reverse):
        def fake_reverse(name, args=None, kwargs=None):
            if name == 'wagtailcore_page_modeladmin_edit':
                return f'/admin/modeladmin/{kwargs["instance_pk"]}/'
            raise NoReverseMatch()

        mock_reverse.side_effect = fake_reverse
        widget = widgets.ModelChooserWidget(Page, **self.get_widget_options())
        self.assertEqual(widget.get_edit_endpoint(), '/admin/modeladmin/0/')

    @patch('wagtailmodelchoosers.widgets.reverse')
    def test_get_edit_endpoint_none_when_all_fail(self, mock_reverse):
        mock_reverse.side_effect = NoReverseMatch()
        widget = widgets.ModelChooserWidget(Page, **self.get_widget_options())
        self.assertIsNone(widget.get_edit_endpoint())


class TestRemoteModelChooserWidget(TestCase):
    def get_widget_options(self):
        return {
            'display': 'title',
            'list_display': [{'name': 'title', 'label': 'Title'}],
            'pk_name': 'id',
            'chooser': 'remote_chooser',
        }

    def test_get_endpoint(self):
        widget = widgets.RemoteModelChooserWidget(**self.get_widget_options())
        self.assertEqual(widget.get_endpoint(), '/admin/modelchoosers/api/v1/remote_model/remote_chooser')

    def test_get_display_value(self):
        widget = widgets.RemoteModelChooserWidget(**self.get_widget_options())
        self.assertEqual(widget.get_display_value({'title': 'Book 1'}), 'Book 1')
        self.assertEqual(widget.get_display_value(None), '')

    def test_get_internal_value(self):
        widget = widgets.RemoteModelChooserWidget(**self.get_widget_options())
        self.assertEqual(widget.get_internal_value({'id': 1}), '{"id": 1}')
        self.assertEqual(widget.get_internal_value(None), '')

    def test_get_value_data(self):
        widget = widgets.RemoteModelChooserWidget(**self.get_widget_options())
        self.assertEqual(widget.get_value_data('{"id": 1}'), {'id': 1})
        self.assertEqual(widget.get_value_data('invalid json'), {})
        self.assertEqual(widget.get_value_data({'id': 1}), {'id': 1})

    def test_get_js_init_data(self):
        widget = widgets.RemoteModelChooserWidget(**self.get_widget_options())
        data = widget.get_js_init_data('field-remote', None, {'id': 1, 'title': 'Remote Title'})
        self.assertEqual(data['label'], 'remote_chooser')
        self.assertEqual(data['initial_display_value'], 'Remote Title')
        self.assertEqual(data['endpoint'], '/admin/modelchoosers/api/v1/remote_model/remote_chooser')

    def test_render_js_init(self):
        widget = widgets.RemoteModelChooserWidget(**self.get_widget_options())
        js_init = widget.render_js_init('field-remote', None, {'id': 1, 'title': 'Remote Title'})
        self.assertIn('wagtailModelChoosers.initRemoteModelChooser(', js_init)

    def test_render_html(self):
        widget = widgets.RemoteModelChooserWidget(**self.get_widget_options())
        html = widget.render_html('remote_field', {'id': 1, 'title': 'Remote Title'}, {})
        self.assertIn('name="remote_field"', html)
        self.assertIn('&quot;id&quot;: 1', html)
