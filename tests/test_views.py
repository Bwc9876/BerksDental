import os

from django.conf import settings
from django.test import TestCase, RequestFactory

from edit import models, views
from tests import utils
from tests.utils import test_url, test_image_path


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
        self.assertEqual(new_link.sort_order, 3)

    def test_ordering_on_deletion(self):
        target_link = models.ExternalLink.objects.get(display_name="Test 2")
        request = self.factory.post(f"/admin/delete/link/?id={target_link.id}")
        vs = views.LinkViewSet()
        vs.obj_delete_view(request)
        link1 = models.ExternalLink.objects.get(display_name="Test 1")
        link2 = models.ExternalLink.objects.get(display_name="Test 3")
        self.assertEqual(link1.sort_order, 0)
        self.assertEqual(link2.sort_order, 1)

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
        utils.delete_image(self.picture)


class Pagination(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.vs = views.LinkViewSet()
        self.vs.per_page = 2
        self.admin = models.User.objects.create_superuser(username="admin", password="Testing123")
        self.link1 = models.ExternalLink.objects.create(url=test_url, display_name="Test1")
        self.link2 = models.ExternalLink.objects.create(url=test_url, display_name="Test2")
        self.link3 = models.ExternalLink.objects.create(url=test_url, display_name="Test3")
        self.link4 = models.ExternalLink.objects.create(url=test_url, display_name="Test4")
        self.test_links = [self.link1, self.link2, self.link3, self.link4]

    def test_page_separation(self):
        page_1_request = self.factory.get("/admin/overview/link/")
        page_1_request.user = self.admin
        page_2_request = self.factory.get("/admin/overview/link/?page=2")
        page_2_request.user = self.admin
        page_1_response = self.vs.obj_overview_view(page_1_request)
        page_2_response = self.vs.obj_overview_view(page_2_request)
        self.assertIn(self.test_links[0].display_name, str(page_1_response.content))
        self.assertNotIn(self.test_links[2].display_name, str(page_1_response.content))
        self.assertIn(self.test_links[2].display_name, str(page_2_response.content))
        self.assertNotIn(self.test_links[0].display_name, str(page_2_response.content))
