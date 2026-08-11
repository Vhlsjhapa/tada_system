import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from travel.models import TravelOrder, TravelBill, Employee

# Create a test user and login
c = Client()
user = User.objects.filter(is_superuser=True).first()
if not user:
    user = User.objects.create_superuser('admin_test', 'a@a.com', 'admin_test')

c.force_login(user)

# Create an order
emp, _ = Employee.objects.get_or_create(name="Test Emp")
order = TravelOrder.objects.create(
    employee=emp,
    person="Test Emp",
    start_date="2082/01/01",
    end_date="2082/01/05",
    purpose="Test",
    created_by=user,
    office_ref=emp.office_ref,
    fiscal_year="2082/83"
)

post_data = {
    'travel_order': order.id,
    'bill_date': '2082/01/05',
    'paying_agency_type': 'INTERNAL',
    'departure_place[]': ['A'],
    'departure_date[]': ['2082/01/01'],
    'arrival_place[]': ['B'],
    'arrival_date[]': ['2082/01/05'],
    'transport_medium[]': ['Bus'],
    'transport_fare[]': ['500'],
    'daily_allowance_days[]': ['5'],
    'daily_allowance_rate[]': ['1000'],
    'misc_desc[]': [''],
    'misc_amount[]': ['0'],
    'row_total[]': ['5500']
}

print("Posting new bill...")
response = c.post('/bill/new/', data=post_data)
print("Post status:", response.status_code)
if response.status_code == 302:
    print("Redirected to:", response.url)
    render_res = c.get(response.url)
    print("Render status:", render_res.status_code)
else:
    print("Failed to post bill. Rendered form instead.")
    if 'error_message' in response.context:
        print("Error:", response.context['error_message'])

