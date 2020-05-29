from datetime import timedelta

# for Debugs
DEBUG_MODE = True  # global switch
DEBUG_LISTACTIVITY_INFO = DEBUG_MODE and True  # [list activities] in/ex-clude debug info in the returned JSON
DEBUG_ROLLCALLACTIVITY_INFO = DEBUG_MODE and True  # [roll call activity]: ex/include debug info in the returned JSON

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

# Redirection url if user authentication is failed
AUTH_FAIL_REDIRECT = ""
