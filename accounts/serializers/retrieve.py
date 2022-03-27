from ..models import User
from rest_auth.serializers import UserDetailsSerializer


class UserSerializer(UserDetailsSerializer):
    '''
        내 정보 보기 기능을 위한 serializer
        기본 rest-auth/user/는 username, first_name, last_name만 보여주기 때문에
        우리의 User 모델의 다른 정보도 보여주기 위하여 커스텀
    '''

    class Meta:
        model = User
        fields = ['username', 'email', 'nickname', 'phone_number', 'name']
