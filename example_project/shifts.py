from django_shift.resources import APIShift
from example_project.resources import UserObject


class AddIdShift(APIShift):
    """
    Adds the field ```id``` to the response
    """

    resource = UserObject

    @staticmethod
    def migrate_response(data):
        data.pop('id')
        return data

    @staticmethod
    def migrate_request(data):
        return data


class AddUsernameShift(APIShift):
    """
    Adds the field ```username``` to the response
    """

    resource = UserObject

    @staticmethod
    def migrate_response(data):
        data.pop('username')
        return data

    @staticmethod
    def migrate_request(data):
        return data