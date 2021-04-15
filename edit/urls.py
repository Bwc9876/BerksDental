from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from main.views import safe_render

from edit import views as views

app_name = "edit"
urlpatterns = [
    path('', views.admin_home, name="admin_home"),
    path('login/', LoginView.as_view(template_name="login.html", redirect_authenticated_user=True), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('help/', views.help_home, name="help"),
]

urlpatterns += views.setup_viewsets()
