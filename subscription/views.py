from enum import Enum
import datetime
from datetime import date

import stripe
from dateutil.relativedelta import *



from django.conf import settings

from rest_framework.response import Response
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework import status
from rest_framework.validators import ValidationError
from rest_framework.views import APIView


from .models  import SubscriptionPlan

stripe.api_key = 'sk_test_wkwaWE7YeaKbYZd5Yz5dpbrF'




class BusinessAccountType(Enum):
    service_provider = 'Service Provider'
    product_seller = 'Product Seller'

class SubscriptionPlanModel(Enum):
    freelance_plan = 'freelance_plan'
    business_plan = 'business_plan'
    freemium_plan = 'freemium_plan'


class CreateSubscriptionPlan(APIView):
    permission_classes = (IsAuthenticated,)


    def post(self, request, **kwargs):
        fetch_plan = request.query_params.get('sub_plan',  None)
        tx_code = request.query_params.get('tf_code',  None)
        if fetch_plan is not None:
            create_customer = self.create_customer(tx_code)
            if fetch_plan ==  SubscriptionPlanModel.freelance_plan.value:

                self.update_user_plan_to_freelancing(create_customer)
                return Response(data={'status': 'success'}, status=status.HTTP_200_OK)
        
               
            elif fetch_plan == SubscriptionPlanModel.business_plan.value:
                self.update_user_plan_to_business(create_customer)
                return Response(data={'status': 'success'}, status=status.HTTP_200_OK)

            else:
                self.update_user_plan_to_freemium(create_customer)
                return Response(data={'status': 'success'}, status=status.HTTP_200_OK)

               
                
        return  Response('Failed to get plan')

    def create_customer(self, token):
        create = stripe.Customer.create(
            email=self.request.user.email,
            source=token)
        return create

    def update_user_plan_to_freelancing(self, customer_id):
        subscribe_plan = self.subscribe_plan(customer_id.id, getattr(settings, 'FREELANCE_PLAN_ID'))
        sub_start_date = datetime.datetime.utcfromtimestamp(subscribe_plan['current_period_start'])
        sub_end_date = datetime.datetime.utcfromtimestamp(subscribe_plan['current_period_end'])
        subscription_type = SubscriptionPlanModel.freelance_plan.value
        return SubscriptionPlan.objects.create(plan_id=self.request.user, subscription_type=subscription_type,
        subscription_start_date=sub_start_date.date(), subscription_end_date=sub_end_date.date(),
        customer_card_id=customer_id, subscription_id=subscribe_plan['id'])

    @staticmethod
    def subscribe_plan(customer_id, plan_id):
        return stripe.Subscription.create(
            customer=customer_id,
            items=[{"plan": plan_id}])
     
       
    def update_user_plan_to_business(self, customer_id):
        subscribe_plan = self.subscribe_plan(customer_id.id, getattr(settings, 'BUSINESS_PLAN_ID'))
        sub_start_date = datetime.datetime.utcfromtimestamp(subscribe_plan['current_period_start'])
        sub_end_date = datetime.datetime.utcfromtimestamp(subscribe_plan['current_period_end'])
        subscription_type = SubscriptionPlanModel.business_plan.value
        return SubscriptionPlan.objects.create(plan_id=self.request.user, subscription_type=subscription_type, 
        subscription_start_date=sub_start_date.date(), subscription_end_date=sub_end_date.date(),
        customer_card_id=customer_id, subscription_id=subscribe_plan['id'])

    def update_user_plan_to_freemium(self, customer_id):
        subscribe_plan = self.subscribe_plan(customer_id.id, getattr(settings, 'FREEMIUM_PLAN_ID'))
        sub_start_date = datetime.datetime.utcfromtimestamp(subscribe_plan['current_period_start'])
        sub_end_date = datetime.datetime.utcfromtimestamp(subscribe_plan['current_period_end'])
        subscription_type = SubscriptionPlanModel.freemium_plan.value
        return SubscriptionPlan.objects.create(plan_id=self.request.user, subscription_type=subscription_type,
        subscription_start_date=sub_start_date.date(), subscription_end_date=sub_end_date.date(),
        customer_card_id=customer_id, subscription_id=subscribe_plan['id'])

       
    
        
    @staticmethod
    def trial_end_date():
        today_date = date.today()
        trial_end_date = today_date + relativedelta(months=+1)
        return trial_end_date
        

    
