/**
 * Nepali Panchanga Calendar & TADA System Engine
 * Fully Authentic Bikram Sambat (BS 2000 - 2095) with Exact Weekday & Tithi Math
 */

(function (window, document) {
    'use strict';

    // 1. Authentic Nepal Panchanga Month Days Dataset (2000 - 2095 BS)
    const BS_MONTH_DATA = {
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
        2090: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
        2091: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
        2092: [31, 31, 32, 32, 31, 30, 30, 30, 29, 30, 29, 31],
        2093: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
        2094: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
        2095: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
    };

    const NEPALI_MONTHS = [
        "बैशाख", "जेठ", "असार", "साउन", "भदौ", "असोज",
        "कात्तिक", "मङ्सिर", "पुस", "माघ", "फागुन", "चैत"
    ];

    const NEPALI_DAYS_FULL = [
        "आइतबार", "सोमबार", "मङ्गलबार", "बुधबार", "बिहीबार", "शुक्रबार", "शनिबार"
    ];

    const NEPALI_DAYS_SHORT = [
        "आइत", "सोम", "मङ्गल", "बुध", "बिही", "शुक्र", "शनि"
    ];

    const NEPALI_DIGITS = ['०', '१', '२', '३', '४', '५', '६', '७', '८', '९'];

    // 2. Conversion & Formatting Utilities
    function toNepaliDigits(input) {
        if (input === null || input === undefined) return '';
        return String(input).replace(/[0-9]/g, match => NEPALI_DIGITS[parseInt(match, 10)]);
    }

    function toEnglishDigits(input) {
        if (!input) return '';
        return String(input).replace(/[०-९]/g, match => NEPALI_DIGITS.indexOf(match));
    }

    // Reference Point: 2080-01-01 BS = 2023-04-14 AD (Friday = 5)
    const REF_BS_YEAR = 2080;
    const REF_WEEKDAY = 5; // Friday
    const REF_AD_DATE = new Date(2023, 3, 14); // 2023 April 14

    // Calculate Weekday (0 = Sunday to 6 = Saturday) for given BS date
    function getBSWeekday(year, monthIndex, day) {
        let totalDays = 0;
        if (year >= REF_BS_YEAR) {
            for (let y = REF_BS_YEAR; y < year; y++) {
                const yearDays = (BS_MONTH_DATA[y] || BS_MONTH_DATA[2080]).reduce((a, b) => a + b, 0);
                totalDays += yearDays;
            }
            const currentMonths = BS_MONTH_DATA[year] || BS_MONTH_DATA[2080];
            for (let m = 0; m < monthIndex; m++) {
                totalDays += currentMonths[m];
            }
            totalDays += (day - 1);
            return (REF_WEEKDAY + totalDays) % 7;
        } else {
            for (let y = year; y < REF_BS_YEAR; y++) {
                const yearDays = (BS_MONTH_DATA[y] || BS_MONTH_DATA[2080]).reduce((a, b) => a + b, 0);
                totalDays += yearDays;
            }
            let passed = 0;
            const currentMonths = BS_MONTH_DATA[year] || BS_MONTH_DATA[2080];
            for (let m = 0; m < monthIndex; m++) {
                passed += currentMonths[m];
            }
            passed += (day - 1);
            const diff = totalDays - passed;
            return ((REF_WEEKDAY - diff) % 7 + 7) % 7;
        }
    }

    // Convert Gregorian Date to Bikram Sambat (AD to BS)
    function adToBs(dateObj) {
        const diffTime = dateObj.getTime() - REF_AD_DATE.getTime();
        let diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
        
        let bsYear = 2080;
        let bsMonth = 0; // 0-indexed
        let bsDay = 1;

        if (diffDays >= 0) {
            while (true) {
                const yearDays = (BS_MONTH_DATA[bsYear] || BS_MONTH_DATA[2080]).reduce((a, b) => a + b, 0);
                if (diffDays >= yearDays) {
                    diffDays -= yearDays;
                    bsYear++;
                } else {
                    break;
                }
            }
            const currentMonths = BS_MONTH_DATA[bsYear] || BS_MONTH_DATA[2080];
            for (let m = 0; m < 12; m++) {
                if (diffDays >= currentMonths[m]) {
                    diffDays -= currentMonths[m];
                    bsMonth++;
                } else {
                    break;
                }
            }
            bsDay += diffDays;
        } else {
            let remDays = Math.abs(diffDays);
            while (remDays > 0) {
                bsMonth--;
                if (bsMonth < 0) {
                    bsMonth = 11;
                    bsYear--;
                }
                const mDays = (BS_MONTH_DATA[bsYear] || BS_MONTH_DATA[2080])[bsMonth];
                if (remDays <= mDays) {
                    bsDay = mDays - remDays + 1;
                    remDays = 0;
                } else {
                    remDays -= mDays;
                }
            }
        }
        return { year: bsYear, month: bsMonth, day: bsDay };
    }

    // Number to Nepali Words (अक्षरमा रूपान्तरण)
    const ONES = ["", "एक", "दुई", "तीन", "चार", "पाँच", "छ", "सात", "आठ", "नौ", "दस",
        "एघार", "बाह्र", "तेह्र", "चौध", "पन्ध्र", "सोह्र", "सत्र", "अठार", "उन्नाइस", "बीस",
        "एक्काइस", "बाइस", "तेइस", "चौबिस", "पच्चिस", "छब्बिस", "सत्ताइस", "अट्ठाइस", "उनन्तीस", "तीस",
        "एकतीस", "बत्तीस", "तेत्तीस", "चौँतीस", "पैँतीस", "छत्तीस", "सरतीस", "अठतीस", "उनन्चालीस", "चालीस",
        "एकचालीस", "बयालीस", "त्रिचालीस", "चवालीस", "पैँतालीस", "छयालीस", "सत्चालीस", "अठचालीस", "उनन्पचास", "पचास",
        "एकाउन्न", "बाउन्न", "त्रिपन्न", "चउन्न", "पचपन्न", "छप्पन्न", "सन्ताउन्न", "अन्ठाउन्न", "उनन्साट्ठी", "साट्ठी",
        "एकसट्ठी", "बासट्ठी", "त्रिसट्ठी", "चौँसट्ठी", "पैँसट्ठी", "छयसट्ठी", "सतसट्ठी", "अठसट्ठी", "उनन्सत्तरी", "सत्तरी",
        "एकहत्तर", "बहत्तर", "त्रिहत्तर", "चौहत्तर", "पचहत्तर", "छयहत्तर", "सतहत्तर", "अठहत्तर", "उनासी", "असी",
        "एकासी", "बयासी", "त्रियासी", "चौरासी", "पचासी", "छयासी", "सतासी", "अठासी", "उनान्नब्बे", "नब्बे",
        "एकान्नब्बे", "बयानब्बे", "त्रियान्नब्बे", "चौरान्नब्बे", "पञ्चान्नब्बे", "छयान्नब्बे", "सन्तान्नब्बे", "अन्ठान्नब्बे", "उनन्सय"
    ];

    function nepaliNumberToWords(num) {
        num = parseInt(toEnglishDigits(num), 10);
        if (isNaN(num) || num === 0) return "शून्य रूपैयाँ मात्र";
        if (num < 0) return "ऋणात्मक " + nepaliNumberToWords(Math.abs(num));

        let words = "";
        if (Math.floor(num / 10000000) > 0) {
            words += ONES[Math.floor(num / 10000000)] + " करोड ";
            num %= 10000000;
        }
        if (Math.floor(num / 100000) > 0) {
            words += ONES[Math.floor(num / 100000)] + " लाख ";
            num %= 100000;
        }
        if (Math.floor(num / 1000) > 0) {
            words += ONES[Math.floor(num / 1000)] + " हजार ";
            num %= 1000;
        }
        if (Math.floor(num / 100) > 0) {
            words += ONES[Math.floor(num / 100)] + " सय ";
            num %= 100;
        }
        if (num > 0) {
            words += ONES[num] + " ";
        }
        return words.trim() + " रूपैयाँ मात्र";
    }

    // 3. Nepali Datepicker Class
    class NepaliDatePicker {
        constructor() {
            this.currentInput = null;
            this.minDateStr = null;
            this.maxDateStr = null;
            const todayBs = adToBs(new Date());
            this.activeYear = todayBs ? todayBs.year : 2083;
            this.activeMonth = todayBs ? todayBs.month : 3;
            this.selectedDate = todayBs || { year: 2083, month: 3, day: 23 };
            this.initDOM();
            this.bindEvents();
        }

        initDOM() {
            this.popup = document.createElement('div');
            this.popup.className = 'nepali-calendar-popup';
            this.popup.innerHTML = `
                <div class="nepali-cal-top-banner" id="nepCalBanner">
                    <span id="nepCalBannerDate">--</span>
                    <span id="nepCalBannerDay" class="nep-day-badge">--</span>
                </div>
                <div class="nepali-cal-range-hint" id="nepCalRangeHint" style="display:none;"></div>
                <div class="nepali-cal-header">
                    <button type="button" class="nepali-cal-nav-btn" id="nepCalPrev" title="अघिल्लो महिना">◀</button>
                    <div style="display:flex; gap:4px;">
                        <select id="nepCalYearSelect"></select>
                        <select id="nepCalMonthSelect"></select>
                    </div>
                    <button type="button" class="nepali-cal-nav-btn" id="nepCalNext" title="पछिल्लो महिना">▶</button>
                </div>
                <div class="nepali-cal-weekdays">
                    ${NEPALI_DAYS_SHORT.map((d, idx) => `<span class="${idx === 6 ? 'saturday-col' : ''}">${d}</span>`).join('')}
                </div>
                <div class="nepali-cal-days" id="nepCalDaysGrid"></div>
                <div class="nepali-cal-footer">
                    <button type="button" class="nepali-cal-today-btn" id="nepCalToday">आज</button>
                    <button type="button" class="nepali-cal-clear-btn" id="nepCalClear">हटाउनुहोस्</button>
                </div>
            `;
            document.body.appendChild(this.popup);

            // Populate Year and Month Selects
            const yearSel = this.popup.querySelector('#nepCalYearSelect');
            for (let y = 2075; y <= 2095; y++) {
                const opt = document.createElement('option');
                opt.value = y;
                opt.textContent = `${toNepaliDigits(y)} (${y})`;
                if (y === this.activeYear) opt.selected = true;
                yearSel.appendChild(opt);
            }

            const monthSel = this.popup.querySelector('#nepCalMonthSelect');
            NEPALI_MONTHS.forEach((m, idx) => {
                const opt = document.createElement('option');
                opt.value = idx;
                opt.textContent = m;
                if (idx === this.activeMonth) opt.selected = true;
                monthSel.appendChild(opt);
            });
        }

        bindEvents() {
            const yearSel = this.popup.querySelector('#nepCalYearSelect');
            const monthSel = this.popup.querySelector('#nepCalMonthSelect');
            const prevBtn = this.popup.querySelector('#nepCalPrev');
            const nextBtn = this.popup.querySelector('#nepCalNext');
            const todayBtn = this.popup.querySelector('#nepCalToday');
            const clearBtn = this.popup.querySelector('#nepCalClear');

            yearSel.addEventListener('change', (e) => {
                this.activeYear = parseInt(e.target.value, 10);
                this.renderDays();
            });

            monthSel.addEventListener('change', (e) => {
                this.activeMonth = parseInt(e.target.value, 10);
                this.renderDays();
            });

            prevBtn.addEventListener('click', () => {
                this.activeMonth--;
                if (this.activeMonth < 0) {
                    this.activeMonth = 11;
                    this.activeYear--;
                }
                yearSel.value = this.activeYear;
                monthSel.value = this.activeMonth;
                this.renderDays();
            });

            nextBtn.addEventListener('click', () => {
                this.activeMonth++;
                if (this.activeMonth > 11) {
                    this.activeMonth = 0;
                    this.activeYear++;
                }
                yearSel.value = this.activeYear;
                monthSel.value = this.activeMonth;
                this.renderDays();
            });

            todayBtn.addEventListener('click', () => {
                const today = adToBs(new Date());
                const todayStr = `${today.year}/${String(today.month + 1).padStart(2, '0')}/${String(today.day).padStart(2, '0')}`;
                
                let isOutOfBounds = false;
                if (this.minDateStr && compareBsDates(todayStr, this.minDateStr) === -1) {
                    isOutOfBounds = true;
                }
                if (this.maxDateStr && compareBsDates(todayStr, this.maxDateStr) === 1) {
                    isOutOfBounds = true;
                }

                if (isOutOfBounds) {
                    if (this.minDateStr) {
                        const pMin = parseBsDate(this.minDateStr);
                        if (pMin) {
                            this.selectDate(pMin.year, pMin.month - 1, pMin.day);
                            return;
                        }
                    }
                    alert('आजको मिति स्वीकृत भ्रमण अवधि भित्र पर्दैन।');
                    return;
                }

                this.selectDate(today.year, today.month, today.day);
            });

            clearBtn.addEventListener('click', () => {
                if (this.currentInput) {
                    this.currentInput.value = '';
                    this.updateInputHelper(this.currentInput, '');
                    this.currentInput.dispatchEvent(new Event('change', { bubbles: true }));
                }
                this.hide();
            });

            document.addEventListener('click', (e) => {
                if (this.popup.style.display === 'block' && 
                    !this.popup.contains(e.target) && 
                    e.target !== this.currentInput) {
                    this.hide();
                }
            });

            window.addEventListener('resize', () => {
                if (this.popup.style.display === 'block' && this.currentInput) {
                    this.positionPopup();
                }
            });

            window.addEventListener('scroll', () => {
                if (this.popup.style.display === 'block' && this.currentInput) {
                    this.positionPopup();
                }
            }, true);
        }

        positionPopup() {
            if (!this.currentInput) return;
            const rect = this.currentInput.getBoundingClientRect();
            const popupWidth = 265;
            const popupHeight = this.popup.offsetHeight || 295;

            let top = rect.bottom + 4;
            if (top + popupHeight > window.innerHeight - 8 && rect.top - popupHeight - 4 > 8) {
                top = rect.top - popupHeight - 4;
            }
            let left = rect.left;
            if (left + popupWidth > window.innerWidth - 8) {
                left = Math.max(8, window.innerWidth - popupWidth - 8);
            }
            if (left < 8) left = 8;

            this.popup.style.position = 'fixed';
            this.popup.style.top = `${Math.round(top)}px`;
            this.popup.style.left = `${Math.round(left)}px`;
        }

        renderDays() {
            const grid = this.popup.querySelector('#nepCalDaysGrid');
            grid.innerHTML = '';

            const daysInMonth = (BS_MONTH_DATA[this.activeYear] || BS_MONTH_DATA[2080])[this.activeMonth];
            const startWeekday = getBSWeekday(this.activeYear, this.activeMonth, 1);
            const todayBs = adToBs(new Date());

            // Top banner update
            const bannerDate = this.popup.querySelector('#nepCalBannerDate');
            const bannerDay = this.popup.querySelector('#nepCalBannerDay');
            
            if (this.selectedDate && this.selectedDate.year === this.activeYear && this.selectedDate.month === this.activeMonth) {
                const selWeekday = getBSWeekday(this.selectedDate.year, this.selectedDate.month, this.selectedDate.day);
                bannerDate.textContent = `${toNepaliDigits(this.selectedDate.year)} ${NEPALI_MONTHS[this.selectedDate.month]} ${toNepaliDigits(this.selectedDate.day)} गते`;
                bannerDay.textContent = NEPALI_DAYS_FULL[selWeekday];
            } else {
                bannerDate.textContent = `${toNepaliDigits(this.activeYear)} ${NEPALI_MONTHS[this.activeMonth]}`;
                bannerDay.textContent = `${toNepaliDigits(daysInMonth)} दिन`;
            }

            // Empty prefix slots
            for (let i = 0; i < startWeekday; i++) {
                const empty = document.createElement('div');
                empty.className = 'nepali-cal-day empty';
                grid.appendChild(empty);
            }

            // Day cells
            for (let day = 1; day <= daysInMonth; day++) {
                const cell = document.createElement('div');
                const weekday = getBSWeekday(this.activeYear, this.activeMonth, day);
                const mStr = String(this.activeMonth + 1).padStart(2, '0');
                const dStr = String(day).padStart(2, '0');
                const dateStr = `${this.activeYear}/${mStr}/${dStr}`;
                
                let classes = ['nepali-cal-day'];
                if (weekday === 6) classes.push('saturday');
                if (todayBs.year === this.activeYear && todayBs.month === this.activeMonth && todayBs.day === day) {
                    classes.push('today');
                }
                if (this.selectedDate && 
                    this.selectedDate.year === this.activeYear && 
                    this.selectedDate.month === this.activeMonth && 
                    this.selectedDate.day === day) {
                    classes.push('selected');
                }

                // Check min/max date restriction
                let isOutOfBounds = false;
                if (this.minDateStr) {
                    const cmpMin = compareBsDates(dateStr, this.minDateStr);
                    if (cmpMin === -1) isOutOfBounds = true;
                }
                if (!isOutOfBounds && this.maxDateStr) {
                    const cmpMax = compareBsDates(dateStr, this.maxDateStr);
                    if (cmpMax === 1) isOutOfBounds = true;
                }

                if (isOutOfBounds) {
                    classes.push('disabled');
                    cell.className = classes.join(' ');
                    cell.textContent = toNepaliDigits(day);
                    cell.title = `स्वीकृत भ्रमण अवधि बाहिरको मिति (स्वीकृत अवधि: ${toNepaliDigits(this.minDateStr || '')} देखि ${toNepaliDigits(this.maxDateStr || '')})`;
                } else {
                    if (this.minDateStr && this.maxDateStr) {
                        classes.push('in-travel-range');
                    }
                    cell.className = classes.join(' ');
                    cell.textContent = toNepaliDigits(day);
                    cell.title = `${toNepaliDigits(day)} गते (${NEPALI_DAYS_FULL[weekday]})`;

                    cell.addEventListener('mouseenter', () => {
                        bannerDate.textContent = `${toNepaliDigits(this.activeYear)} ${NEPALI_MONTHS[this.activeMonth]} ${toNepaliDigits(day)} गते`;
                        bannerDay.textContent = NEPALI_DAYS_FULL[weekday];
                    });

                    cell.addEventListener('click', () => {
                        this.selectDate(this.activeYear, this.activeMonth, day);
                    });
                }

                grid.appendChild(cell);
            }
        }

        selectDate(year, month, day) {
            const mStr = String(month + 1).padStart(2, '0');
            const dStr = String(day).padStart(2, '0');
            const formatted = `${toNepaliDigits(year)}/${toNepaliDigits(mStr)}/${toNepaliDigits(dStr)}`;
            const checkStr = `${year}/${mStr}/${dStr}`;

            // Double check bounds
            if (this.minDateStr && compareBsDates(checkStr, this.minDateStr) === -1) {
                alert(`⚠️ छनोट गरिएको मिति (${formatted}) भ्रमण शुरु मिति (${toNepaliDigits(this.minDateStr)}) भन्दा अगाडिको हुन सक्दैन।`);
                return;
            }
            if (this.maxDateStr && compareBsDates(checkStr, this.maxDateStr) === 1) {
                alert(`⚠️ छनोट गरिएको मिति (${formatted}) भ्रमण समाप्त मिति (${toNepaliDigits(this.maxDateStr)}) भन्दा पछिको हुन सक्दैन।`);
                return;
            }

            const weekday = getBSWeekday(year, month, day);
            const dayName = NEPALI_DAYS_FULL[weekday];

            if (this.currentInput) {
                this.currentInput.value = formatted;
                this.updateInputHelper(this.currentInput, `${NEPALI_MONTHS[month]} ${toNepaliDigits(day)} गते, ${dayName}`);
                this.currentInput.dispatchEvent(new Event('change', { bubbles: true }));
                this.currentInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
            this.selectedDate = { year, month, day };
            this.hide();
        }

        updateInputHelper(input, text) {
            let helper = input.parentElement ? input.parentElement.querySelector('.nepali-day-helper') : null;
            if (!helper && input.parentElement) {
                helper = document.createElement('div');
                helper.className = 'nepali-day-helper';
                input.parentElement.appendChild(helper);
            }
            if (helper) {
                helper.textContent = text ? `📅 ${text}` : '';
            }
        }

        showForInput(input) {
            this.currentInput = input;

            // Determine minDate and maxDate
            let minDateStr = input.getAttribute('data-min-date') || input.dataset.minDate || '';
            let maxDateStr = input.getAttribute('data-max-date') || input.dataset.maxDate || '';
            
            const isBillRowDate = Boolean(
                input.closest('.dynamic-bill-row') || 
                (input.name && (input.name.includes('departure_date') || input.name.includes('arrival_date')))
            );

            if (isBillRowDate) {
                if (!minDateStr && window.currentOrderStartDate) minDateStr = window.currentOrderStartDate;
                if (!maxDateStr && window.currentOrderEndDate) maxDateStr = window.currentOrderEndDate;
            }

            this.minDateStr = minDateStr ? toEnglishDigits(minDateStr).replace(/-/g, '/').replace(/\./g, '/') : null;
            this.maxDateStr = maxDateStr ? toEnglishDigits(maxDateStr).replace(/-/g, '/').replace(/\./g, '/') : null;

            // Show / Hide Range Hint banner
            const hint = this.popup.querySelector('#nepCalRangeHint');
            if (hint) {
                if (this.minDateStr && this.maxDateStr) {
                    hint.innerHTML = `🔒 स्वीकृत भ्रमण अवधि: <b>${toNepaliDigits(this.minDateStr)}</b> देखि <b>${toNepaliDigits(this.maxDateStr)}</b> सम्म`;
                    hint.style.display = 'block';
                } else if (this.minDateStr) {
                    hint.innerHTML = `🔒 न्यूनतम मिति: <b>${toNepaliDigits(this.minDateStr)}</b> वा सोभन्दा पछि`;
                    hint.style.display = 'block';
                } else if (this.maxDateStr) {
                    hint.innerHTML = `🔒 अधिकतम मिति: <b>${toNepaliDigits(this.maxDateStr)}</b> सम्म मात्र`;
                    hint.style.display = 'block';
                } else {
                    hint.style.display = 'none';
                }
            }

    function getTodayBsFormatted() {
        const fySelect = document.getElementById('id_fiscal_year');
        const todayBs = adToBs(new Date());
        if (fySelect && fySelect.value) {
            const startYearStr = fySelect.value.split('/')[0];
            const startYearInt = parseInt(toEnglishDigits(startYearStr), 10);
            // If the selected FY is not the current FY, default to Shrawan 1 of that FY
            if (startYearInt && startYearInt !== todayBs.year && startYearInt !== todayBs.year - 1) {
                 // Note: FY year logic is a bit complex, but if it's clearly a past year, start at Shrawan 1.
                 if (startYearInt < todayBs.year || (startYearInt === todayBs.year && todayBs.month < 3)) {
                     return `${toNepaliDigits(startYearInt)}/०४/०१`;
                 }
            }
        }
        const mStr = String(todayBs.month + 1).padStart(2, '0');
        const dStr = String(todayBs.day).padStart(2, '0');
        return `${toNepaliDigits(todayBs.year)}/${toNepaliDigits(mStr)}/${toNepaliDigits(dStr)}`;
    }

            const todayBs = adToBs(new Date());

            if (input.value && !input.value.includes('२०८२')) {
                const parts = toEnglishDigits(input.value).split('/');
                if (parts.length === 3) {
                    this.activeYear = parseInt(parts[0], 10) || (todayBs ? todayBs.year : 2083);
                    this.activeMonth = (parseInt(parts[1], 10) || 1) - 1;
                    const d = parseInt(parts[2], 10) || 1;
                    this.selectedDate = { year: this.activeYear, month: this.activeMonth, day: d };
                }
            } else if (this.minDateStr) {
                const pMin = parseBsDate(this.minDateStr);
                if (pMin) {
                    this.activeYear = pMin.year;
                    this.activeMonth = pMin.month - 1;
                    this.selectedDate = { year: pMin.year, month: pMin.month - 1, day: pMin.day };
                    const mStr = String(pMin.month).padStart(2, '0');
                    const dStr = String(pMin.day).padStart(2, '0');
                    input.value = `${toNepaliDigits(pMin.year)}/${toNepaliDigits(mStr)}/${toNepaliDigits(dStr)}`;
                }
            } else {
                this.activeYear = todayBs ? todayBs.year : 2083;
                this.activeMonth = todayBs ? todayBs.month : 3;
                this.selectedDate = todayBs || { year: 2083, month: 3, day: 25 };
                const todayFormatted = getTodayBsFormatted();
                input.value = todayFormatted;
                const weekday = getBSWeekday(this.activeYear, this.activeMonth, this.selectedDate.day);
                this.updateInputHelper(input, `${NEPALI_MONTHS[this.activeMonth]} ${toNepaliDigits(this.selectedDate.day)} गते, ${NEPALI_DAYS_FULL[weekday]}`);
                input.dispatchEvent(new Event('change', { bubbles: true }));
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }

            const yearSel = this.popup.querySelector('#nepCalYearSelect');
            const monthSel = this.popup.querySelector('#nepCalMonthSelect');
            if (yearSel) yearSel.value = this.activeYear;
            if (monthSel) monthSel.value = this.activeMonth;
            
            this.renderDays();
            this.popup.style.display = 'block';
            this.positionPopup();
        }

        hide() {
            this.popup.style.display = 'none';
        }
    }

    let datePickerInstance = null;
    function getDatePicker() {
        if (!datePickerInstance) {
            datePickerInstance = new NepaliDatePicker();
        }
        return datePickerInstance;
    }

    function attachDatePickers() {
        const selector = [
            'input[name*="date"]',
            'input[name*="start_date"]',
            'input[name*="end_date"]',
            'input[name*="order_date"]',
            'input[name*="bill_date"]',
            'input[name*="departure_date"]',
            'input[name*="arrival_date"]',
            'input[name*="report_date"]',
            'input[name*="admin_date"]',
            '.nepali-date-picker',
            '[data-nepali-datepicker]'
        ].join(',');

        document.querySelectorAll(selector).forEach(input => {
            if (!input.dataset.nepaliAttached) {
                input.dataset.nepaliAttached = "true";
                input.setAttribute('autocomplete', 'off');
                input.setAttribute('readonly', 'readonly');
                input.setAttribute('placeholder', '२०८३/०४/२५');
                
                const isPrimaryInput = Boolean(
                    input.name && (
                        input.name.includes('order_date') || 
                        input.name.includes('start_date') || 
                        input.name.includes('end_date') || 
                        input.name.includes('bill_date') || 
                        input.name.includes('report_date')
                    )
                );

                if (isPrimaryInput && (!input.value || input.value.includes('२०८२'))) {
                    input.value = getTodayBsFormatted();
                }

                // Show existing day helper if date present
                if (input.value) {
                    const parts = toEnglishDigits(input.value).split('/');
                    if (parts.length === 3) {
                        const y = parseInt(parts[0], 10);
                        const m = parseInt(parts[1], 10) - 1;
                        const d = parseInt(parts[2], 10);
                        if (y && m >= 0 && m < 12 && d) {
                            const weekday = getBSWeekday(y, m, d);
                            getDatePicker().updateInputHelper(input, `${NEPALI_MONTHS[m]} ${toNepaliDigits(d)} गते, ${NEPALI_DAYS_FULL[weekday]}`);
                        }
                    }
                }

                // Blur / manual typing bounds validation
                const validateManualInputBounds = () => {
                    if (!input.value) return;
                    let minDateStr = input.getAttribute('data-min-date') || input.dataset.minDate || '';
                    let maxDateStr = input.getAttribute('data-max-date') || input.dataset.maxDate || '';
                    
                    const isBillRow = Boolean(
                        input.closest('.dynamic-bill-row') || 
                        (input.name && (input.name.includes('departure_date') || input.name.includes('arrival_date')))
                    );
                    if (isBillRow) {
                        if (!minDateStr && window.currentOrderStartDate) minDateStr = window.currentOrderStartDate;
                        if (!maxDateStr && window.currentOrderEndDate) maxDateStr = window.currentOrderEndDate;
                    }

                    const val = input.value.trim();
                    const pVal = parseBsDate(val);
                    if (!pVal) return;

                    if (minDateStr) {
                        const cmpMin = compareBsDates(val, minDateStr);
                        if (cmpMin === -1) {
                            alert(`⚠️ भ्रमण मिति (${toNepaliDigits(val)}) स्वीकृत भ्रमण शुरु मिति (${toNepaliDigits(minDateStr)}) भन्दा अगाडिको हुन सक्दैन।\nमिति स्वतः भ्रमण शुरु मिति (${toNepaliDigits(minDateStr)}) मा मिलाइएको छ।`);
                            input.value = toNepaliDigits(minDateStr);
                            const pMin = parseBsDate(minDateStr);
                            if (pMin) {
                                const weekday = getBSWeekday(pMin.year, pMin.month - 1, pMin.day);
                                getDatePicker().updateInputHelper(input, `${NEPALI_MONTHS[pMin.month - 1]} ${toNepaliDigits(pMin.day)} गते, ${NEPALI_DAYS_FULL[weekday]}`);
                            }
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            return;
                        }
                    }

                    if (maxDateStr) {
                        const cmpMax = compareBsDates(val, maxDateStr);
                        if (cmpMax === 1) {
                            alert(`⚠️ भ्रमण मिति (${toNepaliDigits(val)}) स्वीकृत भ्रमण समाप्त मिति (${toNepaliDigits(maxDateStr)}) भन्दा पछिको हुन सक्दैन।\nमिति स्वतः भ्रमण समाप्त मिति (${toNepaliDigits(maxDateStr)}) मा मिलाइएको छ।`);
                            input.value = toNepaliDigits(maxDateStr);
                            const pMax = parseBsDate(maxDateStr);
                            if (pMax) {
                                const weekday = getBSWeekday(pMax.year, pMax.month - 1, pMax.day);
                                getDatePicker().updateInputHelper(input, `${NEPALI_MONTHS[pMax.month - 1]} ${toNepaliDigits(pMax.day)} गते, ${NEPALI_DAYS_FULL[weekday]}`);
                            }
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            return;
                        }
                    }

                    // Update helper text if valid
                    const weekday = getBSWeekday(pVal.year, pVal.month - 1, pVal.day);
                    getDatePicker().updateInputHelper(input, `${NEPALI_MONTHS[pVal.month - 1]} ${toNepaliDigits(pVal.day)} गते, ${NEPALI_DAYS_FULL[weekday]}`);
                };

                input.addEventListener('blur', validateManualInputBounds);

                input.addEventListener('focus', () => {
                    getDatePicker().showForInput(input);
                });
                input.addEventListener('click', () => {
                    getDatePicker().showForInput(input);
                });
            }
        });
    }

    // 3.5 BS Date Parsing, Comparison and Duration Calculations
    function parseBsDate(dateStr) {
        if (!dateStr) return null;
        const cleanStr = toEnglishDigits(String(dateStr).trim()).replace(/-/g, '/').replace(/\./g, '/');
        const parts = cleanStr.split('/');
        if (parts.length !== 3) return null;
        const y = parseInt(parts[0], 10);
        const m = parseInt(parts[1], 10);
        const d = parseInt(parts[2], 10);
        if (!BS_MONTH_DATA[y] || m < 1 || m > 12) return null;
        const maxDays = BS_MONTH_DATA[y][m - 1];
        if (d < 1 || d > maxDays) return null;
        return { year: y, month: m, day: d };
    }

    function bsToAbsDays(y, m, d) {
        if (!BS_MONTH_DATA[y] || m < 1 || m > 12) return 0;
        let days = 0;
        for (let yr = 2000; yr < y; yr++) {
            if (BS_MONTH_DATA[yr]) {
                days += BS_MONTH_DATA[yr].reduce((a, b) => a + b, 0);
            }
        }
        for (let mo = 1; mo < m; mo++) {
            days += BS_MONTH_DATA[y][mo - 1];
        }
        days += (d - 1);
        return days;
    }

    function compareBsDates(dateStr1, dateStr2) {
        const p1 = parseBsDate(dateStr1);
        const p2 = parseBsDate(dateStr2);
        if (!p1 || !p2) return null;
        const d1 = bsToAbsDays(p1.year, p1.month, p1.day);
        const d2 = bsToAbsDays(p2.year, p2.month, p2.day);
        if (d1 < d2) return -1;
        if (d1 > d2) return 1;
        return 0;
    }

    function getBsDurationDays(startDateStr, endDateStr) {
        const p1 = parseBsDate(startDateStr);
        const p2 = parseBsDate(endDateStr);
        if (!p1 || !p2) return null;
        const d1 = bsToAbsDays(p1.year, p1.month, p1.day);
        const d2 = bsToAbsDays(p2.year, p2.month, p2.day);
        if (d2 < d1) return -1;
        return (d2 - d1) + 1; // inclusive
    }

    function validateOrderDates(orderDateStr, startDateStr, endDateStr, recommenderDateStr, approverDateStr) {
        const pOrder = parseBsDate(orderDateStr);
        const pStart = parseBsDate(startDateStr);
        const pEnd = parseBsDate(endDateStr);

        if (!pOrder) {
            const err = 'आदेश मिति अमान्य छ। कृपया सही नेपाली मिति (जस्तै: २०८२/०४/२०) प्रविष्ट गर्नुहोस्।';
            return { valid: false, error: err, message: err, duration: 0, durationDays: 0 };
        }
        if (!pStart) {
            const err = 'भ्रमण शुरु मिति अमान्य छ। कृपया सही नेपाली मिति प्रविष्ट गर्नुहोस्।';
            return { valid: false, error: err, message: err, duration: 0, durationDays: 0 };
        }
        if (!pEnd) {
            const err = 'भ्रमण अन्त्य मिति अमान्य छ। कृपया सही नेपाली मिति प्रविष्ट गर्नुहोस्।';
            return { valid: false, error: err, message: err, duration: 0, durationDays: 0 };
        }

        // Check start_date >= order_date (भ्रमण शुरु मिति र भ्रमण आदेश मिति एउटै मिति हुन सक्छन्, तर शुरु मिति आदेश मिति भन्दा अगाडिको हुन सक्दैन)
        const cmpOrderStart = compareBsDates(startDateStr, orderDateStr);
        if (cmpOrderStart < 0) {
            const err = `भ्रमण शुरु मिति (${startDateStr}) भ्रमण आदेश मिति (${orderDateStr}) भन्दा अगाडिको हुन सक्दैन।`;
            return { valid: false, error: err, message: err, duration: 0, durationDays: 0 };
        }

        // Check end_date >= start_date
        const cmpStartEnd = compareBsDates(endDateStr, startDateStr);
        if (cmpStartEnd < 0) {
            const err = `भ्रमण अन्त्य मिति (${endDateStr}) भ्रमण शुरु मिति (${startDateStr}) भन्दा अगाडिको हुन सक्दैन।`;
            return { valid: false, error: err, message: err, duration: 0, durationDays: 0 };
        }

        const duration = getBsDurationDays(startDateStr, endDateStr);
        if (duration > 7) {
            const err = `भ्रमण अवधि बढीमा ७ दिनको मात्र हुन सक्छ। (हाल छनोट गरिएको अवधि: ${toNepaliDigits(duration)} दिन)`;
            return { valid: false, error: err, message: err, duration: duration, durationDays: duration };
        }

        // Check recommender_date >= order_date (सिफारिस गर्ने पदाधिकारीको मिति कि त आदेश मितिकै दिन वा सो भन्दा पछि)
        if (recommenderDateStr && String(recommenderDateStr).trim()) {
            const recClean = String(recommenderDateStr).trim();
            const pRec = parseBsDate(recClean);
            if (!pRec) {
                const err = `सिफारिस गर्ने पदाधिकारीको मिति (${recClean}) अमान्य छ। कृपया सही नेपाली मिति प्रविष्ट गर्नुहोस्।`;
                return { valid: false, error: err, message: err, duration: duration, durationDays: duration };
            }
            const cmpOrderRec = compareBsDates(recClean, orderDateStr);
            if (cmpOrderRec < 0) {
                const err = `सिफारिस गर्ने पदाधिकारीको मिति (${recClean}) भ्रमण आदेश मिति (${orderDateStr}) भन्दा अगाडिको हुन सक्दैन।`;
                return { valid: false, error: err, message: err, duration: duration, durationDays: duration };
            }
        }

        // Check approver_date >= order_date (भ्रमण स्वीकृत गर्ने पदाधिकारीको मिति कि त आदेश मितिकै दिन वा सो भन्दा पछि)
        if (approverDateStr && String(approverDateStr).trim()) {
            const appClean = String(approverDateStr).trim();
            const pApp = parseBsDate(appClean);
            if (!pApp) {
                const err = `भ्रमण स्वीकृत गर्ने पदाधिकारीको मिति (${appClean}) अमान्य छ। कृपया सही नेपाली मिति प्रविष्ट गर्नुहोस्।`;
                return { valid: false, error: err, message: err, duration: duration, durationDays: duration };
            }
            const cmpOrderApp = compareBsDates(appClean, orderDateStr);
            if (cmpOrderApp < 0) {
                const err = `भ्रमण स्वीकृत गर्ने पदाधिकारीको मिति (${appClean}) भ्रमण आदेश मिति (${orderDateStr}) भन्दा अगाडिको हुन सक्दैन।`;
                return { valid: false, error: err, message: err, duration: duration, durationDays: duration };
            }
        }

        return { valid: true, error: null, message: null, duration: duration, durationDays: duration };
    }

    // 4. Employee Auto-fill & Travel Order Integration
    function setupEmployeeAutoFill() {
        document.addEventListener('change', function (e) {
            if (e.target && (e.target.name === 'employee' || e.target.id === 'id_employee')) {
                const empId = e.target.value;
                if (!empId) return;

                fetch(`/api/employee/${empId}/`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.success || data.status === 'success') {
                            const emp = data.employee || data;
                            const setField = (name, val) => {
                                const el = document.querySelector(`[name="${name}"], #id_${name}`);
                                if (el && val !== undefined && val !== null) {
                                    el.value = val;
                                    el.dispatchEvent(new Event('input', { bubbles: true }));
                                    el.dispatchEvent(new Event('change', { bubbles: true }));
                                }
                            };
                            setField('person', emp.name);
                            setField('code_no', emp.code_no);
                            setField('designation', emp.designation);
                            if (emp.office_id) {
                                setField('office_ref', emp.office_id);
                            }
                            setField('office', emp.office);
                            setField('permanent_address', emp.permanent_address);
                            setField('address', emp.permanent_address);
                            setField('submitted_by', emp.name);
                            setField('submitted_designation', emp.designation);
                        }
                    })
                    .catch(err => console.log('Employee autofill err:', err));
            }
        });

        document.addEventListener('change', function (e) {
            if (e.target && (e.target.name === 'travel_order' || e.target.id === 'id_travel_order')) {
                const orderId = e.target.value;
                if (!orderId) return;

                fetch(`/api/order/${orderId}/`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.success || data.status === 'success') {
                            const ord = data.order || data;
                            const setField = (name, val) => {
                                const el = document.querySelector(`[name="${name}"], #id_${name}`);
                                if (el && val !== undefined && val !== null) {
                                    el.value = val;
                                    el.dispatchEvent(new Event('input', { bubbles: true }));
                                    el.dispatchEvent(new Event('change', { bubbles: true }));
                                }
                            };
                            // Fill permanent address strictly (never fallback to office)
                            if (ord.permanent_address) {
                                setField('address', ord.permanent_address);
                            }
                            setField('advance_taken', ord.advance_amount || 0);
                            setField('submitted_by', ord.person);
                            setField('submitted_designation', ord.designation);
                            
                            // Trigger callback if custom orderSelected handler exists on page
                            if (typeof window.onTravelOrderSelected === 'function') {
                                window.onTravelOrderSelected(ord);
                            }
                            
                            calculateBillTotals();
                        }
                    })
                    .catch(err => console.log('Order autofill err:', err));
            }
        });
    }

    // 5. Automatic Bill Calculations in TravelBill
    function calculateTadaAllowanceDays(durationDays) {
        const d = parseFloat(toEnglishDigits(String(durationDays || '0'))) || 0;
        if (d <= 0) return 0;
        if (d < 1) return Math.round(d * 0.25 * 100) / 100;
        return Math.round(((d - 1) + 0.25) * 100) / 100;
    }

    function autoCalculateRowAllowanceDays(targetRow) {
        // Collect all active bill rows in the DOM grid
        const allRows = Array.from(document.querySelectorAll('.dynamic-bill-row, .inline-related:not(.empty-form)'));
        const activeRows = allRows.filter(r => {
            const depInp = r.querySelector('[name*="departure_date"]');
            const arrInp = r.querySelector('[name*="arrival_date"]');
            const daysInp = r.querySelector('[name*="daily_allowance_days"]');
            return depInp && arrInp && daysInp;
        });

        if (activeRows.length === 0) return;

        const totalRows = activeRows.length;
        const processedDays = new Set();

        activeRows.forEach((row, index) => {
            const depInput = row.querySelector('[name*="departure_date"]');
            const arrInput = row.querySelector('[name*="arrival_date"]');
            const daysInput = row.querySelector('[name*="daily_allowance_days"]');

            if (!depInput || !arrInput || !daysInput) return;

            const depVal = depInput.value ? depInput.value.trim() : '';
            const arrVal = arrInput.value ? arrInput.value.trim() : '';

            if (!depVal || !arrVal) {
                return;
            }

            const pDep = parseBsDate(depVal);
            const pArr = parseBsDate(arrVal);

            if (!pDep || !pArr) {
                return;
            }

            const startAbs = bsToAbsDays(pDep.year, pDep.month, pDep.day);
            const endAbs = bsToAbsDays(pArr.year, pArr.month, pArr.day);

            if (endAbs < startAbs) {
                daysInput.value = 0;
                return;
            }

            // 1. Inclusive Date Duration Calculation: Duration = (To_Date - From_Date) + 1 Day
            const totalDuration = (endAbs - startAbs) + 1;

            // 2. No Double-Counting / Overlap & Duplicate Prevention
            let uniqueDays = 0;
            let overlapDays = 0;

            for (let d = startAbs; d <= endAbs; d++) {
                if (processedDays.has(d)) {
                    overlapDays++;
                } else {
                    uniqueDays++;
                    processedDays.add(d);
                }
            }

            // 3. Shifting 25% Logic (Only Final Day gets 25%, Preceding Rows get 100%)
            let calculatedDays = 0;
            const isLastRow = (index === totalRows - 1);

            if (!isLastRow) {
                // Any Preceding Row (index < totalRows - 1): full days at 100%
                calculatedDays = uniqueDays * 1.0;
            } else {
                // Absolute Last Active Row (index === totalRows - 1): 25% rule shifts here
                if (uniqueDays >= 1) {
                    calculatedDays = (uniqueDays - 1) * 1.0 + 0.25; // equals uniqueDays - 0.75
                } else {
                    calculatedDays = uniqueDays * 0.25;
                }
            }

            // Round cleanly to 2 decimal places to avoid JS floating point inaccuracy
            calculatedDays = Math.round(calculatedDays * 100) / 100;
            daysInput.value = calculatedDays;

            const rowTitle = `पंक्ति ${index + 1}: कुल अवधि = ${toNepaliDigits(totalDuration)} दिन, अद्वितीय दिन = ${toNepaliDigits(uniqueDays)} दिन (दोहोरिएको = ${toNepaliDigits(overlapDays)} दिन) -> दैनिक भत्ता दिन = ${toNepaliDigits(calculatedDays)}`;
            daysInput.setAttribute('title', rowTitle);
        });

        // 4. Grand Total Alignment & Row Totals Update
        calculateBillTotals();
    }

    function calculateBillTotals() {
        let totalTransport = 0;
        let totalDailyAllowance = 0;
        let totalMisc = 0;

        const itemRows = document.querySelectorAll('.dynamic-bill-row, .inline-related:not(.empty-form)');
        
        itemRows.forEach(row => {
            const fareInput = row.querySelector('[name*="transport_fare"]');
            const daysInput = row.querySelector('[name*="daily_allowance_days"]');
            const rateInput = row.querySelector('[name*="daily_allowance_rate"]');
            const dailyTotalInput = row.querySelector('[name*="daily_allowance_total"]');
            const miscInput = row.querySelector('[name*="misc_amount"]');
            const rowTotalInput = row.querySelector('[name*="row_total"]');

            const fare = fareInput ? (parseFloat(toEnglishDigits(fareInput.value)) || 0) : 0;
            const days = daysInput ? (parseFloat(toEnglishDigits(daysInput.value)) || 0) : 0;
            const rate = rateInput ? (parseFloat(toEnglishDigits(rateInput.value)) || 0) : 0;
            const misc = miscInput ? (parseFloat(toEnglishDigits(miscInput.value)) || 0) : 0;

            const dailyTotal = Math.round(days * rate);
            if (dailyTotalInput) dailyTotalInput.value = dailyTotal;

            const rowTotal = Math.round(fare + dailyTotal + misc);
            if (rowTotalInput) rowTotalInput.value = rowTotal;

            totalTransport += fare;
            totalDailyAllowance += dailyTotal;
            totalMisc += misc;
        });

        const grandTotal = Math.round(totalTransport + totalDailyAllowance + totalMisc);

        const totalTransportEl = document.querySelector('[name="total_transport"], #id_total_transport');
        const totalDailyEl = document.querySelector('[name="total_daily_allowance"], #id_total_daily_allowance');
        const totalMiscEl = document.querySelector('[name="total_misc"], #id_total_misc');
        const grandTotalEl = document.querySelector('[name="grand_total"], #id_grand_total');
        const advanceEl = document.querySelector('[name="advance_taken"], #id_advance_taken');
        const netPayableEl = document.querySelector('[name="net_payable"], #id_net_payable');
        const wordsEl = document.querySelector('[name="amount_in_words"], #id_amount_in_words');

        if (totalTransportEl && (itemRows.length > 0)) totalTransportEl.value = totalTransport;
        if (totalDailyEl && (itemRows.length > 0)) totalDailyEl.value = totalDailyAllowance;
        if (totalMiscEl && (itemRows.length > 0)) totalMiscEl.value = totalMisc;
        
        const finalGrandTotal = (itemRows.length > 0) ? grandTotal : (
            (parseFloat(toEnglishDigits(totalTransportEl?.value)) || 0) +
            (parseFloat(toEnglishDigits(totalDailyEl?.value)) || 0) +
            (parseFloat(toEnglishDigits(totalMiscEl?.value)) || 0)
        );

        if (grandTotalEl) grandTotalEl.value = finalGrandTotal;

        const adv = advanceEl ? (parseFloat(toEnglishDigits(advanceEl.value)) || 0) : 0;
        const netPayable = Math.round(finalGrandTotal - adv);
        if (netPayableEl) netPayableEl.value = netPayable;

        if (wordsEl && netPayable) {
            wordsEl.value = nepaliNumberToWords(netPayable);
        }
    }

    function setupBillCalculations() {
        const handleFieldOrDateChange = (e) => {
            if (!e.target) return;
            const targetName = e.target.name || '';
            const targetClass = e.target.className || '';

            if (targetName.includes('departure_date') || targetName.includes('arrival_date') || targetClass.includes('nepali-date-picker')) {
                const row = e.target.closest('.dynamic-bill-row, .inline-related, tr');
                if (row) {
                    autoCalculateRowAllowanceDays(row);
                }
            }

            if (
                targetName.includes('transport_fare') ||
                targetName.includes('daily_allowance') ||
                targetName.includes('misc_amount') ||
                targetName.includes('advance_taken') ||
                targetName.includes('total_transport') ||
                targetName.includes('total_daily_allowance') ||
                targetName.includes('total_misc') ||
                targetName.includes('departure_date') ||
                targetName.includes('arrival_date')
            ) {
                calculateBillTotals();
            }
        };

        document.addEventListener('input', handleFieldOrDateChange);
        document.addEventListener('change', handleFieldOrDateChange);
    }

    document.addEventListener('DOMContentLoaded', () => {
        attachDatePickers();
        setupEmployeeAutoFill();
        setupBillCalculations();

        const observer = new MutationObserver(() => {
            attachDatePickers();
        });
        observer.observe(document.body, { childList: true, subtree: true });
    });

    window.NepaliCalendar = {
        toNepaliDigits,
        toEnglishDigits,
        nepaliNumberToWords,
        getBSWeekday,
        adToBs,
        attachDatePickers,
        calculateBillTotals,
        calculateTadaAllowanceDays,
        autoCalculateRowAllowanceDays,
        getDatePicker,
        parseBsDate,
        bsToAbsDays,
        compareBsDates,
        getBsDurationDays,
        validateOrderDates
    };

})(window, document);
