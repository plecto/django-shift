from django.core.handlers.wsgi import WSGIRequest
from typing import Optional, List


class APIObject(object):
    name = None  # type: Optional[str]

    def __init__(self, request, *args, **kwargs):
        # type: (WSGIRequest, list, dict) -> None
        self.request = request

    @classmethod
    def get_label(self):
        pass

    @classmethod
    def get_name(cls):
        if cls.name:
            return cls.name
        raise NotImplementedError("Please define get_name or name on %s" % cls)

    @classmethod
    def supports_delete(self):
        pass

    @classmethod
    def supports_update(self):
        pass

    def can_view(self):
        pass

    def can_delete(self):
        pass

    def can_create(self):
        pass

    def can_update(self):
        pass

    def get_fields(self):
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
        raise NotImplementedError()


class APIVersionChange(object):
    description = None  # type: str
    object = None  # type: APIObject

    @staticmethod
    def migrate_response(data):
        # type: (dict) -> dict
        raise NotImplementedError()

    @staticmethod
    def migrate_request(data):
        # type: (dict) -> dict
        raise NotImplementedError()