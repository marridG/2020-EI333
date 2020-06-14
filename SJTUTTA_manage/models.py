from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
import uuid
from datetime import datetime

from . import constants


# Create your models here.
class UserProfile(AbstractUser):
    email = models.EmailField('email address',
                              unique=True,
                              blank=False)
    user_id = models.UUIDField(unique=True,
                               default=uuid.uuid4,
                               editable=False)
    user_phone = models.CharField("Phone",
                                  editable=True,
                                  blank=True,
                                  max_length=constants.PROFILE_LIM_PHONE_MAX_LENGTH,
                                  default=constants.PROFILE_DEF_PHONE)
    user_SJTUID = models.CharField("SJTU ID",
                                   editable=True,
                                   blank=True,
                                   max_length=constants.PROFILE_LIM_SJTUID_MAX_LEN,
                                   default=constants.PROFILE_DEF_SJTUID)
    user_expire_date = models.DateField("Expire Date",
                                        editable=True,
                                        blank=True,
                                        default=now)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = "Users Profile"


class Activities(models.Model):
    activity_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    activity_title = models.CharField("Title", editable=True, blank=False,
                                      max_length=constants.ACTIVITY_LIM_TITLE_MAX_LEN,
                                      default=constants.ACTIVITY_DEF_TITLE)
    activity_start_time = models.DateTimeField("Start Time", editable=True, blank=False)
    # todo: Note that "start_time < end_time" is NOT guaranteed, validation required
    activity_end_time = models.DateTimeField("End Time", editable=True, blank=False)
    activity_location = models.CharField("Location", editable=True, blank=False,
                                         max_length=constants.ACTIVITY_LIM_LOCATION_MAX_LEN,
                                         default=constants.ACTIVITY_DEF_LOCATION)
    activity_description = models.TextField("Descriptions", editable=True, blank=True,
                                            default=constants.ACTIVITY_DEF_DESCRIPTION)

    def __str__(self):
        return "%s" % self.activity_title

    class Meta:
        verbose_name_plural = "Activities"

    def output_time(self):
        time_struct = datetime.timetuple(self.activity_start_time)
        time_dict = {
            "start": {"tm_year": time_struct.tm_year, "tm_mon": time_struct.tm_mon, "tm_mday": time_struct.tm_mday,
                      "tm_hour": time_struct.tm_hour, "tm_min": time_struct.tm_min, "tm_sec": time_struct.tm_sec,
                      "tm_wday": time_struct.tm_wday, "tm_yday": time_struct.tm_yday, "tm_isdst": time_struct.tm_isdst,
                      "tm_zone": time_struct.tm_zone, "tm_gmtoff": time_struct.tm_gmtoff}}
        time_end_struct = datetime.timetuple(self.activity_end_time)
        time_dict["end"] = {
            "tm_year": time_end_struct.tm_year, "tm_mon": time_end_struct.tm_mon, "tm_mday": time_end_struct.tm_mday,
            "tm_hour": time_end_struct.tm_hour, "tm_min": time_end_struct.tm_min, "tm_sec": time_end_struct.tm_sec,
            "tm_wday": time_end_struct.tm_wday, "tm_yday": time_end_struct.tm_yday,
            "tm_isdst": time_end_struct.tm_isdst, "tm_zone": time_end_struct.tm_zone,
            "tm_gmtoff": time_end_struct.tm_gmtoff}
        return time_dict


class ActivitiesRollCall(models.Model):
    activity = models.ForeignKey(Activities, on_delete=models.CASCADE)
    participant = models.ForeignKey(UserProfile, related_name="acp", on_delete=models.CASCADE)
    roll_call_time = datetime.now()

    def __str__(self):
        title = "%s - %s - Roll Call - %s" % (
            datetime.strftime(self.activity.activity_start_time, "%Y/%m/%d %H:%M (%Z)"),
            self.activity.activity_title, self.participant.username)
        return title

    class Meta:
        verbose_name_plural = "Activities - Roll Call"


class StoreItems(models.Model):
    # id
    commodity_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    # information
    commodity_info_type = models.CharField("Type", editable=True, blank=False,
                                           max_length=constants.STORE_INFO_LIM_TYPE_MAX_LENGTH,
                                           default=constants.STORE_INFO_DEF_TYPE)
    commodity_info_title = models.CharField("Title", editable=False, blank=False,
                                            max_length=constants.STORE_INFO_LIM_TITLE_MAX_LENGTH,
                                            default=constants.STORE_INFO_DEF_TITLE)
    commodity_info_size = models.CharField("Size", editable=False, blank=False,
                                           max_length=constants.STORE_INFO_LIM_SIZE_MAX_LENGTH,
                                           default=constants.STORE_INFO_DEF_SIZE)
    commodity_info_description = models.TextField("Description", editable=True, blank=True,
                                                  default=constants.STORE_INFO_DEF_DESCRIPTION)
    commodity_info_image = models.TextField("Image URL", editable=True, blank=True,
                                            default=constants.STORE_INFO_DEF_IMAGE)
    commodity_info_price = models.FloatField("Price", editable=False, blank=False,
                                             default=constants.STORE_INFO_DEF_PRICE)
    commodity_info_sold_by = models.CharField("Sold By", editable=False, blank=False,
                                              max_length=constants.STORE_INFO_LIM_SOLD_BY_MAX_LENGTH,
                                              default=constants.STORE_INFO_DEF_SOLD_BY)
    # status
    commodity_status_stock = models.PositiveIntegerField(
        "Stock", editable=True, blank=False, default=constants.STORE_STATUS_DEF_STOCK)
    commodity_status_availability = models.BooleanField(
        "Availability", editable=True, blank=False, default=constants.STORE_STATUS_DEF_AVAILABILITY)

    def __str__(self):
        return "%s " \
               "[%s] %s (%s): RMB %.2f [%d Left]" % \
               ("√" if self.commodity_status_availability else "×",
                self.commodity_info_sold_by, self.commodity_info_title, self.commodity_info_size,
                self.commodity_info_price,
                self.commodity_status_stock)

    class Meta:
        verbose_name_plural = "Store - Items"


class Order(models.Model):
    # id
    order_id = models.UUIDField(unique=True,
                                default=uuid.uuid4,
                                editable=False)
    # info
    # commodity_id = models.CharField("Commodity ID",
    #                                 editable=False,
    #                                 blank=False,
    #                                 max_length=32)
    commodity = models.ForeignKey("StoreItems", on_delete=models.CASCADE)
    # PositiveSmallIntegerField: meets 0-32767 integer
    item_count = models.PositiveSmallIntegerField("Count of Item",
                                                  editable=False,
                                                  blank=False)
    total_price = models.FloatField("Total Price",
                                    editable=False,
                                    blank=False)
    order_datetime = models.DateTimeField("Order Datetime",
                                          editable=False,
                                          blank=False,
                                          default=now)
    # buyer_email = models.EmailField('Customer Email Address',
    #                                 editable=False,
    #                                 blank=False)
    user = models.ForeignKey("UserProfile", on_delete=models.CASCADE)
    # seller_info = models.CharField("Seller Info",
    #                                editable=False,
    #                                blank=False,
    #                                default=constants.ORDER_SELLER_INFO_DEF,
    #                                max_length=constants.ORDER_INFO_MAX_LENGTH)
    pay_qr_code = models.TextField("QR Code URL for Payment",
                                   editable=False,
                                   blank=False,
                                   default=constants.STORE_INFO_DEF_IMAGE)
    # possible order status:
    # "order_accepted"
    # "seller_shipped"
    # "buyer_accepted"
    # "refund_raised"
    # "refund_completed"
    order_status = models.CharField("Current Order Status",
                                    editable=True,
                                    blank=False,
                                    default=constants.ORDER_STATUS_DEF,
                                    max_length=constants.ORDER_INFO_MAX_LENGTH)

    def __str__(self):
        return "商品名称: {}, " \
               "购买数量: {}, " \
               "总价: {}, " \
               "买家用户名: {}, " \
               "买家手机号: {}, " \
            .format(self.commodity.commodity_info_title,
                    self.item_count,
                    self.total_price,
                    self.user.username,
                    self.user.user_phone)

    class Meta:
        verbose_name_plural = "Order"
