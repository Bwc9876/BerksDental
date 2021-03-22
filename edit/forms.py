"""
    This file contains forms, which perform validation and render to html automatically
    We can also call .save() to the database with this class to save it to the database
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

    It also sets the label to be shown for dateOf to just be Date for simplicity
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
        super().__init__(*args, **kargs)
        self.fields['dateOf'].label = "Date"
        self.fields['startTime'].label = "Start Time"
        self.fields['endTime'].label = "End Time"

    def clean(self):
        cleaned_data = super().clean()
        startTime = cleaned_data.get("startTime")
        endTime = cleaned_data.get("endTime")

        if startTime and endTime:
            if startTime > endTime:
                raise ValidationError("%(start)s is after %(end)s!", params={'start': startTime.strftime("%I:%M %p"),
                                                                             'end': endTime.strftime("%I:%M %p")},
                                      code="invalidTimes")
