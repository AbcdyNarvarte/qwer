import tkinter as tk
from tkcalendar import Calendar
from tkcalendar import DateEntry
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox, filedialog
import customtkinter
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage, CTkToplevel
from PIL import Image
import sqlite3
import time
import os
import hashlib
from datetime import datetime
import pytz
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
import re
from pages_handler import FrameNames
import logging
import sys
sys.path.append('C:/capstone')

from pages_handler import FrameNames
from global_func import on_show, handle_logout


class UserSet(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='white')

        self.main = CTkFrame(self, fg_color="#6a9bc3", width=50, corner_radius=0)
        self.main.pack(side="left", fill="y", pady=(0, 0)) 

        self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
        self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 10))  # Sticks to the top, fills X
        parent.pack_propagate(False)


        #Txt Logs For Info, Warning, Error
        logging.basicConfig(filename='C:/capstone/log_f/settings.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        self.sett_info = logging.getLogger('settings_info')
        self.sett_info.setLevel(logging.INFO)

        self.sett_warning = logging.getLogger('settings_warning')
        self.sett_warning.setLevel(logging.WARNING)

        self.sett_error = logging.getLogger('settings_error')
        self.sett_error.setLevel(logging.ERROR)

        self.logout_info = logging.getLogger('logout_info')
        self.logout_info.setLevel(logging.INFO)
        logout_handler = logging.FileHandler('C:/capstone/log_f/login.log')
        logout_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        logout_handler.setFormatter(logout_formatter)
        self.logout_info.addHandler(logout_handler)

        novus_logo = Image.open('C:/capstone/labels/novus_logo1.png')
        novus_logo = novus_logo.resize((50, 50))
        self.novus_photo = CTkImage(novus_logo, size=(50, 50))

        
        usertype = self.controller.session.get('usertype', '')
        print("DEBUG: usertype =", usertype)

        #Buttons Images
        self.clients_btn = self._images_buttons('C:/capstone/labels/client_btn.png', size=(100,100))
        self.inv_btn = self._images_buttons('C:/capstone/labels/inventory.png', size=(100,100))
        self.order_btn = self._images_buttons('C:/capstone/labels/order.png', size=(100,100))
        self.supply_btn = self._images_buttons('C:/capstone/labels/supply.png', size=(100,100))
        self.logout_btn = self._images_buttons('C:/capstone/labels/logout.png', size=(100,100))
        self.mrp_btn = self._images_buttons('C:/capstone/labels/mrp_btn.png', size=(100,100))
        self.settings_btn = self._images_buttons('C:/capstone/labels/settings.png', size=(100,100))
        self.user_logs_btn = self._images_buttons('C:/capstone/labels/action.png', size=(100,100))
        self.mails_btn = self._images_buttons('C:/capstone/labels/mail.png', size=(100,100))

        # --- Make the whole card scrollable ---
        scroll_frame = customtkinter.CTkScrollableFrame(self, fg_color="white")
        scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Main container for the profile card
        card = CTkFrame(scroll_frame, fg_color="#f5f6fa", corner_radius=20, border_color='#6a9bc3', border_width=2)
        card.pack(padx=40, pady=40, fill="both", expand=True)

        left_col = CTkFrame(card, fg_color="#e1e8ed", width=250, corner_radius=15)
        left_col.pack(side="left", fill="y", padx=(30, 15), pady=30)
        right_col = CTkFrame(card, fg_color="white", corner_radius=15)
        right_col.pack(side="left", fill="both", expand=True, padx=(15, 30), pady=30)

        self.profile_image_label = CTkLabel(left_col, text="No Image", width=120, height=120)
        self.profile_image_label.pack(pady=(20, 10))
        upload_btn = CTkButton(left_col, text="Upload Image", command=self.upload_image, width=120)
        upload_btn.pack(pady=(0, 20))

        # Display name and user type
        self.display_name = CTkLabel(left_col, text=self.controller.session.get('f_name', '') + " " + self.controller.session.get('l_name', ''),
                                    font=("Futura", 18, "bold"), fg_color="#e1e8ed")
        self.display_name.pack(pady=(10, 2))
        self.display_type = CTkLabel(left_col, text=self.controller.session.get('usertype', ''),
                                    font=("Futura", 14), fg_color="#e1e8ed")
        self.display_type.pack(pady=(0, 20))

        title = CTkLabel(right_col, text="User Details", font=("Futura", 22, "bold"), fg_color="white")
        title.pack(pady=(10, 20))

        form = CTkFrame(right_col, fg_color="white")
        form.pack(padx=30, pady=10, fill="x")

        # Helper for adding labeled entries in a grid
        def add_row(label, entry, row):
            CTkLabel(form, text=label, font=('Futura', 15, 'bold'), anchor="w", width=120).grid(row=row, column=0, sticky="w", pady=8, padx=(0, 10))
            entry.grid(row=row, column=1, sticky="ew", pady=8)
            form.grid_columnconfigure(1, weight=1)

        #change all entry fields to text disabled add readonly=True
        #Add a button to create a top level window to edit the user settings
        self.user_id_entry = CTkEntry(form, height=28, width=220, border_width=2, border_color='#6a9bc3')
        self.user_id_entry.insert(0, self.controller.session.get('user_id', ''))
        add_row("User ID:", self.user_id_entry, 0)

        self.f_name_entry = CTkEntry(form, height=28, width=220, border_width=2, border_color='#6a9bc3')
        self.f_name_entry.insert(0, self.controller.session.get('f_name', ''))
        add_row("First Name:", self.f_name_entry, 1)

        self.m_name_entry = CTkEntry(form, height=28, width=220, border_width=2, border_color='#6a9bc3')
        self.m_name_entry.insert(0, self.controller.session.get('m_name', ''))
        add_row("Middle Name:", self.m_name_entry, 2)

        self.l_name_entry = CTkEntry(form, height=28, width=220, border_width=2, border_color='#6a9bc3')
        self.l_name_entry.insert(0, self.controller.session.get('l_name', ''))
        add_row("Last Name:", self.l_name_entry, 3)

        self.email_entry = CTkEntry(form, height=28, width=220, border_width=2, border_color='#6a9bc3')
        self.email_entry.insert(0, self.controller.session.get('useremail', ''))
        add_row("Email:", self.email_entry, 4)

        self.phone_entry = CTkEntry(form, height=28, width=220, border_width=2, border_color='#6a9bc3')
        self.phone_entry.insert(0, self.controller.session.get('phonenum', ''))
        add_row("Phone Number:", self.phone_entry, 5)

        self.username_entry = CTkEntry(form, height=28, width=220, border_width=2, border_color='#6a9bc3')
        self.username_entry.insert(0, self.controller.session.get('username', ''))
        add_row("Username:", self.username_entry, 6)

        # Create a frame to hold password entry and reveal button
        password_frame = CTkFrame(form, fg_color="white")
        self.password_entry = CTkEntry(password_frame, height=28, width=190, border_width=2, border_color='#6a9bc3', show="*")
        self.password_entry.pack(side="left", fill="x", expand=True)
        
        # Add reveal button for password
        self.reveal_password_btn = CTkButton(password_frame, text="👁️", width=30, height=28, 
                                           command=lambda: self.toggle_password_visibility(self.password_entry, self.reveal_password_btn),
                                           fg_color="#6a9bc3", hover_color="#84a8db")
        self.reveal_password_btn.pack(side="right", padx=(5, 0))
        
        # Insert password value
        self.password_entry.insert(0, "")
        add_row("Password:", password_frame, 7)

        # Create a frame to hold confirm password entry and reveal button
        confirm_pass_frame = CTkFrame(form, fg_color="white")
        self.confirm_pass_entry = CTkEntry(confirm_pass_frame, height=28, width=190, border_width=2, border_color='#6a9bc3', show="*")
        self.confirm_pass_entry.pack(side="left", fill="x", expand=True)
        
        # Add reveal button for confirm password
        self.reveal_confirm_btn = CTkButton(confirm_pass_frame, text="👁️", width=30, height=28, 
                                          command=lambda: self.toggle_password_visibility(self.confirm_pass_entry, self.reveal_confirm_btn),
                                          fg_color="#6a9bc3", hover_color="#84a8db")
        self.reveal_confirm_btn.pack(side="right", padx=(5, 0))
        
        # Insert confirm password value
        self.confirm_pass_entry.insert(0, "")
        add_row("Confirm Password:", confirm_pass_frame, 8)

        # Replace the user_type_entry (around line 158) with a dropdown:
        self.user_type_options = ["admin", "owner", "staff", "supplier"]
        self.user_type_var = customtkinter.StringVar(value=self.controller.session.get('usertype', ''))
        self.user_type_dropdown = customtkinter.CTkOptionMenu(form, values=self.user_type_options, variable=self.user_type_var, height=28, width=220, dropdown_fg_color="white", dropdown_hover_color="#84a8db", button_color="#6a9bc3", button_hover_color="#84a8db")
        add_row("User Type:", self.user_type_dropdown, 9)

        # Save button at the bottom
        save_btn = CTkButton(right_col, text="Save Changes", command=self.save_user_settings, width=180, fg_color="#6a9bc3")
        save_btn.pack(pady=(30, 10))


    def generate_salt(self):
        return os.urandom(16).hex()

    def hash_password_with_salt(self, password, salt):
        return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        
    def toggle_password_visibility(self, entry_widget, button):
        """Toggle password visibility between shown and hidden"""
        if entry_widget.cget('show') == '*':
            entry_widget.configure(show='')
            button.configure(text='🔒')
        else:
            entry_widget.configure(show='*')
            button.configure(text='👁️')
    def save_user_settings(self):
        # Get values from entries
        user_id = self.user_id_entry.get()
        f_name = self.f_name_entry.get()
        m_name = self.m_name_entry.get()
        l_name = self.l_name_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_pass = self.confirm_pass_entry.get()
        user_type = self.user_type_var.get()

        # Regex validation
        if not re.fullmatch(r"[A-Za-z ]{2,}", f_name):
            messagebox.showerror("Input Error", "First name must contain only letters and spaces.")
            return
        if m_name and not re.fullmatch(r"[A-Za-z ]*", m_name):
            messagebox.showerror("Input Error", "Middle name must contain only letters and spaces.")
            return
        if not re.fullmatch(r"[A-Za-z ]{2,}", l_name):
            messagebox.showerror("Input Error", "Last name must contain only letters and spaces.")
            return
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Input Error", "Invalid email address.")
            return
        if not re.fullmatch(r"\+?\d{10,15}", phone):
            messagebox.showerror("Input Error", "Phone must be 10-15 digits (optionally starting with +).")
            return
        if not re.fullmatch(r"\w{4,20}", username):
            messagebox.showerror("Input Error", "Username must be 4-20 characters (letters, numbers, or _).")
            return
        if not re.fullmatch(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", password):
            messagebox.showerror("Input Error", "Password must be at least 8 characters, include a letter and a number.")
            return
        if password != confirm_pass:
            messagebox.showerror("Input Error", "Passwords do not match.")
            return
        if not re.fullmatch(r"[A-Za-z]{3,}", user_type):
            messagebox.showerror("Input Error", "User type must contain only letters.")
            return

        # Update session
        #User Profile Image
        self.profile_image_data = None
        self.profile_image_label = CTkLabel(self.main, text="No Image")
        self.profile_image_label.pack(side="left", padx=(0, 10))
        CTkButton(self.main, text="Upload Image", command=self.upload_image).pack(side="left", padx=(0, 10))

        #User Profile Information
        self.controller.session['user_id'] = user_id
        self.controller.session['f_name'] = f_name
        self.controller.session['m_name'] = m_name
        self.controller.session['l_name'] = l_name
        self.controller.session['useremail'] = email
        self.controller.session['phonenum'] = phone
        self.controller.session['username'] = username
        self.controller.session['password_hash'] = password
        self.controller.session['confirm_pass'] = confirm_pass
        self.controller.session['usertype'] = user_type

        # Update the database
        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            
            # Update basic user information
            c.execute("""
                UPDATE users SET f_name = ?, m_name = ?, l_name = ?, useremail = ?, phonenum = ?,
                    username = ?, usertype = ? WHERE user_id = ?
            """, (
                f_name, m_name, l_name, email, phone, username, user_type, user_id
            ))
            
            # Update password only if it's changed and matches confirmation
            if password and password == confirm_pass:
                salt = self.generate_salt()
                hashed_password = self.hash_password_with_salt(password, salt)
                c.execute("""
                    UPDATE users SET password_hash = ?, salt = ? WHERE user_id = ?
                """, (hashed_password, salt, user_id))
                
            conn.commit()
            messagebox.showinfo("Success", "User settings updated!")
            self.sett_info.info(f"User settings updated for user_id: {user_id}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            self.sett_error.error(f"Database error while updating user settings for user_id: {user_id}, Error: {e}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
        finally:
            if conn:
                conn.close()

    def on_show(self):
        for widget in self.main.winfo_children():
            widget.destroy()

        # Retrieve user type from session
        # Change line 67 from:
        user_type = self.controller.session.get('user_type', '')
        # To:
        usertype = self.controller.session.get('usertype', '')
        print("DEBUG: usertype =", usertype)
        
        # Create main buttons based on user type
        self.mrp_main = self._main_buttons(self.main, self.mrp_btn, 'MRP', command=lambda: self.controller.show_frame(FrameNames.MAIN_MRP))
        
        if usertype in ["admin", "owner"]:
            self.clients_main = self._main_buttons(self.main, self.clients_btn, 'Client', command=lambda: self.controller.show_frame(FrameNames.CLIENTS))
            self.orders_main = self._main_buttons(self.main, self.order_btn, 'Order', command=lambda: self.controller.show_frame(FrameNames.ORDERS))
            self.inventory_main = self._main_buttons(self.main, self.inv_btn, 'Storage', command=lambda: self.controller.show_frame(FrameNames.INVENTORY))
            self.supply_main = self._main_buttons(self.main, self.supply_btn, 'Supplier', command=lambda: self.controller.show_frame(FrameNames.SUPPLIERS))
            self.user_logs_main = self._main_buttons(self.main, self.user_logs_btn, 'User  Logs', command=lambda: self.controller.show_frame(FrameNames.LOGS))
            self.mails_main = self._main_buttons(self.main, self.mails_btn, 'Mails', command=lambda: self.controller.show_frame(FrameNames.MAILS))
        elif usertype in ["clerk", "manager"]:
            self.inventory_main = self._main_buttons(self.main, self.inv_btn, 'Storage', command=lambda: self.controller.show_frame(FrameNames.INVENTORY))
            self.supply_main = self._main_buttons(self.main, self.supply_btn, 'Supplier', command=lambda: self.controller.show_frame(FrameNames.SUPPLIERS))
        elif usertype == "employee":
            self.clients_main = self._main_buttons(self.main, self.clients_btn, 'Client', command=lambda: self.controller.show_frame(FrameNames.CLIENTS))
            self.orders_main = self._main_buttons(self.main, self.order_btn, 'Order', command=lambda: self.controller.show_frame(FrameNames.ORDERS))

        # Common buttons for all user types
        self.settings_main = self._main_buttons(self.main, self.settings_btn, 'Settings', command=lambda: self.controller.show_frame(FrameNames.SETTINGS))
        self.logout_main = self._main_buttons(self.main, self.logout_btn, 'Logout', command=self.handle_logout)

        # Update profile fields from session data
        self.update_profile_fields()

        # Load profile image from database
        self.load_profile_image()

    def update_profile_fields(self):
        """Update profile fields with session data."""
        
        fields = {
            'user_id': self.user_id_entry,
            'f_name': self.f_name_entry,
            'm_name': self.m_name_entry,
            'l_name': self.l_name_entry,
            'useremail': self.email_entry,
            'phonenum': self.phone_entry,
            'username': self.username_entry,
            'password_hash': self.password_entry,
            'confirm_pass': self.confirm_pass_entry,
            'usertype': self.user_type_dropdown
        }
        for key, entry in fields.items():
            value = self.controller.session.get(key, '')
            if key == 'usertype':
                entry.set(value)
            else:
                entry.delete(0, "end")
                entry.insert(0, value)

    def load_profile_image(self):
        """Load the user's profile image from the database."""
        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute("SELECT userimage FROM users WHERE user_id = ?", (self.controller.session.get('user_id'),))
            row = c.fetchone()
            if row and row[0]:
                from io import BytesIO
                img = Image.open(BytesIO(row[0]))
                img = img.resize((100, 100))
                self.profile_photo = CTkImage(img, size=(100, 100))
                self.profile_image_label.configure(image=self.profile_photo, text="")
            else:
                img = Image.open('C:/capstone/labels/user_logo.png')
                img = img.resize((100, 100))
                self.profile_photo = CTkImage(img, size=(100, 100))
                self.profile_image_label.configure(image=self.profile_photo, text="")
                if hasattr(self, "profile_image_data") and self.profile_image_label.winfo_exists():
                    self.profile_image_data.configure(image=self.profile_photo, text="")
        except Exception as e:
            if hasattr(self, "profile_image_label") and self.profile_image_label.winfo_exists():
                self.profile_image_label.configure(image=None, text="No Image")
                messagebox.showerror("Error", f"Failed to load profile image: {e}")
        finally:
            if conn:
                conn.close()


    def _main_buttons(self, parent, image, text, command):
        button = CTkButton(parent, image=image, text=text, bg_color="#6a9bc3", fg_color="#6a9bc3", hover_color="white",
        width=100, border_color="white", corner_radius=10, border_width=2, command=command)
        button.pack(side="top", padx=5, pady=15)
        
    def _images_buttons(self, image_path, size=(40, 40)):
        image = Image.open(image_path)
        size = size
        return CTkImage(image)

        
    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            try:
                image = Image.open(file_path)
                image = image.resize((100, 100))
                self.profile_photo = CTkImage(image, size=(100, 100))
                self.profile_image_label.configure(image=self.profile_photo, text="")
                # Optionally, store the image data for saving to DB
                with open(file_path, "rb") as f:
                    self.profile_image_data = f.read()

                # Save the image to the database
                conn = sqlite3.connect('main.db')
                c = conn.cursor()
                c.execute("UPDATE users SET userimage = ? WHERE user_id = ?"
                          , (self.profile_image_data, self.controller.session.get('user_id')))
                conn.commit()
                self.sett_info.info(f"Profile image updated for user_id: {self.controller.session.get('user_id')}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")
                conn.close()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open image: {e}")
                self.sett_error.error(f"Error uploading image: {e}, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")


    def handle_logout(self):
        handle_logout(self)