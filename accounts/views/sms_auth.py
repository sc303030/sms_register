import json

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import SmsAuth, User
from ..serializers import SMSSendSerializer, SmsConfirmSerializer
from rest_framework.permissions import AllowAny


class SMSAuthSendView(APIView):
    '''
        전화번호 인증하기
        전화번호 인증 메시지 보내는 view
    '''
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = json.loads(request.body)
            # 만약 키 값에 phone_number이 없을 경우
            # 전화번호가 11자리 숫자가 맞는지 확인하기
            serializer = SMSSendSerializer(data=data)
            # 형식에 어긋나면 에러 메시지 반환
            if not serializer.is_valid():
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
            # 형식에 맞을 경우
            # 전화번호와 인증번호를 저장하거나 업데이트 하기
            SmsAuth.objects.update_or_create(phone_number=data['phone_number'])
            # 전송완료 되었으면 200 응답
            return Response({'message': ['인증번호가 전송되었습니다.']}, status.HTTP_200_OK)
        # 전송하지 못했을 경우 400 응답
        except KeyError:
            return Response({'message': ['필드 이름을 확인하세요.']}, status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response({'message': ['필드 타입을 확인하세요']}, status.HTTP_400_BAD_REQUEST)


# 회원가입 버전 인증번호 확인 View
class SMSAuthConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = json.loads(request.body)
            serializer = SmsConfirmSerializer(data=data)
            # 가입 진행을 위한 유효성 확인
            if not serializer.is_valid():
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
            phone_number, auth_number = data['phone_number'], data['auth_number']
            # 사용자가 입력한 인증번호랑 db에 저장된 인증번호랑 같은지 비교
            result = SmsAuth.check_auth_number(phone_number, auth_number)
            # 사용자가 입력한 인증번호 == db에 저장된 인증번호
            if result:
                user = User.objects.filter(phone_number=phone_number)
                # 사용자가 입력한 휴대전화번호로 가입된 User가 없거나
                # 이미 인증 확인을 진행했었지만 가입하지 않은 경우
                if not user.exists() or (user.exists() and len(user[0].email) == 0):
                    # User가 없다면 User 생성
                    if not user.exists():
                        User.objects.create(username=phone_number, phone_number=phone_number)
                    return Response({'message': ['인증에 성공하였습니다.']}, status.HTTP_200_OK)
            # 입력한 번호랑 저장된 인증번호가 다른 경우 확인 메시지 반환
            return Response({'auth_number': ['인증번호를 확인하세요.']}, status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'message': ['필드 이름을 확인하세요']}, status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response({'message': ['필드 타입을 확인하세요']}, status.HTTP_400_BAD_REQUEST)
