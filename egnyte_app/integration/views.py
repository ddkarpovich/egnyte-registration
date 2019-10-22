import requests

from flask import render_template, redirect, request, url_for, flash
from flask_login import current_user, login_required

from egnyte_app.app import app
from egnyte_app.integration import config
from egnyte_app.integration.exceptions import TokenExchangeFailed
from egnyte_app.integration.service import (
    get_authorize_url, exchange_code, get_user_info
)


def create_saas_customer(access_token: str):
    # Create SaaS customer by making a call to the REST API
    url = f'http://{config.EGNYTE_SAAS_REST_HOST}/customer/{current_user.id}/operation'

    data = {
        'token': {
            'access_token': access_token
        },
        'farm': 'web'
    }

    try:
        response = requests.post(url, json=data)
        data = response.json()
        if data.get('message'):
            flash(data['message'])
        else:
            flash(f'Something went wrong while tried to create customer - {data}')
    except requests.exceptions.ConnectionError:
        flash('Could not connect to SaaS REST - Connection Error')

    return redirect(url_for('home'))


def status_saas_customer():
    url = f'http://{config.EGNYTE_SAAS_REST_HOST}/customer/{current_user.id}/operation'
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        return {}

    return response.json()


@app.route('/stop')
@login_required
def stop_saas_customer():
    # Stop SaaS customer by making a call to the REST API
    url = f'http://{config.EGNYTE_SAAS_REST_HOST}/customer/{current_user.id}/operation/stop'

    try:
        response = requests.put(url)
        data = response.json()
        if data.get('message'):
            flash(data['message'])
        else:
            flash('fSomething went wrong while tried to stop customer - {data}')
    except ValueError:#requests.exceptions.ConnectionError:
        flash('Could not connect to SaaS REST - Connection Error')

    return redirect(url_for('home'))


@app.route('/start')
@login_required
def start_saas_customer():
    # Start SaaS customer by making a call to the REST API
    url = f'http://{config.EGNYTE_SAAS_REST_HOST}/customer/{current_user.id}/operation/start'

    try:
        response = requests.put(url)
        data = response.json()
        if data.get('message'):
            flash(data['message'])
        else:
            flash('fSomething went wrong while tried to start customer - {data}')
    except requests.exceptions.ConnectionError:
        flash('Could not connect to SaaS REST - Connection Error')

    return redirect(url_for('home'))


@app.route('/delete')
@login_required
def delete_saas_customer():
    # Delete SaaS customer by making a call to the REST API
    url = f'http://{config.EGNYTE_SAAS_REST_HOST}/customer/{current_user.id}/operation'

    try:
        response = requests.delete(url)
        if response.status_code == 204:
            flash('Customer has been removed')
        else:
            flash(f'Something went wrong while tried to delete customer - {response.json()}')
    except requests.exceptions.ConnectionError:
        flash('Could not connect to SaaS REST - Connection Error')

    return redirect(url_for('home'))


@app.route('/')
def home():
    # Check customer integration status
    context = {
        'status': status_saas_customer() if current_user.is_authenticated else {}
    }
    return render_template('home.html', **context)


@app.route('/authorize')
@login_required
def egnyte_app_authorize():
    authorize_url = get_authorize_url()
    return redirect(authorize_url)


@app.route('/return')
@login_required
def egnyte_app_return():
    data = request.args
    error = data.get('error')
    if error:
        if error == 'access_denied':
            flash('You should accept our app to proceed with integration')
        else:
            flash(f'An error occured while processing integration - {error}')
        return redirect(url_for('home'))

    try:
        # Exchange OAuth code for a access token
        access_token, expires_in = exchange_code(data.get('code'))
    except TokenExchangeFailed:
        flash('Something went wrong during Egnyte authorization - unable to exchange token')
        return redirect(url_for('home'))

    user = get_user_info(access_token)
    if user.get('user_type') != 'admin':
        flash(f'Can not process Egnyte integration - admin user type is required.')
        return redirect(url_for('home'))

    flash('Egnyte integration successfully finished - token exchanged')

    # Create new SaaS customer
    create_saas_customer(access_token)

    return redirect(url_for('home'))
