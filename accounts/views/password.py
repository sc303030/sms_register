import json

from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.response import Response

from ..models import User, SmsAuth
from rest_framework import status
from ..serializers import PasswordSmsConfirmSerializer, CustomPasswordChangeFieldsSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.utils.translation import ugettext_lazy as _
from rest_auth.views import PasswordChangeView


class TempPasswordView(APIView):
    '''
        비밀번호를 변경(찾기)하기 위해 전화번호 인증하기
        전화번호로 발송된 인증번호가 해당 User의 임시 비밀번호로 저장
        User는 임시번호로 비밀번호를 입력하여 새로운 비밀번호로 변경 가능
    '''
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = json.loads(request.body)
            # 등록한 회원인지 확인하기 & 전화번호 형식 확인하기
            serializer = PasswordSmsConfirmSerializer(data=data)
            if not serializer.is_valid():
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
            phone_number, auth_number = data['phone_number'], data['auth_number']
            # 사용자가 입력한 인증번호랑 db에 저장된 인증번호랑 같은지 비교
            result = SmsAuth.check_auth_number(phone_number, auth_number)
            # 사용자가 입력한 인증번호 == db에 저장된 인증번호
            if result:
                # 사용자가 입력한 휴대전화번호로 가입된 User가 있을 경우 입력한 인증번호로 임시 비밀번호 변경
                if User.objects.filter(phone_number=phone_number).exists():
                    user = User.objects.get(phone_number=phone_number)
                    user.set_password(str(auth_number))
                    user.save()
                    return Response({'message': ['인증번호로 임시 비밀번호가 변경되었습니다.']}, status.HTTP_200_OK)
            # 입력한 번호랑 저장된 인증번호가 다른 경우 확인 메시지 반환
            return Response({'auth_number': ['인증번호를 확인하세요.']}, status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'message': ['필드 이름을 확인하세요.']}, status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response({'message': ['필드 타입을 확인하세요']}, status.HTTP_400_BAD_REQUEST)


class CustomPasswordChangeView(PasswordChangeView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            # id로 user 객체 찾기
            # 기존 PasswordChangeView은 로그인 한 상태에서 진행해서 user가 request에 있지만
            # 지금은 로그인 하지 않았기 때문에 user객체를 직접 request에 지정해줘야 한다.
            data = json.loads(request.body)
            serializer = CustomPasswordChangeFieldsSerializer(data=data)
            if not serializer.is_valid():
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
            # User 객체 가져오기
            user = User.objects.get(username=data['username'])
            # request에 user를 지정하여 다음 로직에서 user의 비빌번호를 변경할 수 있도록 한다.
            request.user = user
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": ['새로운 패스워드가 저장되었습니다.']})
        except TypeError:
            return Response({'message': ['필드 타입을 확인하세요']}, status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'message': ['필드 이름을 확인하세요.']}, status.HTTP_400_BAD_REQUEST)
