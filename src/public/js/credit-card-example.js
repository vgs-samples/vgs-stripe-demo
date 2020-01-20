const f = VGSCollect.create('{{VAULT_ID}}', '{{VGS_COLLECT_ENV}}', function (state) {
});

const field = f.field('#cc-name .form-control', {
    type: 'text',
    name: 'cardName',
    placeholder: 'Joe Business',
    validations: ['required'],
});

f.field('#amount .form-control', {
    type: 'number',
    name: 'amount',
    successColor: '#4F8A10',
    errorColor: '#D8000C',
    defaultValue: urlParams['amount'] || 100,
});

f.field('#cc-number .form-control', {
    type: 'card-number',
    name: 'cardNumber',
    successColor: '#4F8A10',
    errorColor: '#D8000C',
    placeholder: '4111 1111 1111 1111',
    validations: ['required', 'validCardNumber'],
});

f.field('#cc-cvc .form-control', {
    type: 'card-security-code',
    name: 'cardCvc',
    placeholder: '344',
    validations: ['required', 'validCardSecurityCode'],
});

f.field('#cc-expiration-date .form-control', {
    type: 'card-expiration-date',
    name: 'cardExpirationDate',
    placeholder: '01 / 2022',
    validations: ['required', 'validCardExpirationDate']
});

setTimeout(() => field.focus(), 1000);

document.getElementById('cc-form')
    .addEventListener('submit', function (e) {
        const targetForm = e.target;
        e.preventDefault();
        const form_error = $("#form-error");
        let valid_form = true;
        const keys = Object.keys(f.state);
        for (let key = 0; key < keys.length; key++) {
            valid_form = valid_form && f.state[keys[key]].isValid;
        }
        if (!valid_form) {
            return
        }
        form_error.text("");
        form_error.hide();
        $('#purchase-btn').prepend('<span id="purchase-loader" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
        $('#purchase-btn').prop('disabled', true);

        //submit and send the amount of the transaction
        f.submit('/post', {}, function (status, data) {
            $('#purchase-loader').remove();
            $('#purchase-btn').prop('disabled', false);
            if (data && data.kind) {
                if (data.kind === "transaction_succeeded_without_3ds") {
                    //close modal
                    parent.postMessage({kind: "close-modal", data: {kind: "transaction_succeeded_without_3ds"}}, "*");
                    window.location.replace('/confirm_3ds.html?transaction_succeeded_without_3ds=true&transaction_id=' + data.transaction_id);

                } else if (data.kind === "action_redirect") {
                    //close modal
                    window.location.replace(data.redirect_url);
                } else if (data.kind === "error") {
                    form_error.text(data.message);
                    form_error.show();
                }
            }
            cleanErrorMessages(targetForm);
        }, function (errors) {
            highlightErrors(targetForm, errors);
        });
    }, false);
