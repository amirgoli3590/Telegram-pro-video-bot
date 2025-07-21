import requests

MERCHANT_ID = 'YOUR_MERCHANT_ID'  # 🔥 وقتی زرین‌پال رو ساختی اینجا جایگذاری کن
CALLBACK_URL = 'https://yourdomain.ir/verify'  # 🔥 دامنه تایید پرداخت
AMOUNT = 10000  # مبلغ اشتراک ماهانه به تومان
DESCRIPTION = 'خرید اشتراک ماهانه ربات'

def create_payment_link(user_id):
    data = {
        "merchant_id": MERCHANT_ID,
        "amount": AMOUNT,
        "callback_url": CALLBACK_URL + f"?user_id={user_id}",
        "description": DESCRIPTION
    }
    headers = {'content-type': 'application/json'}
    response = requests.post('https://api.zarinpal.com/pg/v4/payment/request.json', json=data, headers=headers)
    result = response.json()
    if 'data' in result and result['data'].get('code') == 100:
        link = f"https://www.zarinpal.com/pg/StartPay/{result['data']['authority']}"
        authority = result['data']['authority']
        return link, authority
    else:
        return None, None

def verify_payment(authority, status):
    if status != 'OK':
        return False
    data = {
        "merchant_id": MERCHANT_ID,
        "amount": AMOUNT,
        "authority": authority
    }
    headers = {'content-type': 'application/json'}
    response = requests.post('https://api.zarinpal.com/pg/v4/payment/verify.json', json=data, headers=headers)
    result = response.json()
    if 'data' in result and result['data'].get('code') == 100:
        return True
    else:
        return False
