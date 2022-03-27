import json

from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from ...models import SmsAuth, User
from ...serializers import UserSerializer


class UserRetrieveTestCase(APITestCase):
    '''
    내 정보 보기 기능 테스트
    '''

    def setUp(self):
        # 내 정보 보기 테스트에서 사용할 SmsAuth
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
        # 내 정보 보기 테스트에서 사용할 User
        self.user = User.objects.create_user(**self.data)
        self.url = reverse('rest_user_details')

        # 내 정보 보기 테스트에서 사용할 Token
        self.token = str(RefreshToken.for_user(self.user).access_token)

    def test_user_retrieve_success(self):
        '''
        Header에 `Authorization: Bearer ******` 을 삽입하여 내 정보 조회 성공
        :return:
        {'username': 'test', 'email': 'test@test.com', 'nickname': 'test', 'phone_number': '01000000000', 'name': '테스트'}
        '''
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_retrieve_fail_wrong_token(self):
        '''
        Header에 `Authorization: Bearer ******` 을 삽입하여 내 정보 조회 실패 1. Token값 잘못됨
        :return:
        1. {'detail': '이 토큰은 모든 타입의 토큰에 대해 유효하지 않습니다', 'code': 'token_not_valid', 'messages': [{'token_class': 'AccessToken', 'token_type': 'access', 'message': '유효하지 않거나 만료된 토큰'}]}
        '''
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + '123456')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_retrieve_fail_wrong_key(self):
        '''
        Header에 `Authorization: Token ******` 을 삽입하여 내 정보 조회 실패 2. Header에 보내는 Authorization: 'Bearer' 잘못 입력
        :return:
        2. {'detail': '자격 인증데이터(authentication credentials)가 제공되지 않았습니다.'}
        '''
        # Token을 다르게 입력
        self.client.credentials(HTTP_AUTHORIZATION='Beare ' + self.token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_object_details_success(self):
        '''
        내 정보 조회로 조회한 내용일 일치하는지 확인
        :return:
        '''
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_serializer_data = UserSerializer(instance=self.user).data
        response_data = response.json()
        self.assertEqual(user_serializer_data, response_data)
