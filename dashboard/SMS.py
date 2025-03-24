import requests

def sendSMS(mobile, code):
    url = "https://api.umeskiasoftwares.com/api/v1/sms"
    headers = {
        "Content-Type" : "application/json"
    }
    json = {
        "api_key":"NUdYQ0UwUEw6a3Fra28yZmQ=",
        "email":"kembohititoh@gmail.com",
        "Sender_Id": "UMS_SMS",
        "message": f"Your verification code is {code}, use it to verify your Quepter Youth Hub Account.",
        "phone":f"{mobile}"
    }
    try:
        res = requests.post(url=url, json=json, headers=headers)
        print(res.text)
        mes = res.json()
        if mes['success'] == "200":
            #request_id = mes['request_id']
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return None