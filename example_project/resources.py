from django.contrib.auth.models import User

from django_shift.resources import APIObject
from django_shift.serializer import ModelSerializeMixin


class UserObject(APIObject):
    name = 'user'
    label = 'User'

    def can_view(self):
        return True

    def list_records(self):
        return [{
            "username": user.username
        } for user in User.objects.all()]

    def get_record(self, _id):
        return {}


class UserResource(ModelSerializeMixin, APIObject):
    model = User
    name = 'user_v2'
    fields = ('first_name', 'last_name')

    def can_view(self):
        return True