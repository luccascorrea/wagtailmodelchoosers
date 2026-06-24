from django.test import TestCase, override_settings
from django.core.exceptions import ImproperlyConfigured

from wagtailmodelchoosers.utils import (
    flatten,
    curry,
    first_non_empty,
    get_chooser_options,
)


class TestUtils(TestCase):
    def test_flatten(self):
        self.assertEqual(list(flatten([1, [2, 3], [[4], 5]])), [1, 2, 3, 4, 5])
        self.assertEqual(list(flatten([])), [])

    def test_curry(self):
        def add(a, b, c=0):
            return a + b + c

        add_five = curry(add, 5)
        self.assertEqual(add_five(10), 15)
        self.assertEqual(add_five(10, c=3), 18)

    def test_first_non_empty(self):
        # Dictionary input
        self.assertEqual(first_non_empty({'foo': 'bar'}, 'foo'), 'bar')
        self.assertEqual(first_non_empty({'foo': 'bar', 'baz': ''}, ['baz', 'foo']), 'bar')
        self.assertEqual(first_non_empty({'foo': ''}, 'foo', default='default'), '')
        self.assertEqual(first_non_empty({'foo': None}, 'foo', default='default'), None)

        # Object input
        class Dummy:
            foo = 'bar'
            baz = None

        dummy = Dummy()
        self.assertEqual(first_non_empty(dummy, 'foo'), 'bar')
        self.assertEqual(first_non_empty(dummy, ['baz', 'foo']), 'bar')
        self.assertEqual(first_non_empty(dummy, 'baz', default='default'), None)

    @override_settings(MODEL_CHOOSERS_OPTIONS={})
    def test_get_chooser_options_missing(self):
        with self.assertRaises(ImproperlyConfigured) as ctx:
            get_chooser_options('missing')
        self.assertIn('Missing options definition for chooser', str(ctx.exception))

    @override_settings(MODEL_CHOOSERS_OPTIONS={'invalid': {'display': 'name'}})
    def test_get_chooser_options_no_content_or_remote(self):
        with self.assertRaises(ImproperlyConfigured) as ctx:
            get_chooser_options('invalid')
        self.assertIn('should define either `content_type` (for models) or `remote_endpoint` (for remote models)', str(ctx.exception))

    @override_settings(MODEL_CHOOSERS_OPTIONS={
        'invalid_fields': {
            'content_type': 'core.SimpleModel',
            'display': ['title', 'subtitle'],
            'fields_to_save': ['title'],
        }
    })
    def test_get_chooser_options_invalid_fields_to_save(self):
        with self.assertRaises(ImproperlyConfigured) as ctx:
            get_chooser_options('invalid_fields')
        self.assertIn('Invalid `fields_to_save` definition for chooser', str(ctx.exception))
        self.assertIn('missing: `subtitle`', str(ctx.exception))

    @override_settings(MODEL_CHOOSERS_OPTIONS={
        'valid_fields': {
            'content_type': 'core.SimpleModel',
            'display': ['title', 'subtitle'],
            'fields_to_save': ['title', 'subtitle', 'other'],
        }
    })
    def test_get_chooser_options_valid_fields_to_save(self):
        opts = get_chooser_options('valid_fields')
        self.assertEqual(opts['fields_to_save'], ['title', 'subtitle', 'other'])
