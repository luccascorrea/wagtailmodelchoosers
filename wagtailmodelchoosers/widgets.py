import json
import uuid

from django.apps import apps
from django.forms import widgets
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from wagtail.utils.widgets import WidgetWithScript

from .utils import first_non_empty


class ModelChooserWidget(WidgetWithScript, widgets.Input):
    is_hidden = True
    template_name = 'wagtailmodelchoosers/widgets/model_chooser.html'

    def __init__(self, target_model, display, list_display, has_list_filter, adjustable_filter_type, search_fields, chooser, required=True, **kwargs):
        self.required = required
        self._target_model = target_model
        self.label = kwargs.pop('label', self.get_class_name()[1])
        self.display = display
        self.list_display = list_display
        self.has_list_filter = has_list_filter
        self.adjustable_filter_type = adjustable_filter_type
        self.search_fields = search_fields
        self.chooser = chooser
        self.filters = kwargs.pop('filters', [])
        self.thumbnail = kwargs.pop('thumbnail', None)
        self.page_size_param = kwargs.pop('page_size_param', None)
        self.page_size = kwargs.pop('page_size', None)
        self.pk_name = kwargs.pop('pk_name', 'uuid')
        self.translations = kwargs.pop('translations', [])
        self.can_edit = kwargs.pop('can_edit', True)

        super(ModelChooserWidget, self).__init__(**kwargs)

    @cached_property
    def target_model(self):
        if isinstance(self._target_model, str):
            return apps.get_model(self._target_model)

        else:
            return self._target_model

    def get_instance(self, value):
        # helper method for cleanly turning 'value' into an instance object
        if value is None or value == '':
            return None
        try:
            obj = self.target_model.objects.get(pk=value)
            return obj
        except self.target_model.DoesNotExist:
            return None

    def get_instance_and_id(self, model_class, value):
        if value is None:
            return None, None
        elif isinstance(value, model_class):
            return value, value.pk
        else:
            try:
                return model_class.objects.get(pk=value), value
            except model_class.DoesNotExist:
                return None, None

    def value_from_datadict(self, data, files, name):
        result = super(ModelChooserWidget, self).value_from_datadict(data, files, name)

        # Try the id_ method for non-streamfield widgets. Gah!
        if not result:
            result = super(ModelChooserWidget, self).value_from_datadict(data, files, 'id_%s' % name)

        # TODO: Validation should prevent model adding itself as a child
        if result == '':
            return None
        else:
            if isinstance(result, str):
                return result.strip()
            else:
                return result

    def get_endpoint(self):
        app, class_name = self.get_class_name()

        return reverse('wagtailmodelchoosers_api_model', kwargs={"chooser": self.chooser})

    def get_edit_endpoint(self):
        if not self.can_edit:
            return None

        try:
            app, class_name = self.get_class_name()
            return reverse('%s_%s_modeladmin_%s' % (app, class_name.lower(), "edit"), kwargs={"instance_pk": 0})
        except NoReverseMatch:
            return None

    def get_filters_endpoint(self):
        app, class_name = self.get_class_name()

        return reverse('wagtailmodelchoosers_api_filters', kwargs={"chooser": self.chooser})

    def get_internal_value(self, value):
        if hasattr(value, 'pk'):
            if isinstance(value.pk, uuid.UUID):
                return str(value.pk)
            else:
                return value.pk
        return ''

    def get_js_init_data(self, id_, name, value):
        if not isinstance(value, self.target_model):
            value = self.get_instance(value)

        data = {
            'label': self.label,
            'display': self.display,
            'list_display': self.list_display,
            'has_list_filter': self.has_list_filter,
            'adjustable_filter_type': self.adjustable_filter_type,
            'edit_endpoint': self.get_edit_endpoint(),
            'filters_endpoint': self.get_filters_endpoint(),
            'thumbnail': self.thumbnail,
            'pk_name': self.pk_name,
            'required': self.required,
            'initial_display_value': self.get_display_value(value),
            'initial_thumbnail': self.get_thumbnail(value),
            'endpoint': self.get_endpoint(),
        }

        # Only include optional params if they have a value because JS defaults won't work otherwise.
        for attr in ('filters', 'page_size_param', 'page_size', 'translations'):
            val = getattr(self, attr, None)
            if val:
                data[attr] = val

        return data

    def render_js_init(self, id_, name, value):
        data = self.get_js_init_data(id_, name, value)
        return 'wagtailModelChoosers.initModelChooser({id_}, {data})'.format(id_=json.dumps(id_), data=json.dumps(data))

    def get_class_name(self):
        meta = self.target_model._meta
        return meta.app_label, meta.object_name

    def get_display_value(self, instance):
        return first_non_empty(instance, self.display, default='')

    def get_thumbnail(self, instance):
        if instance:
            return getattr(instance, self.thumbnail) if self.thumbnail else None
        return None

    def render_html(self, name, value, attrs):
        if not isinstance(value, self.target_model):
            value = self.get_instance(value)

        context = {
            'widget': self,
            'attrs': attrs,
            'name': name,
            'value': self.get_internal_value(value),
            'instance': value,
        }

        return render_to_string(self.template_name, context)


class RemoteModelChooserWidget(WidgetWithScript, widgets.Input):
    is_hidden = True
    template_name = 'wagtailmodelchoosers/widgets/remote_model_chooser.html'

    def __init__(self, chooser, display, list_display, required=True, **kwargs):
        self.required = required
        self.chooser = chooser
        self.label = kwargs.pop('label', chooser)
        self.display = display
        self.list_display = list_display
        self.filters = kwargs.pop('filters', [])
        self.page_size_param = kwargs.pop('page_size_param', None)
        self.page_size = kwargs.pop('page_size', None)
        self.fields_to_save = kwargs.pop('fields_to_save', None)
        self.pk_name = kwargs.pop('pk_name', 'uuid')
        self.translations = kwargs.pop('translations', [])

        super(RemoteModelChooserWidget, self).__init__(**kwargs)

    def get_endpoint(self):
        return reverse('wagtailmodelchoosers_api_remote_model', args=[self.chooser])

    def get_display_value(self, value):
        return first_non_empty(value, self.display, default='')

    def get_internal_value(self, value):
        return json.dumps(value) if value else ''

    def get_js_init_data(self, id_, name, value):
        data = {
            'label': self.label,
            'display': self.display,
            'list_display': self.list_display,
            'pk_name': self.pk_name,
            'fields_to_save': self.fields_to_save,
            'required': self.required,
            'initial_display_value': self.get_display_value(value),
            'endpoint': self.get_endpoint(),
        }

        # Only include optional params if they have a value because JS defaults won't work otherwise.
        for attr in ('filters', 'page_size_param', 'page_size', 'translations'):
            val = getattr(self, attr, None)
            if val:
                data[attr] = val

        return data

    def render_js_init(self, id_, name, value):
        data = self.get_js_init_data(id_, name, value)
        return 'wagtailModelChoosers.initRemoteModelChooser({id_}, {data})'.format(
            id_=json.dumps(id_), data=json.dumps(data))

    def render_html(self, name, value, attrs):
        context = {
            'widget': self,
            'attrs': attrs,
            'name': name,
            'value': self.get_internal_value(value),
            'instance': value,
        }

        return render_to_string(self.template_name, context)
