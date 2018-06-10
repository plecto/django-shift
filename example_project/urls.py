from django.conf.urls import url
from django.contrib import admin

from django_shift.router import APIRouter
from example_project.views import UserObject

api_router = APIRouter(versions={
    '2018-06-10': [],
})

api_router.add_object(UserObject)

# in the end

urlpatterns = [
    url(r'^admin/', admin.site.urls),
] + api_router.urls()
