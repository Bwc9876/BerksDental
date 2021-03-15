"""
    This file contains a collection of classes that will be translated into database tables, or "models"
    These classes' attributes are set to Field objects which determine how the data will be stored in the database
"""

import uuid

from django.conf import settings
from django.db import models


class GalleryPhoto(models.Model):
    """This is a class meant to represent a table for gallery photos on the database
    It is an extension of the :class:`django.models.Model` class

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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    picture = models.ImageField(upload_to="gallery-photos")
    caption = models.CharField(max_length=1000)
    date_posted = models.DateField(auto_now_add=True)
    featured = models.BooleanField(default=False)

    def get_extension(self):
        """ Used to get the file extension of the uploaded image

        :returns: The file extension of the uploaded image to this GalleryPhoto object
        :rtype: str
        """

        return self.picture.name.split(".")[-1]

    def link(self):
        """ Gets the link to set as a src tag in a <img>

        :returns: The link to this GalleryPhoto's image
        :rtype: str
        """

        return f"{settings.MEDIA_URL}gallery-photos/{self.id}.{self.get_extension()}"

    def __str__(self):
        """ Defines how this object will be casted to a string

        :returns: The caption of the image
        :rtype: str
        """

        return self.caption


class ExternalLink(models.Model):
    """This is a class meant to represent a table for external links on the database
    It is an extension of the :class:`django.models.Model` class

    :attr id: A UUID To identify a specific picture
    :type id: class:`django.db.models.UUIDField`
    :attr url: The link that the user goes to when clicking
    :type url: class:`django.db.models.URLField`
    :attr display_name: The name to show instead of the actual URL
    :type display_name: class:`django.db.models.CharField`
    :attr sort_order: The order to display the links in
    :type sort_order: class:`django.db.models.SmallIntegerField`

    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    url = models.URLField(max_length=350)
    display_name = models.CharField(max_length=100)
    sort_order = models.SmallIntegerField(default=0)

    def get_next_order(self):
        """ Gets the next sort_order attribute depending on the amount of current links

        :returns: The next sort_order attribute (amount of current links + 1)
        :rtype: int
        """

        return len(list(self.objects.all())) + 1

    def __str__(self):
        """ Define how this object will be casted to a string

        :returns: The link's display name
        :rtype: str
        """

        return self.display_name


class Event(models.Model):
    """ This is a class meant to represent a table for events on the database
    It is an extension of the :class:`django.models.Model` class

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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
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


class Officer(models.Model):
    """ This is a class meant to represent a table for gallery photos on the database
    It is an extension of the :class:`django.models.Model` class

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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    picture = models.ImageField(upload_to="officer-photos")
    biography = models.CharField(max_length=2000)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)

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

    def __str__(self):
        """ Defines how this object will be casted to a string

        :returns: The name of the officer
        :rtype: str
        """

        return self.name
