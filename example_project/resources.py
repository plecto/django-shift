from django.contrib.auth.models import User

from django_shift.resources import APIResource, APIResourceAction
from django_shift.serializer import APIModelObject


class UserObject(APIResource):
    name = 'user'
    label = 'User'
    pk_field = 'id'

    schema = {
        "id": {"type": "integer"},
        "username": {"type": "string"},
    }

    def can_view(self):
        return True

    def can_create(self):
        return True

    def can_delete(self):
        return True

    def list_records(self):
        return [self.serialize(user) for user in User.objects.all()]

    def get_record(self, _id):
        obj = User.objects.get(pk=_id)
        return self.serialize(obj)

    def save_record(self, data, _id=None):
        obj = self.deserialize(data)
        obj.save()
        return {}

    def delete_record(self, _id):
        User.objects.filter(pk=_id).delete()
        return {}

    def serialize(self, obj):
        return {
            'id': obj.id,
            'username': obj.username
        }

    def deserialize(self, data):
        # if pk:
        # fetch
        return User(
            username=data['username']
        )


class UserResetPasswordAction(APIResourceAction):
    pass


class UserResource(APIModelObject):
    model = User
    name = 'user_v2'
    label = 'User'
    fields = ('id', 'first_name', 'last_name', 'username', 'is_active')

    # actions = (
    #     'reset_password', UserResetPasswordAction
    # )

    def can_view(self):
        return True

    def can_create(self):
        return True