# wagtailmodelchoosers

A customizable and generic model chooser modal for the Wagtail admin interface, allowing content editors to pick any Django model instance (such as users, categories, or cities) or remote resources from an external API, instead of being limited to snippets or pages.

*This project is a modified fork modernized to support **Wagtail 3.0+, 4.0+, 4.1+, 4.2+ (LTS), 5.0+, 5.1+, and 5.2+ (including 5.2.8 LTS)**, **Django 4.0+, 4.2+ (LTS), and 5.0+**, and **Python 3.12+** with extensive automated test coverage.*

---

## Key Features & Upgrades in this Fork

* **Wagtail 3.0+, 4.0+, 4.1+, 4.2+, 5.0+, 5.1+, and 5.2+ (5.2.8 LTS) Compatibility**: Fully supports modern Wagtail modular namespaces (e.g. `wagtail.models`, `wagtail.blocks`, `wagtail.admin.panels`, `wagtail.hooks`), `read_only` and `attrs` panel options, `SnippetViewSet` and generic `ModelViewSet` URL resolution, dark mode theming and semantic CSS tokens, `ReferenceIndex` reference tracking, Willow image pipelines, and new panel architectures (`TitleFieldPanel`, `icon`, `clone_kwargs`) while preserving backwards-compatible fallbacks for Wagtail 2.x projects.
* **Django 4.0+ & 5.0+ Compatibility**: Handles routing updates (replaces deprecated `url()` imports with `re_path()`) and modern Django template escaping and queryset standards.
* **Python 3.12+ Compatibility**: Resolves runtime `AttributeError` by replacing obsolete collections imports with `collections.abc.Iterable`.
* **Automatic Primary Key Resolution**: The `pk_name` setting dynamically falls back to the model's actual primary key (`id`, `uuid`, etc.) rather than defaulting unconditionally to `'uuid'`.
* **Extensive Test Coverage**: Automated test suite expanded to **100 tests** covering 100% of major logic paths, achieving **86% overall coverage** (>95% for views and >94% for utility helpers).

---

## Installation

Install the package via `pip`:

```bash
pip install wagtailmodelchoosers
```

Then add `wagtailmodelchoosers` to your Django `INSTALLED_APPS` setting:

```python
INSTALLED_APPS = [
    # ...
    'wagtailmodelchoosers',
    # ...
]
```

---

## Configuration

Configure your choosers in your Django settings file under the `MODEL_CHOOSERS_OPTIONS` dictionary:

```python
MODEL_CHOOSERS_OPTIONS = {
    # Chooser for a local Django model (e.g. a category model)
    'category_chooser': {
        'content_type': 'core.Category',
        'display': 'name',
        'list_display': [
            {'name': 'name', 'label': 'Name'},
            {'name': 'slug', 'label': 'Slug'},
        ],
        'list_filter': [
            {'name': 'is_active', 'label': 'Active'},
        ],
        'search_fields': ['name', 'description'],
        'queryset_manager_method': 'all',  # Optional manager method to customize querysets
    },

    # Chooser for a remote API resource
    'remote_book_chooser': {
        'remote_endpoint': 'https://api.example.com/books/',
        'display': 'title',
        'list_display': [
            {'name': 'title', 'label': 'Title'},
            {'name': 'author', 'label': 'Author'},
        ],
        'remote_query_page_size_key': 'limit',
        'remote_query_page_key': 'page',
        'remote_query_search_key': 'q',
        'remote_response_data_key': 'results',
        'remote_response_page_key': 'current_page',
        'filters': [
            {'field': 'genre', 'label': 'Genre'},
        ],
    }
}
```

### Configuration Options Reference

* `content_type` (Local only): The Django `'app_label.ModelName'` format of the target model.
* `remote_endpoint` (Remote only): The HTTP API endpoint URL to fetch items from.
* `display`: The field (or list of fields) used to display the selected item's label.
* `list_display`: List of field dictionaries `{'name': 'field_name', 'label': 'Label'}` to show as table columns in the modal list.
* `list_filter` (Local only): List of fields to generate filter dropdowns (supports related/foreign key fields, booleans, and choice fields).
* `search_fields` (Local only): Model fields to query when typing in the search bar. Defaults to searching all text fields if empty.
* `queryset_manager_method` (Local only): Custom model manager method name to scope the queryset. Supports methods taking a `request` object.
* `pk_name`: The field name of the primary key (automatically resolved to the model's actual primary key for local models).

---

## Usage

### 1. In Page or Model Panels

Import the panels and use them in your edit handlers:

```python
from django.db import models
from wagtail.models import Page
from wagtailmodelchoosers.edit_handlers import ModelChooserPanel, RemoteModelChooserPanel

class ArticlePage(Page):
    category = models.ForeignKey(
        'core.Category',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    
    # Store remote resources as JSON fields or text fields
    remote_book_data = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        ModelChooserPanel('category', chooser='category_chooser'),
        RemoteModelChooserPanel('remote_book_data', chooser='remote_book_chooser'),
    ]
```

### 2. In StreamFields (Blocks)

Import the blocks and use them inside `StreamField` definitions:

```python
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtailmodelchoosers.blocks import ModelChooserBlock, RemoteModelChooserBlock

class BlogPage(Page):
    body = StreamField([
        ('category_link', ModelChooserBlock(chooser='category_chooser')),
        ('book_preview', RemoteModelChooserBlock(chooser='remote_book_chooser')),
    ], use_json_field=True)
```

---

## Development & Running Tests

### Set Up Environment

1. Clone the repository and initialize the virtual environment:
   ```bash
   git clone <repo-url> wagtailmodelchoosers
   cd wagtailmodelchoosers
   virtualenv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -e .[testing,docs] -U
   ```

### Run Tests

Execute the test suite directly:

```bash
python ./runtests.py
```

### Run Coverage Reports

Measure code coverage using `coverage`:

```bash
python -m coverage run ./runtests.py
python -m coverage report
```

### Running the Test Application Locally

To test the admin interface manually in your browser, a test application is located under `tests/testapp`. 

1. Prepare directories and run database migrations:
   ```bash
   mkdir -p tests/testapp/var
   python ./tests/testapp/manage.py migrate
   ```
2. Create an admin user:
   ```bash
   python ./tests/testapp/manage.py createsuperuser
   ```
3. Start the development server:
   ```bash
   python ./tests/testapp/manage.py runserver
   ```
4. Navigate to `http://127.0.0.1:8000/admin/`, create a **Simple Page**, and test the chooser modals in the field panels.
