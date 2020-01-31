from enum import Enum

from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib.auth import login


from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from subscription.models import SubscriptionPlan

from .serializer import UserSerializer, LoginSerializer, PasswordResetSerializer,  PasswordSerializer, BusinessSerializer
from .utils import  password_reset_code, generate_safe_token, validate_code, get_tokens_for_user
from .authentication import JwtAuthentication
from .models import BusinessInfo


class SubscriptionPlanModel(Enum):
    freelance_plan = 'freelance_plan'
    business_plan = 'business_plan'


class SignupView(CreateAPIView):
    serializer_class = BusinessSerializer
    
    def create(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer
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
            else:
                token = get_tokens_for_user(user)

                try:
                    account_plan =  SubscriptionPlan.objects.get(plan_id=user)
                except SubscriptionPlan.DoesNotExist:
                    account_plan = None
                else:
                    account_plan = account_plan.subscription_type

                return Response(data={'token': token, 'has_uploaded_business_account': user.buiness_info.has_uploaded_bank_details, 'pk': user.pk,  'account_type': {'account_plan': account_plan, 'trial': getattr(account_plan, 'is_trial', None)}}, 
                    status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors)

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