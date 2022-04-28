# 로컬(or 개발)환경에서 사용하는 settings 파일
# 이 세팅으로 사용하려면
# wsgi.py, asgi.py, manage.py의 DJANGO_SETTINGS_MODULE의 값을 xxx.settings.dev로 변경

from .common import *
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from secrets_get import secret_get

# 디버깅
DEBUG = False

ALLOWED_HOSTS = ['Smsregister01-env.eba-xi4kbpzp.us-east-1.elasticbeanstalk.com']

# secrets.json 내역
# 외부로 노출되면 안되는 값들은 따로 관리하여 불러오기
# secret_get이라는 함수로 만들어서 가져오기


# SMS 설정
NAVER_KEY = {
    "ClOUD_ACCESS_KEY": secret_get('secrets.json', 'NAVER_ClOUD_ACCESS_KEY'),
    "ClOUD_SECRET_KEY": secret_get('secrets.json', 'NAVER_ClOUD_SECRET_KEY'),
    "SMS_ACCESS_ID": secret_get('secrets.json', 'SMS_ACCESS_ID'),
    "SMS_PHONE_NUMBER": secret_get('secrets.json', 'SMS_PHONE_NUMBER')
}
