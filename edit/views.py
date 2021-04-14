"""
    This is a collection of functions or "views" that will inevitably return :class:`django.http.HttpResponse` objects
    We use the "render" shortcut to render an HTML file using template tags and return it as an HttpResponse object
    Sometimes, we raise Http404 to display a page not found screen (ex: if an id is incorrect)
    We register what url patterns go to what views in urls.py
    The templates (html files) we render should be contained in the templates/ folder
"""

import os
from json import dumps, loads

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import path
from django.db import models as source_fields
from django.views.decorators.http import require_safe, require_http_methods

from edit import forms, models
from edit.viewSet import EditViewSet, formatters


class Action:
    def __init__(self, name, icon, link):
        self.name = name
        self.icon = icon
        self.link = link


# The following classes inherit from EditViewSet class, and are used to add functionality to the models we want


class EventViewSet(EditViewSet):
    displayName = "Event"
    pictureClass = "fa-calendar-alt"
    model = models.Event
    modelForm = forms.EventForm
    displayFields = ['name', 'virtual', 'location', 'startDate', 'endDate']
    labels = {'location': "Location/Link", 'startDate': "Start Date", 'endDate': "End Date", 'startTime': "Start Time",
              'endTime': "End Time"}

    def format_value_list(self, value_list):
        new_value_list = super().format_value_list(value_list)

        for event in new_value_list:
            virtual_location = self.displayFields.index("virtual")
            location_index = self.displayFields.index("location")
            if "check" in event[virtual_location]:
                new_value = self.model.objects.get(id=event[-1]).link
                event[location_index] = formatters[source_fields.URLField](new_value)

        return new_value_list


class SocialViewSet(EditViewSet):
    displayName = "Social Media Page"
    pictureClass = "fa-share-alt"
    model = models.Social
    modelForm = forms.SocialForm
    ordered = True
    displayFields = ['service', 'link']

    def format_value_list(self, value_list):
        """ This function overrides the format_value_list function the EditViewSet class
        it does this in order to provide additional formatting
        The formatting we provide is making sure the label for the social media we chose is shown and not the code
        ("YT" -> "YouTube", "IG" -> "Instagram")

        :param value_list:
        :return:
        """

        new_value_list = super().format_value_list(value_list)

        if "service" in self.displayFields:
            service_location = self.displayFields.index("service")
            for obj in new_value_list:
                obj[service_location] = self.model.service_label_from_string(obj[service_location])

        return new_value_list


class LinkViewSet(EditViewSet):
    displayName = "Link"
    pictureClass = "fa-link"
    model = models.ExternalLink
    modelForm = forms.LinkForm
    ordered = True
    displayFields = ['display_name', 'url']
    labels = {'display_name': "Name"}


class GalleryPhotoViewSet(EditViewSet):
    displayName = "Photo"
    pictureClass = "fa-images"
    model = models.GalleryPhoto
    modelForm = forms.PhotoForm
    # The photo-folder attribute tells the model where to store pictures
    photoFolder = "gallery-photos"
    displayFields = ["picture", "caption", "featured"]

    def rename_photo_file(self, photo_object):
        """ This function is used to rename the picture uploaded by the user to the photo's id
        This is to prevent naming conflicts

        :param photo_object: The GalleryPhoto object that we want to rename the file of
        """

        initial_path = photo_object.picture.path
        photo_object.picture.name = f"{self.photoFolder}/{photo_object.id}.{photo_object.get_extension()}"
        new_path = settings.MEDIA_ROOT + photo_object.picture.name
        if os.path.exists(new_path):
            os.remove(new_path)
        os.rename(initial_path, new_path)
        photo_object.save()

    def post_save(self, new_obj, form_data, new):
        """ This function is run after a GalleryPhoto object is added/edited
        It renames the pictures file to prevent naming conflicts

        """

        if new or str(new_obj.id) not in new_obj.picture.name:
            self.rename_photo_file(new_obj)

    def pre_del(self, obj_to_delete):
        """ This code is run before the GalleryPhoto object is deleted from the database
        It deletes the picture if it still exists

        """

        if os.path.exists(obj_to_delete.picture.path):
            os.remove(obj_to_delete.picture.path)


class OfficerViewSet(GalleryPhotoViewSet):
    displayName = "Officer"
    pictureClass = "fa-user-tie"
    model = models.Officer
    modelForm = forms.OfficerForm
    photoFolder = "officer-photos"
    ordered = True
    displayFields = ["first_name", 'picture']
    labels = {
        "first_name": "Name"
    }

    def format_value_list(self, value_list):
        new_value_list = super().format_value_list(value_list)

        for officer in new_value_list:
            first_name_index = self.displayFields.index("first_name")
            officer[first_name_index] = str(self.model.objects.get(id=officer[-1]))

        return new_value_list


REGISTERED_VIEWSETS = [EventViewSet, LinkViewSet, GalleryPhotoViewSet, OfficerViewSet, SocialViewSet]


def gen_name_dict():
    names = {}
    for vs in REGISTERED_VIEWSETS:
        names[vs().get_safe_name()] = vs
    return names


VIEWSET_NAMES = gen_name_dict()


def get_viewset_by_safename(name):
    return VIEWSET_NAMES.get(name, None)


def view_set_to_permission_pair(user, viewset):
    vs = viewset()
    viewset_name = vs.get_safe_name()
    permission_level = "none"
    if user.has_perms(vs.get_permissions_as_dict()["*"]):
        permission_level = "edit"
    elif user.has_perms(vs.get_permissions_as_dict()["View"]):
        permission_level = "view"

    return viewset_name, permission_level


class UserViewSet(EditViewSet):
    displayName = "User"
    pictureClass = "fa-users-cog"
    additionalActions = [Action("Change Password For", "fa-key", "/admin/password/user/")]
    model = models.User
    modelForm = forms.UserEditForm
    displayFields = ["username", "first_name", "email", "is_staff"]
    labels = {
        "is_staff": "Manager",
        "first_name": "Name",
        "last_login": "Last Login"
    }

    PERMISSION_JSON_TO_VIEWSET = {
        "edit": "*",
        "view": "View",
        "none": "None"
    }

    def format_value_list(self, value_list):
        new_value_list = super().format_value_list(value_list)

        for user in new_value_list:
            first_name_index = self.displayFields.index("first_name")
            user[first_name_index] = str(self.model.objects.get(id=user[-1]))

        return new_value_list

    @staticmethod
    def gen_json_from_viewsets(user, viewsets):
        output_dictionary = {}
        for vs in viewsets:
            name, level = view_set_to_permission_pair(user, vs)
            output_dictionary[name] = level
        return dumps(output_dictionary)

    def additional_form_data(self, obj):
        if obj is None:
            return {"permissions": "{}"}
        else:
            return {"permissions": self.gen_json_from_viewsets(obj, REGISTERED_VIEWSETS)}

    def post_save(self, user, form_data, new):
        if new:
            new_password = form_data.get("new_password", "")
            user.set_password(new_password)
        raw_dict = loads(form_data.get("permissions", "{}"))
        target_perms = []
        for vs_name in raw_dict.keys():
            vs = get_viewset_by_safename(vs_name)
            if vs is not None:
                perms_to_add = vs().get_permissions_as_dict(include_app_name=False)[
                    self.PERMISSION_JSON_TO_VIEWSET.get(raw_dict[vs_name], "None")]
                target_perms += [Permission.objects.get(codename=perm) for perm in perms_to_add]
        user.user_permissions.set(target_perms)
        user.save()

    def get_form_object(self, data_sources, instance=None):
        if instance is None:
            user_form = forms.UserCreateForm(*data_sources, initial=self.additional_form_data(instance))
            user_form.fields["permissions"].set_viewsets(REGISTERED_VIEWSETS)
            return user_form
        else:
            user_form = super().get_form_object(data_sources, instance=instance)
            user_form.fields["permissions"].set_viewsets(REGISTERED_VIEWSETS)
            return user_form

    def change_password_view(self, request):
        target_id = request.GET.get("id", "")
        target_user = get_object_or_404(models.User, id=target_id)
        if request.method == "POST":
            form = forms.SetUserPasswordForm(request.POST)
            form.set_user(target_user)
            if form.is_valid():
                new_password = form.cleaned_data.get("new_password", "")
                target_user.set_password(new_password)
                target_user.save()
                return redirect(f'{self.overview_link()}?alert=Password Changed&alertType=success')
            else:
                return render(request, "db/change_password.html",
                              {"form": form, "viewSet": self, "new": False,
                               'back_link': self.overview_link(), "targetUser": str(target_user)})
        else:
            form = forms.SetUserPasswordForm()
            form.set_user(target_user)
            return render(request, "db/change_password.html",
                          {"form": form, "viewSet": self, "new": False,
                           'back_link': self.overview_link(), "targetUser": str(target_user)})

    def get_password_view_function(self):

        @require_http_methods(["GET", "POST"])
        def change_password(request):
            if request.user.has_perms(self.gen_perms(["edit", "view"])):
                return self.change_password_view(request)
            else:
                return redirect(self.missing_permissions_link())

        return change_password


def generate_paths_from_view_set(view_set):
    """ This function will add give the url patterns for a given :class:`EditViewSet` class

    :param view_set: The :class:`EditViewSet` class to generate the url patterns for
    :returns: A list of paths with the :class:`EditViewSet`'s url patterns
    :rtype: list(:class:`django.urls.path`)
    """

    view_set_instance = view_set()
    if issubclass(view_set, EditViewSet):
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
        raise ValueError(f"{view_set.__name__} Won't Work! Please pass a class that *inherits* EditViewSet!")


def setup_viewsets():
    """ This function gives the url patterns for all the models we want

    :returns: The list of wanted patterns for the models
    :rtype: list(:class:`django.urls.path`)
    """

    new_patterns = []
    for viewset in REGISTERED_VIEWSETS:
        new_patterns += generate_paths_from_view_set(viewset)

    new_patterns += generate_paths_from_view_set(UserViewSet)
    new_patterns.append(path("password/user/", UserViewSet().get_password_view_function(), name="password_user"))

    return new_patterns


@require_safe
@login_required
def admin_home(request):
    """ A django view function, this will render and send the admin_home.html file

    :param request: A request object sent by django
    :type request: class:`django.http.HttpRequest`
    :returns: An HttpResponse containing the rendered html file
    :rtype: class:`django.http.HttpResponse`

    """

    accessible_viewsets = []

    for vs in REGISTERED_VIEWSETS:
        vs_obj = vs()
        if request.user.has_perms(vs_obj.get_permissions_as_dict()["View"]):
            accessible_viewsets.append(vs_obj)

    if request.user.has_perms(UserViewSet().get_permissions_as_dict()["View"]):
        accessible_viewsets.append(UserViewSet())

    return render(request, 'admin_home.html', {"viewsets": accessible_viewsets})
