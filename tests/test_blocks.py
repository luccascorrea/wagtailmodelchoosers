from __future__ import absolute_import, unicode_literals

from django import forms
from django.test import TestCase, override_settings

try:
    from wagtail.blocks import StreamBlock
except ImportError:
    from wagtail.core.blocks import StreamBlock

try:
    from wagtail.models import Page
except ImportError:
    from wagtail.core.models import Page

try:
    from wagtail.models.reference_index import ReferenceIndex
except ImportError:
    ReferenceIndex = None

from core.models import SimplePage

from wagtailmodelchoosers import blocks, widgets

TEST_MODEL_CHOOSERS_OPTIONS = {
    'core_page': {
        'content_type': 'wagtailcore.Page',
    },
    'remote_test': {
        'remote_endpoint': 'http://example.com/api',
        'display': 'name',
    }
}


@override_settings(MODEL_CHOOSERS_OPTIONS=TEST_MODEL_CHOOSERS_OPTIONS)
class TestModelChooserBlock(TestCase):
    def setUp(self):
        self.root_page = Page.objects.get(id=2)

        # Add child page
        self.child_page = SimplePage(
            title="foobarbaz",
            content="hello",
        )
        self.root_page.add_child(instance=self.child_page)

    def test_serialize(self):
        """The value of a ModelChooserBlock (a Page object) should serialize to an ID"""
        block = blocks.ModelChooserBlock('core_page')
        self.assertEqual(block.get_prep_value(self.child_page), self.child_page.id)

        # None should serialize to None
        self.assertEqual(block.get_prep_value(None), None)

    def test_deserialize(self):
        """The serialized value of a ModelChooserBlock (an ID) should deserialize to a Page object"""
        block = blocks.ModelChooserBlock('core_page')
        self.assertEqual(isinstance(block.to_python(self.child_page.id), Page), isinstance(self.child_page, Page))

        # None should deserialize to None
        self.assertEqual(block.to_python(None), None)

    def test_form_render(self):
        block = blocks.ModelChooserBlock('core_page', help_text="pick a page, any page")

        if hasattr(block, 'render_form'):
            empty_form_html = block.render_form(None, 'page')
            self.assertIn('<input type="hidden" value="" name="page"', empty_form_html)
            self.assertIn('initModelChooser(', empty_form_html)
        else:
            try:
                from wagtail.blocks import BlockWidget
            except ImportError:
                from wagtail.core.blocks import BlockWidget
            empty_form_html = BlockWidget(block).render('page', None)
            self.assertIn('data-value="null"', empty_form_html)
            self.assertIn('initModelChooser(', empty_form_html)

        test_page = self.child_page
        if hasattr(block, 'render_form'):
            test_form_html = block.render_form(test_page, 'page')
            expected_html = '<input type="hidden" value="%d" name="page" ' % test_page.id
            self.assertIn(expected_html, test_form_html)
            self.assertIn("pick a page, any page", test_form_html)
        else:
            try:
                from wagtail.blocks import BlockWidget
            except ImportError:
                from wagtail.core.blocks import BlockWidget
            test_form_html = BlockWidget(block).render('page', test_page)
            expected_values = [
                'data-value="&quot;%d&quot;"' % test_page.id,
                'data-value="%d"' % test_page.id,
            ]
            self.assertTrue(any(val in test_form_html for val in expected_values))
            self.assertIn("pick a page, any page", test_form_html)

    def test_to_python(self):
        block = blocks.ModelChooserBlock('core_page')
        test_page = self.child_page

        value = block.to_python(test_page.pk)
        self.assertEqual(isinstance(value, Page), isinstance(test_page, Page))
        self.assertEqual(block.to_python(None), None)

    def test_get_prep_value(self):
        block = blocks.ModelChooserBlock('core_page')
        test_page = self.child_page

        self.assertEqual(block.get_prep_value(test_page.pk), test_page.pk)
        self.assertEqual(block.get_prep_value(test_page), test_page.pk)
        self.assertEqual(block.get_prep_value(None), None)

    def test_target_model(self):
        block = blocks.ModelChooserBlock('core_page')
        self.assertEqual(block.target_model, Page)

    def test_widget(self):
        block = blocks.ModelChooserBlock('core_page')
        self.assertTrue(isinstance(block.widget, widgets.ModelChooserWidget))

    def test_extract_references_instance(self):
        block = blocks.ModelChooserBlock('core_page')
        refs = list(block.extract_references(self.child_page))
        self.assertEqual(refs, [(Page, str(self.child_page.pk), "", "")])

    def test_extract_references_pk(self):
        block = blocks.ModelChooserBlock('core_page')
        refs = list(block.extract_references(self.child_page.pk))
        self.assertEqual(refs, [(Page, str(self.child_page.pk), "", "")])

        refs_str = list(block.extract_references(str(self.child_page.pk)))
        self.assertEqual(refs_str, [(Page, str(self.child_page.pk), "", "")])

    def test_extract_references_none(self):
        block = blocks.ModelChooserBlock('core_page')
        refs = list(block.extract_references(None))
        self.assertEqual(refs, [])


@override_settings(MODEL_CHOOSERS_OPTIONS=TEST_MODEL_CHOOSERS_OPTIONS)
class TestRemoteModelChooserBlock(TestCase):
    def test_serialize(self):
        block = blocks.RemoteModelChooserBlock('remote_test')
        self.assertEqual(block.get_prep_value({'id': 1, 'name': 'foo'}), {'id': 1, 'name': 'foo'})

    def test_deserialize(self):
        block = blocks.RemoteModelChooserBlock('remote_test')
        self.assertEqual(block.to_python(None), {})
        self.assertEqual(block.to_python({'id': 1, 'name': 'foo'}), {'id': 1, 'name': 'foo'})
        self.assertEqual(block.to_python('{"id": 1, "name": "foo"}'), {'id': 1, 'name': 'foo'})

    def test_bulk_to_python(self):
        block = blocks.RemoteModelChooserBlock('remote_test')
        res = block.bulk_to_python(['{"id": 1}', None])
        self.assertEqual(res, [{'id': 1}, {}])

    def test_value_from_form(self):
        block = blocks.RemoteModelChooserBlock('remote_test')
        self.assertEqual(block.value_from_form(None), None)
        self.assertEqual(block.value_from_form('{"id": 1}'), '{"id": 1}')
        self.assertEqual(block.value_from_form('invalid json'), None)

    def test_render_basic(self):
        block = blocks.RemoteModelChooserBlock('remote_test')
        self.assertEqual(block.render_basic({'name': 'Hello'}), 'Hello')
        self.assertEqual(block.render_basic('{"name": "Hello"}'), 'Hello')
        self.assertEqual(block.render_basic(None), '')

    def test_clean(self):
        block = blocks.RemoteModelChooserBlock('remote_test')
        self.assertEqual(block.clean({'id': 1}), {'id': 1})

    def test_field_and_widget(self):
        block = blocks.RemoteModelChooserBlock('remote_test')
        field = block.field
        self.assertTrue(isinstance(field, forms.CharField))
        self.assertTrue(isinstance(block.widget, widgets.RemoteModelChooserWidget))

    def test_extract_references(self):
        block = blocks.RemoteModelChooserBlock('remote_test')
        self.assertEqual(list(block.extract_references(None)), [])
        self.assertEqual(list(block.extract_references({'id': 1, 'name': 'foo'})), [])
        self.assertEqual(list(block.extract_references('{"id": 1, "name": "foo"}')), [])


@override_settings(MODEL_CHOOSERS_OPTIONS=TEST_MODEL_CHOOSERS_OPTIONS)
class TestStreamFieldReferenceExtraction(TestCase):
    def setUp(self):
        self.root_page = Page.objects.get(id=2)
        self.child_page = SimplePage(
            title="stream test child",
            content="stream content",
        )
        self.root_page.add_child(instance=self.child_page)

    def test_stream_block_extract_references(self):
        sb = StreamBlock([
            ('model', blocks.ModelChooserBlock('core_page')),
            ('remote', blocks.RemoteModelChooserBlock('remote_test')),
        ])
        val = sb.to_python([
            {'type': 'model', 'value': self.child_page.pk},
            {'type': 'remote', 'value': {'id': 'ext-123', 'name': 'External Data'}},
        ])
        if hasattr(sb, 'extract_references'):
            refs = list(sb.extract_references(val))
            self.assertEqual(len(refs), 1)
            self.assertEqual(refs[0][0], Page)
            self.assertEqual(refs[0][1], str(self.child_page.pk))

    def test_reference_index_compatibility(self):
        if ReferenceIndex is not None:
            refs = list(ReferenceIndex._extract_references_from_object(self.child_page))
            self.assertIsInstance(refs, list)
