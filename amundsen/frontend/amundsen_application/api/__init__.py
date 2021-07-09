# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Tuple
import logging

from flask import Flask, redirect, render_template, session, url_for
import jinja2
import os

from amundsen_application.oidc_config import oauth


ENVIRONMENT = os.getenv('APPLICATION_ENV', 'development')
LOGGER = logging.getLogger(__name__)


def init_routes(app: Flask) -> None:
    app.add_url_rule('/healthcheck', 'healthcheck', healthcheck)
    app.add_url_rule('/', 'index', index, defaults={'path': ''})  # also functions as catch_all
    app.add_url_rule('/<path:path>', 'index', index)  # catch_all
    app.add_url_rule('/authorization-code/callback', 'auth', auth)

def login():
    redirect_uri = url_for(
                'auth',
                _external=True,
                _scheme='http')
    return oauth.google.authorize_redirect(redirect_uri)


def index(path: str) -> Any:
    user = session.get('user')
    # import pdb
    # pdb.set_trace()
    try:
        token = session['token']
    except KeyError:
        LOGGER.debug("User not logged in, redirect to auth")
        return login()
    try:
        return render_template("index.html", env=ENVIRONMENT)  # pragma: no cover
    except jinja2.exceptions.TemplateNotFound as e:
        LOGGER.error("index.html template not found, have you built the front-end JS (npm run build in static/?")
        raise e

def auth():
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token)
    session['token'] = token
    session['user'] = user
    return redirect(url_for(
                'index',
                _external=True,
                _scheme='http')
    )


def healthcheck() -> Tuple[str, int]:
    return '', 200  # pragma: no cover
