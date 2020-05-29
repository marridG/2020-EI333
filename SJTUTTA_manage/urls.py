from django.urls import path
from . import views

# frontend guys please notice:
# urls below are only used for posting and getting data in json formula
urlpatterns = [
    # ex: app/activities/ # displays the activities list
    path("app/activities/", views.list_activities),
    # ex: app/rollcall/ # roll call an activity
    path("app/rollcall/", views.rollcall_activity),
    path("app/ViewProfile", views.show_profile),
    path("app/EditProfile", views.edit_profile),
    path("app/login", views.my_login),
    path("app/registration", views.my_register),
    path("app/logout", views.my_logout)
]
