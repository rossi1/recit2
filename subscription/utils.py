import stripe
from datetime import timedelta, datetime, date
from datetime import datetime, timedelta, timezone

from dateutil.relativedelta import *

stripe.api_key = 'sk_test_wkwaWE7YeaKbYZd5Yz5dpbrF'

def convert_datetime_to_unix_timestamp():
        d = timedelta(days=30)
        dt = datetime.today()
        timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
        return timestamp

def subscribe_stripe_plan(customer_id, plan_id):
    return stripe.Subscription.create(
        customer=customer_id,
        items=[{"plan": plan_id}],
        trial_period_days=30)



def extend_subscription_date():
    today_date = date.today()
    sub_expiry_date = today_date + relativedelta(months=+1)
    return sub_expiry_date