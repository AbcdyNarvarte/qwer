import tkinter as tk
from tkcalendar import Calendar
import time
from datetime import datetime
from tkcalendar import DateEntry
from tkinter import ttk
from tkinter import messagebox, filedialog
import customtkinter
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage, CTkToplevel
from PIL import Image
import sqlite3
import time
from datetime import datetime
import pytz
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
import sys
sys.path.append('C:/capstone')


from pages_handler import FrameNames
from global_func import on_show, handle_logout, get_credentials, user_logs_to_sheets, action_logs_to_sheets, settings_logs_to_sheets, product_logs_to_sheets
from product import ProductManagementSystem

class MainMRP(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg='white')
        
        # Main UI setup (your existing code)
        self.main = CTkFrame(self, fg_color="#6a9bc3", width=50, corner_radius=0)
        self.main.pack(side="left", fill="y")
        parent.pack_propagate(False)

        self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
        self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 5))  # Sticks to the top, fills X

        novus_logo = Image.open('C:/capstone/labels/novus_logo1.png')
        novus_logo = novus_logo.resize((50, 50))
        self.novus_photo = CTkImage(novus_logo, size=(50, 50))

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

        # --- REFRESH BUTTON ---
        self.refresh_btn = CTkButton(
            self.main_desc,
            text="⟳ Refresh System",
            fg_color="#2980b9",
            hover_color="#3498db",
            text_color="white",
            font=('Segoe UI', 12, 'bold'),
            command=self.refresh_system
        )
        self.refresh_btn.pack(side="right", padx=20, pady=10)

        # --- LOW COUNT NOTIFICATIONS BUTTON ---
        self.low_count_btn_frame = CTkFrame(self.main_desc, fg_color="#84a8db")
        self.low_count_btn_frame.pack(side="right", padx=10)
        self.low_count_btn = CTkButton(
            self.low_count_btn_frame,
            text="Low Count Notifications",
            fg_color="#e74c3c",
            hover_color="#c0392b",
            text_color="white",
            font=('Segoe UI', 12, 'bold'),
            command=self.show_low_count_window,
            width=180,
            height=36,
            corner_radius=8
        )
        self.low_count_btn.pack(side="left", padx=(0, 8), pady=8)
        # Red dot indicator (small and neat)
        self.red_dot = tk.Canvas(self.low_count_btn_frame, width=14, height=14, bg="#84a8db", highlightthickness=0)
        self.red_dot.pack(side="left", pady=8)
        self.update_low_count_dot()

        self.users_log_btn_frame = CTkFrame(self.main_desc, fg_color="#84a8db")
        self.users_log_btn_frame.pack(side="right", padx=10)
        self.users_log_btn = CTkButton(
            self.users_log_btn_frame,
            text="User Logs",
            fg_color="#27ae60",
            hover_color="#2ecc71",
            text_color="white",
            font=('Segoe UI', 12, 'bold'),
            command= user_logs_to_sheets,
            width=180,
            height=36,
            corner_radius=8
        )
        self.users_log_btn.pack(side="left", padx=(0, 8), pady=8)

        self.actions_log_btn_frame = CTkFrame(self.main_desc, fg_color="#84a8db")
        self.actions_log_btn_frame.pack(side="right", padx=10)
        self.actions_log_btn = CTkButton(
            self.actions_log_btn_frame,
            text="User Activity Logs",
            fg_color="#27ae60",
            hover_color="#2ecc71",
            text_color="white",
            font=('Segoe UI', 12, 'bold'),
            command= action_logs_to_sheets,
            width=100,
            height=36,
            corner_radius=8
        )
        self.actions_log_btn.pack(side="left", padx=(0, 8), pady=8)

        self.settings_log_btn_frame = CTkFrame(self.main_desc, fg_color="#84a8db")
        self.settings_log_btn_frame.pack(side="right", padx=10)
        self.settings_log_btn = CTkButton(
            self.settings_log_btn_frame,
            text="Settings Logs",
            fg_color="#27ae60",
            hover_color="#2ecc71",
            text_color="white",
            font=('Segoe UI', 12, 'bold'),
            command= settings_logs_to_sheets,
            width=100,
            height=36,
            corner_radius=8
        )
        self.settings_log_btn.pack(side="left", padx=(0, 8), pady=8)

        self.product_log_btn_frame = CTkFrame(self.main_desc, fg_color="#84a8db")
        self.product_log_btn_frame.pack(side="right", padx=10)
        self.product_log_btn = CTkButton(
            self.product_log_btn_frame,
            text="Product Logs",
            fg_color="#27ae60",
            hover_color="#2ecc71",
            text_color="white",
            font=('Segoe UI', 12, 'bold'),
            command=product_logs_to_sheets,
            width=100,
            height=36,
            corner_radius=8
        )
        self.product_log_btn.pack(side="left", padx=(0, 8), pady=8)        

        # --- DASHBOARD ROW (centered horizontally) ---
        self._dashboard_row()

        # --- DEADLINE DASHBOARD (below dashboard row) ---
        self._deadline_dashboard()

    def refresh_dashboard(self):
        """Refresh all dashboard cards and deadline dashboard with latest DB values."""
        # Destroy and recreate dashboard row
        if hasattr(self, 'dashboard_row_frame') and self.dashboard_row_frame.winfo_exists():
            self.dashboard_row_frame.destroy()
        self._dashboard_row()

        # Destroy and recreate deadline dashboard
        if hasattr(self, 'deadline_dashboard_frame') and self.deadline_dashboard_frame.winfo_exists():
            self.deadline_dashboard_frame.destroy()
        self._deadline_dashboard()

        # Update the low count notification dot
        self.update_low_count_dot()
        
    def refresh_system(self):
        """Refresh the entire system including all frames and database connections"""
        # First refresh the current dashboard
        self.refresh_dashboard()
        
        # Then call the controller's global refresh method to update all frames
        if hasattr(self, 'controller') and self.controller:
            self.controller.refresh_all_frames()
            
        # Show success message
        messagebox.showinfo("System Refreshed", "All system data has been refreshed successfully!")


    def refresh_low_items(self):
        # Create or focus the low inventory window
        if not hasattr(self, 'low_inv_window') or not self.low_inv_window.winfo_exists():
            self.low_inv_window = tk.Toplevel(self)  # Key fix: Use self as parent
            self.low_inv_window.title("Low Inventory Management")
            self.low_inv_window.geometry("650x450")
            
            # Configure window close behavior
            self.low_inv_window.protocol("WM_DELETE_WINDOW", self._close_low_inv_window)
            
            # Main container using pack
            self.low_inv_container = CTkFrame(self.low_inv_window)
            self.low_inv_container.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Header
            self.header_label = CTkLabel(self.low_inv_container, 
                                    text="Loading low inventory items...",
                                    font=('Arial', 14, 'bold'))
            self.header_label.pack(pady=(0, 10))
            
            # Create scrollable area
            self._setup_scrollable_area()
        else:
            self.low_inv_window.lift()  # Bring to front if already exists
        
        # Load and display data
        self._load_and_display_items()

    def _setup_scrollable_area(self):
        """Create the scrollable canvas area for items"""
        self.canvas_frame = tk.Frame(self.low_inv_container)
        self.canvas_frame.pack(fill='both', expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg='white', highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient='vertical', command=self.canvas.yview)
        self.items_frame = tk.Frame(self.canvas)
        
        self.items_frame.bind(
            '<Configure>',
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        )
        
        self.canvas.create_window((0, 0), window=self.items_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')

    def _load_and_display_items(self):
        """Load data from DB and display in the window"""
        try:
            # Clear previous items
            for widget in self.items_frame.winfo_children():
                widget.destroy()
            
            # Get data from database
            conn = sqlite3.connect('main.db')
            cursor = conn.cursor()
            cursor.execute('SELECT mat_id, mat_name, current_stock, supplier_id FROM raw_mats')
            low_items = [row for row in cursor.fetchall() if row[2] < 100]
            conn.close()
            
            # Update header
            self.header_label.configure(
                text=f"{len(low_items)} Low Volume Items (Volume < Unit of Measurement)",
                text_color='red' if low_items else 'green'
            )
            
            if low_items:
                # Create column headers
                headers = tk.Frame(self.items_frame)
                headers.pack(fill='x', pady=(0, 5))
                
                CTkLabel(headers, text="ID", width=10, font=('Arial', 12, 'bold')).pack(side='left', padx=5)
                CTkLabel(headers, text="Material Name", width=25, font=('Arial', 12, 'bold')).pack(side='left', padx=5)
                CTkLabel(headers, text="Supplier", width=20, font=('Arial', 12, 'bold')).pack(side='left', padx=5)
                CTkLabel(headers, text="Stock", width=15, font=('Arial', 12, 'bold')).pack(side='right', padx=5)
                
                # Add items
                for mat_id, name, vol, supplier in low_items:
                    item = tk.Frame(self.items_frame)
                    item.pack(fill='x', pady=2)
                    
                    CTkLabel(item, text=mat_id, width=10).pack(side='left', padx=5)
                    CTkLabel(item, text=name, width=25).pack(side='left', padx=5)
                    CTkLabel(item, text=supplier, width=20).pack(side='left', padx=5)
                    CTkLabel(item, text=f"{vol} units", text_color='red', width=15).pack(side='right', padx=5)
                    CTkButton(item, text="Edit", width=50,
                            command=lambda m=mat_id: self.open_edit_window(m)).pack(side='right', padx=5)
            else:
                CTkLabel(self.items_frame, 
                    text="All items are properly stocked (≥100 units)",
                    font=('Arial', 14),
                    text_color='green').pack(pady=20)
            
            # Schedule next refresh if window still exists
            if hasattr(self, 'low_inv_window') and self.low_inv_window.winfo_exists():
                self.low_inv_window.after(5000, self.refresh_low_items)
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load inventory: {str(e)}")

    def _close_low_inv_window(self):
        """Properly clean up the low inventory window"""
        if hasattr(self, 'low_inv_window') and self.low_inv_window.winfo_exists():
            # Cancel any pending refresh
            self.low_inv_window.after_cancel(self.refresh_low_items)
            self.low_inv_window.destroy()

    def open_edit_window(self, material_id):
        # Placeholder for your edit window function
        print(f"Editing material with ID: {material_id}")
        # Add your edit window implementation here

    def _calendar(self):
        calendar_frame = CTkFrame(self, fg_color='white',  border_color='black',  border_width=1, height=250, width=240)
        calendar_frame.pack(side='left', anchor='n', padx=5, pady=5)
        
        # Set Manila timezone
        self.manila_tz = pytz.timezone('Asia/Manila')
        
        # Time display
        self.time_label = CTkLabel(calendar_frame,text="",font=('Helvetica', 20),text_color='blue')
        self.time_label.pack(pady=(10, 0))
        
        # Date display
        self.date_label = CTkLabel(calendar_frame,text="",font=('Helvetica', 14),text_color='black')
        self.date_label.pack()
        
        # Calendar widget from tkcalendar
        self.calendar = Calendar(calendar_frame,selectmode='day', font=('Helvetica', 10), background='white', foreground='black',
            selectbackground='red', normalbackground='white', bordercolor='black', headersbackground='#f0f0f0' )
        self.calendar.pack(pady=10, padx=5, fill='both', expand=True)
        self._update_calendar_time()
        return calendar_frame

    def _update_calendar_time(self):
        # Get current Manila time
        now = datetime.now(self.manila_tz)
        
        # Update time display (e.g., "14:30:45")
        self.time_label.configure(text=now.strftime("%H:%M:%S"))
        
        # Update date display (e.g., "Monday, June 5, 2023")
        self.date_label.configure(text=now.strftime("%A, %B %d, %Y"))
        
        # Update calendar selection
        self.calendar.selection_set(now.date())
        
        # Schedule next update in 1 second
        self.after(1000, self._update_calendar_time)
        
    def _low_items(self):
        low_item_frame = CTkFrame(self, fg_color='white', border_color='black', border_width=1, height=270, width=600)
        low_item_frame.pack(side='left', anchor='n', padx=5, pady=5)

        # Create container for dynamic content
        self.content_container = tk.Frame(low_item_frame, bg='white')
        self.content_container.pack(fill='both', expand=True)

        # Initial load
        self._refresh_low_items()

    def _refresh_low_items(self):
        pass
            
    def _deadlines(self):
        dl_frame = CTkFrame(self, fg_color='white', border_color='black', border_width=1, height=270, width=600)
        dl_frame.place(relx = 0.27, rely = 0.54)

        # Create container for dynamic content
        self.dl_container = tk.Frame(dl_frame, bg='white')
        self.dl_container.pack(fill='both', expand=True)

        self._dl_report_refresh()

    def _dl_report_refresh(self):

        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()

            today = datetime.today().date()
            today_str = today.strftime("%Y-%m-%d")

            c.execute("SELECT order_id, order_name, order_dl FROM orders") 
            all_orders = c.fetchall()  

            dl_info = [(ord_id, ord_name, ord_dl) for ord_id, ord_name, ord_dl in all_orders if ord_dl == today_str]

            for widget in self.dl_container.winfo_children():
                widget.destroy()

            tk.Label(self.dl_container, 
            text=f"{len(dl_info)} Deadline(s) Today", 
            font=('Arial', 9), bg='white', fg='red').pack(anchor='n', pady=(0, 15))

            canvas = tk.Canvas(self.dl_container, bg='white', 
                            highlightthickness=0, height=180, width=450)
            scrollbar = tk.Scrollbar(self.dl_container, orient='vertical', command=canvas.yview, width=5, bg='#404040', troughcolor='#e0e0e0')
            scroll_frame = tk.Frame(canvas, bg='white')
            scroll_frame.bind('<Configure>', lambda e: canvas.configure(
                scrollregion=canvas.bbox('all')))
            canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')

            if dl_info:
                for ord_id, ord_name, ord_dl in dl_info:
                        item_frame = tk.Frame(scroll_frame, bg='white')
                        item_frame.pack(fill='x', pady=2)
                        
                        tk.Label(item_frame, text=ord_id, bg='white', anchor='w', width=15).pack(side='left')
                        tk.Label(item_frame, text=ord_name, bg='white', anchor='w', width=15).pack(side='left')
                        tk.Label(item_frame, text=ord_dl, bg='white', anchor='w').pack(side='right')
            else:
                tk.Label(self.dl_container, text="No Deadlines Today",font=('Arial', 12), bg='white', fg='green').pack(anchor='w',pady=20)
                        

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

        # Schedule next refresh (5000ms = 5 seconds)
        self.dl_container.after(5000, self._dl_report_refresh)

    def _to_excel(self):
        to_excel = CTkFrame(self, fg_color='white',  border_color='black',  border_width=1, height=270, width=240)
        to_excel.pack(side='left', padx=5)

    def excel_btn(self, parent, text):
        pass

    def _main_buttons(self, parent, image, text, command):
        button = CTkButton(parent, image=image, text=text, bg_color="#6a9bc3", fg_color="#6a9bc3", hover_color="white",
        width=100, border_color="white", corner_radius=10, border_width=2, command=command, anchor='center')
        button.pack(side="top", padx=5, pady=15)

    def _column_heads(self, columns, text):
        self.client_tree.heading(columns, text=text)
        self.client_tree.column(columns, width=100)

    def _images_buttons(self, image_path, size=(40, 40)):

        image = Image.open(image_path)
        size = size
        return CTkImage(image)
    
    def _dashboard_row(self):
        """Create a horizontal row for product, order, and raw materials dashboards, centered."""
        self.dashboard_row_frame = tk.Frame(self, bg='white')
        self.dashboard_row_frame.place(relx=0.5, rely=0.11, anchor='n')  # Centered horizontally, near top

        self._product_dashboard(parent=self.dashboard_row_frame)
        self._orders_dashboard(parent=self.dashboard_row_frame)
        self._rawmats_dashboard(parent=self.dashboard_row_frame)

    def _product_dashboard(self, parent):
        """Dashboard card for total products."""
        dashboard_frame = CTkFrame(
            parent,
            fg_color='white',
            border_color='#e0e0e0',
            border_width=2,
            height=150,
            width=280,
            corner_radius=16,
        )
        dashboard_frame.pack(side="left", padx=20, pady=10)

        title = CTkLabel(
            dashboard_frame,
            text="Total Products",
            font=('Segoe UI', 15, 'bold'),
            text_color='#2a4d69'
        )
        title.pack(pady=(18, 0))

        try:
            conn = sqlite3.connect('main.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            conn.close()
        except Exception:
            count = "?"

        value_label = CTkLabel(
            dashboard_frame,
            text=str(count),
            font=('Segoe UI', 34, 'bold'),
            text_color='#4b86b4'
        )
        value_label.pack(pady=(4, 10))

        def on_enter(e):
            dashboard_frame.configure(fg_color='#f5faff')
        def on_leave(e):
            dashboard_frame.configure(fg_color='white')
        dashboard_frame.bind("<Enter>", on_enter)
        dashboard_frame.bind("<Leave>", on_leave)
        title.bind("<Enter>", on_enter)
        title.bind("<Leave>", on_leave)
        value_label.bind("<Enter>", on_enter)
        value_label.bind("<Leave>", on_leave)

        def open_product_list(event=None):
            try:
                product_window = ProductManagementSystem(self, controller=None, show_only_list=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open Product List: {e}")

        dashboard_frame.bind("<Button-1>", open_product_list)
        title.bind("<Button-1>", open_product_list)
        value_label.bind("<Button-1>", open_product_list)

    def _orders_dashboard(self, parent):
        """Dashboard card for total orders, same size and style as product dashboard."""
        dashboard_frame = CTkFrame(
            parent,
            fg_color='white',
            border_color='#e0e0e0',
            border_width=2,
            height=150,
            width=280,
            corner_radius=16,
        )
        dashboard_frame.pack(side="left", padx=20, pady=10)

        title = CTkLabel(
            dashboard_frame,
            text="Total Orders",
            font=('Segoe UI', 15, 'bold'),
            text_color='#2a4d69'
        )
        title.pack(pady=(18, 0))

        try:
            conn = sqlite3.connect('main.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM orders")
            count = cursor.fetchone()[0]
            conn.close()
        except Exception:
            count = "?"

        value_label = CTkLabel(
            dashboard_frame,
            text=str(count),
            font=('Segoe UI', 34, 'bold'),
            text_color='#4b86b4'
        )
        value_label.pack(pady=(4, 10))

        def on_enter(e):
            dashboard_frame.configure(fg_color='#f5faff')
        def on_leave(e):
            dashboard_frame.configure(fg_color='white')
        dashboard_frame.bind("<Enter>", on_enter)
        dashboard_frame.bind("<Leave>", on_leave)
        title.bind("<Enter>", on_enter)
        title.bind("<Leave>", on_leave)
        value_label.bind("<Enter>", on_enter)
        value_label.bind("<Leave>", on_leave)

        def open_orders_page(event=None):
            if self.controller:
                self.controller.show_frame(FrameNames.ORDERS)

        dashboard_frame.bind("<Button-1>", open_orders_page)
        title.bind("<Button-1>", open_orders_page)
        value_label.bind("<Button-1>", open_orders_page)

    def _rawmats_dashboard(self, parent):
        """Dashboard card for total raw materials, same size and style as others."""
        dashboard_frame = CTkFrame(
            parent,
            fg_color='white',
            border_color='#e0e0e0',
            border_width=2,
            height=150,
            width=280,
            corner_radius=16,
        )
        dashboard_frame.pack(side="left", padx=20, pady=10)

        title = CTkLabel(
            dashboard_frame,
            text="Raw Materials",
            font=('Segoe UI', 15, 'bold'),
            text_color='#2a4d69'
        )
        title.pack(pady=(18, 0))

        try:
            conn = sqlite3.connect('main.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM raw_mats")
            count = cursor.fetchone()[0]
            conn.close()
        except Exception:
            count = "?"

        value_label = CTkLabel(
            dashboard_frame,
            text=str(count),
            font=('Segoe UI', 34, 'bold'),
            text_color='#4b86b4'
        )
        value_label.pack(pady=(4, 10))

        def on_enter(e):
            dashboard_frame.configure(fg_color='#f5faff')
        def on_leave(e):
            dashboard_frame.configure(fg_color='white')
        dashboard_frame.bind("<Enter>", on_enter)
        dashboard_frame.bind("<Leave>", on_leave)
        title.bind("<Enter>", on_enter)
        title.bind("<Leave>", on_leave)
        value_label.bind("<Enter>", on_enter)
        value_label.bind("<Leave>", on_leave)

        def open_rawmats_page(event=None):
            if self.controller:
                self.controller.show_frame(FrameNames.INVENTORY)

        dashboard_frame.bind("<Button-1>", open_rawmats_page)
        title.bind("<Button-1>", open_rawmats_page)
        value_label.bind("<Button-1>", open_rawmats_page)

    def _deadline_dashboard(self):
        """Dashboard card showing the first 3 upcoming order deadlines (with client name) below the dashboard row."""
        self.deadline_dashboard_frame = CTkFrame(
            self,
            fg_color='white',
            border_color='#e0e0e0',
            border_width=2,
            height=220,
            width=1100,
            corner_radius=16,
        )
        self.deadline_dashboard_frame.place(relx=0.5, rely=0.38, anchor='n')

        title = CTkLabel(
            self.deadline_dashboard_frame,
            text="Upcoming Order Deadlines",
            font=('Segoe UI', 15, 'bold'),
            text_color='#2a4d69'
        )
        title.pack(pady=(15, 5))

        # Table headers
        header_frame = tk.Frame(self.deadline_dashboard_frame, bg='white')
        header_frame.pack(fill='x', padx=20)
        tk.Label(header_frame, text="Order Name", font=('Segoe UI', 11, 'bold'), bg='white', fg='#34495e', width=20, anchor='w').pack(side='left')
        tk.Label(header_frame, text="Product", font=('Segoe UI', 11, 'bold'), bg='white', fg='#34495e', width=20, anchor='w').pack(side='left')
        tk.Label(header_frame, text="Client", font=('Segoe UI', 11, 'bold'), bg='white', fg='#34495e', width=20, anchor='w').pack(side='left')
        tk.Label(header_frame, text="Deadline", font=('Segoe UI', 11, 'bold'), bg='white', fg='#34495e', width=15, anchor='w').pack(side='left')

        # Data rows
        try:
            conn = sqlite3.connect('main.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.order_name, p.product_name, c.client_name, o.deadline
                FROM orders o
                JOIN products p ON o.product_id = p.product_id
                JOIN clients c ON o.client_id = c.client_id
                WHERE o.status_quo != 'Cancelled'
                ORDER BY date(o.deadline) ASC
                LIMIT 3
            """)
            deadlines = cursor.fetchall()
            conn.close()
        except Exception:
            deadlines = []

        for order_name, product_name, client_name, deadline in deadlines:
            row_frame = tk.Frame(self.deadline_dashboard_frame, bg='white')
            row_frame.pack(fill='x', padx=20, pady=2)
            tk.Label(row_frame, text=order_name, font=('Segoe UI', 10), bg='white', fg='#2a4d69', width=20, anchor='w').pack(side='left')
            tk.Label(row_frame, text=product_name, font=('Segoe UI', 10), bg='white', fg='#2a4d69', width=20, anchor='w').pack(side='left')
            tk.Label(row_frame, text=client_name, font=('Segoe UI', 10), bg='white', fg='#2a4d69', width=20, anchor='w').pack(side='left')
            tk.Label(row_frame, text=deadline, font=('Segoe UI', 10), bg='white', fg='#2a4d69', width=15, anchor='w').pack(side='left')

        if not deadlines:
            empty_frame = tk.Frame(self.deadline_dashboard_frame, bg='white')
            empty_frame.pack(fill='x', padx=20, pady=10)
            tk.Label(empty_frame, text="No upcoming deadlines.", font=('Segoe UI', 10, 'italic'), bg='white', fg='#b2bec3').pack(anchor='w')

#Global Functions

    def on_show(self):
        on_show(self)  # Calls the shared sidebar logic

    def handle_logout(self):
        handle_logout(self)

    def update_low_count_dot(self):
        """Show/hide red dot if there are low count materials."""
        try:
            conn = sqlite3.connect('main.db')
            cursor = conn.cursor()
            cursor.execute("SELECT current_stock, min_stock_level FROM raw_mats")
            low_items = [row for row in cursor.fetchall() if row[0] < row[1]]
            conn.close()
        except Exception:
            low_items = []

        self.red_dot.delete("all")
        if low_items:
            # Draw a small red dot in the center
            self.red_dot.create_oval(3, 3, 11, 11, fill="red", outline="")
        # else: no dot

    def show_low_count_window(self):
        """Show a neat window with info about low count materials, with both scrollbars."""
        win = tk.Toplevel(self)
        win.title("Low Count Materials")
        win.geometry("600x400")
        win.resizable(True, True)
        frame = CTkFrame(win, fg_color="white")
        frame.pack(fill="both", expand=True, padx=18, pady=18)

        header = CTkLabel(frame, text="Materials Below Low Count", font=('Segoe UI', 16, 'bold'), text_color='#e74c3c')
        header.pack(pady=(0, 12))

        # Scrollable area for table with both scrollbars
        table_canvas = tk.Canvas(frame, bg="white", highlightthickness=0)
        v_scrollbar = tk.Scrollbar(frame, orient="vertical", command=table_canvas.yview)
        h_scrollbar = tk.Scrollbar(frame, orient="horizontal", command=table_canvas.xview)
        table_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        table_canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")

        table_frame = tk.Frame(table_canvas, bg="white")
        table_canvas.create_window((0, 0), window=table_frame, anchor="nw")

        # Table headers
        headers = ["ID", "Material Name", "Volume", "Low Count", "Supplier"]
        for col, text in enumerate(headers):
            tk.Label(table_frame, text=text, font=('Segoe UI', 12, 'bold'), bg="white", fg="#2980b9", width=18, anchor="w").grid(row=0, column=col, padx=4, pady=4, sticky="w")

        # Fetch and display low count items
        try:
            conn = sqlite3.connect('main.db')
            cursor = conn.cursor()
            cursor.execute("SELECT mat_id, mat_name, current_stock, min_stock_level, supplier_id FROM raw_mats")
            rows = cursor.fetchall()
            low_items = [row for row in rows if int(row[2]) < int(row[3])]
            conn.close()
        except Exception as e:
            print("Error fetching low count items:", e)
            low_items = []

        if low_items:
            for r, (mat_id, name, vol, low, supplier) in enumerate(low_items, start=1):
                tk.Label(table_frame, text=mat_id, bg="white", font=('Segoe UI', 11), width=18, anchor="w").grid(row=r, column=0, padx=4, pady=2, sticky="w")
                tk.Label(table_frame, text=name, bg="white", font=('Segoe UI', 11), width=18, anchor="w").grid(row=r, column=1, padx=4, pady=2, sticky="w")
                tk.Label(table_frame, text=str(vol), bg="white", font=('Segoe UI', 11), fg="#e74c3c", width=18, anchor="w").grid(row=r, column=2, padx=4, pady=2, sticky="w")
                tk.Label(table_frame, text=str(low), bg="white", font=('Segoe UI', 11), fg="#e74c3c", width=18, anchor="w").grid(row=r, column=3, padx=4, pady=2, sticky="w")
                tk.Label(table_frame, text=supplier, bg="white", font=('Segoe UI', 11), width=18, anchor="w").grid(row=r, column=4, padx=4, pady=2, sticky="w")
        else:
            tk.Label(table_frame, text="No materials are below their low count.", font=('Segoe UI', 12), bg="white", fg="green").grid(row=1, column=0, columnspan=5, pady=18)

        # Make table scrollable in both directions
        def _on_frame_configure(event):
            table_canvas.configure(scrollregion=table_canvas.bbox("all"))
        table_frame.bind("<Configure>", _on_frame_configure)

        win.protocol("WM_DELETE_WINDOW", lambda: [win.destroy(), self.update_low_count_dot()])

    # Call update_low_count_dot after any inventory change
    def refresh_dashboard(self):
        """Refresh all dashboard cards and deadline dashboard with latest DB values."""
        # Destroy and recreate dashboard row
        if hasattr(self, 'dashboard_row_frame') and self.dashboard_row_frame.winfo_exists():
            self.dashboard_row_frame.destroy()
        self._dashboard_row()

        # Destroy and recreate deadline dashboard
        if hasattr(self, 'deadline_dashboard_frame') and self.deadline_dashboard_frame.winfo_exists():
            self.deadline_dashboard_frame.destroy()
        self._deadline_dashboard()

        # Update the low count notification dot
        self.update_low_count_dot()