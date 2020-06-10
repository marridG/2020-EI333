# from django.contrib import admin
#
# # Register your models here.
# Register your models here.
from django.contrib import admin
# from django.contrib.auth.models import Permission
from .models import *

from . import constants


# from django.contrib.auth.admin import UserAdmin


class UserAdmin(admin.ModelAdmin):
    # 设置显示数据库中哪些字段
    list_display = ['get_user_id',
                    'get_username',
                    'get_user_phone',
                    'get_user_SJTUID',
                    'get_user_expire_date',
                    # 'get_password',
                    'get_email']
    search_fields = ["email", "username", ]
    list_display_links = ["get_email", "get_username", "get_user_id", ]
    ordering = ["user_expire_date", ]
    list_per_page = constants.ADMIN_MAX_PER_PAGE

    def get_user_id(self, obj):
        return obj.user_id

    get_user_id.short_description = "user_id"

    def get_username(self, obj):
        return obj.username

    get_username.short_description = "User Name"

    def get_user_phone(self, obj):
        return obj.user_phone

    get_user_phone.short_description = "user_phone"

    def get_user_SJTUID(self, obj):
        return obj.user_SJTUID

    get_user_SJTUID.short_description = "user_SJTUID"

    def get_user_expire_date(self, obj):
        return obj.user_expire_date

    get_user_expire_date.short_description = "user_expire_date"

    # def get_password(self, obj):
    #     return obj.password
    #
    # get_password.short_description = "password"

    def get_email(self, obj):
        return obj.email

    get_email.short_description = "email"


class StoreItemsAdmin(admin.ModelAdmin):
    """
    ["commodity_info_type", "commodity_info_title", "commodity_info_size",
        "commodity_info_description", "commodity_info_image", "commodity_info_price",
        "commodity_info_sold_by", "commodity_status_stock",
        "commodity_status_availability"]
    """  # All Fields

    list_display = ["commodity_status_availability",
                    "commodity_info_type", "commodity_info_title",
                    "commodity_info_sold_by", "commodity_info_size",
                    "commodity_info_price",
                    "commodity_status_stock", ]
    list_filter = ["commodity_status_availability", "commodity_info_type", "commodity_info_sold_by"]
    search_fields = ["commodity_info_title", "commodity_info_sold_by", ]
    list_display_links = ["commodity_info_title", "commodity_status_stock", ]
    sortable_by = ["commodity_info_type", "commodity_info_title", "commodity_info_price",
                   "commodity_info_sold_by", "commodity_status_stock",
                   "commodity_status_availability"]
    list_per_page = constants.ADMIN_MAX_PER_PAGE


class ActivitiesAdmin(admin.ModelAdmin):
    list_display = ["get_start", "activity_title", "activity_location", ]
    list_filter = ["activity_start_time", "activity_location", ]
    search_fields = ["activity_title", "activity_location", ]
    list_display_links = ["activity_title", ]
    # sortable_by = ["activity_title", "activity_location", "get_start"] # not effective
    list_per_page = constants.ADMIN_MAX_PER_PAGE

    def get_start(self, obj):
        return datetime.strftime(obj.activity_start_time, "%Y/%m/%d %H:%M")

    get_start.short_description = "Start Time"
    get_start.admin_order_field = "activity_start_time"


class ActivitiesRollCallAdmin(admin.ModelAdmin):
    list_display = ["get_start", "get_name", "get_title", "get_location", ]
    list_filter = ["activity__activity_start_time", "activity__activity_location", ]
    search_fields = ["activity__activity_title", "activity__activity_location", ]
    list_display_links = ["get_name", ]
    list_per_page = constants.ADMIN_MAX_PER_PAGE

    def get_start(self, obj):
        return datetime.strftime(obj.activity.activity_start_time, "%Y/%m/%d %H:%M")

    def get_location(self, obj):
        return obj.activity.activity_location

    def get_title(self, obj):
        return obj.activity.activity_title

    def get_name(self, obj):
        return obj.participant.username

    get_start.short_description = "START TIME"
    get_location.short_description = "LOCATION"
    get_title.short_description = "TITLE"
    get_name.short_description = "PARTICIPANT"

    get_start.admin_order_field = "activity__activity_start_time"
    get_location.admin_order_field = "activity__activity_location"
    get_title.admin_order_field = "activity__activity_title"
    get_name.admin_order_field = "participant__username"


admin.site.register(UserProfile, UserAdmin)
# admin.site.register(Permission)
admin.site.register(Activities, ActivitiesAdmin)
admin.site.register(ActivitiesRollCall, ActivitiesRollCallAdmin)
admin.site.register(StoreItems, StoreItemsAdmin)
admin.site.register(Order)

# admin.ModelAdmin.filter_horizontal = ('groups', 'user_permissions')
