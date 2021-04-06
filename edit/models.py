"""
    This file contains a collection of classes that will be translated into database tables, or "models"
    These classes' attributes are set to Field objects which determine how the data will be stored in the database
"""

import os
import uuid

from django.conf import settings
from django.db import models


class GalleryPhoto(models.Model):
    """ This is a class meant to represent a table for gallery photos on the database
    It is an extension of the :class:`django.db.models.Model` class

    :attr id: A UUID To identify a specific picture
    :type id: class:`django.db.models.UUIDField`
    :attr picture: The photo to uploaded and displayed
    :type picture: class:`django.db.models.ImageField`
    :attr caption: A caption describing the picture
    :type caption: class:`django.db.models.CharField`
    :attr date_posted: The date the picture was posted, photos will be sorted using this
    :type date_posted: class:`django.db.models.DateField`
    :attr featured: Whether or not to display the picture on the carousel on the home page
    :type featured: class:`django.db.models.BooleanField`

    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    picture = models.ImageField(upload_to="gallery-photos")
    caption = models.CharField(max_length=1000)
    date_posted = models.DateTimeField(auto_now_add=True)
    featured = models.BooleanField(default=False)

    def get_extension(self):
        """ Used to get the file extension of the uploaded image

        :returns: The file extension of the uploaded image to this GalleryPhoto object
        :rtype: str
        """

        return self.picture.name.split(".")[-1]

    def photo_link(self):
        """ Gets the link to set as a src tag in a <img>

        :returns: The link to this GalleryPhoto's image
        :rtype: str
        """

        return f"{settings.MEDIA_URL}{self.picture.name}"

    def __str__(self):
        """ Defines how this object will be casted to a string

        :returns: The caption of the image
        :rtype: str
        """

        return self.caption

    class Meta:
        ordering = ['-date_posted']


class ExternalLink(models.Model):
    """ This is a class meant to represent a table for external links on the database
    It is an extension of the :class:`django.db.models.Model` class

    :attr id: A UUID To identify a specific picture
    :type id: class:`django.db.models.UUIDField`
    :attr url: The link that the user goes to when clicking
    :type url: class:`django.db.models.URLField`
    :attr display_name: The name to show instead of the actual URL
    :type display_name: class:`django.db.models.CharField`
    :attr sort_order: The order to display the links in
    :type sort_order: class:`django.db.models.SmallIntegerField`

    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=350)
    display_name = models.CharField(max_length=100)
    sort_order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        """ Define how this object will be casted to a string

        :returns: The link's display name
        :rtype: str
        """

        return f"Link To {self.display_name}"

    class Meta:
        ordering = ['sort_order']


class Event(models.Model):
    """ This is a class meant to represent a table for events on the database
    It is an extension of the :class:`django.db.models.Model` class

    :attr id: A UUID To identify a specific picture
    :type id: class:`django.db.models.UUIDField`
    :attr name: The name of the event
    :type name: class:`django.db.models.CharField`
    :attr location: Where the event will take place
    :type location: class:`django.db.models.CharField`
    :attr dateOf: On what day the event occurs
    :type dateOf: class:`django.db.models.DateField`
    :attr startTime: The time the event starts
    :type startTime: class:`django.db.models.TimeField`
    :attr endTime: The time the event stops
    :type endTime: class:`django.db.models.TimeField`

    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    dateOf = models.DateField()
    startTime = models.TimeField()
    endTime = models.TimeField()

    def __str__(self):
        """ Defines how this object will be casted to a string

        :returns: The name of the event
        :rtype: str
        """

        return self.name

    class Meta:
        ordering = ['-dateOf', 'startTime', 'endTime']


class Officer(models.Model):
    """ This is a class meant to represent a table for gallery photos on the database
    It is an extension of the :class:`django.db.models.Model` class

    :attr id: A UUID To identify a specific picture
    :type id: class:`django.db.models.UUIDField`
    :attr name: The name of the Officer
    :type name: class:`django.db.models.CharField`
    :attr picture: The photo to uploaded and displayed
    :type picture: class:`django.db.models.ImageField`
    :attr biography: A short summary about the officer
    :type biography: class:`django.db.models.CharField`
    :attr phone: The phone number of the officer
    :type phone: class:`django.db.models.CharField`, optional
    :attr email: The email of the officer
    :type email: class:`django.db.models.CharField`, optional

    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    picture = models.ImageField(upload_to="officer-photos")
    biography = models.TextField(max_length=2000)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    def get_extension(self):
        """ Used to get the file extension of the uploaded image

        :returns: The file extension of the uploaded image to this Officer object
        :rtype: str
        """

        return self.picture.name.split(".")[-1]

    def photo_link(self):
        """ Gets the link to set as a src tag in a <img>

        :returns: The link to this GalleryPhoto's image
        :rtype: str
        """

        return f"{settings.MEDIA_URL}officer-photos/{self.id}.{self.get_extension()}"

    def masked_email_link(self):
        """ This function is used to mask the officer's email from web scrapers

        :returns: A link that is much harder to get through scrapers
        :rtype: str
        """

        if self.email:
            char_codes = [str(ord(character)) for character in list(self.email)]
            return f'javascript:void(location.href="mailto:"+String.fromCharCode({",".join(char_codes)}))'
        else:
            return "#"

    def masked_phone_link(self):
        """ This function is used to mask the officer's phone from web scrapers

        :returns: A link that is much harder to get through scrapers
        :rtype: str
        """

        if self.phone:
            char_codes = [str(ord(character)) for character in list(self.phone)]
            return f'javascript:void(location.href="tel:"+String.fromCharCode({",".join(char_codes)}))'
        else:
            return "#"

    def __str__(self):
        """ Defines how this object will be casted to a string

        :returns: The name of the officer
        :rtype: str
        """

        return self.name

    class Meta:
        ordering = ['sort_order']


class Social(models.Model):
    """ This is a class meant to represent a table for social media pages on the database
    It is an extension of the :class:`django.db.models.Model` class

    :attr id: A UUID To identify a specific picture
    :type id: class:`django.db.models.UUIDField`
    :attr service: The name of the social media service we're linking to, the icon displayed is based off this
    :type service: class:`django.db.models.CharField`
    :attr link: The link to the social media page
    :type link: class:`django.models.URLField`

    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Services(models.TextChoices):
        """ This is an internal class used to specify what social media services you can chose from
        It extends :class:`django.db.models.TextChoices`

        """

        TWITTER = "TW", "Twitter"
        INSTAGRAM = "IG", "Instagram"
        YOUTUBE = "YT", "YouTube"
        FACEBOOK = "FB", "Facebook"
        LINKEDIN = "LI", "Linkedin"
        PINTEREST = "PT", "Pinterest"

    service = models.CharField(max_length=2, choices=Services.choices, default=Services.TWITTER)
    link = models.URLField(max_length=350)
    sort_order = models.PositiveSmallIntegerField(default=0)

    def service_label(self):
        """ This function is used to get the label for the social media service this links to

        :returns: The name of the social media service this links to
        :rtype: str
        """

        return self.Services.labels[self.Services.values.index(self.service)]

    @classmethod
    def service_label_from_string(cls, service):
        """ This function nsi used as a way to get the label for a social media service given its code

        :param service: The code for a service (FB, IG, YT, etc.)
        :type service: str
        :returns: The Service's label (FaceBook, Instagram, Youtube, etc.)
        :rtype: str
        """

        return cls.Services.labels[cls.Services.values.index(service)]

    def icon_url(self):
        """ This function is used to get the url to the icon for this social media service

        :returns: The url to the icon for this social media type
        :rtype: str
        """

        target_icon = f"{settings.BASE_DIR}/static/social-icons/{self.service}.png"

        if os.path.exists(target_icon):
            return f"{settings.STATIC_URL}social-icons/{self.service}.png"
        else:
            return f"{settings.STATIC_URL}social-icons/DEFAULT.png"

    def __str__(self):
        """ Defines how this object will be casted to a string

        :returns: The name of the social media service
        :rtype: str
        """

        return f"Link To Berks Dental Assistants' {self.service_label()} Page"

    class Meta:
        ordering = ["sort_order"]
