from __future__ import absolute_import, unicode_literals

from django.db import models

try:
    from wagtail.admin.panels import FieldPanel
except ImportError:
    from wagtail.admin.edit_handlers import FieldPanel

try:
    from wagtail.models import Page
except ImportError:
    from wagtail.core.models import Page

__all__ = ['SimplePage']


class SimplePage(Page):
    content = models.TextField()

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('content'),
    ]
