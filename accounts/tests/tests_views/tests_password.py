import json

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from ...models import SmsAuth, User
from django.contrib.auth.hashers import check_password


class TempPasswordTestCase(APITestCase):
    '''
    비밀번호 재설정 시 인증번호 보내고 해당 인증번호로 임시 비밀번호 설정하는 테스트
    '''

    def setUp(self):
        # 임시 비밀번호 테스트에서 사용할 SmsAuth
        self.phone_number = '01000000000'  # 테스트용이기 때문에 간단한 번호 입력
        self.sms_auth = SmsAuth.objects.create(phone_number=self.phone_number)

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
        # 임시 비밀번호 테스트에서 사용할 User
        self.user = User.objects.create_user(**self.data)

        self.temp_password_url = reverse('sms_temp_password')

    def test_temp_password_success(self):
        '''
        전화번호 인증 후 해당 인증번호로 임시 비밀번호 변경 성공
        1. 전화번호 인증을 먼저 진행
        2. 전화번호로 온 인증번호를 입력하여 해당 유저의 비밀번호를 인증번호로 임시로 변경
        :return:
        {'message': ['인증번호로 임시 비밀번호가 변경되었습니다.']}
        '''
        # 1. 전화번호 인증을 먼저 진행
        # 미리 가입했던 회원이니 다시 한 번 인증 진행
        url = reverse('sms_auth_send')
        data = json.dumps({"phone_number": self.phone_number})
        self.client.post(url, data, content_type='application/json')
        sms_auth = SmsAuth.objects.get(phone_number=self.phone_number)
        # 임시로 저정된 비밀번호로 변경하기 위해 인증번호를 변수로
        auth_number = sms_auth.auth_number

        # 2. 전화번호로 온 인증번호를 입력하여 해당 유저의 비밀번호를 인증번호로 임시로 변경
        data2 = json.dumps({
            "phone_number": self.phone_number,
            "auth_number": auth_number
        })
        response = self.client.post(self.temp_password_url, data2, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # user의 비밀번호와 인증번호가 일치하는지 확인하기
        user = User.objects.get(phone_number=self.phone_number)
        check_password_tf = user.check_password(str(auth_number))
        self.assertEqual(check_password_tf, True)

    def test_temp_password_fail_phone_length(self):
        '''
        전화번호 인증 후 해당 인증번호로 임시 비밀번호 변경 실패 1. 필드 값이 형식에 맞지 않은 경우
        :return:
        {'phone_number': ['전화번호 형식이 잘못되었습니다.'], 'auth_number': ['유효한 정수(integer)를 넣어주세요.']}
        '''
        # 1. 전화번호 인증을 먼저 진행
        # 미리 가입했던 회원이니 다시 한 번 인증 진행
        url = reverse('sms_auth_send')
        data = json.dumps({"phone_number": self.phone_number})
        self.client.post(url, data, content_type='application/json')
        sms_auth = SmsAuth.objects.get(phone_number=self.phone_number)
        # 임시로 저정된 비밀번호로 변경하기 위해 인증번호를 변수로
        auth_number = sms_auth.auth_number

        # 2. 전화번호로 온 인증번호를 입력하여 해당 유저의 비밀번호를 인증번호로 임시로 변경
        data2 = json.dumps({
            "phone_number": "121212",
            "auth_number": str(auth_number)
        })
        response = self.client.post(self.temp_password_url, data2, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_temp_password_fail_not_sms_auth_user(self):
        '''
        전화번호 인증 후 해당 인증번호로 임시 비밀번호 변경 실패 2. 전화번호 인증 내역이 없는 경우
        :return:
        2. {'phone_number': ['가입한 회원이 아닙니다.']}
        '''
        # 1. 전화번호 인증을 먼저 진행
        url = reverse('sms_auth_send')
        data = json.dumps({"phone_number": self.phone_number})
        self.client.post(url, data, content_type='application/json')
        sms_auth = SmsAuth.objects.get(phone_number=self.phone_number)
        # 임시로 저정된 비밀번호로 변경하기 위해 인증번호를 변수로
        auth_number = sms_auth.auth_number

        # 2. 전화번호로 온 인증번호를 입력하여 해당 유저의 비밀번호를 인증번호로 임시로 변경
        data2 = json.dumps({
            "phone_number": "01000000001",
            "auth_number": auth_number
        })
        response = self.client.post(self.temp_password_url, data2, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_temp_password_fail_not_signup_user(self):
        '''
        전화번호 인증 후 해당 인증번호로 임시 비밀번호 변경 실패 3. 전화번호 인증은 했었지만 가입하지 않은 경우
        :return:
        3. {'phone_number': ['가입한 회원이 아닙니다.']}
        '''
        # 1. 전화번호 인증을 먼저 진행
        phone_number = '01000000001'  # 테스트용이기 때문에 간단한 번호 입력
        sms_auth = SmsAuth.objects.create(phone_number=phone_number)
        # 임시로 저정된 비밀번호로 변경하기 위해 인증번호를 변수로
        auth_number = sms_auth.auth_number

        # 2. 전화번호로 온 인증번호를 입력하여 해당 유저의 비밀번호를 인증번호로 임시로 변경
        data2 = json.dumps({
            "phone_number": phone_number,
            "auth_number": auth_number
        })
        response = self.client.post(self.temp_password_url, data2, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_temp_password_fail_wrong_auth_number(self):
        '''
        전화번호 인증 후 해당 인증번호로 임시 비밀번호 변경 실패 4. 인증번호가 틀렸을 경우
        :return:
        4. {'auth_number': ['인증번호를 확인하세요.']}
        '''
        # 1. 전화번호 인증을 먼저 진행
        # 미리 가입했던 회원이니 다시 한 번 인증 진행
        url = reverse('sms_auth_send')
        data = json.dumps({"phone_number": self.phone_number})
        self.client.post(url, data, content_type='application/json')

        # 2. 전화번호로 온 인증번호를 입력하여 해당 유저의 비밀번호를 인증번호로 임시로 변경
        data2 = json.dumps({
            "phone_number": self.phone_number,
            "auth_number": 1234
        })
        response = self.client.post(self.temp_password_url, data2, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_temp_password_fail_wrong_type(self):
        '''
        전화번호 인증 후 해당 인증번호로 임시 비밀번호 변경 실패 5. 필드 값의 형식이 틀렸을 경우
        :return:
        5-1. {'phone_number': ['전화번호 형식이 잘못되었습니다.'], 'auth_number': ['유효한 정수(integer)를 넣어주세요.']}
        5-2. {'auth_number': ['이 값이 1000보다 크거나 같은지 확인하십시오.']}
        '''
        # 1. 전화번호 인증을 먼저 진행
        # 미리 가입했던 회원이니 다시 한 번 인증 진행
        url = reverse('sms_auth_send')
        data = json.dumps({"phone_number": self.phone_number})
        self.client.post(url, data, content_type='application/json')

        # 2. 전화번호로 온 인증번호를 입력하여 해당 유저의 비밀번호를 인증번호로 임시로 변경
        # 5-1
        data2 = json.dumps({
            "phone_number": '010000000',
            "auth_number": '1234'
        })
        response = self.client.post(self.temp_password_url, data2, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 5-2
        data3 = json.dumps({
            "phone_number": '01000000000',
            "auth_number": 999
        })
        response2 = self.client.post(self.temp_password_url, data3, content_type='application/json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordChangeTestCase(APITestCase):
    '''
    비밀번호 재설정 테스트
    '''

    def setUp(self):
        # 1. 회원가입 전 전화번호 인증 진행
        # 비밀번호 재설정 테스트에서 용할 SmsAuth
        self.phone_number = '01000000000'  # 테스트용이기 때문에 간단한 번호 입력
        SmsAuth.objects.create(phone_number=self.phone_number)

        # 2. 인증 후 회원가입
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
        # 임시 비밀번호 테스트에서 사용할 User
        User.objects.create_user(**self.data)

        self.sms_auth_send = reverse('sms_auth_send')
        self.temp_password_url = reverse('sms_temp_password')
        self.password_change_url = reverse('password_change')

        # 3. 비밀번호 재설정을 위해 다시 전화번호 인증하기
        self.re_data = json.dumps({
            'phone_number': self.phone_number
        })
        self.client.post(self.sms_auth_send, self.re_data, content_type='application/json')

        self.sms_auth = SmsAuth.objects.get(phone_number=self.phone_number)
        self.auth_number = self.sms_auth.auth_number

        # 4. 비밀번호 임시 비밀번호로 설정하기
        self.temp_data = json.dumps({
            'phone_number': self.phone_number,
            'auth_number': self.auth_number
        })
        self.client.post(self.temp_password_url, self.temp_data, content_type='application/json')
        self.user = User.objects.get(phone_number=self.phone_number)

    def test_password_change_success(self):
        '''
        비밀번호 변경 성공
        :return:
        {'message': ['새로운 패스워드가 저장되었습니다.']}
        '''
        change_password = '123456789zzz'
        data = json.dumps({
            'username': self.username,
            "old_password": str(self.auth_number),
            "new_password1": change_password,
            "new_password2": change_password
        })
        response = self.client.post(self.password_change_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # change_password랑 user에 저장된 password랑 같은지 확인하기
        user = User.objects.get(username=self.username)
        check_password_tf = user.check_password(change_password)
        self.assertEqual(check_password_tf, True)

    def test_password_change_fail_empty_required(self):
        '''
        비밀번호 변경 실패 1. 필수 필드 값이 빈 값일 경우
        :return:
        1. response1 {'old_password': ['이 필드는 blank일 수 없습니다.'], 'new_password1': ['이 필드는 blank일 수 없습니다.'], 'new_password2': ['이 필드는 blank일 수 없습니다.'], 'username': ['이 필드는 blank일 수 없습니다.']}
        '''
        data = json.dumps({
            'username': '',
            "old_password": '',
            "new_password1": '',
            "new_password2": ''
        })
        response = self.client.post(self.password_change_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_change_fail_wrong_username(self):
        '''
        비밀번호 변경 실패 2. 존재하지 않는 username을 입력했을 경우
        :return:
        2. {'username': ['가입한 회원이 아닙니다.']}
        '''
        change_password = '123456789zzz'
        data = json.dumps({
            'username': 'test1234',
            "old_password": str(self.auth_number),
            "new_password1": change_password,
            "new_password2": change_password
        })
        response = self.client.post(self.password_change_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_change_fail_wrong_password(self):
        '''
        비밀번호 변경 실패 3-1. 임시 비밀번호가 틀렸을 경우
        3-2. password1과 password2가 다를경우
        :return:
        3-1. {'old_password': ['임시 비밀번호가 일치하지 않습니다.']}
        3-2. {'new_password2': ['비밀번호가 일치하지 않습니다.']}
        '''
        change_password = '123456789zzz'

        # 3-1. 임시 비밀번호가 틀렸을 경우
        data1 = json.dumps({
            'username': self.username,
            "old_password": '0000',
            "new_password1": change_password,
            "new_password2": change_password
        })
        response1 = self.client.post(self.password_change_url, data1, content_type='application/json')
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)

        # 3-2. password1과 password2가 다를경우
        data2 = json.dumps({
            'username': self.username,
            "old_password": self.auth_number,
            "new_password1": change_password,
            "new_password2": '12121'
        })
        response2 = self.client.post(self.password_change_url, data2, content_type='application/json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_change_fail_wrong_fields_type(self):
        '''
        비밀번호 변경 실패 4. 필드 값의 형식이 틀렸을 경우
        :return:
        4. {'username': ['ID 형식이 잘못되었습니다.']}
        '''
        change_password = '123456789zzz'
        data = json.dumps({
            'username': '1zczx',
            "old_password": str(self.auth_number),
            "new_password1": change_password,
            "new_password2": change_password
        })
        response = self.client.post(self.password_change_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
