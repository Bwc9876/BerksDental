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
from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import slugify
from django.urls import path
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
    """

    displayName = "base"
    model = None
    modelForm = None

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

        :returns: A safe name to be sued in template syntax and url patterns
        :rtype: str
        """
        current_name = self.displayName.lower()
        current_name = slugify(current_name.replace(" ", "_"))
        return current_name

    def get_overview_link(self):
        """ A function used to get the link that can be used to redirect to the overview page for this model

        :returns: The link to be used in the redirect
        :rtype: str
        """

        return "/admin/overview/" + self.get_safe_name()

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
            self.post_save(new_obj, True)
            return redirect(self.get_overview_link())
        else:
            return render(request, "db/edit.html", {'form': form, 'viewSet': self})

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
            return redirect(self.get_overview_link())
        else:
            return render(request, "db/edit.html", {'form': form, 'viewSet': self})

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
            self.post_del(target_obj)
            return redirect(self.get_overview_link())
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
            if target_id == '':
                form = self.modelForm()
            else:
                try:
                    form = self.modelForm(instance=get_object_or_404(self.model, id=target_id))
                except ValidationError:
                    raise Http404()

            return render(request, 'db/edit.html', {'form': form, 'viewSet': self})

    def obj_overview_view(self, request):
        """ A django view function, this will add the model to the database given form data
        It displays all the objects based off this model in the database as an html file

        :param request: A request object sent by django
        :type request: class:`django.http.HttpRequest`
        :returns: An HttpResponse containing the rendered html file
        :rtype: class:`django.http.HttpResponse`
        """

        objects = self.model.objects.all()
        return render(request, f'db/view_{self.get_safe_name()}s.html',
                      {f'{self.get_safe_name()}s': objects, 'viewSet': self})

    def get_view_functions(self):
        """ This function sets up proxy functions
        We need to use the @login_required and other decorators, yet we can't use this within classes
        So we create functions that have the decorator that use the class

        :returns: Three view functions (overview, edit/add, delete)
        :rtype: function(3)
        """

        @require_http_methods(["GET", "POST"])
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


# The following classes inherit from EditViewSet class, and are used to add functionality to the models we want


class EventViewSet(EditViewSet):
    displayName = "Event"
    model = models.Event
    modelForm = forms.EventForm


class SocialViewSet(EditViewSet):
    displayName = "Social Media Page"
    model = models.Social
    modelForm = forms.SocialForm


class LinkViewSet(EditViewSet):
    displayName = "Link"
    model = models.ExternalLink
    modelForm = forms.LinkForm

    def post_save(self, newObj, new):
        """ This function is run after an object is saved to the db
        If this object is new, we assign it a sort_order attribute
        """

        if new:
            newObj.sort_order = len(list(self.model.objects.all())) - 1
            newObj.save()

    def post_del(self, objDeleted):
        """ This function is run after the link is deleted from the db
        It will make sure the sort_order properties on all links are set correctly after deletion
        """

        links_to_fix = list(self.model.objects.filter(sort_order__gt=objDeleted.sort_order))
        for link_object in links_to_fix:
            link_object.sort_order -= 1
            link_object.save()

    def edit_order(self, request):
        """ This function allows the user toe dit the order external links will appear

        :param request: A request object sent by django
        :type request: class:`django.http.HttpRequest`
        :returns: Either a page where the user can edit the order of links, or a redirect back to the overview page
        :rtype: :class:`django.http.HttpResponse`
        """

        if request.method == "POST":
            new_order_raw = request.POST.get("new_order", "").split(",")
            new_order = [UUID(raw_id) for raw_id in new_order_raw]
            current_order = list(self.model.objects.values_list("id", flat=True).order_by("sort_order"))
            if Counter(new_order) == Counter(current_order):
                for target_id in current_order:
                    object_to_be_sorted = self.model.objects.get(id=target_id)
                    object_to_be_sorted.sort_order = new_order.index(target_id)
                    object_to_be_sorted.save()
                return redirect(self.get_overview_link())
            else:
                return render(request, 'db/link_order.html',
                              {'error': 'Invalid List!', 'links': self.model.objects.all, 'viewSet': self})
        else:
            return render(request, "db/link_order.html", {'links': self.model.objects.all(), 'viewSet': self})

    def get_edit_order_view(self):

        @require_http_methods(["GET", "POST"])
        @login_required()
        def edit_order_view(request):
            return self.edit_order(request)

        return edit_order_view


class GalleryPhotoViewSet(EditViewSet):
    displayName = "Photo"
    model = models.GalleryPhoto
    modelForm = forms.PhotoForm
    photoFolder = "gallery-photos"

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
        It renames the pictures file to prevent naming conflict if we just added a picture or a new picture was uploaded

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
            path(f'admin/overview/{url_name}/', overview, name=f"{url_name}_view"),
            path(f'admin/edit/{url_name}/', add_or_edit, name=f"{url_name}_edit"),
            path(f'admin/delete/{url_name}/', delete, name=f"{url_name}_delete")
        ]
        return patterns_to_return
    else:
        raise ValueError("Please pass the *class* of the viewset you want to add!")


def setup_viewsets():
    """ This function adds gives the url patterns for all the models we want

    :returns: The list of wanted patterns for the models
    :rtype: list(:class:`django.urls.path`)
    """

    new_patterns = []
    new_patterns += generate_paths_from_view_set(EventViewSet)
    new_patterns += generate_paths_from_view_set(LinkViewSet)
    new_patterns.append(path("admin/order/link/", LinkViewSet().get_edit_order_view(), name="link_order"))
    new_patterns += generate_paths_from_view_set(GalleryPhotoViewSet)
    new_patterns += generate_paths_from_view_set(OfficerViewSet)
    new_patterns += generate_paths_from_view_set(SocialViewSet)
    return new_patterns
