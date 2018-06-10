import json
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.generic import View
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from django_shift.router import APIRouter


class APIView(View):
    router = None  # type: APIRouter

    def dispatch(self, request, *args, **kwargs):
        self.api_version = request.GET.get('Api-Version', request.META.get("HTTP_API_VERSION", self.router.get_newest_version()))
        if self.api_version not in self.router.versions:
            return JsonResponse({
                'error': 'Invalid API version %s' % self.api_version
            }, status=400)  # bad request
        response = super(APIView, self).dispatch(request, *args, **kwargs)
        response['Api-Version'] = self.api_version
        if isinstance(response, JsonResponse):
            # if request.META['CONTENT_TYPE'] == 'text/plain':
            #
            #     # We can't pass args to the json encoder because it's already encoded so we will (for now) decode it
            #     # and re-encode it with indent. Also - let's order it so it's nicer to read when we are at it
            #
            #     decoded = json.loads(response.content)
            #     indented = json.dumps(decoded, indent=4)
            #
            #     return render_to_response("django_shift/api_view.html", context={
            #         'request': request,
            #         'response': response,
            #         'json': highlight(indented, JSONLexer(), URLHtmlFormatter())
            #     })
            return response
        return JsonResponse({
            'error': 'unexpected return type'
        })


class APIRoot(APIView):  # List of API Collections
    def get(self, request):

        return JsonResponse({
                obj.get_name(): {
                    'deletable': obj.supports_delete(),
                    'label': obj.get_label(),
                    'name': obj.get_name(),
                    'updateable': obj.supports_update(),  # TODO: How to spell this
                    'urls': {
                        'create': reverse("api_object_create", args=[obj.get_name()]),
                        'describe': reverse("api_object_describe", args=[obj.get_name()]),
                        'list': reverse("api_object_create", args=[obj.get_name()]),
                        'record_detail': reverse("api_object_get_record", args=[obj.get_name(), '-id-']).replace("-id-", "{id}"),
                    }
                } for obj in self.router.get_objects()
            }
         )


class APIObjectDescribe(APIView):
    def get(self, request, **kwargs):
        obj = self.router.get_object(kwargs['object_name'])(request)

        return JsonResponse({
            'fields': obj.get_fields(),
            'label': obj.get_label(),
            'name': obj.get_name(),
        })


class MigrationMixin:
    router = None  # type: APIRouter
    api_version = None  # type: str

    def migrate_data(self, obj, data_list, response=False, request=False):
        versions = list(self.router.versions.keys())
        versions_behind = versions.index(self.api_version)
        for version in versions[0:versions_behind]:
            changes = self.router.versions[version]
            for change in changes:
                if isinstance(obj, change.object):
                    for data in data_list:
                        if response:
                            change.migrate_response(data)
                        if request:
                            change.migrate_request(data)


class APIObjectGetRecord(MigrationMixin, APIView):
    def get(self, request, **kwargs):
        obj = self.router.get_object(kwargs['object_name'])(request)
        if not obj.can_view():
            raise PermissionDenied()

        data = obj.get_record(kwargs['record_id'])

        self.migrate_data(obj, [data], response=True)

        # return
        return JsonResponse({
            'object': obj.name,
            'data': data
        })

    def put(self, request, **kwargs):
        # TODO: Support for alternative keys, e.g. external ID
        obj = self.router.get_object(kwargs['object_name'])(request)

        # TODO: Show this work for create as well? https://en.wikipedia.org/wiki/Representational_state_transfer
        if not obj.can_update():
            raise PermissionDenied()

        data = json.loads(request.body)

        self.migrate_data(obj, [data], request=True)

        data = obj.save_record(data, kwargs['record_id'])

        self.migrate_data(obj, [data], response=True)

        # return
        return JsonResponse({
            'object': obj.name,
            'data': data
        })

    def patch(self, *args, **kwargs):
        return self.put(*args, **kwargs)

    def delete(self, request, **kwargs):
        # TODO: Support for alternative keys, e.g. external ID
        obj = self.router.get_object(kwargs['object_name'])(request)

        if not obj.can_delete():
            raise PermissionDenied()

        data = obj.delete_record(kwargs['record_id'])

        self.migrate_data(obj, [data], response=True)

        # return
        return JsonResponse({
            'object': obj.name,
            'data': data
        })


class APIObjectCreate(MigrationMixin, APIView):

    def get(self, request, **kwargs):
        obj = self.router.get_object(kwargs['object_name'])(request)
        if not obj.can_view():
            raise PermissionDenied()

        record_list = obj.list_records()

        self.migrate_data(obj, record_list, response=True)

        # return
        return JsonResponse({
            'object': 'list',
            'data': record_list
        })

    def post(self, request, **kwargs):
        obj = self.router.get_object(kwargs['object_name'])(request)
        if not obj.can_create():
            raise PermissionDenied()

        data = json.loads(request.body)

        self.migrate_data(obj, [data], request=True)

        data = obj.save_record(request, data)

        self.migrate_data(obj, [data], response=True)

        # return
        return JsonResponse({
            'object': obj.name,
            'data': data
        })


class APIChangeLogView(APIView):
    def get(self, request, **kwargs):
        return JsonResponse({
            version: [
                changelog.description for changelog in changelogs
            ] for version, changelogs in self.router.versions.items()
        })
#
#
#
# class APICollection(object):
#     name = None
#
#     def __init__(self, request):
#         self.request = request
#         self.objects = {}
#
#     def add_object(self, obj):
#         self.objects[obj.get_name()] = obj
#
#     def get_objects(self):
#         return self.objects.values()
#
#
