from enum import Enum
from datetime import date


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




class BusinessAccountType(Enum):
    service_provider = 'Service Provider'
    product_seller = 'Product Seller'

class SubscriptionPlanModel(Enum):
    freelance_plan = 'freelance_plan'
    business_plan = 'business_plan'
    freemium_plan = 'freemium_plan'


class CreateSubscriptionPlan(APIView):
    permission_classes = (IsAuthenticated,)


    def post(self, **kwargs):
        fetch_plan = self.request.query_params.get('sub_plan',  None)
        tx_code = self.request.query_params.get('tf_code',  None)
        if fetch_plan is not None:
            if fetch_plan ==  SubscriptionPlanModel.freelance_plan.value:
                self.update_user_plan_to_freelancing(tx_code)
                return Response(data={'status': 'success'}, status=status.HTTP_200_OK)
        
               
            elif fetch_plan == SubscriptionPlanModel.business_plan.value:
                self.update_user_plan_to_business(tx_code)
                return Response(data={'status': 'success'}, status=status.HTTP_200_OK)

            else:
                self.update_user_plan_to_freemium()
                return Response(data={'status': 'success'}, status=status.HTTP_200_OK)

               
                
        raise ValidationError('Failed to get plan')

    def update_user_plan_to_freelancing(self, customer_id):
        subscription_type = SubscriptionPlanModel.freelance_plan.value
        return SubscriptionPlan.objects.create(plan_id=self.request.user, subscription_type=subscription_type, trial_end_date=self.trial_end_date(), 
        is_trial=True, customer_card_id=customer_id)
     
       
    def update_user_plan_to_business(self, customer_id):
        subscription_type = SubscriptionPlanModel.business_plan.value
        return SubscriptionPlan.objects.create(plan_id=self.request.user, subscription_type=subscription_type, 
        trial_end_date=self.trial_end_date(), is_trial=True, customer_card_id=customer_id)

    def update_user_plan_to_freemium(self):
        subscription_type = SubscriptionPlanModel.freemium_plan.value
        return SubscriptionPlan.objects.create(plan_id=self.request.user, subscription_type=subscription_type)

       
        
        
    @staticmethod
    def trial_end_date():
        today_date = date.today()
        trial_end_date = today_date + relativedelta(months=+1)
        return trial_end_date
        

    
