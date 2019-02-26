import requests

from faker import Faker

def _make_request(access_token, store_url, query):
    headers = {"X-Shopify-Access-Token": access_token,
               "Content-Type": "application/graphql"}


    response = requests.post("https://{}/admin/api/graphql.json".format(store_url),
                             headers=headers,
                             data=query)

    response.raise_for_status()
    import pdb;pdb.set_trace()
    print("query to shopify complete. throttle info: {}".format(response.json()["extensions"]["cost"]))

    return response.json()

def create_customer_on_shopify(access_token, store_url):
    # TODO: for my uses all I need is the email, but this could be expanded to have more

    faker = Faker()

    full_query = "".join(["mutation {",
                         "customerCreate(input: {{email: \"{}\"}}) {{".format(faker.email()),
                         "customer { email }",
                         "userErrors { field message } }}"])

    customer = _make_request(access_token, store_url, full_query)

    return customer

def create_order_for_customer_on_shopify(access_token, store_url, customer_obj):
    import pdb; pdb.set_trace()
    full_query = "".join(["mutation {",
                         "checkoutCreate(input: {{email: \"{}\", lineItems: [{{quantity: 1, variantId: 32146881610}}]}}) {{".format(customer_obj["email"]),
                         "checkout { id }",
                         "userErrors { field message } }}"])

    order = _make_request(access_token, store_url, full_query)
