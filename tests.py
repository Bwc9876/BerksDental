from json import dumps

from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect
from django.test import TestCase, RequestFactory

from edit import models, views

test_url = "https://example.org"
test_email = "bwc9876@gmail.com"


class BasicDBTest(TestCase):
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
        self.test_adding()
        old_link = models.ExternalLink.objects.get(display_name="Test Add Link")
        request = self.factory.post(f"/admin/edit/link/?id={old_link.id}",
                                    {'url': test_url, 'display_name': "Test Edit Link"})
        vs = views.LinkViewSet()
        vs.obj_edit(request)
        new_link = models.ExternalLink.objects.get(id=old_link.id)
        self.assertEqual(new_link.display_name, "Test Edit Link")
        self.assertEqual(new_link.url, test_url)

    def test_deleting(self):
        self.test_editing()
        link_to_delete = models.ExternalLink.objects.get(display_name="Test Edit Link")
        request = self.factory.post(f"/admin/delete/link/?id={link_to_delete.id}")
        vs = views.LinkViewSet()
        vs.obj_delete_view(request)
        empty_links_list = list(models.ExternalLink.objects.filter(id=link_to_delete.id))
        self.assertEqual(len(empty_links_list), 0)


class OrderingTest(TestCase):

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


def gen_post_data_for_edit(user, permType="none"):
    permissions = {
        views.LinkViewSet().get_safe_name(): permType
    }
    return {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'permissions': dumps(permissions)
    }


class UserTest(TestCase):
    def setUp(self):
        self.userVS = views.UserViewSet()
        self.vs = views.LinkViewSet()
        self.factory = RequestFactory()
        self.bad_user = AnonymousUser()
        self.test_link = models.ExternalLink.objects.create(display_name="Perm Test Link", url=test_url)
        self.none_user = models.User.objects.create(username="None", email=test_email, first_name="Test",
                                                    last_name="Test", password="TestingTesting123")
        self.view_user = models.User.objects.create(username="View", email=test_email, first_name="Test",
                                                    last_name="Test", password="TestingTesting123")
        self.edit_user = models.User.objects.create(username="Edit", email=test_email, first_name="Test",
                                                    last_name="Test", password="TestingTesting123")
        self.admin_user = models.User.objects.create(username="Admin", is_superuser=True, password="TestingTesting123")

    def test_edit_perms(self):
        view_user_request = self.factory.post(f"/admin/edit/user/?id={self.view_user.id}",
                                              gen_post_data_for_edit(self.view_user, permType="view"))
        edit_user_request = self.factory.post(f"/admin/edit/user/?id={self.edit_user.id}",
                                              gen_post_data_for_edit(self.edit_user, permType="edit"))
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
