from django.apps import AppConfig


class InvoiceConfig(AppConfig):
    name = 'invoice'

    def ready(self):
        import invoice.signal