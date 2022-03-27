from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from django.utils.translation import ugettext_lazy as _


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    '''
    TokenObtainPairSerializer 커스텀
    '''
    default_error_messages = {
        "no_active_account": _("지정된 자격 증명에 해당하는 활성화된 사용자를 찾을 수 없습니다.")
    }
