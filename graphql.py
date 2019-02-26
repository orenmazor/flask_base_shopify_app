import requests

from faker import Faker

def _make_request(access_token, store_url, query):
    headers = {"X-Shopify-Storefront-Access-Token": access_token,
               "Content-Type": "application/graphql"}


    response = requests.post("https://{}/api/graphql.json".format(store_url),
                             headers=headers,
                             data=query)

    response.raise_for_status()

    # its interesting that when you call the storefront api checkouts, the extensions dont exist
    if "extensions" in response.json():
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

def create_order_for_customer_on_shopify(storefront_access_token, store_url):
    full_query = "".join(["mutation {",
        "checkoutCreate(input: {email: \"oren.mazor@gmail.com\", lineItems: [{quantity: 1, variantId: \"Z2lkOi8vc2hvcGlmeS9Qcm9kdWN0VmFyaWFudC8xOTQ2MDg3MjkyOTMzNg==\"}], shippingAddress: {address1: \"150 Elgin Street\", zip: \"K2P 1L4\", city: \"ottawa\", province: \"on\", country: \"Canada\", lastName: \"Lutke\", firstName: \"Tobi\"}}) {",
                          "checkout { id webUrl }",
                          "userErrors { field message }",
                          "}}"])

    checkout = _make_request(storefront_access_token, store_url, full_query)
    # TODO: if the result is a 202, then polling is required because the checkout is
    # possibly recalculating taxes and shipping rates
    # TODO2: if the result is a 303 then there is checkout throttling in place
    # then we need to poll until the throttle is resolved
    checkout_gid = checkout['data']['checkoutCreate']['checkout']['id']

    # if your app permissions have payment processing permissions, you can actually complete with credit cards
    # i have no such permissions, so i test with free checkouts
    full_query = "".join(["mutation {",
                          "checkoutCompleteFree(checkoutId: \"{}\") {{".format(checkout_gid),
                          "checkout { id }",
                          "checkoutUserErrors { message field code }}}"])

    complete_checkout = _make_request(storefront_access_token, store_url, full_query)

# you need payment permissions for this to work
    # mutation {
	#     checkoutCompleteWithCreditCardV2(checkoutId: "Z2lkOi8vc2hvcGlmeS9DaGVja291dC82MzVjMDcxYjkyZDk2NWI4ZGE5NzU4NjhiMjY5N2MxZD9rZXk9YzQxZWUwZTU0Y2Q2MThkZDQzMGMxOTdjMTY3NzU2Y2Q=", payment: {paymentAmount: {amount: 1337, currencyCode: CAD}, idempotencyKey: "abcdef", billingAddress: {}, vaultId: "abcdef"}) {
	# 	checkout {
	# 	    id
	# 	    }
	# 	checkoutUserErrors {
	# 	    message
	# 	    field
	# 	    code
	# 	    }
	# 	}
	#     }
