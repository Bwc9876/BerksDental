import os
from datetime import date, time
from json import dumps

from django.conf import settings
from django.test import RequestFactory

from edit import views, forms

test_url = "https://example.org"
test_email = "bwc9876@gmail.com"
test_image_path = f"{settings.BASE_DIR}/static/tests/test.png"


def delete_image(image):
    img_path = settings.MEDIA_ROOT + image.picture.name
    if os.path.exists(img_path):
        os.remove(img_path)


def gen_post_data_for_user_edit(user, perm_type="none"):
    permissions = {
        views.LinkViewSet().get_safe_name(): perm_type
    }
    return {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'permissions': dumps(permissions)
    }


def gen_post_data_for_event_edit(start_date, start_time, end_date, end_time):
    return RequestFactory().post("/admin/edit/event/", {
        "name": "Test Event",
        "description": "Test Event",
        "virtual": True,
        "link": test_url,
        "startDate": start_date,
        "endDate": end_date,
        "startTime": start_time,
        "endTime": end_time
    }).POST


def gen_post_data_for_user_creation_password(password, confirm_matches=True):
    post_obj = {'username': "test", 'email': test_email, 'first_name': "First", 'last_name': "Last",
                'permissions': "{}", 'new_password': password,
                "confirm_new_password": password if confirm_matches else "Stupid Password"}
    return RequestFactory().post("/admin/edit/user/", post_obj).POST


def gen_post_for_location_and_link_check(virtual, loc):
    post_obj = {
        "name": "Test Event",
        "description": "Test Event",
        "virtual": virtual,
        "startDate": date(2021, 5, 3),
        "endDate": date(2021, 5, 3),
        "startTime": time(5, 50),
        "endTime": time(5, 54)
    }
    if virtual:
        post_obj["link"] = loc
        post_obj["location"] = ""
    else:
        post_obj["link"] = ""
        post_obj["location"] = loc
    return RequestFactory().post("/admin/edit/event/", post_obj).POST


def gen_post_data_for_order_validation_check(uuid_list):
    return RequestFactory().post("/admin/order/link/", {"new_order": ",".join(uuid_list)}).POST


def gen_form_for_order_validation_check(post_data, obj_list):
    form = forms.OrderForm(post_data)
    form.fields["new_order"].set_objects(obj_list)
    return form
