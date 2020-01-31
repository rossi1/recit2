from enum import Enum

from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib.auth import login
from django.db.models import Count


from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

import stripe


from subscription.models import SubscriptionPlan
from subscription.views import SubscriptionPlanModel
from invoice.models  import Invoice

from .serializer import UserSerializer, LoginSerializer, PasswordResetSerializer,  PasswordSerializer, BusinessSerializer
from .utils import  password_reset_code, generate_safe_token, validate_code, get_tokens_for_user
from .authentication import JwtAuthentication
from .models import BusinessInfo



stripe.api_key = 'sk_test_wkwaWE7YeaKbYZd5Yz5dpbrF'


class SignupView(CreateAPIView):
    serializer_class = BusinessSerializer
    
    def create(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = get_user_model().objects.get(email__iexact=serializer.validated_data['account']['email'])
        token = get_tokens_for_user(user)
        return Response(data={'details': serializer.data, 'token': token, 'pk': user.pk,
        'full_name': "{} {}".format(serializer.validated_data['account']['last_name'], serializer.validated_data['account']['first_name'])}, status=status.HTTP_201_CREATED)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)
           
            if user is None:
                return Response({'invalid credentials': 'invalid login credentials'}, status=status.HTTP_400_BAD_REQUEST)

            elif not user.is_active:
                return Response({'status': 'failed', 'message': 
                'Account disabled'}, status=status.HTTP_400_BAD_REQUEST)


            else:
                token = get_tokens_for_user(user)

                try:
                    account_plan =  SubscriptionPlan.objects.get(plan_id=user)
                except SubscriptionPlan.DoesNotExist:
                    account_plan = None
                    invoice_count = 0
                    last_card_no = None
                else:
                    account_plan = account_plan.subscription_type
                    if account_plan == SubscriptionPlanModel.freelance_plan.value:
                        invoice_type = getattr(settings, 'ONE_TIME')
                        invoice = Invoice.objects.filter(user=user, invoice_type=invoice_type,
                        created__range=[user.subscription_plan.subscription_start_date, user.subscription_plan.subscription_end_date]).exclude(is_pending=False).values('created').annotate(count=Count('pk'))
                        #invoice_count = invoice[0]['count']
                    elif account_plan == SubscriptionPlanModel.business_plan.value:
                        invoice_one_time = getattr(settings, 'ONE_TIME')
                        invoice_type = [getattr(settings, 'RECURRING_WEEKLY'), getattr(settings, 'RECURRING_MONTHLY'), getattr(settings, 'RECURRING_DAILY')]
                        invoice = Invoice.objects.filter(user=user, invoice_type__in=invoice_type,
                        created__range=[user.subscription_plan.subscription_start_date, 
                        user.subscription_plan.subscription_end_date]).exclude(is_pending=False).values('created').annotate(count=Count('pk'))
                        
                    else:
                        invoice = Invoice.objects.filter(user=user,
                        created__range=[user.subscription_plan.subscription_start_date, 
                        user.subscription_plan.subscription_end_date]).exclude(is_pending=False).values('created').annotate(count=Count('pk'))
                        


                    if not invoice.exists():
                        invoice_count = 0
                    else:
                        invoice_count = invoice[0]['count']

                    last_card_no = self.get_card_info(user.subscription_plan.customer_id)


                return Response(data={'token': token, 'has_uploaded_business_account': user.buiness_info.has_uploaded_bank_details, 'pk': user.pk, 'business_pk': user.buiness_info.pk,  
            'account_type': {'account_plan': account_plan, 'invoice_count': invoice_count, 'last_card_no': last_card_no}}, 
                    status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors)

    @staticmethod
    def get_card_info(customer_id):
        customer = stripe.Customer.retrieve(customer_id)
        #print(customer)
        if customer.sources.data == []:
            card = None
        else:
            card = customer.sources.data[0]['last4']
        
        return card


class LogoutView(GenericAPIView):
    
 
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({'message': 'True', 'reason': 'logged out successfully', 'res':True}, status=status.HTTP_200_OK)


@api_view(['POST'])
def reset_password_view(request):
    serializer = PasswordResetSerializer(data=request.data)

    if serializer.is_valid():
        if get_user_model().objects.filter(email__iexact=serializer.validated_data['email']).exists():
            code = password_reset_code()
            message_body = 'Real Estate password reset code {}'.format(code)
            send_mail('Password reset code', message_body, settings.EMAIL_HOST_USER, [serializer.validated_data['email']], fail_silently=False)
            tokenize_code = generate_safe_token(code)
            return Response(data={'token': tokenize_code, 'email': serializer.validated_data['email']}, status=status.HTTP_200_OK)
        else:
            return Response(data='Email doesnt belong to any account', status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def reset_code_verification(request):
    tokenize_code = request.query_params.get('code')
    email = request.query_params.get('email')
    serializer = PasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    decode_token = validate_code(tokenize_code)
    encode  = generate_safe_token(email)

    if serializer.validated_data['password'] == decode_token:
        return Response(data={'message': 'Code Verification Successful', 'email': email, 'code': encode}, status=status.HTTP_200_OK)
     
    return Response(data={'message': 'Code Verification Failed', 'email': email}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def reset_password(request):
    tokenize_code = request.query_params.get('code')
    serializer = PasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = validate_code(tokenize_code)
    try:
        queryset = get_user_model().objects.get(email__iexact=email)
    except ObjectDoesNotExist:
        return Response(data='An error occured', status=status.HTTP_400_BAD_REQUEST)
    else:
        password =  serializer.validated_data['password']
        queryset.password = password
        queryset.set_password(password)
        queryset.save() 
    return Response(data='Password Changed Succesfully' , status=status.HTTP_200_OK)


   
class UpdateBusinessAccount(RetrieveUpdateAPIView):
    
    permission_classes = (IsAuthenticated,)
    serializer_class =  BusinessSerializer
    queryset = BusinessInfo
    lookup_url_kwarg = 'pk'


@api_view(['POST'])
@permission_classes([IsAuthenticated,])
def create_business_account(request):
    try:
        instance = BusinessInfo.objects.get(user=request.user)
    except BusinessInfo.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        serializer = BusinessSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.instance.has_uploaded_bank_details = True
        serializer.save()
        return Response(data='Account created successfully', status=status.HTTP_201_CREATED)
            

@api_view(['GET'])
def validate_business_name(request):
    business_name = request.query_params.get('business_name', '')

    if BusinessInfo.objects.filter(business_name__iexact=business_name).exists():
        return Response(data=True, status=status.HTTP_302_FOUND)
    else:
        return Response(data=False, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated,])
def disabled_account(request):
    get_user_model().objects.filter(email=request.user.email).update(is_active=False)
    return Response({'status': 'sucesss', 'message': 'Account disabled'}, status=status.HTTP_200_OK)
