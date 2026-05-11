import requests


def main(userid, amount):
    url = 'http://localhost:8414/LocalSaferServer'  # Replace with your server URL

    payload =  f'''<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
    <s:Body>
    <CreatePaymentForUser xmlns="http://tempuri.org/">
    <userId>{userid}</userId>
    <amount>{amount}</amount>
    <PaymentMethodeName/></CreatePaymentForUser>
    </s:Body>
    </s:Envelope>'''

    len_in_bites = len(payload.encode('utf-8'))

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://tempuri.org/ILocalSaferServer/CreatePaymentForUser",
        "Host": "localhost:8414",
        "Content-Length": f'{len_in_bites}',
        "Expect": "100-continue",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive"
    }

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        print("Payment successful!")
        print(response.text)  # Print the server's response
        return True
    else:
        print(f"Login failed with status code: {response.status_code}")
        return False

if __name__ == "__main__":
    main(22, 5)
