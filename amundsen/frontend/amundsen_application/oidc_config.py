# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0
import json

import logging
import os

from typing import Dict, Optional
from flask import Flask, session
from amundsen_application.config import LocalConfig
from amundsen_application.models.user import load_user, User
from authlib.integrations.flask_client import OAuth

LOGGER = logging.getLogger(__name__)
CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'

oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

def get_access_headers(app: Flask) -> Optional[Dict]:
    """
    Function to retrieve and format the Authorization Headers
    that can be passed to various microservices who are expecting that.
    :param oidc: OIDC object having authorization information
    :return: A formatted dictionary containing access token
    as Authorization header.
    """
    try:
        # noinspection PyUnresolvedReferences
        access_token = json.dumps(app.auth_client.token)
        return {'Authorization': 'Bearer {}'.format(access_token)}
    except Exception:
        return {}


def get_auth_user(app: Flask) -> User:
    """
    Retrieves the user information from oidc token, and then makes
    a dictionary 'UserInfo' from the token information dictionary.
    We need to convert it to a class in order to use the information
    in the rest of the Amundsen application.
    :param app: The instance of the current app.
    :return: A class UserInfo (Note, there isn't a UserInfo class, so we use Any)
    """
    user = session['user']
    user_info = load_user(user)
    LOGGER.debug('USER DICT FROM SESSION {}'.format(user))
    LOGGER.debug('USER INFO {}'.format(user_info))
    return user_info


class OidcConfig(LocalConfig):
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'some-google-client-id')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', 'some-google-client-secret')

    AUTH_USER_METHOD = get_auth_user
    REQUEST_HEADERS_METHOD = get_access_headers
