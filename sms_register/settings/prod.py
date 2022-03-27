# 배포 환경(ex. 클라우드)에서 사용하는 settings 파일
# 이 세팅으로 사용하려면
# wsgi.py, asgi.py, manage.py의 DJANGO_SETTINGS_MODULE의 값을 xxx.settings.prod로 변경

from .common import *

# 필요한 값들은 외부 설정파일에서 설정하여 값을 받아옴

SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# SMS 설정
NAVER_ClOUD_ACCESS_KEY = os.environ.get('NAVER_ClOUD_ACCESS_KEY')
NAVER_ClOUD_SECRET_KEY = os.environ.get('NAVER_ClOUD_SECRET_KEY')

SMS_ACCESS_ID = os.environ.get('SMS_ACCESS_ID')
SMS_PHONE_NUMBER = os.environ.get('SMS_ACCESS_ID')
