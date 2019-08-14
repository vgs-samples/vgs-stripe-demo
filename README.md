# vgs-stripe-demo
VGS Collect.js and Stripe 3D Secure flow demo application


# configure stripe radar

* add this two rules to stripe radar to force 3d secure auth when the card support 
it but does not require it

![](stripe-rules.png)

# vgs inbound/outbound rules

the repo includes a directory called `routes` that contain a template of the inbound and outbound rules on yaml format 
needed by the app to successful redact the credit card data before hit server.py and then reveal it when it send to stripe backend

# Running with docker-compose

- create a .env file in the project root directory using this template

```.env
STRIPE_KEY=
VGS_PROXY=
VGS_PROXY_CERTIFICATE_B64=
PUBLIC_URL=
VGS_COLLECT_LIBRARY_URL=
VAULT_ID=
```

where 

* `STRIPE_KEY`: is the stripe access token  
* `VGS_PROXY`: is the full url with credential of the vgs proxy returned by the dashboard 
* `VGS_PROXY_CERTIFICATE_B64`: the proxy certificate encode in a  base64 long string
* `PUBLIC_URL`: the public url of the server without `/` at the end, the same url used in the inbound rule
* `VGS_COLLECT_LIBRARY_URL`: vgs dashboard>VGS Collect
* `VAULT_ID`: vgs dashboard>settings>Identifier


after the `.env` file is create run the app with `docker-compose up -d stripe-demo`

you can force the docker container to rebuild it self with  docker-compose up -d --build stripe-demo



# on heroku

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)
