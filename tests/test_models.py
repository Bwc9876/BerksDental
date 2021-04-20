from datetime import date, time

from django.test import TestCase, RequestFactory

from edit import models, views
from tests import utils
from tests.utils import test_url, test_email, test_image_path


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
        utils.delete_image(self.picture)