from django.core.validators import RegexValidator
from rest_framework import serializers
from ..models import SmsAuth, User
from django.utils.translation import ugettext_lazy as _


# 전화번호 형식 확인하기
class SMSSendSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=11, validators=[
        RegexValidator(regex=r"^010?[0-9]\d{3}?\d{4}$", message='전화번호 형식이 잘못되었습니다.')])

    class Meta:
        model = SmsAuth
        fields = ['phone_number']


class SmsConfirmSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=11, validators=[
        RegexValidator(regex=r"^010?[0-9]\d{3}?\d{4}$", message='전화번호 형식이 잘못되었습니다.')])
    auth_number = serializers.IntegerField(min_value=1000, max_value=9999)

    class Meta:
        model = SmsAuth
        fields = ['phone_number', 'auth_number']

    def validate_auth_number(self, value):
        value = self.initial_data.get('auth_number')
        if isinstance(value, int):
            return value
        raise serializers.ValidationError(_("유효한 정수(integer)를 넣어주세요."))

    def validate_phone_number(self, phone_number):
        '''
        가입 내역이 있는지 확인하기
        '''
        # 전화 번호 인증 확인하기
        phone_number_obj = SmsAuth.objects.filter(phone_number=phone_number)
        user = User.objects.filter(phone_number=phone_number)
        # 전화 번호 인증하지 않았을 경우
        if not phone_number_obj.exists():
            raise serializers.ValidationError(_("전화번호 인증을 진행해주세요."))
        else:
            if not user.exists() or (user.exists() and len(user[0].email) == 0):
                # 1. 인증번호 확인 과정을 거치지 않았거나
                # 2. 인증과정은 거쳤지만 가입하지 않은 경우
                # phone_number 리턴
                return phone_number
            elif user.exists() and len(user[0].email) > 0:
                # 이미 회원인데 다시 가입하려는 경우
                raise serializers.ValidationError(_("가입내역이 있습니다. 로그인을 진행해주세요."))
