# settings.py
import base64
import logging
import os
import tempfile

import stripe
import ulid
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from stripe.error import StripeError

logging.basicConfig(level=logging.DEBUG)

load_dotenv()
app = Flask(__name__,
            static_url_path='',
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "public"),
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "public"))
CORS(app)
Transactions = {}


@app.route('/', methods=['GET'])
@app.route('/credit-card.html', methods=['GET'])
def credit_card():
    return render_template('credit-card.html', VGS_COLLECT_LIBRARY_URL=os.getenv('VGS_COLLECT_LIBRARY_URL'));

@app.route('/js/credit-card-example.js', methods=['GET'])
def credit_card_form():
    return render_template('js/credit-card-example.js', VAULT_ID=os.getenv('VAULT_ID'));

@app.route('/transaction_info', methods=['GET'])
def get():
    transaction_id = request.args.get('transaction_id')

    if transaction_id not in Transactions:
        return {'kind': 'not_found'}, 404

    if 'payment_intent' not in Transactions[transaction_id]:
        return {'kind': 'not_found'}, 404

    payment_intent_id = Transactions[transaction_id]['payment_intent']
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    except StripeError as e:
        return jsonify({'kind': 'error', 'message': e.user_message}), 400

    return jsonify({'kind': 'payment_intent', 'status': payment_intent['status'],
                    'cancellation_reason': payment_intent['cancellation_reason']}), 200


@app.route('/post', methods=['POST'])
def post():
    # create transaction
    transaction_id = ulid.new().str
    Transactions[transaction_id] = {}

    # create card on stripe
    # in this stage the data is redacted and it will be revealed through the vgs proxy
    # that is configured in the __main__ function
    exp_month, exp_year = request.json['cardExpirationDate'].split('/')
    card = {
        'number': request.json['cardNumber'],
        'name': request.json['cardName'],
        'exp_month': int(exp_month.strip()),
        'exp_year': int(exp_year.strip()),
        'cvc': request.json['cardCvc'],
    }

    try:
        token_response = stripe.Token.create(card=card)
    except StripeError as e:
        return jsonify({'kind': 'error', 'message': e.user_message}), 400

    # create a costumer for this transaction, required by the payment intent stripe api
    try:
        customer_response = stripe.Customer.create(
            description=f'Customer for transaction {transaction_id}',
            source=token_response['id']  # obtained with Stripe.js
        )
    except StripeError as e:
        return jsonify({'kind': 'error', 'message': e.user_message}), 400

    # create payment intent
    try:
        pi_response = stripe.PaymentIntent.create(
            amount=request.json['amount'],
            currency='usd',
            payment_method=token_response['card']['id'],  # obtained with Stripe.js
            customer=customer_response['id'],
        )
    except StripeError as e:
        return jsonify({'kind': 'error', 'message': e.user_message}), 400

    # save payment intent id locally
    Transactions[transaction_id]['payment_intent'] = pi_response['id']

    # confirm intent and tell to stripe to redirect the user to a custom url after the 3ds flow ends
    try:
        intent_response = stripe.PaymentIntent.confirm(
            pi_response['id'],
            return_url=f'{os.environ.get("PUBLIC_URL")}/confirm_3ds.html?transaction_id={transaction_id}'
        )
    except StripeError as e:
        return jsonify({'kind': 'error', 'message': e.user_message}), 400

    # transaction does success and does not support 3d secure
    if not intent_response['next_action']:
        return jsonify({'kind': 'transaction_succeeded_without_3ds', 'transaction_id': transaction_id}), 200
    else:
        return jsonify(
            {'kind': 'action_redirect',
             'redirect_url': intent_response['next_action']['redirect_to_url']['url']}), 200


if not os.getenv('STRIPE_KEY'):
    raise Exception('STRIPE_KEY is missing')
if not os.getenv('VGS_PROXY'):
    raise Exception('VGS_PROXY is missing')
if not os.getenv('PUBLIC_URL'):
    raise Exception('PUBLIC_URL is missing')
if not os.getenv('VGS_COLLECT_LIBRARY_URL'):
    raise Exception('VGS_COLLECT_LIBRARY_URL is missing')
if not os.getenv('VAULT_ID'):
    raise Exception('VAULT_ID is missing')

fd, cert_path = tempfile.mkstemp()

try:
    with os.fdopen(fd, 'w') as tmp:
        # do stuff with temp file
        tmp.write(base64.b64decode(os.getenv('VGS_PROXY_CERTIFICATE_B64','LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUQyVENDQXNHZ0F3SUJBZ0lIQU40R3MvTEdoekFOQmdrcWhraUc5dzBCQVEwRkFEQjVNU1F3SWdZRFZRUUQKREJzcUxuTmhibVJpYjNndWRtVnllV2R2YjJSd2NtOTRlUzVqYjIweElUQWZCZ05WQkFvTUdGWmxjbmtnUjI5dgpaQ0JUWldOMWNtbDBlU3dnU1c1akxqRXVNQ3dHQTFVRUN3d2xWbVZ5ZVNCSGIyOWtJRk5sWTNWeWFYUjVJQzBnClJXNW5hVzVsWlhKcGJtY2dWR1ZoYlRBZ0Z3MHhOakF5TURreU16VXpNelphR0E4eU1URTNNREV4TlRJek5UTXoKTmxvd2VURWtNQ0lHQTFVRUF3d2JLaTV6WVc1a1ltOTRMblpsY25sbmIyOWtjSEp2ZUhrdVkyOXRNU0V3SHdZRApWUVFLREJoV1pYSjVJRWR2YjJRZ1UyVmpkWEpwZEhrc0lFbHVZeTR4TGpBc0JnTlZCQXNNSlZabGNua2dSMjl2ClpDQlRaV04xY21sMGVTQXRJRVZ1WjJsdVpXVnlhVzVuSUZSbFlXMHdnZ0VpTUEwR0NTcUdTSWIzRFFFQkFRVUEKQTRJQkR3QXdnZ0VLQW9JQkFRREkzdWtIcHhJbERDdkZqcHFuNGdBa3JRVmRXbGwvdUkwS3Yzd2lyd1ozUXJwZwpCVmVYakluSityVjlyMG91QklvWThJZ1JMYWs1SHkvdFNlVjZuQVZIdjB0NDFCN1Z5b2VUQXNaWVNXVTExZGVSCkRCU0JYSFdIOXpLRXZYa2tQZHk5dGdIbnZMSXp1aTJINTlPUGxqVjd6M3NDTGd1Ukl2SUl3OGRqYVY5ejdGUm0KS1JzZm1ZSEtPQmxTTzRUbHBmWFFnN2pRNWRzNjVxOEZGR3ZUQjVxQWdMWFM4VzhwdmRrOGpjY211elFYRlVZKwpadEhnalRoZzdCSFdXVW4rN202aFE2aUhIQ2ozNFF1NjlGOG5MYW1kK0tKLy8xNGx1a2R5S3MzQU1yWXNGYWJ5CmsrVUdlbU0vczJxM0IrMzlCNllLYUhhbzBTUnpTSkM3cUR3YldQeTNBZ01CQUFHalpEQmlNQjBHQTFVZERnUVcKQkJSV2xJUnJFMnAyUDAxOFZUelRiNkJhZU9GaEF6QVBCZ05WSFJNQkFmOEVCVEFEQVFIL01Bc0dBMVVkRHdRRQpBd0lCdGpBakJnTlZIU1VFSERBYUJnZ3JCZ0VGQlFjREFRWUlLd1lCQlFVSEF3SUdCRlVkSlFBd0RRWUpLb1pJCmh2Y05BUUVOQlFBRGdnRUJBR1d4TEZscjBiOWxXa09MY1p0UjlJRFZ4REw5eitVUEZFazcwRDNOUGFxWGtvRS8KVE5OVWtYZ1M2K1ZCQTJHOG5pZ3EyWWo4cW9JTStrVFhQYjhUeld2K2xyY0xtK2krNEFTaEtWa25wQjE1Y0MxQwovTkpmeVlHUlc2NnMvdzdITlMyMFJtcmROK2JXUzBQQTRDVkxYZEd6VUpuMFBDc2ZzUys2QWNuN1JQQUUrMEE4CldCN0p6WFdpOHg5bU9Kd2lPaG9kcDRqNDFtdis1ZUhNMHJlTWg2eWN1WWJqcXVETnBpTm5zTHp0azZNR3NnQVAKNUM1OWRyUVdKVTQ3NzM4QmNmYkJ5dVNUWUZvZzZ6TllDbTdBQ3FidGl3dkZUd2puZU5lYk9oc09sYUVBSGp1cApkNFFCcVlWczdwemtoTk5wOW9VdnY0d0dmL0tKY3c1QjlFNlRwZms9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0=')).decode('utf8'))
    # configure stripe
    stripe.api_key = os.getenv('STRIPE_KEY')
    stripe.proxy = os.getenv('VGS_PROXY')
    stripe.ca_bundle_path = cert_path
    stripe.default_http_client = stripe.http_client.RequestsClient(
        verify_ssl_certs=stripe.verify_ssl_certs,
        proxy=stripe.proxy
    )
finally:
    print(cert_path)

if __name__ == '__main__':
    app.run(port=3000, host='0.0.0.0', debug=True)
