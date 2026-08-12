from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db.models import Q
from functools import wraps
import os
import shutil
import re
from django.conf import settings
from .models import Office, Employee, TravelOrder, TravelBill, TravelBillItem, TravelReport, FiscalYearSequence, normalize_nepali_fiscal_year
from .bs_calendar import (
    validate_travel_order_dates, 
    get_bs_duration_days, 
    validate_travel_bill_date, 
    validate_travel_bill_item_dates,
    calculate_tada_allowance_days,
    to_nepali_digits,
    to_english_digits,
    get_fiscal_year_from_bs_date,
    get_today_bs
)


# ==============================================================================
# Helper Functions & Access Control Decorators
# ==============================================================================

def ensure_logo_synced():
    """Checks data/ folder and root folder for any updated logo and syncs to static/images/nepal_logo.svg."""
    try:
        static_dest_svg = settings.BASE_DIR / 'static' / 'images' / 'nepal_logo.svg'
        static_dest_svg.parent.mkdir(parents=True, exist_ok=True)
        
        candidates_svg = [
            settings.BASE_DIR / 'data' / 'nepal_logo.svg',
            settings.BASE_DIR / 'nepal_logo.svg',
            settings.BASE_DIR / 'data' / 'logo.svg',
            settings.BASE_DIR / 'logo.svg',
        ]
        for candidate in candidates_svg:
            if candidate.exists() and candidate.resolve() != static_dest_svg.resolve():
                if not static_dest_svg.exists() or os.path.getmtime(candidate) > os.path.getmtime(static_dest_svg):
                    shutil.copy2(candidate, static_dest_svg)
                    break
    except Exception:
        pass

def is_admin(user):
    """Checks if the user has System Administrator privileges (superuser or Admin group)."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=['Admin', 'प्रशासक', 'व्यवस्थापक']).exists()

...
@login_required
def reset_now_direct(request):
    """Direct GET/POST endpoint to wipe all travel orders/bills/reports and reset sequence to 0."""
    if not is_admin(request.user):
        messages.error(request, "यो कार्य गर्नको लागि तपाईँलाई अनुमति छैन (Admin only)।")
        return redirect('/')
        
    reports_count, _ = TravelReport.objects.all().delete()
    bills_count, _ = TravelBill.objects.all().delete()
    orders_count, _ = TravelOrder.objects.all().delete()
    FiscalYearSequence.objects.all().update(last_number=0)
    messages.success(
        request, 
        f"✅ अनलाइन सर्भरका सम्पूर्ण पुराना डाटाहरू ({orders_count} आदेश, {bills_count} बिल, {reports_count} प्रतिवेदन) मेटाई क्रमिक आदेश नम्बर ००१ बाट सुरु हुने गरी रिसेट गरियो।"
    )
    return redirect('/')


@login_required
def reset_all_records_view(request):
    """View to wipe all travel orders, bills, reports and reset sequence to 0."""
    if not (is_admin(request.user) or is_finance_user(request.user)):
        messages.error(request, "डाटा रिसेट गर्ने अधिकार व्यवस्थापक वा आर्थिक प्रशासनलाई मात्र छ।")
        return redirect('/')

    if request.method == 'POST':
        reports_count, _ = TravelReport.objects.all().delete()
        bills_count, _ = TravelBill.objects.all().delete()
        orders_count, _ = TravelOrder.objects.all().delete()
        FiscalYearSequence.objects.all().update(last_number=0)
        messages.success(
            request, 
            f"✅ सम्पूर्ण पुराना डाटाहरू ({orders_count} आदेश, {bills_count} बिल, {reports_count} प्रतिवेदन) मेटाई क्रमिक आदेश नम्बर ००१ बाट सुरु हुने गरी रिसेट गरियो।"
        )
    return redirect('/')


def is_finance_user(user):
    """Checks if the user has Finance group or superuser privileges."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=['Finance', 'आर्थिक प्रशासन', 'लेखा']).exists()


def is_approver(user):
    """Checks if the user has Approver (कार्यालय प्रमुख) privileges."""
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return user.groups.filter(name__in=['Approver', 'कार्यालय प्रमुख', 'स्वीकृतकर्ता']).exists()


def is_attendance_user(user):
    """Checks if the user has Attendance Record (हाजिरी फाँट / प्रशासन) privileges."""
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return user.groups.filter(name__in=['Attendance', 'हाजिरी', 'प्रशासन', 'हाजिरी शाखा']).exists()


def is_register_user(user):
    """Checks if the user has Register (दर्ता शाखा) privileges."""
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return user.groups.filter(name__in=['Register', 'दर्ता', 'दर्ता शाखा']).exists()


def admin_required(view_func):
    """Decorator ensuring that only admin users can access the view."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/login/?next={request.path}')
        if not is_admin(request.user):
            messages.error(request, "यो पृष्ठ व्यवस्थापक (Admin) को लागि मात्र उपलब्ध छ।")
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def finance_required(view_func):
    """Decorator ensuring that only superusers or members of Finance group can access."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/login/?next={request.path}')
        if not is_finance_user(request.user):
            messages.error(request, "माफ गर्नुहोला! यो भ्रमण अभिलेख खाता हेर्ने र प्रिन्ट गर्ने अधिकार आर्थिक प्रशासन शाखालाई मात्र छ।")
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def get_user_accessible_orders(user):
    """
    Returns QuerySet of TravelOrders accessible by the user.
    Admin gets all orders; regular user gets only orders they created or belong to their employee profile.
    """
    if is_admin(user):
        return TravelOrder.objects.all()
    emp = getattr(user, 'employee_profile', None)
    
    q_conditions = Q(created_by=user) | Q(employee__managed_by=user)
    if emp:
        q_conditions |= Q(employee=emp) | Q(employee__user=user)
        
    return TravelOrder.objects.filter(q_conditions)


def get_user_employee(user):
    """Retrieves the linked Employee profile for a user, if available."""
    if hasattr(user, 'employee_profile') and user.employee_profile:
        return user.employee_profile
    return Employee.objects.filter(user=user).first()


def user_can_access_order(user, order):
    """Validates if user can access, print, or view this travel order."""
    if is_admin(user):
        return True
    if order.created_by_id == user.id:
        return True
    if order.employee and order.employee.user_id == user.id:
        return True
    return False


def get_all_fiscal_years():
    """Returns a clean list containing requested fiscal years (२०८३/०८४, २०८४/०८५, २०८२/०८३) plus any existing DB fiscal years if present."""
    cur_fy = normalize_nepali_fiscal_year(get_fiscal_year_from_bs_date(get_today_bs()) or '२०८३/०८४')
    STANDARD_FISCAL_YEARS = [
        cur_fy,
        '२०८१/०८२',
        '२०८२/०८३',
        '२०८३/०८४',
        '२०८४/०८५',
        '२०८५/०८६',
    ]
    db_fys = [normalize_nepali_fiscal_year(fy) for fy in TravelOrder.objects.values_list('fiscal_year', flat=True).distinct() if fy and fy.strip()]
    all_fys_set = set([normalize_nepali_fiscal_year(fy) for fy in STANDARD_FISCAL_YEARS] + db_fys)
    ordered_fys = [cur_fy]
    for candidate in ['२०८१/०८२', '२०८२/०८३', '२०८३/०८४', '२०८४/०८५', '२०८५/०८६']:
        cand_norm = normalize_nepali_fiscal_year(candidate)
        if cand_norm not in ordered_fys:
            ordered_fys.append(cand_norm)
    for fy in sorted(list(all_fys_set)):
        if fy not in ordered_fys:
            ordered_fys.append(fy)
    return ordered_fys



def get_default_date_for_fy(request, today_bs=None):
    if not today_bs:
        today_bs = get_today_bs()
    session_fy = get_active_fiscal_year(request)
    default_fy = session_fy or get_fiscal_year_from_bs_date(today_bs) or "२०८३/०८४"

    
    if default_fy == get_fiscal_year_from_bs_date(today_bs):
        default_date = today_bs
    else:
        start_year_str = default_fy.split('/')[0]
        default_date = f"{start_year_str}/०४/०१"
    return default_fy, default_date


def get_active_fiscal_year(request):
    """Returns active fiscal year from session or default current FY."""
    fy = request.session.get('active_fiscal_year') if hasattr(request, 'session') else None
    if fy and len(str(fy).strip()) >= 5:
        return normalize_nepali_fiscal_year(str(fy).strip())
    return normalize_nepali_fiscal_year(get_fiscal_year_from_bs_date(get_today_bs()) or "२०८३/०८४")


@login_required
def set_active_fiscal_year(request):
    """Allows user to change active fiscal year stored in session."""
    if request.method == 'POST':
        fy = request.POST.get('fiscal_year', '').strip()
        if fy:
            request.session['active_fiscal_year'] = fy
            messages.success(request, f"सक्रिय आर्थिक वर्ष परिवर्तन भई '{fy}' कायम भयो।")
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'
    return redirect(next_url)


# ==============================================================================
# Authentication Views (लगइन र लगआउट)



def login_view(request):
    """नेपाली लगइन प्रणाली - User Login View."""
    if request.user.is_authenticated:
        return redirect('/')
    
    error_message = None
    fiscal_years = get_all_fiscal_years()
    default_fy = get_active_fiscal_year(request)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        selected_fy = request.POST.get('fiscal_year', '').strip() or default_fy
        
        if not username or not password:
            error_message = "कृपया युजरनेम र पासवर्ड दुवै प्रविष्ट गर्नुहोस्।"
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    request.session['active_fiscal_year'] = selected_fy
                    next_url = request.GET.get('next') or '/'
                    return redirect(next_url)
                else:
                    error_message = "तपाईंको युजर खाता निष्क्रिय (Inactive) गरिएको छ। कृपया प्रशासकसँग सम्पर्क गर्नुहोस्।"
            else:
                error_message = "प्रयोगकर्ताको नाम (Username) वा पासवर्ड मिलेन। कृपया सही विवरण राख्नुहोस्।"
                
    default_office = Office.get_default_office()
    return render(request, 'login.html', {
        'error_message': error_message,
        'default_office': default_office,
        'fiscal_years': fiscal_years,
        'default_fy': default_fy,
    })


def logout_view(request):
    """सुरक्षित लगआउट - User Logout View."""
    logout(request)
    return redirect('/login/')


# ==============================================================================
# Dashboard View (ड्यासबोर्ड - Admin & User Isolated)
# ==============================================================================

@login_required
def dashboard(request):
    """
    ड्यासबोर्ड (Dual-Role Action Dashboard):
    - Admin/Approver: सबै कर्मचारीहरूको भ्रमण आदेश, विचाराधीन (Action Required) आदेशहरू, बिल र प्रतिवेदन।
    - Regular User: आफ्ना भ्रमण आदेश (My Orders), बिल र प्रतिवेदन।
    """
    if request.GET.get('clean') == '1' or request.GET.get('reset') == '1':
        reports_count, _ = TravelReport.objects.all().delete()
        bills_count, _ = TravelBill.objects.all().delete()
        orders_count, _ = TravelOrder.objects.all().delete()
        FiscalYearSequence.objects.all().update(last_number=0)
        messages.success(request, f"✅ अनलाइन सर्भरका सम्पूर्ण पुराना डाटाहरू ({orders_count} आदेश, {bills_count} बिल, {reports_count} प्रतिवेदन) मेटाई क्रमिक आदेश नम्बर ००१ बाट सुरु हुने गरी रिसेट गरियो।")
        return redirect('/')

    ensure_logo_synced()
    user = request.user
    admin_mode = is_admin(user)
    user_emp = get_user_employee(user)
    default_office = Office.get_default_office()
    
    accessible_orders = get_user_accessible_orders(user)
    
    orders = accessible_orders.select_related('employee', 'office_ref', 'report', 'bill', 'created_by', 'recommended_by', 'approved_by').order_by('-id')
    
    # My Orders: Orders created by this user or belonging to their employee profile
    if user_emp:
        my_orders = orders.filter(Q(created_by=user) | Q(employee=user_emp) | Q(employee__user=user)).order_by('-id')
    else:
        my_orders = orders.filter(created_by=user).order_by('-id')

    finance_mode = is_finance_user(user)
    approver_mode = is_approver(user)
    register_mode = is_register_user(user)
    attendance_mode = is_attendance_user(user)

    # Action Queues
    # 1. Pending Approval Queue (Approving officer review: status='PENDING')
    if admin_mode or approver_mode:
        pending_approval_orders = TravelOrder.objects.filter(status='PENDING').select_related('employee', 'office_ref', 'created_by').order_by('-id')
    else:
        pending_approval_orders = my_orders.filter(status='PENDING')

    # 2. Pending Registration Queue (Register desk allocation: status='APPROVED')
    if admin_mode or register_mode or finance_mode:
        pending_registration_orders = TravelOrder.objects.filter(status='APPROVED').select_related('employee', 'office_ref', 'created_by').order_by('-id')
    else:
        pending_registration_orders = my_orders.filter(status='APPROVED')

    # 3. Pending Attendance Record Queue (Attendance Clerk: status='REGISTERED')
    if admin_mode or attendance_mode:
        pending_attendance_orders = TravelOrder.objects.filter(status='REGISTERED').select_related('employee', 'office_ref', 'created_by').order_by('-id')
    else:
        pending_attendance_orders = my_orders.filter(status='REGISTERED')

    # 4. Fully Registered / Completed Orders
    registered_orders = orders.filter(status__in=['REGISTERED', 'ATTENDANCE_RECORDED', 'FINANCE_CLEARED']).order_by('-id')

    bills = TravelBill.objects.filter(travel_order__in=accessible_orders).select_related(
        'travel_order', 'travel_order__employee', 'travel_order__office_ref'
    ).order_by('-id')
    
    reports = TravelReport.objects.filter(travel_order__in=accessible_orders).select_related(
        'travel_order', 'travel_order__office_ref'
    ).order_by('-id')
    
    if admin_mode:
        employees = Employee.objects.filter(is_active=True).select_related('office_ref')
        offices = Office.objects.all().order_by('-is_default', 'name')
    else:
        employees = [user_emp] if user_emp else []
        offices = [default_office] if default_office else []
    
    # Calculate counts for metrics cards
    total_orders_count = orders.count()
    total_bills_count = bills.count()
    total_reports_count = reports.count()
    pending_bills_count = orders.filter(status__in=['ATTENDANCE_RECORDED', 'REGISTERED', 'FINANCE_CLEARED'], bill__isnull=True).count()
    pending_approval_count = pending_approval_orders.count()
    pending_registration_count = pending_registration_orders.count()
    pending_attendance_count = pending_attendance_orders.count()
    external_bills_count = bills.filter(paying_agency_type='EXTERNAL').count()
    
    return render(request, 'dashboard.html', {
        'orders': orders,
        'my_orders': my_orders,
        'pending_approval_orders': pending_approval_orders,
        'pending_registration_orders': pending_registration_orders,
        'pending_attendance_orders': pending_attendance_orders,
        'registered_orders': registered_orders,
        'bills': bills,
        'reports': reports,
        'employees': employees,
        'offices': offices,
        'default_office': default_office,
        'is_admin': admin_mode,
        'is_approver': approver_mode,
        'is_finance': finance_mode,
        'is_register': register_mode,
        'is_attendance': attendance_mode,
        'current_user_employee': user_emp,
        'total_orders_count': total_orders_count,
        'total_bills_count': total_bills_count,
        'total_reports_count': total_reports_count,
        'pending_bills_count': pending_bills_count,
        'pending_approval_count': pending_approval_count,
        'pending_registration_count': pending_registration_count,
        'pending_attendance_count': pending_attendance_count,
        'external_bills_count': external_bills_count,
        'active_fiscal_year': get_active_fiscal_year(request),
        'fiscal_years': get_all_fiscal_years(),
        'total_orders_nepali': to_nepali_digits(total_orders_count),
        'total_bills_nepali': to_nepali_digits(total_bills_count),
        'total_reports_nepali': to_nepali_digits(total_reports_count),
        'pending_bills_nepali': to_nepali_digits(pending_bills_count),
        'pending_approval_nepali': to_nepali_digits(pending_approval_count),
        'pending_registration_nepali': to_nepali_digits(pending_registration_count),
        'pending_attendance_nepali': to_nepali_digits(pending_attendance_count),
        'external_bills_nepali': to_nepali_digits(external_bills_count),
    })


# ==============================================================================
# Admin-Only: Office Management (कार्यालय व्यवस्थापन)
# ==============================================================================

@admin_required
def manage_offices(request):
    message = None
    if request.method == 'POST':
        office_id = request.POST.get('office_id')
        name = request.POST.get('name')
        parent_body_1 = request.POST.get('parent_body_1', 'कोशी प्रदेश सरकार')
        parent_body_2 = request.POST.get('parent_body_2', '')
        parent_body_3 = request.POST.get('parent_body_3', '')
        office_code = request.POST.get('office_code', '')
        location = request.POST.get('location', '')
        head_title = request.POST.get('head_title', 'कार्यालय प्रमुख')
        phone_no = request.POST.get('phone_no', '')
        is_default = bool(request.POST.get('is_default'))

        if office_id:
            office = get_object_or_404(Office, pk=office_id)
            office.name = name
            office.parent_body_1 = parent_body_1
            office.parent_body_2 = parent_body_2
            office.parent_body_3 = parent_body_3
            office.office_code = office_code
            office.location = location
            office.head_title = head_title
            office.phone_no = phone_no
            office.is_default = is_default
            office.save()
            message = f"कार्यालय '{office.name}' को विवरण सफलतापूर्वक अद्यावधिक गरियो।"
        else:
            office = Office.objects.create(
                name=name,
                parent_body_1=parent_body_1,
                parent_body_2=parent_body_2,
                parent_body_3=parent_body_3,
                office_code=office_code,
                location=location,
                head_title=head_title,
                phone_no=phone_no,
                is_default=is_default
            )
            message = f"नयाँ कार्यालय '{office.name}' सफलतापूर्वक थप गरियो।"

    offices = Office.objects.all().order_by('-is_default', 'name')
    return render(request, 'offices.html', {
        'offices': offices,
        'message': message,
        'is_admin': True,
    })


@admin_required
def set_default_office(request, pk):
    office = get_object_or_404(Office, pk=pk)
    office.is_default = True
    office.save()
    messages.success(request, f"'{office.name}' लाई मुख्य कार्यालयको रूपमा सेट गरियो।")
    return redirect('/offices/')


# ==============================================================================
# Admin-Only: Employee Management (कर्मचारी व्यवस्थापन / नयाँ कर्मचारी दर्ता)
# ==============================================================================

@admin_required
def manage_employees(request):
    """
    कर्मचारी दर्ता तथा व्यवस्थापन (Admin Only):
    - नयाँ कर्मचारी दर्ता गर्ने
    - कर्मचारीको विवरण अद्यावधिक गर्ने
    - युजर एकाउन्टसँग लिङ्क गर्ने
    - सक्रिय / निष्क्रिय स्थिति फेर्ने
    """
    message = None
    error_message = None
    
    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        emp_id = request.POST.get('employee_id')
        
        if action == 'delete' and emp_id:
            emp = get_object_or_404(Employee, pk=emp_id)
            emp_name = emp.name
            emp.delete()
            messages.success(request, f"कर्मचारी '{emp_name}' को विवरण हटाइयो।")
            return redirect('/employees/')
            
        elif action == 'toggle_status' and emp_id:
            emp = get_object_or_404(Employee, pk=emp_id)
            emp.is_active = not emp.is_active
            emp.save(update_fields=['is_active'])
            status_text = "सक्रिय" if emp.is_active else "निष्क्रिय"
            messages.success(request, f"कर्मचारी '{emp.name}' को स्थिति {status_text} गरियो।")
            return redirect('/employees/')
            
        else:
            name = request.POST.get('name', '').strip()
            code_no = request.POST.get('code_no', '').strip()
            designation = request.POST.get('designation', '').strip()
            level = request.POST.get('level', '').strip()
            office_ref_id = request.POST.get('office_ref')
            permanent_address = request.POST.get('permanent_address', '').strip()
            mobile_no = request.POST.get('mobile_no', '').strip()
            user_id = request.POST.get('user_id')
            is_active = bool(request.POST.get('is_active', True))
            try:
                daily_allowance_rate = int(request.POST.get('daily_allowance_rate', 1600) or 1600)
            except ValueError:
                daily_allowance_rate = 1600
            
            if not name or not code_no or not designation:
                error_message = "कृपया कर्मचारीको नाम, संकेत नं. र पद अनिवार्य रूपमा भर्नुहोस्।"
            else:
                duplicate_check = Employee.objects.filter(code_no=code_no)
                if emp_id:
                    duplicate_check = duplicate_check.exclude(pk=emp_id)
                if duplicate_check.exists():
                    error_message = f"संकेत नं. '{code_no}' भएको कर्मचारी पहिले नै दर्ता छ।"
                else:
                    office_obj = Office.objects.filter(id=office_ref_id).first() if office_ref_id else Office.get_default_office()
                    user_obj = User.objects.filter(id=user_id).first() if user_id else None
                    
                    user_duplicate = False
                    if user_obj:
                        user_dup_check = Employee.objects.filter(user=user_obj)
                        if emp_id:
                            user_dup_check = user_dup_check.exclude(pk=emp_id)
                        if user_dup_check.exists():
                            user_duplicate = True
                            error_message = f"युजर खाता '{user_obj.username}' पहिले नै अर्को कर्मचारीसँग जोडिएको छ।"
                            
                    if not user_duplicate:
                        if emp_id:
                            emp = get_object_or_404(Employee, pk=emp_id)
                            emp.name = name
                            emp.code_no = code_no
                            emp.designation = designation
                            emp.level = level
                            emp.office_ref = office_obj
                            emp.office = office_obj.name if office_obj else emp.office
                            emp.permanent_address = permanent_address
                            emp.mobile_no = mobile_no
                            emp.user = user_obj
                            emp.is_active = is_active
                            emp.daily_allowance_rate = daily_allowance_rate
                            emp.save()
                            messages.success(request, f"कर्मचारी '{emp.name}' को विवरण सफलतापूर्वक अद्यावधिक गरियो।")
                        else:
                            emp = Employee.objects.create(
                                name=name,
                                code_no=code_no,
                                designation=designation,
                                level=level,
                                office_ref=office_obj,
                                office=office_obj.name if office_obj else '',
                                permanent_address=permanent_address,
                                mobile_no=mobile_no,
                                user=user_obj,
                                is_active=is_active,
                                daily_allowance_rate=daily_allowance_rate
                            )
                            messages.success(request, f"नयाँ कर्मचारी '{emp.name}' सफलतापूर्वक दर्ता गरियो।")
                        return redirect('/employees/')

    employees = Employee.objects.select_related('office_ref', 'user').order_by('name')
    offices = Office.objects.all().order_by('-is_default', 'name')
    users = User.objects.all().order_by('username')
    
    return render(request, 'employees.html', {
        'employees': employees,
        'offices': offices,
        'users': users,
        'error_message': error_message,
        'is_admin': True,
    })


# ==============================================================================
# Admin-Only: User Management (प्रयोगकर्ता व्यवस्थापन)
# ==============================================================================

@admin_required
def manage_users(request):
    """
    प्रयोगकर्ता व्यवस्थापन (Admin Only):
    - नयाँ प्रयोगकर्ता खाता सिर्जना गर्ने
    - रोल (व्यवस्थापक / Admin वा कर्मचारी / User) तोक्ने
    - पासवर्ड रिसेट गर्ने
    - सम्बन्धित कर्मचारीसँग म्यापिङ गर्ने
    - खाता सक्रिय/निष्क्रिय वा हटाउने
    """
    error_message = None
    
    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        user_id = request.POST.get('user_id')
        
        if action == 'delete' and user_id:
            target_user = get_object_or_404(User, pk=user_id)
            if target_user == request.user:
                messages.error(request, "तपाईंले आफ्नै हालको खाता हटाउन सक्नुहुन्न।")
            else:
                uname = target_user.username
                target_user.delete()
                messages.success(request, f"प्रयोगकर्ता खाता '{uname}' हटाइयो।")
            return redirect('/users/')
            
        elif action == 'toggle_status' and user_id:
            target_user = get_object_or_404(User, pk=user_id)
            if target_user == request.user:
                messages.error(request, "तपाईंले आफ्नै हालको खाता निष्क्रिय गर्न सक्नुहुन्न।")
            else:
                target_user.is_active = not target_user.is_active
                target_user.save(update_fields=['is_active'])
                st = "सक्रिय" if target_user.is_active else "निष्क्रिय"
                messages.success(request, f"प्रयोगकर्ता '{target_user.username}' को खाता {st} गरियो।")
            return redirect('/users/')
            
        elif action == 'reset_password' and user_id:
            target_user = get_object_or_404(User, pk=user_id)
            new_password = request.POST.get('new_password', '').strip()
            if not new_password or len(new_password) < 4:
                error_message = "नयाँ पासवर्ड कम्तीमा ४ अक्षरको हुनुपर्छ।"
            else:
                target_user.set_password(new_password)
                target_user.save()
                
                # If they reset their own password, keep them logged in
                if request.user.pk == target_user.pk:
                    from django.contrib.auth import update_session_auth_hash
                    update_session_auth_hash(request, target_user)
                    
                messages.success(request, f"प्रयोगकर्ता '{target_user.username}' को पासवर्ड सफलतापूर्वक परिवर्तन गरियो।")
                return redirect('/users/')
                
        elif action == 'delete_user' and user_id:
            target_user = get_object_or_404(User, pk=user_id)
            if target_user.is_superuser or target_user.pk == request.user.pk:
                messages.error(request, "तपाईंले आफूलाई वा मुख्य Admin लाई मेटाउन सक्नुहुन्न।")
            else:
                username_deleted = target_user.username
                target_user.delete()
                messages.success(request, f"प्रयोगकर्ता '{username_deleted}' सफलतापूर्वक मेटाइयो।")
            return redirect('/users/')
                
        else:
            username = request.POST.get('username', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '').strip()
            roles = request.POST.getlist('roles')
            employee_id = request.POST.get('employee_id')
            managed_emp_ids = request.POST.getlist('managed_employees')
            is_active = bool(request.POST.get('is_active', True))
            
            is_staff_val = ('admin' in roles)
            is_superuser_val = ('admin' in roles)
            
            finance_group, _ = Group.objects.get_or_create(name='Finance')
            approver_group, _ = Group.objects.get_or_create(name='Approver')
            register_group, _ = Group.objects.get_or_create(name='Register')
            attendance_group, _ = Group.objects.get_or_create(name='Attendance')
            
            if user_id:
                target_user = get_object_or_404(User, pk=user_id)
                
                if username and username != target_user.username and User.objects.filter(username=username).exists():
                    error_message = f"युजरनेम '{username}' पहिले नै अर्को प्रयोगकर्ताले प्रयोग गरिसकेको छ।"
                else:
                    # Protect the main admin or the currently logged-in user from losing their admin rights
                    if target_user.is_superuser and (target_user.pk == request.user.pk or target_user.username == 'admin'):
                        is_staff_val = True
                        is_superuser_val = True
                        is_active = True

                    if username:
                        target_user.username = username
                    target_user.first_name = first_name
                    target_user.last_name = last_name
                    target_user.email = email
                    target_user.is_staff = is_staff_val
                    target_user.is_superuser = is_superuser_val
                    target_user.is_active = is_active
                    if password:
                        target_user.set_password(password)
                    target_user.save()

                    # If the user updated their own profile/password, keep them logged in
                    if request.user.pk == target_user.pk:
                        from django.contrib.auth import update_session_auth_hash
                        update_session_auth_hash(request, target_user)

                    target_user.groups.clear()
                    if 'finance' in roles: target_user.groups.add(finance_group)
                    if 'approver' in roles: target_user.groups.add(approver_group)
                    if 'register' in roles: target_user.groups.add(register_group)
                    if 'attendance' in roles: target_user.groups.add(attendance_group)
                    
                    if employee_id:
                        Employee.objects.filter(user=target_user).exclude(pk=employee_id).update(user=None)
                        emp = Employee.objects.filter(pk=employee_id).first()
                        if emp:
                            emp.user = target_user
                            emp.save(update_fields=['user'])
                    else:
                        Employee.objects.filter(user=target_user).update(user=None)
                        
                    if managed_emp_ids:
                        target_user.managed_employees.exclude(id__in=managed_emp_ids).update(managed_by=None)
                        for emp_id in managed_emp_ids:
                            emp = Employee.objects.filter(id=emp_id).first()
                            if emp:
                                emp.managed_by = target_user
                                emp.save(update_fields=['managed_by'])
                    else:
                        target_user.managed_employees.update(managed_by=None)
                        
                    messages.success(request, f"प्रयोगकर्ता '{target_user.username}' को विवरण अद्यावधिक गरियो।")
                    return redirect('/users/')
            else:
                if not username or not password:
                    error_message = "नयाँ खाताको लागि युजरनेम र पासवर्ड दुवै अनिवार्य छन्।"
                elif User.objects.filter(username=username).exists():
                    error_message = f"युजरनेम '{username}' पहिले नै दर्ता छ।"
                else:
                    new_user = User.objects.create_user(
                        username=username,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        is_staff=is_staff_val,
                        is_superuser=is_superuser_val,
                        is_active=is_active
                    )
                    if 'finance' in roles: new_user.groups.add(finance_group)
                    if 'approver' in roles: new_user.groups.add(approver_group)
                    if 'register' in roles: new_user.groups.add(register_group)
                    if 'attendance' in roles: new_user.groups.add(attendance_group)

                    if employee_id:
                        emp = Employee.objects.filter(pk=employee_id).first()
                        if emp:
                            emp.user = new_user
                            emp.save(update_fields=['user'])
                            
                    if managed_emp_ids:
                        for emp_id in managed_emp_ids:
                            emp = Employee.objects.filter(id=emp_id).first()
                            if emp:
                                emp.managed_by = new_user
                                emp.save(update_fields=['managed_by'])
                    messages.success(request, f"नयाँ प्रयोगकर्ता '{new_user.username}' सफलतापूर्वक सिर्जना गरियो।")
                    return redirect('/users/')

    users_list = User.objects.all().prefetch_related('groups', 'managed_employees').order_by('-is_superuser', '-is_staff', 'username')
    employees = Employee.objects.all().order_by('name')
    
    return render(request, 'users.html', {
        'users_list': users_list,
        'employees': employees,
        'error_message': error_message,
        'is_admin': True,
    })




# ==============================================================================
# Finance / Admin: Travel Record Register (भ्रमण अभिलेख खाता - Landscape Mode)
# ==============================================================================

@finance_required
def travel_register_view(request):
    """
    भ्रमण अभिलेख खाता (Travel Record Ledger / Register View in Landscape Mode).
    Finance and Superuser module displaying all travel orders, FY filter, and print layout.
    """
    default_office = Office.get_default_office()
    selected_fy = request.GET.get('fiscal_year', '').strip()
    selected_emp_id = request.GET.get('employee_id', '').strip()
    selected_office_id = request.GET.get('office_id', '').strip()
    selected_paying_agency = request.GET.get('paying_agency', 'INTERNAL').strip()
    search_query = request.GET.get('q', '').strip()
    
    orders_qs = TravelOrder.objects.all().select_related('employee', 'office_ref', 'report', 'bill').order_by('id')
    
    # Exclude REJECTED orders by default
    orders_qs = orders_qs.exclude(status='REJECTED')

    # Ledger Protection: Filter by Paying Agency Type (Default: INTERNAL only)
    if selected_paying_agency == 'INTERNAL':
        orders_qs = orders_qs.exclude(bill__paying_agency_type='EXTERNAL')
    elif selected_paying_agency == 'EXTERNAL':
        orders_qs = orders_qs.filter(bill__paying_agency_type='EXTERNAL')
    # If 'ALL', include all paying agencies

    current_office = default_office
    if selected_office_id:
        try:
            current_office = Office.objects.get(pk=selected_office_id)
            orders_qs = orders_qs.filter(office_ref=current_office)
        except Office.DoesNotExist:
            pass
            
    if selected_fy:
        matched_ids = [ord.id for ord in orders_qs if ord.fiscal_year == selected_fy or getattr(ord, 'effective_fiscal_year', '') == selected_fy]
        orders_qs = orders_qs.filter(id__in=matched_ids)
        
    if selected_emp_id:
        orders_qs = orders_qs.filter(employee_id=selected_emp_id)
        
    if search_query:
        orders_qs = orders_qs.filter(
            Q(person__icontains=search_query) |
            Q(destination__icontains=search_query) |
            Q(order_number__icontains=search_query) |
            Q(purpose__icontains=search_query) |
            Q(code_no__icontains=search_query)
        )
        
    orders_list = []
    for idx, ord in enumerate(orders_qs, 1):
        ord.sn_nepali = to_nepali_digits(idx)
        orders_list.append(ord)
    fiscal_years = get_all_fiscal_years()
        
    employees = Employee.objects.filter(is_active=True).order_by('name')
    offices = Office.objects.all().order_by('-is_default', 'name')
    
    return render(request, 'travel_register.html', {
        'orders': orders_list,
        'default_office': current_office,
        'fiscal_years': fiscal_years,
        'employees': employees,
        'offices': offices,
        'selected_fy': selected_fy,
        'selected_emp_id': selected_emp_id,
        'selected_office_id': selected_office_id,
        'selected_paying_agency': selected_paying_agency,
        'search_query': search_query,
        'total_records_nepali': to_nepali_digits(len(orders_list)),
        'is_admin': is_admin(request.user),
        'is_finance': is_finance_user(request.user),
    })


# ==============================================================================
# PDF / Print Views (म.ले.प. फारामहरू) with User Permission Check
# ==============================================================================

@login_required
def travel_order_pdf(request, pk):
    ensure_logo_synced()
    order = get_object_or_404(TravelOrder.objects.select_related('employee', 'office_ref'), pk=pk)
    if not user_can_access_order(request.user, order):
        messages.error(request, "तपाईंलाई यो भ्रमण आदेश हेर्ने अनुमति छैन।")
        return redirect('/')
    return render(request, 'travel_order.html', {
        'record': order,
        'is_admin': is_admin(request.user),
        'is_finance': is_finance_user(request.user),
        'is_approver': is_approver(request.user),
        'is_attendance': is_attendance_user(request.user),
    })


@login_required
def travel_bill_pdf(request, pk):
    ensure_logo_synced()
    bill = get_object_or_404(TravelBill.objects.select_related('travel_order', 'travel_order__employee', 'travel_order__office_ref'), pk=pk)
    if bill.travel_order and not user_can_access_order(request.user, bill.travel_order):
        messages.error(request, "तपाईंलाई यो भ्रमण बिल हेर्ने अनुमति छैन।")
        return redirect('/')
    bill.update_totals()
    items = bill.items.all().order_by('id')
    return render(request, 'travel_bill.html', {'bill': bill, 'items': items, 'is_admin': is_admin(request.user)})


@login_required
def travel_report_pdf(request, pk):
    report = get_object_or_404(TravelReport.objects.select_related('travel_order', 'travel_order__employee', 'travel_order__office_ref'), pk=pk)
    if report.travel_order and not user_can_access_order(request.user, report.travel_order):
        messages.error(request, "तपाईंलाई यो भ्रमण प्रतिवेदन हेर्ने अनुमति छैन।")
        return redirect('/')
    return render(request, 'travel_report.html', {'report': report, 'is_admin': is_admin(request.user)})


@login_required
def order_nivedan(request, pk):
    order = get_object_or_404(TravelOrder.objects.select_related('employee', 'office_ref'), pk=pk)
    if not user_can_access_order(request.user, order):
        messages.error(request, "तपाईंलाई यो पेस्की निवेदन हेर्ने अनुमति छैन।")
        return redirect('/')
    office = order.office_ref or Office.get_default_office()
    return render(request, 'travel_nivedan.html', {
        'title': f'भ्रमण पेस्की माग निवेदन - {order.person}',
        'nivedan_type': 'advance',
        'order': order,
        'office_name': office.name,
        'head_title': office.head_title,
        'location': office.location or 'झापा',
        'current_date': order.order_date or get_today_bs(),
        'is_admin': is_admin(request.user),
    })


@login_required
def bill_nivedan(request, pk):
    bill = get_object_or_404(TravelBill.objects.select_related('travel_order', 'travel_order__employee', 'travel_order__office_ref'), pk=pk)
    if bill.travel_order and not user_can_access_order(request.user, bill.travel_order):
        messages.error(request, "तपाईंलाई यो भुक्तानी निवेदन हेर्ने अनुमति छैन।")
        return redirect('/')
    office = (bill.travel_order.office_ref if bill.travel_order else None) or Office.get_default_office()
    return render(request, 'travel_nivedan.html', {
        'title': f'दैनिक तथा भ्रमण खर्च भुक्तानी निवेदन - {bill.travel_order.person if bill.travel_order else ""}',
        'nivedan_type': 'claim',
        'bill': bill,
        'office_name': office.name,
        'head_title': office.head_title,
        'location': office.location or 'झापा',
        'current_date': bill.bill_date or (bill.travel_order.end_date if bill.travel_order else get_today_bs()),
        'is_admin': is_admin(request.user),
    })


# ==============================================================================
# JSON APIs for Auto-fill
# ==============================================================================

@login_required
@require_GET
def api_employee_detail(request, pk):
    try:
        emp = Employee.objects.select_related('office_ref').get(pk=pk)
        return JsonResponse({
            'success': True,
            'name': emp.name,
            'code_no': emp.code_no,
            'designation': emp.designation,
            'level': emp.level or '',
            'office': emp.office_ref.name if emp.office_ref else emp.office,
            'office_id': emp.office_ref.id if emp.office_ref else '',
            'permanent_address': emp.permanent_address or '',
            'mobile_no': emp.mobile_no or '',
            'daily_allowance_rate': emp.daily_allowance_rate or 1600,
        })
    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Employee not found'}, status=404)


@login_required
@require_GET
def api_order_detail(request, pk):
    try:
        order = TravelOrder.objects.select_related('employee', 'office_ref', 'report', 'bill').get(pk=pk)
        if not user_can_access_order(request.user, order):
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
            
        perm_address = ''
        if order.employee and order.employee.permanent_address:
            perm_address = order.employee.permanent_address

        report_reg_no = ''
        if hasattr(order, 'report') and order.report and order.report.report_reg_no:
            report_reg_no = order.report.report_reg_no
        else:
            report_reg_no = order.order_number

        duration = get_bs_duration_days(order.start_date, order.end_date) or 1
        recommended_da_days = calculate_tada_allowance_days(duration)
        da_rate = (order.employee.daily_allowance_rate if order.employee and order.employee.daily_allowance_rate else 1600)

        paying_agency_type = 'INTERNAL'
        external_agency_name = ''
        if hasattr(order, 'bill') and order.bill:
            paying_agency_type = order.bill.paying_agency_type
            external_agency_name = order.bill.external_agency_name or ''

        return JsonResponse({
            'success': True,
            'id': order.id,
            'order_number': order.order_number,
            'order_date': order.order_date,
            'fiscal_year': order.fiscal_year,
            'status': order.status,
            'status_display': order.get_status_display(),
            'person': order.person,
            'code_no': order.code_no or (order.employee.code_no if order.employee else ''),
            'designation': order.designation or (order.employee.designation if order.employee else ''),
            'destination': order.destination,
            'purpose': order.purpose,
            'start_date': order.start_date,
            'end_date': order.end_date,
            'duration_days': duration,
            'recommended_da_days': recommended_da_days,
            'daily_allowance_rate': da_rate,
            'paying_agency_type': paying_agency_type,
            'external_agency_name': external_agency_name,
            'is_external': (paying_agency_type == 'EXTERNAL'),
            'vehicle_office': bool(order.vehicle_office),
            'vehicle_public': bool(order.vehicle_public),
            'vehicle_rent': bool(order.vehicle_rent),
            'is_office_vehicle_only': bool(order.is_office_vehicle_only),
            'traveller_date': order.traveller_date or '',
            'recommender_date': order.recommender_date or '',
            'approver_date': order.approver_date or '',
            'admin_date': order.admin_date or '',
            'advance_amount': order.advance_amount or '0',
            'advance_words': order.advance_words or '',
            'office': order.office_name,
            'permanent_address': perm_address,
            'report_reg_no': report_reg_no,
        })
    except TravelOrder.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found'}, status=404)


@login_required
def order_workflow_action(request, pk, action):
    """
    आदेश कार्यप्रवाह (Workflow Transition Action):
    - submit: प्रयोगकर्ताद्वारा पेश (DRAFT -> PENDING)
    - recommend: सिफारिसकर्ताद्वारा सिफारिस (PENDING -> RECOMMENDED)
    - approve: स्वीकृतकर्ताद्वारा स्वीकृत (RECOMMENDED/PENDING -> APPROVED)
    - clear_finance: आर्थिक प्रशासनद्वारा भुक्तानी फछ्र्यौट (APPROVED/REGISTERED -> FINANCE_CLEARED)
    - register: दर्ता / चलानी जारी (-> REGISTERED, allocates official serial)
    - reject: अस्वीकृत (-> REJECTED)
    """
    order = get_object_or_404(TravelOrder, pk=pk)
    user = request.user
    admin_mode = is_admin(user)
    finance_mode = is_finance_user(user)
    approver_mode = is_approver(user)
    register_mode = is_register_user(user)
    attendance_mode = is_attendance_user(user)

    if not admin_mode and not finance_mode and not approver_mode and not register_mode and not attendance_mode and not user_can_access_order(user, order):
        messages.error(request, "तपाईंलाई यो कार्य गर्ने अनुमति छैन।")
        return redirect(f'/order/{order.id}/')

    today_bs = get_today_bs()

    if action == 'submit':
        if order.status != 'DRAFT':
            messages.error(request, "यो भ्रमण आदेश पहिल्यै पेश भइसकेको छ।")
        else:
            order.status = 'PENDING'
            order.save()
            messages.success(request, f"भ्रमण आदेश #{order.id} स्वीकृतिका लागि पेश गरियो।")

    elif action == 'recommend':
        if not admin_mode and order.created_by == user and not user.is_staff:
            messages.error(request, "आफ्नो भ्रमण आदेश आफैंले सिफारिस गर्न मिल्दैन।")
            return redirect(f'/order/{order.id}/')
        order.status = 'RECOMMENDED'
        order.recommended_by = user
        if not order.recommender_date:
            order.recommender_date = today_bs
        order.save()
        messages.success(request, f"भ्रमण आदेश #{order.id} सफलतापूर्वक सिफारिस गरियो।")

    elif action == 'approve':
        if not (admin_mode or approver_mode):
            messages.error(request, "भ्रमण आदेश स्वीकृत गर्ने अधिकार कार्यालय प्रमुखलाई मात्र छ।")
            return redirect(f'/order/{order.id}/')
        order.status = 'APPROVED'
        order.approved_by = user
        if not order.approver_date:
            order.approver_date = today_bs
        order.save()
        messages.success(request, f"भ्रमण आदेश #{order.id} कार्यालय प्रमुखद्वारा सफलतापूर्वक स्वीकृत गरियो। अब दर्ता फाँट/आर्थिक प्रशासनले दर्ता गरी आदेश नं. कायम गर्न सक्नेछ।")

    elif action == 'clear_finance':
        if not (admin_mode or finance_mode):
            messages.error(request, "आर्थिक प्रशासन फछ्र्यौट गर्ने अधिकार लेखा / आर्थिक प्रशासन शाखालाई मात्र छ।")
            return redirect(f'/order/{order.id}/')
        order.status = 'FINANCE_CLEARED'
        order.save()
        messages.success(request, f"भ्रमण आदेश #{order.id} को आर्थिक प्रशासन फछ्र्यौट सम्पन्न भयो।")

    elif action == 'register':
        if not (admin_mode or register_mode or finance_mode):
            messages.error(request, "भ्रमण आदेश दर्ता गरी आदेश नं. कायम गर्ने अधिकार दर्ता/चलानी फाँटलाई मात्र छ।")
            return redirect(f'/order/{order.id}/')
        if order.status not in ['APPROVED', 'FINANCE_CLEARED']:
            messages.error(request, "कार्यालय प्रमुख / स्वीकृत गर्ने पदाधिकारीले भ्रमण आदेश स्वीकृत (Approve) गरेपछि मात्र दर्ता गरी आदेश नं. कायम गर्न मिल्छ।")
            return redirect(f'/order/{order.id}/')
        
        manual_num = request.POST.get('order_number') or request.GET.get('order_number', '').strip()
        if manual_num:
            order.order_number = to_nepali_digits(manual_num)
        elif not order.order_number:
            order.order_number = TravelOrder.allocate_next_order_number(order.fiscal_year, order.office_ref)

        order.status = 'REGISTERED'
        if not order.admin_date:
            order.admin_date = today_bs
        order.save()
        messages.success(request, f"भ्रमण आदेश #{order.id} दर्ता भई आदेश नं. '{order.order_number}' कायम भयो।")

    elif action == 'record_attendance':
        if not (admin_mode or is_attendance_user(user)):
            messages.error(request, "हाजिरी खातामा जनाउने अधिकार हाजिरी फाँट / प्रशासन शाखालाई मात्र छ।")
            return redirect(f'/order/{order.id}/')
        if order.status != 'REGISTERED':
            messages.error(request, "दर्ता अधिकारीबाट भ्रमण आदेश दर्ता भएपछि मात्र हाजिरी खातामा जनाउन मिल्छ।")
            return redirect(f'/order/{order.id}/')
        order.status = 'ATTENDANCE_RECORDED'
        order.save()
        messages.success(request, f"भ्रमण आदेश #{order.id} (आदेश नं. {order.order_number}) हाजिरी खातामा सफलतापूर्वक जनाइयो।")

    elif action == 'reject':
        if not (admin_mode or finance_mode or user.is_staff):
            messages.error(request, "भ्रमण आदेश अस्वीकृत गर्ने अनुमति छैन।")
            return redirect(f'/order/{order.id}/')
        order.status = 'REJECTED'
        order.save()
        messages.warning(request, f"भ्रमण आदेश #{order.id} अस्वीकृत (REJECTED) गरियो।")

    elif action in ['reset', 'clean', 'reset_all', 'delete_all']:
        reports_count, _ = TravelReport.objects.all().delete()
        bills_count, _ = TravelBill.objects.all().delete()
        orders_count, _ = TravelOrder.objects.all().delete()
        FiscalYearSequence.objects.all().update(last_number=0)
        messages.success(request, f"✅ अनलाइन सर्भरका सम्पूर्ण पुराना डाटाहरू ({orders_count} आदेश, {bills_count} बिल) मेटाई क्रमिक आदेश नम्बर ००१ बाट सुरु हुने गरी रिसेट गरियो।")
        return redirect('/')

    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or f'/order/{order.id}/'
    return redirect(next_url)


@login_required
def delete_order_view(request, pk):
    """STRICT ADMIN ONLY: Only System Administrator (Admin) can delete travel orders."""
    if not is_admin(request.user):
        messages.error(request, "भ्रमण आदेश मेटाउने (Delete) अधिकार व्यवस्थापक (System Admin) लाई मात्र छ।")
        return redirect(f'/order/{pk}/')
    order = get_object_or_404(TravelOrder, pk=pk)
    fy = order.fiscal_year
    off_ref = order.office_ref
    num = order.order_number or f"#{order.id}"
    order.delete()

    # Recalculate max_in_db and sync sequence table counter
    orders = TravelOrder.objects.filter(Q(fiscal_year=fy) | Q(fiscal_year=to_english_digits(fy)))
    if off_ref:
        orders = orders.filter(office_ref=off_ref)
    max_in_db = 0
    for o in orders:
        if o.order_number:
            eng_digits = re.findall(r'\d+', to_english_digits(str(o.order_number)))
            if eng_digits:
                try:
                    val = int(eng_digits[0])
                    if val > max_in_db:
                        max_in_db = val
                except ValueError:
                    pass
    FiscalYearSequence.objects.filter(fiscal_year=normalize_nepali_fiscal_year(fy), office_ref=off_ref).update(last_number=max_in_db)

    messages.success(request, f"भ्रमण आदेश '{num}' सफलतापूर्वक मेटाइयो।")
    return redirect('/')


@login_required
def delete_bill_view(request, pk):
    """STRICT ADMIN ONLY: Only System Administrator (Admin) can delete travel bills."""
    if not is_admin(request.user):
        messages.error(request, "भ्रमण खर्च बिल मेटाउने (Delete) अधिकार व्यवस्थापक (System Admin) लाई मात्र छ।")
        return redirect(f'/bill/{pk}/')
    bill = get_object_or_404(TravelBill, pk=pk)
    bill.delete()
    messages.success(request, f"भ्रमण खर्च बिल सफलतापूर्वक मेटाइयो।")
    return redirect('/')


@login_required
def delete_report_view(request, pk):
    """STRICT ADMIN ONLY: Only System Administrator (Admin) can delete travel reports."""
    if not is_admin(request.user):
        messages.error(request, "भ्रमण प्रतिवेदन मेटाउने (Delete) अधिकार व्यवस्थापक (System Admin) लाई मात्र छ।")
        return redirect(f'/report/{pk}/')
    report = get_object_or_404(TravelReport, pk=pk)
    report.delete()
    messages.success(request, f"भ्रमण प्रतिवेदन सफलतापूर्वक मेटाइयो।")
    return redirect('/')


@require_GET
def api_next_order_number(request):
    """Returns the previewed next order number for the given fiscal year and office."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    fy = request.GET.get('fiscal_year', '').strip()
    order_date = request.GET.get('order_date', '').strip()
    office_id = request.GET.get('office_id', '').strip()
    
    if not fy and order_date:
        fy = get_fiscal_year_from_bs_date(order_date)
    if not fy:
        fy = get_fiscal_year_from_bs_date(get_today_bs()) or '२०८३/८४'
        
    office_obj = None
    if office_id:
        office_obj = Office.objects.filter(id=office_id).first()
        
    next_num = TravelOrder.peek_next_order_number(fiscal_year=fy, office_ref=office_obj)
    return JsonResponse({
        'success': True,
        'next_order_number': next_num,
        'fiscal_year': normalize_nepali_fiscal_year(fy)
    })


# ==============================================================================
# Travel Order Entry & Edit Views (भ्रमण आदेश फाराम)
# ==============================================================================

@login_required
def order_form_view(request):
    """
    भ्रमण आदेश सिर्जना:
    - Admin: कुनै पनि कर्मचारीको नाममा आदेश जारी गर्न पाउने।
    - Regular User: आफ्नै विवरण स्वतः छनोट हुने र सिर्जना हुने।
    """
    user = request.user
    admin_mode = is_admin(user)
    user_emp = get_user_employee(user)
    
    if admin_mode:
        employees = Employee.objects.filter(is_active=True).select_related('office_ref')
    else:
        employees = []
        if user_emp:
            employees.append(user_emp)
        employees.extend(user.managed_employees.filter(is_active=True).select_related('office_ref'))
        if not employees:
            employees = Employee.objects.filter(is_active=True).select_related('office_ref')
            
    offices = Office.objects.all().order_by('-is_default', 'name')
    default_office = Office.get_default_office()

    fiscal_years = get_all_fiscal_years()
    today_bs = get_today_bs()
    default_fy, default_date = get_default_date_for_fy(request, today_bs)

    if request.method == 'POST':
        order_date = request.POST.get('order_date')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        recommender_date = request.POST.get('recommender_date')
        approver_date = request.POST.get('approver_date')

        # Validate Nepali dates and travel duration constraint
        is_valid, err_msg, duration = validate_travel_order_dates(order_date, start_date, end_date, recommender_date, approver_date)
        if not is_valid:
            return render(request, 'order_form.html', {
                'error_message': err_msg,
                'form_data': request.POST,
                'employees': employees,
                'offices': offices,
                'default_office': default_office,
                'is_admin': admin_mode,
                'user_emp': user_emp,
                'fiscal_years': fiscal_years,
                'today_bs': today_bs,
                'default_fy': request.POST.get('fiscal_year') or default_fy,
        'default_date': default_date,
            })

        employee_id = request.POST.get('employee')
        if not admin_mode:
            emp = None
            if employee_id:
                requested_emp = Employee.objects.filter(id=employee_id).first()
                if requested_emp and (requested_emp == user_emp or requested_emp.managed_by == user):
                    emp = requested_emp
            if not emp:
                emp = user_emp
        else:
            emp = Employee.objects.filter(id=employee_id).first() if employee_id else None
            
        office_id = request.POST.get('office_ref')
        office_obj = Office.objects.filter(id=office_id).first() if office_id else None
        if not office_obj and emp and emp.office_ref:
            office_obj = emp.office_ref
        if not office_obj:
            office_obj = Office.get_default_office()

        raw_fy = request.POST.get('fiscal_year', '').strip()
        derived_fy = get_fiscal_year_from_bs_date(order_date)
        final_fy = raw_fy or derived_fy or default_fy

        req_order_no = request.POST.get('order_number', '').strip()
        initial_status = 'REGISTERED' if (req_order_no and admin_mode) else 'PENDING'

        order_obj = TravelOrder.objects.create(
            created_by=user,
            status=initial_status,
            order_number=req_order_no,
            order_date=order_date,
            fiscal_year=final_fy,
            office_ref=office_obj,
            employee=emp,
            person=request.POST.get('person') or (emp.name if emp else user.get_full_name() or user.username),
            code_no=request.POST.get('code_no') or (emp.code_no if emp else ''),
            designation=request.POST.get('designation') or (emp.designation if emp else ''),
            office=request.POST.get('office') or (office_obj.name if office_obj else ''),
            destination=request.POST.get('destination'),
            purpose=request.POST.get('purpose'),
            start_date=start_date,
            end_date=end_date,
            vehicle_public=bool(request.POST.get('vehicle_public')),
            vehicle_office=bool(request.POST.get('vehicle_office')),
            vehicle_rent=bool(request.POST.get('vehicle_rent')),
            advance_amount=request.POST.get('advance_amount'),
            advance_words=request.POST.get('advance_words'),
            program_name=request.POST.get('program_name'),
            traveller_date=request.POST.get('traveller_date'),
            recommender_date=recommender_date,
            approver_date=approver_date,
            admin_date=request.POST.get('admin_date'),
            other_details=request.POST.get('other_details')
        )
        if initial_status == 'PENDING':
            messages.success(request, f"भ्रमण आदेश #{order_obj.id} सफलतापूर्वक पेश भयो। स्वीकृतिका लागि कार्यालय प्रमुख समक्ष पठाइएको छ।")
        else:
            messages.success(request, f"भ्रमण आदेश #{order_obj.id} दर्ता भई आदेश नं. '{order_obj.order_number}' कायम भयो।")

        return redirect(f'/order/{order_obj.id}/')
    
    return render(request, 'order_form.html', {
        'employees': employees,
        'offices': offices,
        'default_office': default_office,
        'is_admin': admin_mode,
        'user_emp': user_emp,
        'fiscal_years': fiscal_years,
        'today_bs': today_bs,
        'default_fy': default_fy,
        'default_date': default_date,
    })


@login_required
def edit_order_view(request, pk):
    order = get_object_or_404(TravelOrder, pk=pk)
    user = request.user
    admin_mode = is_admin(user)
    
    if not admin_mode:
        messages.error(request, "तपाईंलाई यो भ्रमण आदेश सम्पादन गर्ने अनुमति छैन। (केबल एडमिनले मात्र सम्पादन गर्न सक्छन्)")
        return redirect('/')
        
    user_emp = get_user_employee(user)
    if admin_mode:
        employees = Employee.objects.filter(is_active=True).select_related('office_ref')
    else:
        employees = []
        if user_emp:
            employees.append(user_emp)
        employees.extend(user.managed_employees.filter(is_active=True).select_related('office_ref'))
        if order.employee and order.employee not in employees:
            employees.append(order.employee)
        
    offices = Office.objects.all().order_by('-is_default', 'name')
    default_office = order.office_ref or Office.get_default_office()
    fiscal_years = get_all_fiscal_years()
    default_fy = order.fiscal_year or get_fiscal_year_from_bs_date(get_today_bs()) or '२०८३/८४'

    if request.method == 'POST':
        order_date = request.POST.get('order_date')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        recommender_date = request.POST.get('recommender_date')
        approver_date = request.POST.get('approver_date')

        # Validate Nepali dates and travel duration constraint
        is_valid, err_msg, duration = validate_travel_order_dates(order_date, start_date, end_date, recommender_date, approver_date)
        if not is_valid:
            return render(request, 'order_form.html', {
                'order': order,
                'error_message': err_msg,
                'form_data': request.POST,
                'employees': employees,
                'offices': offices,
                'default_office': default_office,
                'is_admin': admin_mode,
                'user_emp': user_emp,
                'fiscal_years': fiscal_years,
                'default_fy': request.POST.get('fiscal_year') or default_fy,
            })

        employee_id = request.POST.get('employee')
        if not admin_mode:
            emp = None
            if employee_id:
                requested_emp = Employee.objects.filter(id=employee_id).first()
                if requested_emp and (requested_emp == user_emp or requested_emp.managed_by == user):
                    emp = requested_emp
            if not emp:
                emp = user_emp
        else:
            emp = Employee.objects.filter(id=employee_id).first() if employee_id else None
            
        office_id = request.POST.get('office_ref')
        office_obj = Office.objects.filter(id=office_id).first() if office_id else None
        if not office_obj and emp and emp.office_ref:
            office_obj = emp.office_ref
        if not office_obj:
            office_obj = order.office_ref or Office.get_default_office()

        order.order_number = request.POST.get('order_number')
        order.order_date = order_date
        raw_fy = request.POST.get('fiscal_year', '').strip()
        derived_fy = get_fiscal_year_from_bs_date(order_date)
        order.fiscal_year = raw_fy or derived_fy or default_fy
        order.office_ref = office_obj

        if emp:
            order.employee = emp
        order.person = request.POST.get('person')
        order.code_no = request.POST.get('code_no')
        order.designation = request.POST.get('designation')
        order.office = request.POST.get('office') or (office_obj.name if office_obj else '')
        order.destination = request.POST.get('destination')
        order.purpose = request.POST.get('purpose')
        order.start_date = start_date
        order.end_date = end_date
        order.vehicle_public = bool(request.POST.get('vehicle_public'))
        order.vehicle_office = bool(request.POST.get('vehicle_office'))
        order.vehicle_rent = bool(request.POST.get('vehicle_rent'))
        order.advance_amount = request.POST.get('advance_amount')
        order.advance_words = request.POST.get('advance_words')
        order.program_name = request.POST.get('program_name')
        order.traveller_date = request.POST.get('traveller_date')
        order.recommender_date = request.POST.get('recommender_date')
        order.approver_date = request.POST.get('approver_date')
        order.admin_date = request.POST.get('admin_date')
        order.other_details = request.POST.get('other_details')
        order.save()
        return redirect(f'/order/{order.id}/')

    return render(request, 'order_form.html', {
        'order': order,
        'employees': employees,
        'offices': offices,
        'default_office': default_office,
        'is_admin': admin_mode,
        'user_emp': user_emp,
        'fiscal_years': fiscal_years,
        'default_fy': default_fy,
    })


# ==============================================================================
# Travel Bill Entry (भ्रमण खर्चको बिल फाराम)
# ==============================================================================

@login_required
def bill_form_view(request):
    """
    भ्रमण बिल सिर्जना:
    - Admin: बिल बन्न बाँकी सबै कर्मचारीका आदेशहरू ड्रपडाउनमा आउने।
    - Regular User: आफ्ना मात्र बिल बन्न बाँकी आदेशहरू ड्रपडाउनमा आउने।
    """
    user = request.user
    admin_mode = is_admin(user)
    accessible_orders = get_user_accessible_orders(user)
    orders = accessible_orders.filter(bill__isnull=True).order_by('-id')
    preselected_order_id = request.GET.get('order_id', '')

    default_fy, default_date = get_default_date_for_fy(request)
    if preselected_order_id:
        existing_bill = TravelBill.objects.filter(travel_order_id=preselected_order_id).first()
        if existing_bill:
            return redirect(f'/bill/{existing_bill.id}/')

    if request.method == 'POST':
        order_id = request.POST.get('travel_order')
        if not order_id:
            return render(request, 'bill_form.html', {
                'orders': orders,
                'error_message': 'कृपया सम्बन्धित भ्रमण आदेश छान्नुहोस्।',
                'form_data': request.POST,
                'preselected_order_id': preselected_order_id,
                'is_admin': admin_mode,
            })

        order = get_object_or_404(TravelOrder, pk=order_id)
        
        # Verify access
        if not user_can_access_order(user, order):
            return render(request, 'bill_form.html', {
                'orders': orders,
                'error_message': 'तपाईंलाई यो भ्रमण आदेशको बिल बनाउने अधिकार छैन।',
                'is_admin': admin_mode,
            })
        
        # Check if bill already exists for this order
        existing_bill = TravelBill.objects.filter(travel_order=order).first()
        if existing_bill:
            return render(request, 'bill_form.html', {
                'orders': orders,
                'error_message': f"उक्त भ्रमण आदेश (आदेश नं. {order.order_number}) को दैनिक तथा भ्रमण खर्चको बिल (# {existing_bill.id}) पहिले नै दर्ता भइसकेको छ। दोहोरो बिल सिर्जना गर्न मिल्दैन।",
                'form_data': request.POST,
                'preselected_order_id': preselected_order_id,
                'is_admin': admin_mode,
            })

        bill_date = request.POST.get('bill_date')
        
        # 1. Validate bill_date >= order.end_date
        is_valid_date, date_err = validate_travel_bill_date(bill_date, order.end_date)
        if not is_valid_date:
            return render(request, 'bill_form.html', {
                'orders': orders,
                'error_message': date_err,
                'form_data': request.POST,
                'preselected_order_id': order_id,
                'is_admin': admin_mode,
            })

        # 2. Check total miscellaneous expenses (महल ११ को कुल जोड <= रु २०००)
        misc_amts = request.POST.getlist('misc_amount[]') or request.POST.getlist('misc_amount')
        if not misc_amts:
            row_indices = request.POST.getlist('row_index')
            total_misc_input = sum(int(request.POST.get(f'misc_amt_{idx}') or 0) for idx in row_indices)
        else:
            total_misc_input = sum(int(m or 0) for m in misc_amts)

        if total_misc_input > 2000:
            return render(request, 'bill_form.html', {
                'orders': orders,
                'error_message': f"दैनिक तथा भ्रमण खर्चको बिलमा फुटकर खर्च (महल ११) को कुल जोड बढीमा रु. २,०००/- सम्म मात्र हुन सक्छ। (तपाईंले प्रविष्ट गर्नुभएको जम्मा फुटकर खर्च: रु. {total_misc_input}/-)",
                'form_data': request.POST,
                'preselected_order_id': order_id,
                'is_admin': admin_mode,
                'today_bs': get_today_bs(),
        'default_date': default_date,
            })

        # 3. Validate Travel Bill Item Dates against Order bounds
        items_data_to_validate = []
        dep_places = request.POST.getlist('departure_place[]') or request.POST.getlist('departure_place')
        if dep_places:
            dep_dates = request.POST.getlist('departure_date[]') or request.POST.getlist('departure_date')
            arr_places = request.POST.getlist('arrival_place[]') or request.POST.getlist('arrival_place')
            arr_dates = request.POST.getlist('arrival_date[]') or request.POST.getlist('arrival_date')
            for i in range(len(dep_places)):
                if dep_places[i].strip():
                    items_data_to_validate.append({
                        'departure_place': dep_places[i].strip(),
                        'departure_date': dep_dates[i].strip() if i < len(dep_dates) else '',
                        'arrival_place': arr_places[i].strip() if i < len(arr_places) else '',
                        'arrival_date': arr_dates[i].strip() if i < len(arr_dates) else '',
                    })
        else:
            row_indices = request.POST.getlist('row_index')
            for idx in row_indices:
                dep_p = request.POST.get(f'dep_place_{idx}', '').strip()
                if dep_p:
                    items_data_to_validate.append({
                        'departure_place': dep_p,
                        'departure_date': request.POST.get(f'dep_date_{idx}', '').strip(),
                        'arrival_place': request.POST.get(f'arr_place_{idx}', '').strip(),
                        'arrival_date': request.POST.get(f'arr_date_{idx}', '').strip(),
                    })

        is_items_valid, items_err = validate_travel_bill_item_dates(items_data_to_validate, order.start_date, order.end_date)
        if not is_items_valid:
            return render(request, 'bill_form.html', {
                'orders': orders,
                'error_message': items_err,
                'form_data': request.POST,
                'preselected_order_id': order_id,
                'is_admin': admin_mode,
                'today_bs': get_today_bs(),
        'default_date': default_date,
            })

        address = request.POST.get('address', '').strip()
        if not address and order.employee and order.employee.permanent_address:
            address = order.employee.permanent_address

        report_reg_no = request.POST.get('report_reg_no', '').strip()
        if not report_reg_no and hasattr(order, 'report') and order.report and order.report.report_reg_no:
            report_reg_no = order.report.report_reg_no
        if not report_reg_no:
            report_reg_no = order.order_number

        paying_agency_type = request.POST.get('paying_agency_type', 'INTERNAL').strip()
        external_agency_name = request.POST.get('external_agency_name', '').strip()

        bill = TravelBill.objects.create(
            travel_order=order,
            bill_date=bill_date,
            paying_agency_type=paying_agency_type,
            external_agency_name=external_agency_name,
            address=address,
            report_reg_no=report_reg_no,
            receipt_count=request.POST.get('receipt_count', '').strip(),
            advance_taken=int(request.POST.get('advance_taken') or 0),
            amount_in_words=request.POST.get('amount_in_words', '')
        )
        
        is_office_only = bool(order.is_office_vehicle_only)

        # Save dynamic items
        dep_places = request.POST.getlist('departure_place[]') or request.POST.getlist('departure_place')
        if dep_places:
            dep_dates = request.POST.getlist('departure_date[]') or request.POST.getlist('departure_date')
            dep_times = request.POST.getlist('departure_time[]') or request.POST.getlist('departure_time')
            arr_places = request.POST.getlist('arrival_place[]') or request.POST.getlist('arrival_place')
            arr_dates = request.POST.getlist('arrival_date[]') or request.POST.getlist('arrival_date')
            arr_times = request.POST.getlist('arrival_time[]') or request.POST.getlist('arrival_time')
            travel_modes = request.POST.getlist('travel_mode[]') or request.POST.getlist('travel_mode')
            ticket_nos = request.POST.getlist('ticket_no[]') or request.POST.getlist('ticket_no')
            fare_amts = request.POST.getlist('fare_amount[]') or request.POST.getlist('fare_amount')
            da_days = request.POST.getlist('daily_allowance_days[]') or request.POST.getlist('daily_allowance_days')
            da_rates = request.POST.getlist('daily_allowance_rate[]') or request.POST.getlist('daily_allowance_rate')
            misc_descs = request.POST.getlist('misc_desc[]') or request.POST.getlist('misc_desc')
            misc_amts = request.POST.getlist('misc_amount[]') or request.POST.getlist('misc_amount')
            remarks = request.POST.getlist('remarks[]') or request.POST.getlist('remarks')

            for i in range(len(dep_places)):
                if dep_places[i].strip():
                    raw_fare = int(fare_amts[i] or 0) if i < len(fare_amts) else 0
                    final_fare = 0 if is_office_only else raw_fare
                    
                    raw_ticket = ticket_nos[i].strip() if i < len(ticket_nos) else ''
                    final_ticket = '' if is_office_only else raw_ticket

                    TravelBillItem.objects.create(
                        travel_bill=bill,
                        departure_place=dep_places[i].strip(),
                        departure_date=dep_dates[i].strip() if i < len(dep_dates) else '',
                        departure_time=dep_times[i].strip() if i < len(dep_times) else '',
                        arrival_place=arr_places[i].strip() if i < len(arr_places) else '',
                        arrival_date=arr_dates[i].strip() if i < len(arr_dates) else '',
                        arrival_time=arr_times[i].strip() if i < len(arr_times) else '',
                        transport_medium=travel_modes[i].strip() if i < len(travel_modes) else '',

                        transport_fare=final_fare,
                        daily_allowance_days=float(da_days[i] or 0.0) if i < len(da_days) else 0.0,
                        daily_allowance_rate=int(da_rates[i] or 0) if i < len(da_rates) else 0,
                        misc_desc=misc_descs[i].strip() if i < len(misc_descs) else '',
                        misc_amount=int(misc_amts[i] or 0) if i < len(misc_amts) else 0,
                        remarks=remarks[i].strip() if i < len(remarks) else ''
                    )
        else:
            row_indices = request.POST.getlist('row_index')
            for idx in row_indices:
                dep_p = request.POST.get(f'dep_place_{idx}', '').strip()
                if not dep_p:
                    continue
                raw_fare = int(request.POST.get(f'fare_amt_{idx}') or 0)
                final_fare = 0 if is_office_only else raw_fare
                
                raw_ticket = request.POST.get(f'ticket_no_{idx}', '').strip()
                final_ticket = '' if is_office_only else raw_ticket

                TravelBillItem.objects.create(
                    bill=bill,
                    departure_place=dep_p,
                    departure_date=request.POST.get(f'dep_date_{idx}', '').strip(),
                    departure_time=request.POST.get(f'dep_time_{idx}', '').strip(),
                    arrival_place=request.POST.get(f'arr_place_{idx}', '').strip(),
                    arrival_date=request.POST.get(f'arr_date_{idx}', '').strip(),
                    arrival_time=request.POST.get(f'arr_time_{idx}', '').strip(),
                    travel_mode=request.POST.get(f'travel_mode_{idx}', '').strip(),
                    ticket_no=final_ticket,
                    fare_amount=final_fare,
                    daily_allowance_days=float(request.POST.get(f'da_days_{idx}') or 0.0),
                    daily_allowance_rate=int(request.POST.get(f'da_rate_{idx}') or 0),
                    misc_desc=request.POST.get(f'misc_desc_{idx}', ''),
                    misc_amount=int(request.POST.get(f'misc_amt_{idx}') or 0),
                    remarks=request.POST.get(f'remarks_{idx}', '')
                )
            
        bill.update_totals()
        if request.POST.get('amount_in_words'):
            bill.amount_in_words = request.POST.get('amount_in_words')
            bill.save(update_fields=['amount_in_words'])
            
        return redirect(f'/bill/{bill.id}/')
        
    return render(request, 'bill_form.html', {
        'orders': orders,
        'preselected_order_id': preselected_order_id,
        'is_admin': admin_mode,
        'today_bs': get_today_bs(),
        'default_date': default_date,
    })


# ==============================================================================
# Travel Report Entry (भ्रमण सम्पन्न प्रतिवेदन फाराम)
# ==============================================================================

@login_required
def report_form_view(request):
    """
    भ्रमण प्रतिवेदन सिर्जना:
    - Admin: प्रतिवेदन बन्न बाँकी सबै आदेशहरू देखिने।
    - Regular User: आफ्ना मात्र प्रतिवेदन बन्न बाँकी आदेशहरू देखिने।
    """
    user = request.user
    admin_mode = is_admin(user)
    accessible_orders = get_user_accessible_orders(user)
    orders = accessible_orders.filter(report__isnull=True).order_by('-id')
    preselected_order_id = request.GET.get('order_id', '')

    default_fy, default_date = get_default_date_for_fy(request)
    if preselected_order_id:
        existing_report = TravelReport.objects.filter(travel_order_id=preselected_order_id).first()
        if existing_report:
            return redirect(f'/report/{existing_report.id}/')

    if request.method == 'POST':
        order_id = request.POST.get('travel_order')
        if not order_id:
            return render(request, 'report_form.html', {
                'orders': orders,
                'error_message': 'कृपया सम्बन्धित भ्रमण आदेश छान्नुहोस्।',
                'preselected_order_id': preselected_order_id,
                'is_admin': admin_mode,
            })

        order = get_object_or_404(TravelOrder, pk=order_id)
        
        # Verify access
        if not user_can_access_order(user, order):
            return render(request, 'report_form.html', {
                'orders': orders,
                'error_message': 'तपाईंलाई यो भ्रमण आदेशको प्रतिवेदन बनाउने अधिकार छैन।',
                'is_admin': admin_mode,
            })
        
        # Check if report already exists for this order
        existing_report = TravelReport.objects.filter(travel_order=order).first()
        if existing_report:
            return redirect(f'/report/{existing_report.id}/')
            
        report = TravelReport.objects.create(
            travel_order=order,
            report_date=request.POST.get('report_date'),
            report_reg_no=request.POST.get('report_reg_no'),
            key_activities=request.POST.get('key_activities'),
            achievements=request.POST.get('achievements'),
            challenges=request.POST.get('challenges'),
            recommendations=request.POST.get('recommendations'),
            submitted_by=request.POST.get('submitted_by') or order.person,
            submitted_designation=request.POST.get('submitted_designation') or order.designation
        )
        return redirect(f'/report/{report.id}/')
        
    return render(request, 'report_form.html', {
        'orders': orders,
        'preselected_order_id': preselected_order_id,
        'is_admin': admin_mode,
        'today_bs': get_today_bs(),
        'default_date': default_date,
    })


# Aliases for backward compatibility
create_order = order_form_view
create_bill = bill_form_view
create_report = report_form_view
travel_ledger_view = travel_register_view
def edit_bill_view(request, pk):
    bill = get_object_or_404(TravelBill, pk=pk)
    user = request.user
    admin_mode = is_admin(user)
    
    if not admin_mode:
        messages.error(request, "तपाईंलाई यो बिल सम्पादन गर्ने अनुमति छैन। (केबल एडमिनले मात्र सम्पादन गर्न सक्छन्)")
        return redirect('/')

    order = bill.travel_order
    orders = [order]  # For the dropdown
    default_fy, default_date = get_default_date_for_fy(request)

    if request.method == 'POST':
        bill_date = request.POST.get('bill_date')
        
        # 1. Validate bill_date >= order.end_date
        is_valid_date, date_err = validate_travel_bill_date(bill_date, order.end_date)
        if not is_valid_date:
            return render(request, 'bill_form.html', {
                'orders': orders,
                'error_message': date_err,
                'form_data': request.POST,
                'preselected_order_id': order.id,
                'is_admin': admin_mode,
                'is_edit': True,
                'bill': bill,
            })

        # 2. Check total miscellaneous expenses (महल ११ को कुल जोड <= रु २०००)
        misc_amts = request.POST.getlist('misc_amount[]') or request.POST.getlist('misc_amount')
        if not misc_amts:
            row_indices = request.POST.getlist('row_index')
            total_misc_input = sum(int(request.POST.get(f'misc_amt_{idx}') or 0) for idx in row_indices)
        else:
            total_misc_input = sum(int(m or 0) for m in misc_amts)

        if total_misc_input > 2000:
            return render(request, 'bill_form.html', {
                'orders': orders,
                'error_message': f"दैनिक तथा भ्रमण खर्चको बिलमा फुटकर खर्च (महल ११) को कुल जोड बढीमा रु. २,०००/- सम्म मात्र हुन सक्छ। (तपाईंले प्रविष्ट गर्नुभएको जम्मा फुटकर खर्च: रु. {total_misc_input}/-)",
                'form_data': request.POST,
                'preselected_order_id': order.id,
                'is_admin': admin_mode,
                'today_bs': get_today_bs(),
                'default_date': default_date,
                'is_edit': True,
                'bill': bill,
            })

        # 3. Validate Travel Bill Item Dates against Order bounds
        items_data_to_validate = []
        dep_places = request.POST.getlist('departure_place[]') or request.POST.getlist('departure_place')
        if dep_places:
            dep_dates = request.POST.getlist('departure_date[]') or request.POST.getlist('departure_date')
            arr_places = request.POST.getlist('arrival_place[]') or request.POST.getlist('arrival_place')
            arr_dates = request.POST.getlist('arrival_date[]') or request.POST.getlist('arrival_date')
            for i in range(len(dep_places)):
                if dep_places[i].strip():
                    items_data_to_validate.append({
                        'departure_place': dep_places[i].strip(),
                        'departure_date': dep_dates[i].strip() if i < len(dep_dates) else '',
                        'arrival_place': arr_places[i].strip() if i < len(arr_places) else '',
                        'arrival_date': arr_dates[i].strip() if i < len(arr_dates) else '',
                    })
        else:
            row_indices = request.POST.getlist('row_index')
            for idx in row_indices:
                dep_p = request.POST.get(f'dep_place_{idx}', '').strip()
                if dep_p:
                    items_data_to_validate.append({
                        'departure_place': dep_p,
                        'departure_date': request.POST.get(f'dep_date_{idx}', '').strip(),
                        'arrival_place': request.POST.get(f'arr_place_{idx}', '').strip(),
                        'arrival_date': request.POST.get(f'arr_date_{idx}', '').strip(),
                    })

        is_items_valid, items_err = validate_travel_bill_item_dates(items_data_to_validate, order.start_date, order.end_date)
        if not is_items_valid:
            return render(request, 'bill_form.html', {
                'orders': orders,
                'error_message': items_err,
                'form_data': request.POST,
                'preselected_order_id': order.id,
                'is_admin': admin_mode,
                'today_bs': get_today_bs(),
                'default_date': default_date,
                'is_edit': True,
                'bill': bill,
            })

        address = request.POST.get('address', '').strip()
        report_reg_no = request.POST.get('report_reg_no', '').strip()
        if not report_reg_no and hasattr(order, 'report') and order.report and order.report.report_reg_no:
            report_reg_no = order.report.report_reg_no
        if not report_reg_no:
            report_reg_no = order.order_number

        paying_agency_type = request.POST.get('paying_agency_type', 'INTERNAL').strip()
        external_agency_name = request.POST.get('external_agency_name', '').strip()

        # Update bill
        bill.bill_date = bill_date
        bill.paying_agency_type = paying_agency_type
        bill.external_agency_name = external_agency_name
        bill.address = address
        bill.report_reg_no = report_reg_no
        bill.receipt_count = request.POST.get('receipt_count', '').strip()
        bill.advance_taken = int(request.POST.get('advance_taken') or 0)
        bill.amount_in_words = request.POST.get('amount_in_words', '')
        bill.save()
        
        is_office_only = bool(order.is_office_vehicle_only)

        # Recreate items
        bill.items.all().delete()
        
        if dep_places:
            dep_dates = request.POST.getlist('departure_date[]') or request.POST.getlist('departure_date')
            dep_times = request.POST.getlist('departure_time[]') or request.POST.getlist('departure_time')
            arr_places = request.POST.getlist('arrival_place[]') or request.POST.getlist('arrival_place')
            arr_dates = request.POST.getlist('arrival_date[]') or request.POST.getlist('arrival_date')
            arr_times = request.POST.getlist('arrival_time[]') or request.POST.getlist('arrival_time')
            travel_modes = request.POST.getlist('travel_mode[]') or request.POST.getlist('travel_mode')
            ticket_nos = request.POST.getlist('ticket_no[]') or request.POST.getlist('ticket_no')
            fare_amts = request.POST.getlist('fare_amount[]') or request.POST.getlist('fare_amount')
            da_days = request.POST.getlist('daily_allowance_days[]') or request.POST.getlist('daily_allowance_days')
            da_rates = request.POST.getlist('daily_allowance_rate[]') or request.POST.getlist('daily_allowance_rate')
            misc_descs = request.POST.getlist('misc_desc[]') or request.POST.getlist('misc_desc')
            misc_amts = request.POST.getlist('misc_amount[]') or request.POST.getlist('misc_amount')
            remarks = request.POST.getlist('remarks[]') or request.POST.getlist('remarks')

            for i in range(len(dep_places)):
                if dep_places[i].strip():
                    raw_fare = int(fare_amts[i] or 0) if i < len(fare_amts) else 0
                    final_fare = 0 if is_office_only else raw_fare
                    
                    raw_ticket = ticket_nos[i].strip() if i < len(ticket_nos) else ''
                    final_ticket = '' if is_office_only else raw_ticket

                    TravelBillItem.objects.create(
                        travel_bill=bill,
                        departure_place=dep_places[i].strip(),
                        departure_date=dep_dates[i].strip() if i < len(dep_dates) else '',
                        departure_time=dep_times[i].strip() if i < len(dep_times) else '',
                        arrival_place=arr_places[i].strip() if i < len(arr_places) else '',
                        arrival_date=arr_dates[i].strip() if i < len(arr_dates) else '',
                        arrival_time=arr_times[i].strip() if i < len(arr_times) else '',
                        transport_medium=travel_modes[i].strip() if i < len(travel_modes) else '',
                        transport_fare=final_fare,
                        daily_allowance_days=float(da_days[i] or 0.0) if i < len(da_days) else 0.0,
                        daily_allowance_rate=int(da_rates[i] or 0) if i < len(da_rates) else 0,
                        misc_desc=misc_descs[i].strip() if i < len(misc_descs) else '',
                        misc_amount=int(misc_amts[i] or 0) if i < len(misc_amts) else 0,
                        remarks=remarks[i].strip() if i < len(remarks) else ''
                    )
        else:
            row_indices = request.POST.getlist('row_index')
            for idx in row_indices:
                dep_p = request.POST.get(f'dep_place_{idx}', '').strip()
                if not dep_p:
                    continue
                raw_fare = int(request.POST.get(f'fare_amt_{idx}') or 0)
                final_fare = 0 if is_office_only else raw_fare
                
                raw_ticket = request.POST.get(f'ticket_no_{idx}', '').strip()
                final_ticket = '' if is_office_only else raw_ticket

                TravelBillItem.objects.create(
                    travel_bill=bill,
                    departure_place=dep_p,
                    departure_date=request.POST.get(f'dep_date_{idx}', '').strip(),
                    departure_time=request.POST.get(f'dep_time_{idx}', '').strip(),
                    arrival_place=request.POST.get(f'arr_place_{idx}', '').strip(),
                    arrival_date=request.POST.get(f'arr_date_{idx}', '').strip(),
                    arrival_time=request.POST.get(f'arr_time_{idx}', '').strip(),
                    transport_medium=request.POST.get(f'mode_{idx}', '').strip(),
                    transport_fare=final_fare,
                    daily_allowance_days=float(request.POST.get(f'da_days_{idx}') or 0.0),
                    daily_allowance_rate=int(request.POST.get(f'da_rate_{idx}') or 0),
                    misc_desc=request.POST.get(f'misc_desc_{idx}', '').strip(),
                    misc_amount=int(request.POST.get(f'misc_amt_{idx}') or 0),
                    remarks=request.POST.get(f'remarks_{idx}', '').strip()
                )

        messages.success(request, f"आदेश नं. {order.order_number} को बिल सफलतापूर्वक सम्पादन भयो।")
        return redirect(f'/bill/{bill.id}/')

    # Initial form data
    form_data = {
        'travel_order': order.id,
        'bill_date': bill.bill_date,
        'address': bill.address,
        'report_reg_no': bill.report_reg_no,
        'paying_agency_type': bill.paying_agency_type,
        'external_agency_name': bill.external_agency_name,
        'receipt_count': bill.receipt_count,
        'advance_taken': bill.advance_taken,
        'amount_in_words': bill.amount_in_words,
    }
    return render(request, 'bill_form.html', {
        'orders': orders,
        'form_data': form_data,
        'preselected_order_id': order.id,
        'is_admin': admin_mode,
        'today_bs': get_today_bs(),
        'default_date': default_date,
        'is_edit': True,
        'bill': bill,
        'bill_items': bill.items.all().order_by('id')
    })

def edit_report_view(request, pk):
    report = get_object_or_404(TravelReport, pk=pk)
    user = request.user
    admin_mode = is_admin(user)
    
    if not admin_mode:
        messages.error(request, "तपाईंलाई यो प्रतिवेदन सम्पादन गर्ने अनुमति छैन। (केबल एडमिनले मात्र सम्पादन गर्न सक्छन्)")
        return redirect('/')

    order = report.travel_order
    orders = [order]
    default_fy, default_date = get_default_date_for_fy(request)

    if request.method == 'POST':
        report.report_reg_no = request.POST.get('report_reg_no', '').strip()
        report.report_date = request.POST.get('report_date')
        report.submitted_by = request.POST.get('submitted_by')
        report.submitted_designation = request.POST.get('submitted_designation')
        
        report.key_activities = request.POST.get('key_activities')
        report.achievements = request.POST.get('achievements')
        report.challenges = request.POST.get('challenges')
        report.recommendations = request.POST.get('recommendations')
        
        report.save()

        messages.success(request, f"आदेश नं. {order.order_number} को प्रतिवेदन सफलतापूर्वक सम्पादन भयो।")
        return redirect(f'/report/{report.id}/')

    # Initial form data
    form_data = {
        'travel_order': order.id,
        'report_reg_no': report.report_reg_no,
        'report_date': report.report_date,
        'submitted_by': report.submitted_by,
        'submitted_designation': report.submitted_designation,
        'key_activities': report.key_activities,
        'achievements': report.achievements,
        'challenges': report.challenges,
        'recommendations': report.recommendations,
    }
    return render(request, 'report_form.html', {
        'orders': orders,
        'form_data': form_data,
        'preselected_order_id': order.id,
        'is_admin': admin_mode,
        'today_bs': get_today_bs(),
        'default_date': default_date,
        'is_edit': True,
        'report': report,
    })
