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

__all__ = ['SimplePage', 'SimpleModel']


from wagtailmodelchoosers.edit_handlers import ModelChooserPanel


class SimplePage(Page):
    content = models.TextField()
    selected_user = models.ForeignKey(
        'auth.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('content'),
        ModelChooserPanel('selected_user', chooser='user_chooser'),
    ]



class SimpleModelManager(models.Manager):
    def custom_all(self):
        return self.filter(name__contains='cool')

    def custom_with_request(self, request):
        if request.GET.get('req_filter') == '1':
            return self.filter(name__contains='request')
        return self.all()


class SimpleModel(models.Model):
    name = models.CharField(max_length=255)
    is_cool = models.BooleanField(default=True)
    status_choice = models.CharField(
        max_length=20,
        choices=[('draft', 'Draft'), ('published', 'Published')],
        default='draft'
    )
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)

    objects = SimpleModelManager()

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name
