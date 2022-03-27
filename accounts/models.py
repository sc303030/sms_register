import datetime
import json

import sys
import uuid

from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from model_utils.models import TimeStampedModel
from random import randint
import hashlib
import hmac
import base64
import requests
import time

from django.conf import settings

key = settings.NAVER_KEY


# Create your models here.
# 유저의 전화번호와 인증번호를 담을 테이블
class SmsAuth(TimeStampedModel):
    phone_number = models.CharField(max_length=11, validators=[RegexValidator(r"^010?[0-9]\d{3}?\d{4}$")],
                                    primary_key=True, verbose_name='휴대폰 번호')
    auth_number = models.IntegerField(verbose_name='인증 번호')

    class Meta:
        db_table = 'sms_auth'

    def save(self, *args, **kwargs):
        self.auth_number = randint(1000, 10000)  # 4자리 랜덤 난수 생성
        super().save(*args, **kwargs)
        self.send_sms()  # SMS 전송하기(인증번호 포함)

    # 인증번호 전송
    def send_sms(self):
        timestamp = str(int(time.time() * 1000))
        uri = f'/sms/v2/services/{key["SMS_ACCESS_ID"]}/messages'
        post_url = f'https://sens.apigw.ntruss.com{uri}'

        message = "POST" + " " + uri + "\n" + timestamp + "\n" + key["ClOUD_ACCESS_KEY"]
        message = bytes(message, 'UTF-8')

        signature = self.make_signature(message)

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "x-ncp-apigw-timestamp": timestamp,
            "x-ncp-iam-access-key": key["ClOUD_ACCESS_KEY"],
            "x-ncp-apigw-signature-v2": signature
        }

        body = {
            "type": "SMS",
            "from": key["SMS_PHONE_NUMBER"],
            "content": f"[테스트] 인증번호 [{self.auth_number}]를 입력해주세요.",
            "messages": [
                {
                    "to": self.phone_number,
                }
            ],
        }

        requests.post(post_url, data=json.dumps(body), headers=headers)

    def make_signature(self, message):
        secret_key = bytes(key["ClOUD_SECRET_KEY"], 'UTF-8')
        return base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())

    @classmethod
    def check_auth_number(cls, phone_number, auth_number):
        '''
            사용자 입력 인증번호 == db에 저장된 인증번호 확인 함수
            외부의 값을 받아서 현재 모델에서 filter로 결과 확인
            해당 값이 있으면 True, 없으면 False 리턴 
        '''
        time_limit = timezone.now() - datetime.timedelta(minutes=5)
        result = cls.objects.filter(phone_number=phone_number, auth_number=auth_number, modified__gte=time_limit)
        if result:
            return True
        return False

    def __str__(self):
        return f'{self.phone_number}'


class User(AbstractUser):
    '''
        필요한 항목들 추가
    '''
    nickname = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=11, validators=[RegexValidator(r"^010?[0-9]\d{3}?\d{4}$")])
    name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.username}'
