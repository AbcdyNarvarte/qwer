import tkinter as tk
from tkcalendar import Calendar
from tkcalendar import DateEntry
from tkinter import ttk
from tkinter import messagebox, filedialog
import customtkinter
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage
from PIL import Image
import sqlite3
import time
from datetime import datetime, timedelta
import pytz
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
import os
import uuid
import hashlib
import bcrypt
import logging





from pages_handler import FrameNames
from global_func import get_credentials


class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='white')

        self.option_menu = CTkFrame(self, fg_color="#00117F", height=60)
        self.option_menu.pack(side="top", fill="x", pady=(0, 10))
        # LP_NB - LOBBY PAGE NAV BAR
        self.lp_nb_btn()

        self.login_act = logging.getLogger('LOGIN_ACT')
        self.login_act.setLevel(logging.INFO)
        act_handler = logging.FileHandler('C:/capstone/log_f/login.log')
        act_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        act_handler.setFormatter(act_formatter)
        self.login_act.addHandler(act_handler)
        self.login_act.propagate = False

        self.login_warning = logging.getLogger('LOGIN_WARNING')
        self.login_warning.setLevel(logging.WARNING)
        warn_handler = logging.FileHandler('C:/capstone/log_f/login.log')
        warn_handler.setFormatter(act_formatter)
        self.login_warning.addHandler(warn_handler)
        self.login_warning.propagate = False

        self.login_error = logging.getLogger('LOGIN_ERROR')
        self.login_error.setLevel(logging.ERROR)
        err_handler = logging.FileHandler('C:/capstone/log_f/login.log')
        err_handler.setFormatter(act_formatter)
        self.login_error.addHandler(err_handler)
        self.login_error.propagate = False

        #Login Variables
        self.attempts = 0
        self.max_attempts = 3
        self.locked = False
        self.lock_time = 30
        self.end_time = 0 
        
        self.timer_label = tk.Label(self, text="", fg="red")
        self.timer_label.pack(pady=5)


        #Google API Variables


    def create_label_frame(self, parent, label_text, label_font, desc_text):
        CTkLabel(parent, text=label_text, font=label_font, bg_color='transparent').pack()
        CTkLabel(parent, text=desc_text, bg_color='transparent', wraplength=800).pack()

    def lp_nb_btn(self):
        def show_frame(frame):
            # Try to hide all frames, but ignore if they don't exist
            for frame_name in ['about_frame', 'contact_frame', 'team_frame']:
                if hasattr(self, frame_name):
                    getattr(self, frame_name).place_forget()
                    
            if frame:
                frame.place(y=100)
        def home_page():
            try:
                self.about_frame.place_forget(),
                self.contact_frame.place_forget(),
                self.team_frame.place_forget()
            except AttributeError:
                pass
            
        def about_page():
            # Create about frame if it doesn't exist
            if not hasattr(self, 'about_frame'):
                self.about_frame = CTkFrame(self, fg_color='white', height=600, width=1200)
                self.about_box = CTkLabel(self.about_frame, bg_color='transparent', text='MISSION', font=("Futura", 20, 'bold')).place(x=570)
                self.mission = CTkFrame(self.about_frame, fg_color='white', border_color='blue', corner_radius=10, border_width=3, height=180, width=800).place(x=210, y=30)
                self.mission_desc = CTkLabel(self.about_frame, text=
                        'TO MAKE OUR CUSTOMERS HAPPY AND SATISFIED WITH OUR SUPPLIES AND SERVICES THROUGH OUR NOVUS\n\
                        ECONOMICAL & WORLD CLASS (NEW) INDUSTRY SOLUTIONS.\n\
                    TO PHASE-IN STATE-OF-THE-ART EQUIPMENT AND TECHNOLOGIES TO MEET CUSTOMER NEEDS IN A TIMELY MANNER.\n\
                        TO CONTINUOUSLY DEVELOP THE ORGANIZATION’S ENGINEERING CAPABILITIES AND SKILLS THROUGH\n\
                        TRAINING AND SEMINARS THAT PROMOTE A HIGHER LEVEL OF EXCELLENCE.\n\
                    TO CREATE MORE JOBS FOR OTHER FILIPINO PEOPLE EMBRACING THE VISION MINDSET, AS GOD-FEARING\n\
                        INDIVIDUALS, AND HELP BUILD A BETTER COMMUNITY WITHIN OUR REACH.', bg_color='transparent', font=("Futura", 12, 'bold')).place(x=260, y=80)
                self.about_box1 = CTkLabel(self.about_frame, bg_color='transparent', text='VISION', font=("Futura", 20, 'bold')).place(x=575, y=240)
                self.vision = CTkFrame(self.about_frame, fg_color='white', border_color='blue', corner_radius=10, border_width=3, height=180, width=800).place(x=210, y=280)
                self.vision_desc = CTkLabel(self.about_frame, text=
                                    'TO BE THE CUSTOMER‘S PREFERRED OUTSOURCE AND SERVICE PROVIDER IN MIND',
                            bg_color='transparent', font=("Futura", 15, 'bold')).place(x=295, y=350)

            show_frame(self.about_frame)

        def contact_page():
            # Create contact frame if it doesn't exist
            if not hasattr(self, 'contact_frame'):
                self.contact_frame = CTkFrame(self, fg_color='white', height=600, width=1200)
                self.contact_label = CTkLabel(self.contact_frame, text='CONTACT', bg_color='transparent', font=("Futura", 20, 'bold')).place(x=550)
                self.contact_box = CTkFrame(self.contact_frame, fg_color='white', border_color='blue', corner_radius=10, border_width=3, height=350, width=800).place(x=210, y=30)
                self.contact_info = CTkLabel(self.contact_frame, text='                      For inquiries and system troubleshoot, please reach out to us through the following channels:\n\
                            Phone: +63 992 286 5855\n\
                            Email: mheng@novus-is.com\n\
                            Address: Novus Industry Solution, Sicily, Calamba, 4027 Laguna\n\
                            Developer Contact: vamorana@ccc.edu.ph & atnarvarte@ccc.edu.ph ',
      bg_color='transparent', font=("Futura", 15, 'bold')).place(x=215, y=150)

            show_frame(self.contact_frame)

        def team_page():
            if not hasattr(self, 'team_frame'):
                miss_universe = Image.open('C:/capstone/labels/jade.png')
                miss_universe = miss_universe.resize((120, 120))
                self.miss_universe_jj = CTkImage(miss_universe, size=((120, 120)))

                rhomar = Image.open('C:/capstone/labels/r.png')
                rhomar = rhomar.resize((120, 110))
                self.rhomar_pic = CTkImage(rhomar, size=((120, 110)))

                abnoy1 = Image.open('C:/capstone/labels/cd.png')
                abnoy1 = abnoy1.resize((120, 110))
                self.abnoy1_pic = CTkImage(abnoy1, size=((120, 120)))

                highlight = Image.open('C:/capstone/labels/hl.png')
                highlight = highlight.resize((120, 110))
                self.high_light = CTkImage(highlight, size=((120, 120)))

                self.team_frame = CTkFrame(self, fg_color='white', height=600, width=1200)
                self.team_frame.place(y=100)


                self.member1_box = CTkFrame(self.team_frame, fg_color='white', border_color='blue', corner_radius=10, border_width=3, height=220, width=530).grid(row=0, column=0, padx=35, pady=15, sticky='nsew')
                self.member2_box = CTkFrame(self.team_frame, fg_color='white', border_color='blue', corner_radius=10, border_width=3, height=220, width=530).grid(row=0, column=1, padx=35, pady=15, sticky='nsew')
                self.member3_box = CTkFrame(self.team_frame, fg_color='white', border_color='blue', corner_radius=10, border_width=3, height=220, width=530).grid(row=1, column=0, padx=35, pady=15, sticky='nsew')
                self.member4_box = CTkFrame(self.team_frame, fg_color='white', border_color='blue', corner_radius=10, border_width=3, height=220, width=530).grid(row=1, column=1, padx=35, pady=15, sticky='nsew')

                CTkLabel(self.team_frame, image=self.miss_universe_jj, text="").place(x=230, y=20)
                CTkLabel(self.team_frame, text=
                    '             JUSTINE  JADE  A.  ABRERA\n\
                jjabrera@ccc.edu.ph\n\
                DOCUMENTATION\n\
                Oversees project documentation.',justify="center",font=("Futura", 11, 'bold'), fg_color='transparent', bg_color='transparent').place(x=150, y=150)

                CTkLabel(self.team_frame, image=self.rhomar_pic, text="").place(x=850, y=20)
                CTkLabel(self.team_frame, text=
                    '                 RHOMAR  A.  LABANDILLO\n\
                ralabandilo@ccc.edu.ph\n\
                DOCUMENTATION\n\
                Responsible for Documentatio Quality',justify="center", font=("Futura", 11, 'bold'), fg_color='transparent', bg_color='transparent').place(x=750, y=150)

                CTkLabel(self.team_frame, image=self.abnoy1_pic, text="").place(x=230, y=270)
                CTkLabel(self.team_frame, text=
                '               ABCDY  ROMER  T.  NARVARTE\n\
                atnarvarte@ccc.edu.ph\n\
                DEVELOPER\n\
                Ensures product quality', font=("Futura", 11, 'bold'),justify="center", fg_color='transparent', bg_color='transparent').place(x=170, y=400)

                CTkLabel(self.team_frame, image=self.high_light, text="").place(x=840, y=270)
                CTkLabel(self.team_frame, text=
                    '              VICTOR  EMMANUEL  A.  MORANA\n\
                vamorana@ccc.edu.ph\n\
                MAIN DEVELOPER\n\
                Software development.', font=("Futura", 11, 'bold'),justify="center",fg_color='transparent', bg_color='transparent').place(x=760, y=400)

            show_frame(self.team_frame)

        CTkButton(self.option_menu, text='HOME', font=("Futura", 15, 'bold'), fg_color='#00117F', command=home_page).pack(side='left', padx=80, pady=30)
        CTkButton(self.option_menu, text='ABOUT', font=("Futura", 15, 'bold'), fg_color='#00117F', command=about_page).pack(side='left', padx=90, pady=30)
        CTkButton(self.option_menu, text='CONTACT', font=("Futura", 15, 'bold'), fg_color='#00117F', command=contact_page).pack(side='right', padx=90, pady=30)
        CTkButton(self.option_menu, text='TEAM', font=("Futura", 15, 'bold'), fg_color='#00117F', command=team_page).pack(side='right', padx=80, pady=30)
        # Load logos
        user_logo = Image.open('C:/capstone/labels/user_logo.png')
        user_logo = user_logo.resize((40,40))
        self.user_photo = CTkImage(user_logo, size = ((40,40)))

        pass_logo = Image.open('C:/capstone/labels/pass_logo.png')
        pass_logo = pass_logo.resize((40,40))
        self.pass_photo = CTkImage(pass_logo, size = ((40,40)))

        novus_logo = Image.open('C:/capstone/labels/novus_logo1.png')
        novus_logo = novus_logo.resize((200, 200))
        self.novus_photo = CTkImage(novus_logo, size=(200, 200))

        CTkLabel(self, image=self.novus_photo, text="").place(x=520, y=150)
        CTkLabel(self, text='NOVUS INDUSTRY SOLUTIONS', font=('Futura', 25, 'bold'), bg_color='white').place(x=440, y=390)

        CTkLabel(self, image=self.user_photo, text="").place(x=490, y=430)
        self.username_entry = CTkEntry(self, height=35, width=200, border_width=2, border_color='black')
        self.username_entry.place(x=535, y=430)

        CTkLabel(self, image=self.pass_photo, text="").place(x=490, y=470)
        self.password_entry = CTkEntry(self, height=35, width=200, show="*", border_width=2, border_color='black')
        self.password_entry.place(x=535, y=470)

        self.loginbutton = CTkButton(self, text='LOGIN', font=("futura", 12, 'bold'), width=120, height=30, bg_color='white',
                  fg_color='blue', corner_radius=10, border_width=2, border_color='black', command=self.login)
        self.loginbutton.place(x=495, y=510)

        self.bind("<Return>", lambda event: self.login())

        CTkButton(self, text='SIGN UP', font=("futura", 12, 'bold'), width=120, height=30, bg_color='white',
                  fg_color='blue', corner_radius=10, border_width=2, border_color='black', command=self.only_owner_sign).place(x=620, y=510)
        
        CTkButton(self, text='EMAIL LOGIN', font=("futura", 12, 'bold'), width=120, height=30, bg_color='white',
                  fg_color='blue', corner_radius=10, border_width=2, border_color='black', command=lambda: get_credentials(self.controller)).place(x=745, y=510)

        self.forgot_pass = CTkButton(self, text='FORGOT PASSWORD?', font=("futura", 12, 'bold'), width=220, height=30, bg_color='white',
                  fg_color='blue', corner_radius=10, border_width=2, border_color='black', command=self.forgot_pass)
        self.forgot_pass.place(x=495, y=545)
        
    def only_owner_sign(self, title="Owner Verification"):
        self.only_owner = tk.Toplevel(self)
        self.only_owner.title("Owner Sign Up")
        self.only_owner.geometry("400x300")
        self.only_owner.grab_set()

        CTkLabel(self.only_owner, text="Owner Verification", font=("Futura", 20, 'bold')).pack(pady=20)
        CTkLabel(self.only_owner, text="PASSCODE").pack(pady=10)
        passcode_entry = CTkEntry(self.only_owner, show="*", placeholder_text="Enter Passcode", width=200)
        passcode_entry.pack(pady=10)

        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            admin_pass = c.execute("SELECT * FROM users WHERE user_id = 'nickdiaz'").fetchone()

            if not admin_pass:
                messagebox.showerror("Error", "Owner passcode not found in the database.")
                self.only_owner.destroy()
                return

            # Unpack stored values
            _, _, _, _, _, _, _, password_hash, salt, _ = admin_pass[0:10]

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            self.only_owner.destroy()
            return
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            self.only_owner.destroy()
            return
        finally:
            conn.close()

        def verify_passcode():
            entered_password = passcode_entry.get()

            if password_hash.startswith('$2b$'): 
                if bcrypt.checkpw(entered_password.encode('utf-8'), password_hash.encode('utf-8')):
                    self.controller.show_frame(FrameNames.SIGNUP)
                    self.only_owner.destroy()
                else:
                    messagebox.showerror("Error", "Incorrect Passcode")
            else:  #
                computed_hash = hashlib.sha256((entered_password + salt).encode()).hexdigest()
                if computed_hash == password_hash:
                    self.controller.show_frame(FrameNames.SIGNUP)
                else:
                    messagebox.showerror("Error", "Incorrect Passcode")

        CTkButton(self.only_owner, text="Verify", command=verify_passcode).pack(pady=20)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if self.locked:
            messagebox.showwarning("Account Locked", "Please wait before trying again.")
            return

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            self.attempts += 1
            self.login_warning.warning(
                f"Empty fields for login attempt {self.attempts}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}"
            )
            self.check_attempts()
            return

        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()

            # Verify credentials - first try exact match on username
            user_search = '''SELECT * FROM users 
                            WHERE username = ? 
                            OR useremail = ?
                            ORDER BY user_id LIMIT 1'''
            login_user = c.execute(user_search, (username, username)).fetchone()

            if not login_user:
                self.attempts += 1
                self.check_attempts()
                messagebox.showerror("Error", "Invalid username or password")
                self.username_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)
                self.login_warning.warning(
                    f"Failed login attempt {self.attempts} for username: {username}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}"
                )
                return

            # Unpack user data
            user_id, f_name, m_name, l_name, e_mail, number, username_db, password_hash, salt, user_type = login_user[0:10]

            # Debug log the user data (excluding sensitive info)
            self.login_act.info(f"Attempting login for user: {user_id}, email: {e_mail}")

            # Password verification
            login_ok = False
            if password_hash and password_hash.startswith('$2b$'):
                # bcrypt
                try:
                    login_ok = bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
                    self.login_act.info(f"bcrypt verification result: {login_ok}")
                except Exception as e:
                    login_ok = False
                    self.login_error.error(f"bcrypt verification failed: {e}")
                    messagebox.showerror("Error", f"Password verification failed: {e}")
            else:
                # SHA256 + salt
                if salt is None:
                    salt = ""
                computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                login_ok = computed_hash == password_hash
                self.login_act.info(f"SHA256 verification result: {login_ok}")

            if not login_ok:
                self.attempts += 1
                self.check_attempts()
                messagebox.showerror("Error", "Invalid username or password")
                self.username_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)
                self.login_warning.warning(
                    f"Failed login attempt {self.attempts} for username: {username}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}"
                )
                return

            # Log successful login
            timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
            c.execute(
                "INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
                (user_id, 'Login', timestamp)
            )
            c.execute('UPDATE users SET last_login = ? WHERE user_id = ?', (timestamp, user_id))
            conn.commit()
            self.login_act.info(f"User  {user_id} logged in at {timestamp}")

            # Success
            self.controller.login(
                user_id, f_name, m_name, l_name, e_mail, number,
                username_db, password_hash, password_hash, user_type
            )

            # Send email notification for successful login
            from global_func import send_email_with_attachment, load_credentials_if_logged_in
            creds = load_credentials_if_logged_in()
            email_sent = False
            if creds:
                timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
                email_subject = "Login Notification"
                email_body = f"Hello {f_name} {l_name},\n\nYour account was successfully logged in at {timestamp}.\n\nIf this wasn't you, please contact the administrator immediately.\n\nRegards,\nNovus Industry Solutions"
                
                try:
                    # Make sure we're using the email address from the database for this user
                    # Use the email from the user who is logging in, not the credentials email
                    user_email = e_mail
                    # First try sending from the user's own email
                    email_sent = send_email_with_attachment(creds, user_email, email_subject, email_body, from_email=e_mail)
                    if email_sent:
                        self.login_act.info(f"Login notification email sent to {user_email} from {e_mail}")
                    else:
                        # If sending from user email fails, try with default sender
                        email_sent = send_email_with_attachment(creds, user_email, email_subject, email_body)
                        if email_sent:
                            self.login_act.info(f"Login notification email sent to {user_email} using default sender")
                        else:
                            self.login_warning.warning(f"Failed to send login notification email to {user_email}")
                except Exception as e:
                    self.login_error.error(f"Failed to send login notification email: {e}")
                    # Don't block login process if email fails

            self.attempts = 0
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)

            # Show main page or settings page as needed
            self.controller.show_frame("MainMRP")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            self.login_error.error(
                f"Database error during login attempt {self.attempts}: {e}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}"
            )
        finally:
            conn.close()

    def check_attempts(self):
        if self.attempts >= 3:  # Lock after 3 attempts
            self.lock_account()
            self.login_warning.warning(f"Account locked after {self.attempts} failed attempts, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")

    def lock_account(self):
        self.locked = True
        self.loginbutton.configure(state=tk.DISABLED)
        self.end_time = time.time() + self.lock_time
        self.update_timer()

    def update_timer(self):
        if not self.locked:
            return
        
        remaining = int(self.end_time - time.time())
        if remaining > 0:
            self.timer_label.config(text=f"Account locked. Try again in {remaining} seconds.")
            self.after(1000, self.update_timer)  # Update every second
        else:
            self.unlock_account()
            self.login_error.error(f"Account unlocked after {self.lock_time} seconds, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")

    def unlock_account(self):

        print("DEBUG: Unlocking account")
        self.locked = False
        self.attempts = 0
        self.loginbutton.configure(state=tk.NORMAL)
        self.timer_label.config(text="")
        messagebox.showinfo("Unlocked", "You may now attempt to login again.")
        self.login_act.info(f"Account unlocked, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")

    def forgot_pass(self, title="Forgot Password"):
        self.forgot_pass = tk.Toplevel(self)
        self.forgot_pass.title("Forgot Password")
        self.forgot_pass.geometry("400x500")
        self.forgot_pass.grab_set()

        CTkLabel(self.forgot_pass, text="Forgot Password", font=("Futura", 20, 'bold')).pack(pady=20)
        CTkLabel(self.forgot_pass, text="Enter your username: ").pack(pady=10)
        self.forgot_username_entry = CTkEntry(self.forgot_pass, placeholder_text="Username", width=200)
        self.forgot_username_entry.pack(pady=10)

        search_acc = CTkButton(self.forgot_pass, text="Reset Password", command=self.reset_password)
        search_acc.pack(pady=20)
        reset_pass = CTkButton(self.forgot_pass, text="Reset Password with Token", command=lambda: [self.show_reset_password_dialog(), self.forgot_pass.destroy()]
)
        reset_pass.pack(pady=10)

    def reset_password(self):
        forgot_username = self.forgot_username_entry.get().strip()
        if not forgot_username:
            messagebox.showwarning("Input Error", "Please enter a username.")
            return
        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            # Try to find user by username or email
            fetched_user = c.execute('SELECT user_id, f_name, l_name, useremail, reset_token, reset_token_expiry FROM users WHERE username = ? OR useremail = ?', 
                                    (forgot_username, forgot_username)).fetchone()
            if not fetched_user:
                messagebox.showerror("Error", "Username or email not found in the database.")
                return
            user_id, f_name, l_name, user_email, reset_token, reset_expiry = fetched_user
            
            # Check if user has an email address
            if not user_email:
                messagebox.showerror("Error", "No email address found for this user.")
                return
                
            # Generate a new reset token and expiry time
            new_reset_token = str(uuid.uuid4())
            expiry_time = datetime.now(pytz.timezone('Asia/Manila')) + timedelta(minutes=30)
            
            # Update the user record with the new reset token and expiry
            c.execute('UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE user_id = ?', (new_reset_token, expiry_time, user_id))
            conn.commit()
            
            # Send email with reset token
            from global_func import send_email_with_attachment, load_credentials_if_logged_in, get_credentials
            
            # Try to load existing credentials or get new ones
            creds = load_credentials_if_logged_in()
            email_sent = False
            
            if creds:
                email_subject = "Password Reset Token"
                email_body = f"Hello {f_name} {l_name},\n\nYou have requested to reset your password.\n\nYour reset token is: {new_reset_token}\n\nIt will expire at {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}\n\nIf you did not request this password reset, please contact the administrator immediately.\n\nRegards,\nNovus Industry Solutions"
                
                try:
                    # First try sending from the user's own email
                    email_sent = send_email_with_attachment(creds, user_email, email_subject, email_body, from_email=user_email)
                    if email_sent:
                        messagebox.showinfo("Success", f"A reset token has been sent to {user_email}. Please check your email.")
                        self.login_act.info(f"Password reset token sent to {user_email} for user {user_id}")
                    else:
                        # If sending from user email fails, try with default sender
                        email_sent = send_email_with_attachment(creds, user_email, email_subject, email_body)
                        if email_sent:
                            messagebox.showinfo("Success", f"A reset token has been sent to {user_email}. Please check your email.")
                            self.login_act.info(f"Password reset token sent to {user_email} for user {user_id} using default sender")
                        else:
                            raise Exception("Failed to send email with both user and default sender")
                except Exception as e:
                    # If email fails, try to refresh credentials and try again
                    self.login_warning.warning(f"First email attempt failed: {e}. Trying to refresh credentials...")
                    try:
                        # Try to get fresh credentials
                        if os.path.exists('json_f/token.json'):
                            os.remove('json_f/token.json')
                        # Ask user if they want to try logging in with Google again
                        if messagebox.askyesno("Email Authentication", "Email sending failed. Would you like to authenticate with Google to send the reset token?"): 
                            new_creds = get_credentials(self.controller)
                            if new_creds:
                                email_sent = send_email_with_attachment(new_creds, user_email, email_subject, email_body)
                                if email_sent:
                                    messagebox.showinfo("Success", f"A reset token has been sent to {user_email}. Please check your email.")
                                    self.login_act.info(f"Password reset token sent to {user_email} for user {user_id} after credential refresh")
                    except Exception as refresh_error:
                        self.login_error.error(f"Failed to refresh credentials and send email: {refresh_error}")
            
            # If email wasn't sent successfully, show the token in a messagebox as fallback
            if not email_sent:
                messagebox.showinfo("Reset Token", f"Your reset token is: {new_reset_token}\nIt will expire at {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}")
                self.login_warning.warning(f"Showing reset token in UI for user {user_id} as email sending failed")
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            self.login_error.error(f"Database error during password reset: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            self.login_error.error(f"Unexpected error during password reset: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if 'conn' in locals() and conn:
                conn.close()

    def show_reset_password_dialog(self):
        """Show dialog to reset password using token"""
        self.reset_dialog = tk.Toplevel(self)
        self.reset_dialog.title("Reset Password")
        self.reset_dialog.geometry("400x800")

        tk.Label(self.reset_dialog, text="Reset Password", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.reset_dialog, text="Username:").pack()
        self.reset_username_entry = CTkEntry(self.reset_dialog)
        self.reset_username_entry.pack(pady=5)

        tk.Label(self.reset_dialog, text="Reset Token:").pack()
        self.reset_token_entry = CTkEntry(self.reset_dialog)
        self.reset_token_entry.pack(pady=5)

        tk.Label(self.reset_dialog, text="New Password:").pack()
        self.new_password_entry = CTkEntry(self.reset_dialog, show="*")
        self.new_password_entry.pack(pady=5)

        tk.Button(self.reset_dialog, text="Submit", command=self.process_password_reset).pack(pady=10)

    def process_password_reset(self):
        """Verify token and update password"""
        username = self.reset_username_entry.get().strip()
        token = self.reset_token_entry.get().strip()
        new_password = self.new_password_entry.get().strip()

        if not all([username, token, new_password]):
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()

            # Verify the token is valid and not expired
            current_time = datetime.now(pytz.timezone('Asia/Manila'))
            c.execute("""
                SELECT reset_token_expiry FROM users
                WHERE username = ? AND reset_token = ? AND reset_token_expiry > ?
            """, (username, token, current_time))

            result = c.fetchone()
            if not result:
                messagebox.showerror("Error", "Invalid or expired token.")
                return

            # Generate new password hash
            salt = os.urandom(16).hex()
            hashed_pw = hashlib.sha256((new_password + salt).encode()).hexdigest()

            # Update password and clear reset token
            c.execute("""
                UPDATE users
                SET password_hash = ?, salt = ?, 
                    reset_token = NULL, reset_token_expiry = NULL
                WHERE username = ?
            """, (hashed_pw, salt, username))

            conn.commit()
            messagebox.showinfo("Success", "Password has been reset successfully!")
            self.reset_dialog.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            conn.close()