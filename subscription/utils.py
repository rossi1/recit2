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

def subscribe_stripe_plan(customer_id, plan_id, switch=False):
        if not switch:
                return stripe.Subscription.create(
                        customer=customer_id,
                        items=[{"plan": plan_id}],
                        trial_period_days=30)
        else:
                return stripe.Subscription.create(
                        customer=customer_id,
                        items=[{"plan": plan_id}])
    

def upgrade_and_downgrade_stripe_plan(subscription_id, plan_id):
        subscription = stripe.Subscription.modify(subscription_id,
        cancel_at_period_end=False,
        items=[{'id': subscription['items']['data'][0].id,'plan': plan_id,
        }])
        return subscription



def disabled_sub_switch():
    today_date = date.today()
    disable_sub_switch_date = today_date + relativedelta(days=+1)
    return disable_sub_switch_date