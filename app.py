from flask import *
from flask_oidc import OpenIDConnect
from okta import UsersClient
import jwt
import requests
from jwt.algorithms import RSAAlgorithm
import json

app = Flask(__name__)
app.config["OIDC_CLIENT_SECRETS"] = "clients_secrets.json"
app.config["OIDC_COOKIE_SECURE"] = False
app.config["OIDC_CALLBACK_ROUTE"] = "/end/callback"
app.config["OIDC_SCOPES"] = ["openid", "email", "profile"]
app.config["OIDC_ID_TOKEN_COOKIE_NAME"]="oidc_token"
app.config["SECRET_KEY"] = "{{ LONG_RANDOM_STRING }}"
oidc = OpenIDConnect(app)
okta_client = UsersClient("https://dev-764808.okta.com", "00eyvjQ5-edxVO-whsoxWbORgbfr7kc--8cuSckLzZ")


def convert(data):
    if isinstance(data, bytes):  return data.decode('ascii')
    return data


@app.before_request
def before_request():
    if oidc.user_loggedin:
        if oidc.get_access_token() is None:
            oidc.logout()
        else:
            g.user = okta_client.get_user(oidc.user_getfield("sub"))
            access_token=oidc.get_access_token()
            keys_respose=requests.get("https://dev-764808.okta.com/oauth2/default/v1/keys").content
            keys_respose=convert(keys_respose)
            keys_respose=json.loads(keys_respose)
            key_json = keys_respose['keys'][0];
            aud= "api://default"
            public_key = RSAAlgorithm.from_jwk(json.dumps(key_json))
            decoded = jwt.decode(access_token, public_key,audience=aud, algorithms='RS256')
            g.groups = decoded["groups"]
    else:
        g.user = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
@oidc.require_login
def dashboard():

    if 'applicant' in g.groups:
        g.userRole = 'applicant'
        return render_template("applicant/applicant_dashboard.html")
    elif 'recruiter' in g.groups:
        g.userRole = 'recruiter'
        return render_template("recruiter/recruiter_dashboard.html")


@app.route("/login")
@oidc.require_login
def login():
    return redirect(url_for(".dashboard"))


@app.route("/logout")
def logout():
    oidc.logout()
    return redirect(url_for(".index"))

# app.run(debug=True)
