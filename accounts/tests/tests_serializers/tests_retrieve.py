from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.reverse import reverse

from ...models import SmsAuth, User
from ...serializers import UserSerializer


class UserSerializerTestCase(APITestCase):
    '''
    UserSerializer 테스트 케이스
    '''

    def setUp(self):
        # UserSerializer 테스트에서 사용할 SmsAuth
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
        # UserSerializer 테스트에서 사용할 User
        self.user = User.objects.create_user(**self.data)

        # UserSerializer 테스트에서 사용할 Token
        self.token = str(RefreshToken.for_user(self.user).access_token)

        self.url = reverse('rest_user_details')

    def test_user_detail_success(self):
        '''
        UserSerializer 성공
        :return:
        '''
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.url)
        user_serializer = UserSerializer(instance=self.user)
        self.assertEqual(response.json(), user_serializer.data)

    def test_user_detail_fail_empty_fields(self):
        '''
        UserSerializer 실패 1. fields에 적은 데이터랑 response로 받은 데이터가 다름
        :return:
        '''
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.url)
        del self.data['nickname']
        user_serializer = UserSerializer(instance=self.user)
        self.assertNotEqual(response.json(), user_serializer)
