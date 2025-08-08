from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import *

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('generate/', generate_form_view, name='create_website'),
    path('login', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('', view_website, name='view_website'),
    path('websites/<int:website_id>/', view_website, name='view_website_detail'),
    path('websites/<int:website_id>/edit/', edit_website, name='edit_website'),
    path('websites/<int:website_id>/delete/', delete_website, name='delete_website'),
    path('api/websites/', WebsiteAPIView.as_view(), name='website-list-create'),
    path('api/websites/<int:pk>/', WebsiteAPIView.as_view(), name='website-detail-update'),
]