from django.contrib import admin
from .models import Account, Transaction
from unfold.admin import ModelAdmin
from django.contrib.auth.models import User , Group
from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm, SelectableFieldsExportForm
# import export select 

# Register your models here.


# unregister user and groups
admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(ModelAdmin):
    pass


class SentTransactionInline(admin.TabularInline):
    model = Transaction
    fk_name = 'sender'  # Refers to the sender field
    extra = 0
    verbose_name = "Sent Transaction"
    verbose_name_plural = "Sent Transactions"


class ReceivedTransactionInline(admin.TabularInline):
    model = Transaction
    fk_name = 'receiver'  # Refers to the receiver field
    extra = 0
    verbose_name = "Received Transaction"
    verbose_name_plural = "Received Transactions"


@admin.register(Account)
class AccountAdmin(ModelAdmin, ImportExportModelAdmin):

    list_display = ['name', 'balance']
    search_fields = ['name']
    list_per_page = 50
    inlines = [SentTransactionInline, ReceivedTransactionInline]




@admin.register(Transaction)
class TransactionAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ['sender', 'receiver', 'amount', 'date']
    search_fields = ['sender__name', 'receiver__name']
    list_per_page = 50




