import shopify
import json
import os

from flask import Flask, redirect, url_for, render_template, request, session
from flask_login import LoginManager, login_required, login_user, current_user, UserMixin
from random import randint
from zappa.async import task
from wtforms import Form, StringField, validators

from graphql import create_customer_on_shopify, create_order_for_customer_on_shopify

app = Flask(__name__)
app.secret_key = "change me"
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, token, store_url, storefront_token):
        # gross but i dont care here
        # if you want to make this not gross, set up proper user objects
        self.id = json.dumps({"token": token, "store_url": store_url, "storefront_token": storefront_token})
        self.token = token
        self.store_url = store_url
        self.storefront_token = storefront_token

@login_manager.user_loader
def user_loader(id):
    return User(**json.loads(id))

@task
@app.route("/create_customer")
def create_customer(access_token, store_url):
    print("creating customers for {}".format(store_url))

    new_customer = create_customer_on_shopify(access_token, store_url)
    if new_customer["data"]["customerCreate"]["customer"]:
        new_customer = new_customer["data"]["customerCreate"]["customer"]

    order_count = randint(0, 4)
    for order_idx in range(order_count):
        create_order_for_customer_on_shopify(access_token, store_url, new_customer)

    print("done!")

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

@app.route("/oauth_callback")
def oauth_callback():
    shopify.Session.setup(api_key=os.environ.get("API_KEY"), secret=os.environ.get("SHARED_SECRET"))
    shopify_session = shopify.Session(request.args['shop'])

    token = shopify_session.request_token(request.args)
    with shopify.Session.temp(request.args['shop'], token):
        storefront_token = shopify.StorefrontAccessToken.create({"title": "0xDEADBEEF"})
    u = User(token=token, store_url=request.args['shop'], storefront_token=storefront_token.access_token)
    login_user(u)

    return redirect(url_for("index"))

@app.route("/login", methods=["GET", "POST"])
def login():
    class ShopifyShopForm(Form):
        store_name = StringField('shopify_store_name', [validators.Length(min=4, max=1024)])
    
    form = ShopifyShopForm(request.form)

    if form.validate():
        shopify.Session.setup(api_key=os.environ.get("API_KEY"), secret=os.environ.get("SHARED_SECRET"))
        shopify_session = shopify.Session(request.form['store_name'])

        scope=["write_customers", "unauthenticated_write_checkouts"]
        return redirect(shopify_session.create_permission_url(scope, url_for("oauth_callback", _external=True, _scheme=app.config.get("PREFERRED_URL_SCHEME"))))

    return render_template("shop_login.html")

@app.route("/")
@login_required
def index():
    for idx in range(10):
        # zappa will make this run async in lambdas <3
        create_order_for_customer_on_shopify(current_user.storefront_token, current_user.store_url)

    return "Hello World!"
