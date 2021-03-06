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
from django.db import models as source_fields
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import path, reverse
from django.views.decorators.http import require_safe, require_http_methods

from edit import forms, models
from edit.exceptions import ImproperlyConfiguredViewSetError
from edit.view_set import ViewSet, formatters, Action
from edit.webcal import update_file


# The following classes inherit from the ViewSet class, and are used to add functionality to the models we want


class EventViewSet(ViewSet):
    displayName = "Event"
    pictureClass = "calendar-alt"
    model = models.Event
    modelForm = forms.EventForm
    displayFields = ['name', 'virtual', 'location', 'startDate', 'endDate']
    labels = {'location': "Location/Link", 'startDate': "Start Date", 'endDate': "End Date"}

    def format_value_list(self, value_list):
        new_value_list = super().format_value_list(value_list)

        for event in new_value_list:
            virtual_location = self.displayFields.index("virtual")
            location_index = self.displayFields.index("location")
            if "check" in event[virtual_location]:
                new_value = self.model.objects.get(id=event[-1]).link
                event[location_index] = formatters[source_fields.URLField](new_value)

        return new_value_list

    def post_save(self, new_obj, form_data, new):
        update_file()

    def post_del(self, obj_deleted):
        update_file()


class SocialViewSet(ViewSet):
    displayName = "Social Media Page"
    pictureClass = "share-alt"
    model = models.Social
    modelForm = forms.SocialForm
    ordered = True
    displayFields = ['service', 'link']

    def format_value_list(self, value_list):

        new_value_list = super().format_value_list(value_list)

        if "service" in self.displayFields:
            service_location = self.displayFields.index("service")
            for obj in new_value_list:
                obj[service_location] = self.model.service_label_from_string(obj[service_location])

        return new_value_list


class LinkViewSet(ViewSet):
    displayName = "Link"
    pictureClass = "link"
    model = models.ExternalLink
    modelForm = forms.LinkForm
    ordered = True
    displayFields = ['display_name', 'url']
    labels = {'display_name': "Name"}


class GalleryPhotoViewSet(ViewSet):
    displayName = "Photo"
    pictureClass = "images"
    model = models.GalleryPhoto
    modelForm = forms.PhotoForm
    # The photo-folder attribute tells the model where to store pictures
    photoFolder = "galleryphoto-pictures"
    displayFields = ["caption", "picture", "featured"]

    def rename_photo_file(self, photo_object):
        """
        This function renames the photo file uploaded to the GalleryPhoto object's id

        @param photo_object: The object with the photo file
        @type photo_object: Model
        """

        initial_path = photo_object.picture.path
        photo_object.picture.name = f"{self.photoFolder}/{photo_object.id}.{photo_object.get_extension()}"
        new_path = settings.MEDIA_ROOT + photo_object.picture.name
        if os.path.exists(new_path):
            os.remove(new_path)
        os.rename(initial_path, new_path)
        photo_object.save()

    def post_save(self, new_obj, form_data, new):

        if new or str(new_obj.id) not in new_obj.picture.name:
            self.rename_photo_file(new_obj)

    def pre_del(self, obj_to_delete):

        if os.path.exists(obj_to_delete.picture.path):
            os.remove(obj_to_delete.picture.path)


class OfficerViewSet(GalleryPhotoViewSet):
    displayName = "Officer"
    pictureClass = "user-tie"
    model = models.Officer
    modelForm = forms.OfficerForm
    photoFolder = "officer-pictures"
    ordered = True
    displayFields = ["first_name", "title", 'picture']
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

for view_set in REGISTERED_VIEWSETS:
    try:
        view_set()
    except ImproperlyConfiguredViewSetError as config_error:
        REGISTERED_VIEWSETS.remove(view_set)
        print(f"View Set: {view_set.displayName} Is Not Configured Correctly, And Will Be Removed")
        print(f"Error: {config_error}")


def gen_name_dict():
    """
    Generates a dictionary where ViewSet safe names are the keys, and their objects are the values

    @return: A dictionary that converts safe_name -> ViewSet
    @rtype: dict
    """

    names = {}
    for vs in REGISTERED_VIEWSETS:
        names[vs().get_safe_name()] = vs
    return names


VIEWSET_NAMES = gen_name_dict()


def get_viewset_by_safename(name):
    """
    This function gets the ViewSet object from its safe name

    @param name: The safe name of the target object
    @type name: str
    @return: The ViewSet object that was found, if any
    """

    return VIEWSET_NAMES.get(name, None)


def view_set_to_permission_pair(user, viewset):
    """
    This function is used to get the permissions the user has for a viewset

    @param user: The user to check
    @type user: User
    @param viewset: The ViewSet to check the permissions for
    @return: The permission level the user has for the viewset
    @rtype: str, str
    """

    vs = viewset()
    viewset_name = vs.get_safe_name()
    permission_level = "None"
    if user.has_perms(vs.get_permissions_as_dict()["*"]):
        permission_level = "*"
    elif user.has_perms(vs.get_permissions_as_dict()["View"]):
        permission_level = "View"

    return viewset_name, permission_level


class UserViewSet(ViewSet):
    displayName = "User"
    pictureClass = "users-cog"
    additionalActions = [Action("Change Password For", "fa-key", "/admin/password/user/")]
    model = models.User
    modelForm = forms.UserEditForm
    displayFields = ["username", "first_name", "email", "is_staff"]
    labels = {
        "is_staff": "Manager",
        "first_name": "Name",
    }

    def format_value_list(self, value_list):
        new_value_list = super().format_value_list(value_list)

        for user in new_value_list:
            first_name_index = self.displayFields.index("first_name")
            user[first_name_index] = str(self.model.objects.get(id=user[-1]))

        return new_value_list

    @staticmethod
    def gen_json_from_viewsets(user, viewsets):
        """
        This function is used to generate json to be sent to the PermissionField object

        @param user: The user to check permissions for
        @param viewsets: The viewset to check
        @return: A JSON string of all permissions for the list of viewsets
        @rtype: str
        """

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
                perms_to_add = vs().get_permissions_as_dict(include_app_name=False).get(raw_dict[vs_name], [])
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
        """
        This view is used to change a user's password

        @param request: A django request object
        @type request: HttpRequest
        @return: A response to the request
        @rtype: HttpResponse
        """

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
                               'back_link': self.overview_link(), "targetUser": str(target_user),
                               'help_link': reverse("edit:help_password")})
        else:
            form = forms.SetUserPasswordForm()
            form.set_user(target_user)
            return render(request, "db/change_password.html",
                          {"form": form, "viewSet": self, "new": False,
                           'back_link': self.overview_link(), "targetUser": str(target_user),
                           'help_link': reverse("edit:help_password")})

    def get_password_view_function(self):
        """
        This function is used to get the password view as a function

        @return: The change password view function
        @rtype: function
        """

        @login_required
        @require_http_methods(["GET", "POST"])
        def change_password(request):
            if request.user.has_perms(self.gen_perms(["edit", "view"])):
                return self.change_password_view(request)
            else:
                return redirect(self.missing_permissions_link())

        return change_password


def generate_paths_from_view_set(source_view_set):
    """
    This function creates path objects for all the views in a ViewSet
    @param source_view_set: The view set to get the views from
    @return: Path objects to be added to url_patterns
    @rtype: list[path]
    """

    view_set_instance = source_view_set()
    if issubclass(source_view_set, ViewSet):
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
        raise ValueError(f"{source_view_set.__name__} Won't Work! Please pass a class that *inherits* ViewSet!")


def setup_viewsets():
    """
    This function loops through each registered ViewSet and adds their views to the patterns

    @return: A list of paths to be added to url_patterns
    @rtype: list[path]
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
    """
    This view is used to show a user all of their available actions

    @param request: A django request object
    @type request: HttpRequest
    @return: A response to the request
    @rtype: HttpResponse
    """

    accessible_viewsets = []

    for vs in REGISTERED_VIEWSETS:
        vs_obj = vs()
        if request.user.has_perms(vs_obj.get_permissions_as_dict()["View"]):
            accessible_viewsets.append(vs_obj)

    if request.user.has_perms(UserViewSet().get_permissions_as_dict()["View"]):
        accessible_viewsets.append(UserViewSet())

    return render(request, 'admin_home.html', {"viewsets": accessible_viewsets,
                                               'hide_home': True})


def help_page(name, display_name):
    """
    This function is used as a shortcut to generate a view for a help page

    @param name: The name of the html file to display as a help page
    @type name: str
    @param display_name: The display name for the help page
    @type display_name: str
    @return: A path object for the help page
    @rtype: path
    """

    def render_function(request):
        return render(request, f"help/{name}.html", {"article_name": display_name, "back_link": reverse("edit:help")})

    return path(f"help/{name}", render_function, name=f"help_{name}")
