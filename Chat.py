import pyrebase
def noquote(s):
    return s
pyrebase.pyrebase.quote = noquote
import pyrebase
import requests
import json
import datetime
from firebase_admin import db
from firebase import firebase
from firebase.firebase import FirebaseApplication

from getpass import getpass

firebaseConfig = {
    #FIREBASE CONFIG DATA
}

firebase_auth = pyrebase.initialize_app(firebaseConfig)
auth = firebase_auth.auth()


def clear_Screen():
    from IPython.display import clear_output
    clear_output()
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def register_user():
    db = firebase_auth.database()
    registered_success = False
    user_fname = input("Please Enter Your First Name : ")
    user_lname = input("Please Enter Your Last Name : ")
    user_email = input("Please Enter Your Email Address : ")
    username = input("Please Enter Your User-Name : ")
    user_password = input("Please Enter Your Password : ")

    user_confirmPass = input("Please Confirm Your Password : ")
    if user_password != user_confirmPass:
        while user_password == user_confirmPass:
            print("Both passwords are different. Please re-enter the passwords. ")
            user_password = input("Please Enter Your Password : ")
            user_confirmPass = input("Please Confirm Your Password : ")
    if user_password == user_confirmPass:
        temp_val = db.child("users").child(username).get().val()
        if (type(temp_val) == type(None)):
            try:
                auth.create_user_with_email_and_password(user_email, user_password)
                registered_success = True
            except:
                print("The User Already Exists !!! ")
                return False
    else:
        print("Username is already selected")
        return False

    if (registered_success):
        data = {'First Name': user_fname, 'Last Name': user_lname, 'Email': user_email}
        db.child("users").child(username).set(data)
        print("Account Registered Successfully! ")
        return True


def login():
    login_data_list = []
    Email = input("Please Enter Your Email Address : ")
    Password = input("Please Enter Your Password : ")
    try:
        user = auth.sign_in_with_email_and_password(Email, Password)
        print("Login Successfull!")
        login_data_list.append(True)
        login_data_list.append(Email)
        return login_data_list
    except:
        print("Either Email Or Password Is Incorrect")
        login_data_list.append(False)
        return login_data_list


def reset_password():
    try:
        email_addr = input("Please Enter Your Email Address : ")
        auth.send_password_reset_email(email_addr)
        print("Please Check Your Email For Password Reset Instructions !")
    except:
        print("No User With This Email Address! ")


def get_username(email):
    username = ""
    db = firebase_auth.database()
    username = db.child("users").order_by_child("Email").equal_to(email).get()
    for user in username.each():
        username = user.key()
    return username


def send_message(Email):
    login_email = Email
    receiver_email = input('Please enter the Email where you want to send message : ')
    login_username = get_username(login_email)
    receiver_username = get_username(receiver_email)
    if type(receiver_username) == type("hi"):
        db = firebase_auth.database()
        message = input("Please enter the message that you want to send : ")
        date_now = str(datetime.datetime.now())
        data = {"Message": login_username + " : \t" + message + "     \t\t" + (date_now[0:16])}
        print(login_username)
        firebasedb = firebase.FirebaseApplication(DBPATH, None)
        message_id = firebasedb.post('message/', data)
        message_id = message_id["name"]
        # store the message id on both emails.
        sender_receiver_key = login_username + receiver_username
        total_messages = 0
        if not db.child("message-details").child(sender_receiver_key).shallow().get().val():
            total_messages = 0
        else:
            total_messages = db.child("message-details").child(sender_receiver_key).child("Totalmsg").get().val()
        total_messages = total_messages + 1
        message_num = "MSG" + str(total_messages)
        msg_id = {message_num: message_id, "Totalmsg": total_messages}
        db.child("message-details").child(sender_receiver_key).update(msg_id)
        receiver_sender_key = receiver_username + login_username
        db = firebase_auth.database()
        db.child("message-details").child(receiver_sender_key).update(msg_id)
        add_friend(login_username, receiver_username)
    else:
        print("User Doesnt Exists")


def read_messages(Email_1 , Email_2):
    login_email = Email_1
    receiver_email = Email_2
    login_username = get_username(login_email)
    receiver_username = get_username(receiver_email)
    if type(receiver_username) == type("hi"):
        chatData_key = login_username + receiver_username
        db = firebase_auth.database()
        total_messages = db.child("message-details").child(chatData_key).child("Totalmsg").get().val()
        messageslist = []
        for i in range(0, total_messages):
            message_no = "MSG" + str(i + 1)
            x = db.child("message-details").child(chatData_key).child(message_no).get().val()
            messageslist.append(db.child("message").child(x).child("Message").get().val())
        if (len(messageslist) > 0):
            for i in range(0, len(messageslist)):
                print(messageslist[i])
        else:
            print(f"You have no chat history with {receiver_username}")
    else:
        print("User doesnt Exists")


def add_friend(sender, receiver):
    db = firebase_auth.database()
    total_friends_sender = 0
    if not db.child("friends").child(sender).shallow().get().val():
        total_friends_sender = 0
    else:
        total_friends_sender = db.child("friends").child(sender).child("totalfriends").get().val()
    friend_already_present = False
    if total_friends_sender > 0:
        for i in range(1, total_friends_sender + 1):
            friend_id = "FRIEND-" + str(i)
            if db.child("friends").child(sender).child(friend_id).get().val() == receiver:
                friend_already_present = True

    if friend_already_present == False:
        # for sender
        friend_id_sender = "FRIEND-" + str(total_friends_sender+ 1)
        data = {friend_id_sender: receiver, "totalfriends": (total_friends_sender + 1)}
        db.child("friends").child(sender).update(data)

        # for receiver
        if not db.child("friends").child(receiver).shallow().get().val():
            total_friends_receiver = 0
        else:
            total_friends_receiver = db.child("friends").child(receiver).child("totalfriends").get().val()
        friend_id_receiver = "FRIEND-" + str(total_friends_receiver + 1)
        data = {friend_id_receiver: sender, "totalfriends": (total_friends_receiver + 1)}
        db.child("friends").child(receiver).update(data)

def view_all_friends(login):
    username = get_username(login)
    db = firebase_auth.database()
    total_friends= 0
    if not db.child("friends").child(username).shallow().get().val():
        total_friends = 0
    else:
        total_friends = db.child("friends").child(username).child("totalfriends").get().val()
    friends_list = []

    if total_friends >0:
        for i in range (1 , total_friends +1):
            friends_id = "FRIEND-"+str(i)
            friends_list.append(db.child("friends").child(username).child(friends_id).get().val())
        for i in range(0,len(friends_list)):
            print(friends_list[i]+" \t Press "+str(i+1)+" to read all the messages")
        user_input = input("Press Between (1 to "+str(len(friends_list))+" ) to read the messages or Press x to go back ")
        if user_input != 'x' or user_input != 'X' :
            read_messages(login , db.child("users").child(friends_list[int(user_input)-1]).child("Email").get().val())










def Menu_after_login(Email):
    clear_Screen()
    print("Account Logged In Successfully!")
    print("Please Select The Following Options")
    print("Press 1 to send a new message ")
    print("Press 2 to read the messages ")
    print("Press 3 to view all friends")
    print("Press 4 to logout ")
    user_inpt = input ("Your Choice : ")
    if int(user_inpt) == 1:
        send_message(Email)
        print()
        user_inptt = input("Press 1 to send another message or Press 2 to go back")
        if int(user_inptt) == 1:
            clear_Screen()
            receiver_email = input("Please enter the email of the user whose messages you want to read")
            send_message(Email)
        elif int(user_inptt) == 2:
            Menu_after_login(Email)
    if int(user_inpt) == 2:
        clear_Screen()
        read_messages(Email)
        print()
        user_inptt = input("Press 1 to go back")
        if int(user_inptt) == 1:
            Menu_after_login(Email)
    if int(user_inpt) == 3:
        view_all_friends(Email)
        print()
        user_inptt = input("Press 1 to go back")
        if int(user_inptt ) == 1:
            view_all_friends(Email)
    if int (user_inpt) == 4:
        Menu_before_login()


def Menu_before_login():
  loggedIn_Email = ""
  clear_Screen()
  num = 1
  while num == 1:
    logged_in = False
    print()
    print("Press 1 to login")
    print("Press 2 to create a new account")
    print("Press 3 to reset password")
    print("Press 4 to exit")
    user_input = input("Your Choice : ")
    if int(user_input) == 1:
      logged_in = login()
      flag = logged_in[0]
      if flag:
        loggedIn_Email = logged_in[1]
        print("Welcome User ! ")
        num = 2
    if int(user_input) == 2:
      flag = register_user()
      print("")
      if (flag):
        print("Please Sign In ")
        logged_in = login()
        if logged_in:
          print("Welcome User ! ")
          num = 2
      else:
        Menu_before_login()
    if int(user_input) == 3:
      reset_password()
      print()
      Menu_before_login()
    if int(user_input) == 4:
      num = 3
  if(num == 2):
    Menu_after_login(loggedIn_Email)

Menu_before_login()
