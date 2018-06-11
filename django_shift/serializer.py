import json
from collections import Iterable

from typing import Sequence
from uuid import uuid4

from django.core.serializers.python import Serializer, Deserializer
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.db.models import Model


class ModelSerializeMixin(object):
    model = None   # type: Model
    fields = None  # type: Sequence[str]

    def get_fields(self):
        return [field.name for field in self.model._meta.fields]

    def get_queryset(self):
        return self.model.objects.all()

    @staticmethod
    def serialize(obj, fields=None):
        serializer = Serializer()
        if not isinstance(obj, Iterable):
            obj = [obj]
        return serializer.serialize(obj, fields=fields)

    def list_records(self, fields=None):
        return [self.serialize(obj, fields=fields) for obj in self.get_queryset()]

    def get_record(self, uuid, fields=None):
        try:
            record = self.get_queryset().get(uuid=uuid)
            serialized_record = self.serialize(record, fields=fields)
            serialized_record_json = json.loads(serialized_record)
            return serialized_record_json[0]
        except ObjectDoesNotExist:
            return Http404

    def save_record(self, data, pk=None):
        if type(data) == str:
            data = json.loads(data)

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
            obj = self.get_queryset().get(pk=pk)
            obj.delete()
        except ObjectDoesNotExist:
            return Http404
