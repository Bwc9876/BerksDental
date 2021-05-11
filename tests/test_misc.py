from datetime import date, time

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect
from django.test import TestCase, RequestFactory

from edit import models, views, forms, exceptions
from edit.templatetags import adminTags, eventTags, socialTags
from edit.view_set import ViewSet
from main import contexts
from tests import utils
from tests.utils import test_url, test_email


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
                                              utils.gen_post_data_for_user_edit(self.view_user, perm_type="View"))
        edit_user_request = self.factory.post(f"/admin/edit/user/?id={self.edit_user.id}",
                                              utils.gen_post_data_for_user_edit(self.edit_user, perm_type="*"))
        self.userVS.obj_edit(view_user_request)
        self.userVS.obj_edit(edit_user_request)
        self.assertTrue(self.view_user.has_perms(self.vs.get_permissions_as_dict()["View"]))
        self.assertTrue(self.edit_user.has_perms(self.vs.get_permissions_as_dict()["*"]))

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

    def test_get_socials(self):
        models.Social.objects.create(service=models.Social.Services.YOUTUBE, link=test_url, sort_order=0)
        models.Social.objects.create(service=models.Social.Services.TWITTER, link=test_url, sort_order=1)
        socials = list(socialTags.get_socials())
        self.assertEqual(len(socials), 2)
        self.assertEqual(socials[0].sort_order, 0)

    def test_make_date_obj(self):
        context = {'day': 5, 'month': 3, 'year': 2021}
        new_date = eventTags.make_date_obj(context)
        self.assertEqual(new_date, date(2021, 3, 5))

    def test_get_events_on_day(self):
        models.Event.objects.create(name="Good Event", startDate=date(2021, 3, 5), endDate=date(2021, 3, 5),
                                    startTime=time(hour=5, minute=56), endTime=time(hour=5, minute=59),
                                    description="Should be included")
        models.Event.objects.create(name="Bad Event", startDate=date(2021, 4, 5), endDate=date(2021, 5, 5),
                                    startTime=time(hour=5, minute=56), endTime=time(hour=5, minute=59),
                                    description="Should not be included")
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
        test_object = ("1", "2")
        self.assertEqual(adminTags.get_primary_value(test_object), "1")

    def test_base_data(self):
        request = self.factory.get("/")

        target_values = {'app_name': "main", "agent_type": "None",
                         "debug": settings.DEBUG, 'protocol': "http" if settings.DEBUG else "https"}

        self.assertEqual(target_values, contexts.base_data(request))

    def test_needs_multipart(self):
        self.assertTrue(adminTags.needs_multipart(forms.PhotoForm()))
        self.assertFalse(adminTags.needs_multipart(forms.LinkForm()))


class FormValidation(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_date_validation(self):
        good_date = utils.gen_post_data_for_event_edit(date(2021, 5, 3), time(5, 50), date(2021, 6, 3), time(5, 50))
        bad_date = utils.gen_post_data_for_event_edit(date(2021, 5, 3), time(5, 50), date(2021, 4, 3), time(5, 50))
        self.assertTrue(forms.EventForm(good_date).is_valid())
        self.assertFalse(forms.EventForm(bad_date).is_valid())

    def test_time_validation(self):
        good_date = utils.gen_post_data_for_event_edit(date(2021, 5, 3), time(5, 50), date(2021, 5, 3), time(5, 56))
        bad_date = utils.gen_post_data_for_event_edit(date(2021, 5, 3), time(5, 50), date(2021, 5, 3), time(5, 40))
        ignored_date = utils.gen_post_data_for_event_edit(date(2021, 5, 3), time(5, 50), date(2021, 6, 3), time(5, 40))
        self.assertTrue(forms.EventForm(good_date).is_valid())
        self.assertFalse(forms.EventForm(bad_date).is_valid())
        self.assertTrue(forms.EventForm(ignored_date).is_valid())

    def test_link_and_location_validation(self):
        good_virtual_event = utils.gen_post_for_location_and_link_check(True, test_url)
        bad_virtual_event = utils.gen_post_for_location_and_link_check(True, "")
        good_physical_event = utils.gen_post_for_location_and_link_check(False, "Test Location")
        bad_physical_event = utils.gen_post_for_location_and_link_check(False, "")
        self.assertTrue(forms.EventForm(good_virtual_event).is_valid())
        self.assertFalse(forms.EventForm(bad_virtual_event).is_valid())
        self.assertTrue(forms.EventForm(good_physical_event).is_valid())
        self.assertFalse(forms.EventForm(bad_physical_event).is_valid())

    def test_password_match_validation(self):
        good_password = utils.gen_post_data_for_user_creation_password("Testing123")
        bad_password = utils.gen_post_data_for_user_creation_password("Testing123", confirm_matches=False)
        self.assertTrue(forms.UserCreateForm(good_password).is_valid())
        self.assertFalse(forms.UserCreateForm(bad_password).is_valid())

    def test_password_format_validation(self):
        too_short = utils.gen_post_data_for_user_creation_password("Ta123")
        no_upper = utils.gen_post_data_for_user_creation_password("bad_pass123")
        no_lower = utils.gen_post_data_for_user_creation_password("BAD_PASS123")
        no_number = utils.gen_post_data_for_user_creation_password("Bad_Pass")
        self.assertFalse(forms.UserCreateForm(too_short).is_valid())
        self.assertFalse(forms.UserCreateForm(no_upper).is_valid())
        self.assertFalse(forms.UserCreateForm(no_lower).is_valid())
        self.assertFalse(forms.UserCreateForm(no_number).is_valid())

    def test_order_uuid_validation(self):
        link1 = models.ExternalLink.objects.create(display_name="1", url=test_url)
        link2 = models.ExternalLink.objects.create(display_name="2", url=test_url, sort_order=1)
        invalid_uuids = utils.gen_post_data_for_order_validation_check(["bad string", "bad string 2"])
        unequal_lists = utils.gen_post_data_for_order_validation_check([str(link1.id)])
        good_list = utils.gen_post_data_for_order_validation_check([str(link2.id), str(link1.id)])
        objs = [link1, link2]
        self.assertFalse(utils.gen_form_for_order_validation_check(invalid_uuids, objs).is_valid())
        self.assertFalse(utils.gen_form_for_order_validation_check(unequal_lists, objs).is_valid())
        self.assertTrue(utils.gen_form_for_order_validation_check(good_list, objs).is_valid())


class ViewSetConfigurations(TestCase):

    def test_model_check(self):
        class BadVS(ViewSet):
            model = None
            modelForm = forms.LinkForm
            displayName = "Test"
            displayFields = ["asdf"]

        self.assertRaises(exceptions.ImproperlyConfiguredViewSetError, BadVS)

    def test_model_form_check(self):
        class BadVS(ViewSet):
            model = models.ExternalLink
            modelForm = None
            displayFields = ["url"]
            displayName = "Test"

        self.assertRaises(exceptions.ImproperlyConfiguredViewSetError, BadVS)

    def test_display_field_check(self):
        class BadVS(ViewSet):
            model = models.ExternalLink
            modelForm = forms.LinkForm
            displayFields = ["invalid"]
            displayName = "Test"

        self.assertRaises(exceptions.ImproperlyConfiguredViewSetError, BadVS)

    def test_sort_order_check(self):
        class BadVS(ViewSet):
            model = models.GalleryPhoto
            modelForm = forms.PhotoForm
            displayFields = ["caption"]
            ordered = True
            displayName = "Test"

        self.assertRaises(exceptions.ImproperlyConfiguredViewSetError, BadVS)

    def test_per_page_check(self):
        class BadVS(ViewSet):
            model = models.GalleryPhoto
            modelForm = forms.PhotoForm
            displayFields = ["caption"]
            displayName = "Test"
            per_page = -5

        self.assertRaises(exceptions.ImproperlyConfiguredViewSetError, BadVS)

    def test_label_invalid_field_check(self):
        class BadVS(ViewSet):
            model = models.GalleryPhoto
            modelForm = forms.PhotoForm
            displayFields = ["caption"]
            displayName = "Test"
            labels = {'asdf': 'bad label'}

        self.assertRaises(exceptions.ImproperlyConfiguredViewSetError, BadVS)

    def test_labels_not_in_display_fields_check(self):
        class BadVS(ViewSet):
            model = models.GalleryPhoto
            modelForm = forms.PhotoForm
            displayFields = ["caption"]
            displayName = "Test"
            labels = {'picture': 'bad label'}

        self.assertRaises(exceptions.ImproperlyConfiguredViewSetError, BadVS)

    def test_actions_check(self):
        class BadVS(ViewSet):
            model = models.ExternalLink
            modelForm = forms.LinkForm
            displayFields = ["url"]
            displayName = "Link"
            additionalActions = ["Not an action!"]

        self.assertRaises(exceptions.ImproperlyConfiguredViewSetError, BadVS)

    def test_good_vs(self):
        class GoodVS(ViewSet):
            model = models.ExternalLink
            modelForm = forms.LinkForm
            displayName = "Link"
            displayFields = ["display_name", "url"]
            labels = {'url': "Link"}
            ordered = True
            per_page = 5

        try:
            GoodVS()
        except exceptions.ImproperlyConfiguredViewSetError:
            self.fail()

    def test_registered_viewsets(self):
        for vs in views.REGISTERED_VIEWSETS:
            try:
                vs()
            except exceptions.ImproperlyConfiguredViewSetError:
                self.fail()
        try:
            views.UserViewSet()
        except exceptions.ImproperlyConfiguredViewSetError:
            self.fail()
