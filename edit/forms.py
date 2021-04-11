"""
    This file contains forms, which perform validation and render to html automatically
    We can also call .save() on an instance of this class to save it to the database
"""
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password, ValidationError
from django.forms import Form, ModelForm, fields
from django.forms.widgets import DateInput, TimeInput, ClearableFileInput, TextInput

from edit import models


class TimeSelectorField(TimeInput):
    """ This class overrides the django :class:`django.forms.widgets.TimeInput`
    class and sets the html input type to "time"
    """

    input_type = 'time'


class DateSelectorField(DateInput):
    """ This class overrides the django :class:`django.forms.widgets.DateInput`
    class and sets the html input type to "date"
    """

    input_type = 'date'


class PermInput(TextInput):
    input_type = "hidden"
    template_name = "custom_widgets/PermissionWidget.html"

    viewsets = []

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['viewsets'] = self.viewsets
        return context


class PermField(fields.CharField):
    widget = PermInput

    def set_viewsets(self, viewsets):
        self.widget.viewsets = viewsets


class PasswordInput(TextInput):
    input_type = "password"


class PasswordField(fields.CharField):
    widget = PasswordInput


class PhotoField(ClearableFileInput):
    template_name = "custom_widgets/PhotoInput.html"


class LinkForm(ModelForm):
    """ This is a django Form object, which is used to edit the Link object in the database
    It only displays the url and display_name properties of the Link
    as the other fields aren't meant to be edited manually
    """

    class Meta:
        model = models.ExternalLink
        fields = ['url', 'display_name']


class SocialForm(ModelForm):
    """ This is a django Form object, which is used to edit the Link object in the database
    It only displays the name, icon, and url properties of the Link
    as the id fields isn't meant to be edited manually
    """

    class Meta:
        model = models.Social
        exclude = ['id', 'sort_order']


class PhotoForm(ModelForm):
    """ This is a django Form object, which is used to edit the GalleryPhoto object in the database
    It only displays the picture, caption, and featured properties of the GalleryPhoto
    as the other fields aren't meant to be edited manually
    """

    def __init__(self, *args, **kargs):

        super().__init__(*args, **kargs)
        self.fields['picture'].widget.attrs.update(target="_blank", rel="nofollow")

    class Meta:
        model = models.GalleryPhoto
        fields = ['picture', 'caption', 'featured']
        widgets = {
            'picture': PhotoField
        }

    def clean(self):
        """ This function is run to make sure that all fields are valid outside of formatting
        It ensures that there are only six featured photos at a time, in order to feature another photo,
        The user will need to un-set the featured attribute of another photo

        """

        max_featured_photos = 6
        cleaned_data = super().clean()
        featured = cleaned_data.get("featured")

        if featured is not None:
            currently_featured = len(list(models.GalleryPhoto.objects.filter(featured=True)))
            if featured and currently_featured >= max_featured_photos:
                msg = f"There are already {max_featured_photos} featured photos"
                self.add_error("featured", msg)


class OfficerForm(ModelForm):
    """ This is a django Form object, which is used to edit the Officer object in the database
    It displays all properties except id and sort_order, as both aren't meant to be edited manually
    """

    class Meta:
        model = models.Officer
        exclude = ['id', 'sort_order']


class EventForm(ModelForm):
    """ This is a django Form object, which is used to edit the Event object in the database
    It displays all properties except id, as id isn't meant to be edited manually

    It sets the widget to be used for the start and end time fields to :class:`TimeSelector`
    and the widget to be used for the dateOf field to be :class:`DateSelector`
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
        js = ("admin/eventForm.js",)

    def __init__(self, *args, **kargs):
        """ This function is run when the class is instantiated
        It changes some of the labels for the field to more suitable names
        """

        super().__init__(*args, **kargs)
        self.fields['startDate'].label = "Start Date"
        self.fields['endDate'].label = "End Date"
        self.fields['startTime'].label = "Start Time"
        self.fields['endTime'].label = "End Time"


class UserCreateForm(UserCreationForm):
    permissions = PermField()

    class Meta:
        model = models.User
        fields = ["username", "email", "password1", "password2", "first_name", "last_name"]

    class Media:
        js = ("admin/permissionLogic.js",)

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.fields['first_name'].widget.attrs.update(required=True)
        self.fields['last_name'].widget.attrs.update(required=True)
        self.fields['email'].widget.attrs.update(required=True)


class UserEditForm(ModelForm):
    permissions = PermField()

    class Meta:
        model = models.User
        fields = ["username", "email", "first_name", "last_name"]

    class Media:
        js = ("admin/permissionLogic.js",)

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.fields['first_name'].widget.attrs.update(required=True)
        self.fields['last_name'].widget.attrs.update(required=True)
        self.fields['email'].widget.attrs.update(required=True)


class SetUserPasswordForm(Form):
    new_password = PasswordField()
    confirm_new_password = PasswordField()
    user = None

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.fields["new_password"].label = "New Password"
        self.fields["confirm_new_password"].label = "Confirm New Password"

    def set_user(self, user):
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password", "")
        confirm_password = cleaned_data.get("confirm_new_password", "")
        if new_password != confirm_password:
            self.add_error("confirm_new_password", "Passwords don't match")
        try:
            validate_password(new_password, user=self.user)
        except ValidationError as ve:
            [self.add_error("new_password", error) for error in list(ve)]
