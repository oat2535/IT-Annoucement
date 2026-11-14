"""Shared display-formatting helpers for the announcements app."""

THAI_WEEKDAYS = {
    0: 'วันจันทร์', 1: 'วันอังคาร', 2: 'วันพุธ', 3: 'วันพฤหัสบดี',
    4: 'วันศุกร์', 5: 'วันเสาร์', 6: 'วันอาทิตย์',
}

THAI_MONTHS = {
    1: 'มกราคม', 2: 'กุมภาพันธ์', 3: 'มีนาคม', 4: 'เมษายน',
    5: 'พฤษภาคม', 6: 'มิถุนายน', 7: 'กรกฎาคม', 8: 'สิงหาคม',
    9: 'กันยายน', 10: 'ตุลาคม', 11: 'พฤศจิกายน', 12: 'ธันวาคม',
}

ENGLISH_WEEKDAYS = {
    0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
    4: 'Friday', 5: 'Saturday', 6: 'Sunday',
}

ENGLISH_MONTHS = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December',
}


def format_operate_date_defaults(date_obj):
    """Return (thai_text, english_text) for the "วันที่ดำเนินการ" card, for date_obj.

    Names are looked up from fixed tables rather than strftime('%A'/'%B') so the
    result is identical regardless of the server's locale configuration, and
    matches the Thai/English pair the front-end's own sync logic produces.
    """
    weekday = date_obj.weekday()
    buddhist_year = date_obj.year + 543

    thai_text = f"{THAI_WEEKDAYS[weekday]}ที่ {date_obj.day} {THAI_MONTHS[date_obj.month]} {buddhist_year}"
    english_text = f"{ENGLISH_WEEKDAYS[weekday]}, {date_obj.day} {ENGLISH_MONTHS[date_obj.month]} {date_obj.year}"

    return thai_text, english_text
