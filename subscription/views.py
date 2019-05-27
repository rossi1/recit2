from enum import Enum
from datetime import date
import datetime

from dateutil.relativedelta import *
import stripe





from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.response import Response
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework import status
from rest_framework.validators import ValidationError
from rest_framework.views import APIView


from .models  import SubscriptionPlan
from .utils import subscribe_stripe_plan, extend_subscription_date
from .tasks import _send_email


endpoint_secret = 'whsec_Po9VYbT7FbzvhGdjVlg7TB6lGokUJNIk'





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
        tx_code = request.data.get('tf_code',  None)
        if fetch_plan is not None:
            create_customer = self.create_customer(tx_code)
            cu = 'cus_F1vznWGNy8kXKz'
           
            if fetch_plan ==  SubscriptionPlanModel.freelance_plan.value:

                self.update_user_plan_to_freelancing(create_customer)
                return Response(data={'status': 'success'}, status=status.HTTP_200_OK)
        
               
            elif fetch_plan == SubscriptionPlanModel.business_plan.value:
                self.update_user_plan_to_business(create_customer)
                return Response(data={'status': 'success'}, status=status.HTTP_200_OK)

            else:
                self.update_user_plan_to_freemium()
                return Response(data={'status': 'success'}, status=status.HTTP_200_OK)

               
                
        return  Response('Failed to get plan')

    def create_customer(self, token):
        create = stripe.Customer.create(
            email=self.request.user.email,
            source=token)
        return create

    


    def update_user_plan_to_freelancing(self, customer_id):
        subscribe_plan = subscribe_stripe_plan(customer_id.id, getattr(settings, 'FREELANCE_PLAN_ID'))
        sub_start_date = datetime.datetime.utcfromtimestamp(subscribe_plan.current_period_start)
        sub_end_date = datetime.datetime.utcfromtimestamp(subscribe_plan.current_period_end)
        subscription_type = SubscriptionPlanModel.freelance_plan.value
        return SubscriptionPlan.objects.create(plan_id=self.request.user, subscription_type=subscription_type,
        subscription_start_date=sub_start_date.date(), subscription_end_date=sub_end_date.date(),
        customer_id=customer_id.id, subscription_id=subscribe_plan.id)


     
       
    def update_user_plan_to_business(self, customer_id):
        subscribe_plan = subscribe_stripe_plan(customer_id.id, getattr(settings, 'BUSINESS_PLAN_ID'))
        sub_start_date = datetime.datetime.utcfromtimestamp(subscribe_plan.current_period_start)
        sub_end_date = datetime.datetime.utcfromtimestamp(subscribe_plan.current_period_end)
        subscription_type = SubscriptionPlanModel.business_plan.value
        return SubscriptionPlan.objects.create(plan_id=self.request.user, subscription_type=subscription_type, 
        subscription_start_date=sub_start_date.date(), subscription_end_date=sub_end_date.date(),
        customer_id=customer_id.id, subscription_id=subscribe_plan.id)

    def update_user_plan_to_freemium(self):
        #subscribe_plan = subscribe_stripe_plan(customer_id.id, getattr(settings, 'FREEMIUM_PLAN_ID'))
        subscription_type = SubscriptionPlanModel.freemium_plan.value
        return SubscriptionPlan.objects.create(plan_id=self.request.user, subscription_type=subscription_type,
        subscription_start_date=date.today(), subscription_end_date=extend_subscription_date())

       
    
    
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cancel_subscription_plan(request):
   stripe.Subscription.delete(request.user.subscription_id)
   #freemium_plan = subscribe_stripe_plan(request.user.customer_id, getattr(settings, 'FREEMIUM_PLAN_ID'))
   sub_start_date = date.today()
   sub_end_date = extend_subscription_date()
   subscription_type = SubscriptionPlanModel.freemium_plan.value
   SubscriptionPlan.objects.filter(plan_id=request.user).update(subscription_type=subscription_type,
   subscription_start_date=sub_start_date, 
   subscription_end_date=sub_end_date,
   subscription_id='')
   return Response(data={'status': 'success'}, status=status.HTTP_200_OK)


class SwitchSubscriptionPlan(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        #
        get_plan = request.query_params.get('sub_plan',  None)

        if get_plan is not None:
        
            if get_plan == SubscriptionPlanModel.freelance_plan.value:
                if request.user.subscription_plan.subscription_type == SubscriptionPlanModel.freemium_plan.value:
                    pass
                else:
                    stripe.Subscription.delete(request.user.subscription_plan.subscription_id)
              
                subscription_type = SubscriptionPlanModel.freelance_plan.value
                try:
                    subscribe_plan = subscribe_stripe_plan(request.user.subscription_plan.customer_id, getattr(settings, 'FREELANCE_PLAN_ID'), switch=True)
                except stripe.error.CardError as e:
                    return Response({
                        "status": "failed", "message": "Unable to charge card please update card"
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    sub_start_date = datetime.datetime.utcfromtimestamp(subscribe_plan.current_period_start)
                    sub_end_date = datetime.datetime.utcfromtimestamp(subscribe_plan.current_period_end)
                    SubscriptionPlan.objects.filter(plan_id=request.user).update(subscription_type=subscription_type,
                    subscription_start_date=sub_start_date.date(), 
                    subscription_end_date=sub_end_date.date(), subscription_id=subscribe_plan.id)
                    return Response(data={'status': 'success'}, status=status.HTTP_200_OK)

            elif get_plan == SubscriptionPlanModel.business_plan.value:
                if request.user.subscription_plan.subscription_type == SubscriptionPlanModel.freemium_plan.value:
                    pass
                else:
                    stripe.Subscription.delete(request.user.subscription_plan.subscription_id)
                #stripe.Subscription.delete(request.user.subscription_plan.subscription_id)
                subscription_type = SubscriptionPlanModel.business_plan.value
                try:
                    
                    subscribe_plan = subscribe_stripe_plan(request.user.subscription_plan.customer_id, getattr(settings, 'BUSINESS_PLAN_ID'), switch=True)
                except stripe.error.CardError as e:
                    return Response({
                        "error": "failed", "message": "Unable to charge card please update card"
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    sub_start_date = datetime.datetime.utcfromtimestamp(subscribe_plan.current_period_start)
                    sub_end_date = datetime.datetime.utcfromtimestamp(subscribe_plan.current_period_end)
                    SubscriptionPlan.objects.filter(plan_id=request.user).update(subscription_type=subscription_type,
                    subscription_start_date=sub_start_date.date(), 
                    subscription_end_date=sub_end_date.date(), subscription_id=subscribe_plan.id)
                    return Response(data={'status': 'success'}, status=status.HTTP_200_OK)
            else:
                subscription_type = SubscriptionPlanModel.freemium_plan.value
                if request.user.subscription_plan.subscription_type == SubscriptionPlanModel.freemium_plan.value:
                    pass
                else:
                    stripe.Subscription.delete(request.user.subscription_plan.subscription_id)
                sub_start_date = date.today()
                sub_end_date = extend_subscription_date()
                SubscriptionPlan.objects.filter(plan_id=request.user).update(subscription_type=subscription_type,
                subscription_start_date=sub_start_date.date(), 
                subscription_end_date=sub_end_date.date(),
                subscription_id='')
                return Response(data={'status': 'success'}, status=status.HTTP_200_OK)


class UpdateCustomerCardToken(APIView):
    PermissionError = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        request_body = request.data.get('tf_code',  None)
        if request_body is not None:
            if request.user.subscription_plan.subscription_type == SubscriptionPlanModel.freemium_plan.value:
                create_customer = stripe.Customer.create(email=self.request.user.email, source=token)
                SubscriptionPlan.objects.filter(plan_id=request.user).update(customer_id=create_customer.id)

            else:
                stripe.Customer.modify(request.user.subscription_plan.customer_id,
                source=request_body)
                
                
            return Response({"status": "success", "message":  "Card updated"}, status=status.HTTP_200_OK)

        return Response(
            {"status": "error", "message": 
            "No parameters found"}, status=status.HTTP_400_BAD_REQUEST
        )


@csrf_exempt
def my_webhook_view(request):
  payload = request.body
  sig_header = request.META['HTTP_STRIPE_SIGNATURE']
  event = None

  try:
    event = stripe.Webhook.construct_event(
      payload, sig_header, endpoint_secret
    )
  except ValueError as e:
    # Invalid payload
    return Response(status.HTTP_400_BAD_REQUEST)
  except stripe.error.SignatureVerificationError as e:
    # Invalid signature
    return HttpResponse(status=400)

  else:
       # Handle the event
    if event.type == 'payment_intent.succeeded':
         # contains a stripe.PaymentIntent

        payment_intent = event.data.object
        
        if payment_intent.billing_reason == "subscription_update":
            customer_id = payment_intent.customer
            sub_start_date = datetime.datetime.utcfromtimestamp(payment_intent.lines.data.period.start)
            sub_end_date =  datetime.datetime.utcfromtimestamp(payment_intent.lines.data.period.start)
            subscription_id = payment_intent.subscription
            SubscriptionPlan.objects.filter(customer_id=customer_id).update(subscription_start_date=sub_start_date.date(), 
                subscription_end_date=sub_end_date.date(),
                subscription_id=subscription_id

            )
            
    elif event.type == 'invoice.payment_failed':
        payment_intent = event.data.object
        customer_id = payment_intent.customer
        cus_email = payment_intent.customer_email
        subscription_type = SubscriptionPlanModel.freemium_plan.value
        sub_start_date = date.today()
        sub_end_date = extend_subscription_date()
        SubscriptionPlan.objects.filter(customer_id=customer_id).update(subscription_start_date=sub_start_date, 
        subscription_end_date=sub_end_date,
        subscription_id='',
        subscription_type=subscription_type)
        _send_email("Your Subscription plan to Recit Failed",  "Failed to subscribe to plan", cus_email)
    
    

  return HttpResponse(200)

   