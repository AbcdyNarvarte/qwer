import tkinter as tk
from tkcalendar import Calendar
from tkcalendar import DateEntry
from tkinter import ttk
from tkinter import messagebox, filedialog
import customtkinter
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage, CTkToplevel, CTkComboBox, CTkOptionMenu
from PIL import Image
import sqlite3
import time
from datetime import datetime
import pytz
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import uuid
import bcrypt
import pandas as pd
import os

#Imported Files
from pages_handler import FrameNames

from global_func import on_show, handle_logout

class InventoryPage(tk.Frame):
    def __init__(self, parent, controller):
            super().__init__(parent)
            self.controller = controller
            self.config(bg='white')

            self.main = CTkFrame(self, fg_color="#6a9bc3", width=50, corner_radius=0)
            self.main.pack(side="left", fill="y", pady=(0, 0))

            self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
            self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 10))
            parent.pack_propagate(False)


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
      
            #User Type
            user_type = self.controller.session.get('usertype')


            # Crud Buttons
            self.search_entry = ctk.CTkEntry(self, placeholder_text="Search...")
            self.search_entry.pack(side="left", anchor="n", padx=(15, 20), ipadx=60)

            vol_stat_search = CTkFrame(self, fg_color='white')
            vol_stat_search.pack(side="left", anchor="n", padx=(15, 15), pady=(5, 0), fill='x')

            CTkLabel(vol_stat_search,
                    text="STATUS:",
                    font=('Futura', 15, 'bold'),
                    width=100,
                    anchor="w").pack(side="left")

            self.vol_stat_var = tk.StringVar(value="None")
            self.vol_stat_dd = CTkComboBox(vol_stat_search,
                                            variable=self.vol_stat_var,
                                            values=["Low Count", "Average Count", "High Count"],
                                            width=100,
                                            height=25,
                                            border_width=1,
                                            corner_radius=6)
            self.vol_stat_dd.pack(side="left", padx=5) 

            self.srch_btn = self.add_del_upd('SEARCH', '#5dade2', command=self.upd_srch)
            self.add_btn = self.add_del_upd('ADD MATERIAL', '#2ecc71', command=self.add_mats)
            self.del_btn = self.add_del_upd('DELETE MATERIAL', '#e74c3c', command=self.del_mats)
            self.update_btn = self.add_del_upd('UPDATE MATERIAL', '#f39c12', command=self.upd_mats)



            # Treeview style
            style = ttk.Style(self)
            style.theme_use("default")
            style.configure("Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white", font=('Arial', 11), bordercolor="#cccccc", borderwidth=1)
            style.configure("Treeview.Heading", background="#007acc", foreground="white", font=('futura', 13, 'bold'))
            style.map("Treeview", background=[('selected', '#b5d9ff')])

            tree_frame = tk.Frame(self)
            tree_frame.place(x=120, y=105, width=1100, height=475)

            self.inventory_tree = ttk.Treeview(        
            tree_frame, columns=('mat_id', 'mat_name', 'mat_description', 'mat_volume', 'current_stock', 'unit_of_measure', 'min_stock_level', 'mat_order_date', 'supplier_id', 'last_restocked', 'shelf_life_days'), show='headings', style='Treeview')
            self._column_heads('mat_id', 'MATERIAL ID')
            self._column_heads('mat_name', 'NAME')
            self._column_heads('mat_description', 'DESCRIPTION')
            self._column_heads('mat_volume', 'VOLUME')
            self._column_heads('current_stock', 'CURRENT STOCK')
            self._column_heads('unit_of_measure', 'UNIT OF MEASUREMENT')
            self._column_heads('mat_volume', 'MATERIAL VOLUME')
            self._column_heads('min_stock_level', 'MINIMUM STOCK LEVEL')
            self._column_heads('mat_order_date', 'DELIVERY DATE')
            self._column_heads('supplier_id', 'SUPPLIER ID')
            self._column_heads('last_restocked', 'LAST RESTOCKED')
            self._column_heads('shelf_life_days', 'SHELF LIFE (DAYS)')
            for col in ('mat_id', 'mat_name', 'mat_description', 'mat_volume', 'current_stock', 'unit_of_measure', 'min_stock_level', 'mat_order_date', 'supplier_id', 'last_restocked', 'shelf_life_days'):
                self.inventory_tree.column(col, width=200, stretch=False)

            # Scrollbars
            self.scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.inventory_tree.yview)
            self.h_scrollbar = tk.Scrollbar(tree_frame, orient="horizontal", command=self.inventory_tree.xview)
            self.inventory_tree.configure(yscrollcommand=self.scrollbar.set, xscrollcommand=self.h_scrollbar.set)

            # Use grid for proper layout
            self.inventory_tree.grid(row=0, column=0, sticky="nsew")
            self.scrollbar.grid(row=0, column=1, sticky="w")
            self.h_scrollbar.grid(row=1, column=0, sticky="ew")

            # Make the treeview expandable
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)
            self.load_mats_from_db()

    def _column_heads(self, columns, text):
        self.inventory_tree.heading(columns, text=text)
        self.inventory_tree.column(columns, width=195)

    def add_del_upd(self, text, fg_color, command):
        button = CTkButton(self, text=text, width=73, fg_color=fg_color, command=command)
        button.pack(side="left", anchor="n", padx=4)

    def _add_mat(self, label_text, y):
        label = CTkLabel(self.mat_window, text=label_text, font=('Futura', 15, 'bold'))
        label.pack(pady=(5, 0))
        entry = CTkEntry(self.mat_window, height=20, width=250, border_width=2, border_color='black')
        entry.pack(pady=(0, 10))
        return entry
    
    def load_mats_from_db(self):
        try:
            conn = sqlite3.connect("main.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM raw_mats")
            rows = cursor.fetchall()

            # Clear existing rows
            for i in self.inventory_tree.get_children():
                self.inventory_tree.delete(i)

            for row in rows:
                # row: ('mat_id', 'mat_name', 'mat_description', 'mat_volume', 'current_stock', 'unit_of_measure', 'min_stock_level', 'mat_order_date', 'supplier_id', 'last_restocked', 'shelf_life_days')
                tags = ()
                try:
                    current_stock = int(row[5]) if row[5] is not None else 0
                    min_stock_level = int(row[7]) if row[7] is not None else 0
                    if current_stock < min_stock_level:
                        tags = ('low',)
                except (ValueError, TypeError):
                    pass  # If conversion fails, skip highlighting
                self.inventory_tree.insert("", "end", values=row, tags=tags)
            self.inventory_tree.tag_configure('low', background='#ffe6e6')

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()


    def add_mats(self):
        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'owner', 'manager', 'supplier'):
            messagebox.showwarning("Access Denied", "You do not have permission to add materials.")
            return

        try:
            if hasattr(self, 'mat_window') and self.mat_window.winfo_exists():
                self.mat_window.lift()
                return

            self.mat_window = tk.Toplevel()
            self.mat_window.geometry('500x550')
            self.mat_window.title('Add Material')
            self.mat_window.config(bg='white')

            labels = [
                "Material ID:", "Material Name:", 'Material Description:',
                "Material Volume:", 'Current Stock', "Unit of Measurement:",
                "Minimum Stock Level:", "Shelf Life:"
            ]

            self.mat_entries = []
            for i, label_text in enumerate(labels):
                label = CTkLabel(self.mat_window, text=label_text, font=('Futura', 13, 'bold'))
                label.grid(row=i, column=0, padx=15, pady=10, sticky='e')
                entry = CTkEntry(self.mat_window, height=28, width=220, border_width=2, border_color='#6a9bc3')
                entry.grid(row=i, column=1, padx=10, pady=10, sticky='w')
                self.mat_entries.append(entry)

            # 🔹 Order Date (calendar)
            tk.Label(self.mat_window, text="Order Date:", font=('Futura', 13, 'bold'), bg='white').grid(
                row=len(labels), column=0, padx=15, pady=10, sticky='e'
            )
            self.order_date_entry = DateEntry(
                self.mat_window,
                width=18,
                background='darkblue',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd'
            )
            self.order_date_entry.grid(row=len(labels), column=1, padx=10, pady=10, sticky='w')

            # 🔹 Supplier dropdown
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute('SELECT supplier_id FROM suppliers')
            suppliers = [row[0] for row in c.fetchall()]
            conn.close()

            self.suppliers_ids = tk.StringVar()
            self.suppliers_ids.set(suppliers[0] if suppliers else "")

            CTkLabel(self.mat_window, text='Supplier ID:', font=('Futura', 13, 'bold')).grid(
                row=len(labels)+1, column=0, padx=15, pady=10, sticky='e'
            )
            self.suppliers_ids = tk.StringVar(value=suppliers[0] if suppliers else "")
            supplier_id_drop = CTkOptionMenu(
                self.mat_window,
                variable=self.suppliers_ids,
                values=suppliers if suppliers else [""]
            )
            supplier_id_drop.grid(row=len(labels)+1, column=1, padx=10, pady=10, sticky='w')

            def mat_to_db():
                user_id = self.controller.session.get('user_id')
                timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')

                mat_data = [e.get().strip() for e in self.mat_entries]
                order_date = self.order_date_entry.get_date().strftime('%Y-%m-%d')
                supplier_id = self.suppliers_ids.get().strip()

                mat_data.append(order_date)
                mat_data.append(supplier_id)

                # Validate required fields
                if not all(mat_data[:7]) or not supplier_id:
                    messagebox.showerror("Input Error", "All fields are required.")
                    return

                try:
                    conn = sqlite3.connect('main.db')
                    c = conn.cursor()
                    c.execute("""
                        INSERT INTO raw_mats (
                            mat_id, mat_name, mat_description,
                            mat_volume, current_stock, unit_of_measure,
                            min_stock_level, shelf_life_days, mat_order_date, supplier_id
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, tuple(mat_data))
                    conn.commit()

                    messagebox.showinfo("Success", "Material registered successfully!")
                    c.execute("""INSERT INTO user_logs (user_id, action, timestamp) VALUES (?,?,?)""",
                            (user_id, f"Added Material ID: {mat_data[0]}", timestamp))
                    conn.commit()
                    
                    # Log to user_activity.log
                    from log_f.user_activity_logger import user_activity_logger
                    username = self.controller.session.get('username')
                    user_activity_logger.log_activity(
                        user_id=user_id,
                        username=username,
                        action="create",
                        feature="inventory",
                        operation="add_material",
                        details=f"Added material ID: {mat_data[0]}, Name: {mat_data[1]}, Supplier: {supplier_id}"
                    )

                    self.load_mats_from_db()
                    self.mat_window.destroy()

                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", str(e))
                finally:
                    conn.close()

            submit_btn = CTkButton(
                self.mat_window, text='Submit All',
                font=("Arial", 12), width=120, height=30,
                bg_color='white', fg_color='blue',
                corner_radius=10, border_width=2, border_color='black',
                command=mat_to_db
            )
            submit_btn.grid(row=len(labels)+2, column=0, columnspan=3, pady=20)

        except Exception as e:
            print(f"Error while creating Add Materials window: {e}")

    
    def upd_srch(self):
        search = self.search_entry.get().strip()
        vol_stat = self.vol_stat_var.get().strip()
        user_id = self.controller.session.get('user_id')
        username = self.controller.session.get('username')

        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()

            if search:
                # Search by material name
                query = "SELECT * FROM raw_mats WHERE mat_name LIKE ? ORDER BY mat_name"
                params = (f'%{search}%',) * 11
                results = c.execute(query, params).fetchall()
                
                if not results:
                    messagebox.showinfo("No Results", f"No materials found matching '{search}'")
                    self.load_mats_from_db()
                    
                    # Log unsuccessful search to user_activity.log
                    from log_f.user_activity_logger import user_activity_logger
                    user_activity_logger.log_activity(
                        user_id=user_id,
                        username=username,
                        action="read",
                        feature="inventory",
                        operation="search_materials",
                        details=f"Search for '{search}' returned no results"
                    )
                    return

            elif vol_stat != "None":
                # Filter by volume status
                if vol_stat == "Low Count":
                    query = "SELECT * FROM raw_mats WHERE current_stock <= min_stock_level ORDER BY mat_name"
                elif vol_stat == "Average Count":
                    query = "SELECT * FROM raw_mats WHERE current_stock > min_stock_level AND current_stock <= min_stock_level * 2 ORDER BY mat_name"
                elif vol_stat == "High Count":
                    query = "SELECT * FROM raw_mats WHERE current_stock > min_stock_level * 2 ORDER BY mat_name"
                else:
                    self.load_mats_from_db()
                    return
                    
                results = c.execute(query).fetchall()
                
                if not results:
                    messagebox.showinfo("No Results", f"No materials with {vol_stat} status")
                    self.load_mats_from_db()
                    return
            else:
                self.load_mats_from_db()
                return

            for item in self.inventory_tree.get_children():
                self.inventory_tree.delete(item)
                
            for item in results:
                self.inventory_tree.insert("", "end", values=item)
                
            # Log successful search to user_activity.log
            from log_f.user_activity_logger import user_activity_logger
            search_term = search if search else f"Filter by {vol_stat}"
            user_activity_logger.log_activity(
                user_id=user_id,
                username=username,
                action="read",
                feature="inventory",
                operation="search_materials",
                details=f"Search for '{search_term}' returned {len(results)} results"
            )

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error executing query: {str(e)}")
            self.load_mats_from_db()
        finally:
            if 'conn' in locals():
                conn.close()

                                                


    def del_mats(self):
        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'owner', 'manager', 'supplier'):
            messagebox.showwarning("Access Denied", "You do not have permission to delete materials.")
            return


        user_id = self.controller.session.get('user_id')
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        selected = self.inventory_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select a material to delete.")
            return

        try:
            values = self.inventory_tree.item(selected, 'values')
            mat_id = values[0]  # Assuming client_id is the first column

            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete material ID '{mat_id}'?")
            if not confirm:
                return

            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            c.execute("SELECT * FROM raw_mats WHERE mat_id =  ?", (mat_id,))
            row = c.fetchone()

            if row:
                c.execute("DELETE FROM raw_mats WHERE mat_id = ?", (mat_id,))
                conn.commit()
                messagebox.showinfo("Deleted", f"Order ID '{mat_id}' has been deleted.")
                self.load_mats_from_db()
                c.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
                          (user_id, f"Deleted Material ID: {mat_id}", timestamp))
                conn.commit()
                
                # Log to user_activity.log
                from log_f.user_activity_logger import user_activity_logger
                username = self.controller.session.get('username')
                user_activity_logger.log_activity(
                    user_id=user_id,
                    username=username,
                    action="delete",
                    feature="inventory",
                    operation="delete_material",
                    details=f"Deleted material ID: {mat_id}, Name: {values[1]}"
                )
            else:
                messagebox.showinfo("Not Found", f"No material found with ID '{mat_id}'")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

        finally:
            conn.close()

    def upd_mats(self):
        if (user_type := self.controller.session.get('usertype')) not in ('admin', 'owner', 'manager', 'supplier'):
            messagebox.showwarning("Access Denied", "You do not have permission to add materials.")
            return
        user_id = self.controller.session.get('user_id')
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        selected = self.inventory_tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select a material to update.")
            return

        values = self.inventory_tree.item(selected, 'values')
        original_id = values[0]

        top = tk.Toplevel(self)
        top.title("Update Material")
        top.geometry("500x400")
        top.config(bg="white")

        fields = [
            ("Material ID", values[0], False),
            ("Material Name", values[1], True),
            ("Material Description", values[2], True),
            ("Material Volume", values[3], True),
            ("Current Stock", values[4], True),
            ("Unit of Measurement", values[5], True),
            ("Minimum Stock Level", values[6], True),
            ("Material Delivery Date", values[7], True),
            ("Supplier ID", values[8], False),
            ("Last Restocked", values[9], False),
            ("Shelf Life (Days)", values[10], False)
        ]
        entries = []

        for i, (label, value, editable) in enumerate(fields):
            lbl = CTkLabel(top, text=label + ":", font=('Futura', 13, 'bold'))
            lbl.grid(row=i, column=0, padx=15, pady=10, sticky='e')
            if label == "Material Delivery Date" or label == "Last Restocked":
                entry = DateEntry(top, width=18, background='darkblue', foreground='white', borderwidth=2)
                try:
                    entry.set_date(value)
                except Exception:
                    pass
            else:
                entry = CTkEntry(top, height=28, width=220, border_width=2, border_color='#6a9bc3')
                entry.insert(0, value)
                if not editable:
                    entry.configure(state='readonly')
            entry.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            entries.append(entry)

            try:
                conn = sqlite3.connect('main.db')
                c = conn.cursor()
                c.execute("SELECT supplier_id FROM suppliers")
                suppliers = [row[0] for row in c.fetchall()]

                if label == "Supplier ID":
                    entry.destroy()
                    supplier_var = tk.StringVar(value=value)
                    supplier_dropdown = CTkOptionMenu(top, variable=supplier_var, values=suppliers if suppliers else [""])
                    supplier_dropdown.grid(row=i, column=1, padx=10, pady=10, sticky='w')
                    entries[i] = supplier_dropdown

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
                return

        def update_material():
            material_id = entries[0].get().strip()
            material_name = entries[1].get().strip()
            material_description = entries[2].get().strip()
            mat_volume = entries[3].get().strip()
            current_stock = entries[4].get().strip()
            unit_of_measure = entries[5].get().strip()
            min_stock_level = entries[6].get().strip()
            delivery_date = entries[7].get_date().strftime('%Y-%m-%d')
            supplier_id = entries[8].get().strip()
            last_restocked = entries[9].get().strip()
            shelf_life = entries[10].get().strip()

            if not all([material_id, material_name, material_description, mat_volume, current_stock, unit_of_measure, min_stock_level, delivery_date, supplier_id, last_restocked, shelf_life]):
                messagebox.showerror("Input Error", "All fields are required.")
                return

            try:
                int(mat_volume)
                int(current_stock)
                int(min_stock_level)
                int(shelf_life)
            except ValueError:
                messagebox.showerror("Input Error", "Material Volume, Current Stock, Minimum Stock Level, and Shelf Life must be numeric.")
                return

            try:
                conn = sqlite3.connect('main.db')
                c = conn.cursor()
                c.execute('''
                    UPDATE raw_mats
                    SET mat_name=?, mat_description=?, mat_volume=?, current_stock=?, unit_of_measure=?, min_stock_level=?, mat_order_date=?, supplier_id=?, last_restocked=?, shelf_life_days=?
                    WHERE mat_id=?
                ''', (material_name, material_description, mat_volume, current_stock, unit_of_measure, min_stock_level, delivery_date, supplier_id, last_restocked, shelf_life, material_id))
                conn.commit()
                messagebox.showinfo("Success", "Material updated successfully!")
                self.load_mats_from_db()
                c.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
                        (user_id, f"Updated Material ID: {material_id}", timestamp))
                conn.commit()
                
                # Log to user_activity.log
                from log_f.user_activity_logger import user_activity_logger
                username = self.controller.session.get('username')
                user_activity_logger.log_activity(
                    user_id=user_id,
                    username=username,
                    action="update",
                    feature="inventory",
                    operation="update_material",
                    details=f"Updated material ID: {material_id}, Name: {material_name}, Description: {material_description}, Stock: {current_stock}"
                )
                top.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
            finally:
                conn.close()

        update_btn = CTkButton(top, text="Update", width=120, fg_color="#6a9bc3", command=update_material)
        update_btn.grid(row=len(fields), column=0, columnspan=2, pady=20)


    def mats_history(self, event):

        selected = self.inventory_tree.focus()

        if not selected:
            messagebox.showwarning("No selection", "Please select a material to view history.")
            return
        
        values = self.inventory_tree.item(selected, 'values')
        mat_id = values[0]
        mat_splr = values[4]

        try:

            conn = sqlite3.connect('main.db')
            c = conn.cursor()

            mat_info = c.execute("""
                SELECT rm.mat_id, rm.mat_name, rm.mat_volume, s.supplier_id
                FROM raw_mats rm
                JOIN suppliers s ON rm.supplier_id = s.supplier_id
                WHERE rm.mat_id = ? AND s.supplier_id = ?
            """, (mat_id, mat_splr)).fetchall()



            if not mat_info:
                messagebox.showerror('Error', f"No Material found with ID: {mat_id} and Supplier ID: {mat_splr}")
                return
            else:
                print('Supplier Info:', mat_info)

                mat_desc += "\n".join(f"Material ID: {row[0]}, Material Name: {row[1]}, Current Volume: {row[2]}, Ordered From: {row[3]}" for row in mat_info)

                popup = tk.Toplevel(self)
                popup.title(f"Material History: {mat_id}")
                popup.geometry("600x400")

                txt = tk.Text(popup, wrap="word", state="normal")
                txt.insert('1.0', mat_desc)
                txt.config(state='disabled')
                txt.pack(expand=True, fill='both', padx=10, pady=10)

        except sqlite3.Error as e:
            messagebox.showerror('Database Error', str(e))
            return
        except Exception as e:
            messagebox.showerror('Error', str(e))
            return
        finally:
            conn.close()

    def _main_buttons(self, parent, image, text, command):
        button = CTkButton(parent, image=image, text=text, bg_color="#6a9bc3", fg_color="#6a9bc3", hover_color="white",
        width=100, border_color="white", corner_radius=10, border_width=2, command=command, anchor='center')
        button.pack(side="top", padx=5, pady=15)

    def _images_buttons(self, image_path, size=(40, 40)):
        image = Image.open(image_path)
        size = size
        return CTkImage(image)

    def on_show(self):
        on_show(self)  # Calls the shared sidebar logic

    def handle_logout(self):
        handle_logout(self)