from datetime import timedelta

# for Debugs
DEBUG_MODE = True  # global switch
DEBUG_LISTACTIVITY_INFO = DEBUG_MODE and True  # [list activities] in/ex-clude debug info in the returned JSON
DEBUG_ROLLCALLACTIVITY_INFO = DEBUG_MODE and True  # [roll call activity]: ex/include debug info in the returned JSON
DEBUG_EDITITEM_INFO = DEBUG_MODE and True  # [edit commodity items]: ex/include debug info in the returned JSON

# Activities Related: Defaults(DEF), Limits(LIM), etc.
ACTIVITY_DEF_TITLE = "乒协活动 SJTUTTA"
# [UNAVAILABLE] ACTIVITY_DEF_DURATION = timedelta(hours=1, minutes=30)  # total duration = hours : minutes
ACTIVITY_DEF_LOCATION = "南区体育场乒乓球馆 Ping-Pong in South Gym"
ACTIVITY_DEF_DESCRIPTION = "欢迎各位参加.\nWelcome."
ACTIVITY_LIM_TITLE_MAX_LEN = 100
ACTIVITY_LIM_LOCATION_MAX_LEN = 50

# UserProfile Related: Defaults(DEF), Limits(LIM), etc.
PROFILE_LIM_PHONE_MAX_LENGTH = 11
PROFILE_DEF_PHONE = ""
PROFILE_LIM_SJTUID_MAX_LEN = 12
PROFILE_DEF_SJTUID = ""

# Store Related: Defaults(DEF), Limits(LIM), etc.
STORE_INFO_LIM_TYPE_MAX_LENGTH = 5
STORE_INFO_DEF_TYPE = "UNK"
STORE_INFO_LIM_TITLE_MAX_LENGTH = 12
STORE_INFO_DEF_TITLE = "Commodity 商品"
STORE_INFO_LIM_SIZE_MAX_LENGTH = 12
STORE_INFO_DEF_SIZE = "One 1 一"
STORE_INFO_DEF_DESCRIPTION = "Unfilled"
STORE_INFO_DEF_IMAGE = "http://vi.sjtu.edu.cn/uploads/files/caf2f5045c47308250fab3812dfe2003" \
                       "-6896b91594f238b24e67696224948251.png "
STORE_INFO_DEF_PRICE = 2.33
STORE_INFO_LIM_SOLD_BY_MAX_LENGTH = 15
STORE_INFO_DEF_SOLD_BY = "微电子工业"
STORE_STATUS_DEF_STOCK = 0
STORE_STATUS_DEF_AVAILABILITY = True

# order related
ORDER_SELLER_INFO_DEF = "SJTUTTA"
ORDER_STATUS_DEF = "order_accepted"
ORDER_PAY_QR_CODE_DEF = STORE_INFO_DEF_IMAGE  # TODO:to be replaced with a image of real QR code
ORDER_INFO_MAX_LENGTH = 255

# Redirection url if user authentication is failed
AUTH_FAIL_REDIRECT = ""
AUTH_LIM_SESSION_EXPIRY = 1000 * 60  # seconds

# admin @GuoZL: username: admin, password: 1
