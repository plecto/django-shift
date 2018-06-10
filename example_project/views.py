from django_shift.resources import APIObject


class UserObject(APIObject):
    name = 'User'

    def can_view(self):
        return True

    def list_records(self):
        return []

    def get_record(self, _id):
        return {}

