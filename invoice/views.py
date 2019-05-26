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


from twilio.rest import Client


from django.db.models import Count


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

from subscription.views import SubscriptionPlanModel


class Medium(Enum):
    email = 'email'
    sms = 'sms'
    emailsms = 'emailsms'

class ReminderType(Enum):
    once = 'ONCE'
    everyday = 'EVERYDAY'


def invoice_data_with_client(invoice, exclude=False):


    data = {
                    'pk': invoice.pk,
                    'client_name': invoice.client_id.client_name,
                    'client_address': invoice.client_id.client_address,
                    'client_email': invoice.client_id.client_email,
                    'client_phone_number': invoice.client_id.client_phone_number,
                    'invoice_id': invoice.invoice_id,
                    'invoice_type': invoice.invoice_type,
                    'created': invoice.created,
                    'due_date': invoice.due_date,
                    'is_pending': invoice.is_pending,
                    'data': invoice.data,
                    'description': invoice.description,
                    'link': invoice.link,
                    #'logo': invoice.logo,
                    'project_amount': invoice.project_amount,
                    'currency': invoice.currency,
                    'tax': invoice.tax,
                    'shipping_fee': invoice.shipping_fee,
                    'can_create_reminder': invoice.can_create_reminder
                    
                }

    if exclude:
        del data['can_create_reminder']
        del data['pk']

   
    return data

def invoice_data_with__no_client(invoice, exclude=False):
    
    data = {
                    'pk': invoice.pk,
                    'client_name': invoice.client_name,
                    'client_address': invoice.client_address,
                    'client_email': invoice.client_email,
                    'client_phone_number': invoice.client_phone_number,
                    'invoice_id': invoice.invoice_id,
                    'invoice_type': invoice.invoice_type,
                    'created': invoice.created,
                    'due_date': invoice.due_date,
                    'is_pending': invoice.is_pending,
                    'data': invoice.data,
                    'description': invoice.description,
                    'link': invoice.link,
                    
                    #'logo': invoice.logo,
                    'project_amount': invoice.project_amount,
                    'currency': invoice.currency,
                    'tax': invoice.tax,
                    'shipping_fee': invoice.shipping_fee,
                    'can_create_reminder': invoice.can_create_reminder
                    
                }

    if exclude:
        del data['can_create_reminder']
        del data['pk']


    return data 



class CreateInvoice(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    #authentication_classes = (SessionAuthentication,)
    queryset = Invoice
    serializer_class = InvoiceSerializer

    def create(self, request, **kwargs):
        option = request.query_params.get('option', '')
        client_id = request.query_params.get('client__id', 0)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #encode_payment = self.encode_payment_data(**serializer.validated_data)
        client = self.get_client_id(client_id)

        if client != 0:
            if request.user.subscription_plan.subscription_type == SubscriptionPlanModel.freemium_plan.value:
                verify_user_status = self.verify_user_monthly_invoice()
                if verify_user_status:
                    generate_link = self.generate_invoice_link(serializer.validated_data['invoice_id'], request.user.user_id)
                    self.perform_create(serializer, generate_link, client_id=client)
                    self.perform_invoice_delivery(generate_link, option, client=client, client_id=True)

                else:
                    return Response(data={
                    'status': 'failed', 'message': 'Exeeceded monthly limit'}, status=status.HTTP_400_BAD_REQUEST)

                
            elif request.user.subscription_plan.subscription_type == SubscriptionPlanModel.freelance_plan.value:
                if serializer.validated_data['invoice_type'].lower() == settings.ONE_TIME:
                    generate_link = self.generate_invoice_link(serializer.validated_data['invoice_id'], request.user.user_id)
                    self.perform_create(serializer, generate_link, client_id=client)
                    self.perform_invoice_delivery(generate_link, option, client=client, client_id=True)
                else:
                    verify_user_status = self.verify_user_monthly_invoice(invoice_one_time=False)
                    if verify_user_status:
                        generate_link = self.generate_invoice_link(serializer.validated_data['invoice_id'], request.user.user_id)
                        self.perform_create(serializer, generate_link, client_id=client)
                        self.perform_invoice_delivery(generate_link, option, client=client, client_id=True)
                    
                    else:
                        return Response(data={'status': 'failed', 'message': 'Exeeceded monthly limit'}, status=status.HTTP_400_BAD_REQUEST)

            else:
                generate_link = self.generate_invoice_link(serializer.validated_data['invoice_id'], request.user.user_id)
                self.perform_create(serializer, generate_link, client_id=client)
                self.perform_invoice_delivery(generate_link, option, client=client, client_id=True)
                


                        
        else:
            if request.user.subscription_plan.subscription_type == SubscriptionPlanModel.freemium_plan.value:
                verify_user_status = self.verify_user_monthly_invoice()
                if verify_user_status:
                    generate_link = self.generate_invoice_link(serializer.validated_data['invoice_id'], request.user.user_id)
                    self.perform_create(serializer, generate_link, client_id=client)
                    self.perform_invoice_delivery(generate_link, option, serializer=serializer)
        

                   
                else:
                    return Response(data={
                    'status': 'failed', 'message': 'Exeeceded monthly limit'}, status=status.HTTP_400_BAD_REQUEST)

                
            elif request.user.subscription_plan.subscription_type == SubscriptionPlanModel.freelance_plan.value:
                if serializer.validated_data['invoice_type'].lower() == settings.ONE_TIME:
                    generate_link = self.generate_invoice_link(serializer.validated_data['invoice_id'], request.user.user_id)
                    self.perform_create(serializer, generate_link, client_id=client)
                    self.perform_invoice_delivery(generate_link, option, client=client, client_id=True)
                else:
                    verify_user_status = self.verify_user_monthly_invoice(invoice_one_time=False)
                    if verify_user_status:
                        generate_link = self.generate_invoice_link(serializer.validated_data['invoice_id'], request.user.user_id)
                        self.perform_create(serializer, generate_link, client_id=client)
                        self.perform_invoice_delivery(generate_link, option, serializer=serializer)
                    else:
                        return Response(data={'status': 'failed', 'message': 'Exeeceded monthly limit'}, status=status.HTTP_400_BAD_REQUEST)

            else:
                generate_link = self.generate_invoice_link(serializer.validated_data['invoice_id'], request.user.user_id)
                self.perform_create(serializer, generate_link, client_id=client)
                self.perform_invoice_delivery(generate_link, option, serializer=serializer)
                


    
        
        return Response(data={
            'data': serializer.data,
            'url': generate_link
        }, status=status.HTTP_201_CREATED)


    @staticmethod
    def perform_invoice_delivery(generate_link, option, serializer='', client='', client_id=False):
        message_body = 'invoice link {}'.format(generate_link)
        if client_id:
            if option != '' and option.lower() == Medium.email.value:
                _send_email.delay('Invoice', message_body, client.client_email)
            elif option != '' and option.lower() == Medium.sms.value and client.client_phone_number is not None:
                send_sms.delay(generate_link, client.client_phone_number)
            elif option != '' and option.lower() == Medium.emailsms.value:
                _send_email.delay('Invoice', message_body, client.client_email)
                send_sms.delay(generate_link, client.client_phone_number)
            
            

        else:
            if option != '' and option.lower() == Medium.email.value:
                _send_email.delay('Invoice', message_body, serializer.validated_data['client_email'])
            elif option != '' and option.lower() == Medium.sms.value and serializer.validated_data['client_phone_number'] is not None:
                send_sms.delay(generate_link, serializer.validated_data['client_phone_number'])
                
            elif option != '' and option.lower() == Medium.emailsms.value:
                _send_email.delay('Invoice', message_body, serializer.validated_data['client_email'])
                send_sms.delay(generate_link, serializer.validated_data['client_phone_number'])
         
            

    
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
    
    def verify_user_monthly_invoice(self, invoice_one_time=True):
        if invoice_one_time:
            limit = settings.FREEMIUM_PLAN_LIMIT
            invoice_type = getattr(settings, 'ONE_TIME')
            invoice_count = Invoice.objects.filter(user=self.request.user, invoice_type=invoice_type,
            created__range=[self.request.user.subscription_plan.subscription_start_date, self.request.user.subscription_plan.subscription_end_date]).exclude(
                is_pending=False).values('created').annotate(count=Count('pk'))
        else:
            limit = settings.FREELANCE_PLAN_LIMIT
            invoice_one_time = getattr(settings, 'ONE_TIME')
            invoice_type = [getattr(settings, 'RECURRING_WEEKLY'), getattr(settings, 'RECURRING_MONTHLY'), getattr(settings, 'RECURRING_DAILY')]
            invoice_count = Invoice.objects.filter(user=self.request.user, invoice_type__in=invoice_type,
            created__range=[self.request.user.subscription_plan.subscription_start_date, 
            self.request.user.subscription_plan.subscription_end_date]).exclude(
                is_pending=False).values('created').annotate(count=Count('pk'))

        
        print(invoice_count)

        if not invoice_count.exists():
            return True
            
    
        if invoice_count[0]['count'] == limit:
            
            return False
        return True

        
        
    

class ViewPendingInvoice(ListAPIView):
    queryset = Invoice
    #authentication_classes = (SessionAuthentication,)
    
    serializer_class = InvoiceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        data  = OrderedDict()
        list_data = []
        invoices = self.queryset.objects.filter(user=self.request.user, is_pending=True).order_by('-created').all()
        if invoices.exists():
            for invoice in invoices:
                try:
                    data = invoice_data_with_client(invoice)
                except AttributeError:
                    data = invoice_data_with__no_client(invoice)
                   

                list_data.append(data)

        return list_data

       
  
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            #serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(queryset)

        #serializer = self.get_serializer(queryset, many=True)
        return Response(queryset)


class ViewPaidInvoice(ViewPendingInvoice):

    def get_queryset(self):
        data  = OrderedDict()
        list_data = []
        invoices = self.queryset.objects.filter(user=self.request.user, is_pending=False).order_by('-created').all()
        if invoices.exists():
            for invoice in invoices:
                try:
                    data = invoice_data(invoice)
                except:
                    data['client_email'] = invoice.client_email
                    data['client_name'] = invoice.client_name
                    data['client_phone_number'] = invoice.client_phone_number
                    data['client_address'] = invoice.client_address

                    list_data.append(data)

                else:
                    list_data.append(data)
        

        return list_data


@api_view(['GET'])
#@authentication_classes([SessionAuthentication,])
@permission_classes([IsAuthenticated,])
def invoice_detail_view(request, invoice_id=None):
    if invoice_id is None:
        assert invoice_id ( "Expected view {} to be called with a URL keyword argument named {}\
            Fix your URL conf, \
                 attribute on the view correctly".format(invoice_detail_view, invoice_id)
        )
    
    data = OrderedDict()
    invoice = get_object_or_404(Invoice, invoice_id=invoice_id)

    #data =  invoice_data(invoice)
    try:
        data = invoice_data_with_client(invoice)
    except:
        data = invoice_data_with__no_client(invoice) 
        
        

    return Response(data)




class CreateClient(CreateAPIView):
    # write a custom permission later
    permission_classes = (IsAuthenticated,)
    queryset = ClientInfo
    serializer_class = ClientSerializer


    def create(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['client_email'] == request.user.email:
            raise ValidationError('You cant add yourself as a client')
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

 
  
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
                if serializer.validated_data['medium'] == Medium.sms.value:
                    try:
                        invoice.client_id.client_phone_number
                    except AttributeError:
                        if invoice.client_phone_number is None:
                            self.reminder_cant_be_created()
                    else:
                        if  invoice.client_id.client_phone_number is None:
                            self.reminder_cant_be_created()
                elif serializer.validated_data['medium'] == Medium.email.value:
                    try:
                        invoice.client_id.client_email
                    except AttributeError:
                        if invoice.client_email is None:
                            self.reminder_cant_be_created()
                    else:
                        if invoice.client_id.client_email:
                            self.reminder_cant_be_created()
                   
                elif serializer.validated_data['medium'] == Medium.emailsms.value :
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
                elif reminder_type == ReminderType.everyday.value:
                        self.perform_create(serializer, invoice)
                        invoice.can_create_reminder = False
                        invoice.save()
                        return Response(data='Reminder created', status=status.HTTP_201_CREATED)
                  
                    
            else:
                self.reminder_cant_be_created()

    @staticmethod
    def reminder_cant_be_created():
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

    #invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
    #invoice_detail = invoice_data(invoice, exclude=True)
    try:
        invoice_detail = invoice_data_with_client(invoice, exclude=True)
    except AttributeError:
        invoice_detail = invoice_data_with__no_client(invoice, exclude=True)
        
    
    
    data['user'] = user_detail
    data['invoice_detail'] = invoice_detail
    print(data)
    return Response(data)





