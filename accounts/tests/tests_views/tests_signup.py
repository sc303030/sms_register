import json

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from ...models import SmsAuth, User


class SignupTestCase(APITestCase):
    '''
    회원가입 테스트
    '''

    def setUp(self):
        # 회원가입 테스트에서 사용할 SmsAuth
        self.phone_number = '01000000000'  # 테스트용이기 때문에 간단한 번호 입력
        self.sms_auth = SmsAuth.objects.create(phone_number=self.phone_number)
        self.auth_number = self.sms_auth.auth_number

        # 인증번호 확인 과정에서 생성된 phone_number와 username만 있는 User 객체
        self.user = User.objects.create(phone_number=self.phone_number, username=self.phone_number)
        self.url = reverse('rest_register')

        # 이미 가입된 유저 테스트를 위한 User객체
        self.phone_number_1 = '01000000001'  # 테스트용이기 때문에 간단한 번호 입력
        self.sms_auth_1 = SmsAuth.objects.create(phone_number=self.phone_number_1)
        self.auth_number_1 = self.sms_auth_1.auth_number

        self.data = {
            'username': 'test_1',
            'email': 'test_1@test.com',
            'password': 'test123456',
            'nickname': 'test_1',
            'phone_number': self.phone_number_1,
            'name': '테스트일'
        }
        User.objects.create_user(**self.data)

    def test_signup_user_create_success(self):
        '''
        회원가입 성공 1. 모든 필드 값이 다 들어간 경우
        2. 가입하지 않은 전화번호일 경우(중복 x)
        3. 전화번호 인증 과정을 거친 경우
        4. password1 과 password2의 값이 같을 경우
        5. rest-auth의 비밀번호 조건에 부합한 경우
        :return:
        {'token': '************', 'user': {'username': 'test', 'email': 'test@test.com', 'nickname': 'nick_test', 'phone_number': '01000000000', 'name': '테스트'}}
        '''
        data = json.dumps({
            'username': 'test__1',
            'email': 'test@test.com',
            'password1': 'test123456',
            'password2': 'test123456',
            'nickname': 'nick_test_!',
            'phone_number': self.phone_number,
            'name': '테스트'
        })
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 두 번째 유저 가입
        phone_number = '01000000002'
        sms2 = SmsAuth.objects.create(phone_number=phone_number)
        auth_number2 = sms2.auth_number
        url = reverse('sms_auth_confirm')
        user2_data = json.dumps({
            'phone_number': phone_number,
            'auth_number': auth_number2
        })
        self.client.post(url, user2_data, content_type='application/json')

        user2_data_signup = json.dumps({
            'username': 'test2',
            'email': 'test2@test.com',
            'password1': 'test123456',
            'password2': 'test123456',
            'nickname': 'nick_test2',
            'phone_number': phone_number,
            'name': '테스트이'
        })

        response2 = self.client.post(self.url, user2_data_signup, content_type='application/json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.all().count(), 3)

    def test_signup_user_create_fail_blink_fields(self):
        '''
        회원가입 실패 1. 필수 필드에 빈 값이 있을 경우( 모든 필드가 필수 필드)
        :return:
        1. {'username': ['이 필드는 blank일 수 없습니다.'], 'email': ['이 필드는 blank일 수 없습니다.'], 'password1': ['이 필드는 blank일 수 없습니다.'], 'password2': ['이 필드는 blank일 수 없습니다.'], 'nickn
ame': ['이 필드는 blank일 수 없습니다.'], 'phone_number': ['이 필드는 blank일 수 없습니다.'], 'name': ['이 필드는 blank일 수 없습니다.']}
        '''
        data = json.dumps({
            'username': '',
            'email': '',
            'password1': '',
            'password2': '',
            'nickname': '',
            'phone_number': '',
            'name': ''
        })
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_user_create_fail_already_user(self):
        '''
        회원가입 실패 2. 중복값을 입력한 경우
        :return:
        2. {'username': ['해당 사용자 이름은 이미 존재합니다.'], 'email': ['이미 이 이메일 주소로 등록된 사용자가 있습니다.'], 'nickname': ['이미 이 닉네임으로 등록된 사용자가 있습니다.'], 'phone_number': ['가입내역이 있습
니다. 로그인을 진행해주세요.']}
        '''
        # 2. 모든 정보를 동일하게 가입
        data = json.dumps({
            'username': 'test_1',
            'email': 'test_1@test.com',
            'password1': 'test123456',
            'password2': 'test123456',
            'nickname': 'test_1',
            'phone_number': self.phone_number_1,
            'name': '테스트일'
        })
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_user_create_fail_not_sms_auth(self):
        '''
        회원가입 실패  3. 인증과정을 거치지 않은 핸드폰 번호로 가입하는 경우
            - 원래는 인증을 거친후에 확인된 User만 회원가입을 할 수 있지만
            혹시 모를 경우를 대비하여 다시 한 번 오류 반환
        :return:
        3. {'phone_number': ['전화번호 인증 후 회원가입을 진행해주세요.']}
        '''

        # 3. 전화번호 인증을 하지 않았을 경우
        data = json.dumps({
            'username': 'fail_test_new',
            'email': 'fail_test_new@test.com',
            'password1': 'test123456',
            'password2': 'test123456',
            'nickname': '실패_new_테스트',
            'phone_number': "01000000002",
            'name': '실패새로운테스트'
        })
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_user_create_fail_diff_password1_2(self):
        '''
        회원가입 실패 4. password1과 password2가 다를 경우
        :return:
        4. {'non_field_errors': ['두 개의 패스워드 필드가 서로 맞지 않습니다.']}
        '''

        # 4. 비밀번호와 비밀번호 확인이 서로 다를 경우
        data = json.dumps({
            'username': 'fail_test_new',
            'email': 'fail_test_new@test.com',
            'password1': 'test123456zzz',
            'password2': 'test123456',
            'nickname': '실패_new_테스트',
            'phone_number': self.phone_number,
            'name': '실패새로운테스트'
        })
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_user_create_fail_not_match_type(self):
        '''
        회원가입 실패 5. 필드 값이 형식에 맞지 않는 경우
        :return:
        5. {'username': ['ID 형식이 잘못되었습니다.'], 'email': ['유효한 이메일 주소를 입력하십시오.'], 'password1': ['비밀번호가 너무 짧습니다. 최소 8 문자를 포함해야 합니다.', '비밀번호가 너무 일상적
인 단어입니다.', '비밀번호가 전부 숫자로 되어 있습니다.'], 'nickname': ['닉네임 형식이 잘못되었습니다.'], 'phone_number': ['전화번호 형식이 잘못되었습니다.'], 'name': ['이름 형식이 잘못되었습니다.']}
        '''

        data = json.dumps({
            'username': '1zzz',
            'email': 'fail_test_new',
            'password1': '1234',
            'password2': '1234',
            'nickname': '실패_new_테스트ㄱㄴㄹ',
            'phone_number': '121212',
            'name': '121212'
        })
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_user_create_fail_wrong_fields_name(self):
        '''
        회원가입 실패 6. 필드 이름 틀렸을 경우
        :return:
        6. {'username': ['이 필드는 필수 항목입니다.'], 'email': ['이 필드는 필수 항목입니다.'], 'password1': ['이 필드는 필수 항목입니다.'], 'password2': ['이 필드는 필수 항목입니다.'], 'nickname': [
'이 필드는 필수 항목입니다.'], 'phone_number': ['이 필드는 필수 항목입니다.'], 'name': ['이 필드는 필수 항목입니다.']}
        '''

        data = json.dumps({
            'user': '1zzz',
            'ema': 'fail_test_new',
            'pass': '1234',
            'pass2': '1234',
            'nick': '실패_new_테스트',
            'phone': '121212',
            'na': '121212'
        })
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)