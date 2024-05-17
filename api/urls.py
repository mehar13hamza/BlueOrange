from django.urls import path
from .views import ZipCodeDetailView, TopZipCodesView
from . import views

urlpatterns = [
    path('zipcode/<str:zipcode>/', ZipCodeDetailView.as_view(), name='zip-code-detail'),
    path('top_zipcodes/', TopZipCodesView.as_view(), name='top-zipcodes'),
]
    