import json

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from ...models import SmsAuth, User


class LoginTestCase(APITestCase):
    '''
    로그인 테스트
    식별 가능한 정보 : username(id) + password
    '''

    def setUp(self):
        # 로그인 테스트에서 사용할 SmsAuth
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
        # 로그인 테스트에서 사용할 User
        User.objects.create_user(**self.data)
        self.url = reverse('token_obtain_pair')

    def test_login_authentication_success(self):
        '''
        로그인 토근(jwt 토큰) 반환 성공
        :return:
        {'refresh': '******', 'access': '*******'}
        '''
        data = json.dumps({
            'username': self.username,
            'password': self.password
        })
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_authentication_fail_wrong_username(self):
        '''
        로그인 토근 반환 실패 1. 아이디 틀림
        :return:
        1. {'detail': '지정된 자격 증명에 해당하는 활성화된 사용자를 찾을 수 없습니다.'}
        '''
        data = json.dumps({
            'username': 'zzz',
            'password': self.password
        })
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_authentication_fail_wrong_password(self):
        '''
        로그인 토큰 반환 실패 2. 비밀번호 틀림
        :return:
        2. {'detail': '지정된 자격 증명에 해당하는 활성화된 사용자를 찾을 수 없습니다.'}
        '''
        data = json.dumps({
            'username': self.username,
            'password': 'dsdfsdf'
        })
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_authentication_fail_wrong_fields_name(self):
        '''
        로그인 토큰 반환 실패 3. 필드 이름을 틀렸을 경우
        :return:
        3. {'username': ['이 필드는 필수 항목입니다.'], 'password': ['이 필드는 필수 항목입니다.']}
        '''
        data = json.dumps({
            'user': self.username,
            'pass': 'dsdfsdf'
        })
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_jwt_token_refresh_success(self):
        '''
        Token refresh 성공
        - access_token의 시간이 만료되면 다시 refresh로 토큰을 받아야 한다.
        - 새로운 access token 반환
        :return:
        {'access' : '******'}
        '''
        data = json.dumps({
            'username': self.username,
            'password': self.password
        })
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refresh = response.json()['refresh']
        access = response.json()['access']
        url = reverse('token_refresh')
        token_data = json.dumps({
            'refresh': refresh
        })
        response2 = self.client.post(url, token_data, content_type='application/json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        access2 = response2.json()['access']
        self.assertNotEqual(access, access2)

    def test_jwt_token_refresh_fail_wrong_token(self):
        '''
        Token refresh 실패 1-1. refresh 값이 틀린 경우
        1-2. refresh 값이 비었을 경우
        :return:
        1-1. {'detail': 'Token is invalid or expired', 'code': 'token_not_valid'}
        1-2. {'refresh': ['이 필드는 blank일 수 없습니다.']}
        '''
        url = reverse('token_refresh')

        # 1-1. refresh 값이 틀린 경우
        token_data = json.dumps({
            'refresh': 'ddd'
        })
        response2 = self.client.post(url, token_data, content_type='application/json')
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)

        # 1-2. refresh 값이 비었을 경우
        token_data2 = json.dumps({
            'refresh': ''
        })
        response3 = self.client.post(url, token_data2, content_type='application/json')
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)

    def test_jwt_token_refresh_fail_wrong_fields_name(self):
        '''
        Token refresh 실패 2. 필드 이름을 틀렸을 경우
        :return:
        2. {'refresh': ['이 필드는 필수 항목입니다.']}
        '''
        data = json.dumps({
            'username': self.username,
            'password': self.password
        })
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refresh = response.json()['refresh']

        url = reverse('token_refresh')
        token_data = json.dumps({
            'refres': refresh
        })
        response2 = self.client.post(url, token_data, content_type='application/json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
