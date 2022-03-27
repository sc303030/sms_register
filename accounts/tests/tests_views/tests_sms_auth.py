import json

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from ...models import SmsAuth, User


class SmsAuthSendTestCase(APITestCase):
    '''
    회원가입 전 전화번호 인증 테스트
    '''

    def setUp(self):
        # 인증번호 테스트에서 사용할 SmsAuth
        self.phone_number = '01000000000'  # 테스트용이기 때문에 간단한 번호 입력
        self.sms_auth = SmsAuth.objects.create(phone_number=self.phone_number)
        # 인증번호를 활용하여 회원가입 단계로 진행됨
        # 실제로 api에서는 문자로 받은 번호로 인증하여 값을 리턴받지만
        # 테스트를 실행하면 객체의 인증번호가 초기화되어서 다시 인증이 잘 안되는 경우 발생
        # 그래서 저장한 객체의 인증번호로 인증 테스트 진행
        self.auth_number = self.sms_auth.auth_number
        self.sms_send_url = reverse('sms_auth_send')
        self.sms_confirm_url = reverse('sms_auth_confirm')

    # def test_sms_auth_send_view_success(self):
    #     '''
    #     인증번호 발신 성공
    #     1. 전화번호가 형식에 맞는 경우
    #     2. key값을 제대로 입력한 경우
    #     :return
    #     1. {'detail': ['인증번호가 전송되었습니다.']}
    #     2. 전화번호로 인증번호 전송
    #     '''
    #     phone_number = "01049486035"  # 인증번호 받을 전화번호 입력
    #     data = json.dumps({'phone_number': phone_number})
    #     response = self.client.post(self.sms_send_url, data, content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    #     # 실제로 보낸 문자와 일치하는지 확인하기
    #     # print로 나온 보안 문자와 문자메시지로 온 문자가 일치하는지 확인하기
    #     sms_auth = SmsAuth.objects.get(phone_number=phone_number)
    #     print(f'실제로 보낸 보안문자 : {sms_auth.auth_number}')

    def test_sms_auth_send_view_fail_wrong_fields_type(self):
        '''
        인증번호 발신 실패 1. 필드 값이 형식과 틀렸을 경우
        :return
        1. {'phone_number': ['전화번호 형식이 잘못되었습니다.']}
        '''
        # 1. 전화번호가 형식에 맞지 않은 경우
        data = json.dumps({'phone_number': '0000'})
        response = self.client.post(self.sms_send_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sms_auth_send_view_fail_wrong_fields_name(self):
        '''
        인증번호 발신 실패 2. 필드 이름을 잘못 입력한 경우
        :return
        2.  {'phone_number': ['이 필드는 필수 항목입니다.']}
        '''
        data = json.dumps({'phone_numb': '01000000000'})
        response = self.client.post(self.sms_send_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sms_auth_send_view_fail_empty_fields(self):
        '''
        인증번호 발신 실패 3. 필드 값을 빈 값으로 보낸 경우
        :return
        3. {'phone_number': ['이 필드는 blank일 수 없습니다.']}
        '''
        data = json.dumps({'phone_number': ''})
        response = self.client.post(self.sms_send_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sms_auth_confirm_view_success(self):
        '''
        인증번호 인증 성공 1. 필드 값을 모두 채웠는지
        2. 입력한 값들이 모두 형식에 맞는지
        3. 인증을 진행한 번호인지
        4. 발신된 인증번호와 사용자가 입력한 인증번호가 일치하는지(5분 안에 인증번호 확인을 진행하였는지)
        5. 이미 회원가입한 번호인데 다시 회원가입 인증을 진행하는지
        - setUp에서 만든 객체를 활용하여 인증확인 진행
        :return:
        {'message': ['인증에 성공하였습니다.']}
        '''
        data = json.dumps({
            "phone_number": self.phone_number,
            "auth_number": self.auth_number
        })
        response = self.client.post(self.sms_confirm_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.all().count(), 1)

    def test_sms_auth_confirm_view_fail_empty_fields(self):
        '''
        인증번호 인증 실패 1. 필수 필드 빈 값으로 보낸 경우
        :return:
        1. {'phone_number': ['이 필드는 blank일 수 없습니다.'], 'auth_number': ['유효한 정수(integer)를 넣어주세요.']}
        '''
        data = json.dumps({
            "phone_number": '',
            "auth_number": ''
        })
        response = self.client.post(self.sms_confirm_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sms_auth_confirm_view_fail_length(self):
        '''
        인증번호 인증 실패 2-1. 입력한 값들이 형식에 맞지 않을 경우(전화번호 형식 틀림)
        2-2-1. 인증번호 형식 틀림(문자입력)
        2-2-2. 1000보다 작은 값 입력
        :return:
        2-1. {'phone_number': ['전화번호 형식이 잘못되었습니다.']}
        2-2-1. {'auth_number': ['유효한 정수(integer)를 넣어주세요.']}
        2-2-2. {'auth_number': ['이 값이 1000보다 크거나 같은지 확인하십시오.']}
        '''
        # 2-1
        data1 = json.dumps({
            "phone_number": "000000",
            "auth_number": self.auth_number
        })
        response1 = self.client.post(self.sms_confirm_url, data1, content_type='application/json')
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)

        # 2-2-1
        data2 = json.dumps({
            "phone_number": self.phone_number,
            "auth_number": 'zxzxzx'
        })
        response2 = self.client.post(self.sms_confirm_url, data2, content_type='application/json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

        # 2-2-2
        data3 = json.dumps({
            "phone_number": self.phone_number,
            "auth_number": 999
        })
        response3 = self.client.post(self.sms_confirm_url, data3, content_type='application/json')
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sms_auth_confirm_view_fail_already_number(self):
        '''
        인증번호 인증 실패 3. 인증을 진행한 번호인지
        :return:
        3. {'phone_number': ['전화번호 인증을 진행해주세요.']}
        '''

        data = json.dumps({
            "phone_number": "01000000001",
            "auth_number": self.auth_number
        })
        response = self.client.post(self.sms_confirm_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sms_auth_confirm_view_fail_equal(self):
        '''
        인증번호 인증 실패 4. 발신된 인증번호와 사용자가 입력한 인증번호가 일치하는지
        - 5분안에 인증번호 확인을 진행하였는지
        :return:
        4.  {'auth_number': ['인증번호를 확인하세요.']}
        '''

        data = json.dumps({
            "phone_number": self.phone_number,
            "auth_number": 1111
        })
        response = self.client.post(self.sms_confirm_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sms_auth_confirm_view_fail_already_user(self):
        '''
        인증번호 인증 실패 5. 이미 회원가입한 번호인데 다시 회원가입 인증을 진행하는지
        - setUp에서 만든 객체를 활용하여 인증확인 진행
        :return:
        5. {'phone_number': ['가입내역이 있습니다. 로그인을 진행해주세요.']}
        '''

        # 4. 이미 존재하는 회원일 경우
        User.objects.create(phone_number=self.phone_number, username='test', email='test@test.com')
        data = json.dumps({
            "phone_number": self.phone_number,
            "auth_number": self.auth_number
        })
        response = self.client.post(self.sms_confirm_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sms_auth_confirm_view_fail_wrong_fields_name(self):
        '''
        인증번호 인증 실패 6. 필드 이름 틀렸을 때
        :return:
        6. {'phone_number': ['이 필드는 필수 항목입니다.'], 'auth_number': ['이 필드는 필수 항목입니다.']}
        '''

        data = json.dumps({
            "phone": "01000000001",
            "auth": self.auth_number
        })
        response = self.client.post(self.sms_confirm_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sms_auth_confirm_dummy(self):
        '''
        회원 인증 여러명 테스트 하기
        - 2명 생성하여 User 객체에 2명이 있는지 비교하기
        :return:
        {'message': ['인증에 성공하였습니다.']}
        {'message': ['인증에 성공하였습니다.']}
        True
        '''

        def create_sms_auth(phone):
            phone_number = phone  # 테스트용이기 때문에 간단한 번호 입력
            sms_auth = SmsAuth.objects.create(phone_number=phone_number)
            auth_number = sms_auth.auth_number

            data = json.dumps({
                "phone_number": phone_number,
                "auth_number": auth_number
            })
            return data

        data1 = create_sms_auth('01000000001')
        data2 = create_sms_auth('01000000002')

        response1 = self.client.post(self.sms_confirm_url, data1, content_type='application/json')
        response2 = self.client.post(self.sms_confirm_url, data2, content_type='application/json')

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.all().count(), 2)

    def test_sms_auth_several_times_confirm(self):
        '''
        전화번호 인증을 여러번 했지만 가입하지 않은 경우
        :return:
        {'message': ['인증번호가 전송되었습니다.']}
        {'message': ['인증에 성공하였습니다.']}
        {'message': ['인증번호가 전송되었습니다.']}
        {'message': ['인증에 성공하였습니다.']}
        '''
        phone_number = '01000000001'
        data = json.dumps({'phone_number': phone_number})

        response1 = self.client.post(self.sms_send_url, data, content_type='application/json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        auth_number = SmsAuth.objects.get(phone_number=phone_number).auth_number
        data2 = json.dumps({
            'phone_number': phone_number,
            'auth_number': auth_number
        })
        response2 = self.client.post(self.sms_confirm_url, data2, content_type='application/json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        response3 = self.client.post(self.sms_send_url, data, content_type='application/json')
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        auth_number2 = SmsAuth.objects.get(phone_number=phone_number).auth_number
        data3 = json.dumps({
            'phone_number': phone_number,
            'auth_number': auth_number2
        })
        response4 = self.client.post(self.sms_confirm_url, data3, content_type='application/json')
        self.assertEqual(response4.status_code, status.HTTP_200_OK)
