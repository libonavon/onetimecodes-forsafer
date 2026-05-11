import sqlite3, os


DB_PATH = f'{os.environ['PROGRAMDATA']}\\KioskTorani\\LocalSaferServer.db'


class User():

    def __init__(
            self,
            user_name: str,
            password: str = "",
            password_required: bool =True):

        self.__con = sqlite3.connect(DB_PATH)
        self.__cur: sqlite3.Cursor

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
    
    
    def get_full_name(self, last_name_last=True):
        if last_name_last:
            return f'{self.__first_name} {self.__last_name}'
        else:
            return f'{self.__last_name} {self.__first_name}'
        

    def is_admin(self):
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
    