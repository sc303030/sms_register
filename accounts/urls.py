from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView
from django.conf.urls import (
    handler400, handler403, handler404, handler500)
from .views import SMSAuthSendView, SMSAuthConfirmView, TempPasswordView, CustomPasswordChangeView

urlpatterns = [
    path('sms/send/', SMSAuthSendView.as_view(), name='sms_auth_send'),  # sms 인증 문자 보내기
    path('sms/confirm/', SMSAuthConfirmView.as_view(), name='sms_auth_confirm'),  # sms 인증번호 확인
    path('sms/temp-password/', TempPasswordView.as_view(), name='sms_temp_password'),  # sms인증 확인 후 인증번호 임시 비밀번호로 설정
    path('password/change/', CustomPasswordChangeView.as_view(), name='password_change'),  # 비밀번호 변경

    # simple-jwt
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
