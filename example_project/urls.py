from django.conf.urls import url
from django.contrib import admin

from django_shift.router import APIRouter
from example_project.resources import UserObject, UserResource
from example_project.shifts import AddUsernameShift

api_router = APIRouter(versions={
    'DEV': [],
    '2018-06-10': [
        AddUsernameShift
    ],
    '2018-06-01': [],
})

api_router.add_object(UserResource)
api_router.add_object(UserObject)

# in the end

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^docs/', api_router.documentation_urls()),
    url(r'^', api_router.urls()),
]
