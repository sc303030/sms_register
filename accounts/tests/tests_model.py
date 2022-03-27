from django.core.exceptions import ValidationError
from django.test import TestCase
from ..models import SmsAuth, User


class SmsAuthTestCase(TestCase):
    '''
    SmsAuth  테스트
    '''

    def setUp(self):
        self.phone_number = '01012345678'
        SmsAuth.objects.create(phone_number=self.phone_number)

    def test_sms_auth_phone_number(self):
        '''
        1. 객체에 저장된 핸드폰 번호가 우리가 입력한 번호랑 일치하는지 확인
        2. 최대 길이가 11인지 확인
        '''
        sms_auth = SmsAuth.objects.get(phone_number=self.phone_number)
        self.assertEqual(sms_auth.phone_number, self.phone_number)
        self.assertEqual(sms_auth._meta.get_field('phone_number').max_length, 11)

    def test_sms_auth_Raise_validation(self):
        '''
        SmsAuth 모델에 설정한 validators가 작동하는지 확인 - 일부러 에러 발생시킴
        '''
        client = SmsAuth(phone_number='00011112222')
        client.full_clean()
        self.assertRaises(ValidationError, client.full_clean)

    def test_sms_auth_auth_number(self):
        '''
        1. auth_number의 fields가 IntegerField인지 확인
        2. 4자리인지 확인
        '''
        sms_auth = SmsAuth.objects.get(phone_number=self.phone_number)
        auth_number = sms_auth.auth_number
        self.assertEqual(sms_auth._meta.get_field('auth_number').get_internal_type(), 'IntegerField')
        self.assertEqual(len(str(auth_number)), 4)


class UserModelTestCase(TestCase):
    '''
    User 모델 테스트
    '''

    def setUp(self):
        self.user_data = {
            "username": 'test01',
            'email': 'test01@test.com',
            "password": 'test123456',
            "nickname": '테스트_닉네임',
            'name': '테스트',
            "phone_number": '01011112222'
        }
        self.user = User.objects.create(**self.user_data)

    def test_user_max_length(self):
        '''
        추가로 입력한 필드들의 길이 확인
        '''
        nickname_length = self.user._meta.get_field('nickname').max_length
        phone_number_length = self.user._meta.get_field('phone_number').max_length
        name_length = self.user._meta.get_field('name').max_length
        self.assertEqual(nickname_length, 20)
        self.assertEqual(phone_number_length, 11)
        self.assertEqual(name_length, 50)

    def test_user_Raise_validation(self):
        '''
        User 모델에 설정한 validators가 작동하는지 확인 - 일부러 에러 발생시킴
        '''
        self.user_data = {
            "username": 'test01',
            'email': 'test01@tcom',
            "password": '0000',
            "nickname": '테스트_닉네임',
            'name': '테스트',
            "phone_number": '452'
        }
        user = User(**self.user_data)
        user.full_clean()
        self.assertRaises(ValidationError, user.full_clean)

    def test_user_fields_confirm(self):
        '''
        User 모델 추가 컬럼 fields 속성값 확인
        '''
        nickname = self.user._meta.get_field('nickname').get_internal_type()
        phone_number = self.user._meta.get_field('phone_number').get_internal_type()
        name = self.user._meta.get_field('name').get_internal_type()
        self.assertEqual(nickname, 'CharField')
        self.assertEqual(phone_number, 'CharField')
        self.assertEqual(name, 'CharField')
