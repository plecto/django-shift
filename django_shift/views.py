import json
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse
from django.views.generic import View
from typing import List
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from django_shift.router import APIRouter

from django_shift.resources import APIShift


class APIView(View):
    router = None  # type: APIRouter
    api_version = None  # type: str

    def dispatch(self, request, *args, **kwargs):
        self.api_version = request.GET.get('Api-Version', request.META.get("HTTP_API_VERSION", self.router.get_newest_version()))
        if self.api_version not in self.router.versions:
            return JsonResponse({
                'error': 'Invalid API version %s' % self.api_version
            }, status=400)  # bad request
        response = super(APIView, self).dispatch(request, *args, **kwargs)
        response['Api-Version'] = self.api_version
        if isinstance(response, JsonResponse):
            return response
        return JsonResponse({
            'error': 'unexpected return type'
        })


    def error_reponse(self, error_type, message):
        assert error_type in ['validation_error']
        return JsonResponse({
            'type': error_type,
            'message': message
        })


class APIRoot(APIView):  # List of API Collections
    def get(self, request):

        objects = {
            obj.get_name(): {
                'label': obj.get_label(),
                'name': obj.get_name(),
                'urls': {
                    'create': reverse("shift:api_object_create", args=[obj.get_name()]),
                    'describe': reverse("shift:api_object_describe", args=[obj.get_name()]),
                    'list': reverse("shift:api_object_create", args=[obj.get_name()]),
                    'record_detail': reverse("shift:api_object_get_record", args=[obj.get_name(), '-id-']).replace("-id-", "{id}"),
                }
            } for obj in self.router.get_objects()
        }

        return JsonResponse({
            "objects": objects,
            "api_version": self.api_version

        })


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
            changes = self.router.versions[version]  # type: List[APIShift]
            for change in changes:
                if isinstance(obj, change.resource):
                    for data in data_list:
                        if response:
                            change.migrate_response(data)
                        if request:
                            change.migrate_request(data)


class APIResourceView(MigrationMixin, APIView):
    def get(self, request, **kwargs):
        obj = self.router.get_object(kwargs['object_name'])(request)

        # Permissions

        if not obj.can_view():
            raise PermissionDenied()

        # Fetch data

        data = obj.get_record(kwargs['record_id'])

        # Migrate newest API version to actual version

        self.migrate_data(obj, [data], response=True)

        # Validate

        # if not obj.validator.validate(data):
        #     return self.error_reponse("validation_error", message=obj.validator.errors)  # TODO: Log silently and return incorrect response

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

        # Get the posted data

        data = json.loads(request.body)

        # Migrate old request to newest

        self.migrate_data(obj, [data], request=True)

        if not obj.validator.validate(data):
            return self.error_reponse("validation_error", message=obj.validator.errors)

        # Save record

        data = obj.save_record(data, kwargs['record_id'])

        if not obj.validator.validate(data):
            return self.error_reponse("validation_error", message=obj.validator.errors)  # TODO: Log silently and return incorrect response

        # Migrate back to old format

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


class APICollectionView(MigrationMixin, APIView):

    def get(self, request, **kwargs):
        obj = self.router.get_object(kwargs['object_name'])(request)
        if not obj.can_view():
            raise PermissionDenied()

        try:
            record_list = obj.list_records()
        except ValidationError as e:
            return self.error_reponse(
                'validation_error',
                message=e.message
            )

        self.migrate_data(obj, record_list, response=True)

        # TODO: Pagination. Should it be required?

        def enrich_list_item(itm):
            itm.update({
                "object": obj.name,
                "url": reverse('shift:api_object_get_record', args=[obj.name, itm.get(obj.pk_field)]),
            })
            return itm

        # return
        return JsonResponse({
            'object': 'list',
            # 'has_more': True
            'data': [enrich_list_item(itm) for itm in record_list]
        })

    def post(self, request, **kwargs):
        obj = self.router.get_object(kwargs['object_name'])(request)
        if not obj.can_create():
            raise PermissionDenied()

        # Get posted data
        data = json.loads(request.body)

        # Migrate old request to newest

        self.migrate_data(obj, [data], request=True)

        print(obj.get_schema())

        # Validate request
        if not obj.validator.validate(data):
            return self.error_reponse("validation_error", message=obj.validator.errors)

        data = obj.save_record(data)

        # Migrate back to old format

        self.migrate_data(obj, [data], response=True)

        # Validate response
        if not obj.validator.validate(data):
            return self.error_reponse("validation_error", message=obj.validator.errors)  # TODO: Log silently and return incorrect response

        # return
        return JsonResponse({
            'object': obj.name,
            'data': data
        })


class APIChangeLogView(APIView):
    def get(self, request, **kwargs):
        return JsonResponse({
            version: [
                {
                    "resource": changelog.resource.name,
                    "description": changelog.get_description()
                } for changelog in changelogs
            ] for version, changelogs in self.router.versions.items()
        })
