from wagtail.admin.edit_handlers import BaseChooserPanel
from wagtail.utils.decorators import cached_classmethod

from wagtailmodelchoosers.utils import flatten, get_chooser_options
from wagtailmodelchoosers.widgets import ModelChooserWidget, RemoteModelChooserWidget
from wagtail.admin.compare import M2MFieldComparison, FieldComparison, ChildRelationComparison
from wagtail.admin.edit_handlers import InlinePanel
from wagtail.admin import compare
from wagtailmodelchoosers.utils import curry
from django.utils.html import escape
from django.db import models
import collections

class InlineModelPanel(InlinePanel):

    def get_comparison(self):
        if self.is_relation:
            field = self.model._meta.get_field(self.relation_name.replace("_set", ""))
            field.verbose_name = self.heading
        else:
            field = self.model._meta.get_field(self.relation_name)

        field_comparisons = []

        for panel in self.get_panel_definitions():
            field_comparisons.extend(panel.bind_to_model(self.db_field.related_model).get_comparison())

        return [curry(ChildModelComparison, field, field_comparisons)]

    def on_model_bound(self):
        # super().on_model_bound()
        try:
            related = getattr(self.model, self.relation_name).rel
        except AttributeError:
            related = getattr(self.model, self.relation_name + "_set").rel
            related.related_name = self.relation_name + "_set"

        self.db_field = related


class ChildModelComparison(ChildRelationComparison):

    def __init__(self, field, field_comparisons, obj_a, obj_b):
        self.field = field
        self.field_comparisons = field_comparisons
        accessor = field.get_accessor_name()
        self.val_a = getattr(obj_a, accessor).all()
        self.val_b = getattr(obj_b, accessor).all()

class ModelComparison(M2MFieldComparison):
    def __init__(self, field, obj_a, obj_b):
        if isinstance(field, models.ManyToOneRel):
            self.field = field
            accessor = field.get_accessor_name()
            self.val_a = getattr(obj_a, accessor).all()
            self.val_b = getattr(obj_b, accessor).all()
        else:
            super().__init__(field, obj_a, obj_b)

    def get_item_display(self, item):
        if isinstance(self.val_a, collections.Iterable):
            return str(item)
        else:
            return str(self.field.model.objects.get(id=item))

    def get_items(self):
        if isinstance(self.val_a, collections.Iterable):
            return super().get_items()
        else:
            return self.val_a, self.val_b

    def htmldiff(self):
        # Get tags
        items_a, items_b = self.get_items()
        if isinstance(items_a, collections.Iterable):
            return super().htmldiff()
        else:
            if items_a == items_b:
                return escape(self.get_item_display(items_a))
            else:
                return compare.TextDiff([('deletion', self.get_item_display(items_a)), ('addition', self.get_item_display(items_b))]).to_html()
class ModelChooserPanel(BaseChooserPanel):
    object_type_name = 'model'


    def __init__(self, field_name, chooser, **kwargs):
        options = get_chooser_options(chooser)
        options.update(kwargs)

        self.field_name = field_name
        self.chooser = chooser
        self.label = options.pop('label', chooser)
        self.display = options.pop('display', 'title')
        self.list_display = options.pop('list_display', list(flatten([self.display])))
        self.adjustable_filter_type = options.pop('adjustable_filter_type', False)
        self.search_fields = options.pop("search_fields", [])
        self.has_list_filter = options.pop('list_filter', None) is not None
        self.thumbnail = options.pop('thumbnail', None)
        self.filters = options.pop('filters', [])
        self.page_size_param = options.pop('page_size_param', None)
        self.page_size = options.pop('page_size', None)
        self.pk_name = options.pop('pk_name', 'uuid')
        self.translations = options.pop('translations', [])

        options.pop("content_type", None)
        options.pop("queryset_manager_method", None)

        super().__init__(field_name, **options)

    def target_model(self):
        return self.model._meta.get_field(self.field_name).related_model

    def get_required(self):
        null = self.model._meta.get_field(self.field_name).null
        return not null

    def widget_overrides(self):
        return {
            self.field_name: ModelChooserWidget(
                self.target_model(),
                required=self.get_required(),
                chooser=self.chooser,
                label=self.label,
                display=self.display,
                list_display=self.list_display,
                has_list_filter=self.has_list_filter,
                adjustable_filter_type=self.adjustable_filter_type,
                search_fields=self.search_fields,
                filters=self.filters,
                page_size_param=self.page_size_param,
                page_size=self.page_size,
                pk_name=self.pk_name,
                translations=self.translations,
                thumbnail=self.thumbnail,
            )
        }

    def clone(self):
        return self.__class__(
            field_name=self.field_name,
            widget=self.widget if hasattr(self, 'widget') else None,
            heading=self.heading,
            classname=self.classname,
            help_text=self.help_text,
            chooser=self.chooser,
        )


class BaseRemoteModelChooserPanel(BaseChooserPanel):
    object_type_name = 'remote_model'

    @classmethod
    def get_required(cls):
        blank = cls.model._meta.get_field(cls.field_name).blank
        return not blank

    @classmethod
    def widget_overrides(cls):
        return {
            cls.field_name: RemoteModelChooserWidget(
                cls.chooser,
                required=cls.get_required(),
                label=cls.label,
                display=cls.display,
                list_display=cls.list_display,
                filters=cls.filters,
                page_size_param=cls.page_size_param,
                page_size=cls.page_size,
                fields_to_save=cls.fields_to_save,
                pk_name=cls.pk_name,
                translations=cls.translations,
            )
        }


class RemoteModelChooserPanel(BaseChooserPanel):
    object_type_name = 'remote_model'

    def __init__(self, field_name, chooser, **kwargs):
        options = get_chooser_options(chooser)
        options.update(kwargs)

        self.field_name = field_name
        self.chooser = chooser
        self.label = options.pop('label', chooser)
        self.display = options.pop('display', 'title')
        self.list_display = options.pop('list_display', list(flatten([self.display])))
        self.filters = options.pop('filters', [])
        self.page_size_param = options.pop('page_size_param', None)
        self.page_size = options.pop('page_size', None)
        self.fields_to_save = options.pop('fields_to_save', None)
        self.pk_name = options.pop('pk_name', 'uuid')
        self.translations = options.pop('translations', [])

        super().__init__(field_name, **options)

    def get_required(self):
        blank = self.model._meta.get_field(self.field_name).blank
        return not blank

    def widget_overrides(self):
        return {
            self.field_name: RemoteModelChooserWidget(
                self.chooser,
                required=self.get_required(),
                label=self.label,
                display=self.display,
                list_display=self.list_display,
                filters=self.filters,
                page_size_param=self.page_size_param,
                page_size=self.page_size,
                fields_to_save=self.fields_to_save,
                pk_name=self.pk_name,
                translations=self.translations,
            )
        }