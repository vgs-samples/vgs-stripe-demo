# Description
[VGS Collect.js](https://www.verygoodsecurity.com/collect/collectjs) powered by [VGS](https://www.verygoodsecurity.com) and Stripe 3D Secure (3DS) flow demo application. This is [SCA](https://en.wikipedia.org/wiki/Strong_customer_authentication)-ready integration. To use it you must have VGS and Stripe accounts created and configured. Follow the  instructions below.

You can run it locally with doker-compose (see below) or deploy to heroku in one click.

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

# VGS Dashboard configurations
> **Note! You MUST have VGS inbound/outbound routes configured**

To configure your VGS routes:

1. Signup or login to [VGS Dashboard](http://dashboard.verygoodsecurity.com)
2. Create routes by importing from YAML. The repo includes a directory called [routes](https://github.com/verygoodsecurity/vgs-stripe-demo/tree/master/routes) that contain templates of the inbound and outbound routes in YAML format needed by the app to successfully redact the credit card data before hit server.py and then reveal it when it send to Stripe API.
3. Change your inbound route `Upstream Host` to your public URL (your heroku or ngrok url)

# Configure Stripe Radar
- Go to [Stripe dashboard](https://dashboard.stripe.com/dashboard) and get your secret key.
- Add this two rules to stripe radar to force 3d secure auth when the card support 
it but does not require it

![](stripe-rules.png)


# Running locally with docker-compose

- Create a .env file in the project root directory using this template

```.env
STRIPE_KEY=
VGS_PROXY=
PUBLIC_URL=
VGS_COLLECT_LIBRARY_URL=
VAULT_ID=
```

where 

* `STRIPE_KEY`: Stripe Secret API Key (Stripe dashboard -> Developers -> API keys) 
* `VGS_PROXY`: full URL with credentials for the VGS outbound proxy, `https://USERNAME:PASSWORD@<vault_id>.SANDBOX.verygoodproxy.com:8080`
* `VGS_PROXY_CERTIFICATE_B64`: VGS proxy certificate encoded as a base64 string. **Optional** field, if no - default VGS Sandbox certificate used. 
* `PUBLIC_URL`: The public URL of the server without `/` at the end, `https://<some_id>.ngrok.io` (see below how to get it)
* `VGS_COLLECT_LIBRARY_URL`: https://dashboard.verygoodsecurity.com -> VGS Collect page
* `VAULT_ID`: https://dashboard.verygoodsecurity.com -> Settings -> Identifier

After the `.env` file is create run the app with `docker-compose up -d stripe-demo`
You can force the docker container to rebuild it self with  `docker-compose up -d --build stripe-demo`

- Run [ngrok](https://ngrok.com/)

```
ngrok http 3000
```

- Copy provided address:
```
https://<some_id>.ngrok.io
```

# Check your test payments
- Open Stripe Payments to see your payments info
- Open Stripe logs (`Developers` tab -> `Logs`) to see your request


## Useful links
- [VGS Collect.js docs](https://www.verygoodsecurity.com/docs/vgs-collect/index)
- [Stripe radar 3DS rules docs](https://stripe.com/docs/radar/rules#request-3ds)
