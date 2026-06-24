from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import SimpleModel

User = get_user_model()

TEST_MODEL_CHOOSERS_OPTIONS = {
    'simple_model_chooser': {
        'content_type': 'core.SimpleModel',
        'display': 'name',
        'list_display': [{'name': 'name', 'label': 'Name'}],
        'list_filter': [
            {'name': 'owner', 'label': 'Owner'},
            {'name': 'is_cool', 'label': 'Is Cool'},
            {'name': 'status_choice', 'label': 'Status'},
        ],
        'search_fields': ['name'],
    },
    'simple_model_no_search_fields': {
        'content_type': 'core.SimpleModel',
        'display': 'name',
        'list_display': [{'name': 'name', 'label': 'Name'}],
    },
    'no_filter_chooser': {
        'content_type': 'core.SimpleModel',
        'display': 'name',
        'list_display': [{'name': 'name', 'label': 'Name'}],
    },
    'custom_manager_chooser': {
        'content_type': 'core.SimpleModel',
        'display': 'name',
        'list_display': [{'name': 'name', 'label': 'Name'}],
        'queryset_manager_method': 'custom_all',
    },
    'custom_manager_with_request_chooser': {
        'content_type': 'core.SimpleModel',
        'display': 'name',
        'list_display': [{'name': 'name', 'label': 'Name'}],
        'queryset_manager_method': 'custom_with_request',
    },
    'remote_chooser': {
        'remote_endpoint': 'http://example.com/api/items',
        'display': 'name',
        'list_display': [{'name': 'name', 'label': 'Name'}],
        'remote_query_page_size_key': 'limit',
        'remote_query_page_key': 'p',
        'remote_query_search_key': 'q',
        'remote_response_data_key': 'items',
        'remote_response_page_key': 'current_page',
        'filters': [
            {'field': 'category', 'label': 'Category'},
        ],
    }
}


@override_settings(MODEL_CHOOSERS_OPTIONS=TEST_MODEL_CHOOSERS_OPTIONS)
class TestViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser(username='admin', email='admin@example.com', password='password')
        cls.user2 = User.objects.create_user(username='editor', email='editor@example.com', password='password')

        cls.model_cool_draft = SimpleModel.objects.create(
            name="cool draft model",
            is_cool=True,
            status_choice="draft",
            owner=cls.user,
        )

        cls.model_normal_published = SimpleModel.objects.create(
            name="normal published model",
            is_cool=False,
            status_choice="published",
            owner=cls.user2,
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_filter_view_list_filter_defined(self):
        url = reverse('wagtailmodelchoosers_api_filters', kwargs={'chooser': 'simple_model_chooser'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # We expect a list with three filters: owner, is_cool, status_choice
        self.assertEqual(len(data), 3)

        # Check owner filter (RelatedField)
        owner_filter = next(f for f in data if f['name'] == 'owner')
        self.assertEqual(owner_filter['label'], 'Owner')
        # All + 2 users
        self.assertEqual(len(owner_filter['options']), 3)
        self.assertEqual(owner_filter['options'][0], {'label': 'All', 'value': None, 'selected': True})

        # Check is_cool filter (BooleanField)
        is_cool_filter = next(f for f in data if f['name'] == 'is_cool')
        self.assertEqual(is_cool_filter['label'], 'Is Cool')
        self.assertEqual(is_cool_filter['options'], [
            {'label': 'All', 'value': None, 'selected': True},
            {'label': 'Yes', 'value': 'True'},
            {'label': 'No', 'value': 'False'},
        ])

        # Check status_choice filter (Choices field)
        status_filter = next(f for f in data if f['name'] == 'status_choice')
        self.assertEqual(status_filter['label'], 'Status')
        self.assertEqual(status_filter['options'], [
            {'label': 'All', 'value': None, 'selected': True},
            {'label': 'Draft', 'value': 'draft'},
            {'label': 'Published', 'value': 'published'},
        ])

    def test_filter_view_no_list_filter(self):
        url = reverse('wagtailmodelchoosers_api_filters', kwargs={'chooser': 'no_filter_chooser'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {})

    def test_model_view_unauthenticated(self):
        self.client.logout()
        url = reverse('wagtailmodelchoosers_api_model', kwargs={'chooser': 'simple_model_chooser'})
        response = self.client.get(url)
        # Wagtail admin routing redirects unauthenticated users to the admin login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_model_view_list_all(self):
        url = reverse('wagtailmodelchoosers_api_model', kwargs={'chooser': 'simple_model_chooser'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data['count'], 2)
        results = data['results']
        self.assertEqual(len(results), 2)
        names = {m['name'] for m in results}
        self.assertEqual(names, {"cool draft model", "normal published model"})

    def test_model_view_search_with_search_fields(self):
        url = reverse('wagtailmodelchoosers_api_model', kwargs={'chooser': 'simple_model_chooser'})
        response = self.client.get(url, {'search': 'cool'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['name'], "cool draft model")

    def test_model_view_search_without_search_fields(self):
        url = reverse('wagtailmodelchoosers_api_model', kwargs={'chooser': 'simple_model_no_search_fields'})
        response = self.client.get(url, {'search': 'normal'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['name'], "normal published model")

    def test_model_view_filter_exclusive(self):
        url = reverse('wagtailmodelchoosers_api_model', kwargs={'chooser': 'simple_model_chooser'})

        # Test single filter
        response = self.client.get(url, {'is_cool': 'True'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['name'], "cool draft model")

        # Test multiple exclusive filters (AND) - should return 0 results
        response = self.client.get(url, {'is_cool': 'True', 'status_choice': 'published'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

    def test_model_view_filter_inclusive(self):
        url = reverse('wagtailmodelchoosers_api_model', kwargs={'chooser': 'simple_model_chooser'})

        # Test multiple inclusive filters (OR) - should return both
        response = self.client.get(url, {
            'is_cool': 'True',
            'status_choice': 'published',
            'filter_type': 'inclusive'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)

    def test_model_view_queryset_manager_method_no_args(self):
        url = reverse('wagtailmodelchoosers_api_model', kwargs={'chooser': 'custom_manager_chooser'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['name'], "cool draft model")

    def test_model_view_queryset_manager_method_with_request(self):
        url = reverse('wagtailmodelchoosers_api_model', kwargs={'chooser': 'custom_manager_with_request_chooser'})

        # Without special GET param, should return both models
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)

        # With special GET param, should return 0 models
        response = self.client.get(url, {'req_filter': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

    @patch('wagtailmodelchoosers.views.requests.get')
    def test_remote_resource_view_list_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'items': [{'id': 1, 'name': 'Item 1'}, {'id': 2, 'name': 'Item 2'}],
            'current_page': 3,
            'num_pages': 5,
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        url = reverse('wagtailmodelchoosers_api_remote_model', kwargs={'chooser': 'remote_chooser'})
        response = self.client.get(url, {
            'page': 3,
            'page_size': 20,
            'search': 'testing',
            'category': 'books',
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check mapped parameters sent to requests.get
        mock_get.assert_called_once_with('http://example.com/api/items', {
            'p': '3',
            'limit': '20',
            'q': 'testing',
            'category': 'books',
        })

        # Check mapped response values
        self.assertEqual(data, {
            'results': [{'id': 1, 'name': 'Item 1'}, {'id': 2, 'name': 'Item 2'}],
            'page': 3,
            'num_pages': 5,
        })

    @patch('wagtailmodelchoosers.views.requests.get')
    def test_remote_resource_view_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404

        from requests.exceptions import HTTPError
        http_error = HTTPError("404 Client Error", response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response

        url = reverse('wagtailmodelchoosers_api_remote_model', kwargs={'chooser': 'remote_chooser'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['status_code'], 404)
        self.assertIn("404 Client Error", data['detail'])
