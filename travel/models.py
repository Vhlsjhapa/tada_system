import re
from django.db import models, transaction
from django.db.models import Q
from django.contrib.auth.models import User
from .bs_calendar import (
    get_bs_duration_days, 
    calculate_tada_allowance_days, 
    to_nepali_digits, 
    to_english_digits,
    get_fiscal_year_from_bs_date,
    get_today_bs
)


def normalize_nepali_fiscal_year(fy_str):
    if not fy_str:
        return get_fiscal_year_from_bs_date(get_today_bs()) or "२०८३/८४"
    eng = to_english_digits(str(fy_str).strip())
    eng = eng.replace('-', '/').replace('.', '/')
    parts = eng.split('/')
    if len(parts) >= 2:
        return f"{to_nepali_digits(parts[0])}/{to_nepali_digits(parts[1])}"
    return str(fy_str).strip()

class Office(models.Model):
    name = models.CharField(max_length=255, verbose_name="कार्यालयको नाम (Office Name)")
    parent_body_1 = models.CharField(
        max_length=255, 
        default="कोशी प्रदेश सरकार", 
        verbose_name="प्रदेश / संघीय सरकार (Level 1)",
        blank=True,
        null=True
    )
    parent_body_2 = models.CharField(
        max_length=255, 
        default="उद्योग, कृषि तथा सहकारी मन्त्रालय", 
        verbose_name="मन्त्रालय (Ministry - Level 2)",
        blank=True,
        null=True
    )
    parent_body_3 = models.CharField(
        max_length=255, 
        default="पशुपन्छी तथा मत्स्य विकास निर्देशनालय", 
        verbose_name="विभाग / निर्देशनालय (Department/Directorate - Level 3)",
        blank=True,
        null=True
    )
    office_code = models.CharField(
        max_length=50, 
        default="३१२०२१२०११", 
        verbose_name="कार्यालय कोड नं. (Office Code)",
        blank=True,
        null=True
    )
    location = models.CharField(
        max_length=255, 
        default="भद्रपुर, झापा", 
        verbose_name="ठेगाना / जिल्ला (Location)",
        blank=True,
        null=True
    )
    head_title = models.CharField(
        max_length=100, 
        default="कार्यालय प्रमुख", 
        verbose_name="कार्यालय प्रमुखको पद (Head Designation)",
        help_text="जस्तै: कार्यालय प्रमुख, प्रमुख प्रशासकीय अधिकृत, आयोजना प्रमुख, महानिर्देशक"
    )
    phone_no = models.CharField(max_length=50, verbose_name="फोन नं.", blank=True, null=True)
    email = models.EmailField(verbose_name="इमेल", blank=True, null=True)
    is_default = models.BooleanField(
        default=False, 
        verbose_name="सक्रिय / पूर्वनिर्धारित कार्यालय (Active/Default Office)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="सिर्जना मिति")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="अद्यावधिक मिति")

    class Meta:
        verbose_name = "कार्यालय (Office)"
        verbose_name_plural = "कार्यालयहरूको व्यवस्थापन (Offices)"
        ordering = ['-is_default', 'name']

    def __str__(self):
        star = "★ [सक्रिय] " if self.is_default else ""
        return f"{star}{self.name} ({self.location or ''})"

    def save(self, *args, **kwargs):
        if self.is_default:
            Office.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_default_office(cls):
        default_off = cls.objects.filter(is_default=True).first()
        if not default_off:
            default_off = cls.objects.first()
        if not default_off:
            # Create default office if none exists
            default_off = cls.objects.create(
                name="भेटेरिनरी अस्पताल तथा पशु सेवा विज्ञ केन्द्र, भद्रपुर झापा",
                parent_body_1="कोशी प्रदेश सरकार",
                parent_body_2="उद्योग, कृषि तथा सहकारी मन्त्रालय",
                parent_body_3="पशुपन्छी तथा मत्स्य विकास निर्देशनालय",
                office_code="३१२०२१२०११",
                location="भद्रपुर, झापा",
                head_title="कार्यालय प्रमुख",
                is_default=True
            )
        return default_off


class FiscalYearSequence(models.Model):
    fiscal_year = models.CharField(max_length=20, verbose_name="आर्थिक वर्ष")
    office_ref = models.ForeignKey(
        Office,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="कार्यालय"
    )
    last_number = models.PositiveIntegerField(default=0, verbose_name="पछिल्लो आदेश नं.")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "आर्थिक वर्ष आदेश क्रम संख्या (Sequence)"
        verbose_name_plural = "आदेश क्रम संख्याहरू"
        unique_together = ('fiscal_year', 'office_ref')

    def __str__(self):
        return f"{self.fiscal_year} ({self.office_ref.name if self.office_ref else 'All'}) - Last: {self.last_number}"


class Employee(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_profile',
        verbose_name="युजर खाता (User Account)"
    )
    office_ref = models.ForeignKey(
        Office, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="सम्बन्धित कार्यालय (Office)"
    )
    name = models.CharField(max_length=100, verbose_name="कर्मचारीको नामथर")
    code_no = models.CharField(max_length=50, verbose_name="कर्मचारी संकेत नं", unique=True)
    designation = models.CharField(max_length=100, verbose_name="पद")
    level = models.CharField(max_length=100, verbose_name="तह / श्रेणी", blank=True, null=True)
    daily_allowance_rate = models.PositiveIntegerField(
        default=1600, 
        verbose_name="दैनिक भत्ता दर (रु.)", 
        help_text="कर्मचारीको तह अनुसार तोकिएको प्रतिदिन भ्रमण भत्ता दर"
    )
    office = models.CharField(
        max_length=255, 
        default="भेटेरिनरी अस्पताल तथा पशु सेवा विज्ञ केन्द्र, भद्रपुर झापा", 
        verbose_name="कार्यालयको नाम"
    )
    permanent_address = models.CharField(max_length=255, verbose_name="स्थायी ठेगाना", blank=True, null=True)
    mobile_no = models.CharField(max_length=20, verbose_name="सम्पर्क नं", blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="सक्रिय स्थिति")

    class Meta:
        verbose_name = "कर्मचारी विवरण"
        verbose_name_plural = "कर्मचारीहरूको सूची"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (संकेत नं: {self.code_no}) - {self.designation}"

    def save(self, *args, **kwargs):
        if not self.office_ref:
            self.office_ref = Office.get_default_office()
        if self.office_ref and not self.office:
            self.office = self.office_ref.name
        super().save(*args, **kwargs)


class TravelOrder(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'पेश भएको (विचाराधीन)'),
        ('RECOMMENDED', 'सिफारिस गरिएको'),
        ('APPROVED', 'स्वीकृत'),
        ('FINANCE_CLEARED', 'लेखाबाट फछ्र्यौट भएको'),
        ('REGISTERED', 'दर्ता भई अन्तिम भएको'),
        ('REJECTED', 'अस्वीकृत / फिर्ता'),
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_travel_orders',
        verbose_name="सिर्जना गर्ने युजर (Created By)"
    )
    office_ref = models.ForeignKey(
        Office, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="सम्बन्धित कार्यालय (Office)"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='REGISTERED', 
        db_index=True, 
        verbose_name="आदेश स्थिति"
    )
    recommended_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='recommended_travel_orders', 
        verbose_name="सिफारिस गर्ने"
    )
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_travel_orders', 
        verbose_name="स्वीकृत गर्ने"
    )
    order_number = models.CharField(max_length=50, verbose_name="आदेश नं", blank=True)
    order_date = models.CharField(max_length=50, verbose_name="आदेश मिति", default="२०८३/०४/२५")
    fiscal_year = models.CharField(max_length=20, verbose_name="आर्थिक वर्ष", default="२०८३/८४")
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="कर्मचारी छान्नुहोस् (Employee)"
    )
    person = models.CharField(max_length=100, verbose_name="कर्मचारीको नामथर")
    code_no = models.CharField(max_length=50, verbose_name="कर्मचारी संकेत नं", blank=True, null=True)
    designation = models.CharField(max_length=100, verbose_name="पद", blank=True, null=True)
    office = models.CharField(
        max_length=255, 
        default="भेटेरिनरी अस्पताल तथा पशु सेवा विज्ञ केन्द्र, भद्रपुर झापा", 
        verbose_name="कार्यालय"
    )
    destination = models.CharField(max_length=255, verbose_name="भ्रमण गर्ने स्थान")
    purpose = models.CharField(max_length=255, verbose_name="भ्रमणको उद्देश्य", default="तोकिएको सरकारी कामकाज")
    start_date = models.CharField(max_length=50, verbose_name="भ्रमण अवधि शुरु मिति")
    end_date = models.CharField(max_length=50, verbose_name="भ्रमण अवधि अन्त्य मिति")
    
    # साधनहरू (Vehicles)
    vehicle_office = models.BooleanField(default=False, verbose_name="साधन: कार्यालयको")
    vehicle_public = models.BooleanField(default=True, verbose_name="साधन: सार्वजनिक")
    vehicle_rent = models.BooleanField(default=False, verbose_name="साधन: भाडाको")
    
    advance_amount = models.CharField(max_length=50, verbose_name="पेस्की रकम (रु.)", blank=True, null=True)
    advance_words = models.CharField(max_length=255, verbose_name="पेस्की रकम अक्षरमा", blank=True, null=True)
    other_details = models.TextField(verbose_name="भ्रमण सम्बन्धी अन्य आवश्यक विवरण", blank=True, null=True)
    program_name = models.CharField(max_length=255, verbose_name="खर्च जनाउने कार्यक्रम/आयोजनाको नाम", blank=True, null=True)
    
    # दस्तखत तथा शाखा मितिहरू (Signature & Admin Dates)
    traveller_date = models.CharField(max_length=50, verbose_name="भ्रमण गर्ने पदाधिकारीको मिति", blank=True, null=True)
    recommender_date = models.CharField(max_length=50, verbose_name="सिफारिस गर्ने पदाधिकारीको मिति", blank=True, null=True)
    approver_date = models.CharField(max_length=50, verbose_name="भ्रमण स्वीकृत गर्ने पदाधिकारीको मिति", blank=True, null=True)
    admin_date = models.CharField(max_length=50, verbose_name="हाजिरी खातामा जनाएको मिति", blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="सिर्जना मिति")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="अद्यावधिक मिति")

    class Meta:
        verbose_name = "राष्ट्रिय भ्रमण आदेश (म.ले.प. २२३)"
        verbose_name_plural = "राष्ट्रिय भ्रमण आदेशहरू"
        ordering = ['-id']

    def __str__(self):
        num_str = self.order_number or "दर्ता बाँकी"
        return f"आदेश नं: {num_str} | {self.person} ({self.destination})"

    @classmethod
    def peek_next_order_number(cls, fiscal_year=None, office_ref=None):
        """Preview next order number (non-locking) for UI display."""
        fy = normalize_nepali_fiscal_year(fiscal_year)
        seq = FiscalYearSequence.objects.filter(fiscal_year=fy, office_ref=office_ref).first()
        current_max = seq.last_number if seq else 0

        # Also check existing TravelOrders in case sequence table isn't initialized yet
        orders = cls.objects.filter(
            Q(fiscal_year=fy) | Q(fiscal_year=to_english_digits(fy))
        )
        if office_ref:
            orders = orders.filter(office_ref=office_ref)
        
        for o in orders:
            if o.order_number:
                eng_digits = re.findall(r'\d+', to_english_digits(str(o.order_number)))
                if eng_digits:
                    try:
                        num = int(eng_digits[0])
                        if num > current_max:
                            current_max = num
                    except ValueError:
                        pass
        
        next_num = current_max + 1
        return to_nepali_digits(f"{next_num:03d}")

    @classmethod
    def allocate_next_order_number(cls, fiscal_year=None, office_ref=None):
        """
        Concurrency-safe allocation of next order number.
        Uses database row-level locking (select_for_update) inside an atomic transaction
        with automatic retry backoff for high concurrency.
        """
        import time
        fy = normalize_nepali_fiscal_year(fiscal_year)
        max_retries = 10

        for attempt in range(max_retries):
            try:
                with transaction.atomic():
                    seq, created = FiscalYearSequence.objects.select_for_update().get_or_create(
                        fiscal_year=fy,
                        office_ref=office_ref,
                        defaults={'last_number': 0}
                    )
                    
                    # Always synchronize seq.last_number with actual max_in_db from active orders
                    orders = cls.objects.filter(
                        Q(fiscal_year=fy) | Q(fiscal_year=to_english_digits(fy))
                    )
                    if office_ref:
                        orders = orders.filter(office_ref=office_ref)
                    
                    max_in_db = 0
                    for o in orders:
                        if o.order_number:
                            eng_digits = re.findall(r'\d+', to_english_digits(str(o.order_number)))
                            if eng_digits:
                                try:
                                    num = int(eng_digits[0])
                                    if num > max_in_db:
                                        max_in_db = num
                                except ValueError:
                                    pass
                    
                    seq.last_number = max_in_db
                    seq.last_number += 1
                    seq.save(update_fields=['last_number', 'updated_at'])
                    return to_nepali_digits(f"{seq.last_number:03d}")
            except Exception as e:
                if attempt < max_retries - 1 and "locked" in str(e).lower():
                    time.sleep(0.05 * (attempt + 1))
                    continue
                raise e

    @property
    def parent_body_1(self):
        if self.office_ref and self.office_ref.parent_body_1:
            return self.office_ref.parent_body_1
        return "कोशी प्रदेश सरकार"

    @property
    def parent_body_2(self):
        if self.office_ref and self.office_ref.parent_body_2:
            return self.office_ref.parent_body_2
        return "उद्योग, कृषि तथा सहकारी मन्त्रालय"

    @property
    def parent_body_3(self):
        if self.office_ref and self.office_ref.parent_body_3:
            return self.office_ref.parent_body_3
        return "पशुपन्छी तथा मत्स्य विकास निर्देशनालय"

    @property
    def office_name(self):
        if self.office_ref:
            return self.office_ref.name
        return self.office or "भेटेरिनरी अस्पताल तथा पशु सेवा विज्ञ केन्द्र, भद्रपुर झापा"

    @property
    def office_code(self):
        if self.office_ref and self.office_ref.office_code:
            return self.office_ref.office_code
        return "३१२०२१२०११"

    @property
    def office_location(self):
        if self.office_ref and self.office_ref.location:
            return self.office_ref.location
        return "भद्रपुर, झापा"

    @property
    def head_title(self):
        if self.office_ref and self.office_ref.head_title:
            return self.office_ref.head_title
        return "कार्यालय प्रमुख"

    @property
    def is_office_vehicle_only(self):
        """Returns True only when office vehicle is selected exclusively without public or rental vehicle."""
        return bool(self.vehicle_office and not self.vehicle_public and not self.vehicle_rent)

    @property
    def duration_days(self):
        """Returns total duration days between start_date and end_date."""
        return get_bs_duration_days(self.start_date, self.end_date) or 1

    @property
    def duration_days_nepali(self):
        """Returns duration days in Nepali Devanagari numerals."""
        return to_nepali_digits(self.duration_days)

    @property
    def vehicle_display(self):
        """Returns a comma-separated list of vehicle types selected."""
        vehicles = []
        if self.vehicle_office:
            vehicles.append("कार्यालयको")
        if self.vehicle_public:
            vehicles.append("सार्वजनिक")
        if self.vehicle_rent:
            vehicles.append("भाडाको")
        return ", ".join(vehicles) if vehicles else "सार्वजनिक"

    @property
    def effective_fiscal_year(self):
        """Returns the effective Nepali fiscal year based on fiscal_year field or order_date/start_date."""
        if self.fiscal_year and len(self.fiscal_year.strip()) >= 5 and '/' in self.fiscal_year:
            return self.fiscal_year.strip()
        if self.order_date:
            fy = get_fiscal_year_from_bs_date(self.order_date)
            if fy:
                return fy
        if self.start_date:
            fy = get_fiscal_year_from_bs_date(self.start_date)
            if fy:
                return fy
        return "२०८३/८४"

    def save(self, *args, **kwargs):
        # Auto-derive or align fiscal_year with order_date if fiscal_year is default or empty
        if self.order_date:
            derived_fy = get_fiscal_year_from_bs_date(self.order_date)
            if derived_fy and (not self.fiscal_year or self.fiscal_year in ['२०८२/८३', '2082/83', '']):
                # If the order_date falls in a different FY than default, use the derived FY
                self.fiscal_year = derived_fy
        elif self.start_date:
            derived_fy = get_fiscal_year_from_bs_date(self.start_date)
            if derived_fy and not self.fiscal_year:
                self.fiscal_year = derived_fy

        self.fiscal_year = normalize_nepali_fiscal_year(self.fiscal_year)

        if not self.office_ref:
            if self.employee and self.employee.office_ref:
                self.office_ref = self.employee.office_ref
            else:
                self.office_ref = Office.get_default_office()

        if self.employee:
            if not self.created_by and self.employee.user:
                self.created_by = self.employee.user
            if not self.person:
                self.person = self.employee.name
            if not self.code_no:
                self.code_no = self.employee.code_no
            if not self.designation:
                self.designation = self.employee.designation
            if not self.office:
                self.office = self.employee.office or (self.office_ref.name if self.office_ref else '')
        elif self.office_ref and not self.office:
            self.office = self.office_ref.name

        # Auto-generate order_number only when status is REGISTERED or if order_number was explicitly provided
        if self.status == 'REGISTERED':
            if not self.order_number or not str(self.order_number).strip():
                self.order_number = TravelOrder.allocate_next_order_number(
                    fiscal_year=self.fiscal_year,
                    office_ref=self.office_ref
                )
            else:
                # Sync FiscalYearSequence if user manually entered a higher number
                eng_digits = re.findall(r'\d+', to_english_digits(str(self.order_number)))
                if eng_digits:
                    try:
                        manual_num = int(eng_digits[0])
                        seq, _ = FiscalYearSequence.objects.get_or_create(
                            fiscal_year=self.fiscal_year,
                            office_ref=self.office_ref,
                            defaults={'last_number': 0}
                        )
                        if manual_num > seq.last_number:
                            seq.last_number = manual_num
                            seq.save(update_fields=['last_number', 'updated_at'])
                    except Exception:
                        pass
        else:
            # In preliminary workflow stages (PENDING/RECOMMENDED/APPROVED/REJECTED), keep order_number blank if not set
            if not self.order_number:
                self.order_number = ""

        super().save(*args, **kwargs)



class TravelBill(models.Model):
    PAYING_AGENCY_CHOICES = (
        ('INTERNAL', 'यसै कार्यालयको बजेटबाट भुक्तानी'),
        ('EXTERNAL', 'अन्य सरकारी निकाय / बाह्य स्रोतबाट भुक्तानी'),
    )

    travel_order = models.OneToOneField(
        TravelOrder, 
        on_delete=models.CASCADE, 
        verbose_name="भ्रमण आदेश छान्नुहोस्", 
        related_name="bill",
        null=True, 
        blank=True
    )
    paying_agency_type = models.CharField(
        max_length=20, 
        choices=PAYING_AGENCY_CHOICES, 
        default='INTERNAL', 
        db_index=True, 
        verbose_name="भुक्तानी गर्ने निकाय"
    )
    external_agency_name = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="बाह्य निकायको नाम"
    )
    bill_date = models.CharField(max_length=50, verbose_name="बिल पेश मिति", blank=True, null=True)
    address = models.CharField(max_length=255, verbose_name="कर्मचारीको स्थायी ठेगाना", blank=True, null=True)
    report_reg_no = models.CharField(max_length=50, verbose_name="भ्रमण प्रतिवेदन दर्ता नं", blank=True, null=True)
    receipt_count = models.CharField(max_length=50, verbose_name="नत्थी रसिद/बिल संख्या", blank=True, null=True)
    
    # खर्चको विवरण (Summary)
    total_transport = models.IntegerField(default=0, verbose_name="१. भ्रमण/यातायात खर्च (रु.)")
    total_daily_allowance = models.IntegerField(default=0, verbose_name="२. दैनिक भत्ता (रु.)")
    total_misc = models.IntegerField(default=0, verbose_name="४. फुटकर खर्च (रु.)")
    grand_total = models.IntegerField(default=0, verbose_name="५. कुल जम्मा (रु.)")
    advance_taken = models.IntegerField(default=0, verbose_name="६. भ्रमण पेस्की (रु.)")
    net_payable = models.IntegerField(default=0, verbose_name="७. खुद भुक्तानी पाउने/बुझाउने रकम (रु.)")
    amount_in_words = models.CharField(max_length=255, verbose_name="खुद रकम अक्षरमा", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "दैनिक तथा भ्रमण खर्चको बिल (म.ले.प. २२४)"
        verbose_name_plural = "दैनिक तथा भ्रमण खर्चका बिलहरू"
        ordering = ['-id']

    def __str__(self):
        if self.travel_order:
            return f"बिल - {self.travel_order.person} (आदेश नं: {self.travel_order.order_number})"
        return f"बिल #{self.id}"

    @property
    def employee_code_no(self):
        if self.travel_order:
            if self.travel_order.code_no:
                return self.travel_order.code_no
            if self.travel_order.employee and self.travel_order.employee.code_no:
                return self.travel_order.employee.code_no
            emp = Employee.objects.filter(name=self.travel_order.person).first()
            if emp and emp.code_no:
                return emp.code_no
        return ""

    @property
    def employee_designation(self):
        if self.travel_order:
            if self.travel_order.designation:
                return self.travel_order.designation
            if self.travel_order.employee and self.travel_order.employee.designation:
                return self.travel_order.employee.designation
            emp = Employee.objects.filter(name=self.travel_order.person).first()
            if emp and emp.designation:
                return emp.designation
        return ""

    @property
    def employee_permanent_address(self):
        default_off = Office.get_default_office()
        office_name = default_off.name if default_off else ""
        if self.address and self.address != office_name:
            return self.address
        if self.travel_order:
            if self.travel_order.employee and self.travel_order.employee.permanent_address:
                return self.travel_order.employee.permanent_address
            emp = Employee.objects.filter(name=self.travel_order.person).first()
            if emp and emp.permanent_address:
                return emp.permanent_address
        return ""

    @property
    def final_report_reg_no(self):
        if self.report_reg_no:
            return self.report_reg_no
        if self.travel_order and hasattr(self.travel_order, 'report') and self.travel_order.report and self.travel_order.report.report_reg_no:
            return self.travel_order.report.report_reg_no
        return ""

    def save(self, *args, **kwargs):
        default_off = Office.get_default_office()
        office_name = default_off.name if default_off else ""
        if self.travel_order and (not self.address or self.address == office_name):
            if self.travel_order.employee and self.travel_order.employee.permanent_address:
                self.address = self.travel_order.employee.permanent_address
            else:
                emp = Employee.objects.filter(name=self.travel_order.person).first()
                if emp and emp.permanent_address:
                    self.address = emp.permanent_address
        
        # Auto-fill report registration number from report, or fallback to travel order's order_number
        if not self.report_reg_no and self.travel_order:
            if hasattr(self.travel_order, 'report') and self.travel_order.report and self.travel_order.report.report_reg_no:
                self.report_reg_no = self.travel_order.report.report_reg_no
            elif self.travel_order.order_number:
                self.report_reg_no = self.travel_order.order_number

        super().save(*args, **kwargs)

    def update_totals(self):
        items = self.items.all()
        is_office_veh_only = bool(self.travel_order and self.travel_order.is_office_vehicle_only)
        t_trans = 0
        t_daily = 0
        t_misc = 0
        for i in items:
            if is_office_veh_only:
                i.transport_fare = 0
                if not i.transport_medium or i.transport_medium == "सार्वजनिक सवारी":
                    i.transport_medium = "कार्यालयको सवारी"
            i.daily_allowance_total = int(round((i.daily_allowance_days or 0) * (i.daily_allowance_rate or 0)))
            i.row_total = (i.transport_fare or 0) + i.daily_allowance_total + (i.misc_amount or 0)
            i.save(update_fields=['transport_fare', 'transport_medium', 'daily_allowance_total', 'row_total'])
            t_trans += i.transport_fare
            t_daily += i.daily_allowance_total
            t_misc += (i.misc_amount or 0)
            
        g_total = t_trans + t_daily + t_misc
        
        self.total_transport = t_trans
        self.total_daily_allowance = t_daily
        self.total_misc = t_misc
        self.grand_total = g_total
        
        adv = self.advance_taken or 0
        self.net_payable = g_total - adv
        self.save(update_fields=['total_transport', 'total_daily_allowance', 'total_misc', 'grand_total', 'net_payable', 'address'])


class TravelBillItem(models.Model):
    travel_bill = models.ForeignKey(
        TravelBill, 
        related_name="items", 
        on_delete=models.CASCADE, 
        verbose_name="बिल"
    )
    # प्रस्थान
    departure_place = models.CharField(max_length=100, verbose_name="प्रस्थान स्थान (महल १)", default="झापा")
    departure_date = models.CharField(max_length=50, verbose_name="प्रस्थान मिति (महल २)", blank=True, null=True)
    departure_time = models.CharField(max_length=20, verbose_name="प्रस्थान समय", blank=True, null=True)
    
    # आगमन
    arrival_place = models.CharField(max_length=100, verbose_name="आगमन स्थान (महल ३)", blank=True, null=True)
    arrival_date = models.CharField(max_length=50, verbose_name="आगमन मिति (महल ४)", blank=True, null=True)
    arrival_time = models.CharField(max_length=20, verbose_name="आगमन समय", blank=True, null=True)
    
    # साधन र खर्च
    transport_medium = models.CharField(max_length=100, verbose_name="भ्रमणको साधन (महल ५)", default="सार्वजनिक सवारी", blank=True, null=True)
    transport_fare = models.IntegerField(default=0, verbose_name="यातायात खर्च रू (महल ६)")
    
    # दैनिक भत्ता
    daily_allowance_days = models.FloatField(default=1.0, verbose_name="दैनिक भत्ता दिन (महल ७)")
    daily_allowance_rate = models.IntegerField(default=0, verbose_name="दैनिक भत्ता दर (महल ८)")
    daily_allowance_total = models.IntegerField(default=0, verbose_name="दैनिक भत्ता जम्मा रू (महल ९)")
    
    # फुटकर खर्च
    misc_desc = models.CharField(max_length=255, verbose_name="फुटकर खर्च विवरण (महल १०)", blank=True, null=True)
    misc_amount = models.IntegerField(default=0, verbose_name="फुटकर खर्च जम्मा रू (महल ११)")
    
    # कुल जम्मा र कैफियत
    row_total = models.IntegerField(default=0, verbose_name="कुल जम्मा रू (महल १२)")
    remarks = models.CharField(max_length=255, verbose_name="कैफियत (महल १३)", blank=True, null=True)

    class Meta:
        verbose_name = "भ्रमण बिल खर्च पंक्ति (महल १ देखि १३)"
        verbose_name_plural = "भ्रमण बिल खर्च पंक्तिहरू"

    @property
    def get_daily_allowance_total(self):
        if self.daily_allowance_total is not None and self.daily_allowance_total > 0:
            return self.daily_allowance_total
        return int(round((self.daily_allowance_days or 0) * (self.daily_allowance_rate or 0)))

    @property
    def get_row_total(self):
        if self.row_total is not None and self.row_total > 0:
            return self.row_total
        fare = 0 if (self.travel_bill and self.travel_bill.travel_order and self.travel_bill.travel_order.is_office_vehicle_only) else (self.transport_fare or 0)
        return fare + self.get_daily_allowance_total + (self.misc_amount or 0)

    def save(self, *args, **kwargs):
        if self.travel_bill and self.travel_bill.travel_order and self.travel_bill.travel_order.is_office_vehicle_only:
            self.transport_fare = 0
            if not self.transport_medium or self.transport_medium == "सार्वजनिक सवारी":
                self.transport_medium = "कार्यालयको सवारी"
        self.daily_allowance_total = int(round((self.daily_allowance_days or 0) * (self.daily_allowance_rate or 0)))
        self.row_total = (self.transport_fare or 0) + self.daily_allowance_total + (self.misc_amount or 0)
        super().save(*args, **kwargs)


class TravelReport(models.Model):
    travel_order = models.OneToOneField(
        TravelOrder, 
        on_delete=models.CASCADE, 
        verbose_name="भ्रमण आदेश छान्नुहोस्",
        related_name="report"
    )
    report_date = models.CharField(max_length=50, verbose_name="प्रतिवेदन पेश गरेको मिति", default="२०८३/०४/२५")
    report_reg_no = models.CharField(max_length=50, verbose_name="प्रतिवेदन दर्ता नं", blank=True, null=True)
    
    key_activities = models.TextField(verbose_name="१. सम्पादित मुख्य कार्यहरू (Key Activities)")
    achievements = models.TextField(verbose_name="२. हासिल भएका मुख्य उपलब्धिहरू (Achievements)")
    challenges = models.TextField(verbose_name="३. देखिएका समस्या तथा चुनौतीहरू (Challenges)", blank=True, null=True)
    recommendations = models.TextField(verbose_name="४. निष्कर्ष तथा सुझावहरू (Recommendations)")
    
    submitted_by = models.CharField(max_length=100, verbose_name="प्रतिवेदन पेश गर्ने कर्मचारीको नाम", blank=True, null=True)
    submitted_designation = models.CharField(max_length=100, verbose_name="पद", blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="सिर्जना मिति")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="अद्यावधिक मिति")

    class Meta:
        verbose_name = "भ्रमण सम्पन्न प्रतिवेदन (Travel Completion Report)"
        verbose_name_plural = "भ्रमण सम्पन्न प्रतिवेदनहरू"
        ordering = ['-id']

    def __str__(self):
        return f"प्रतिवेदन - {self.travel_order.person} (आदेश नं: {self.travel_order.order_number})"

    def save(self, *args, **kwargs):
        # Auto-fill report_reg_no from linked TravelOrder's order_number if empty
        if not self.report_reg_no and self.travel_order and self.travel_order.order_number:
            self.report_reg_no = self.travel_order.order_number

        # Auto-fill submitted_by / designation from travel_order if empty
        if self.travel_order:
            if not self.submitted_by:
                self.submitted_by = self.travel_order.person
            if not self.submitted_designation:
                self.submitted_designation = self.travel_order.designation

        super().save(*args, **kwargs)

        # Also sync to linked TravelBill if it exists and bill doesn't have a report_reg_no
        if self.travel_order and hasattr(self.travel_order, 'bill') and self.travel_order.bill:
            bill = self.travel_order.bill
            if not bill.report_reg_no or bill.report_reg_no != self.report_reg_no:
                bill.report_reg_no = self.report_reg_no
                bill.save(update_fields=['report_reg_no'])