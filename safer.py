import sqlite3, os, requests


class User():

    def __init__(
            self,
            db_path: str,
            user_name: str,
            password: str = "",
            password_required: bool =True):

        self.__con = sqlite3.connect(db_path)
        self.__cur: sqlite3.Cursor
        self.__user_name = user_name

        self.__cur = self.__con.cursor()

        exe = f'SELECT rowid, LastName, FirstName, UserType FROM users WHERE username="{user_name}"'
        if password_required:
            if password == '':
                raise ValueError('The password is undefind')
            exe += f' AND password={password}'

        status_answer = self.__cur.execute(exe).fetchall()
        if not status_answer:
            raise ValueError('User name is incurrect')
        
        answer = status_answer[0]
        self.__id = answer[0]
        self.__last_name = answer[1]
        self.__first_name = answer[2]
        self.__user_type = answer[3]

        exe = 'SELECT SUM(Amount) FROM Payments WHERE UserID=?'
        answer = self.__cur.execute(exe, (self.__id,)).fetchall()[0]

        self.__payments = answer[0]

        exe = 'SELECT SUM(TotalPages), SUM(TotalSeconds), SUM(Amount) FROM Actions WHERE UserID=?'
        answer = self.__cur.execute(exe, (self.__id,)).fetchall()[0]

        self.__pages = answer[0]
        self.__seconds = answer[1]
        self.__amount = answer[2]


    def get_id(self):
        return self.__id
    
    
    def get_full_name(self, last_name_last=True) -> str:
        return f'{self.__first_name} {self.__last_name}' if last_name_last else f'{self.__last_name} {self.__first_name}'
        

    def is_admin(self) -> bool:
        return self.__user_type == 2

    def get_ytra(self):
        return self.__payments - self.__amount

    def get_pages(self):
        return self.__pages

    def get_use_time(self, format=False):
        if format:
            return '{}:{}:{}'.format(
                self.__seconds // 3600,
                (self.__seconds % 3600) // 60,
                self.__seconds % 60
            )
        return self.__seconds
    
    def get_user_name(self) -> str:
        return self.__user_name
    
    def recharge(self, amount) -> bool:

        url = 'http://localhost:8414/LocalSaferServer'  # Replace with your server URL

        payload =  f'''<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
        <s:Body>
        <CreatePaymentForUser xmlns="http://tempuri.org/">
        <userId>{self.__id}</userId>
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
