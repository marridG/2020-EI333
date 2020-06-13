from django.urls import path
from . import views

# frontend guys please notice:
# urls below are only used for posting and getting data in json formula
urlpatterns = [
    # [Activities]
    path("app/activities/user/", views.activities_list_user_related_activities),
    path("app/activities/all/", views.activities_list_all_activities),
    path("app/activities/new/", views.activities_new_activity),
    path("app/activities/rollcall/", views.rollcall_activity),
    path("app/activities/participants/", views.activities_list_participants),

    # [Store]
    path("app/store/items/", views.store_list_items),
    path("app/store/items/new/", views.store_new_item),
    path("app/store/items/edit/", views.store_edit_item),

    # [Profile]
    path("app/ViewProfile", views.show_profile),
    path("app/EditProfile", views.edit_profile),

    path("user/expiration/extend/", views.user_extend_expiration),  # test
    path("user/all/view/", views.user_show_info_batch),  # test

    # [login, logout & reg]
    path("app/login", views.my_login),
    path("app/registration", views.my_register),
    path("app/logout", views.my_logout),

    # [Orders]
    path("app/GetOrder", views.get_order),
]
