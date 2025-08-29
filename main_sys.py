import tkinter as tk
from tkinter import messagebox
import customtkinter
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage, CTkToplevel
from PIL import Image
import threading
import os
import logging
import sqlite3
import pytz
from datetime import datetime
import sys
from pages_handler import FrameNames
from database import DatabaseManager




class NovusApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.session = {}
        self.db_manager = DatabaseManager(session=self.session)
        self._setup_ui()
        self._initialize_frames()
        self.protocol("WM_DELETE_WINDOW", self._on_app_close)

    def login(self, user_id, f_name, m_name, l_name, e_mail, number, username, password, confirm_pass, user_type):
        """Store user session data"""
        self.session['user_id'] = user_id
        self.session['f_name'] = f_name
        self.session['m_name'] = m_name
        self.session['l_name'] = l_name
        self.session['useremail'] = e_mail  # Changed from 'e_mail' to 'useremail'
        self.session['phonenum'] = number  # Changed from 'number' to 'phonenum'
        self.session['username'] = username
        self.session['password_hash'] = password  # Changed from 'password' to 'password_hash'
        self.session['confirm_pass'] = confirm_pass
        self.session['usertype'] = user_type
        messagebox.showinfo("Login Successful", f"User {username} logged in as {user_type}")

    def _setup_ui(self):
        self.title("NOVUS INDUSTRY SOLUTIONS INVENTORY")
        self.geometry("1200x600")
        self.iconbitmap('C:/capstone/labels/novus_logo1.png')
        self.config(bg='white')
        self.resizable(False, False)
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.frames = {}

    def _initialize_frames(self):
        """Lazy import frames to prevent circular imports"""
        from clients_crud import ClientsPage
        from prod_crud import ProductPage
        from order_crud import OrdersPage
        from inventory_crud import InventoryPage
        from supplier_crud import SuppliersPage
        from user_sets import UserSet
        from mails import MessagesPage
        from login_page import LoginPage
        from user_log import LogsPage
        from home_mrp import MainMRP
        from signup_page import SignupPage

        frame_classes = {
            FrameNames.CLIENTS: ClientsPage,
            FrameNames.LOGS: LogsPage,
            FrameNames.PRODUCTS: ProductPage,
            FrameNames.ORDERS: OrdersPage,
            FrameNames.INVENTORY: InventoryPage,
            FrameNames.SUPPLIERS: SuppliersPage,
            FrameNames.SETTINGS: UserSet,
            FrameNames.MAILS: MessagesPage,
            FrameNames.MAIN_MRP: MainMRP,
            FrameNames.SIGNUP: SignupPage,
            FrameNames.LOGIN: LoginPage
        }

        login_frame = LoginPage(parent=self.container, controller=self)
        self.frames[FrameNames.LOGIN] = login_frame
        login_frame.grid(row=0, column=0, sticky="nsew")
        threading.Thread(target=self._load_other_frames, args=(frame_classes,), daemon=True).start()
        self.show_frame(FrameNames.LOGIN)

    def _load_other_frames(self, frame_classes):
        """Load other frames in the background"""
        for frame_name, frame_class in frame_classes.items():
            if frame_name != FrameNames.LOGIN:
                frame = frame_class(parent=self.container, controller=self)
                self.frames[frame_name] = frame
                frame.grid(row=0, column=0, sticky="nsew")

        # Show the login frame first
        self.show_frame(FrameNames.LOGIN)


    def show_frame(self, page_name):
        if page_name in self.frames:
            frame = self.frames[page_name]
            frame.tkraise()
            if hasattr(frame, 'on_show'):
                frame.on_show()
        else:
            available = "\n".join(self.frames.keys())
            messagebox.showerror("Navigation Error", f"Frame '{page_name}' not found.\n\nAvailable frames:\n{available}")


    def _on_app_close(self):
        confirm =  messagebox.askokcancel("Quit", "Do you want to quit?")
        conn = None
        
        if confirm:
            try:
                """Handle user logout and log the action."""
                self.logout_info = logging.getLogger('logout_info')
                self.logout_info.setLevel(logging.INFO)

                if not self.logout_info.handlers:
                    logout_handler = logging.FileHandler('C:/capstone/log_f/login.log')
                    logout_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                    logout_handler.setFormatter(logout_formatter)
                    self.logout_info.addHandler(logout_handler)

                # Log the logout
                self.logout_info.info(f"User {self.session.get('user_id', None)} logged out, Time: {datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')}")

                # Log to DB
                user_id = self.session.get('user_id')
                if user_id:
                    conn = sqlite3.connect('main.db')
                    c = conn.cursor()
                    timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
                    c.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)", (user_id, 'Logout', timestamp))
                    print('DEBUG: User logged out:', user_id, timestamp)
                    conn.commit()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during logout: {e}")
            finally:
                if conn:
                    conn.close()
                self.destroy()
        else:
            return


if __name__ == "__main__":
    print("Working")
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")
    app = NovusApp()
    app.mainloop()
