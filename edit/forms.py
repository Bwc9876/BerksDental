"""
    This file contains a collection of Forms, Fields, And Widgets that we use in form_base.html
"""

import os
from collections import Counter
from uuid import UUID

from django.conf import settings
from django.contrib.auth.password_validation import validate_password, ValidationError, \
    get_password_validators, password_validators_help_texts
from django.forms import Form, ModelForm, fields, PasswordInput
from django.forms.widgets import DateInput, TimeInput, ClearableFileInput, TextInput

from edit import models


def get_size_of_folder(folder_path):
    """
    Given the path of a folder, get its size

    @param folder_path: The path to a folder
    @type folder_path: str
    @return: The size of the folder in bytes
    @rtype: int
    """

    total_size = 0
    for dir_path, dir_names, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dir_path, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size


MAX_BYTES = 900000000


def check_media_quota():
    """
    Checks to ensure we won't go over the max amount of bytes we can store

    @return: whether we're close to going over the limit
    @rtype: bool
    """

    return get_size_of_folder(settings.MEDIA_ROOT) <= MAX_BYTES


class TimeSelectorField(TimeInput):
    """
    This class overrides the django TimeInput
    class and sets the html input type to "time"
    """

    input_type = 'time'


class DateSelectorField(DateInput):
    """ This class overrides the django DateInput
    class and sets the html input type to "date"
    """

    input_type = 'date'


class OrderInput(TextInput):
    """
    This input is used to allow the user to re-order the arrangemnt of objects with drag&drop
    """

    input_type = "hidden"
    template_name = "custom_widgets/OrderWidget.html"
    objects = []
    display_name = ""

    def get_context(self, name, value, attrs):
        """
        Get the context and add our custom values to it

        @return: New Context
        @rtype: dict
        """

        context = super().get_context(name, value, attrs)
        context['widget']['objects'] = self.objects
        context['widget']['viewset_display_name'] = self.display_name
        context['widget']['currentOrder'] = ",".join(self.get_current_order())
        return context

    def get_current_order(self):
        """
        Get the current order of objects

        @return: a list of objects in the current order
        @rtype: list
        """

        return [str(obj.id) for obj in self.objects]

    class Media:
        """
        This class defines additonal css and js we want to use in the input
        """

        css = {
            "all": ("admin/order.css",)
        }
        js = ("https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js",
              "https://cdn.jsdelivr.net/npm/jquery-sortablejs@latest/jquery-sortable.js", "admin/order.js")


class OrderField(fields.CharField):
    """
        This field uses the OrderWidget
    """

    widget = OrderInput()

    def set_objects(self, objects):
        """
        This sets the objects value of the widget

        @param objects: a list of objects
        @type objects: list
        """

        self.widget.objects = objects

    def set_name(self, name):
        """
        This sets the display name for the widget

        @param name: The new name to diaplay
        @type name: str
        """

        self.widget.display_name = name


class PermInput(TextInput):
    """
    This widget is used to allow the user to edit what other users can access and edit
    """

    input_type = "hidden"
    template_name = "custom_widgets/PermissionWidget.html"

    viewsets = []

    def get_context(self, name, value, attrs):
        """
        Get the context and add our custom values to it

        @return: New Context
        @rtype: dict
        """

        context = super().get_context(name, value, attrs)
        context['widget']['viewsets'] = self.viewsets
        return context

    class Media:
        """
        This class defines additonal css and js we want to use in the input
        """

        css = {
            "all": ("admin/permissionStyle.css",)
        }
        js = ("admin/permissionLogic.js",)


class PermField(fields.CharField):
    """
    This field uses the permissions widget
    """

    widget = PermInput

    def set_viewsets(self, viewsets):
        """
        This sets the viewsets the user can change permissions of

        @param viewsets: A list of viewsets that we can change permissions for
        @type viewsets: list
        """

        self.widget.viewsets = viewsets


class ConfirmWidget(TextInput):
    """
        This is a simple widget that asks the user if they're sure they want to delete an object
    """

    input_type = "hidden"
    template_name = "custom_widgets/ConfirmTextWidget.html"

    def get_context(self, name, value, attrs):
        """
        Get the context and add our custom values to it

        @return: New Context
        @rtype: dict
        """

        context = super().get_context(name, value, attrs)
        context['widget']['object_name'] = self.object_name
        return context

    class Media:
        """
        This class defines additonal css and js we want to use in the input
        """

        css = {
            "all": ("admin/confirm_style.css",)
        }


class ConfirmField(fields.CharField):
    """
    This field uses the ConfirmWidget
    """

    widget = ConfirmWidget

    def set_object_name(self, object_name):
        """
        Sets the objects name to display

        @param object_name: The name of an object that's being deleted
        @type object_name: str
        """

        self.widget.object_name = object_name


class PhotoField(ClearableFileInput):
    template_name = "custom_widgets/PhotoInput.html"


class LinkForm(ModelForm):
    """
    This form handles editting and adding links in the db
    """

    class Meta:
        model = models.ExternalLink
        fields = ['url', 'display_name']


class SocialForm(ModelForm):
    """
    This form handles editting and adding Social Media Pages to the db
    """

    class Meta:
        model = models.Social
        exclude = ['id', 'sort_order']


class PhotoForm(ModelForm):
    """
    This form handles editting and adding Gallery Photos to the db
    """

    def __init__(self, *args, **kargs):
        """
        Set the help text on the caption field to explain its purpose
        """

        super().__init__(*args, **kargs)
        self.fields['caption'].help_text = "This is required for accessibility," \
                                           " please provide a description of the picture"

    class Meta:
        model = models.GalleryPhoto
        fields = ['picture', 'caption', 'featured']
        widgets = {
            'picture': PhotoField
        }

    def clean(self):
        """
        This function ensures two things:
            1. Only 6 featured photos are active at one time
            2. We have enough space to save the picture
        """

        max_featured_photos = 6
        cleaned_data = super().clean()
        featured = cleaned_data.get("featured")

        if not check_media_quota():
            self.add_error("picture", "There is not enough space to upload this picture,"
                                      " please delete some older pictures to free up space")

        if featured is not None:
            currently_featured = len(list(models.GalleryPhoto.objects.filter(featured=True)))
            if featured and currently_featured >= max_featured_photos:
                msg = f"There are already {max_featured_photos} featured photos"
                self.add_error("featured", msg)


class OfficerForm(ModelForm):
    """
    This form handles adding and editting Officers to the db
    """

    class Meta:
        model = models.Officer
        exclude = ['id', 'sort_order', "width", "height"]
        widgets = {
            "picture": PhotoField
        }

    def __init__(self, *args, **kargs):
        """
        Set the biography field's textarea to have a more suitable row and column count
        """

        super().__init__(*args, **kargs)
        self.fields["biography"].widget.attrs.update(rows="4", cols="25")


class EventForm(ModelForm):
    """
    This form handles editting and adding events to the db
    """

    class Meta:
        model = models.Event
        exclude = ['id']
        widgets = {
            'startTime': TimeSelectorField,
            'endTime': TimeSelectorField,
            'startDate': DateSelectorField,
            'endDate': DateSelectorField
        }

    class Media:
        """
        This class defines extra css and js to include in the form
        """

        js = ("admin/event_form.js",)

    def __init__(self, *args, **kargs):
        """
        Sets label and help texts to more suitable values
        It also updates the description field to have differnt width/col
        """

        super().__init__(*args, **kargs)
        self.fields["virtual"].help_text = "Determines Whether We Should Display A Link Or A Location"
        self.fields["description"].widget.attrs.update(rows="4", cols="25")
        self.fields['startDate'].label = "Start Date"
        self.fields['endDate'].label = "End Date"
        self.fields['startTime'].label = "Start Time"
        self.fields['endTime'].label = "End Time"


class OrderForm(Form):
    """
    This form is used to change the sort order of objects (like Links or Social Media Pages)
    """

    new_order = OrderField()

    def __init__(self, *args, **kargs):
        """
        Sets the help text to explain how to use this form
        """

        super().__init__(*args, **kargs)
        self.fields["new_order"].help_text = 'Click and drag the handle (<i class="fas fa-grip-lines"></i>)' \
                                             ' on an item to move it.'

    def clean(self):
        """
        If the user uses the form, this should never fail, however, if the user uses another way to send the POST data
        We check to make sure everything is valid for security
        """

        cleaned_data = super().clean()
        new_order_raw = cleaned_data.get("new_order").split(",")
        if new_order_raw:
            try:
                new_order = [UUID(raw_id) for raw_id in new_order_raw]
                current_order = [UUID(raw_id) for raw_id in self.fields["new_order"].widget.get_current_order()]
                if Counter(new_order) != Counter(current_order):
                    self.add_error("new_order", "Error Setting New Order (Counter)")
            except ValueError:
                self.add_error("new_order", "Error Setting New Order (ValueError)")


class UserCreateForm(ModelForm):
    """
    This form is used to add a user to the db
    The main difference between this and the edit, is this one includes the password fields
    """

    new_password = fields.CharField(widget=PasswordInput)
    confirm_new_password = fields.CharField(widget=PasswordInput)
    permissions = PermField()

    class Meta:
        model = models.User
        fields = ["username", "first_name", "last_name", "email"]

    def __init__(self, *args, **kargs):
        """
        Show requirements for password, and change labels to more suitable names
        """

        super().__init__(*args, **kargs)
        validators = list(settings.AUTH_PASSWORD_VALIDATORS)
        for ignored in settings.IGNORED_VALIDATORS_FOR_NEW_PASSWORD:
            validators.remove(ignored)
        new_config = get_password_validators(validators)
        rule_list = password_validators_help_texts(password_validators=new_config)
        self.fields['username'].help_text = None
        self.fields['first_name'].widget.attrs.update(required=True)
        self.fields['last_name'].widget.attrs.update(required=True)
        self.fields['email'].widget.attrs.update(required=True)
        self.fields["new_password"].widget.attrs.update(autocomplete="new-password")
        self.fields["new_password"].help_text = "<br/>".join(rule_list)
        self.fields["confirm_new_password"].widget.attrs.update(autocomplete="new-password")

    def clean(self):
        """
        This validates the password, and makes sure the sonfirm password matches
        """

        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password", "")
        confirm_password = cleaned_data.get("confirm_new_password", "")
        if new_password != confirm_password:
            self.add_error("confirm_new_password", "Passwords don't match")
        try:
            validate_password(new_password, user=None)
        except ValidationError as ve:
            [self.add_error("new_password", error) for error in list(ve)]


class UserEditForm(ModelForm):
    """
    This form is used to edit details about a user
    This form cannot change a user's password, we use another page for that
    """

    permissions = PermField()

    class Meta:
        model = models.User
        fields = ["username", "email", "first_name", "last_name"]

    def __init__(self, *args, **kargs):
        """
        Sets variables to more suitable values, makes some fields required
        """

        super().__init__(*args, **kargs)
        self.fields['username'].help_text = None
        self.fields['first_name'].widget.attrs.update(required=True)
        self.fields['last_name'].widget.attrs.update(required=True)
        self.fields['email'].widget.attrs.update(required=True)


class SetUserPasswordForm(Form):
    """
    This form is used to set a users password
    """

    new_password = fields.CharField(widget=PasswordInput)
    confirm_new_password = fields.CharField(widget=PasswordInput)
    user = None

    def __init__(self, *args, **kargs):
        """
        Display the requirements for the new password
        """

        super().__init__(*args, **kargs)
        self.fields["new_password"].label = "New Password"
        rule_list = password_validators_help_texts()
        self.fields["new_password"].help_text = "<br/>".join(rule_list)
        self.fields["confirm_new_password"].label = "Confirm New Password"
        self.fields["new_password"].widget.attrs.update(autocomplete="new-password")
        self.fields["confirm_new_password"].widget.attrs.update(autocomplete="new-password")

    def set_user(self, user):
        """
        Set the user whose password we want to change
        """

        self.user = user

    def clean(self):
        """
        Validates the password and ensures that the passwords match
        """

        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password", "")
        confirm_password = cleaned_data.get("confirm_new_password", "")
        if new_password != confirm_password:
            self.add_error("confirm_new_password", "Passwords don't match")
        try:
            validate_password(new_password, user=self.user)
        except ValidationError as ve:
            [self.add_error("new_password", error) for error in list(ve)]


class ConfirmDeleteForm(Form):
    """
    This an extremely simple form that confirms a user wants to delete an object
    """

    confirm = ConfirmField()
