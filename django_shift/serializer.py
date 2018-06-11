import json
from collections import Iterable

from typing import Sequence
from uuid import uuid4

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.db.models import Model


class ModelSerializeMixin(object):

    model = None   # type: Model
    fields = None  # type: Sequence[str]

    def get_fields(self):
        pass

    def get_queryset(self):
        return self.model.objects.all()

    @staticmethod
    def serialize(qs, fields=None):
        if not isinstance(qs, Iterable):
            qs = [qs]
        return serializers.serialize('json', qs, fields=fields)

    def list_records(self, fields=None):
        return [json.loads(self.serialize(obj))[0] for obj in self.get_queryset()]
        # return json.loads(self.serialize(self.get_queryset(), fields=fields))

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
        for obj in serializers.deserialize('json', json.dumps(save_data)):
            obj.save()

    def delete_record(self, pk):
        try:
            obj = self.get_queryset().get(pk=pk)
            obj.delete()
        except ObjectDoesNotExist:
            return Http404
