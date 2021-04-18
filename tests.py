import os
from datetime import date, time
from json import dumps

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect
from django.test import TestCase, RequestFactory

from edit import models, views, forms
from edit.templatetags import adminTags, eventTags, socialTags
from main import contexts

test_url = "https://example.org"
test_email = "bwc9876@gmail.com"
test_image_path = f"{settings.BASE_DIR}/static/tests/test.png"


class BasicDBActions(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_adding(self):
        request = self.factory.post("/admin/edit/link/", {'url': test_url, 'display_name': "Test Add Link"})
        vs = views.LinkViewSet()
        vs.obj_add(request)
        new_link = models.ExternalLink.objects.get(display_name="Test Add Link")
        self.assertEqual(new_link.display_name, "Test Add Link")
        self.assertEqual(new_link.url, test_url)

    def test_editing(self):
        request = self.factory.post("/admin/edit/link/", {'url': test_url, 'display_name': "Test Add Link"})
        vs = views.LinkViewSet()
        vs.obj_add(request)
        old_link = models.ExternalLink.objects.get(display_name="Test Add Link")
        request = self.factory.post(f"/admin/edit/link/?id={old_link.id}",
                                    {'url': test_url, 'display_name': "Test Edit Link"})
        vs = views.LinkViewSet()
        vs.obj_edit(request)
        new_link = models.ExternalLink.objects.get(id=old_link.id)
        self.assertEqual(new_link.display_name, "Test Edit Link")
        self.assertEqual(new_link.url, test_url)

    def test_deleting(self):
        request = self.factory.post("/admin/edit/link/", {'url': test_url, 'display_name': "Test Add Link"})
        vs = views.LinkViewSet()
        vs.obj_add(request)
        link_to_delete = models.ExternalLink.objects.get(display_name="Test Add Link")
        request = self.factory.post(f"/admin/delete/link/?id={link_to_delete.id}")
        vs = views.LinkViewSet()
        vs.obj_delete_view(request)
        empty_links_list = list(models.ExternalLink.objects.filter(id=link_to_delete.id))
        self.assertEqual(len(empty_links_list), 0)


class Ordering(TestCase):

    def setUp(self):
        link1 = models.ExternalLink.objects.create(url=test_url, display_name="Test 1", sort_order=0)
        link2 = models.ExternalLink.objects.create(url=test_url, display_name="Test 2", sort_order=1)
        link3 = models.ExternalLink.objects.create(url=test_url, display_name="Test 3", sort_order=2)
        self.factory = RequestFactory()
        self.test_links = [link1, link2, link3]

    def test_ordering_on_creation(self):
        request = self.factory.post("/admin/edit/link/", {'url': test_url, 'display_name': "Test 4"})
        vs = views.LinkViewSet()
        vs.obj_add(request)
        new_link = models.ExternalLink.objects.get(display_name="Test 4")
        self.assertEqual(new_link.sort_order, 3, msg="Objects Don't Get Proper Sort Order On Creation!")

    def test_ordering_on_deletion(self):
        target_link = models.ExternalLink.objects.get(display_name="Test 2")
        request = self.factory.post(f"/admin/delete/link/?id={target_link.id}")
        vs = views.LinkViewSet()
        vs.obj_delete_view(request)
        link1 = models.ExternalLink.objects.get(display_name="Test 1")
        link2 = models.ExternalLink.objects.get(display_name="Test 3")
        self.assertEqual(link1.sort_order, 0, msg="Objects Before Deleted Object Sort Order Invalid!")
        self.assertEqual(link2.sort_order, 1, msg="Objects After Deleted Object Sort Order Invalid!")

    def test_order_editing(self):
        link1, link2, link3 = self.test_links
        source_list = [str(link1.id), str(link3.id), str(link2.id)]
        new_order = ",".join(source_list)
        request = self.factory.post("/admin/order/link/", {'new_order': new_order})
        vs = views.LinkViewSet()
        vs.object_order_view(request)
        link1_new = models.ExternalLink.objects.get(display_name="Test 1")
        link2_new = models.ExternalLink.objects.get(display_name="Test 2")
        link3_new = models.ExternalLink.objects.get(display_name="Test 3")
        self.assertEqual(link1_new.sort_order, 0)
        self.assertEqual(link3_new.sort_order, 1)
        self.assertEqual(link2_new.sort_order, 2)


def delete_image(image):
    img_path = settings.MEDIA_ROOT + image.picture.name
    if os.path.exists(img_path):
        os.remove(img_path)


class PictureUploads(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.vs = views.GalleryPhotoViewSet()
        with open(test_image_path, 'rb') as image:
            request = self.factory.post("/admin/edit/photo/", {"picture": image, "caption": "Test Image Upload"})
            self.vs.obj_add(request)
            self.picture = models.GalleryPhoto.objects.get(caption="Test Image Upload")

    def test_upload_on_creation(self):
        self.assertTrue(os.path.exists(settings.MEDIA_ROOT + self.picture.picture.name))
        self.assertEqual(self.picture.picture.name, f"gallery-photos/{self.picture.id}.{self.picture.get_extension()}")

    def test_upload_on_edit(self):
        with open(test_image_path, 'rb') as image:
            request = self.factory.post(f"/admin/edit/photo/?id={self.picture.id}",
                                        {'caption': self.picture.caption, 'image': image})
            self.vs.obj_edit(request)
        self.assertTrue(os.path.exists(settings.MEDIA_ROOT + self.picture.picture.name))
        self.assertEqual(self.picture.picture.name, f"gallery-photos/{self.picture.id}.{self.picture.get_extension()}")

    def test_removal_on_deletion(self):
        request = self.factory.post(f"/admin/delete/photo/?id={self.picture.id}")
        self.vs.obj_delete_view(request)
        self.assertFalse(os.path.exists(settings.MEDIA_ROOT + self.picture.picture.name))

    def tearDown(self):
        delete_image(self.picture)


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


class User(TestCase):
    def setUp(self):
        self.userVS = views.UserViewSet()
        self.vs = views.LinkViewSet()
        self.factory = RequestFactory()
        self.bad_user = AnonymousUser()
        self.test_link = models.ExternalLink.objects.create(display_name="Perm Test Link", url=test_url)
        self.none_user = models.User.objects.create_user(username="None", email=test_email, first_name="Test",
                                                         last_name="Test", password="TestingTesting123")
        self.view_user = models.User.objects.create_user(username="View", email=test_email, first_name="Test",
                                                         last_name="Test", password="TestingTesting123")
        self.edit_user = models.User.objects.create_user(username="Edit", email=test_email, first_name="Test",
                                                         last_name="Test", password="TestingTesting123")
        self.admin_user = models.User.objects.create_superuser(username="Admin", is_superuser=True,
                                                               password="TestingTesting123")

    def test_edit_perms(self):
        view_user_request = self.factory.post(f"/admin/edit/user/?id={self.view_user.id}",
                                              gen_post_data_for_user_edit(self.view_user, perm_type="view"))
        edit_user_request = self.factory.post(f"/admin/edit/user/?id={self.edit_user.id}",
                                              gen_post_data_for_user_edit(self.edit_user, perm_type="edit"))
        self.userVS.obj_edit(view_user_request)
        self.userVS.obj_edit(edit_user_request)
        self.assertEqual(self.view_user.has_perms(self.vs.get_permissions_as_dict()["View"]), True)
        self.assertEqual(self.edit_user.has_perms(self.vs.get_permissions_as_dict()["*"]), True)

    def gen_user_requests_for_perm_check(self, user):
        requests = [self.factory.get("/admin/overview/link/"), self.factory.get("/admin/edit/link/"),
                    self.factory.get(f"/admin/delete/link/?id={self.test_link.id}"),
                    self.factory.get("/admin/order/link/")]
        for request in requests:
            request.user = user
        return requests

    def test_perm_checks(self):
        self.test_edit_perms()
        none_requests = self.gen_user_requests_for_perm_check(self.none_user)
        view_requests = self.gen_user_requests_for_perm_check(self.view_user)
        edit_requests = self.gen_user_requests_for_perm_check(self.edit_user)
        none_expectations = [False, False, False, False]
        view_expectations = [True, False, False, False]
        edit_expectations = [True, True, True, True]
        vs_view, vs_edit, vs_delete = self.vs.get_view_functions()
        vs_order = self.vs.get_edit_order_view()
        access_denied = redirect(self.vs.missing_permissions_link())
        reqs = [none_requests, view_requests, edit_requests]
        expectations = [none_expectations, view_expectations, edit_expectations]

        for requests in reqs:
            x = reqs.index(requests)
            results = [vs_view(requests[0]), vs_edit(requests[1]), vs_delete(requests[2]), vs_order(requests[3])]
            for result in results:
                i = results.index(result)
                if expectations[x][i]:
                    self.assertNotEqual(result.get("Location"), access_denied.get("Location"))
                else:
                    self.assertEqual(result.get("Location"), access_denied.get("Location"))

    def test_password_set(self):
        user = self.view_user
        new_password = "WayBetterPassword432!"
        request = self.factory.post(f"/admin/password/user/?id={user.id}",
                                    {"new_password": new_password, "confirm_new_password": new_password})
        self.userVS.change_password_view(request)
        attempted_login = authenticate(request, username=user.username, password=new_password)
        self.assertIsNotNone(attempted_login)


class Template(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        models.Social.objects.create(service=models.Social.Services.YOUTUBE, link=test_url, sort_order=0)
        models.Social.objects.create(service=models.Social.Services.TWITTER, link=test_url, sort_order=1)
        models.Event.objects.create(name="Good Event", startDate=date(2021, 3, 5), endDate=date(2021, 3, 5),
                                    startTime=time(hour=5, minute=56), endTime=time(hour=5, minute=59),
                                    description="Should be included")
        models.Event.objects.create(name="Bad Event", startDate=date(2021, 4, 5), endDate=date(2021, 5, 5),
                                    startTime=time(hour=5, minute=56), endTime=time(hour=5, minute=59),
                                    description="Should not be included")

    def test_get_socials(self):
        socials = list(socialTags.get_socials())
        self.assertEqual(len(socials), 2)
        self.assertEqual(socials[0].sort_order, 0)

    def test_make_date_obj(self):
        context = {'day': 5, 'month': 3, 'year': 2021}
        new_date = eventTags.make_date_obj(context)
        self.assertEqual(new_date, date(2021, 3, 5))

    def test_get_events_on_day(self):
        context = {'events': models.Event.objects.all(), 'date': date(2021, 3, 5)}
        events = eventTags.get_events_on_day(context)
        self.assertIn(models.Event.objects.get(name="Good Event"), events)
        self.assertNotEquals(models.Event.objects.get(name="Bad Event"), events)

    def test_admin_alerts(self):
        request = self.factory.get("/admin/?alert=Test&alertType=info")
        request.user = AnonymousUser()
        alert_text = adminTags.get_alert(request)
        alert_type = adminTags.get_alert_type(request)
        alert_icon = adminTags.get_alert_icon(request)
        self.assertIsNotNone(alert_text)
        self.assertEqual(alert_text, "Test")
        self.assertEqual(alert_type, "info")
        self.assertEqual(alert_icon, adminTags.alertIcons["info"])

    def test_is_checkbox(self):
        checkbox = forms.PhotoForm().fields["featured"]
        not_checkbox = forms.PhotoForm().fields["caption"]

        class DummyFieldObject:
            def __init__(self, field):
                self.field = field

        self.assertTrue(adminTags.is_checkbox(DummyFieldObject(checkbox)))
        self.assertFalse(adminTags.is_checkbox(DummyFieldObject(not_checkbox)))

    def test_get_primary_value(self):
        test_object = ["1", "2"]
        self.assertEqual(adminTags.get_primary_value(test_object), "1")

    def test_base_data(self):
        request = self.factory.get("/")

        target_values = {'app_name': "main", "agent_type": "None",
                         "debug": settings.DEBUG, 'protocol': "http" if settings.DEBUG else "https"}

        self.assertEqual(target_values, contexts.base_data(request))


class ModelStringFunctions(TestCase):

    def test_user_string(self):
        user = models.User.objects.create(username="admin")
        self.assertEqual(str(user), "admin")
        user.first_name = "First"
        user.last_name = "Last"
        self.assertEqual(str(user), "First Last")

    def test_photo_string(self):
        photo = models.GalleryPhoto.objects.create(caption="Test Photo", width=100, height=100)
        self.assertEqual(str(photo), 'Photo Captioned: "Test Photo"')

    def test_link_string(self):
        link = models.ExternalLink.objects.create(url=test_url, display_name="Test String Link")
        self.assertEqual(str(link), "Link To Test String Link")

    def test_event_string(self):
        event = models.Event.objects.create(name="Test String Event", startDate=date(2021, 4, 5),
                                            endDate=date(2021, 5, 5),
                                            startTime=time(hour=5, minute=56), endTime=time(hour=5, minute=59),
                                            description="__str__")
        self.assertEqual(str(event), "Test String Event")

    def test_officer_string(self):
        officer = models.Officer(first_name="Test", last_name="Officer")
        self.assertEqual(str(officer), "Test Officer")

    def test_social_string(self):
        social = models.Social.objects.create(service=models.Social.Services.YOUTUBE, link=test_url)
        self.assertEqual(str(social), "Berks Dental Assistants' YouTube Page")


class ModelUtilFunctions(TestCase):
    def test_masked_links(self):
        officer = models.Officer.objects.create(first_name="Test", last_name="Officer", email=test_email,
                                                phone="(123)-456-789", width=100, height=100)
        self.assertNotEqual(officer.masked_email_link(), officer.email)
        self.assertNotEqual(officer.masked_phone_link(), officer.phone)

    def test_service_label(self):
        social = models.Social.objects.create(service=models.Social.Services.YOUTUBE, link=test_url)
        self.assertEqual(social.service_label(), "YouTube")

    def test_service_label_from_string(self):
        self.assertEqual(models.Social.service_label_from_string("YT"), "YouTube")

    def test_fa_icon_class(self):
        social = models.Social.objects.create(service=models.Social.Services.YOUTUBE, link=test_url)
        social2 = models.Social.objects.create(service=models.Social.Services.LINKEDIN, link=test_url)
        self.assertEqual(social.fa_icon_class(), "fa-youtube-square")
        self.assertEqual(social2.fa_icon_class(), "fa-linkedin")


class PhotoModelUtilFunctions(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        with open(test_image_path, 'rb') as image:
            request = self.factory.post("/admin/edit/photo/", {"picture": image, "caption": "Test Photo"})
            views.GalleryPhotoViewSet().obj_add(request)
            self.picture = models.GalleryPhoto.objects.get(caption="Test Photo")

    def test_get_extension(self):
        self.assertEqual(self.picture.get_extension(), "png")

    def test_photo_link(self):
        self.assertEqual(self.picture.photo_link(), f"/media/gallery-photos/{self.picture.id}.png")

    def tearDown(self):
        delete_image(self.picture)


def gen_post_data_for_event_edit(startDate, startTime, endDate, endTime):
    return RequestFactory().post("/admin/edit/event/", {
        "name": "Test Event",
        "description": "Test Event",
        "virtual": True,
        "link": test_url,
        "startDate": startDate,
        "endDate": endDate,
        "startTime": startTime,
        "endTime": endTime
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


class FormValidation(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_date_validation(self):
        good_date = gen_post_data_for_event_edit(date(2021, 5, 3), time(5, 50), date(2021, 6, 3), time(5, 50))
        bad_date = gen_post_data_for_event_edit(date(2021, 5, 3), time(5, 50), date(2021, 4, 3), time(5, 50))
        self.assertTrue(forms.EventForm(good_date).is_valid())
        self.assertFalse(forms.EventForm(bad_date).is_valid())

    def test_time_validation(self):
        good_date = gen_post_data_for_event_edit(date(2021, 5, 3), time(5, 50), date(2021, 5, 3), time(5, 56))
        bad_date = gen_post_data_for_event_edit(date(2021, 5, 3), time(5, 50), date(2021, 5, 3), time(5, 40))
        ignored_date = gen_post_data_for_event_edit(date(2021, 5, 3), time(5, 50), date(2021, 6, 3), time(5, 40))
        self.assertTrue(forms.EventForm(good_date).is_valid())
        self.assertFalse(forms.EventForm(bad_date).is_valid())
        self.assertTrue(forms.EventForm(ignored_date).is_valid())

    def test_link_and_location_validation(self):
        good_virtual_event = gen_post_for_location_and_link_check(True, test_url)
        bad_virtual_event = gen_post_for_location_and_link_check(True, "")
        good_physical_event = gen_post_for_location_and_link_check(False, "Test Location")
        bad_physical_event = gen_post_for_location_and_link_check(False, "")
        self.assertTrue(forms.EventForm(good_virtual_event).is_valid())
        self.assertFalse(forms.EventForm(bad_virtual_event).is_valid())
        self.assertTrue(forms.EventForm(good_physical_event).is_valid())
        self.assertFalse(forms.EventForm(bad_physical_event).is_valid())

    def test_password_match_validation(self):
        good_password = gen_post_data_for_user_creation_password("Testing123")
        bad_password = gen_post_data_for_user_creation_password("Testing123", confirm_matches=False)
        self.assertTrue(forms.UserCreateForm(good_password).is_valid())
        self.assertFalse(forms.UserCreateForm(bad_password).is_valid())

    def test_password_format_validation(self):
        too_short = gen_post_data_for_user_creation_password("Ta123")
        no_upper = gen_post_data_for_user_creation_password("bad_pass123")
        no_lower = gen_post_data_for_user_creation_password("BAD_PASS123")
        no_number = gen_post_data_for_user_creation_password("Bad_Pass")
        self.assertFalse(forms.UserCreateForm(too_short).is_valid())
        self.assertFalse(forms.UserCreateForm(no_upper).is_valid())
        self.assertFalse(forms.UserCreateForm(no_lower).is_valid())
        self.assertFalse(forms.UserCreateForm(no_number).is_valid())

    def test_order_uuid_validation(self):
        link1 = models.ExternalLink.objects.create(display_name="1", url=test_url)
        link2 = models.ExternalLink.objects.create(display_name="2", url=test_url, sort_order=1)
        invalid_uuids = gen_post_data_for_order_validation_check(["bad string", "bad string 2"])
        unequal_lists = gen_post_data_for_order_validation_check([str(link1.id)])
        good_list = gen_post_data_for_order_validation_check([str(link2.id), str(link1.id)])
        objs = [link1, link2]
        self.assertFalse(gen_form_for_order_validation_check(invalid_uuids, objs).is_valid())
        self.assertFalse(gen_form_for_order_validation_check(unequal_lists, objs).is_valid())
        self.assertTrue(gen_form_for_order_validation_check(good_list, objs).is_valid())
