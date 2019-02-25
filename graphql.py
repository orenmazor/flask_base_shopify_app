import requests

def _make_request(access_token, store_url, query):
    headers = {"X-Shopify-Access-Token": access_token,
               "Content-Type": "application/graphql"}


    response = requests.post("https://{}/admin/api/graphql.json".format(store_url),
                             headers=headers,
                             data=query)

    import pdb; pdb.set_trace()
    response.raise_for_status()

    return response.json()

def create_customer_on_shopify(access_token, store_url, data):
    full_query = "".join(["mutation {",
                         "customerCreate(input: {{email: \"{}\"}}) {{".format("asdf@google.com"),
                         "customer { id email }",
                         "userErrors { field message } }}"])

    customer = _make_request(access_token, store_url, full_query)

    return customer

def create_order_for_customer_on_shopify(id, access_token, store_url, data):
    order = _make_request(access_token, store_url, data)

    import pdb; pdb.set_trace()
    pass
