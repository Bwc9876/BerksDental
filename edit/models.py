"""
    This file contains a collection of classes that will be translated into database tables, or "models"
    These classes' attributes are set to ModelField objects which determine how the data will be stored in the database
"""

import uuid
from json import dumps

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError
from django.template.defaultfilters import escape


class OrderedMixin(models.Model):
    """
    A mixin which makes a model ordered via a sort_order attribute
    """

    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ['sort_order']


def get_upload_to(instance, name):
    """
    Gets what folder to upload an image to
    @param instance: The model that's saving the photo
    @type instance: Model
    @param name: The name of the photo file
    @type name: str
    @return: The folder to store the image in
    @rtype: str
    """

    return f"{instance.__class__.__name__.lower()}-pictures/{name}"


class PhotoMixin(models.Model):
    """
    A mixin that allows the user to upload a picture and save it to this model
    """

    width = models.IntegerField()
    height = models.IntegerField()
    picture = models.ImageField(upload_to=get_upload_to, width_field='width', height_field='height')

    def get_extension(self):
        """
        This function gets the file extension an image uses, for renaming

        @return: the extension (png, jpg, etc.) of the image
        @rtype: str
        """

        return self.picture.name.split(".")[-1]

    def photo_link(self):
        """
        This function provides a link to use in a src attribute to show the image

        @return: The url that the image uses
        @rtype: str
        """

        return f"{settings.MEDIA_URL}{self.picture.name}"

    class Meta:
        abstract = True


class BaseModel(models.Model):
    """
    This class is a model that all models in this file should inherit from, it provides the ID attribute
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class User(AbstractUser):
    """
    This model represents users in the db
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        """
        If the user has a first and last name, show it, otherwise show the username

        @return: The first/last name if available, otherwise the username
        @rtype: str
        """

        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.username


class GalleryPhoto(PhotoMixin, BaseModel):
    """
    This class represents a GalleryPhoto in the db
    """

    caption = models.CharField(max_length=1000)
    date_posted = models.DateTimeField(auto_now_add=True)
    featured = models.BooleanField(default=False,
                                   help_text="This will determine whether to show this image on the home page "
                                             "(Max of 6)")

    def __str__(self):
        """
        Defines how this object will be cast to a string
        @return: A string that can be used to represent the image
        @rtype: str
        """

        return f"Photo Captioned: \"{self.caption}\""

    class Meta:
        ordering = ['-date_posted']


class ExternalLink(OrderedMixin, BaseModel):
    """
    This class represents External Links (Quick Links) in the db
    """

    url = models.URLField(max_length=350)
    display_name = models.CharField(max_length=100)

    def __str__(self):
        """
        Defines how this object will be cast to a string

        @return: A string that can be used to represent the link
        @rtype: str
        """

        return f"{self.display_name}"


class Event(BaseModel):
    """
    This class represents an Event in the db
    """

    name = models.CharField(max_length=100)
    virtual = models.BooleanField(default=False)
    location = models.CharField(max_length=200, blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    description = models.TextField(max_length=500, default="No description provided")
    startDate = models.DateField()
    endDate = models.DateField()
    startTime = models.TimeField()
    endTime = models.TimeField()

    def clean(self):
        """
        Ensures the startTime is after the endTime, and the startDate is after the endDate
        """

        if self.startDate == self.endDate:
            if self.startTime > self.endTime:
                raise ValidationError("Start time is after end time!")
        elif self.startDate > self.endDate:
            raise ValidationError("Start date is after end date!")
        if self.virtual:
            if self.link is None:
                raise ValidationError({"link": "Please fill out this field"})
            else:
                self.location = None
        else:
            if self.location is None:
                raise ValidationError({"location": "Please fill out this field"})
            else:
                self.link = None

    def __str__(self):
        """
        Defines how this object will be cast to a string

        @return: The event's name
        @rtype: str
        """

        return self.name

    def as_json_script(self):
        """
        Gives a version of the event that can be parsed as JSON, used in the calendar view

        @return: The json representation of this event
        @rtype: str
        """

        raw_dict = {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "startDate": self.startDate.strftime("%x"),
            "endDate": self.endDate.strftime("%x"),
            "startTime": self.startTime.strftime("%I:%M %p"),
            "endTime": self.endTime.strftime("%I:%M %p"),
            "virtual": self.virtual,
            "link": self.link,
            "location": self.location
        }

        return escape(dumps(raw_dict))

    class Meta:
        ordering = ["-startDate", "-endDate", "-startTime", "-endTime"]


class Officer(OrderedMixin, PhotoMixin, BaseModel):
    """
    This class represents an Officer in the db
    """

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    biography = models.TextField(max_length=2000)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)

    def masked_email_link(self):
        """
        Gets the officer's email as a link, the link is like this to prevent scraping

        @return: The officer's email "encoded" to a more secure string
        @rtype: str
        """

        if self.email:
            char_codes = [str(ord(character)) for character in list(self.email)]
            return f'javascript:void(location.href="mailto:"+String.fromCharCode({",".join(char_codes)}))'
        else:
            return "#"

    def masked_phone_link(self):
        """
        Gets the officer's phone as a link, the link is like this to prevent scraping

        @return: The officer's phone "encoded" to a more secure string
        @rtype: str
        """

        if self.phone:
            char_codes = [str(ord(character)) for character in list(self.phone)]
            return f'javascript:void(location.href="tel:"+String.fromCharCode({",".join(char_codes)}))'
        else:
            return "#"

    def __str__(self):
        """
        Defines how this object will be cast to a string

        @return: The officer's name
        @rtype: str
        """

        return f"{self.first_name} {self.last_name}"


class Social(OrderedMixin, BaseModel):
    """
    This class represents a Social Media Page in the db
    """

    class Services(models.TextChoices):
        """
        This class represents all the choices the user has for social media pages
        """

        TWITTER = "TW", "Twitter"
        INSTAGRAM = "IG", "Instagram"
        YOUTUBE = "YT", "YouTube"
        FACEBOOK = "FB", "Facebook"
        LINKEDIN = "LI", "Linkedin"
        PINTEREST = "PT", "Pinterest"

    service = models.CharField(max_length=2, choices=Services.choices, default=Services.TWITTER)
    link = models.URLField(max_length=350)

    def service_label(self):
        """
        Gets the label of this Social Media Page's service
        (YT -> "YouTube")

        @return: The label for the service this Social Media Page uses
        @rtype: str
        """

        return self.Services.labels[self.Services.values.index(self.service)]

    @classmethod
    def service_label_from_string(cls, service):
        """
        Gets the label of a given Social Media Service's 2-letter code
        (YT -> "YouTube")

        @return: The label for the service
        @rtype: str
        """

        return cls.Services.labels[cls.Services.values.index(service)]

    def fa_icon_class(self):
        """
        Gets the font awesome class that this social media uses

        @return: The font awesome class to use to make the icon for this social media page
        @rtype: str
        """

        if self.service == "LI":
            return "fa-linkedin"
        else:
            return f"fa-{self.service_label().lower()}-square"

    def __str__(self):
        """
        Defines how this object will be cast to a string

        @return: The social media service's name
        @rtype: str
        """

        return f"Berks Dental Assistants' {self.service_label()} Page"
