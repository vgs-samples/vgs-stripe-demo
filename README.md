# Description
VGS Collect.js and Stripe 3D Secure flow demo application. To use it you must have VGS and Stripe accounts created and configured. Follow instructions below.

You can run it locally with doker-compose (see below) or deploy to heroku in one click.

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

# VGS Dashboard configurations
> **Note! You MUST have VGS inbound/outbound routes configured**

To configure your VGS routes:

1. Signup or login to [VGS Dashboard](http://dashboard.verygoodsecurity.com)
2. Create routes by importing from YAML. The repo includes a directory called [routes](https://github.com/verygoodsecurity/vgs-stripe-demo/tree/master/routes) that contain templates of the inbound and outbound routes in YAML format needed by the app to successfully redact the credit card data before hit server.py and then reveal it when it send to Stripe API.
3. Change your inbound route `Destination URL` to your public URL

# Configure Stripe Radar

* add this two rules to stripe radar to force 3d secure auth when the card support 
it but does not require it

![](stripe-rules.png)


# Running locally with docker-compose

- create a .env file in the project root directory using this template

```.env
STRIPE_KEY=
VGS_PROXY=
PUBLIC_URL=
VGS_COLLECT_LIBRARY_URL=
VAULT_ID=
```

where 

* `STRIPE_KEY`: Stripe Secret API Key  
* `VGS_PROXY`: full URL with credentials for the VGS outbound proxy, `https://USERNAME:PASSWORD@<vault_id>.SANDBOX.verygoodproxy.com:8080`
* `VGS_PROXY_CERTIFICATE_B64`: VGS proxy certificate encoded as a base64 string. **Optional** field, if no - default VGS Sandbox certificate used. 
* `PUBLIC_URL`: The public URL of the server without `/` at the end, `https://{app-name}.herokuapp.com`
* `VGS_COLLECT_LIBRARY_URL`: https://dashboard.verygoodsecurity.com -> VGS Collect page
* `VAULT_ID`: https://dashboard.verygoodsecurity.com -> Settings -> Identifier


after the `.env` file is create run the app with `docker-compose up -d stripe-demo`

you can force the docker container to rebuild it self with  docker-compose up -d --build stripe-demo


## Useful links
- [VGS Collect.js docs](https://www.verygoodsecurity.com/docs/vgs-collect/index)
- [Stripe radar 3DS rules docs](https://stripe.com/docs/radar/rules#request-3ds)
