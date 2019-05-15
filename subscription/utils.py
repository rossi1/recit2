import stripe

stripe.api_key = 'sk_test_wkwaWE7YeaKbYZd5Yz5dpbrF'



def subscribe_plan(customer_id, plan_id):
    return stripe.Subscription.create(
        customer=customer_id,
        items=[{"plan": plan_id}])