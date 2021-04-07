"""
    This is a collection of functions or "views" that will inevitably return :class:`django.http.HttpResponse` objects
    We use the "render" shortcut to render an html file using template tags and return it as an HttpResponse object
    Sometimes, we raise Http404 to display a page not found screen (ex: if an id is incorrect)
    We register what url patterns go to what views in urls.py
    The templates (html files) we render should be contained in the templates/ folder
"""

import os
from collections import Counter
from uuid import UUID

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import models as model_fields
from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import slugify, escape
from django.urls import path, reverse
from django.views.decorators.http import require_safe, require_http_methods

from edit import forms, models


@require_safe
@login_required
def admin_home(request):
    """ A django view function, this will render and send the admin_home.html file

    :param request: A request object sent by django
    :type request: class:`django.http.HttpRequest`
    :returns: An HttpResponse containing the rendered html file
    :rtype: class:`django.http.HttpResponse`

    """

    return render(request, 'admin_home.html')


class EditViewSet:
    """ A class used to manage and render models easily, this class is meant to be inherited

    :attr displayName: The name to display on html forms and certain links
    :type displayName: str
    :attr model: The model to edit using the view functions
    :type model: class:`django.db.models.Model`
    :attr modelForm: The form to render in the view functions
    :type modelForm: class:`django.forms.ModelForm`
    :attr ordered: A boolean, telling us if the order these objects appear in is editable
    :type ordered: bool
    :attr displayFields: A list of fields we want to be shown in the overview view
    :type displayFields: list(str)
    :attr labels: If theres any fields we want to be displayed differently,
    we put the field name as the key and the desired label as the value
    """

    displayName: str = "base"
    model = None
    modelForm = None
    ordered = False
    displayFields = []
    labels = {}

    formatters = {
        model_fields.URLField: lambda
            inputVal: f'<a target="_blank" href="{escape(str(inputVal))}">{escape(str(inputVal))}</a>',
        model_fields.ImageField: lambda
            inputVal: f'<a target="_blank" href="{settings.MEDIA_URL}{escape(inputVal)}">Click To '
                      f'View Image</a> ',
        model_fields.BooleanField: lambda
            inputVal: f'<i class="fas {"fa-check-circle" if inputVal is True else "fa-times-circle"} fa-lg"></i>',
        model_fields.TimeField: lambda inputVal: inputVal.strftime("%I:%M %p")
    }

    def __init__(self):
        """ This function is run when the ViewSet is instantiated
        It sets up a format list, which essentially tells us how each field of the object should be formatted
        """

        self.format_list = []
        for field in self.displayFields:
            field_object = self.model._meta.get_field(field)
            self.format_list.append(self.formatters.get(type(field_object), lambda inputVal: str(inputVal)))

    def format_value_list(self, valueList):
        """ This function is used as a way to format any values we read from the database, like dates and links
        It reads from the format_list and if the field name matches it, it'll fun teh lambda function specified

        :param valueList: A list of lists, each nested list containing the values for objects
        :type valueList: list(list(*))
        :returns: A new, formatted valueList
        :rtype: list(list(*))
        """

        new_value_list = [list(obj) for obj in valueList]

        for obj_counter in range(0, len(new_value_list)):
            for value_counter in range(0, len(new_value_list[obj_counter]) - 1):
                new_value_list[obj_counter][value_counter] = self.format_list[value_counter](
                    new_value_list[obj_counter][value_counter])

        return new_value_list

    def pre_save(self, newObj, new):
        """ The function to be run before an object is saved to the database
        For now, it just passes, but classes that inherit this can override this function

        :param newObj: The newObj that is about to be saved (if the item is being added, it will be :type:None)
        :type newObj: class:`django.db.models.Model`
        :param new: True if the object is just being added to the db, false if its being edited
        :type new: bool
        """

        pass

    def post_save(self, newObj, new):
        """ The function to be run after an object is saved to the database
        For now, it just passes, but classes that inherit this can override this function

        :param newObj: The newObj that has been saved
        :type newObj: class:`django.db.models.Model`
        :param new: True if the object is just being added to the db, false if its being edited
        :type new: bool
        """

        pass

    def pre_del(self, objToDelete):
        """ The function to be run before an object is deleted from the database
        For now, it just passes, but classes that inherit this can override this function

        :param objToDelete: The object that is about to be deleted
        :type objToDelete: class:`django.db.models.Model`
        """

        pass

    def post_del(self, objDeleted):
        """ The function to be run after an object is deleted from the database
        For now, it just passes, but classes that inherit this can override this function

        :param objDeleted: The object that has been deleted (the data will still be passed, but the db row is deleted)
        :type objDeleted: class:`django.db.models.Model`
        """

        pass

    def get_safe_name(self):
        """ This function is run to get the name of this view set as a url/template syntax safe string
        it gets rid of spaces in favor of underscores, and makes the name lowercase

        :returns: A safe name to be used in template syntax and url patterns
        :rtype: str
        """

        current_name = self.displayName.lower()
        current_name = slugify(current_name.replace(" ", "_"))
        return current_name

    def get_link(self, linkType):
        """ This function is used to get and reverse a url name with a given type.
         So passing "add" when the model is "ExternalLink" will resolve to the url "/admin/edit/link/"

        :param linkType: The type of url we want to reverse
        :type linkType: str
        :returns: The link to hte requested url
        :rtype: str
        """

        return reverse(f"edit:{self.get_safe_name()}_{linkType}")

    def overview_link(self):
        """ A function used to get the link that can be used to redirect to the overview page for this model

        :returns: The link to be used in the redirect
        :rtype: str
        """

        return self.get_link("view")

    def edit_link(self):
        """ A function used to get the link that can be used to redirect to the edit page for this model

        :returns: The link to be used in the redirect
        :rtype: str
        """

        return self.get_link("edit")

    def order_link(self):
        """ A function used to get the link that can be used to redirect to the re-order page for this model

        :returns: The link to be used in the redirect
        :rtype: str
        """

        if self.ordered:
            return self.get_link("order")
        else:
            return "#"

    def delete_link(self):
        """ A function used to get the link that can be used to redirect to the delete page for this model

        :returns: The link to be used in the redirect
        :rtype: str
        """

        return self.get_link("delete")

    def obj_add(self, request):
        """ A django view function, this will add the model to the database given form data
        If the form is invalid, it re-renders the html and sends it back to the user
        If the form is valid, it will redirect to the overview page

        :param request: A request object sent by django
        :type request: class:`django.http.HttpRequest`
        :returns: An HttpResponse containing the rendered html file
        :rtype: class:`django.http.HttpResponse`
        """

        form = self.modelForm(request.POST, request.FILES)

        if form.is_valid():
            self.pre_save(None, True)
            new_obj = form.save()
            if self.ordered:
                new_obj.sort_order = len(list(self.model.objects.all())) - 1
                new_obj.save()
            self.post_save(new_obj, True)
            return redirect(self.overview_link())
        else:
            return render(request, "db/edit.html", {'form': form, 'viewSet': self, 'new': True})

    def obj_edit(self, request):
        """ A django view function, this will edit the model on the database given form data
        If the form is invalid, it re-renders the html and sends it back to the user
        If the form is valid, it will redirect to the overview page

        :param request: A request object sent by django
        :type request: class:`django.http.HttpRequest`
        :returns: An HttpResponse containing the rendered html file
        :rtype: class:`django.http.HttpResponse`
        """

        target_obj = get_object_or_404(self.model, id=request.GET.get('id', ''))
        form = self.modelForm(request.POST, request.FILES, instance=target_obj)

        if form.is_valid():
            self.pre_save(target_obj, False)
            edited_obj = form.save()
            self.post_save(edited_obj, False)
            return redirect(self.overview_link())
        else:
            return render(request, "db/edit.html", {'form': form, 'viewSet': self, 'new': False})

    def obj_delete_view(self, request):
        """ A django view function, this will delete the model from the database given form data
        It will ask the user for confirmation that they would like to delete the object
        After the object is deleted, it will redirect to the overview page

        :param request: A request object sent by django
        :type request: class:`django.http.HttpRequest`
        :returns: An HttpResponse containing the rendered html file
        :rtype: class:`django.http.HttpResponse`
        """

        if request.method == "POST":
            target_obj = get_object_or_404(self.model, id=request.GET.get('id', ''))
            self.pre_del(target_obj)
            target_obj.delete()
            if self.ordered:
                objects_to_fix = list(self.model.objects.filter(sort_order__gt=target_obj.sort_order))
                for object_to_fix in objects_to_fix:
                    object_to_fix.sort_order -= 1
                    object_to_fix.save()
            self.post_del(target_obj)
            return redirect(self.overview_link())
        else:
            target_obj = get_object_or_404(self.model, id=request.GET.get('id', ''))
            return render(request, "db/delete.html", {'viewSet': self, 'objectName': target_obj})

    def obj_edit_or_add_view(self, request):
        """ A django view function, this will add the model to the database given form data
        This function uses the :func:`obj_add` and :func:`obj_edit` functions and combines them
        If an id is passed, we'll edit the object with that id
        If an id is not passed, we add the object to the database

        :param request: A request object sent by django
        :type request: class:`django.http.HttpRequest`
        :returns: An HttpResponse containing the rendered html file
        :rtype: class:`django.http.HttpResponse`
        """

        if request.method == "POST":
            target_id = request.GET.get('id', '')
            if target_id == '':
                return self.obj_add(request)
            else:
                try:
                    return self.obj_edit(request)
                except ValidationError:
                    raise Http404()
        else:
            target_id = request.GET.get('id', '')
            new = False
            if target_id == '':
                form = self.modelForm()
                new = True
            else:
                try:
                    form = self.modelForm(instance=get_object_or_404(self.model, id=target_id))
                except ValidationError:
                    raise Http404()

            return render(request, 'db/edit.html', {'form': form, 'viewSet': self, 'new': new})

    def object_order_view(self, request):
        """ This function allows the user to edit the order external links will appear with drag-and-drop
        On the backend, we expect a list of ids, we then get the links these ids are associates with
        and set the sort_order property of it to where the id is located from the incoming list

        :param request: A request object sent by django
        :type request: class:`django.http.HttpRequest`
        :returns: Either a page where the user can edit the order of links, or a redirect back to the overview page
        :rtype: :class:`django.http.HttpResponse`
        """

        if request.method == "POST":
            new_order_raw = request.POST.get("new_order", "").split(",")
            try:
                new_order = [UUID(raw_id) for raw_id in new_order_raw]
            except ValueError:
                new_order = []
            current_order = list(self.model.objects.values_list("id", flat=True).order_by("sort_order"))
            if Counter(new_order) == Counter(current_order):
                for target_id in current_order:
                    object_to_be_sorted = self.model.objects.get(id=target_id)
                    object_to_be_sorted.sort_order = new_order.index(target_id)
                    object_to_be_sorted.save()
                return redirect(self.overview_link())
            else:
                return render(request, 'db/order.html',
                              {'error': 'Invalid List!', 'objects': self.model.objects.all, 'viewSet': self})
        else:
            return render(request, "db/order.html", {'objects': self.model.objects.all(), 'viewSet': self})

    def obj_overview_view(self, request):
        """ A django view function, this will add the model to the database given form data
        It displays all the objects based off this model in the database as an html file

        :param request: A request object sent by django
        :type request: class:`django.http.HttpRequest`
        :returns: An HttpResponse containing the rendered html file
        :rtype: class:`django.http.HttpResponse`
        """

        headers = self.displayFields.copy()
        objects = self.model.objects.all().values_list(*self.displayFields, 'id')
        for target in self.labels.keys():
            if target in headers:
                headers[headers.index(target)] = self.labels[target]

        return render(request, 'db/view.html',
                      {'headers': headers, 'objects': self.format_value_list(objects), 'viewSet': self})

    def get_view_functions(self):
        """ This function sets up proxy functions
        We need to use the @login_required and other decorators, yet we can't use this within classes
        So we create functions that have the decorator that use the class

        :returns: Three view functions (overview, edit/add, delete)
        :rtype: function(3)
        """

        @require_safe
        @login_required
        def viewset_overview(request):
            return self.obj_overview_view(request)

        @require_http_methods(["GET", "POST"])
        @login_required
        def viewset_edit_or_add(request):
            return self.obj_edit_or_add_view(request)

        @require_http_methods(["GET", "POST"])
        @login_required
        def viewset_delete(request):
            return self.obj_delete_view(request)

        return viewset_overview, viewset_edit_or_add, viewset_delete

    def get_edit_order_view(self):
        @require_http_methods(["GET", "POST"])
        @login_required()
        def edit_order_view(request):
            return self.object_order_view(request)

        return edit_order_view


# The following classes inherit from EditViewSet class, and are used to add functionality to the models we want


class EventViewSet(EditViewSet):
    displayName = "Event"
    model = models.Event
    modelForm = forms.EventForm
    displayFields = ['name', 'virtual', 'location', 'startDate', 'endDate', 'startTime', "endTime"]
    labels = {'location': "Location/Link", 'startDate': "Start Date", 'endDate': "End Date", 'startTime': "Start Time",
              'endTime': "End Time"}

    def format_value_list(self, valueList):
        new_value_list = super().format_value_list(valueList)

        for event in new_value_list:
            virtual_location = self.displayFields.index("virtual")
            location_index = self.displayFields.index("location")
            if "check" in event[virtual_location]:
                new_value = self.model.objects.get(id=event[-1]).link
                event[location_index] = f'<a href="{new_value}">{new_value}</a>'

        return new_value_list


class SocialViewSet(EditViewSet):
    displayName = "Social Media Page"
    model = models.Social
    modelForm = forms.SocialForm
    ordered = True
    displayFields = ['service', 'link']

    def format_value_list(self, valueList):
        """ This function overrides the format_value_list function the EditViewSet class
        it does this in order to provide additional formatting
        The formatting we provide is making sure the label for the social media we chose is shown and not the code
        ("YT" -> "Youtube", "IG" -> "Instagram")

        :param valueList:
        :return:
        """

        new_value_list = super().format_value_list(valueList)

        if "service" in self.displayFields:
            service_location = self.displayFields.index("service")
            for obj in new_value_list:
                obj[service_location] = self.model.service_label_from_string(obj[service_location])

        return new_value_list


class LinkViewSet(EditViewSet):
    displayName = "Link"
    model = models.ExternalLink
    modelForm = forms.LinkForm
    ordered = True
    displayFields = ['display_name', 'url']
    labels = {'display_name': "Name"}


class GalleryPhotoViewSet(EditViewSet):
    displayName = "Photo"
    model = models.GalleryPhoto
    modelForm = forms.PhotoForm
    # The photo-folder attribute tells the model where to store pictures
    photoFolder = "gallery-photos"
    displayFields = ["picture", "caption", "featured"]

    def rename_photo_file(self, photoObject):
        """ This function is used to rename the picture uploaded by the user to the photo's id
        This is to prevent naming conflicts

        :param photoObject: The GalleryPhoto object that we want to rename the file of
        """

        initial_path = photoObject.picture.path
        photoObject.picture.name = f"{self.photoFolder}/{photoObject.id}.{photoObject.get_extension()}"
        new_path = settings.MEDIA_ROOT + photoObject.picture.name
        if os.path.exists(new_path):
            os.remove(new_path)
        os.rename(initial_path, new_path)
        photoObject.save()

    def post_save(self, newObj, new):
        """ This function is run after a GalleryPhoto object is added/edited
        It renames the pictures file to prevent naming conflicts

        """

        if new or str(newObj.id) not in newObj.picture.name:
            self.rename_photo_file(newObj)

    def pre_del(self, objToDelete):
        """ This code is run before the GalleryPhoto object is deleted from the database
        It deletes the picture if it still exists

        """

        if os.path.exists(objToDelete.picture.path):
            os.remove(objToDelete.picture.path)


class OfficerViewSet(GalleryPhotoViewSet):
    displayName = "Officer"
    model = models.Officer
    modelForm = forms.OfficerForm
    photoFolder = "officer-photos"
    ordered = True
    displayFields = ["name", 'picture']


def generate_paths_from_view_set(viewSet):
    """ This function will add give the url patterns for a given :class:`EditViewSet` class

    :param viewSet: The :class:`EditViewSet` class to generate the url patterns for
    :returns: A list of paths with the :class:`EditViewSet`'s url patterns
    :rtype: list(:class:`django.urls.path`)
    """

    view_set_instance = viewSet()
    if issubclass(viewSet, EditViewSet):
        url_name = view_set_instance.get_safe_name()

        overview, add_or_edit, delete = view_set_instance.get_view_functions()

        patterns_to_return = [
            path(f'overview/{url_name}/', overview, name=f"{url_name}_view"),
            path(f'edit/{url_name}/', add_or_edit, name=f"{url_name}_edit"),
            path(f'delete/{url_name}/', delete, name=f"{url_name}_delete")
        ]

        if view_set_instance.ordered:
            patterns_to_return.append(path(f"order/{url_name}/",
                                           view_set_instance.get_edit_order_view(), name=f"{url_name}_order"))

        return patterns_to_return
    else:
        raise ValueError(f"{viewSet.__name__} Won't Work! Please pass a class that *inherits* EditViewSet!")


def setup_viewsets():
    """ This function gives the url patterns for all the models we want

    :returns: The list of wanted patterns for the models
    :rtype: list(:class:`django.urls.path`)
    """

    new_patterns = []
    new_patterns += generate_paths_from_view_set(EventViewSet)
    new_patterns += generate_paths_from_view_set(LinkViewSet)
    new_patterns += generate_paths_from_view_set(GalleryPhotoViewSet)
    new_patterns += generate_paths_from_view_set(OfficerViewSet)
    new_patterns += generate_paths_from_view_set(SocialViewSet)
    return new_patterns
