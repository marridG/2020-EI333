from django.urls import path
from . import views

# frontend guys please notice:
# urls below are only used for posting and getting data in json formula
urlpatterns = [
    # [Activities]
    path("app/activities/", views.list_activities),
    path("app/activities/rollcall/", views.rollcall_activity),

    # [Store]
    path("app/store/items/new/", views.store_newitem),

    path("app/ViewProfile", views.show_profile),
    path("app/EditProfile", views.edit_profile),
    path("app/login", views.my_login),
    path("app/registration", views.my_register),
    path("app/logout", views.my_logout)
]
