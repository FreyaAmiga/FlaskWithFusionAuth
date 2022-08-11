"""
This code was based on https://github.com/FusionAuth/fusionauth-example-python-flask
I ended up creating a complete new version
"""

import os
from flask import Flask, request, render_template, session, redirect, url_for
from fusionauth.fusionauth_client import FusionAuthClient
from datetime import timedelta

# Step 1. Create an application according to https://fusionauth.io/docs/v1/tech/5-minute-setup-guide
# Step 2. Change the variables here to what your application needs
# BEGIN: Variables to update
fusionauth_api_key = "Tzo5j1mK........T_ip07t19RMLhn-ZI21sKg_"  # Can be left empty
fusionauth_client_id = "59c540ca-....-.....-.....-40c1a40c0b76"  # Can be found in the list of applications
fusionauth_client_secret = "41X78fC...............ccQ62Hd90wnUus"  # View your app
                                                                          # This can be found under OAuth Configuration
fusionauth_protocol = "http"  # Set this to https if needed
fusionauth_host_ip = "172.16.0.200"  # The host where FusionAuth is running
fusionauth_host_port = "9011"  # The port on wich FusionAuth is running
# END: Variables to update

client = FusionAuthClient(fusionauth_api_key,
                          f"{fusionauth_protocol}://{fusionauth_host_ip}:{fusionauth_host_port}")
app = Flask(__name__)
# By default, sessions in Flask will expire when browser is closed, or after 31 days.
app.permanent_session_lifetime = timedelta(minutes=60)


def set_session_variable(array_in, key, pre=None, default=None):
    if key in array_in:
        session_key = key
        if pre:
            session_key = f"{pre}.{key}"
        session[f"{session_key}"] = array_in[key]
    elif default:
        session_key = key
        if pre:
            session_key = f"{pre}.{key}"
        session[f"{session_key}"] = default


@app.route("/")
def index():
    app.logger.info(f"Session: {session}")
    return render_template("public/index.html", login_uri="/login", register_uri="/register")


@app.route("/login", methods=["GET", "POST"])
def login_form():
    # app.logger.info(f"Request method: {request.method}")
    if request.method == 'POST':
        app.logger.info("Login POSTED")
        username = request.form['username']
        password = request.form['password']
        # app.logger.info(f"username: {username}, password {password}")
        response = client.login({
            'loginId': username,
            'password': password,
            'applicationId': fusionauth_client_id
        })
        if response.success_response:
            user = response.success_response['user']
            # See https://fusionauth.io/docs/v1/tech/apis/login, I just made a selection
            set_session_variable(array_in=user, key='id', pre="FusionAuth.user")
            set_session_variable(array_in=user, key='state', pre="FusionAuth.user")
            set_session_variable(array_in=user, key='token', pre="FusionAuth.user")
            set_session_variable(array_in=user, key='email', pre="FusionAuth.user")
            set_session_variable(array_in=user, key='expiry', pre="FusionAuth.user")
            set_session_variable(array_in=user, key='firstName', pre="FusionAuth.user")
            set_session_variable(array_in=user, key='middleName', pre="FusionAuth.user")
            set_session_variable(array_in=user, key='lastName', pre="FusionAuth.user")
            set_session_variable(array_in=user, key='username', pre="FusionAuth.user")
            set_session_variable(array_in=user, key='verified', pre="FusionAuth.user")
            set_session_variable(array_in=user, key='insertInstant', pre="FusionAuth.user")
            set_session_variable(array_in=user, key='lastUpdateInstant', pre="FusionAuth.user")
            set_session_variable(array_in=user, key='lastLoginInstant', pre="FusionAuth.user")
            set_session_variable(array_in=user, key='passwordLastUpdateInstant', pre="FusionAuth.user")
            set_session_variable(array_in=user, key='passwordChangeRequired', pre="FusionAuth.user")
            app.logger.info(f"Session: {session}")
            return redirect(url_for('logged_in'))
        else:
            app.logger.info(f"Unsuccessful login: {response.error_response}")
    return render_template("public/login.html", login_uri="/login")


@app.route("/logged_in")
def logged_in():
    uri = url_for('logout')
    return render_template(
        "public/logged_in.html",
        uri=uri,
        user_id=session["FusionAuth.user.id"],
        email=session["FusionAuth.user.email"],
        created_at=session["FusionAuth.user.insertInstant"],
        updated_at=session["FusionAuth.user.lastUpdateInstant"],
        last_login=session["FusionAuth.user.lastLoginInstant"],
        pwd_updated_at=session["FusionAuth.user.passwordLastUpdateInstant"],
        pwd_change=session["FusionAuth.user.passwordChangeRequired"]
    )


@app.route("/logout")
def logout():
    # Remove all session variables
    session.clear()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True, host="0.0.0.0")

