from django.core.handlers.wsgi import WSGIRequest
from six import with_metaclass
from typing import Optional, List, Dict


class APIObject(object):
    name = None  # type: Optional[str]
    label = None  # type: Optional[str]

    def __init__(self, request, *args, **kwargs):
        # type: (WSGIRequest, list, dict) -> None
        self.request = request

    @classmethod
    def get_label(cls):
        # type: () -> str
        if cls.label:
            return cls.label

    @classmethod
    def get_name(cls):
        # type: () -> str
        if cls.name:
            return cls.name
        raise NotImplementedError("Please define get_name or name on %s" % cls)

    @classmethod
    def supports_delete(cls):
        # type: () -> bool
        return False

    @classmethod
    def supports_update(cls):
        # type: () -> bool
        return False

    def can_view(self):
        # type: () -> bool
        return False

    def can_delete(self):
        # type: () -> bool
        return False

    def can_create(self):
        # type: () -> bool
        return False

    def can_update(self):
        # type: () -> bool
        return False

    def get_fields(self):
        # type: () -> List[Dict[str, dict]]
        return [
            # {
            #     field.name: {
            #         'label': field.name,
            #     }
            # } for field in obj.datasourceextrafield_set.all()

        ]

    def get_record(self, _id):
        # type: (str) -> dict
        raise NotImplementedError()

    def list_records(self):
        # type: () -> List[dict]
        raise NotImplementedError()

    def save_record(self, data, _id=None):
        # type: (dict, Optional[str]) -> dict
        raise NotImplementedError()

    def delete_record(self, _id):
        # TODO: What should delete return?
        raise NotImplementedError()


class ShiftMeta(type):
    pass
    # def __new__(mcs, name, bases, attrs):
    #     klass = type.__new__(mcs, name, bases, attrs)  # type: APIShift
    #     if not klass.resource:
    #         raise Exception("Please set the `resource` attribute on APIShift")
    #     return klass


class APIShift(with_metaclass(ShiftMeta, object)):
    description = None  # type: str
    resource = None  # type: APIObject

    @classmethod
    def get_description(cls):
        if cls.description:
            return cls.description
        if cls.__doc__:
            return cls.__doc__.strip()
        return 'N/A'

    @staticmethod
    def migrate_response(data):
        # type: (dict) -> dict
        raise NotImplementedError()

    @staticmethod
    def migrate_request(data):
        # type: (dict) -> dict
        raise NotImplementedError()