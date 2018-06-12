import json
from collections import Iterable

from typing import Sequence
from uuid import uuid4

from django.core.serializers.python import Serializer, Deserializer
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.db.models import Model
from django.shortcuts import get_object_or_404

from django_shift.resources import APIResource

from django.db import models

serializer = Serializer()

DJANGO_FIELD_TO_CERBERUS = {
    'default': 'string',
    models.BooleanField: 'boolean'

}


class APIModelResource(APIResource):
    model = None   # type: Model
    fields = None  # type: Sequence[str]

    def __init__(self, *args, **kwargs):
        super(APIModelResource, self).__init__(*args, **kwargs)
        if not self.pk_field:
            self.pk_field = self.model._meta.pk.name

    def get_schema(cls):
        return {
            field.name: {
                'type': DJANGO_FIELD_TO_CERBERUS.get(type(field), DJANGO_FIELD_TO_CERBERUS['default'])
            } for field in cls.model._meta.fields if field.name in cls.fields
        }

    def get_queryset(self):
        return self.model.objects.all()

    def get_object(self, pk):
        return get_object_or_404(self.get_queryset(), **{
            self.pk_field: pk
        })

    def serialize(self, obj):
        response = serializer.serialize([obj], fields=self.fields)[0]
        data = response['fields']

        # add pk's to the 'fields' as django always take them out of it
        if 'pk' in self.fields:
            data['pk'] = response['pk']
        if self.model._meta.pk.name in self.fields:
            data[self.model._meta.pk.name] = response['pk']

        return data

    def list_records(self):
        return [self.serialize(obj) for obj in self.get_queryset()]

    def get_record(self, pk):
        return self.serialize(self.get_object(pk))

    def save_record(self, data, pk=None):
        if pk:  # If we are updating an existing record
            existing_record = self.get_record(pk)
            existing_record['fields'].update(data)
            save_data = [existing_record]
        else:  # If we are creating a new record
            data['uuid'] = str(uuid4())
            save_data = [{
                    'fields': data,
                    'model': '{}.{}'.format(self.model._meta.app_label, self.model._meta.model_name),
            }]
        for obj in Deserializer(save_data):
            obj.save()

    def delete_record(self, pk):
        try:
            self.get_object(pk).delete()
        except ObjectDoesNotExist:
            return Http404
