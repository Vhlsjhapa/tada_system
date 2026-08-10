from django.contrib import admin
from django.utils.html import format_html
from .models import Office, Employee, TravelOrder, TravelBill, TravelBillItem, TravelReport

class BaseAdminMedia(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/nepali_calendar.css',)
        }
        js = ('js/nepali_calendar.js',)


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'office_code', 'head_title', 'is_default_status', 'quick_actions')
    list_filter = ('is_default', 'location')
    search_fields = ('name', 'location', 'office_code', 'parent_body_1', 'parent_body_2')
    fieldsets = (
        ('१. कार्यालयको मुख्य पहिचान', {
            'fields': ('name', 'location', 'office_code', 'head_title', 'is_default')
        }),
        ('२. तहगत निकायहरू (Hierarchy Details)', {
            'fields': ('parent_body_1', 'parent_body_2', 'parent_body_3')
        }),
        ('३. सम्पर्क विवरण', {
            'fields': ('phone_no', 'email')
        }),
    )

    def is_default_status(self, obj):
        if obj.is_default:
            return format_html('<span style="background:#16a34a; color:white; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:bold;">★ सक्रिय कार्यालय</span>')
        return format_html('<span style="color:#64748b; font-size:12px;">सामान्य</span>')
    is_default_status.short_description = 'स्थिति'

    def quick_actions(self, obj):
        if not obj.is_default:
            return format_html('<a class="button" style="background:#0284c7; color:white; padding:3px 8px; border-radius:4px; font-size:11px; text-decoration:none;" href="/offices/set-default/{}/">सक्रिय बनाउनुहोस्</a>', obj.pk)
        return format_html('<b style="color:#16a34a;">सक्रिय छ</b>')
    quick_actions.short_description = 'कार्य'


@admin.register(Employee)
class EmployeeAdmin(BaseAdminMedia):
    list_display = ('name', 'code_no', 'designation', 'level', 'get_office', 'mobile_no', 'is_active')
    search_fields = ('name', 'code_no', 'designation', 'office', 'office_ref__name')
    list_filter = ('is_active', 'office_ref', 'designation')

    def get_office(self, obj):
        if obj.office_ref:
            return obj.office_ref.name
        return obj.office or '-'
    get_office.short_description = 'कार्यालय'


@admin.register(TravelOrder)
class TravelOrderAdmin(BaseAdminMedia):
    list_display = ('order_number', 'person', 'code_no', 'destination', 'start_date', 'end_date', 'print_button', 'nivedan_button', 'create_bill_button')
    list_filter = ('fiscal_year', 'office_ref', 'created_at')
    search_fields = ('order_number', 'person', 'code_no', 'destination')
    autocomplete_fields = ['employee']
    fieldsets = (
        ('१. आदेश तथा कार्यालय/कर्मचारी विवरण', {
            'fields': ('order_number', 'order_date', 'fiscal_year', 'office_ref', 'employee', 'person', 'code_no', 'designation', 'office')
        }),
        ('२. भ्रमण विवरण तथा साधन', {
            'fields': ('destination', 'purpose', 'start_date', 'end_date', 'vehicle_office', 'vehicle_public', 'vehicle_rent')
        }),
        ('३. पेस्की तथा अन्य विवरण', {
            'fields': ('advance_amount', 'advance_words', 'other_details', 'program_name', 'admin_date')
        }),
    )

    def print_button(self, obj):
        return format_html('<a class="button" style="background:#1e40af; color:white; padding:4px 8px; border-radius:4px; text-decoration:none;" href="/order/{}/" target="_blank">🖨️ आदेश (म.ले.प. २२३)</a>', obj.pk)
    print_button.short_description = 'आदेश प्रिन्ट'

    def nivedan_button(self, obj):
        return format_html('<a class="button" style="background:#4338ca; color:white; padding:4px 8px; border-radius:4px; text-decoration:none;" href="/order/{}/nivedan/" target="_blank">📝 पेस्की निवेदन</a>', obj.pk)
    nivedan_button.short_description = 'पेस्की निवेदन'

    def create_bill_button(self, obj):
        return format_html('<a class="button" style="background:#059669; color:white; padding:4px 8px; border-radius:4px; text-decoration:none;" href="/bill/new/?order_id={}">➕ बिल बनाउनुहोस्</a>', obj.pk)
    create_bill_button.short_description = 'बिल कार्य'


class TravelBillItemInline(admin.TabularInline):
    model = TravelBillItem
    extra = 1
    fields = (
        'departure_place', 'departure_date', 
        'arrival_place', 'arrival_date', 
        'transport_medium', 'transport_fare', 
        'daily_allowance_days', 'daily_allowance_rate', 'daily_allowance_total', 
        'misc_desc', 'misc_amount', 
        'row_total', 'remarks'
    )


@admin.register(TravelBill)
class TravelBillAdmin(BaseAdminMedia):
    list_display = ('id', 'get_person', 'get_order_no', 'total_transport', 'total_daily_allowance', 'grand_total', 'net_payable', 'print_button', 'nivedan_button')
    list_filter = ('created_at',)
    search_fields = ('travel_order__person', 'travel_order__order_number', 'report_reg_no')
    inlines = [TravelBillItemInline]
    fieldsets = (
        ('१. भ्रमण आदेश तथा कर्मचारी जानकारी', {
            'fields': ('travel_order', 'bill_date', 'address', 'report_reg_no', 'receipt_count')
        }),
        ('२. खर्च तथा भुक्तानी सारांश (Automatic Calculations)', {
            'fields': ('total_transport', 'total_daily_allowance', 'total_misc', 'grand_total', 'advance_taken', 'net_payable', 'amount_in_words')
        }),
    )

    def get_person(self, obj):
        return obj.travel_order.person if obj.travel_order else '-'
    get_person.short_description = 'कर्मचारी'

    def get_order_no(self, obj):
        return obj.travel_order.order_number if obj.travel_order else '-'
    get_order_no.short_description = 'आदेश नं'

    def print_button(self, obj):
        return format_html('<a class="button" style="background:#0284c7; color:white; padding:4px 8px; border-radius:4px; text-decoration:none;" href="/bill/{}/" target="_blank">🖨️ बिल (म.ले.प. २२४)</a>', obj.pk)
    print_button.short_description = 'बिल प्रिन्ट'

    def nivedan_button(self, obj):
        return format_html('<a class="button" style="background:#0d9488; color:white; padding:4px 8px; border-radius:4px; text-decoration:none;" href="/bill/{}/nivedan/" target="_blank">📝 भुक्तानी निवेदन</a>', obj.pk)
    nivedan_button.short_description = 'भुक्तानी निवेदन'

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.update_totals()


@admin.register(TravelReport)
class TravelReportAdmin(BaseAdminMedia):
    list_display = ('id', 'get_person', 'get_order_no', 'report_date', 'report_reg_no', 'print_button')
    search_fields = ('travel_order__person', 'travel_order__order_number', 'report_reg_no')
    list_filter = ('report_date', 'created_at')

    def get_person(self, obj):
        return obj.travel_order.person if obj.travel_order else '-'
    get_person.short_description = 'कर्मचारी'

    def get_order_no(self, obj):
        return obj.travel_order.order_number if obj.travel_order else '-'
    get_order_no.short_description = 'भ्रमण आदेश नं'

    def print_button(self, obj):
        return format_html('<a class="button" style="background:#7c3aed; color:white; padding:4px 8px; border-radius:4px; text-decoration:none;" href="/report/{}/" target="_blank">🖨️ प्रतिवेदन प्रिन्ट</a>', obj.pk)
    print_button.short_description = 'प्रतिवेदन प्रिन्ट'