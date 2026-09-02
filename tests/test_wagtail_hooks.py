from django.test import TestCase

from wagtailmodelchoosers.wagtail_hooks import (
    wagtailmodelchoosers_admin_css,
    wagtailmodelchoosers_admin_js,
    wagtailmodelchoosers_admin_urls,
)


class TestWagtailHooks(TestCase):
    def test_admin_css(self):
        css_html = wagtailmodelchoosers_admin_css()
        self.assertIn('wagtailmodelchoosers.css', str(css_html))
        self.assertIn('<link rel="stylesheet"', str(css_html))

    def test_admin_js(self):
        js_html = wagtailmodelchoosers_admin_js()
        self.assertIn('wagtailmodelchoosers.js', str(js_html))
        self.assertIn('polyfills.js', str(js_html))
        self.assertIn('<script src=', str(js_html))

    def test_admin_urls(self):
        urls = wagtailmodelchoosers_admin_urls()
        self.assertEqual(len(urls), 3)
        url_names = [u.name for u in urls]
        self.assertIn('wagtailmodelchoosers_api_model', url_names)
        self.assertIn('wagtailmodelchoosers_api_filters', url_names)
        self.assertIn('wagtailmodelchoosers_api_remote_model', url_names)
