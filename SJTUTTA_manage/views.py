# from django.shortcuts import render

# Create your views here.
import django.core.exceptions
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import *
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from datetime import datetime, timezone, timedelta, date
import pytz

from . import constants


@csrf_exempt
def my_login(request):
    """
    Rewrites the default login function in django, changing the email to be the certification of logging in.
    :param
        request:
            (.body)<json>
                {"email": <str>,
                 "password": <str>}
    :return:
        <json>
            {"login_status": <str>}
            (possible values:
            "membership_expired"
            "email_not_found",
            "password_wrong",
            "successful")
    """
    return_data = {"login_status": ""}

    received_data = read_request(request, "log in")
    email = received_data['email']
    password = received_data['password']

    try:
        user_obj = UserProfile.objects.get(email=email)
        username = user_obj.username
    # MultipleObjectsReturned Not handled
    except django.core.exceptions.ObjectDoesNotExist as e:
        return_data["login_status"] = "email_not_found"
        return JsonResponse(return_data)

    user = authenticate(request, username=username, password=password)
    if user is not None:
        if user.user_expire_date < date.today():
            return_data["login_status"] = "membership_expired"
            return JsonResponse(return_data)
        # Notice str() is required since <byte>UUID is unsupported in json.dumps
        request.session["user_id"] = str(user.user_id)
        request.session.set_expiry(constants.AUTH_LIM_SESSION_EXPIRY)
        request.session.modified = True
        login(request, user)
        return_data["login_status"] = "successful"
    else:
        return_data["login_status"] = "password_wrong"

    return JsonResponse(return_data)


@csrf_exempt
def my_register(request):
    """
    Rewrites the default registration function in django, changing the email to be necessary and unique.
    :param
        request:
            (.body)<json>
                {"email": <str>,
                 "username": <str>,
                 "password": <str>}
                 (Assume the char are not legal by the check of frontend)
    :return:
        <json>
            {"reg_status": <str>}
            (possible values:
            "email_already_used",
            "successful",
            "unknown_errors")
    """
    received_data = json.loads(request.body.decode("utf8", 'ignore'))
    return_data = {"reg_status": ""}
    username = received_data["username"]
    email = received_data['email']
    password = received_data['password']

    try:
        user = UserProfile.objects.create_user(username=username,
                                               email=email,
                                               password=password)
    except Exception as e:
        return_data["reg_status"] = "email_already_used"
        return JsonResponse(return_data)
    user.save()
    try:
        UserProfile.objects.get(email=email)
    except UserProfile.DoesNotExist:
        return_data["reg_status"] = "unknown_errors"
        return JsonResponse(return_data)
    return_data["reg_status"] = "successful"
    return JsonResponse(return_data)
    # if UserProfile.objects.get(email=email):
    #     return_data["reg_status"] = "succ"
    # else:
    #     return_data["reg_status"] = "fail"
    # return JsonResponse(return_data)


@csrf_exempt
def my_logout(request):
    """
    When you call logout(), the session data for the current request is completely cleaned out.
    All existing data is removed.
    :param
        request:
    :return:
        <json>:
            {"logout_status": <str>}
            (only possible value: "succ")
    """
    try:
        del request.session['user_id']
    except KeyError:
        pass

    logout(request)
    return JsonResponse({"logout_status": "succ"})


def read_request(req, des_verb):
    """
    Check if is empty. En/decode and load requests
    :param req:         <request>
    :param des_verb:    <str> a verb describing what action is taken, in case of errors
    :return:
    """
    req_body = req.body
    # if not req_body:
    if req_body is None:
        raise RuntimeError("Empty request body while attempting to %s." % des_verb)

    received_data = json.loads(req_body.decode("utf8", 'ignore'))
    return received_data


def form_activity_info_dict(_act, show_id=False):
    """
    :param _act:        <object>
    :param show_id:     <bool>
    :return:
    """
    _d = {"title": _act.activity_title,
          # .encode("utf8", "ignore").decode("utf8","ignore") # should be utf8 default
          "time": _act.output_time(),
          "location": _act.activity_location,
          "description": _act.activity_description}

    if show_id:
        _d["id"] = _act.activity_id

    return _d


def form_user_info_dict(_user, show_id=False):
    """
    :param _user:       <object>
    :param show_id:     <bool>
    :return:
    """
    _d = {"name": _user.username,
          "phone": _user.user_phone,
          "email": _user.email,
          "sjtu_id": _user.user_SJTUID,
          "expire_date": _user.user_expire_date}

    if show_id:
        _d["id"] = _user.user_id

    return _d


def form_commodity_info_dict(_item, show_id=False):
    """
    :param _item:       <object>
    :param show_id:     <bool>
    :return:
    """
    _d = {"type": _item.commodity_info_type,
          "title": _item.commodity_info_title,
          "size": _item.commodity_info_size,
          "description": _item.commodity_info_description,
          "image": _item.commodity_info_image,
          "price": _item.commodity_info_price,
          "stock": _item.commodity_status_stock,
          "availability": _item.commodity_status_availability}

    if show_id:
        _d["id"] = _item.commodity_id

    return _d


@csrf_exempt
def activities_list_all(request):
    """
    for a LOGGED_IN user:
    handles the JSON request form "/app/activities/" and return JSON data
        NOT authenticated:      Notification
        authenticated:          Handle request.body and return JSON
    Try for more details about "return".
    :param request:     None (should include sessionid in Cookies to authenticate user/anonymous)
    :return:    <json>  {"Fields": <list>some info, "Request": <json>requested data,
                            "Ongoing Activities": <list> of <dict>, "Attended Activities Count": <int>,
                            "Attended Activities": <list> of <dict>, "Upcoming Activities Count": <int>,
                            "Upcoming Activities": <list> of <dict>}
    """

    if not request.user.is_authenticated:
        return JsonResponse({"ERROR": "Anonymous Access is Forbidden"})
    # elif not request.user.has_perm("SJTUTTA_manage.view_Activities"): # no constraints here
    #     return JsonResponse({"ERROR": "You are attempting to access activities list "
    #                                   " without corresponding privileges."})

    user_id = request.user.user_id

    # "_data_info": some info in return JSON for DEBUG, in/ex-clude by constants.DEBUG_LISTACTIVITY_INFO
    _data_info = {
        "Fields": [
            {"Fields": "DEBUG"}, {"Request User ID": "DEBUG"},
            {"Ongoing Activities": [
                "start_time <= now < end_time",
                "order by start_time, the more in the past, the more in the front",
                "attributes of 'time'(start&end) follows 'time.struct_time'"
            ]},
            {"Attended Activities Count": None},
            {"Attended Activities": [
                "not-ongoing & past & attended event(s)"
                "past: end_time <= now",
                "order by start_time, the more in the past, the more in the front",
                "attributes of 'time'(start&end) follows 'time.struct_time'"
            ]},
            {"Upcoming Activities Count": None},
            {"Upcoming Activities": [
                "not-ongoing & upcoming event(s)",
                "upcoming: now < start_time",
                "order by start_time, the more in the past, the more in the front",
                "attributes of 'time'(start&end) follows 'time.struct_time'"]}
        ],
        "Request User ID": user_id
    }
    _data = {
        "Ongoing Activities": [],
        "Attended Activities Count": 0,
        "Attended Activities": [],
        "Upcoming Activities Count": 0,
        "Upcoming Activities": []
    }
    if constants.DEBUG_LISTACTIVITY_INFO:
        data = {**_data_info, **_data}
    else:
        data = _data

    activities_lst = Activities.objects.order_by("activity_start_time")
    for _act in activities_lst:
        _attended = ActivitiesRollCall.objects.filter(
            activity__activity_id=_act.activity_id, participant__user_id=user_id).exists()
        _d = form_activity_info_dict(_act=_act, show_id=False)

        if _act.activity_end_time < now:  # attended
            if _attended:
                data["Attended Activities"].append(_d)
                data["Attended Activities Count"] += 1
        elif now < _act.activity_start_time:  # upcoming
            data["Upcoming Activities"].append(_d)
            data["Upcoming Activities Count"] += 1
        else:  # ongoing
            data["Ongoing Activities"].append(_d)

    return JsonResponse(data)


@csrf_exempt
def activities_new_activity(request):
    """
    :param request:
        (.body)<json> {"title": <str>/None,
                        "start time", "end time": <str, as UTC+8 datetime>,
                            "YEAR-MONTH-DAY HOUR:MINUTE" e.g. "2020-6-08 23:2"
                        "location": <str>/None,
                        "description": <str>/None}
            * should include sessionid in Cookies to authenticate user/admin
            * [NOT Recommended] DEFAULT value 'll be assigned to unfilled "title" & "location"
            * All keys must be included, although they may map to ""(None) values
            * Notice that value/type validation is not conducted in backend
    :return:
        (.body)<json>   if Success: {"Success": Created Activity ID} else a raised error
    """
    if not request.user.is_authenticated:
        return JsonResponse({"ERROR": "Anonymous Access is Forbidden"})
    elif not request.user.has_perm("SJTUTTA_manage.add_activities"):
        return JsonResponse({"ERROR": "Attempting to Add New Activities"
                                      " without Corresponding Privileges."})

    try:
        received_data = read_request(request, "add new activities")

        in_kwargs = {"activity_start_time":
                         tz.localize(datetime.strptime(received_data.get("start time"), "%Y-%m-%d %H:%M")),
                     "activity_end_time":
                         tz.localize(datetime.strptime(received_data.get("end time"), "%Y-%m-%d %H:%M"))}
        if received_data.get("description"):
            in_kwargs["activity_description"] = received_data.get("description")
        else:  # allow descriptions to be left blank
            in_kwargs["activity_description"] = ""
        if received_data.get("title"):
            in_kwargs["activity_title"] = received_data.get("title")
        if received_data.get("location"):
            in_kwargs["activity_location"] = received_data.get("location")
    except Exception as e:
        raise RuntimeError("Invalid Request: %s" % e)
    else:
        new_item_obj = Activities.objects.create(**in_kwargs)

        return JsonResponse({"Success": new_item_obj.activity_id})


def rollcall_asst_validate_request(data):
    """
    check validation of the received data and return the corresponding step
    :param data:    <json>
    :return:    error raised if invalid
                True, <int>:    1: Query Activity
                                2: Select Activity
                                3: Query User
                                4: Select User
                                5: Submit
    """
    # Query Activity
    if data.get("Activity_Query"):
        for _f in ["User_Query", "Activity_Selected", "User_Selected"]:  # extra args
            if data.get(_f):
                raise RuntimeError("Extra \"%s\" given when querying Activity" % _f)

        _d = eval(str(data.get("Activity_Query")))
        if (not _d.get("title")) and (not _d.get("date")) and (not _d.get("location")):  # missing sub-args
            raise RuntimeError("No Expected Arguments (title, date location) are given when querying Activity")
        if _d.get("date"):  # missing sub-args
            _d_d = _d.get("date")
            _valid = False
            for _f in ["year", "month", "day"]:
                if _d_d.get(_f):
                    _valid = True
            if not _valid:
                raise RuntimeError(
                    "No Expected Arguments (year, month, day) are given when querying Activity by date")

        return True, 1

    # Select Activity
    elif data.get("Activity_Selected"):
        for _f in ["User_Query", "Activity_Query", "User_Selected"]:  # extra args
            if data.get(_f):
                raise RuntimeError("Extra \"%s\" given when querying Activity" % _f)

        return True, 2

    # Query User
    elif data.get("User_Query"):
        # if not data.get("Activity_Selected"):  # missiong args
        #     raise RuntimeError("Missing Expected Argument \"Activity_Selected\" when querying User")
        for _f in ["Activity_Query", "User_Selected"]:  # extra args
            if data.get(_f):
                raise RuntimeError("Extra \"%s\" given when querying User" % _f)

        _valid = False
        _d = eval(str(data.get("User_Query")))
        for _f in ["name", "tele", "email", "sjtu_id"]:  # missing sub-args
            if _d.get(_f):
                _valid = True
        if not _valid:
            raise RuntimeError(
                "No Expected Arguments (name, tele, email, sjtu_id) are given when querying User")

        return True, 3

    # Select User
    elif data.get("User_Selected"):
        for _f in ["User_Query", "Activity_Query"]:  # extra args
            if data.get(_f):
                raise RuntimeError("Extra \"%s\" given when querying Activity" % _f)

        if not data.get("Activity_Selected"):
            raise RuntimeError("Missing \"Activity_Selected\" when selecting activity")

        return True, 4

    # Submit
    elif data.get("Submit"):
        for _f in ["Activity_Query", "User_Query", "Activity_Selected", "User_Selected"]:  # extra args
            if data.get(_f):
                raise RuntimeError("Extra \"%s\" given when submitting log" % _f)

        _d = eval(str(data.get("Submit")))
        if (not _d.get("activity_id")) or (not _d.get("user_id")):  # missing sub-args
            raise RuntimeError("Missing either/both (activity_id, user_id) when submitting")

        return True, 5

    else:  # otherwise
        raise RuntimeError("Missing Required Identifiers (Query_Activity, etc.)")


@csrf_exempt
def rollcall_activity(request):
    """
    Search for users and roll call
    Frontend Steps:
        1. Query activity       ==returned==>       Select activity
        2. Query participant    ==returned==>       Select Participant
    :param request: (.body)<json> {"Activity_Query": {"title": <str>/None, "location": <str>/None,
                                                        "date": None/<dict>{"year","month","day":<int>} }
                                    "User_Query": {"name": <str>/None, "tele": <str/int>/None,
                                            "email": <str>/None, "sjtu_id": <str/int>/None },
                                    "Activity_Selected": <str>activity_id/None,
                                    "User_Selected": <str>user_id/None,
                                    "Submit": None/{"activity_id": <str>, "user_id": <str>} }
                    * should include sessionid in Cookies to authenticate user/admin
                    * >=1 sub-args must be given
                    * while querying, "_Selected"&not-under-query are all empty;
                      while selecting, "_Query"&not-selected are all empty
    :return:
    """

    if not request.user.is_authenticated:
        return JsonResponse({"ERROR": "Anonymous Access is Forbidden"})
    elif not request.user.has_perm("SJTUTTA_manage.add_activitiesrollcall"):
        return JsonResponse({"ERROR": "Attempting to Access Activities Roll Call"
                                      " without Corresponding Privileges."})

    received_data = read_request(request, "roll call an activity")
    # print(received_data)
    _valid, op_id = rollcall_asst_validate_request(received_data)

    # "_data_info": some info in return JSON for DEBUG, in/ex-clude by constants.DEBUG_ROLLCALLACTIVITY_INFO
    _data_info = {
        "Fields": [{"Fields": "DEBUG"}, {"Request": "DEBUG"},
                   {"Activities": [
                       "queried activities",
                       "order by start_time, the earlier in the given day, the more in the front",
                       "attributes of 'time'(start&end) follows 'time.struct_time'"
                   ]},
                   {"Users": ["queried subscribed users"]},
                   {"Activities Count": None}, {"Users Count": None},
                   {"Activity": [
                       "selected activity",
                       "attributes of 'time'(start&end) follows 'time.struct_time'"
                   ]},
                   {"User": ["selected user"]},
                   {"Failed": "None/<str> Successfully add the roll call log / Error Message"}],
        "Request": received_data}
    _data = {
        "Activities": [],  # emptied after selection
        "Activities Count": 0,  # emptied after selection
        "Users": [],  # emptied after selection
        "Users Count": 0,  # emptied after selection
        "Activity": None,  # empty before selection
        "User": None,  # empty before selection
        "Failed": "Not logged yet"  # True iff successfully roll called
    }
    if constants.DEBUG_ROLLCALLACTIVITY_INFO:
        data = {**_data_info, **_data}
    else:
        data = _data

    # Query Activity
    if 1 == op_id:
        res_query_obj = Activities.objects.order_by("activity_start_time")
        in_dt = eval(str(received_data.get("Activity_Query")))
        in_title = in_dt.get("title")
        in_date = in_dt.get("date")  # <dict>
        in_loc = in_dt.get("location")
        if in_title:
            res_query_obj = res_query_obj.filter(activity_title__icontains=in_title)
        if in_date:
            res_query_obj = res_query_obj.filter(
                activity_start_time__year=in_date["year"],
                activity_start_time__month=in_date["month"],
                activity_start_time__day=in_date["day"])
        if in_loc:
            res_query_obj = res_query_obj.filter(activity_location__icontains=in_loc)

        for _act in res_query_obj:
            _d = form_activity_info_dict(_act=_act, show_id=True)
            data["Activities"].append(_d)
            data["Activities Count"] += 1

        return JsonResponse(data)

    # Select Activity
    elif 2 == op_id:
        in_id = received_data.get("Activity_Selected")
        _act = Activities.objects.get(activity_id=in_id)
        data["Activity"] = form_activity_info_dict(_act=_act, show_id=False)

        return JsonResponse(data)

    # Query User
    elif 3 == op_id:
        res_query_obj = UserProfile.objects.order_by("username")
        in_dt = eval(str(received_data.get("User_Query")))
        in_name = in_dt.get("name")
        in_tele = in_dt.get("tele")
        in_email = in_dt.get("email")
        in_sjtuid = in_dt.get("sjtu_id")
        if in_name:
            res_query_obj = res_query_obj.filter(username__icontains=in_name)
        if in_tele:
            res_query_obj = res_query_obj.filter(user_phone__contains=in_tele)
        if in_email:
            res_query_obj = res_query_obj.filter(email__icontains=in_email)
        if in_sjtuid:
            res_query_obj = res_query_obj.filter(user_SJTUID__contains=in_sjtuid)

        for _act in res_query_obj:
            if _act.user_expire_date < now.date():
                continue
            _d = form_user_info_dict(_user=_act, show_id=True)
            data["Users"].append(_d)
            data["Users Count"] += 1

        return JsonResponse(data)

    # Select User
    elif 4 == op_id:
        in_id = received_data.get("User_Selected")
        _act = UserProfile.objects.get(user_id=in_id)
        data["User"] = form_user_info_dict(_user=_act, show_id=False)

        return JsonResponse(data)

    # Submit
    else:  # 5 == op_id:
        try:
            in_dt = eval(str(received_data.get("Submit")))
            in_act_id = in_dt.get("activity_id")
            in_user_id = in_dt.get("user_id")
            # print(in_act_id)
            act_obj = Activities.objects.get(activity_id=in_act_id)
            user_obj = UserProfile.objects.get(user_id=in_user_id)
            ActivitiesRollCall.objects.create(activity=act_obj, participant=user_obj)
            data["Failed"] = None
        except Exception as err:
            data["Failed"] = "Failed at Submit: %s" % (str(err))

        return JsonResponse(data)


@csrf_exempt
def store_new_item(request):
    """
    :param request:
        (.body)<json> {"Info": {"type": <str>/None, "title": <str>/None,
                                "size": <str>/None, "description": <str>/None,
                                "image": <str>/None, "price": <str, as float>/None}
                        "Status": {"stock": <str, as int>/None,
                                    "availability": <str, as bool: True/False>/None}}
            * should include sessionid in Cookies to authenticate user/admin
            * "Info", "Status" and sub-keys must be given, although they may map to ""(None) values
            * DEFAULT value will be assigned to unfilled arguments
            * Notice that value/type validation is not conducted in backend
    :return:
        (.body)<json>   if Success: {"Success": Created Activity ID} else a raised error
    """
    if not request.user.is_authenticated:
        return JsonResponse({"ERROR": "Anonymous Access is Forbidden"})
    elif not request.user.has_perm("SJTUTTA_manage.add_storeitems"):
        return JsonResponse({"ERROR": "Attempting to Add New Commodities"
                                      " without Corresponding Privileges."})

    try:
        received_data = read_request(request, "add new commodities")
        info = eval(str(received_data.get("Info")))
        status = eval(str(received_data.get("Status")))

        in_kwargs = {"commodity_info_type": info.get("type"),
                     "commodity_info_title": info.get("title"),
                     "commodity_info_size": info.get("size"),
                     "commodity_info_description": info.get("description"),
                     "commodity_info_image": info.get("image"),
                     "commodity_info_price": info.get("price"),
                     "commodity_status_stock": status.get("stock"),
                     "commodity_status_availability": status.get("availability")}
        # delete empty key-value
        for k in list(in_kwargs.keys()):
            if not in_kwargs[k]:
                del in_kwargs[k]
    except Exception as e:
        raise RuntimeError("Invalid Request: %s" % e)
    else:
        new_item_obj = StoreItems.objects.create(**in_kwargs)

        return JsonResponse({"Success": new_item_obj.commodity_id})


@csrf_exempt
def store_edit_item(request):
    """
    Search for users and roll call
    Frontend Steps:
        1. Query items          ==returned==>       Select items
        2. Submit Item Edits
    :param request:
         (.body)<json> {"Items Query": None/<dict>
                             {"type": <str>/None, "title": <str>/None,
                                 "availability": <str, as bool: True/False>/None},
                         "Edits": None/<dict>
                             {"Edits Count": <int>,
                                 "Edits": <list> of <dict>
                                     {"id": <str>commodity id,
                                         "type": <str>/None, "description": <str>/None,
                                         "image": <str>/None, "stock": <str, as int>/None,
                                         "availability": <str, as bool: True/False>/None}}
            * should include sessionid in Cookies to authenticate user/admin
            * EXACTLY one of "Items_Qeury"/"Edits" should be included
            * all sub-keys of the given key ("I_Q"/"E") must be included,
                although they may map to ""(None)
    :return:
    """
    if not request.user.is_authenticated:
        return JsonResponse({"ERROR": "Anonymous Access is Forbidden"})
    elif (not request.user.has_perm("SJTUTTA_manage.view_storeitems")) or \
            (not request.user.has_perm("SJTUTTA_manage.change_storeitems")):
        return JsonResponse({"ERROR": "Attempting to Edit Commodities Info"
                                      " without Corresponding Privileges."})

    received_data = read_request(request, "edit commodities Info")
    _keys = received_data.keys()
    if not ("Items Query" in _keys) ^ ("Edits" in _keys):
        raise RuntimeError("Neither/Both of 'Items Query'/'Edits' is/are given")

    # "_data_info": some info in return JSON for DEBUG, in/ex-clude by constants.DEBUG_EDITITEM_INFO
    _data_info = {
        "Fields": [{"Fields": "DEBUG"}, {"Request": "DEBUG"},
                   {"Items": [
                       "queried items",
                       "order by availability(True->False), then ascending by type, title",
                   ]},
                   {"Items Count": ""},
                   {"Results": "<dict> Status of Submitting the Edits"
                               "{Fail:<list>Message} and {Success:<list>ID}"}],
        "Request": received_data}
    _data = {"Items": [], "Items Count": 0,  # return with values only querying
             "Results": {"Fail": [], "Success": []}}  # return with values only submitting
    if constants.DEBUG_EDITITEM_INFO:
        data = {**_data_info, **_data}
    else:
        data = _data

    # Query Items
    if "Items Query" in _keys:
        res_query_obj = StoreItems.objects.order_by("-commodity_status_availability"). \
            order_by("commodity_info_type").order_by("commodity_info_title")
        in_dt = eval(str(received_data.get("Items Query")))
        in_type = in_dt.get("type")
        in_title = in_dt.get("title")
        in_availability = in_dt.get("availability")
        if in_type:
            res_query_obj = res_query_obj.filter(commodity_info_type__icontains=in_type)
        if in_title:
            res_query_obj = res_query_obj.filter(commodity_info_title__icontains=in_title)
        if in_availability:
            res_query_obj = res_query_obj.filter(commodity_status_availability=in_availability)

        for _itm in res_query_obj:
            _d = form_commodity_info_dict(_item=_itm, show_id=True)
            data["Items"].append(_d)
            data["Items Count"] += 1

        return JsonResponse(data)

    # Edit Items
    else:  # if "Edits" in _keys:
        in_dt = eval(str(received_data.get("Edits")))
        edits_cnt = in_dt.get("Edits Count")
        edits_target = in_dt.get("Edits")

        if edits_cnt != len(edits_target):
            raise RuntimeError("Invalid Request Data: Edits Count does not Match")

        for edit in edits_target:
            edit_id = edit.get("id")
            target_obj = StoreItems.objects.get(commodity_id=edit_id)
            if not target_obj:
                data["Results"]["Fail"].append("%s: Invalid Item id" % edit_id)
                continue

            if edit.get("type"):
                target_obj.commodity_info_type = edit.get("type")
            if edit.get("description"):
                target_obj.commodity_info_description = edit.get("description")
            if edit.get("image"):
                target_obj.commodity_info_image = edit.get("image")
            if edit.get("stock"):
                target_obj.commodity_status_stock = edit.get("stock")
            if edit.get("availability"):
                target_obj.commodity_status_availability = edit.get("availability")

            target_obj.save()
            data["Results"]["Success"].append(edit_id)

        return JsonResponse(data)


@csrf_exempt
def show_profile(request):
    """
    for a LOGGED_IN user:
    handles the JSON request form "/SJTUTTA_manage/app/ViewProfile" and return JSON data
        NOT authenticated:      Return a notification in JSON
        authenticated:          Handle request.body and return JSON
    Try for more details about "return".
    :param
        request:
            (a request with no body is enough)
    :return:
        <json>
            {"user_id": <str>,
             "User Name": <str>,
             "user_phone": <str>,
             "user_SJTUID": <str>,
             "user_expire_date": <str>,
             "email": <str>,
             "RequestStatus": <str>}
                    (possible strings of "RequestStatus":
                    "NotAuthenticated",
                    "SessionExpired",
                    "CurrentUserNotExist",
                    "OK")
    """

    _data = {"user_id": "",
             "user_name": "",
             "user_phone": "",
             "user_SJTUID": "",
             "user_expire_date": "",
             "email": "",
             "RequestStatus": ""}

    if not request.user.is_authenticated:
        _data["RequestStatus"] = "NotAuthenticated"
        return JsonResponse(_data)
    # elif False: # sample codes if extra privilege check is required
    #     return JsonResponse({"ERROR": "You are attempting to access activities list "
    #                                   " without corresponding privileges."})

    user_id = request.user.user_id

    try:
        queue_result = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        _data["RequestStatus"] = "CurrentUserNotExist"
    else:
        _data["user_id"] = queue_result.user_id
        _data["user_name"] = queue_result.username
        _data["user_phone"] = queue_result.user_phone
        _data["user_SJTUID"] = queue_result.user_SJTUID
        _data["user_expire_date"] = queue_result.user_expire_date
        _data["email"] = queue_result.email
        _data["RequestStatus"] = "OK"

    return JsonResponse(_data)


@csrf_exempt
def edit_profile(request):
    """
        for a LOGGED_IN user:
        handles the JSON request form "/SJTUTTA_manage/app/EditProfile" and return JSON data
            NOT authenticated:      Return a notification in JSON
            authenticated:          Handle request.body and return JSON
        Bear in mind that only two words are editable by ordinary users:
            user_SJTUID;
            user_phone.
        Try for more details about "return".
        :param
            request:
                (.body)<json>
                    {"modified_user_SJTUID": <str>,
                     "modified_phone": <str>}
                        (assume chars legality checked by the frontend;
                        if the user only adjusts one of them, please POST the other string as "NoChange".)
        :return:
            <json>
                {"EditStatus": <str>}
                    (possible strings of "EditStatus":
                    "NotAuthenticated",
                    "SessionExpired",
                    "OK")
    """

    _data = {"EditStatus": ""}

    if not request.user.is_authenticated:
        _data["EditStatus"] = "NotAuthenticated"
        return JsonResponse(_data)
    # elif False: # sample codes if extra privilege check is required
    #     return JsonResponse({"ERROR": "You are attempting to access activities list "
    #                                   " without corresponding privileges."})

    # user_id = request.user.user_id
    # user = UserProfile.objects.get(user_id=user_id)
    user = request.user

    received_data = read_request(request, "access the adjusting demand")
    modified_user_SJTUID = received_data.get("modified_user_SJTUID")
    modified_phone = received_data.get("modified_phone")

    if modified_user_SJTUID != "NoChange":
        user.user_SJTUID = modified_user_SJTUID
    if modified_phone != "NoChange":
        user.user_phone = modified_phone
    user.save()

    _data["EditStatus"] = "OK"
    return JsonResponse(_data)


@csrf_exempt
def get_order(request):
    """
        for a LOGGED_IN user:
        handles the JSON request form "/SJTUTTA_manage/app/GetOrder" and return JSON data
            NOT authenticated:      Return a notification in JSON
            authenticated:          Handle request.body and return JSON
        receives a dict of items and numbers, and returns the separated order number(s) and total price.
        Try for more details about "return".
        :param
            request:
                (.body)<json>
                    {"items": <dict>}
                     (in which every k-v pair represents a commodity and its number)
                     (e.g., {certain commodity_id: count})
                     (frontend ensures that each kind of commodity has 0-32767 items(an integer))
        :return:
            <json>
                {"total_price": <float>,
                 "order_id": <list>,
                 "RequestStatus": <str>}
                (order_id is a list of orders, arranged by the sequence of those in the "items" dict;
                each kind of commodity generates an order.)
                (possible values for RequestStatus:
                    "NotAuthenticated",
                    "SomeCommodityNotExist"
                    "OK")
    """

    _data = {"total_price": 0.,
             "order_id": [],
             "RequestStatus": ""}

    if not request.user.is_authenticated:
        _data["RequestStatus"] = "NotAuthenticated"
        return JsonResponse(_data)

    received_data = read_request(request, "access the dict of commodities")
    # buyer_email = received_data.get("buyer_email")
    commodity_dict = received_data.get("items")

    user_id = request.user.user_id
    buyer_email = UserProfile.objects.get(user_id=user_id).email

    for (k, v) in commodity_dict.items():
        # todo: add seller info in models.StoreItems
        try:
            commodity = StoreItems.objects.get(commodity_id=k)
        except django.core.exceptions.ValidationError and StoreItems.DoesNotExist:
            _data["total_price"] = 0.
            _data["order_id"] = [],
            _data["RequestStatus"] = "SomeCommodityNotExist"
            return JsonResponse(_data)
        if not commodity:
            _data["total_price"] = 0.
            _data["order_id"] = [],
            _data["RequestStatus"] = "SomeCommodityNotExist"
            return JsonResponse(_data)
        order = Order.objects.create(commodity_id=k,
                                     item_count=v,
                                     total_price=v*commodity.commodity_info_price,
                                     buyer_email=buyer_email)
        _data["order_id"].append(order.order_id)
        _data["total_price"] += order.total_price

    _data["RequestStatus"] = "OK"
    return JsonResponse(_data)


# local time, as Beijing (CST, UTC+8)
# bj_CST = timezone(timedelta(hours=8))
# now = datetime.now().astimezone(bj_CST)

tz = pytz.timezone('Asia/Shanghai')
now = tz.localize(datetime.now())
