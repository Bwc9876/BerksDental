"""
    This file contains forms, which perform validation and render to html automatically
    We can also call .save() on an instance of this class to save it to the database
"""

from django.forms import ModelForm, ValidationError
from django.forms.widgets import DateInput, TimeInput

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

    class Meta:
        model = models.GalleryPhoto
        fields = ['picture', 'caption', 'featured']

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
            'dateOf': DateSelectorField
        }

    def __init__(self, *args, **kargs):
        """ This function is run when the class is instantiated
        It changes some of the labels for the field to more suitable names
        """

        super().__init__(*args, **kargs)
        self.fields['dateOf'].label = "Date"
        self.fields['startTime'].label = "Start Time"
        self.fields['endTime'].label = "End Time"

    def clean(self):
        """ This function is run to make sure that all fields are valid outside of formatting
        It ensures that the start and end times for the event make logical sense (startTime shouldn't be after endTime)
        """

        cleaned_data = super().clean()
        start_time = cleaned_data.get("startTime")
        end_time = cleaned_data.get("endTime")

        if start_time and end_time:
            if start_time > end_time:
                raise ValidationError("%(start)s is after %(end)s!", params={'start': start_time.strftime("%I:%M %p"),
                                                                             'end': end_time.strftime("%I:%M %p")},
                                      code="invalidTimes")
