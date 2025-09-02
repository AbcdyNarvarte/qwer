from pages_handler import FrameNames
import sqlite3
import pytz
import re
from datetime import datetime
import logging
import os
import sys
import threading
from customtkinter import CTkImage, CTkButton, CTkFrame
from tkinter import messagebox, filedialog
from PIL import Image
import re
import traceback
import time
import hashlib
import tkinter as tk
import traceback
import jwt


#Data Imports
import json


#Google imports
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


#Email Imports
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


#Import Web Browser
import webbrowser


import base64
#Import Functions

def on_show(self):
    for widget in self.main.winfo_children():
        widget.destroy()

    usertype = self.controller.session.get('usertype', '')

    self.mrp_main = self._main_buttons(self.main, self.mrp_btn, 'MRP', command=lambda: self.controller.show_frame(FrameNames.MAIN_MRP))

    if usertype == "admin" or usertype == "owner":
        self.clients_main = self._main_buttons(self.main, self.clients_btn, 'Client', command=lambda: self.controller.show_frame(FrameNames.CLIENTS))
        self.orders_main = self._main_buttons(self.main, self.order_btn, 'Order', command=lambda: self.controller.show_frame(FrameNames.ORDERS))
        self.inventory_main = self._main_buttons(self.main, self.inv_btn, 'Storage', command=lambda: self.controller.show_frame(FrameNames.INVENTORY))
        self.supply_main = self._main_buttons(self.main, self.supply_btn, 'Supplier', command=lambda: self.controller.show_frame(FrameNames.SUPPLIERS))
        self.mails_main = self._main_buttons(self.main, self.mails_btn, 'Mails', command=lambda: self.controller.show_frame(FrameNames.MAILS))

    elif usertype == "supplier" or usertype == "manager":
        self.inventory_main = self._main_buttons(self.main, self.inv_btn, 'Storage', command=lambda: self.controller.show_frame(FrameNames.INVENTORY))
        self.supply_main = self._main_buttons(self.main, self.supply_btn, 'Supplier', command=lambda: self.controller.show_frame(FrameNames.SUPPLIERS))
        self.orders_main = self._main_buttons(self.main, self.order_btn, 'Order', command=lambda: self.controller.show_frame(FrameNames.ORDERS))
        self.mails_main = self._main_buttons(self.main, self.mails_btn, 'Mails', command=lambda: self.controller.show_frame(FrameNames.MAILS))

    elif usertype == "staff":
        self.clients_main = self._main_buttons(self.main, self.clients_btn, 'Client', command=lambda: self.controller.show_frame(FrameNames.CLIENTS))
        self.orders_main = self._main_buttons(self.main, self.order_btn, 'Order', command=lambda: self.controller.show_frame(FrameNames.ORDERS))
        self.mails_main = self._main_buttons(self.main, self.mails_btn, 'Mails', command=lambda: self.controller.show_frame(FrameNames.MAILS))


    self.settings_main = self._main_buttons(self.main, self.settings_btn, 'Settings', command=lambda: self.controller.show_frame(FrameNames.SETTINGS))
    self.logout_main = self._main_buttons(self.main, self.logout_btn,  'Logout', command=self.handle_logout)


def handle_logout(self):
    """Handle user logout and log the action."""
    # Get user information from session
    user_id = self.controller.session.get('user_id')
    username = self.controller.session.get('username')
    email = self.controller.session.get('useremail')
    
    # Set up logging
    self.logout_info = logging.getLogger('logout_info')
    self.logout_info.setLevel(logging.INFO)

    if not self.logout_info.handlers:
        logout_handler = logging.FileHandler('C:/capstone/log_f/login.log')
        logout_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        logout_handler.setFormatter(logout_formatter)
        self.logout_info.addHandler(logout_handler)

    # Log the logout with more detailed information for email-based logins
    if email and username:
        # For users who logged in with email
        self.logout_info.info(f"User {user_id} ({username}, {email}) logged out, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        # For regular users
        self.logout_info.info(f"User {user_id} logged out, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")

    # Log to DB
    if user_id:
        conn = sqlite3.connect('main.db')
        c = conn.cursor()
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        c.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)", (user_id, 'Logout', timestamp))
        conn.commit()
        conn.close()
        

    self.controller.show_frame(FrameNames.LOGIN)

def export_materials_to_json(db_path: str, output_file: str) -> None:
    """Exports product materials to JSON in a background thread."""

    def _export_thread():
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT product_id, product_name, materials FROM products")
                rows = cursor.fetchall()

            export_data = []

            for product_id, product_name, materials in rows:
                if materials:
                    try:
                        materials_dict = json.loads(materials)
                    except json.JSONDecodeError:
                        materials_dict = {}
                        for item in re.split(r'[;,]', materials):
                            parts = item.strip().split('-')
                            if len(parts) == 2:
                                name = parts[0].strip()
                                try:
                                    qty = int(parts[1].strip())
                                    materials_dict[name] = qty
                                except ValueError:
                                    continue
                        if not materials_dict:
                            materials_dict = {"raw": materials}
                else:
                    materials_dict = {}

                export_data.append({
                    "product_id": product_id,
                    "product_name": product_name,
                    "materials": materials_dict
                })

            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=4)

            logging.info(f"✅ Exported {len(export_data)} products to {output_file}")
        except Exception as e:
            logging.error(f"❌ Export failed: {e}")

    # Start the export in a background thread
    thread = threading.Thread(target=_export_thread)
    thread.start()

#Create a JSON Decoder for Total Materials Needed  = Finish the New SCHEMA first
def export_total_amount_mats(db_path: str, output_file: str) -> None:
    """Exports product materials to JSON in a background thread."""

    def export_thread():
        try:
            with sqlite3.connect(db_path) as conn:
                c = conn.cursor()
                c.execute("SELECT order_id, order_name, mats_need from orders")
                rows = c.fetchall()

            export_data = []

            for order_id, order_name, ttl_mats in rows:
                if ttl_mats:
                    try:
                        ttl_mats_dict = json.loads(ttl_mats)
                    except json.JSONDecodeError:
                        ttl_mats_dict = {}
                        for item in re.split(r'[;,]', ttl_mats):
                            parts = item.strip().split('-')
                            if len(parts) == 2:
                                name = parts[0].strip()
                                try:
                                    qty = int(parts[1].strip())
                                    ttl_mats_dict[name] = qty
                                except ValueError:
                                    continue
                        if not ttl_mats_dict:
                            ttl_mats_dict = {"raw": ttl_mats}
                else:
                    ttl_mats_dict = {}

                export_data.append({
                    'order_id': order_id,
                    'order_name': order_name,
                    'mats_need': ttl_mats_dict
                })

            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=4)
                        
            logging.info(f"✅ Exported {len(export_data)} products to {output_file}")
        except Exception as e:
            logging.error(f"❌ Export failed: {e}")

    # Start the export in a background thread
    thread = threading.Thread(target=export_thread, daemon=True)
    thread.start()


#Google API Variables
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/userinfo.email',   # 👈 needed
    'https://www.googleapis.com/auth/userinfo.profile', # 👈 optional but useful
    'openid'                     # 👈 optional but useful
]


credentials = "C:/capstone/json_f/cred_api.json"
login_token = "C:/capstone/json_f/token.json"


SHEETS = {

    "user_logs" : '1EeySwJry3Cdqu8Cxv0SjP58yC61EU7oolXcJUqPzzds',
    "action_logs" :'1dnewU7bfSb0YVbHuPgXtWtM7d89KgbLhezR8vxFISMg',
    "product_logs" : '1zY24U_A18zD5A60K3bCsypPVAkmbHUsgpBn7n5qjzIU',
    "settings_logs" : '19PpokaC8K8GwENb6PMttNz_yKrJ0yZcuZfRj1AcoNUc',

}

user_last_sync = "C:/capstone/sync_txt/user_sync.log"
action_last_sync = "C:/capstone/sync_txt/action_sync.log"
product_last_sync = "C:/capstone/sync_txt/product_sync.log"
settings_last_sync = "C:/capstone/sync_txt/settings_sync.log"

# ----------------- OAUTH LOGIN -----------------
def get_credentials(controller=None):
    """Google OAuth login and session setup."""
    creds = None
    
    # Always use the main app controller if not provided
    if not controller:
        controller = sys.modules['__main__'].app

    # Remove existing token to force new login every time
    if os.path.exists(login_token):
        try:
            os.remove(login_token)
        except Exception as e:
            print(f"Error removing token: {e}")
    
    # Always force new login flow
    try:
        # Configure the flow to handle unverified apps
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials, 
            SCOPES,
            # Add redirect_uri to ensure proper callback handling
            redirect_uri='http://localhost:0'
        )
        
        # Set up authorization parameters to handle unverified apps
        auth_url, _ = flow.authorization_url(
            # Enable offline access so that you can refresh an access token without
            # re-prompting the user for permission
            access_type='offline',
            # Enable incremental authorization
            include_granted_scopes='true',
            # Force to display the consent prompt
            prompt='consent',
        )   
        
        # Run the local server to handle the redirect
        # This will automatically open the browser with the auth URL
        creds = flow.run_local_server(port=0)
        
        # Save new token
        with open(login_token, "w") as token:
            token.write(creds.to_json())
    except Exception as e:
        print(f"Error during authentication flow: {e}")
        messagebox.showerror("Login Error", f"Error during Google authentication: {e}")
        return None

    # ---- Fetch user info ----
    try:
        oauth2_service = build("oauth2", "v2", credentials=creds)
        user_info = oauth2_service.userinfo().get().execute()
        email = user_info.get("email")
        name = user_info.get("name", "Google User")
        
        # Create or update user in database
        create_or_update_google_user(email, name, controller)
        
        messagebox.showinfo("Login Success", f"Welcome {email}")
        return creds
    except Exception as e:
        messagebox.showerror("Login Error", f"Error during authentication: {e}")
        # Delete token file to force new login next time
        if os.path.exists(login_token):
            os.remove(login_token)
        return None

def load_credentials_if_logged_in():
    """
    Load saved credentials if user is already logged in.
    Returns:
        creds (Credentials) if valid credentials exist,
        None otherwise.
    """
    creds = None
    if os.path.exists(login_token):
        creds = Credentials.from_authorized_user_file(login_token, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save refreshed token
                with open(login_token, "w") as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Failed to refresh token: {e}")
                return None
        if not creds.valid:
            return None
        return creds
    else:
        return None

creds = load_credentials_if_logged_in()

def create_or_update_google_user(email, name, controller):
    """
    Creates a new user or updates an existing one based on Google account information.
    This function allows any Gmail account to be used without pre-registration.
    """
    try:
        # Log the login action
        login_info = logging.getLogger('login_info')
        login_info.setLevel(logging.INFO)
        
        if not login_info.handlers:
            login_handler = logging.FileHandler('C:/capstone/log_f/login.log')
            login_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            login_handler.setFormatter(login_formatter)
            login_info.addHandler(login_handler)
        
        # Log the login with email information
        login_info.info(f"User with email {email} logged in via Google OAuth, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
        
        conn = sqlite3.connect('main.db')
        c = conn.cursor()

        # First try to find user by email
        user_data = c.execute('SELECT * FROM users WHERE useremail = ?', (email,)).fetchone()
        
        # If user doesn't exist, create a new one
        if not user_data:
            # Generate a unique user ID based on email
            user_id = f"google_{email.split('@')[0]}_{int(time.time())}"
            
            # Split name into first and last name if possible
            name_parts = name.split(' ', 1)
            f_name = name_parts[0]
            l_name = name_parts[1] if len(name_parts) > 1 else ""
            
            # Generate a random password hash and salt for the account
            salt = os.urandom(16).hex()
            password_hash = hashlib.sha256(("google_auth" + salt).encode()).hexdigest()
            
            # Set default values for new Google users
            m_name = ""
            number = ""
            username = email  # Use email as username
            user_type = "employee"  # Default user type
            
            # Insert new user into database
            c.execute('''
                INSERT INTO users 
                (user_id, f_name, m_name, l_name, useremail, phonenum, username, password_hash, salt, usertype) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, f_name, m_name, l_name, email, number, username, password_hash, salt, user_type))
            conn.commit()
            
            # Fetch the newly created user
            user_data = c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
            messagebox.showinfo("New Account", f"Created new account for {email}")
        
        # Process user data
        user_id, f_name, m_name, l_name, e_mail, number, username_db, password_hash, salt, user_type = user_data[0:10]
        
        # Update session with user data
        controller.session['user_id'] = user_id
        controller.session['f_name'] = f_name
        controller.session['m_name'] = m_name
        controller.session['l_name'] = l_name
        controller.session['useremail'] = email  # Use the email from Google
        controller.session['phonenum'] = number
        controller.session['username'] = username_db
        controller.session['password_hash'] = password_hash
        controller.session['salt'] = salt
        controller.session['usertype'] = user_type

        controller.show_frame("MainMRP")
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during user creation/update: {e}")
        traceback.print_exc()
        return False

# Keep the original function for backward compatibility
def validate_user_email(email, controller):
    """
    Legacy function maintained for backward compatibility.
    Now just calls create_or_update_google_user.
    """
    return create_or_update_google_user(email, email.split('@')[0], controller)

def send_email_with_attachment(creds, to, subject, body, attachments=[], from_email=None):
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Get the sender's email if not provided
        if not from_email:
            try:
                # Get user info from credentials
                oauth2_service = build("oauth2", "v2", credentials=creds)
                user_info = oauth2_service.userinfo().get().execute()
                from_email = user_info.get("email")
                if not from_email:
                    if hasattr(creds, 'token_response') and 'id_token' in creds.token_response:
                        id_info = jwt.decode(creds.token_response['id_token'], options={"verify_signature": False})
                        from_email = id_info.get('email')
            except Exception as oauth_error:
                print(f"Error getting user email from OAuth: {oauth_error}")
                # Use a default sender if we can't get the user's email
                from_email = "noreply@novusindustry.com"
            
        # Create a multipart message
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = from_email
        message['subject'] = subject

        # Add body
        message.attach(MIMEText(body, "plain"))

        # Add attachments
        for filepath in attachments:
            try:
                filename = os.path.basename(filepath)
                with open(filepath, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={filename}",
                )
                message.attach(part)
            except Exception as attach_error:
                print(f"Error attaching file {filepath}: {attach_error}")

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Add retry logic for sending email
        max_retries = 3
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                send_result = service.users().messages().send(
                    userId="me",
                    body={"raw": raw_message}
                ).execute()
                print("Email sent successfully. Message ID:", send_result['id'])
                return True
            except Exception as send_error:
                retry_count += 1
                last_error = send_error
                print(f"Attempt {retry_count} failed: {send_error}")
                if retry_count < max_retries:
                    time.sleep(2)  # Wait before retrying
        
        # If we get here, all retries failed
        print(f"Failed to send email after {max_retries} attempts. Last error: {last_error}")
        return False
    except Exception as e:
        print("Error in send_email_with_attachment:", e)
        traceback.print_exc()
        return False
    
def create_email(controller=None):

    attachments = []

    mail_wdw = tk.Toplevel()
    mail_wdw.title("Compose Email")
    mail_wdw.geometry("600x600")
    mail_wdw.resizable(False, False)
    mail_wdw.grab_set()

    # Get the current user's email if available
    user_email = None
    if controller and hasattr(controller, 'session'):
        user_email = controller.session.get('useremail')

    # Email fields
    email_frame = tk.LabelFrame(mail_wdw, text="Email Sender with Attachments", padx=10, pady=10)
    email_frame.pack(padx=10, pady=10, fill="both", expand=True)

    # Show sender email if available
    if user_email:
        tk.Label(email_frame, text=f"From: {user_email}").pack(pady=5)

    tk.Label(email_frame, text="To:").pack(pady=5)
    to_entry = tk.Entry(email_frame, width=50)
    to_entry.pack(pady=5)

    tk.Label(email_frame, text="Subject:").pack(pady=5)
    subject_entry = tk.Entry(email_frame, width=50)
    subject_entry.pack(pady=5)

    tk.Label(email_frame, text="Body:").pack(pady=5)
    body_textbox = tk.Text(email_frame, height=10, width=50)
    body_textbox.pack(pady=5)

    attach_label = tk.Label(email_frame, text="No attachments selected", fg="gray")
    attach_label.pack(pady=5)

    #Multiple Attachments
    def add_attachment():
        filepaths = filedialog.askopenfilenames(title="Select Attachment(s)")
        if filepaths:
            attachments.extend(filepaths)
            attach_label.config(
                text="\n".join(os.path.basename(f) for f in attachments)
            )

    attach_button = tk.Button(email_frame, text="Add Attachment(s)", command=add_attachment)
    attach_button.pack(pady=5)

    #Connects to API through the creds variable and sends email function
    def on_send_button_click():
        to = to_entry.get()
        subject = subject_entry.get()
        body = body_textbox.get("1.0", "end-1c")

        if send_email_with_attachment(creds, to, subject, body, attachments, from_email=user_email):
            messagebox.showinfo("Success", "Email sent!")
        else:
            messagebox.showerror("Error", "Failed to send email.")

    send_button = tk.Button(email_frame, text="Send Email", command=on_send_button_click)
    send_button.pack(pady=10)

def see_mails(creds):
    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])

        mail_wdw = tk.Toplevel()
        mail_wdw.title("Inbox")
        mail_wdw.geometry("600x400")
        mail_wdw.resizable(False, False)
        mail_wdw.grab_set()

        listbox = tk.Listbox(mail_wdw, width=80, height=20)
        listbox.pack(pady=10)

        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            snippet = msg_data.get('snippet', '')
            listbox.insert(tk.END, snippet)

    except HttpError as error:
        print(f'An error occurred: {error}')
        messagebox.showerror("Error", f"Failed to fetch emails: {error}")


def to_gmail_web():
    try:
        creds = load_credentials_if_logged_in()
        if not creds:
            messagebox.showerror("Error", "You must be logged in to access Gmail.")
            return
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(login_token, "w") as token:
                token.write(creds.to_json())
        webbrowser.open("https://mail.google.com/mail/u/0/#inbox")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to refresh credentials: {e}")
        return



def read_logs(log_file):
    """Reads a log file and extracts [timestamp, level, message] for Sheets."""
    rows = []
    log_pattern = re.compile(r"^([\d\-]+\s[\d:,]+)\s-\s(\w+)\s-\s(.+)$")

    with open(log_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            match = log_pattern.match(line)
            if match:
                ts, level, message = match.groups()
                rows.append([ts, level, message])

    return rows


def sync_logs_to_sheets(last_sync_file, log_file, sheet_id):

    """Append new log entries to Google Sheets."""
    controller = sys.modules['__main__'].app

    creds = load_credentials_if_logged_in()

    usertype = controller.session.get('usertype', '')
    if usertype not in ['admin', 'owner']:
        messagebox.showinfo("Permission Denied", "You do not have permission to sync logs.")
        return

    if not creds:
        messagebox.showinfo(text="Please login with Google first")
        return
    sheets_service = build("sheets", "v4", credentials=creds)

    try:
        with open(last_sync_file, "r") as f:
            last_ts = f.read().strip()
    except FileNotFoundError:
        last_ts = None

    rows = read_logs(log_file)

    if last_ts:
        rows = [r for r in rows if r[0] > last_ts]

    if not rows:
        messagebox.showinfo("No new logs to upload")
        webbrowser.open(f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
        return

    try:
        sheets_service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="Sheet1!A:C",
            valueInputOption="RAW",
            body={"values": rows}
        ).execute()

        with open(last_sync_file, "w") as f:
            f.write(rows[-1][0])

        messagebox.showinfo(f"✅ Synced {len(rows)} logs to Sheets")
        webbrowser.open(f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit")

    except HttpError as e:
        messagebox.showinfo(text=f"❌ Sheets sync failed: {e}")


def user_logs_to_sheets():
    sync_logs_to_sheets(user_last_sync, 'C:/capstone/log_f/login.log', SHEETS['user_logs'])

def action_logs_to_sheets():
    sync_logs_to_sheets(action_last_sync, 'C:/capstone/log_f/action.log', SHEETS['action_logs'])

def product_logs_to_sheets():
    sync_logs_to_sheets(product_last_sync, 'C:/capstone/log_f/product.log', SHEETS['product_logs'])

def settings_logs_to_sheets():
    sync_logs_to_sheets(settings_last_sync, 'C:/capstone/log_f/settings.log', SHEETS['settings_logs'])