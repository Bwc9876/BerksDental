from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from edit import views as views
from main.views import safe_render

app_name = "edit"
urlpatterns = [
    path('', views.admin_home, name="admin_home"),
    path('login/', LoginView.as_view(template_name="login.html", redirect_authenticated_user=True), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('help/', safe_render("help/home.html", ctx={"back_link": "/admin/"}), name="help"),
    views.help_page("navigation", "Navigation"),
    views.help_page("edit", "Adding And Editing"),
    views.help_page("image", "Uploading Pictures"),
    views.help_page("password", "User Passwords"),
    views.help_page("ordering", "Ordering"),
]

urlpatterns += views.setup_viewsets()
