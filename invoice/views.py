import json
from enum import Enum
from collections import OrderedDict
from datetime import datetime

from django.contrib.auth import authenticate, get_user_model
from django.core import signing
from django.http import HttpResponseBadRequest
from django.core.mail import send_mail
from django.urls import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.db.models import Count


from twilio.rest import Client

from rest_framework.response import Response
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.validators import ValidationError
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, get_object_or_404

from cashtarg._celery import app
from accounts.authentication import JwtAuthentication


from .models import Invoice,  ClientInfo, AutomatedReminder
from .serializer import InvoiceSerializer, ClientSerializer, AutomatedReminderSerializer
from .tasks import send_sms, _send_email


class Medium(Enum):
    email = 'email'
    sms = 'sms'
    emailsms = 'emailsms'

class ReminderType(Enum):
    once = 'ONCE'
    everyday = 'EVERYDAY'


class CreateInvoice(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    #authentication_classes = (SessionAuthentication,)
    queryset = Invoice
    serializer_class = InvoiceSerializer

    def create(self, request, **kwargs):
        option = request.query_params.get('option', '')
        client_id = request.query_params.get('client_id', 0)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #encode_payment = self.encode_payment_data(**serializer.validated_data)
        client = self.get_client_id(client_id)

        if client != 0:
            if request.user.subscription_plan.is_freemium:
                if self.verify_user_monthly_invoice():
                    generate_link = self.generate_invoice_link(serializer.validated_data['invoice_id'], request.user.user_id)
                    self.perform_create(serializer, generate_link, client_id=client)
                    self.perform_invoice_delivery(generate_link, option, client=client, client_id=True)

                else:
                    return Response(data={
                    'status': 'failed', 'message': 'Exeeceded monthly limit'}, status=status.HTTP_400_BAD_REQUEST)

            generate_link = self.generate_invoice_link(serializer.validated_data['invoice_id'], request.user.user_id)
            self.perform_create(serializer, generate_link, client_id=client)
            self.perform_invoice_delivery(generate_link, option, client=client, client_id=True)


        else:
            if request.user.subscription_plan.is_freemium:
                verify_user_status = self.verify_user_monthly_invoice()
                if verify_user_status:
                    generate_link = self.generate_invoice_link(serializer.validated_data['invoice_id'], request.user.user_id)
                    self.perform_create(serializer, generate_link, client_id=client)
                    self.perform_invoice_delivery(generate_link, option, serializer=serializer)
              
                else:
                    return Response(data={'status': 'failed', 'message': 'Exeeceded monthly limit'}, status=status.HTTP_400_BAD_REQUEST)
                
            generate_link = self.generate_invoice_link(serializer.validated_data['invoice_id'], request.user.user_id)
            self.perform_create(serializer, generate_link, client_id=client)
            self.perform_invoice_delivery(generate_link, option, serializer=serializer)
    
        
        return Response(data={ 'data': serializer.data,  'url': generate_link}, status=status.HTTP_201_CREATED)


    @staticmethod
    def perform_invoice_delivery(generate_link, option, serializer='', client='', client_id=False):
        message_body = 'invoice link {}'.format(generate_link)
        if not client_id:
            
            if option != '' and option.lower() == Medium.email.value:
                _send_email.delay('Invoice', message_body, serializer.validated_data['client_email'])
            elif option != '' and option.lower() == Medium.sms.value and serializer.validated_data['client_phone_number'] is not None:
                send_sms.delay(generate_link, serializer.validated_data['client_phone_number'])
                
            elif option != '' and option.lower() == Medium.emailsms.value:
                _send_email.delay('Invoice', message_body, serializer.validated_data['client_email'])
                send_sms.delay(generate_link, serializer.validated_data['client_phone_number'])

        else:
            if option != '' and option.lower() == Medium.email.value:
                _send_email.delay('Invoice', message_body, client.client_email)
            elif option != '' and option.lower() == Medium.sms.value and client.client_phone_number is not None:
                send_sms.delay(generate_link, client.client_phone_number)
            elif option != '' and option.lower() == Medium.emailsms.value:
                _send_email.delay('Invoice', message_body, client.client_email)
                send_sms.delay(generate_link, client.client_phone_number)

    
    @staticmethod
    def get_client_id(pk_value):
        try:
            client_pk = ClientInfo.objects.get(pk=pk_value)
            
        except ClientInfo.DoesNotExist:
            client = 0
            return  client

        else:
            return client_pk


    def perform_create(self, instance, link, client_id, **kwargs):
        if client_id != 0:
            instance.save(link=link, client_id=client_id)
        else:
            instance.save(link=link)
 
    def generate_invoice_link(self, invoice_id, user_id):
        #link = getattr('settings', 'LINK_URL')
        link = getattr(settings, 'LINK_URL')
        url = '{}/{}/?user_id={}'.format(link, invoice_id, user_id)
        
        return url
    
    def verify_user_monthly_invoice(self):
        invoice_count = Invoice.objects.filter(user=self.request.user, created__month=datetime.today().month).values('created').annotate(count=Count('pk'))

        if not invoice_count.exists():
            return True

        if invoice_count[0]['count'] == settings.FREEMIUM_PLAN_LIMIT:
            
            return False
        return True
        

    

class ViewPendingInvoice(ListAPIView):
    queryset = Invoice
    #authentication_classes = (SessionAuthentication,)
    
    serializer_class = InvoiceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.objects.filter(user=self.request.user, is_pending=True).order_by('-created').all()
       
       

class ViewPaidInvoice(ViewPendingInvoice):

    def get_queryset(self):
        return self.queryset.objects.filter(user=self.request.user, is_pending=False).order_by('-created').all()
        

@api_view(['GET'])
#@authentication_classes([SessionAuthentication,])
@permission_classes([IsAuthenticated,])
def invoice_detail_view(request, invoice_id=None):
    if invoice_id is None:
        assert invoice_id ( "Expected view {} to be called with a URL keyword argument named {}\
            Fix your URL conf, \
                 attribute on the view correctly".format(invoice_detail_view, invoice_id)
        )
    
    invoice = get_object_or_404(Invoice, invoice_id=invoice_id)      

    invoice_data =  InvoiceSerializer(instance=invoice).data

    return Response(invoice_data)



class CreateClient(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = ClientInfo
    serializer_class = ClientSerializer
 
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated,])
def retrieve_client_info(request, user_pk):
    client_detail = get_object_or_404(ClientInfo, pk=user_pk)
    return Response(data={
        'client_name': client_detail.client_name,
        'client_email': client_detail.client_email,
        'client_phone_number': client_detail.phone_number
    }, status=status.HTTP_200_OK)



class ViewAllClient(ListAPIView):
    queryset = ClientInfo
    serializer_class = ClientSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.objects.filter(user=self.request.user)

class UpdateClientInfo(RetrieveUpdateAPIView):
    permission_classes = (
        
        IsAuthenticated,
    )
    serializer_class = ClientSerializer
    queryset = ClientInfo
    lookup_field = 'pk'
  

@api_view(['GET'])
@permission_classes([AllowAny,])
def view_data(request, encoded_data):
    value = signing.loads(encoded_data)
    
    return Response(data={
        'data': value
    }, status=status.HTTP_200_OK)


class CreateAutomatedReminder(CreateAPIView):
    #authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = AutomatedReminder
    serializer_class = AutomatedReminderSerializer


    def create(self, request, **kwargs):
        invoice_id = request.query_params.get('invoice_id', '')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice = Invoice.objects.get(invoice_id__iexact=invoice_id)
        if not invoice.is_pending:
            self.reminder_cant_be_created()

        elif invoice.is_pending and invoice.can_create_reminder:
                   
            try:
                AutomatedReminder.objects.get(invoice=invoice)
            except AutomatedReminder.DoesNotExist:
                if serializer.validated_data['medium'] == Medium.sms:
                    try:
                        invoice.client_id.client_phone_number
                    except AttributeError:
                        if invoice.client_phone_number is None:
                            self.reminder_cant_be_created()
                    else:
                        if  invoice.client_id.client_phone_number is None:
                            self.reminder_cant_be_created()
                elif serializer.validated_data['medium'] == Medium.email:
                    try:
                        invoice.client_id.client_email
                    except AttributeError:
                        if invoice.client_email is None:
                            self.reminder_cant_be_created()
                    else:
                        if invoice.client_id.client_email:
                            self.reminder_cant_be_created()
                   
                elif serializer.validated_data['medium'] == Medium.emailsms :
                    try:
                        invoice.client_id.client_email 
                        invoice.client_id.client_phone_number
                    except AttributeError:
                        if invoice.client_email is None and invoice.client_phone_number is None:
                            self.reminder_cant_be_created()
                    else:
                        if invoice.client_id.client_email  and invoice.client_id.client_phone_number:
                            self.reminder_cant_be_created()
                            
                reminder_type =  settings.AUTOMATED_REMINDER_TYPE.get(serializer.validated_data['reminder_type'].upper(), '')
                if reminder_type == ReminderType.once.value:
                    reminder_day = settings.AUTOMATED_REMINDERS_DAYS.get(serializer.validated_data['reminder_set_day'].upper(), 0)
                    self.perform_create(serializer, invoice, day=reminder_day)
                    invoice.can_create_reminder = False
                    invoice.save()
                    return Response(data='Reminder created', status=status.HTTP_201_CREATED)
                elif reminder_type == ReminderType.everyday:
                        self.perform_create(serializer, invoice)
                        invoice.can_create_reminder = False
                        invoice.save()
                        return Response(data='Reminder created', status=status.HTTP_201_CREATED)
            else:
                self.reminder_cant_be_created()

    def reminder_cant_be_created(self):
        return Response(data='Reminder Cant be created', status=status.HTTP_400_BAD_REQUEST)
        
    def perform_create(self, instance, invoice_id, day=0):
        instance.save(invoice=invoice_id, days_of_the_week=day)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated,])
def cancel_reminder(request, invoice_id):
    invoice = Invoice.objects.get(invoice_id__iexact=invoice_id)
    invoice.can_create_reminder = True
    invoice.save()
    AutomatedReminder.objects.filter(invoice=invoice).delete()
    return Response(data='Reminder Cancelled', status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated,])
def approve_invoice(request, invoice_id):
    invoice = Invoice.objects.get(invoice_id__iexact=invoice_id)
    invoice.is_pending = False
    invoice.save()
    return Response(data='Reminder Cancelled', status=status.HTTP_200_OK)


class DeleteClientView(DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ClientSerializer
    queryset = ClientInfo
    lookup_field = 'pk'

class DeleteInvoiceView(DeleteClientView):
    queryset = Invoice
    serializer_class = InvoiceSerializer


@api_view(['GET'])
@authentication_classes([JwtAuthentication,])
@permission_classes([AllowAny,])
def view_invoice_for_payment(request, invoice_id):
    user_id = request.query_params.get('user_id', None)
    if user_id is None:
        raise ValidationError('The request made to this server was bad')

    if request.user.is_authenticated and request.user.user_id == user_id:
        raise ValidationError('The request made to this server was bad')

    
    data = OrderedDict()
    queryset = getattr(settings, 'AUTH_USER_MODEL')
    
    #user = get_object_or_404(queryset, user_id=user_id)
    try:
        user = get_user_model().objects.get(user_id=user_id)
        invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
    except get_user_model().DoesNotExist:
       
        raise  ValidationError('The request made to this server was bad')
    except Invoice.DoestNotExist:
       raise  ValidationError('The request made to this server was bad')

    user_detail = {
        'business_name': user.buiness_info.business_name,
        'business_number': user.buiness_info.business_number,
        'business_address': user.buiness_info.business_address,
        'business_email': user.email
    }

    invoice_detail = InvoiceSerializer(instance=invoice).data
    data['user'] = user_detail
    data['invoice_detail'] = invoice_detail
    
    return Response(data)





