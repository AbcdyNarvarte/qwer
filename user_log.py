import tkinter as tk
import pytz
import datetime
import time
from datetime import datetime
from tkinter import ttk, messagebox
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage
from PIL import Image
import sqlite3
import logging
import traceback
import os
import sys
sys.path.append("C:/capstone")

from pages_handler import FrameNames
from global_func import on_show, handle_logout

class LogsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='white')

        self.main = CTkFrame(self, fg_color="#6a9bc3", width=50, corner_radius=0)
        self.main.pack(side="left", fill="y", pady=(0, 0))
        parent.pack_propagate(False)


        self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
        self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 10))

        novus_logo = Image.open('C:/capstone/labels/novus_logo1.png')
        novus_logo = novus_logo.resize((50, 50))
        self.novus_photo = CTkImage(novus_logo, size=(50, 50))

        # Buttons Images
        self.clients_btn = self._images_buttons('C:/capstone/labels/client_btn.png', size=(100,100))
        self.inv_btn = self._images_buttons('C:/capstone/labels/inventory.png', size=(100,100))
        self.order_btn = self._images_buttons('C:/capstone/labels/order.png', size=(100,100))
        self.supply_btn = self._images_buttons('C:/capstone/labels/supply.png', size=(100,100))
        self.logout_btn = self._images_buttons('C:/capstone/labels/logout.png', size=(100,100))
        self.mrp_btn = self._images_buttons('C:/capstone/labels/mrp_btn.png', size=(100,100))
        self.settings_btn = self._images_buttons('C:/capstone/labels/settings.png', size=(100,100))
        self.user_logs_btn = self._images_buttons('C:/capstone/labels/action.png', size=(100,100))
        self.mails_btn = self._images_buttons('C:/capstone/labels/mail.png', size=(100,100))
        

        # Search and CRUD buttons
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Search...")
        self.search_entry.pack(side="left", anchor="n", padx=(15, 20), ipadx=150)

        self.srch_btn = self.add_del_upd('SEARCH', command=lambda: [self.search_logs()])

        # Treeview style
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white", font=('Aial', 11), bordercolor="#cccccc", borderwidth=1)
        style.configure("Treeview.Heading", background="#007acc", foreground="white", font=('futura', 13, 'bold'))
        style.map("Treeview", background=[('selected', '#b5d9ff')])

        tree_frame = tk.Frame(self)
        tree_frame.place(x=120, y=105, width=1100, height=475)

        self.logs_tree = ttk.Treeview(        
            tree_frame,
            columns=('log_id', 'user_id', 'action', 'timestamp'),
            show='headings',
            style='Treeview'
        )
        self.logs_tree.bind("<Double-1>", self.show_info)
        self._column_heads('log_id', 'LOG ID')
        self._column_heads('user_id', 'USER ID')
        self._column_heads('action', 'ACTION')
        self._column_heads('timestamp', 'TIMESTAMP')


        for col in ('log_id', 'user_id', 'action', 'timestamp'):
            self.logs_tree.column(col, width=400, stretch=False)

        # Scrollbars
        self.scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.logs_tree.yview)
        self.h_scrollbar = tk.Scrollbar(tree_frame, orient="horizontal", command=self.logs_tree.xview)
        self.logs_tree.configure(yscrollcommand=self.scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Use grid for proper layout
        self.logs_tree.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="w")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Make the treeview expandable
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.load_user_logs()


    def load_user_logs(self):
        try:
            conn = sqlite3.connect("main.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_logs")
            rows = cursor.fetchall()

            # Enumerate loop for getting every single client in the DB & inseting data in each column represented
            for i in self.logs_tree.get_children():
                self.logs_tree.delete(i)

            for row in rows:
                self.logs_tree.insert("", "end", values=row)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            logging.error("Error loading user logs: %s", e, exc_info=True)
        finally:
            conn.close()


    def search_logs(self):
        searched = self.search_entry.get().strip()
        if not searched:
            messagebox.showwarning("Warning", "Please enter a search term.")
            return

        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            user_logs = c.execute("SELECT * FROM user_logs WHERE user_id = ?", (searched,)).fetchall()

            if not user_logs:
                messagebox.showinfo("No Results", "No logs found for the given search term.")
                return
            
            for i in self.logs_tree.get_children():
                self.logs_tree.delete(i)
            for log in user_logs:
                self.logs_tree.insert("", "end", values=log)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            logging.error("Error searching user logs: %s", e, exc_info=True)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            logging.error("Unexpected error during search: %s", e, exc_info=True)
        finally:
            if conn():
                conn.close



    def show_info(self, event):
        selected = self.logs_tree.focus()
        if not selected:
            return
        values = self.logs_tree.item(selected, 'values')
        user_id = values[1]


        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            user_actions = c.execute("SELECT * FROM user_logs WHERE user_id = ?", (user_id,)).fetchone()

            if user_actions:
                action_details = f"Log ID: {user_actions[0]}\nUser ID: {user_actions[1]}\nAction: {user_actions[2]}\nTimestamp: {user_actions[3]}"
                pop_up = tk.Toplevel(self)
                pop_up.title("User Logs")
                pop_up.geometry("800x600")

                frame = CTkFrame(pop_up)
                frame.pack(fill="both", expand=True, padx=20, pady=20)

                text = tk.Text(frame, wrap="word", state="normal", font=('Arial', 12))
                text.insert("1.0", action_details)
                text.configure(state="disabled")
                text.pack(expand=True, fill="both", padx=10, pady=10)

                btn = CTkButton(frame, text="Close", command=pop_up.destroy)
                btn.pack(side="bottom", pady=10)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            logging.error("Error fetching user log details: %s", e, exc_info=True)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            logging.error("Unexpected error: %s", e, exc_info=True)
        finally:
            conn.close()
            self.load_user_logs()


    def _images_buttons(self, image_path, size=(40, 40)):
        image = Image.open(image_path)
        image = image.resize(size)
        return CTkImage(image)
    
    def add_del_upd(self, text, command):
        button = ctk.CTkButton(self, text=text, width=73, command=command)
        button.pack(side="left", anchor="n", padx=4)

    def _column_heads(self, columns, text):
        self.logs_tree.heading(columns, text=text)
        self.logs_tree.column(columns, width=400, stretch=False)

    def _main_buttons(self, parent, image, text, command):
        button = ctk.CTkButton(parent, image=image, text=text, bg_color="#6a9bc3", fg_color="#6a9bc3", hover_color="white",
        width=100, border_color="white", corner_radius=10, border_width=2, command=command)
        button.pack(side="top", padx=5, pady=15)

    def on_show(self):
        on_show(self)  # Calls the shared sidebar logic

    def handle_logout(self):
        handle_logout(self) 