from allauth.utils import get_username_max_length
from django.core.validators import RegexValidator
from rest_auth.serializers import PasswordChangeSerializer
from rest_framework import serializers
from ..models import SmsAuth, User
from django.utils.translation import ugettext_lazy as _

try:
    from allauth.account import app_settings as allauth_settings
except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")


class PasswordSmsConfirmSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=11, validators=[RegexValidator(regex=r"^010?[0-9]\d{3}?\d{4}$",
                                                                                   message='전화번호 형식이 잘못되었습니다.')])
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
        # 인증을 하지 않았다면 가입한 적도 없었으니 비밀번호를 찾을 수 없음
        if not phone_number_obj.exists():
            raise serializers.ValidationError(_("가입한 회원이 아닙니다."))
        else:
            if not user.exists() or (user.exists() and len(user[0].email) == 0):
                # 1. 인증번호 확인 과정을 거치지 않았거나
                # 2. 인증과정은 거쳤지만 가입하지 않은 경우
                # 가입 내역이 없기 때문에 비밀번호 찾기 불가
                raise serializers.ValidationError(_("가입한 회원이 아닙니다."))
            elif user.exists() and len(user[0].email) > 0:
                # 회원이기 때문에 phone_number 리턴
                return phone_number


class CustomPasswordChangeFieldsSerializer(serializers.Serializer):
    '''
    PasswordChangeSerializer은 user가 필요하기 때문에
    해당 serializer로 넘어가기 전에 모든 필드가 있는지 확인하기 &
    User가 있는지 확인하기
    '''
    old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)
    username = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=allauth_settings.USERNAME_MIN_LENGTH,
        required=allauth_settings.USERNAME_REQUIRED,
        validators=[RegexValidator(regex=r"^([a-zA-Z])[a-zA-Z0-9_]*$", message='ID 형식이 잘못되었습니다.')]
    )

    def validate_username(self, username):
        user = User.objects.filter(username=username)
        if user.exists():
            return username
        else:
            raise serializers.ValidationError(_("가입한 회원이 아닙니다."))


# PasswordChangeSerializer를 커스텀하여 재정의
class CustomPasswordChangeSerializer(PasswordChangeSerializer):
    '''
        기존의 PasswordChangeSerializer는 로그인 한 상태에서 진행되기 때문에
        username이 필요없지만
        지금은 로그인하지 않고 진행하기때문에 username이 필요하다.
    '''
    username = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=allauth_settings.USERNAME_MIN_LENGTH,
        validators=[RegexValidator(regex=r"^([a-zA-Z])[a-zA-Z0-9_]*$", message='ID 형식이 잘못되었습니다.')]
    )

    def validate_old_password(self, value):
        invalid_password_conditions = (
            self.old_password_field_enabled,
            self.user,
            not self.user.check_password(value)
        )

        if all(invalid_password_conditions):
            raise serializers.ValidationError(_("임시 비밀번호가 일치하지 않습니다."))
        return value
