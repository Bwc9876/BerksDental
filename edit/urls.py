from django.urls import path
from edit import views as views
from django.contrib.auth.views import LoginView, LogoutView

app_name = "edit"
urlpatterns = [
    path('', views.admin_home, name="admin_home"),
    path('login/', LoginView.as_view(template_name="login.html", redirect_authenticated_user=True), name="login"),
    path('logout/', LogoutView.as_view(), name="logout")
]

urlpatterns += views.setup_viewsets()
