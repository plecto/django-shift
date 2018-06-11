from collections import OrderedDict

from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from typing import Type, Sequence

from django_shift.docs.views import DocumentationRoot
from django_shift.views import APIRoot, APIChangeLogView, APIObjectCreate, APIObjectDescribe, APIObjectGetRecord
from django_shift.resources import APIObject


class APIRouter(object):
    def __init__(self, versions=None):
        self.objects = {}
        self.versions = OrderedDict(
            sorted(versions.items(), key=lambda x: x[0], reverse=True) or {}
        )

    def get_newest_version(self):
        return list(self.versions.keys())[0]

    def add_object(self, obj):
        if not obj.name:
            raise NotImplemented("Please set a name on your collection to be used in the URL")
        self.objects[obj.name] = obj

    def get_objects(self):
        # type: () -> Sequence[Type[APIObject]]
        return self.objects.values()

    def get_object(self, name):
        # type: (str) -> Type[APIObject]
        return self.objects[name]

    def urls(self):
        return ([
            url('^$', APIRoot.as_view(router=self), name="api_root"),
            url('^changelog/$', APIChangeLogView.as_view(router=self), name="api_changelog"),
            url('^(?P<object_name>([\w\- ]+))/$', csrf_exempt(APIObjectCreate.as_view(router=self)), name="api_object_create"),
            url('^(?P<object_name>([\w\- ]+))/describe/$', APIObjectDescribe.as_view(router=self), name="api_object_describe"),
            url('^(?P<object_name>([\w\- ]+))/(?P<record_id>([\w\- ]+))/$', csrf_exempt(APIObjectGetRecord.as_view(router=self)), name="api_object_get_record"),
        ], 'shift', 'shift')

    def documentation_urls(self):
        return ([
            url('^$', DocumentationRoot.as_view(router=self), name="docs_root"),
        ], 'shift-docs', 'shift-docs')