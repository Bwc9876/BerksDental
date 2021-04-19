from uuid import UUID

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models as model_fields
from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import slugify, escape
from django.urls import reverse
from django.views.decorators.http import require_safe, require_http_methods

from edit import forms

formatters = {
    model_fields.URLField: lambda
        input_val: f'<a class="link-value" rel="noopener" target="_blank" href="{escape(str(input_val))}">'
                   f'{escape(str(input_val))}</a>',
    model_fields.ImageField: lambda
        input_val: f'<a class="link-value" target="_blank" href="{settings.MEDIA_URL}{escape(input_val)}"'
                   f'>Click To View Image</a> ',
    model_fields.BooleanField: lambda input_val: f'<i class="fas '
                                                 f'{"fa-check-circle" if input_val is True else "fa-times-circle"}'
                                                 f' fa-lg bool-icon"></i>',
    model_fields.TimeField: lambda input_val: input_val.strftime("%I:%M %p"),
    model_fields.DateTimeField: lambda input_val: input_val.strftime("%d-%m-%y at %I:%M %p")
}


class EditViewSet:
    """ A class used to manage and render models easily, this class is meant to be inherited

    :attr displayName: The name to display on html forms and certain links
    :type displayName: str
    :attr model: The model to edit using the view functions
    :type model: class:`django.db.models.Model`
    :attr modelForm: The form to render in the view functions
    :type modelForm: class:`django.forms.ModelForm`
    :attr ordered: A boolean, tells us if we can edit the order in which these objects appear
    :type ordered: bool
    :attr displayFields: A list of fields we want to be shown in the overview view
    :type displayFields: list(str)
    :attr labels: If there's any fields we want to be displayed differently,
    we put the field name as the key, and the desired label as the value
    """

    displayName: str = "base"
    pictureClass = "fa-edit"
    additionalActions = []
    model = None
    modelForm = None
    ordered = False
    per_page = 10
    displayFields = []
    labels = {}

    def __init__(self):
        """ This function is run when the ViewSet is instantiated
        It sets up a format list, which essentially tells us how each field of the object should be formatted
        """

        self.format_list = []
        for field in self.displayFields:
            field_object = self.model._meta.get_field(field)
            self.format_list.append(formatters.get(type(field_object), lambda input_val: str(input_val)))
        if self.model is None:
            raise ValueError("No Model Set")

    def format_value_list(self, value_list):
        """ This function is used as a way to format any values we read from the database, like dates and links
        It reads from the format_list and if the field name matches it, it'll fun teh lambda function specified

        :param value_list: A list of lists, each nested list containing the values for objects
        :type value_list: list(list(*))
        :returns: A new, formatted valueList
        :rtype: list(list(*))
        """

        new_value_list = [list(obj) for obj in value_list]

        for obj_counter in range(0, len(new_value_list)):
            for value_counter in range(0, len(new_value_list[obj_counter]) - 1):
                new_value_list[obj_counter][value_counter] = self.format_list[value_counter](
                    new_value_list[obj_counter][value_counter])

        return new_value_list

    def pre_save(self, new_obj, form_data, new):
        """ The function to be run before an object is saved to the database
        For now, it just passes, but classes that inherit this can override this function

        :param new_obj: The newObj that is about to be saved (if the item is being added, it will be :type:None)
        :type new_obj: class:`django.db.models.Model`
        :param form_data: Additional data from the form that the viewSet may need
        :type form_data: dict
        :param new: True if the object is just being added to the db, false if its being edited
        :type new: bool
        """

        pass

    def post_save(self, new_obj, form_data, new):
        """ The function to be run after an object is saved to the database
        For now, it just passes, but classes that inherit this can override this function

        :param new_obj: The newObj that has been saved
        :type new_obj: class:`django.db.models.Model`
        :param form_data: Additional data from the form that the viewSet may need
        :type form_data: dict
        :param new: True if the object is just being added to the db, false if its being edited
        :type new: bool
        """

        pass

    def pre_del(self, obj_to_delete):
        """ The function to be run before an object is deleted from the database
        For now, it just passes, but classes that inherit this can override this function

        :param obj_to_delete: The object that is about to be deleted
        :type obj_to_delete: class:`django.db.models.Model`
        """

        pass

    def get_form_object(self, data_sources, instance=None):
        # dataSources.append(self.additional_form_data(instance))
        return self.modelForm(*data_sources, initial=self.additional_form_data(instance), instance=instance)

    def additional_form_data(self, obj):
        return {}

    def post_del(self, obj_deleted):
        """ The function to be run after an object is deleted from the database
        For now, it just passes, but classes that inherit this can override this function

        :param obj_deleted: The object that has been deleted (the data will still be passed, but the db row is deleted)
        :type obj_deleted: class:`django.db.models.Model`
        """

        pass

    def get_safe_name(self):
        """ This function is run to get the name of this view set as a template syntax safe string
        it gets rid of spaces in favor of underscores, and makes the name lowercase

        :returns: A safe name to be used in template syntax and url patterns
        :rtype: str
        """

        current_name = self.displayName.lower()
        current_name = slugify(current_name.replace(" ", "_"))
        return current_name

    def get_link(self, link_type):
        """ This function is used to get and reverse a name with a given type.
         So passing "add" when the model is "ExternalLink" will resolve to the url "/admin/edit/link/"

        :param link_type: The type of url we want to reverse
        :type link_type: str
        :returns: The link to hte requested url
        :rtype: str
        """

        return reverse(f"edit:{self.get_safe_name()}_{link_type}")

    def gen_perms(self, actions, include_app_name=True):
        perms = []
        for action in actions:
            if include_app_name:
                perms.append(f"edit.{action}_{self.model.__name__.lower()}")
            else:
                perms.append(f"{action}_{self.model.__name__.lower()}")
        return perms

    def get_permissions_as_dict(self, include_app_name=True):
        return {
            "Edit": self.gen_perms(["change", "add", "delete"], include_app_name=include_app_name),
            "View": self.gen_perms(["view"], include_app_name=include_app_name),
            "*": self.gen_perms(["change", "add", "delete", "view"], include_app_name=include_app_name),
            "None": []
        }

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
            return render(request, "db/edit.html", {'form': form, 'viewSet': self, 'new': True, "verb": "Add",
                                                    "back_link": self.overview_link(),
                                                    'help_link': reverse("edit:help_edit")})

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
        form = self.get_form_object([request.POST, request.FILES], instance=target_obj)

        if form.is_valid():
            self.pre_save(target_obj, form.cleaned_data, False)
            edited_obj = form.save()
            self.post_save(edited_obj, form.cleaned_data, False)
            return redirect(f'{self.overview_link()}?alert={self.displayName} Saved&alertType=success')
        else:
            return render(request, "db/edit.html",
                          {'form': form, 'viewSet': self, 'new': False, "verb": "Edit",
                           "back_link": self.overview_link(), 'help_link': reverse("edit:help_edit")})

    def obj_delete_view(self, request):
        """ A django view function, this will delete the model from the database given form data
        It will ask the user for confirmation that they would like to delete the object
        After the object is deleted, it will redirect to the overview page

        :param request: A request object sent by django
        :type request: class:`django.http.HttpRequest`
        :returns: An HttpResponse containing the rendered html file
        :rtype: class:`django.http.HttpResponse`
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
                form = self.get_form_object([])
                new = True
            else:
                try:
                    form = self.get_form_object([], instance=get_object_or_404(self.model, id=target_id))
                except ValidationError:
                    raise Http404()
            print(form.media)
            return render(request, 'db/edit.html',
                          {'form': form, 'viewSet': self, 'new': new, "verb": "Add" if new else "Edit",
                           "back_link": self.overview_link(), 'help_link': reverse("edit:help_edit")})

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
            form = forms.OrderForm(request.POST)
            form.fields["new_order"].set_objects(self.model.objects.all())
            if form.is_valid():
                new_order = [UUID(raw_id) for raw_id in form.cleaned_data.get("new_order").split(",")]
                current_order = list(self.model.objects.values_list("id", flat=True).order_by("sort_order"))
                for target_id in current_order:
                    object_to_be_sorted = self.model.objects.get(id=target_id)
                    object_to_be_sorted.sort_order = new_order.index(target_id)
                    object_to_be_sorted.save()
                return redirect(f'{self.overview_link()}?alert=New Order Saved&alertType=success')
            else:
                return render(request, "db/edit.html", {'viewSet': self, 'back_link': self.overview_link(),
                                                        'verb': "Re-Order", 'plural': True, "form": form,
                                                        'help_link': reverse("edit:help_ordering")})
        else:
            form = forms.OrderForm()
            form.fields["new_order"].set_objects(self.model.objects.all())
            return render(request, "db/edit.html",
                          {'viewSet': self, 'back_link': self.overview_link(),
                           'verb': "Re-Order", 'plural': True, "form": form,
                           'help_link': reverse("edit:help_ordering")})

    def obj_overview_view(self, request):
        """ A django view function, this will add the model to the database given form data
        It displays all the objects based off this model in the database as an HTML file

        :param request: A request object sent by django
        :type request: class:`django.http.HttpRequest`
        :returns: An HttpResponse containing the rendered html file
        :rtype: class:`django.http.HttpResponse`
        """
        page_number = request.GET.get('page', 1)
        model_paginator = Paginator(self.model.objects.all(), self.per_page, allow_empty_first_page=True)
        page = model_paginator.get_page(page_number)
        start = page.start_index() - 1
        end = page.end_index()
        next_link = "#"
        previous_link = "#"
        if page.has_next():
            next_link = f"{self.overview_link()}?page={page.next_page_number()}"
        if page.has_previous():
            previous_link = f"{self.overview_link()}?page={page.previous_page_number()}"
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
                       'max_pages': model_paginator.num_pages, 'help_link': reverse("edit:help_navigation")})

    @staticmethod
    def missing_permissions_link():
        missing_permissions_message = "You don't have sufficient permissions to perform this action"
        return f"{reverse('edit:admin_home')}?alert={missing_permissions_message}&alertType=error"

    def get_view_functions(self):
        """ This function sets up proxy functions
        We need to use the @login_required and other decorators, but we can't use this within a class,
        So we create functions that have the decorator that use the class

        :returns: Three view functions (overview, edit/add, delete)
        :rtype: function(3)
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
        @require_http_methods(["GET", "POST"])
        @login_required()
        def edit_order_view(request):
            if request.user.has_perms(self.gen_perms(["change"])):
                return self.object_order_view(request)
            else:
                return redirect(self.missing_permissions_link())

        return edit_order_view
