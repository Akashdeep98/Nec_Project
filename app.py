from flask import *
from flask_oidc import OpenIDConnect
from okta import UsersClient

app = Flask(__name__)
app.config["OIDC_CLIENT_SECRETS"] = "clients_secrets.json"
app.config["OIDC_COOKIE_SECURE"] = False
app.config["OIDC_CALLBACK_ROUTE"] = "/end/callback"
app.config["OIDC_SCOPES"] = ["openid", "email", "profile"]
app.config["SECRET_KEY"] = "{{ LONG_RANDOM_STRING }}"
oidc = OpenIDConnect(app)

okta_client = UsersClient("https://dev-764808.okta.com", "00eyvjQ5-edxVO-whsoxWbORgbfr7kc--8cuSckLzZ")


@app.before_request
def before_request():
    if oidc.user_loggedin:
        g.user = okta_client.get_user(oidc.user_getfield("sub"))
    else:
        g.user = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/login")
@oidc.require_login
def login():
    return redirect(url_for(".dashboard"))


@app.route("/logout")
def logout():
    oidc.logout()
    return redirect(url_for(".index"))
