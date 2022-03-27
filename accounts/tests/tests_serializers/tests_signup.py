from django.test import TestCase
from ...serializers import CustomRegisterSerializer
from ...models import SmsAuth, User


class CustomRegisterSerializerTestCase(TestCase):
    '''
    CustomRegisterSerializer 테스트 케이스
    '''

    def setUp(self):
        # CustomRegisterSerializer 테스트에서 사용할 SmsAuth
        self.phone_number = '01000000000'  # 테스트용이기 때문에 간단한 번호 입력
        self.sms_auth = SmsAuth.objects.create(phone_number=self.phone_number)

        self.user = User.objects.create(phone_number=self.phone_number)

    def test_custom_register_serializer_success(self):
        '''
        CustomRegisterSerializer 성공
        :return:
        '''
        data = {
            'username': 'test',
            'email': 'test@test.com',
            'password1': 'test123456',
            'password2': 'test123456',
            'nickname': 'test123456',
            'phone_number': self.phone_number,
            'name': '테스트'
        }
        custom_serializer = CustomRegisterSerializer(data=data)
        self.assertEqual(custom_serializer.is_valid(), True)

    def test_custom_register_serializer_fail_empty_required(self):
        '''
        CustomRegisterSerializer 실패 1. 필수 필드 빈 값으로 보내는 경우
        :return:
        1. {'username': [ErrorDetail(string='이 필드는 blank일 수 없습니다.', code='blank')], 'email': [ErrorDetail(string='이 필드는 blank일 수 없습니다.', code='blank')], 'password1': [ErrorDetail(string='이 필드는 blank일 수 없습니
다.', code='blank')], 'password2': [ErrorDetail(string='이 필드는 blank일 수 없습니다.', code='blank')], 'nickname': [ErrorDetail(string='이 필드는 blank일 수 없습니다.', code='blank')], 'phone_number': [ErrorDetail(string='이 필
드는 blank일 수 없습니다.', code='blank')], 'name': [ErrorDetail(string='이 필드는 blank일 수 없습니다.', code='blank')]}
        '''
        data = {
            'username': '',
            'email': '',
            'password1': '',
            'password2': '',
            'nickname': '',
            'phone_number': '',
            'name': ''
        }
        custom_serializer = CustomRegisterSerializer(data=data)
        self.assertEqual(custom_serializer.is_valid(), False)

    def test_custom_register_serializer_fail_wrong_fields_type(self):
        '''
        CustomRegisterSerializer 실패 2. 필드 값의 형식이 틀렸을 경우
        :return:
        1. {'username': [ErrorDetail(string='ID 형식이 잘못되었습니다.', code='invalid')], 'email': [ErrorDetail(string='유효한 이메일 주소를 입력하십시오.', code='invalid')], 'password1': [ErrorDetail(string='비밀번호가 너무 짧습니다
. 최소 8 문자를 포함해야 합니다.', code='password_too_short'), ErrorDetail(string='비밀번호가 너무 일상적인 단어입니다.', code='password_too_common'), ErrorDetail(string='비밀번호가 전부 숫자로 되어 있습니다.', code='password_enti
rely_numeric')], 'phone_number': [ErrorDetail(string='전화번호 형식이 잘못되었습니다.', code='invalid')], 'name': [ErrorDetail(string='이름 형식이 잘못되었습니다.', code='invalid')]}
        '''
        data = {
            'username': '1ada',
            'email': 'sdfsdf',
            'password1': '13',
            'password2': '13',
            'nickname': 'zzz',
            'phone_number': '010000000',
            'name': 1212
        }
        custom_serializer = CustomRegisterSerializer(data=data)
        self.assertEqual(custom_serializer.is_valid(), False)
