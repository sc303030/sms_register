"""ably URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf.urls import (
    handler400, handler403, handler404, handler500)
from accounts.views import custom404, custom500, MyTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/v1/', include('accounts.urls')),  # accounts app urls

    # DRF
    path('api-auth/', include('rest_framework.urls')),

    # rest-auth
    path('accounts/v1/rest-auth/', include('rest_auth.urls')),  # login, logout, user를 담당하는 url
    path('accounts/v1/rest-auth/signup/', include('rest_auth.registration.urls')),  # 회원가입 url

    # simple-jwt
    path('accounts/v1/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('accounts/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

handler404 = custom404
handler500 = custom500
