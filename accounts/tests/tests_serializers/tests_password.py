import json

from django.test import TestCase
from rest_framework.reverse import reverse

from ...serializers import PasswordSmsConfirmSerializer, \
    CustomPasswordChangeFieldsSerializer
from ...models import User, SmsAuth
from rest_framework.test import APITestCase


class PasswordSmsConfirmSerializerTestCase(TestCase):
    '''
    PasswordSmsConfirmSerializer 테스트 케이스
    '''

    def setUp(self):
        self.phone_number = "01000000000"
        self.sms_auth = SmsAuth.objects.create(phone_number=self.phone_number)
        self.auth_number = self.sms_auth.auth_number

        # User 객체 생성
        self.username = 'test'
        self.email = 'test@test.com'
        self.password = 'test123456'
        self.nickname = 'test'
        self.name = '테스트'
        self.data = {
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'nickname': self.username,
            'phone_number': self.phone_number,
            'name': self.name
        }

        # PasswordSmsConfirmSerializer 테스트에서 사용할 User
        self.user = User.objects.create_user(**self.data)

    def test_password_sms_confirm_success(self):
        '''
        PasswordSmsConfirmSerializer 성공
        :return:
        True
        '''
        data = {
            "phone_number": self.phone_number,
            'auth_number': self.auth_number
        }
        password_confirm_serializer = PasswordSmsConfirmSerializer(data=data)
        self.assertEqual(password_confirm_serializer.is_valid(), True)

    def test_password_sms_confirm_fail_not_sms_send(self):
        '''
        PasswordSmsConfirmSerializer 실패 1. 전화번호를 인증하지 않았을 경우
        :return:
        1. {'phone_number': [ErrorDetail(string='가입한 회원이 아닙니다.', code='invalid')]}
        '''
        data = {
            "phone_number": '01000000001',
            'auth_number': self.auth_number
        }
        password_confirm_serializer = PasswordSmsConfirmSerializer(data=data)
        self.assertEqual(password_confirm_serializer.is_valid(), False)

    def test_password_sms_confirm_fail_not_signup(self):
        '''
        PasswordSmsConfirmSerializer 실패 2. 전화번호 인증은 했지만 가입하지 않은 경우
        :return:
        2. {'phone_number': [ErrorDetail(string='가입한 회원이 아닙니다.', code='invalid')]}
        '''
        phone_number = '01000000001'
        SmsAuth.objects.create(phone_number=phone_number)
        data = {
            "phone_number": phone_number,
            'auth_number': self.auth_number
        }
        password_confirm_serializer = PasswordSmsConfirmSerializer(data=data)
        self.assertEqual(password_confirm_serializer.is_valid(), False)

    def test_password_sms_confirm_fail_wrong_fields_type(self):
        '''
        PasswordSmsConfirmSerializer 실패 3. 필드 값의 형식이 틀렸을 때때
        :return:
        3. {'phone_number': [ErrorDetail(string='전화번호 형식이 잘못되었습니다.', code='invalid')], 'auth_number': [ErrorDetail(string='유효한 정수(integer)를 넣어주세요.', code='invalid')]}
        '''
        data = {
            "phone_number": '010000000',
            'auth_number': str(self.auth_number)
        }
        password_confirm_serializer = PasswordSmsConfirmSerializer(data=data)
        self.assertEqual(password_confirm_serializer.is_valid(), False)


class CustomPasswordChangeFieldsSerializerTestCase(APITestCase):
    '''
    CustomPasswordChangeFieldsSerializer 테스트 케이스
    이 serializer는 비밀번호를 변경하기전에 모든 필드가 있는지, 유저가 있는지 확인만 하는 serializer
    '''

    def setUp(self):
        # sms 인증
        self.phone_number = "01000000000"
        self.sms_auth = SmsAuth.objects.create(phone_number=self.phone_number)
        self.auth_number = self.sms_auth.auth_number

        # User 객체 생성
        self.username = 'test'
        self.email = 'test@test.com'
        self.password = 'test123456'
        self.nickname = 'test'
        self.name = '테스트'
        self.data = {
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'nickname': self.username,
            'phone_number': self.phone_number,
            'name': self.name
        }

        # CustomPasswordChangeFieldsSerializer 테스트에서 사용할 User
        self.user = User.objects.create_user(**self.data)

        # 인증번호를 임시 비밀번호로 설정
        self.data2 = json.dumps({
            'phone_number': self.phone_number,
            'auth_number': self.auth_number
        })
        self.url = reverse("sms_temp_password")
        self.client.post(self.url, self.data2, content_type='application/json')
        self.sms_auth2 = SmsAuth.objects.get(phone_number=self.phone_number)
        self.auth_number2 = self.sms_auth2.auth_number

    def test_password_change_fields_success(self):
        '''
        CustomPasswordChangeFieldsSerializer 성공
        :return:
        True
        '''
        data = {
            'username': self.username,
            'old_password': self.auth_number2,
            'new_password1': 'test123456',
            'new_password2': 'test123456',
        }
        change_fields_serializer = CustomPasswordChangeFieldsSerializer(data=data)
        self.assertEqual(change_fields_serializer.is_valid(), True)

    def test_password_change_fields_fail_empty_fields(self):
        '''
        CustomPasswordChangeFieldsSerializer 실패 1. 필수 필드 값이 빈 값일 경우
        :return:
        1. {'old_password': [ErrorDetail(string='이 필드는 blank일 수 없습니다.', code='blank')], 'new_password1': [ErrorDetail(string='이 필드는 blank일 수 없습니다.', code='blank')], 'new_password2': [ErrorDetail(string='이
필드는 blank일 수 없습니다.', code='blank')], 'username': [ErrorDetail(string='이 필드는 blank일 수 없습니다.', code='blank')]}
        '''
        data = {
            'username': '',
            'old_password': '',
            'new_password1': '',
            'new_password2': '',
        }
        change_fields_serializer = CustomPasswordChangeFieldsSerializer(data=data)
        self.assertEqual(change_fields_serializer.is_valid(), False)

    def test_password_change_fields_fail_not_signup(self):
        '''
        CustomPasswordChangeFieldsSerializer 실패 2. 가입하지 않은 username을 입력했을 때
        :return:
        2. {'username': [ErrorDetail(string='가입한 회원이 아닙니다.', code='invalid')]}
        '''
        data = {
            'username': 'test2',
            'old_password': self.auth_number2,
            'new_password1': 'test123456zzz',
            'new_password2': 'test123456',
        }
        change_fields_serializer = CustomPasswordChangeFieldsSerializer(data=data)
        self.assertEqual(change_fields_serializer.is_valid(), False)

    def test_password_change_fields_fail_wrong_fields_type(self):
        '''
        CustomPasswordChangeFieldsSerializer 실패 3. 필드 값의 형식이 틀렸을 때
        :return:
        3. {'username': [ErrorDetail(string='ID 형식이 잘못되었습니다.', code='invalid')]}
        '''
        data = {
            'username': '1zzz',
            'old_password': self.auth_number2,
            'new_password1': 'test123456zzz',
            'new_password2': 'test123456zzz',
        }
        change_fields_serializer = CustomPasswordChangeFieldsSerializer(data=data)
        self.assertEqual(change_fields_serializer.is_valid(), False)
