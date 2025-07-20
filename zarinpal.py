import requests

MERCHANT_ID = 'YOUR_MERCHANT_ID'  # 👈 شب جای MerchantID خودتو می‌ذاری
CALLBACK_URL = 'https://yourdomain.com/callback'  # 👈 بعد روی VPS اینو ست می‌کنیم

def create_payment_link(user_id):
    data = {
        "MerchantID": MERCHANT_ID,
        "Amount": 10000,  # مبلغ اشتراک (به تومان)
        "CallbackURL": CALLBACK_URL,
        "Description": f"خرید اشتراک توسط کاربر {user_id}"
    }
    response = requests.post('https://api.zarinpal.com/pg/v4/payment/request.json', json=data)
    res = response.json()
    if res['data']['code'] == 100:
        link = f"https://www.zarinpal.com/pg/StartPay/{res['data']['authority']}"
        return link, res['data']['authority']
    return None, None

def verify_payment(authority):
    data = {
        "MerchantID": MERCHANT_ID,
        "Amount": 10000,
        "Authority": authority
    }
    response = requests.post('https://api.zarinpal.com/pg/v4/payment/verify.json', json=data)
    res = response.json()
    return res['data']['code'] == 100
