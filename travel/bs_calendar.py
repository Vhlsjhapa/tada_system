"""
Authentic Bikram Sambat (BS) Calendar Dataset (2000 - 2095 BS) and Date Operations
Supports date parsing, comparison, duration calculation, and validation for TADA system.
"""

BS_MONTH_DATA = {
    2000: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2001: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2002: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2003: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2004: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2005: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2006: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2007: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2008: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2009: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2010: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2011: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2012: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2013: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2014: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2015: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2016: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2017: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2018: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2019: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2020: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2021: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2022: [31, 31, 32, 31, 32, 30, 30, 30, 29, 30, 29, 31],
    2023: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2024: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2025: [31, 32, 31, 32, 30, 31, 30, 30, 29, 30, 29, 31],
    2026: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2027: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2028: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2029: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2030: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2031: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2032: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2033: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2034: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2035: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2036: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2037: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2038: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2039: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2040: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2041: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2042: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2043: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2044: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2045: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2046: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2047: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2048: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2049: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2050: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2051: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2052: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2053: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2054: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2055: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2056: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2057: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2058: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2059: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2060: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2061: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2062: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2063: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2064: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2065: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2066: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2067: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2068: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2069: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2070: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2071: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2072: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2073: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2074: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2075: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2076: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2077: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2078: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2079: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2080: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2081: [31, 31, 32, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2082: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2083: [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30],
    2084: [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30],
    2085: [31, 32, 31, 32, 30, 31, 30, 30, 29, 30, 30, 30],
    2086: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2087: [31, 31, 32, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2088: [31, 31, 32, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2089: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2090: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2091: [31, 31, 32, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2092: [31, 31, 32, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2093: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2094: [31, 31, 32, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2095: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30]
}

NEPALI_DIGITS = '०१२३४५६७८९'

def to_english_digits(text):
    if not text:
        return ''
    res = []
    for char in str(text):
        if char in NEPALI_DIGITS:
            res.append(str(NEPALI_DIGITS.index(char)))
        else:
            res.append(char)
    return ''.join(res)

def to_nepali_digits(num):
    if num is None:
        return ''
    res = []
    for char in str(num):
        if char.isdigit():
            res.append(NEPALI_DIGITS[int(char)])
        else:
            res.append(char)
    return ''.join(res)

def parse_bs_date(date_str):
    """
    Parses a BS date string in formats like '2082/04/21', '२०८२/०४/२१', '2082-04-21'.
    Returns (year, month, day) as integers, or None if invalid.
    """
    if not date_str:
        return None
    eng_str = to_english_digits(date_str.strip())
    # replace dash or dot with slash
    eng_str = eng_str.replace('-', '/').replace('.', '/')
    parts = eng_str.split('/')
    if len(parts) != 3:
        return None
    try:
        y = int(parts[0])
        m = int(parts[1])
        d = int(parts[2])
        if y not in BS_MONTH_DATA:
            return None
        if m < 1 or m > 12:
            return None
        max_days = BS_MONTH_DATA[y][m - 1]
        if d < 1 or d > max_days:
            return None
        return (y, m, d)
    except (ValueError, IndexError):
        return None

def bs_to_abs_days(year, month, day):
    """
    Converts a valid BS date into absolute cumulative days starting from 2000/01/01.
    """
    if year not in BS_MONTH_DATA or month < 1 or month > 12:
        return 0
    days = 0
    for y in range(2000, year):
        if y in BS_MONTH_DATA:
            days += sum(BS_MONTH_DATA[y])
    for m in range(1, month):
        days += BS_MONTH_DATA[year][m - 1]
    days += (day - 1)
    return days

def compare_bs_dates(date_str1, date_str2):
    """
    Compares two BS dates.
    Returns:
      -1 if date1 < date2
       0 if date1 == date2
       1 if date1 > date2
       None if either is unparseable
    """
    p1 = parse_bs_date(date_str1)
    p2 = parse_bs_date(date_str2)
    if not p1 or not p2:
        return None
    d1 = bs_to_abs_days(*p1)
    d2 = bs_to_abs_days(*p2)
    if d1 < d2:
        return -1
    elif d1 > d2:
        return 1
    return 0

def get_bs_duration_days(start_date_str, end_date_str):
    """
    Calculates inclusive travel duration in days between start_date and end_date.
    e.g. 2082/04/21 to 2082/04/21 is 1 day.
    Returns integer days, or None if dates are invalid or end_date < start_date.
    """
    p_start = parse_bs_date(start_date_str)
    p_end = parse_bs_date(end_date_str)
    if not p_start or not p_end:
        return None
    start_abs = bs_to_abs_days(*p_start)
    end_abs = bs_to_abs_days(*p_end)
    if end_abs < start_abs:
        return -1  # end date earlier than start date
    return (end_abs - start_abs) + 1

def validate_travel_order_dates(order_date_str, start_date_str, end_date_str, recommender_date_str=None, approver_date_str=None):
    """
    Validates travel order date constraints:
    1. 'भ्रमण शुरु मिति' cannot be earlier than 'आदेश मिति' (can be same day or later, but not before order_date).
    2. 'भ्रमण अन्त्य मिति' cannot be earlier than 'भ्रमण शुरु मिति'
    3. 'भ्रमण अवधि' cannot exceed 7 days (बढीमा ७ दिन)
    4. 'सिफारिस गर्ने पदाधिकारीको मिति' (if provided) cannot be earlier than 'आदेश मिति' (recommender_date >= order_date)
    5. 'भ्रमण स्वीकृत गर्ने पदाधिकारीको मिति' (if provided) cannot be earlier than 'आदेश मिति' (approver_date >= order_date)
    
    Returns (is_valid: bool, error_message: str or None, duration_days: int)
    """
    p_order = parse_bs_date(order_date_str)
    p_start = parse_bs_date(start_date_str)
    p_end = parse_bs_date(end_date_str)

    if not p_order:
        return (False, "आदेश मिति अमान्य छ। कृपया सही नेपाली मिति (जस्तै: २०८२/०४/२०) प्रविष्ट गर्नुहोस्।", 0)
    if not p_start:
        return (False, "भ्रमण शुरु मिति अमान्य छ। कृपया सही नेपाली मिति प्रविष्ट गर्नुहोस्।", 0)
    if not p_end:
        return (False, "भ्रमण अन्त्य मिति अमान्य छ। कृपया सही नेपाली मिति प्रविष्ट गर्नुहोस्।", 0)

    # 1. start_date cannot be earlier than order_date (start_date >= order_date)
    cmp_order_start = compare_bs_dates(start_date_str, order_date_str)
    if cmp_order_start < 0:
        return (
            False, 
            f"भ्रमण शुरु मिति ({start_date_str}) भ्रमण आदेश मिति ({order_date_str}) भन्दा अगाडिको हुन सक्दैन।", 
            0
        )

    # 2. end_date cannot be earlier than start_date
    cmp_start_end = compare_bs_dates(end_date_str, start_date_str)
    if cmp_start_end < 0:
        return (
            False, 
            f"भ्रमण अन्त्य मिति ({end_date_str}) भ्रमण शुरु मिति ({start_date_str}) भन्दा अगाडिको हुन सक्दैन।", 
            0
        )

    # 3. duration <= 7 days
    duration = get_bs_duration_days(start_date_str, end_date_str)
    if duration > 7:
        return (
            False, 
            f"भ्रमण अवधि बढीमा ७ दिनको मात्र हुन सक्छ। (तपाईंले छान्नुभएको अवधि: {to_nepali_digits(duration)} दिन)", 
            duration
        )

    # 4. recommender_date cannot be earlier than order_date
    if recommender_date_str and recommender_date_str.strip():
        rec_clean = recommender_date_str.strip()
        p_rec = parse_bs_date(rec_clean)
        if not p_rec:
            return (False, f"सिफारिस गर्ने पदाधिकारीको मिति ({rec_clean}) अमान्य छ। कृपया सही नेपाली मिति प्रविष्ट गर्नुहोस्।", duration)
        cmp_order_rec = compare_bs_dates(rec_clean, order_date_str)
        if cmp_order_rec < 0:
            return (
                False,
                f"सिफारिस गर्ने पदाधिकारीको मिति ({rec_clean}) भ्रमण आदेश मिति ({order_date_str}) भन्दा अगाडिको हुन सक्दैन।",
                duration
            )

    # 5. approver_date cannot be earlier than order_date
    if approver_date_str and approver_date_str.strip():
        app_clean = approver_date_str.strip()
        p_app = parse_bs_date(app_clean)
        if not p_app:
            return (False, f"भ्रमण स्वीकृत गर्ने पदाधिकारीको मिति ({app_clean}) अमान्य छ। कृपया सही नेपाली मिति प्रविष्ट गर्नुहोस्।", duration)
        cmp_order_app = compare_bs_dates(app_clean, order_date_str)
        if cmp_order_app < 0:
            return (
                False,
                f"भ्रमण स्वीकृत गर्ने पदाधिकारीको मिति ({app_clean}) भ्रमण आदेश मिति ({order_date_str}) भन्दा अगाडिको हुन सक्दैन।",
                duration
            )

    return (True, None, duration)

def validate_travel_bill_date(bill_date_str, order_end_date_str):
    """
    Validates travel bill submission date:
    'बिल पेश गरेको मिति' must be on or after 'भ्रमण अन्त्य मिति' (order_end_date).
    Returns (is_valid: bool, error_message: str or None)
    """
    p_bill = parse_bs_date(bill_date_str)
    if not p_bill:
        return (False, "बिल पेश गरेको मिति अमान्य छ। कृपया सही नेपाली मिति प्रविष्ट गर्नुहोस्।")
    
    if not order_end_date_str:
        return (True, None)

    p_end = parse_bs_date(order_end_date_str)
    if not p_end:
        return (True, None)

    cmp = compare_bs_dates(bill_date_str, order_end_date_str)
    if cmp < 0:
        return (
            False, 
            f"बिल पेश गरेको मिति ({bill_date_str}) राष्ट्रिय भ्रमण आदेशको भ्रमण अन्तिम मिति ({order_end_date_str}) वा सो मिति भन्दा पछिको हुनुपर्दछ।"
        )

    return (True, None)

def calculate_tada_allowance_days(duration_days):
    """
    According to Nepal TADA rules:
    The return day is counted at 1/4 (0.25) of the daily rate.
    For N days of travel, total allowance days = (N - 1) * 1.0 + 0.25 = N - 0.75 days (for N >= 1).
    e.g. 1 day -> 0.25 days
         2 days -> 1.25 days
         3 days -> 2.25 days
         7 days -> 6.25 days
    """
    if not duration_days or duration_days <= 0:
        return 0.0
    if duration_days == 1:
        return 0.25
    return round((duration_days - 1) + 0.25, 2)

def validate_travel_bill_item_dates(items_data, order_start_date, order_end_date):
    """
    Validates date constraints across travel bill items:
    1. Every departure and arrival date must fall strictly within [order_start_date, order_end_date].
    2. In each row, arrival_date cannot be earlier than departure_date.
    3. The first item's departure_date must be order_start_date (भ्रमण शुरु मिति शुरुमा हुनुपर्छ).
    4. The last item's arrival_date must be order_end_date (भ्रमण समाप्त मिति अन्त्यमा हुनुपर्छ).
    5. Each subsequent row's departure_date must not precede the previous row's arrival_date.
    
    items_data: list of dicts with keys 'departure_date', 'arrival_date', and optionally 'row_index' or 'departure_place'.
    Returns (is_valid: bool, error_message: str or None)
    """
    if not items_data:
        return (False, "कम्तिमा एउटा भ्रमण विवरण (पंक्ति) हुनुपर्दछ।")

    if not order_start_date or not order_end_date:
        return (True, None)

    p_order_start = parse_bs_date(order_start_date)
    p_order_end = parse_bs_date(order_end_date)
    if not p_order_start or not p_order_end:
        return (True, None)

    valid_items = [it for it in items_data if it.get('departure_date') or it.get('arrival_date')]
    if not valid_items:
        return (False, "भ्रमण विवरणमा प्रस्थान तथा आगमन मिति अनिवार्य छ।")

    # 1. First row departure date must start on order_start_date
    first_dep = valid_items[0].get('departure_date', '').strip()
    if first_dep:
        cmp_first = compare_bs_dates(first_dep, order_start_date)
        if cmp_first != 0:
            return (
                False,
                f"पहिलो पंक्तिको प्रस्थान मिति (२) भ्रमण आदेशको शुरु मिति ({order_start_date}) नै हुनुपर्दछ। (हाल: {first_dep})"
            )

    # 2. Last row arrival date must end on order_end_date
    last_arr = valid_items[-1].get('arrival_date', '').strip()
    if last_arr:
        cmp_last = compare_bs_dates(last_arr, order_end_date)
        if cmp_last != 0:
            return (
                False,
                f"अन्तिम पंक्तिको आगमन मिति (४) भ्रमण आदेशको समाप्त मिति ({order_end_date}) नै हुनुपर्दछ। (हाल: {last_arr})"
            )

    prev_arr_date = None
    for idx, item in enumerate(valid_items):
        row_num = idx + 1
        dep_date = item.get('departure_date', '').strip()
        arr_date = item.get('arrival_date', '').strip()

        if not dep_date:
            return (False, f"पंक्ति नं. {to_nepali_digits(row_num)} मा प्रस्थान मिति (२) अनिवार्य छ।")
        if not arr_date:
            return (False, f"पंक्ति नं. {to_nepali_digits(row_num)} मा आगमन मिति (४) अनिवार्य छ।")

        p_dep = parse_bs_date(dep_date)
        if not p_dep:
            return (False, f"पंक्ति नं. {to_nepali_digits(row_num)} को प्रस्थान मिति ({dep_date}) अमान्य छ।")

        p_arr = parse_bs_date(arr_date)
        if not p_arr:
            return (False, f"पंक्ति नं. {to_nepali_digits(row_num)} को आगमन मिति ({arr_date}) अमान्य छ।")

        # Range check against order_start_date
        if compare_bs_dates(dep_date, order_start_date) < 0:
            return (
                False,
                f"पंक्ति नं. {to_nepali_digits(row_num)} को प्रस्थान मिति ({dep_date}) भ्रमण आदेशको शुरु मिति ({order_start_date}) भन्दा अगाडिको हुन सक्दैन।"
            )

        # Range check against order_end_date
        if compare_bs_dates(dep_date, order_end_date) > 0:
            return (
                False,
                f"पंक्ति नं. {to_nepali_digits(row_num)} को प्रस्थान मिति ({dep_date}) भ्रमण आदेशको समाप्त मिति ({order_end_date}) भन्दा पछिको हुन सक्दैन।"
            )

        if compare_bs_dates(arr_date, order_start_date) < 0:
            return (
                False,
                f"पंक्ति नं. {to_nepali_digits(row_num)} को आगमन मिति ({arr_date}) भ्रमण आदेशको शुरु मिति ({order_start_date}) भन्दा अगाडिको हुन सक्दैन।"
            )

        if compare_bs_dates(arr_date, order_end_date) > 0:
            return (
                False,
                f"पंक्ति नं. {to_nepali_digits(row_num)} को आगमन मिति ({arr_date}) भ्रमण आदेशको समाप्त मिति ({order_end_date}) भन्दा पछिको हुन सक्दैन।"
            )

        # In-row check: arr_date >= dep_date
        if compare_bs_dates(arr_date, dep_date) < 0:
            return (
                False,
                f"पंक्ति नं. {to_nepali_digits(row_num)} मा आगमन मिति ({arr_date}) प्रस्थान मिति ({dep_date}) भन्दा अगाडिको हुन सक्दैन।"
            )

        # Sequence check with previous row
        if prev_arr_date:
            if compare_bs_dates(dep_date, prev_arr_date) < 0:
                return (
                    False,
                    f"पंक्ति नं. {to_nepali_digits(row_num)} को प्रस्थान मिति ({dep_date}) अघिल्लो पंक्तिको आगमन मिति ({prev_arr_date}) भन्दा अगाडिको हुन सक्दैन।"
                )

        prev_arr_date = arr_date

    return (True, None)


def get_fiscal_year_from_bs_date(bs_date_str):
    """
    Computes standard Nepali Fiscal Year (e.g. '२०८२/८३') from a BS date string (e.g. '२०८२/०४/२०').
    In Nepal, FY runs from Shrawan 1 (Month 04) to Ashadh end (Month 03 of next year).
    Month 4..12 of Year Y -> Year Y / (Y+1)%100 (e.g. 2082/04 -> 2082/83 -> २०८२/८३)
    Month 1..3 of Year Y  -> Year (Y-1) / Y%100 (e.g. 2083/01 -> 2082/83 -> २०८२/८३)
    """
    if not bs_date_str:
        return None
    eng_str = to_english_digits(str(bs_date_str).strip())
    eng_str = eng_str.replace('-', '/').replace('.', '/')
    parts = eng_str.split('/')
    if len(parts) >= 2:
        try:
            y = int(parts[0])
            m = int(parts[1])
            if 2000 <= y <= 2100 and 1 <= m <= 12:
                if m >= 4:
                    start_y = y
                    end_y = (y + 1) % 100
                else:
                    start_y = y - 1
                    end_y = y % 100
                end_y_str = f"{end_y:02d}"
                return f"{to_nepali_digits(start_y)}/{to_nepali_digits(end_y_str)}"
        except (ValueError, TypeError):
            pass
    return None


import datetime

BS_YEAR_AD_START = {
    2080: datetime.date(2023, 4, 14),
    2081: datetime.date(2024, 4, 13),
    2082: datetime.date(2025, 4, 14),
    2083: datetime.date(2026, 4, 14),
    2084: datetime.date(2027, 4, 14),
    2085: datetime.date(2028, 4, 13),
}

def get_today_bs(ad_date=None):
    """
    Returns today's date in Bikram Sambat (BS) format (e.g. '२०८३/०४/२५').
    Automatically uses real system date (datetime.date.today()).
    """
    if ad_date is None:
        ad_date = datetime.date.today()
    if isinstance(ad_date, str):
        try:
            ad_date = datetime.datetime.strptime(ad_date, "%Y-%m-%d").date()
        except ValueError:
            ad_date = datetime.date.today()
            
    bs_y = 2083
    for y in sorted(BS_YEAR_AD_START.keys(), reverse=True):
        if ad_date >= BS_YEAR_AD_START[y]:
            bs_y = y
            break
            
    start_ad = BS_YEAR_AD_START[bs_y]
    diff_days = (ad_date - start_ad).days
    if diff_days < 0:
        return "२०८३/०४/२५"
        
    cur_m = 1
    cur_d = 1
    for m_days in BS_MONTH_DATA.get(bs_y, BS_MONTH_DATA[2083]):
        if diff_days >= m_days:
            diff_days -= m_days
            cur_m += 1
        else:
            break
            
    cur_d += diff_days
    return f"{to_nepali_digits(bs_y)}/{to_nepali_digits(f'{cur_m:02d}')}/{to_nepali_digits(f'{cur_d:02d}')}"


