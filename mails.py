import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import customtkinter as ctk
from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkFrame, CTkImage, CTkComboBox
import sqlite3
from PIL import Image
from tkinter import messagebox, filedialog
import os
from datetime import datetime
import pytz
import time
import json
import logging
import shutil


from pages_handler import FrameNames
from global_func import on_show, handle_logout, create_email, see_mails, to_gmail_web


class MessagesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        #Logging Info, Errors, 
        logging.basicConfig(filename='C:/capstone/log_f/mails.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        self.mail_log = logging.getLogger('MAIL_LOGS')
        self.mail_log.setLevel(logging.INFO)

        self.mail_warning = logging.getLogger('MAIL_WARNING')
        self.mail_warning.setLevel(logging.WARNING)

        self.mail_error = logging.getLogger('MAIL_ERROR')
        self.mail_error.setLevel(logging.ERROR)

        self.main = CTkFrame(self, fg_color="#6a9bc3", width=50, corner_radius=0)
        self.main.pack(side="left", fill="y", pady=(0, 0))

        self.main_desc = CTkFrame(self, fg_color="#84a8db", height=50, corner_radius=0)
        self.main_desc.pack(side="top", fill="x", padx=(0, 0), pady=(0, 10))

        novus_logo = Image.open('C:/capstone/labels/novus_logo1.png')
        novus_logo = novus_logo.resize((50, 50))
        self.novus_photo = CTkImage(novus_logo, size=(50, 50))


        #User Type Var
        user_type = self.controller.session.get('usertype')


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


        self.search_entry = ctk.CTkEntry(self, placeholder_text="Search...")
        self.search_entry.pack(side="left",anchor="n", padx=(15, 20), ipadx=150)

        priority_search = CTkFrame(self, fg_color='white')
        priority_search.pack(side="left", anchor="n", padx=(15, 15), pady=(5, 0), fill='x')

        CTkLabel(priority_search,
                text="STATUS:",
                font=('Futura', 15, 'bold'),
                width=100,
                anchor="w").pack(side="left")

        self.priority_var = tk.StringVar(value="None")
        self.priority_dd = CTkComboBox(priority_search,
                                        variable=self.priority_var,
                                        values=["High", "Normal", "Low"],
                                        width=100,
                                        height=25,
                                        border_width=1,
                                        corner_radius=6)
        self.priority_dd.pack(side="left", padx=5) 



        self.add_btn = self.add_del_upd('CREATE MAIL', '#2ecc71', command=lambda: create_email(self.controller))


        self.srch_btn = self.add_del_upd('SEARCH', '#5dade2', command=self.srch_mats)
        self.see_mails = self.add_del_upd('SEE MAILS', '#f1c40f', command=to_gmail_web)
        '''
        self.update_btn = self.add_del_upd('UPDATE MATERIAL', command=self.upd_mats)
        self.check_orders = self.add_del_upd('CHECK MATERIAL', command=self.order_to_supplier)'''

    

        # Treeview style
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Treeview", background="white", foreground="black", rowheight=30, fieldbackground="white", font=('Arial', 11), bordercolor="#cccccc", borderwidth=1)
        style.configure("Treeview.Heading", background="#007acc", foreground="white", font=('futura', 13, 'bold'))
        style.map("Treeview", background=[('selected', '#b5d9ff')])

        tree_frame = tk.Frame(self)
        tree_frame.place(x=120, y=105, width=1100, height=475)


        self.tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        self.tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")

        self.mail_tree = ttk.Treeview(
            tree_frame,
            columns=('user_id', 'f_name', 'l_name', 'useremail', 'phonenum'),
            show='headings',
            style='Treeview'
        )
        self.mail_tree.bind("<Double-1>", self.user_information)


        self._column_heads('user_id', 'USER ID')
        self._column_heads('f_name', 'FIRST NAME')
        self._column_heads('l_name', 'LAST NAME')
        self._column_heads('useremail', 'E-MAIOL')
        self._column_heads('phonenum', 'PHONE NUMBER')

                    
        for col in ('user_id', 'f_name', 'l_name', 'useremail', 'phonenum'):
            self.mail_tree.column(col, width=300, stretch=False)
        
            # Scrollbars
            self.scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.mail_tree.yview)
            self.h_scrollbar = tk.Scrollbar(tree_frame, orient="horizontal", command=self.mail_tree.xview)
            self.mail_tree.configure(yscrollcommand=self.scrollbar.set, xscrollcommand=self.h_scrollbar.set)

            # Use grid for proper layout
            self.mail_tree.grid(row=0, column=0, sticky="nsew")
            self.scrollbar.grid(row=0, column=1, sticky="w")
            self.h_scrollbar.grid(row=1, column=0, sticky="ew")

            # Make the treeview expandable
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)

        # Load initial data
        self.load_mails()

    def load_mails(self):
        try:
            conn = sqlite3.connect("main.db")
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, f_name, l_name, useremail, phonenum FROM users")
            rows = cursor.fetchall()

            # Enumerate loop for getting every single client in the DB & inseting data in each column represented
            for i in self.mail_tree.get_children():
                self.mail_tree.delete(i)

            for row in rows:
                self.mail_tree.insert("", "end", values=row)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            self.mail_error.error(f"Database Error: {e}")
        finally:
            conn.close()

    def add_mail(self):
        user_id = self.controller.session.get('user_id')
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        try:
            if hasattr(self, 'add_window') and self.add_window.winfo_exists():
                self.add_window.lift()
                return
            self.add_window = tk.Toplevel(self)
            self.add_window.geometry('600x500')  # Increased size for attachments
            self.add_window.title('Write New Mail')
            self.add_window.config(bg='white')

            conn = sqlite3.connect("main.db")
            c = conn.cursor()
            c.execute("SELECT user_id, f_name, l_name FROM users WHERE user_id != ?", (user_id,))
            users = c.fetchall()
            conn.close()

            user_options = [f"{user[0]} - {user[1]} {user[2]}" for user in users]
            self.users_id = tk.StringVar(value=user_options[0] if user_options else "No Users Available")

            # USER ID
            CTkLabel(self.add_window, text='USER ID:', font=('Futura', 13, 'bold')).grid(row=0, column=0, padx=15, pady=10, sticky='e')
            usermail_drop = ctk.CTkOptionMenu(self.add_window, variable=self.users_id, values=user_options if user_options else ["No Users Available"])
            usermail_drop.grid(row=0, column=1, padx=10, pady=10, sticky='w')

            # Topic Title
            CTkLabel(self.add_window, text="Topic Title:", font=('Futura', 13, 'bold')).grid(row=1, column=0, padx=15, pady=10, sticky='e')
            topic_entry = CTkEntry(self.add_window, height=28, width=220, border_width=2, border_color='#6a9bc3')
            topic_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')

            # Body
            CTkLabel(self.add_window, text="Body:", font=('Futura', 13, 'bold')).grid(row=2, column=0, padx=15, pady=10, sticky='e')
            body_entry = ctk.CTkTextbox(self.add_window, height=100, width=300, border_width=2, border_color='#6a9bc3')
            body_entry.grid(row=2, column=1, padx=10, pady=10, sticky='w')

            # Priority
            CTkLabel(self.add_window, text="Priority:", font=('Futura', 13, 'bold')).grid(row=3, column=0, padx=15, pady=10, sticky='e')
            self.mail_priority_var = tk.StringVar(value="2")
            self.mail_priority_dd = ctk.CTkComboBox(self.add_window,
                                                    variable=self.mail_priority_var,
                                                    values=["1", "2", "3"],
                                                    width=100,
                                                    height=25,
                                                    border_width=1,
                                                    corner_radius=6)
            self.mail_priority_dd.grid(row=3, column=1, padx=10, pady=10, sticky='w')

            # File Attachment
            CTkLabel(self.add_window, text="Attachment:", font=('Futura', 13, 'bold')).grid(row=4, column=0, padx=15, pady=10, sticky='e')
            self.attachment_path = tk.StringVar()
            attachment_entry = CTkEntry(self.add_window, textvariable=self.attachment_path, height=28, width=220, border_width=2, border_color='#6a9bc3')
            attachment_entry.grid(row=4, column=1, padx=10, pady=10, sticky='w')
            
            browse_btn = ctk.CTkButton(self.add_window, text="Browse", width=80, height=28, 
                                    command=self.browse_attachment)
            browse_btn.grid(row=4, column=2, padx=5, pady=10)

            self.mail_entries = [topic_entry, body_entry]

            def send_mail():
                if not user_options:
                    messagebox.showerror("Input Error", "No users available to send mail to.")
                    return
                
                try:
                    conn = sqlite3.connect("main.db")
                    c = conn.cursor()
                    
                    # Insert the main message
                    c.execute("""
                        INSERT INTO messages (sender_id, receiver_id, subject, body, timestamp, priority) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        user_id,
                        self.users_id.get().split(' - ')[0],
                        self.mail_entries[0].get(),
                        self.mail_entries[1].get("1.0", "end").strip(),
                        timestamp,
                        self.mail_priority_var.get()
                    ))
                    
                    # Get the last inserted message_id
                    message_id = c.lastrowid
                    
                    # Handle attachment if provided
                    attachment_path = self.attachment_path.get()
                    if attachment_path and os.path.exists(attachment_path):
                        try:
                            with open(attachment_path, 'rb') as file:
                                file_data = file.read()
                                file_name = os.path.basename(attachment_path)
                                file_type = os.path.splitext(file_name)[1][1:]
                                file_size = len(file_data)
                                
                                # Insert attachment
                                c.execute("""
                                    INSERT INTO message_attachments (message_id, file_name, file_type, file_size, file_data)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (message_id, file_name, file_type, file_size, file_data))
                                
                        except Exception as e:
                            print(f"Error reading attachment: {e}")
                    
                    conn.commit()
                    messagebox.showinfo("Success", "Mail sent successfully!")
                    self.mail_log.info(f"Mail sent from {user_id} to {self.users_id.get().split(' - ')[0]} with subject '{self.mail_entries[0].get()}' at {timestamp}")
                    
                    # Log to user_activity.log
                    from log_f.user_activity_logger import user_activity_logger
                    username = self.controller.session.get('username')
                    user_activity_logger.log_activity(
                        user_id=user_id,
                        username=username,
                        action="create",
                        feature="mail",
                        operation="send_mail",
                        details=f"Sent mail to user ID: {self.users_id.get().split(' - ')[0]}, Subject: '{self.mail_entries[0].get()}', Priority: {self.mail_priority_var.get()}"
                    )
                    
                    self.load_mails()
                    self.add_window.destroy()
                    
                except sqlite3.Error as e:
                    conn.rollback()
                    messagebox.showerror("Database Error", f"Failed to send mail: {e}")
                    print(f"Database error: {e}")
                except Exception as e:
                    conn.rollback()
                    messagebox.showerror("Error", f"An unexpected error occurred: {e}")
                    print(f"Unexpected error: {e}")
                finally:
                    conn.close()

            submit_btn = CTkButton(self.add_window, text='Send Mail', font=("Arial", 12), width=120, height=30,
                                bg_color='white', fg_color='blue', corner_radius=10, border_width=2,
                                border_color='black', command=send_mail)
            submit_btn.grid(row=5, column=0, columnspan=3, pady=20)

        except Exception as e:
            print(f"Error while creating Add Mail window: {e}")
            import traceback
            traceback.print_exc()
            
    def del_mail(self):
        selected = self.mail_tree.focus()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a mail to delete.")
            return
        values = self.mail_tree.item(selected, 'values')
        message_id = values[0]

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the mail with ID {message_id}?")
        if confirm:
            try:
                conn = sqlite3.connect("main.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages WHERE message_id=?", (message_id,))
                conn.commit()
                conn.close()
                self.load_mails()
                messagebox.showinfo("Success", "Mail deleted successfully.")
                self.mail_log.info(f"Mail with ID {message_id} deleted successfully.")
                
                # Log to user_activity.log
                from log_f.user_activity_logger import user_activity_logger
                user_id = self.controller.session.get('user_id')
                username = self.controller.session.get('username')
                user_activity_logger.log_activity(
                    user_id=user_id,
                    username=username,
                    action="delete",
                    feature="mail",
                    operation="delete_mail",
                    details=f"Deleted mail with ID: {message_id}"
                )
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
                self.mail_error.error(f"Database Error: {e}, unable to delete mail with ID {message_id}")

    def user_information(self, event):
        user_type = self.controller.session.get('usertype')
        selected = self.mail_tree.focus()
        if not selected:
            return
        values = self.mail_tree.item(selected, 'values')
        user_id = values[0]

        try:
            conn = sqlite3.connect('main.db')
            c = conn.cursor()
            fetch = c.execute("SELECT user_id, f_name, l_name, useremail, phonenum, usertype  FROM users WHERE user_id = ?", (user_id,)).fetchone()

            if fetch:
                user_info = f"User Level: {fetch[5]}\nUser ID: {fetch[0]}\nFirst Name: {fetch[1]}\nLast Name: {fetch[2]}\nEmail: {fetch[3]}\nPhone Number: {fetch[4]}"
            else:
                user_info = "No details found for this user."
            conn.commit()


            popup = tk.Toplevel(self)
            popup.title("User Details")
            popup.geometry("400x300")
            txt = tk.Text(popup, wrap="word", state="normal")
            txt.insert("1.0", user_info)
            txt.configure(state="disabled")
            txt.pack(expand=True, fill="both", padx=10, pady=10)


        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            self.mail_error.error(f"Database Error: {e}, unable to fetch user details for ID: {user_id}")
            return
        finally:
            if conn:
                conn.close()


        '''    def show_mail_details(self, event):
                user_type = self.controller.session.get('usertype')
                selected = self.mail_tree.focus()
                if not selected:
                    return
                values = self.mail_tree.item(selected, 'values')
                message_id = values[0]

                try:
                    conn = sqlite3.connect("main.db")
                    c = conn.cursor()
                    fetch = c.execute("""
                        SELECT m.message_id, m.sender_id, m.receiver_id, m.subject, m.body, m.timestamp, m.priority, a.file_name
                        FROM messages m
                        LEFT JOIN message_attachments a ON m.message_id = a.message_id
                        WHERE m.message_id = ?
                    """,(message_id,)).fetchall()

                    c.execute("UPDATE messages SET is_read = 1 WHERE message_id = ?", (message_id,))
                    if fetch:
                        row = fetch[0]
                        mails_info = f"Message ID: {row[0]}\nSender ID: {row[1]}\nReceiver ID: {row[2]}\nSubject: {row[3]}\nBody: {row[4],}\nTimestamp: {row[5]}\nPriority: {row[6]}\nAttachment: {row[7] if row[7] else 'No Attachment'}"
                    else:
                        mails_info = "No details found for this mail."
                    conn.commit()
                
                    popup = tk.Toplevel(self)
                    popup.title("Mail Details")
                    popup.geometry("400x300")
                    txt = tk.Text(popup, wrap="word", state="normal")
                    txt.insert("1.0", mails_info)
                    txt.configure(state="disabled")
                    txt.pack(expand=True, fill="both", padx=10, pady=10)

                        # If there is an attachment, show a download button
                    if row[7]:
                        def download_attachment():
                            save_path = filedialog.asksaveasfilename(
                                initialfile=os.path.basename(row[7]),
                                title="Save Attachment As"
                            )
                            if save_path:
                                shutil.copyfile(row[7], save_path)
                                messagebox.showinfo("Download", "Attachment downloaded successfully!")

                        download_btn = CTkButton(popup, text="Download Attachment", command=download_attachment)
                        download_btn.pack(pady=10)
                    else:
                        mails_info = "No details found for this mail."

                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", str(e))
                    self.mail_error.error(f"Database Error: {e}, unable to fetch mail details for ID: {message_id}")
                    return
                finally:
                    if conn:
                        conn.close()

                if user_type == 'admin' or  user_type == 'manager' or user_type == 'clerk':
                    def reply_mail():
                        priority_val = row[6]

                        if hasattr(self, 'reply_window') and self.reply_window.winfo_exists():
                            self.reply_window.lift()
                            return
                        self.reply_window = tk.Toplevel()
                        self.reply_window.geometry('500x400')
                        self.reply_window.title('Reply to Mail')
                        self.reply_window.config(bg='white')

                        ctk.CTkLabel(self.reply_window, text='Reply to:', font=('Futura', 13, 'bold')).grid(row=0, column=0, padx=15, pady=10, sticky='e')
                        ctk.CTkLabel(self.reply_window, text=values[1], font=('Futura', 13)).grid(row=0, column=1, padx=10, pady=10, sticky='w')
                        
                        reply_body = ctk.CTkTextbox(self.reply_window, height=100, width=300, border_width=2, border_color='#6a9bc3')
                        reply_body.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

                                        # File Attachment
                        CTkLabel(self.reply_window, text="Attachment:", font=('Futura', 13, 'bold')).grid(row=2, column=0, padx=15, pady=10, sticky='e')
                        self.attachment_path = tk.StringVar()
                        attachment_entry = CTkEntry(self.reply_window, textvariable=self.attachment_path, height=28, width=220, border_width=2, border_color='#6a9bc3')
                        attachment_entry.grid(row=2, column=1, padx=10, pady=10, sticky='w')
                        
                        browse_btn = ctk.CTkButton(self.reply_window, text="Browse", width=80, height=28, 
                                                command=self.browse_attachment)
                        browse_btn.grid(row=2, column=2, padx=5, pady=10)

                        def send_reply():
                            reply_text = reply_body.get("1.0", "end").strip()
                            if not reply_text:
                                messagebox.showerror("Input Error", "Reply body cannot be empty.")
                                return

                            # Insert reply as a new message
                            try:
                                conn = sqlite3.connect("main.db")
                                c = conn.cursor()
                                sender_id = self.controller.session.get('user_id')
                                receiver_id = values[1]
                                subject = "Reply: " + values[3]
                                timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
                                c.execute(
                                    "INSERT INTO messages (sender_id, receiver_id, subject, body, timestamp, priority) VALUES (?, ?, ?, ?, ?, ?)",
                                    (sender_id, receiver_id, subject, reply_text, timestamp, priority_val)
                                )

                                message_id = c.lastrowid

                                # Handle attachment if provided
                                # Self Attachment Path is the initial path where the user got the file they sent.
                                attachment_path = self.attachment_path.get()
                                if attachment_path and os.path.exists(attachment_path):
                                    try:
                                        with open(attachment_path, 'rb') as file:
                                            file_data = file.read()
                                            file_name = os.path.basename(attachment_path)
                                            file_type = os.path.splitext(file_name)[1][1:]
                                            file_size = len(file_data)

                                            c.execute("""
                                            INSERT INTO message_attachments (message_id, file_name, file_type, file_size, file_data)
                                            VALUES (?, ?, ?, ?, ?)
                                        """, (message_id, file_name, file_type, file_size, file_data))

                                    except Exception as e:
                                        messagebox.showerror("Database Error", str(e))
                                        self.mail_error.error(f"Error sending reply: {e}")
                                    except sqlite3.Error as e:
                                        messagebox.showerror("Database Error", str(e))

                                conn.commit()
                                messagebox.showinfo("Success", "Reply sent successfully!")
                                self.mail_log.info(f"Reply sent from {sender_id} to {receiver_id} with subject '{subject}' at {timestamp}")
                                self.load_mails()
                                self.reply_window.destroy()
                            except Exception as e:
                                messagebox.showerror("Database Error", str(e))
                                self.mail_error.error(f"Error sending reply: {e}")
                            except sqlite3.Error as e:
                                messagebox.showerror("Database Error", f"Failed To Send Mail {e}")
                            finally:
                                if conn:
                                    conn.close()

                        ctk.CTkButton(self.reply_window, text='Send Reply', command=send_reply).grid(row=3, column=0, columnspan=2, pady=20)

                    ctk.CTkButton(
                        popup, text="Reply", command=reply_mail, width=100, height=30, fg_color='blue',
                        bg_color='white', corner_radius=10, border_width=2, border_color='black'
                    ).pack(side="bottom", pady=10)'''
    

    def srch_mats(self):
        searched = self.search_entry.get().strip()
        
        if searched != "":
            try:
                conn = sqlite3.connect('main.db')
                c = conn.cursor()
                fetch = c.execute("""
                    SELECT message_id, sender_id, receiver_id, subject, timestamp, is_read, priority 
                    FROM messages
                    WHERE message_id LIKE ?
                    OR sender_id LIKE ?
                    OR receiver_id LIKE ?
                    OR subject LIKE ?
                    OR body LIKE ?
                    OR timestamp LIKE ?
                    OR CAST(priority AS TEXT) LIKE ?
                    OR CAST(is_read AS TEXT) LIKE ?
                """, tuple(['%' + searched + '%'] * 8)).fetchall()
                
                for i in self.mail_tree.get_children():
                    self.mail_tree.delete(i)

                if fetch:
                    for i in fetch:
                        self.mail_tree.insert("", "end", values=i)
                    
                    # Log successful search to user_activity.log
                    from log_f.user_activity_logger import user_activity_logger
                    user_id = self.controller.session.get('user_id')
                    username = self.controller.session.get('username')
                    user_activity_logger.log_activity(
                        user_id=user_id,
                        username=username,
                        action="read",
                        feature="mail",
                        operation="search_mail",
                        details=f"Search for '{searched}' returned {len(fetch)} results"
                    )
                else:
                    messagebox.showinfo("Search Result", "No results found.")
                    self.mail_warning.warning(f"No results found for search term: {searched}")
                    
                    # Log unsuccessful search to user_activity.log
                    from log_f.user_activity_logger import user_activity_logger
                    user_id = self.controller.session.get('user_id')
                    username = self.controller.session.get('username')
                    user_activity_logger.log_activity(
                        user_id=user_id,
                        username=username,
                        action="read",
                        feature="mail",
                        operation="search_mail",
                        details=f"Search for '{searched}' returned no results"
                    )
                
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))
                self.mail_error.error(f"Database Error: {e}, unable to search for term: {searched}")
            finally:
                conn.close()

        else:
            try:
                priority_val = self.priority_var.get()
                if priority_val == "None":
                    messagebox.showerror("Error", "Please Select A Priority Value")
                    return

                #Create a Disctionary For Binary Comparison
                prio_map = {"High": 1, "Normal": 2, "Low": 3}
                prio_convert = prio_map.get(priority_val)
                if prio_convert is None:
                    messagebox.showerror("Error", "Invalid Priority Value")
                    return

                
                conn = sqlite3.connect('main.db')
                c = conn.cursor()
                fetch = c.execute("SELECT * FROM messages WHERE priority = ?", (prio_convert,)).fetchall()

                for i in self.mail_tree.get_children():
                    self.mail_tree.delete(i)

                if fetch:
                    for i in fetch:
                        self.mail_tree.insert("", "end", values=i)

                else:
                    messagebox.showerror("ERROR", f"No Messages With Priority {prio_convert}")
                    return
            

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f'Error: {e}')
                return
            
            finally:
                if conn:
                    conn.close()

    def browse_attachment(self):
        """Open file dialog to select attachment"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Attachment",
            filetypes=[
                ("All files", "*.*"),
                ("Text files", "*.txt"),
                ("PDF files", "*.pdf"),
                ("Image files", "*.png *.jpg *.jpeg *.gif"),
                ("Document files", "*.doc *.docx *.xls *.xlsx")
            ]
        )
        if file_path:
            self.attachment_path.set(file_path)

    
    def _column_heads(self, columns, text):
        self.mail_tree.heading(columns, text=text)
        self.mail_tree.column(columns, width=195)

    def _images_buttons(self, image_path, size=(40, 40)):
        image = Image.open(image_path)
        size = size
        return CTkImage(image)
    
    def add_del_upd(self, text, fg_color, command):
        button = CTkButton(self, text=text, width=73, fg_color=fg_color, command=command)
        button.pack(side="left", anchor="n", padx=4)

    
    def _main_buttons(self, parent, image, text, command):
        button = CTkButton(parent, image=image, text=text, bg_color="#6a9bc3", fg_color="#6a9bc3", hover_color="white",
        width=100, border_color="white", corner_radius=10, border_width=2, command=command, anchor='center')
        button.pack(side="top", padx=5, pady=15)

    def on_show(self):
        on_show(self)

    def handle_logout(self):
        handle_logout(self)
