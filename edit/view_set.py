"""
    This file contains a base class from which classes can inherit
    This base class provides a way to handle generating and processing many parts of the admin site
    It provides methods like pre_save and post_save to allow for customization and additional behaviour
    Classes that inherit from the base class must specify a model, and a form to use
"""

from uuid import UUID

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import FieldDoesNotExist
from django.core.paginator import Paginator
from django.db import models as model_fields
from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import slugify, escape
from django.urls import reverse
from django.views.decorators.http import require_safe, require_http_methods

from edit import forms, exceptions

formatters = {
    model_fields.URLField: lambda input_val: f'<a class="link-value" rel="noopener" target="_blank"'
                                             f' href="{escape(str(input_val))}">'
                                             f'{escape(str(input_val))}</a>',
    model_fields.ImageField: lambda input_val: f'<a class="link-value" target="_blank"'
                                               f' href="{settings.MEDIA_URL}{escape(input_val)}"'
                                               f'>Click To View Image</a> ',
    model_fields.BooleanField: lambda input_val: f'<i class="fas '
                                                 f'{"fa-check-circle" if input_val is True else "fa-times-circle"}'
                                                 f' fa-lg bool-icon"></i>',
    model_fields.TimeField: lambda input_val: input_val.strftime("%I:%M %p"),
    model_fields.DateField: lambda input_val: input_val.strftime("%d-%m-%y")
}


class Action:
    def __init__(self, name, icon, link):
        self.name = name
        self.icon = icon
        self.link = link


class ViewSet:
    """ A class used to manage and render models easily, this class is meant to be inherited

    @type displayName: str
    @type model: class:`django.db.models.Model`
    @type modelForm: class:`django.forms.ModelForm`
    @type ordered: bool
    @type displayFields: list(str)
    @type labels: str
    """

    displayName: str = "base"
    pictureClass: str = "fa-edit"
    additionalActions: list = []
    model = None
    modelForm = None
    ordered: bool = False
    per_page: int = 10
    displayFields: list = []
    labels: dict = {}

    def __init__(self):
        """
        Checks the class to ensure the inheritor has been configured correctly

        @raise edit.exceptions.ImproperlyConfiguredViewSetError
        """

        if self.model is None:
            raise exceptions.ImproperlyConfiguredViewSetError("No Model Set")
        if self.modelForm is None:
            raise exceptions.ImproperlyConfiguredViewSetError("No Model Form Set")

        self.format_list = []

        for field in self.displayFields:
            try:
                field_object = self.model._meta.get_field(field)
                self.format_list.append(formatters.get(type(field_object), lambda input_val: str(input_val)))
            except FieldDoesNotExist:
                raise exceptions.ImproperlyConfiguredViewSetError(f"No Field Named: {field} "
                                                                  f"(double-check displayFields)")

        if self.ordered:
            try:
                self.model._meta.get_field("sort_order")
            except FieldDoesNotExist:
                raise exceptions.ImproperlyConfiguredViewSetError("Ordered Is True,"
                                                                  " but Model Doesn't Have sort_order Field")

        if self.per_page <= 0:
            raise exceptions.ImproperlyConfiguredViewSetError("per_page Must Be Over 0")

        for field in self.labels.keys():
            try:
                self.model._meta.get_field(field)
                if field not in self.displayFields:
                    raise exceptions.ImproperlyConfiguredViewSetError(f"{field} is a field, on the model,"
                                                                      f" but it is not included in displayFields"
                                                                      f" (labels)")
            except FieldDoesNotExist:
                raise exceptions.ImproperlyConfiguredViewSetError(f"Labels Contains Unknown Field: {field}")

        for action in self.additionalActions:
            if action.__class__.__name__ != "Action":
                raise exceptions.ImproperlyConfiguredViewSetError("additionalActions contains a non-action object")

    def format_value_list(self, value_list):
        """
        This function formats values to a more suitable format
        Like making links go in a tags, making booleans render as checkmarks or crosses etc.

        @param value_list: The list of tuples to format
        @type value_list: list
        """

        new_value_list = [list(obj) for obj in value_list]

        for obj_counter in range(0, len(new_value_list)):
            for value_counter in range(0, len(new_value_list[obj_counter]) - 1):
                new_value_list[obj_counter][value_counter] = self.format_list[value_counter](
                    new_value_list[obj_counter][value_counter])

        return new_value_list

    def pre_save(self, new_obj, form_data, new):
        """
        Before saving an object, this function will run

        @param new_obj: The object to be saved, will be None is the object is new
        @type new_obj: Model
        @param form_data: Form data from the request, in case the inheritor needs it
        @type form_data: dict
        @param new: Whether this object is new
        @type new: bool
        """

        pass

    def post_save(self, new_obj, form_data, new):
        """
        After saving an object, this function will run

        @param new_obj: The object that was saved
        @type new_obj: Model
        @param form_data: Form data from the request, in case the inheritor needs it
        @type form_data: dict
        @param new: Whether this object is new
        @type new: bool
        """

        pass

    def get_form_object(self, data_sources, instance=None):
        """
        This function is run to get the form object, this can be overridden if the inheritor needs it
        @param data_sources: Sources to create the form from (POST, FILES, etc.)
        @type data_sources: list[str]
        @param instance: The instance the form may get data from
        @type instance: Model
        @return: The form object to render/validate
        @rtype: Form
        """

        return self.modelForm(*data_sources, initial=self.additional_form_data(instance), instance=instance)

    def additional_form_data(self, obj):
        """
        Additional form data to pass as a data source

        @param obj: The instance the inheritor may read from
        @return: A dict with additional form data
        @rtype: dict
        """

        return {}

    def pre_del(self, obj_to_delete):
        """
        Before deleting an object, this function will run

        @param obj_to_delete: The object to be deleted
        @type obj_to_delete: Model
        """

        pass

    def post_del(self, obj_deleted):
        """
        After deleting an object, this function will run

        @param obj_deleted: The object that was deleted (ReadOnly)
        @type obj_deleted: Model
        """

        pass

    def get_safe_name(self):
        """
        Get a URL/File safe name for this ViewSet

        @return: A name that can be used internally to referrer to the ViewSet
        @rtype: str
        """

        current_name = self.displayName.lower()
        current_name = slugify(current_name.replace(" ", "_"))
        return current_name

    def gen_perms(self, actions, include_app_name=True):
        """
        Get a list of permission codenames for this ViewSet based off actions

        @param actions: The actions you want to generate permissions for
        @type actions: list[str]
        @param include_app_name: Whether to include the app name
        (needed to convert from codename to permission object)
        @type include_app_name: bool
        @return: A list of permission codenames you can use
        @rtype: list[str]
        """

        perms = []
        for action in actions:
            if include_app_name:
                perms.append(f"edit.{action}_{self.model.__name__.lower()}")
            else:
                perms.append(f"{action}_{self.model.__name__.lower()}")
        return perms

    def get_permissions_as_dict(self, include_app_name=True):
        """
        Gets permissions as a dictionary
        @param include_app_name: Whether to include the app name
        (needed to convert from codename to permission object)
        @type include_app_name: bool
        @return: A dictionary of permission codenames
        @rtype: dict
        """

        return {
            "Edit": self.gen_perms(["change", "add", "delete"], include_app_name=include_app_name),
            "View": self.gen_perms(["view"], include_app_name=include_app_name),
            "*": self.gen_perms(["change", "add", "delete", "view"], include_app_name=include_app_name),
            "None": []
        }

    def get_link(self, link_type):
        """
        Gets a link for this ViewSet based off an action (view, edit, delete, etc.)

        @param link_type: The action for the link
        @type link_type: str
        @return: A link to the requested action for this ViewSet
        @rtype: str
        """

        return reverse(f"edit:{self.get_safe_name()}_{link_type}")

    def overview_link(self):
        """
        Gets the overview link for this ViewSet

        @return: The overview link
        @rtype: str
        """

        return self.get_link("view")

    def edit_link(self):
        """
        Gets the edit link for this ViewSet

        @return: The edit link
        @rtype: str
        """

        return self.get_link("edit")

    def order_link(self):
        """
        Gets the re-order link for this ViewSet

        @return: The re-order link
        @rtype: str
        """

        if self.ordered:
            return self.get_link("order")
        else:
            return "#"

    def delete_link(self):
        """
        Gets the delete link for this ViewSet

        @return: The delete link
        @rtype: str
        """

        return self.get_link("delete")

    def obj_add(self, request):
        """
        This view is used to add an object to the database

        @param request: A django request object
        @type request: HttpRequest
        @return: A response to the request
        @rtype: HttpResponse
        """

        form = self.get_form_object([request.POST, request.FILES])

        if form.is_valid():
            self.pre_save(None, form.cleaned_data, True)
            new_obj = form.save()
            if self.ordered:
                new_obj.sort_order = len(list(self.model.objects.all())) - 1
                new_obj.save()
            self.post_save(new_obj, form.cleaned_data, True)
            return redirect(f'{self.overview_link()}?alert=New {self.displayName} Saved&alertType=success')
        else:
            return render(request, "db/form_base.html", {'form': form, 'viewSet': self, 'new': True, "verb": "Add",
                                                         "back_link": self.overview_link(),
                                                         'help_link': reverse("edit:help_edit")})

    def obj_edit(self, request):
        """
        This view is used to edit an object in the database

        @param request: A django request object
        @type request: HttpRequest
        @return: A response to the request
        @rtype: HttpResponse
        """

        target_obj = get_object_or_404(self.model, id=request.GET.get('id', ''))
        form = self.get_form_object([request.POST, request.FILES], instance=target_obj)

        if form.is_valid():
            self.pre_save(target_obj, form.cleaned_data, False)
            edited_obj = form.save()
            self.post_save(edited_obj, form.cleaned_data, False)
            return redirect(f'{self.overview_link()}?alert={self.displayName} Saved&alertType=success')
        else:
            return render(request, "db/form_base.html",
                          {'form': form, 'viewSet': self, 'new': False, "verb": "Edit",
                           "back_link": self.overview_link(), 'help_link': reverse("edit:help_edit")})

    def obj_delete_view(self, request):
        """
        This view is used to delete an object from the database

        @param request: A django request object
        @type request: HttpRequest
        @return: A response to the request
        @rtype: HttpResponse
        """

        form = forms.ConfirmDeleteForm()
        if request.method == "POST":
            target_obj = get_object_or_404(self.model, id=request.GET.get('id', ''))
            form.fields["confirm"].set_object_name(str(target_obj))
            self.pre_del(target_obj)
            target_obj.delete()
            if self.ordered:
                objects_to_fix = list(self.model.objects.filter(sort_order__gt=target_obj.sort_order))
                for object_to_fix in objects_to_fix:
                    object_to_fix.sort_order -= 1
                    object_to_fix.save()
            self.post_del(target_obj)
            return redirect(f'{self.overview_link()}?alert={self.displayName} Deleted&alertType=success')
        else:
            target_obj = get_object_or_404(self.model, id=request.GET.get('id', ''))
            form.fields["confirm"].set_object_name(str(target_obj))
            return render(request, "db/delete.html",
                          {'viewSet': self, "verb": "Delete",
                           "back_link": self.overview_link(), "form": form})

    def obj_edit_or_add_view(self, request):
        """
        This view is used to determine whether to add or edit (if an id is specified in the GET parameters)

        @param request: A django request object
        @type request: HttpRequest
        @return: A response to the request
        @rtype: HttpResponse
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
                form = self.get_form_object([])
                new = True
            else:
                try:
                    form = self.get_form_object([], instance=get_object_or_404(self.model, id=target_id))
                except ValidationError:
                    raise Http404()
            return render(request, 'db/form_base.html',
                          {'form': form, 'viewSet': self, 'new': new, "verb": "Add" if new else "Edit",
                           "back_link": self.overview_link(), 'help_link': reverse("edit:help_edit")})

    def object_order_view(self, request):
        """
        This view is used to arrange objects in the database

        @param request: A django request object
        @type request: HttpRequest
        @return: A response to the request
        @rtype: HttpResponse
        """

        if request.method == "POST":
            form = forms.OrderForm(request.POST)
            form.fields["new_order"].set_objects(self.model.objects.all())
            form.fields["new_order"].set_name(self.displayName)
            if form.is_valid():
                new_order = [UUID(raw_id) for raw_id in form.cleaned_data.get("new_order").split(",")]
                current_order = list(self.model.objects.values_list("id", flat=True).order_by("sort_order"))
                for target_id in current_order:
                    object_to_be_sorted = self.model.objects.get(id=target_id)
                    object_to_be_sorted.sort_order = new_order.index(target_id)
                    object_to_be_sorted.save()
                return redirect(f'{self.overview_link()}?alert=New Order Saved&alertType=success')
            else:
                return render(request, "db/form_base.html", {'viewSet': self, 'back_link': self.overview_link(),
                                                             'verb': "Re-Order", 'plural': True, "form": form,
                                                             'help_link': reverse("edit:help_ordering")})
        else:
            form = forms.OrderForm()
            form.fields["new_order"].set_objects(self.model.objects.all())
            form.fields["new_order"].set_name(self.displayName)
            return render(request, "db/form_base.html",
                          {'viewSet': self, 'back_link': self.overview_link(),
                           'verb': "Re-Order", 'plural': True, "form": form,
                           'help_link': reverse("edit:help_ordering")})

    def obj_overview_view(self, request):
        """
        This view is used to view objects in the database

        @param request: A django request object
        @type request: HttpRequest
        @return: A response to the request
        @rtype: HttpResponse
        """

        page_number = request.GET.get('page', 1)
        model_paginator = Paginator(self.model.objects.all(), self.per_page, allow_empty_first_page=True)
        page = model_paginator.get_page(page_number)
        start = page.start_index() - 1
        end = page.end_index()
        blank_link = "javascript:void(0);"
        next_link = blank_link
        last_link = blank_link
        previous_link = blank_link
        first_link = blank_link
        if page.has_next():
            next_link = f"{self.overview_link()}?page={page.next_page_number()}"
            last_link = f"{self.overview_link()}?page={model_paginator.num_pages}"
        if page.has_previous():
            previous_link = f"{self.overview_link()}?page={page.previous_page_number()}"
            first_link = f"{self.overview_link()}?page=1"
        headers = self.displayFields.copy()
        if start >= 0:
            objects = self.model.objects.all()[start:end].values_list(*self.displayFields, 'id')
        else:
            objects = []
        for target in self.labels.keys():
            if target in headers:
                headers[headers.index(target)] = self.labels[target]
        return render(request, 'db/view.html',
                      {'headers': headers, 'objects': self.format_value_list(objects), 'viewSet': self,
                       'canEdit': request.user.has_perms(self.get_permissions_as_dict()["Edit"]),
                       'back_link': reverse("edit:admin_home"), 'verb': "View/Edit",
                       'page': page, 'next_link': next_link, 'previous_link': previous_link, 'plural': True,
                       'max_pages': model_paginator.num_pages, 'help_link': reverse("edit:help_navigation"),
                       'first_link': first_link, 'last_link': last_link})

    @staticmethod
    def missing_permissions_link():
        """
        This is the link the user will be sent to if they're missing permissions to access a page

        @return: The link the user will be redirected to
        @rtype: str
        """

        missing_permissions_message = "You don't have sufficient permissions to perform this action"
        return f"{reverse('edit:admin_home')}?alert={missing_permissions_message}&alertType=error"

    def get_view_functions(self):
        """
        This is used a way to add decorators to view functions, such as require_safe and login_required

        @return: The view, edit, and delete Views
        @rtype: list[function]
        """

        @require_safe
        @login_required
        def viewset_overview(request):
            if request.user.has_perms(self.get_permissions_as_dict()["View"]):
                return self.obj_overview_view(request)
            else:
                return redirect(self.missing_permissions_link())

        @require_http_methods(["GET", "POST"])
        @login_required
        def viewset_edit_or_add(request):
            if request.user.has_perms(self.get_permissions_as_dict()["Edit"]):
                return self.obj_edit_or_add_view(request)
            else:
                return redirect(self.missing_permissions_link())

        @require_http_methods(["GET", "POST"])
        @login_required
        def viewset_delete(request):
            if request.user.has_perms(self.get_permissions_as_dict()["Edit"]):
                return self.obj_delete_view(request)
            else:
                return redirect(self.missing_permissions_link())

        return viewset_overview, viewset_edit_or_add, viewset_delete

    def get_edit_order_view(self):
        """
        This is used a way to add decorators to the order view function

        @return: The order View
        @rtype: function
        """

        @require_http_methods(["GET", "POST"])
        @login_required()
        def edit_order_view(request):
            if request.user.has_perms(self.gen_perms(["change"])):
                return self.object_order_view(request)
            else:
                return redirect(self.missing_permissions_link())

        return edit_order_view
