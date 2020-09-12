from django.urls import path
from . import views

app_name = 'report'
urlpatterns = [
    path('/about',views.about,name="about"),

]
