from faker import Faker
from flask import Flask
from random import randint
from zappa.async import task

from graphql import create_customer_on_shopify, create_order_for_customer_on_shopify

app = Flask(__name__)

@task
@app.route("/create_customer")
def create_customer(access_token, store_url, customer_count=20):
    print("creating {} customers for {}".format(customer_count, store_url))

    fake = Faker()

    new_customer_data = {"email": fake.email(),
                         "firstName": fake.first_name(),
                         "lastName": fake.last_name()}

    new_customer = create_customer_on_shopify(access_token, store_url, data=new_customer_data)

    order_count = randint(0, 4)
    for order_idx in xrange(order_count):
        create_order_for_customer_on_shopify(new_customer["id"])

    print("done!")

@app.route("/")
def index():
    create_customer("39da5abe709be02c08da67663398ce91", "whydontyoujust.myshopify.com")
    return "Hello World!"
