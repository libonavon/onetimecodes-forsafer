import sqlite3, datetime, os
from random import randint
from test import User
from configparser import ConfigParser


def create_codes(pay, sum, manager):
    
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    try:
        exe = 'SELECT * FROM codes'
        answer = cur.execute(exe).fetchall()
    except Exception as OperationalError:
        cur.execute('CREATE TABLE codes (code, pay, manager, allowed, time_used, user)')
        con.commit()

    exe = 'INSERT INTO codes VALUES (?, ?, ?, 1, 0, 0)'
    for _ in range(sum):
        cur.execute(exe, (str(randint(0,999999)).zfill(6), pay, manager,))

    con.commit()
    con.close()

    return True


def get_string_of_codes(payment, limit, manager):

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    exe = "SELECT code FROM codes WHERE allowed=1 and pay=? and manager=? LIMIT ?"
    codes = []

    try:
        for i in payment:
            codes.append([i[0] for i in cur.execute(exe, (i, manager, limit,)).fetchall()])
    except Exception as OperationalError:
        create_codes(payment[0], manager=manager)
        return get_string_of_codes(payment, limit, manager)

    for i in range(len(codes)):
        if len(codes[i]) < limit:
            create_codes(payment[i], manager=manager)
            return get_string_of_codes(payment, limit, manager)

    code_string = ''

    for i in payment:
        code_string += 'קוד {}\t\t'.format(i)
    code_string += '\n'

    for i in range(limit):
        for j in range(len(codes)):
            code_string += '{}\t\t'.format(codes[j][i])
        code_string += '\n'

    con.commit()
    con.close()

    return code_string


def find_if_code_is_true(code):

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    exe = 'SELECT * FROM codes WHERE code=? AND allowed=1'

    # The code is stored in the database as text, Because it sometimes starts at 0.
    text = cur.execute(exe, (str(code),)).fetchall() 

    if bool(text):
        return True, text[0][1]
    else: return False, 0


def get_user_data(user_name):

    user_data = {}

    user = User(user_name=user_name, password_required=False)

    user_data['id'] = user.get_id()
    user_data['name'] = user.get_full_name()
    user_data['username'] = user_name
    user_data['usertype'] = user.is_admin()
    user_data['count'] = 0

    try:
        user_data['ytra'] = user.get_ytra()
    except Exception as TypeError:
        user_data['ytra'] = 0

    return user_data


def create_file_of_codes(file_path, link_file_path, manager, payment, limit):

    text = get_string_of_codes(payment, limit, manager)

    with open(file_path, 'w') as f:
        f.write(text)
    
    if not os.path.islink(link_file_path):
        os.symlink(file_path, link_file_path)

    return


def code_not_active(code, user):

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    
    time = datetime.datetime.now()
    exe = '''UPDATE codes SET allowed=0, time_used=?, user=? WHERE code=?'''
    cur.execute(exe, (time, user, code,))

    con.commit()
    con.close()


def get_code(setting_file):

    with open(setting_file, 'r', encoding='utf-8') as f:
        text = f.read()

    return text[text.find('<ManagerPassword>') + len('<ManagerPassword>'):text.find('</ManagerPassword>')]


def start():

    global DB_PATH, SAFER_DB_PATH, SETTINGS_FILE, USERS_BLACKLIST, LINK_USERS_BLACKLIST, PROGRAM_DATA_BASE, USER_DESKTOP, CONFIG_PATH, config

    current_path = os.environ['userprofile']
    CONFIG_PATH = f'{current_path}\\cfs_config.ini'
    
    if not os.path.isfile(CONFIG_PATH):

        config = ConfigParser()

        program_data = os.environ['ProgramData']
        user_profile = os.environ['userprofile']

        config['PATH'] = {
            'CONFIG_PATH': CONFIG_PATH,
            'DB_PATH': f'{program_data}\\codes\\data.db',
            'SAFER_DB_PATH': f'{program_data}\\KioskTorani\\LocalSaferServer.db',
            'SETTINGS_FILE': f'{program_data}\\KioskTorani\\settings.xml',
            'USERS_BLACKLIST': f'{program_data}\\codes\\blacklist.txt',
            'LINK_USERS_BLACKLIST': f'{user_profile}\\Desktop\\חסומים.txt',
            'PROGRAM_DATA_BASE': f'{program_data}\\codes',
            'USER_DESKTOP': f'{user_profile}\\Desktop',
        }
        config['GLOBAL PAY OPTIONS'] = {
            'payments': '5,10,20',
            'limit': '10' 
        }

        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            config.write(f)

    config = ConfigParser()
    config.read(CONFIG_PATH, encoding='utf-8')
    paths = dict(config.items('PATH'))

    # PROGRAM_DATA = os.environ['PROGRAMDATA']
    # USER_PROFILE = os.environ['USERPROFILE']
    DB_PATH = paths['db_path']
    SAFER_DB_PATH = paths['safer_db_path']
    SETTINGS_FILE = paths['settings_file']
    USERS_BLACKLIST = paths['users_blacklist']
    LINK_USERS_BLACKLIST = paths['link_users_blacklist']
    PROGRAM_DATA_BASE = paths['program_data_base']
    USER_DESKTOP = paths['user_desktop']


    if not os.path.isdir(PROGRAM_DATA_BASE):
        os.mkdir(PROGRAM_DATA_BASE)
    if not os.path.isfile(USERS_BLACKLIST):
        with open(USERS_BLACKLIST, 'w') as f:
            f.write('')
    if not os.path.islink(LINK_USERS_BLACKLIST):
        os.symlink(USERS_BLACKLIST, LINK_USERS_BLACKLIST)


def block_user(user_name):

    with open(USERS_BLACKLIST, 'a') as f:
        f.write(f'{user_name},')


def is_user_blockd(user_name):

    try:
        with open(USERS_BLACKLIST, 'r') as f:
            users = f.read().split(',')
    except Exception as FileNotFoundError:
        return False

    return user_name in users and user_name != ''

start()
