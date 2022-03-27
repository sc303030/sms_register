import re

from allauth.utils import get_username_max_length
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.db import transaction
from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer
from accounts.models import SmsAuth, User
from django.utils.translation import ugettext_lazy as _
from rest_framework_simplejwt.models import TokenUser

try:
    from allauth.account import app_settings as allauth_settings
except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")


# rest-auth에서 기본적으로 제공하는 RegisterSerializer 커스텀 하여 재사용
class CustomRegisterSerializer(RegisterSerializer):
    # 필요한 필드 다시 적기
    username = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=allauth_settings.USERNAME_MIN_LENGTH,
        required=allauth_settings.USERNAME_REQUIRED,
        validators=[RegexValidator(regex=r"^([a-zA-Z])[a-zA-Z0-9_]*$", message='ID 형식이 잘못되었습니다.')]
    )
    nickname = serializers.CharField(max_length=20, validators=[
        RegexValidator(regex=r"[^ㄱ-ㅣ]$", message='닉네임 형식이 잘못되었습니다.')])
    phone_number = serializers.CharField(max_length=11,
                                         validators=[RegexValidator(regex=r"^010?[0-9]\d{3}?\d{4}$",
                                                                    message='전화번호 형식이 잘못되었습니다.')])
    name = serializers.CharField(max_length=50,
                                 validators=[RegexValidator(regex=r"^[a-zA-Z|가-힣]*$", message='이름 형식이 잘못되었습니다.')])
    email = serializers.EmailField(required=True)

    def validate_name(self, name):
        eng = re.compile(r"^[a-zA-Z]*$")
        korea = re.compile(r"^[가-힣]*$")
        if eng.match(name):
            return name
        elif korea.match(name):
            return name
        raise serializers.ValidationError(_('이름 형식이 잘못되었습니다.'))

    def validate_nickname(self, nickname):
        if User.objects.filter(nickname=nickname).count() > 0:
            raise serializers.ValidationError(_('이미 이 닉네임으로 등록된 사용자가 있습니다.'))
        return nickname

    def validate_phone_number(self, phone_number):
        '''
            미리 전화번호로 User가 있는지 확인하고 가입 단계로 넘어오겠지만
            혹시 모를 경우를 대비해 다시 한 번 전화번호 확인
        '''
        # 전화 번호 인증 확인하기
        phone_number_obj = SmsAuth.objects.filter(phone_number=phone_number)
        user = User.objects.filter(phone_number=phone_number)
        # 1. 전화 번호 인증을 진행하지 않았을 경우
        # 2. 전화번호 인증만 진행한 경우(인증번호 확인 작업 x)
        if not phone_number_obj.exists() or not user.exists():
            raise serializers.ValidationError(_("전화번호 인증 후 회원가입을 진행해주세요."))
        elif phone_number_obj.exists() and user.exists():
            # 전화번호 인증과 인증번호 확인 까지 완료
            if len(user[0].email) > 0:
                # 이미 회원인데 다시 가입하려는 경우
                raise serializers.ValidationError(_("가입내역이 있습니다. 로그인을 진행해주세요."))
            else:
                # email의 길이가 0보다 크지 않다는건 
                # 회원가입을 진행하지 않았다는 뜻이기에 phone_number 리턴
                return phone_number

    # 추가된 필드를 다시 저장해줘야 해서 재정의하기
    def get_cleaned_data(self):
        # 먼저 부모 클래스를 진행해서 data를 가져오고
        data = super().get_cleaned_data()
        # 그 다음에 우리가 정의한 값들을 data에 추가하기
        data['nickname'] = self.validated_data.get('nickname', '')
        data['phone_number'] = self.validated_data.get('phone_number', '')
        data['name'] = self.validated_data.get('name', '')
        return data

    @transaction.atomic
    def save(self, request):
        '''
            원래는 super().save(request)를 상속받아서 새로운 객체를 생성하지만
            전화번호를 인증하는 과정에서 미리 User객체를 생성하였기 때문에
            해당 객체를 다시 불러와 객체의 속성값을 업데이트 하는 방법으로 진행
        '''
        # 위에서 다시 정의한 함수를 실행하여 data 얻기
        data = self.get_cleaned_data()
        phone_number = data.get('phone_number')
        user = User.objects.get(phone_number=phone_number)
        user.nickname = data.get('nickname')
        user.username = data.get('username')
        user.email = data.get('email')
        # 비밀번호 같은 경우 user.password로 하면 암호화되서 저장이 안되기 때문에
        # set_password()로 해야 암호화되서 저장됨
        user.set_password(data.get("password1"))
        user.nickname = data.get('nickname')
        user.phone_number = phone_number
        user.name = data.get('name')
        user.save()
        return user
