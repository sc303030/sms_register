from django.test import TestCase
from ...serializers import SMSSendSerializer, SmsConfirmSerializer
from ...models import SmsAuth, User


class SmsSendSerializerTestCase(TestCase):
    '''
    SMSSendSerializer 테스트 케이스
    '''

    def test_sms_send_success(self):
        '''
        SmsSendSerializer 성공
        :return:
        True
        '''
        data = {
            "phone_number": '01000000000'
        }
        sms_serializer = SMSSendSerializer(data=data)
        sms_serializer.is_valid()
        self.assertEqual(sms_serializer.validated_data, data)

    def test_sms_send_fail_wrong_type(self):
        '''
        SmsSendSerializer 실패 1. 전화번호 형식에 맞지 않을 경우
        :return:
        {'phone_number': [ErrorDetail(string='전화번호 형식이 잘못되었습니다.', code='invalid')]}
        '''
        data = {
            "phone_number": '0000'
        }
        sms_serializer = SMSSendSerializer(data=data)
        self.assertEqual(sms_serializer.is_valid(), False)


class SmsConfirmSerializerTestCase(TestCase):
    '''
    SmsConfirmSerializer 테스트 케이스
    '''

    def setUp(self):
        self.phone_number = '01000000000'
        self.sms_auth = SmsAuth.objects.create(phone_number=self.phone_number)
        self.auth_number = self.sms_auth.auth_number

    def test_sms_confirm_success(self):
        '''
        SmsConfirmSerializer 성공
        :return:
        True
        '''
        data = {'phone_number': self.phone_number, 'auth_number': self.auth_number}
        confirm_serializer = SmsConfirmSerializer(data=data)
        self.assertEqual(confirm_serializer.is_valid(), True)

    def test_sms_confirm_fail_not_send(self):
        '''
        SmsConfirmSerializer 실패 1. 전화번호 인증을 진행하지 않음
        :return: 
        1. {'phone_number': [ErrorDetail(string='전화번호 인증을 진행해주세요.', code='invalid')]}
        '''
        data = {'phone_number': "01000000001", 'auth_number': self.auth_number}
        confirm_serializer = SmsConfirmSerializer(data=data)
        self.assertEqual(confirm_serializer.is_valid(), False)

    def test_sms_confirm_fail_already_user(self):
        '''
        SmsConfirmSerializer 실패 2. 이미 계정이 존재하는 경우
        :return: 
        2. {'phone_number': [ErrorDetail(string='가입내역이 있습니다. 로그인을 진행해주세요.', code='invalid')]}
        '''
        user_data = {
            'username': 'test',
            'email': 'test@test.com',
            'password': 'test123456',
            'nickname': 'test_test',
            'phone_number': self.phone_number,
            'name': '테스트'
        }
        User.objects.create(**user_data)
        data = {'phone_number': self.phone_number, 'auth_number': self.auth_number}
        confirm_serializer = SmsConfirmSerializer(data=data)
        self.assertEqual(confirm_serializer.is_valid(), False)

    def test_sms_confirm_fail_wrong_fields_type(self):
        '''
        SmsConfirmSerializer 실패 3. 필드 값의 형식이 틀렸을 경우
        :return:
        3. {'phone_number': [ErrorDetail(string='전화번호 형식이 잘못되었습니다.', code='invalid')], 'auth_number': [ErrorDetail(string='유효한 정수(integer)를 넣어주세요.', code='invalid')]}
        '''
        data = {'phone_number': "010000000", 'auth_number': str(self.auth_number)}
        confirm_serializer = SmsConfirmSerializer(data=data)
        self.assertEqual(confirm_serializer.is_valid(), False)

