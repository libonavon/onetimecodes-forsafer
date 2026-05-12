import tkinter as tk, subprocess
from payments import *
from tkinter import EventType
import safer


def mange_conf(id):

    if str(id) in config.sections():
        return dict(config[str(id)])
    else:
        return dict(config['GLOBAL PAY OPTIONS'])


def change_color(e: tk.Event):
    
    if e.type == EventType.Enter:
        e.widget['bg'] = '#E1E1E1'
    elif e.type == EventType.Leave:
        e.widget['bg'] = BG


def lable_click_un(e: tk.Event):

    global safer_user

    if e.type == EventType.Key:
        if e.keycode != 13:
            return

    user_name = input_user_name.get()

    if is_user_blockd(user_name):
        lable_high['text'] = 'נחסמת'
        lable_user_name['text'] = 'אנא פנה למנהל'
        lable_under['text'] = 'שימוש לא ראוי במערכת'
        lable_ytra.destroy()
        input_user_name.destroy()
        lable_click.bind('<Button-1>', end_gue)
        root.bind('<Key>', end_gue)
        return

    try:
        safer_user = safer.User(user_name, password_required=False)
    except Exception as ValueError:
        input_user_name.delete(0, 'end')
        lable_under['text'] = 'תעודת זהות שגויה'
        return


    lable_under['text'] = ''
    lable_high['text'] = f'שלום {safer_user.get_full_name()}'
    lable_user_name['text'] = f'יתרתך: ₪{round(safer_user.get_ytra(), 2)}'
    lable_ytra['text'] = ':לטעינה הקש קוד'
    input_user_name.delete(0, 'end')
    input_user_name['show'] = ''

    lable_click.bind('<Button-1>', lable_click_vf)
    input_user_name.bind('<Key>', lable_click_vf)

    if safer_user.is_admin():
        mnager_click.place(width=100, height=30, x=50, y=240)
        mnager_click.bind('<Button-1>', admin_login)


def lable_click_vf(e: tk.Event):

    global count
    count = 0

    if count > 2:
        block_user(safer_user.get_user_name())
        root.quit()

    if e.type == EventType.Key:
        if e.keycode != 13:
            return

    code = input_user_name.get()

    if len(code) != 6 or not code.isdigit():
        input_user_name.delete(0, 'end')
        lable_under['text'] = 'קוד שגוי'
        return

    status = find_if_code_is_true(code)

    if not status[0]:
        count += 1
        input_user_name.delete(0, 'end')
        lable_under['text'] = 'קוד שגוי'
        return
    
    if status[0]:
        lable_under['text'] = ''
        status_charge = safer_user.recharge(status[1])
        code_not_active(code, safer_user.get_full_name())
        lable_user_name['text'] = 'יתרתך ₪{}'.format(int((safer_user.get_ytra()) + status[1]))
        input_user_name.place(width=0)

    if status_charge:
        lable_ytra['text'] = 'טעינה בוצעה בהצלחה'
        lable_under['text'] = ''
    else:
        lable_ytra['text'] = ''
        lable_user_name['text'] = 'יתרתך ₪{}'.format(int(safer_user.get_ytra()))
        lable_under['text'] = 'טעינה נכשלה, פנה למנהל'

    input_user_name.bind('<Key>', end_gue)
    lable_click.bind('<Button-1>', end_gue)


def end_gue(e: tk.Event):
    root.quit()


def c_f_code(e: tk.Event):
    code_file = f'{PROGRAM_DATA_BASE}\\codes{safer_user.get_id()}.txt'
    link_file = f'{USER_DESKTOP}\\codes{safer_user.get_full_name()}.txt'
    manager = safer_user.get_id()

    if str(manager) not in config.sections():
        section = 'GLOBAL PAY OPTIONS'
    else:
        section = str(manager)

    payments = [int(i) for i in config[section]['payments'].split(',')]
    limits = int(config[section]['limit'])

    create_file_of_codes(code_file, link_file, manager, payments, limits)
    lable_under['text'] = 'קודים נוצרו בהצלחה'


def kill_process(e):

    # Define your PowerShell command
    powershell_command = "Stop-Process -Name KioskToraniV1"  

    # Execute the command and capture output
    process = subprocess.Popen(
        ['powershell.exe', '-Command', powershell_command],
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        shell=True  # Necessary for running PowerShell commands directly
    )
    stdout, stderr = process.communicate()

    # Print the output (decode from bytes to string)
    output = stdout.decode('utf-8')
    print(output)

    if stderr:
        print("Error:", stderr.decode('utf-8'))

    root.quit()


def manager_settings(e: tk.Event):

    setting_click['text'] = 'אישור'
    kill_program_click.destroy()
    mnager_click.destroy()
    settings = mange_conf(safer_user.get_id())
    payments = settings['payments']
    limit = settings['limit']

    pay_ent.place(width=80, height=30, x=5, y=150)
    pay_ent.insert(0,payments)

    pay_lab['text'] = ':סוגי קודים להנפקה\nמספרים מופרדים\nבפסיק'
    pay_lab.place(width=110, height=50, x=90, y=150)

    lim_ent.place(width=80, height=30, x=5, y=220)
    lim_ent.insert(0, limit)

    lim_lab['text'] = ':כמות קודים מכל סוג'
    lim_lab.place(width=110, height=30, x=90, y=220)

    setting_click.bind('<Button-1>', active_set)


def active_set(e: tk.Event):

    try:
        [int(i) for i in pay_ent.get().split(',')]
        int(lim_ent.get())
    except:
        return

    if not str(safer_user.get_id()) in config.sections():
        config[str(safer_user.get_id())] = {}

    config[str(safer_user.get_id())]['payments'] = pay_ent.get()
    config[str(safer_user.get_id())]['limit'] = lim_ent.get()

    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        config.write(f)

    root.quit()


def admin_login(e: tk.Event):

    lable_under['text'] = ''
    lable_user_name['text'] = 'ברוכים הבאים לממשק ניהול'
    lable_ytra['text'] = ':הקש קוד ניהול'
    input_user_name['show'] = '*'
    mnager_click.place(width=0)
    lable_click.bind('<Button-1>', admin_ok)
    input_user_name.bind('<Key>', admin_ok)


def admin_ok(e: tk.Event):

    if e.type == EventType.Key:
        if e.keycode != 13:
            return

    code = input_user_name.get()
    if get_code(SETTINGS_FILE) != code:
        lable_under['text'] = 'קוד שגוי'
        input_user_name.delete(0, 'end')
        return

    lable_under['text'] = ''
    mnager_click['text'] = 'קודים'
    kill_program_click['text'] = 'מחשב'
    mnager_click.place(width=90, height=30, x=5, y=240)
    kill_program_click.place(width=90, height=30, x=100, y=240)
    setting_click.place(width=90, height=30, x=55, y=100)
    lable_ytra.destroy()
    input_user_name.destroy()
    lable_click.destroy()
    mnager_click.bind('<Button-1>', c_f_code)
    kill_program_click.bind('<Button-1>', kill_process)
    setting_click.bind('<Button-1>', manager_settings)


FONT = 'Calibri 14'
BG = '#F0F0F0'

root = tk.Tk()
root.title('טעינה')
root.geometry('200x300')
root.resizable(False, False)
root['bg'] = BG
root.iconbitmap('icon.ico')


lable_high = tk.Label(root, text='טעינה באמצעות קוד', font=FONT + ' bold', bg=BG)
lable_high.place(height=25, width=200, x=0, y=20)

lable_user_name = tk.Label(root, text='ברוך הבא', font=FONT, bg=BG)
lable_user_name.place(height=25, width=200, x=0, y=55)

lable_ytra = tk.Label(root, text=':הקש תעודת זהות', font=FONT, bg=BG)
lable_ytra.place(height=25, width=200, x=0, y=90)

input_user_name = tk.Entry(root, show='*', font=FONT)
input_user_name.place(height=25, width=100, x=50, y=125)
input_user_name.focus()

lable_click = tk.Label(root, text='אישור', font='Calibri 18 bold', bg=BG)
lable_click.place(width=80, height=30, x=60, y=170)

lable_under = tk.Label(root, text='', font=FONT, bg=BG, fg='#ff0000')
lable_under.place(width=200, height=25, x=0, y=205)

mnager_click = tk.Label(root, text='ניהול', font='Calibri 18 bold', bg=BG)
kill_program_click = tk.Label(root, text='מחשב', font='Calibri 18 bold', bg=BG)
setting_click = tk.Label(root, text='הגדרות', font='Calibri 18 bold', bg=BG)

# Elements for addmin settings
pay_ent = tk.Entry(root, font='Calibri 18 bold')
pay_lab = tk.Label(root, font='Calibri 11')
lim_ent = tk.Entry(root, font='Calibri 18 bold')
lim_lab = tk.Label(root, font='Calibri 11')


lable_click.bind('<Enter>', change_color)
lable_click.bind('<Leave>', change_color)
lable_click.bind('<Button-1>', lable_click_un)
input_user_name.bind('<Key>', lable_click_un)
mnager_click.bind('<Enter>', change_color)
kill_program_click.bind('<Enter>', change_color)
setting_click.bind('<Enter>', change_color)
mnager_click.bind('<Leave>', change_color)
kill_program_click.bind('<Leave>', change_color)
setting_click.bind('<Leave>', change_color)


root.mainloop()
