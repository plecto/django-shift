import json
from collections import Iterable
from uuid import uuid4

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404


class ModelSerializeMixin(object):

    @staticmethod
    def serialize(qs, fields=None):
        if not isinstance(qs, Iterable):
            qs = [qs]
        return serializers.serialize('json', qs, fields=fields)

    @classmethod
    def list_records(cls, fields=None):
        qs = cls.objects.all()
        return json.loads(cls.serialize(qs, fields=fields))

    @classmethod
    def get_record(cls, uuid, fields=None):
        try:
            record = cls.objects.get(uuid=uuid)
            serialized_record = cls.serialize(record, fields=fields)
            serialized_record_json = json.loads(serialized_record)
            return serialized_record_json[0]
        except ObjectDoesNotExist:
            return Http404

    @classmethod
    def save_record(cls, data, uuid=None):
        if type(data) == str:
            data = json.loads(data)

        if uuid:  # If we are updating an existing record
            existing_record = cls.get_record(uuid)
            existing_record['fields'].update(data)
            save_data = [existing_record]
        else:  # If we are creating a new record
            data['uuid'] = str(uuid4())
            save_data = [
                {'fields': data,
                 'model': '{}.{}'.format(cls._meta.app_label, cls._meta.model_name),
                 }
            ]
        for obj in serializers.deserialize('json', json.dumps(save_data)):
            obj.save()

    @classmethod
    def delete_record(cls, uuid=None):
        try:
            obj = cls.objects.get(uuid=uuid)
            obj.delete()
        except ObjectDoesNotExist:
            return Http404
