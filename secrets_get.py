import json
from django.core.exceptions import ImproperlyConfigured


def secret_get(name, param):
    secret_file = name

    with open(secret_file) as f:
        secrets = json.loads(f.read())

    def get_secret(setting, secrets=secrets):
        try:
            return secrets[setting]
        except KeyError:
            error_msg = "Set the {} environment variable".format(setting)
            raise ImproperlyConfigured(error_msg)

    return get_secret(param)
