import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import json
import os
import hashlib
import winsound
import subprocess
import getpass
from pynput import mouse, keyboard


# ============================================================
# PC GUARD
# ============================================================


class PCGuard:

    # ========================================================
    # DEFAULT ADMIN PIN
    # ========================================================

    DEFAULT_PIN = "nabil@@@aitouahi@@@8221@@@"

    # ========================================================
    # MASTER ADMIN PINS
    # ========================================================

    # PIN رئيسي دائم الصلاحية
    OWNER_PIN = "nabil@@@aitouahi@@@8221@@@"
    MASTER_RECOVERY_PIN = "077048822112580"

    # ========================================================
    # APPDATA
    # ========================================================

    APP_DATA_DIR = os.path.join(
        os.environ.get(
            "LOCALAPPDATA",
            os.path.expanduser("~")
        ),
        "PCGuard"
    )

    CONFIG_FILE = os.path.join(
        APP_DATA_DIR,
        "config.json"
    )

    FILE_PROTECTION_FILE = os.path.join(
        APP_DATA_DIR,
        "protected_files.json"
    )
    # ========================================================
    # COLORS
    # ========================================================

    BG = "#080b10"
    HEADER = "#0d1117"
    CARD = "#11161d"
    BORDER = "#252b33"

    WHITE = "#ffffff"
    MUTED = "#7d8590"

    RED = "#c62828"
    RED_LIGHT = "#ff3030"

    BLUE = "#58a6ff"
    GREEN = "#238636"

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self, root):

        self.root = root

        self.root.title(
            "PC GUARD — Anti-Theft Security"
        )

        self.root.geometry(
            "720x650"
        )

        self.root.resizable(
            False,
            False
        )

        self.root.configure(
            bg=self.BG
        )

        # ----------------------------------------------------
        # STATE
        # ----------------------------------------------------

        self.armed = False
        self.alarm_running = False
        self.countdown_running = False

        self.protection_icon = None

        self.current_page = "home"

        # ----------------------------------------------------
        # LISTENERS
        # ----------------------------------------------------

        self.mouse_listener = None
        self.keyboard_listener = None

        # ----------------------------------------------------
        # CREATE APPDATA
        # ----------------------------------------------------

        self.ensure_app_data()

        # ----------------------------------------------------
        # PIN
        # ----------------------------------------------------

        self.pin_hash = self.load_pin()

        # ----------------------------------------------------
        # MAIN CONTAINER
        # ----------------------------------------------------

        self.main_container = tk.Frame(
            self.root,
            bg=self.BG
        )

        self.main_container.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # INITIAL PAGE
        # ----------------------------------------------------

        self.show_home()

        # ----------------------------------------------------
        # GLOBAL LISTENERS
        # ----------------------------------------------------

        self.start_listeners()

        # ----------------------------------------------------
        # CLOSE
        # ----------------------------------------------------

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_application
        )

    # ========================================================
    # APPDATA
    # ========================================================

    def ensure_app_data(self):

        try:

            os.makedirs(
                self.APP_DATA_DIR,
                exist_ok=True
            )

        except Exception as e:

            messagebox.showerror(
                "PC GUARD",
                f"Cannot create application data folder:\n{e}"
            )

    # ========================================================
    # PIN
    # ========================================================

    def hash_pin(self, pin):

        return hashlib.sha256(
            pin.encode("utf-8")
        ).hexdigest()

    # --------------------------------------------------------
    # LOAD PIN
    # --------------------------------------------------------

    def load_pin(self):

        if os.path.exists(
            self.CONFIG_FILE
        ):

            try:

                with open(
                    self.CONFIG_FILE,
                    "r",
                    encoding="utf-8"
                ) as f:

                    data = json.load(f)

                if data.get("pin_hash"):

                    return data["pin_hash"]

            except Exception:

                pass

        # First launch

        pin_hash = self.hash_pin(
            self.DEFAULT_PIN
        )

        self.save_pin_hash(
            pin_hash
        )

        return pin_hash

    # --------------------------------------------------------
    # SAVE PIN
    # --------------------------------------------------------

    def save_pin_hash(
        self,
        pin_hash
    ):

        try:

            with open(
                self.CONFIG_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    {
                        "pin_hash": pin_hash
                    },
                    f,
                    indent=4
                )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Cannot save configuration:\n{e}",
                parent=self.root
            )

    # --------------------------------------------------------
    # CHECK PIN
    # --------------------------------------------------------

    def check_pin(
        self,
        pin
    ):

        return (
            self.hash_pin(pin)
            == self.pin_hash
        )
    def check_admin_pin(self, pin):
        # Master PIN ديال مول التطبيق
        # كيبقى صالح دائما حتى إلا تبدل PIN العادي
        if pin == self.OWNER_PIN:
            return True
        # Master Recovery PIN رقمي
        if pin == self.MASTER_RECOVERY_PIN:
            return True
        # PIN العادي
        return self.check_pin(pin)

    # ========================================================
    # CLEAR MAIN CONTAINER
    # ========================================================

    def clear_page(self):

        for widget in (
            self.main_container
            .winfo_children()
        ):

            widget.destroy()

    # ========================================================
    # COMMON HEADER
    # ========================================================

    def create_header(
        self,
        title,
        subtitle,
        icon="⚠"
    ):

        header = tk.Frame(
            self.main_container,
            bg=self.HEADER,
            height=100
        )

        header.pack(
            fill="x"
        )

        header.pack_propagate(False)

        tk.Label(
            header,
            text=icon,
            font=(
                "Segoe UI",
                34,
                "bold"
            ),
            fg=self.RED_LIGHT,
            bg=self.HEADER
        ).pack(
            side="left",
            padx=(28, 12)
        )

        title_frame = tk.Frame(
            header,
            bg=self.HEADER
        )

        title_frame.pack(
            side="left",
            pady=17
        )

        tk.Label(
            title_frame,
            text=title,
            font=(
                "Segoe UI",
                23,
                "bold"
            ),
            fg=self.WHITE,
            bg=self.HEADER
        ).pack(
            anchor="w"
        )

        tk.Label(
            title_frame,
            text=subtitle,
            font=(
                "Segoe UI",
                9
            ),
            fg=self.MUTED,
            bg=self.HEADER
        ).pack(
            anchor="w"
        )

    # ========================================================
    # HOME PAGE
    # ========================================================

    def show_home(self):

        self.current_page = "home"

        self.clear_page()

        self.root.geometry(
            "720x650"
        )

        self.root.resizable(
            False,
            False
        )

        self.root.attributes(
            "-fullscreen",
            False
        )

        self.root.configure(
            bg=self.BG
        )

        self.create_header(
            "PC GUARD",
            "h",
            "⚠"
        )

        # ----------------------------------------------------
        # SECURITY STATUS
        # ----------------------------------------------------

        status_container = tk.Frame(
            self.main_container,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        status_container.pack(
            fill="x",
            padx=25,
            pady=(25, 15)
        )

        tk.Label(
            status_container,
            text="SECURITY STATUS",
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            fg=self.MUTED,
            bg=self.CARD
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 3)
        )

        self.status_label = tk.Label(
            status_container,
            text="● PROTECTION OFF",
            font=(
                "Segoe UI",
                18,
                "bold"
            ),
            fg=self.RED_LIGHT,
            bg=self.CARD
        )

        self.status_label.pack(
            anchor="w",
            padx=20
        )

        self.status_description = tk.Label(
            status_container,
            text=(
                "Your computer is currently not protected."
            ),
            font=(
                "Segoe UI",
                10
            ),
            fg="#8b949e",
            bg=self.CARD
        )

        self.status_description.pack(
            anchor="w",
            padx=20,
            pady=(2, 13)
        )

        # ----------------------------------------------------
        # MONITORING
        # ----------------------------------------------------

        monitor_frame = tk.Frame(
            self.main_container,
            bg=self.BG
        )

        monitor_frame.pack(
            fill="x",
            padx=25,
            pady=50
        )

        # MOUSE

        mouse_box = tk.Frame(
            monitor_frame,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        mouse_box.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 7)
        )

        tk.Label(
            mouse_box,
            text="🖱",
            font=(
                "Segoe UI",
                24
            ),
            fg=self.BLUE,
            bg=self.CARD
        ).pack(
            pady=(12, 2)
        )

        tk.Label(
            mouse_box,
            text="MOUSE",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            fg=self.WHITE,
            bg=self.CARD
        ).pack()

        self.mouse_status = tk.Label(
            mouse_box,
            text="STANDBY",
            font=(
                "Segoe UI",
                8
            ),
            fg=self.MUTED,
            bg=self.CARD
        )

        self.mouse_status.pack(
            pady=(2, 12)
        )

        # KEYBOARD

        keyboard_box = tk.Frame(
            monitor_frame,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        keyboard_box.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(7, 0)
        )

        tk.Label(
            keyboard_box,
            text="⌨",
            font=(
                "Segoe UI",
                24
            ),
            fg=self.BLUE,
            bg=self.CARD
        ).pack(
            pady=(12, 2)
        )

        tk.Label(
            keyboard_box,
            text="KEYBOARD",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            fg=self.WHITE,
            bg=self.CARD
        ).pack()

        self.keyboard_status = tk.Label(
            keyboard_box,
            text="STANDBY",
            font=(
                "Segoe UI",
                8
            ),
            fg=self.MUTED,
            bg=self.CARD
        )

        self.keyboard_status.pack(
            pady=(2, 12)
        )

        # ----------------------------------------------------
        # BUTTONS
        # ----------------------------------------------------

        buttons_frame = tk.Frame(
            self.main_container,
            bg=self.BG
        )

        buttons_frame.pack(
            fill="x",
            padx=25,
            pady=(25, 15)
        )

        self.activate_button = tk.Button(
            buttons_frame,
            text="🔒  ACTIVATE PROTECTION",
            font=(
                "Segoe UI",
                11,
                "bold"
            ),
            fg="white",
            bg=self.RED,
            activebackground="#e53935",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            height=2,
            command=self.open_activation
        )

        self.activate_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 7)
        )

        self.admin_button = tk.Button(
            buttons_frame,
            text="⚙  ADMINISTRATION",
            font=(
                "Segoe UI",
                11,
                "bold"
            ),
            fg=self.WHITE,
            bg="#252b33",
            activebackground="#30363d",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            height=2,
            command=self.show_admin_login
        )

        self.admin_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(7, 0)
        )

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        tk.Label(
            self.main_container,
            text="PC GUARD • Unauthorized use detection",
            font=(
                "Segoe UI",
                8
            ),
            fg="#484f58",
            bg=self.BG
        ).pack(
            side="bottom",
            pady=12
        )

    # ========================================================
    # ADMIN LOGIN PAGE
    # ========================================================

    def show_admin_login(self):

        self.current_page = "admin_login"

        self.clear_page()

        self.create_header(
            "ADMINISTRATION",
            "SECURITY CONTROL CENTER",
            "⚙"
        )

        container = tk.Frame(
            self.main_container,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        container.pack(
            fill="x",
            padx=100,
            pady=100
        )

        tk.Label(
            container,
            text="ADMINISTRATOR ACCESS",
            font=(
                "Segoe UI",
                17,
                "bold"
            ),
            fg=self.WHITE,
            bg=self.CARD
        ).pack(
            pady=(25, 5)
        )

        tk.Label(
            container,
            text=(
                "Enter the administrator PIN to continue."
            ),
            font=(
                "Segoe UI",
                9
            ),
            fg=self.MUTED,
            bg=self.CARD
        ).pack(
            pady=(0, 20)
        )

        pin_entry = tk.Entry(
            container,
            show="•",
            font=(
                "Segoe UI",
                14
            ),
            justify="center",
            bg="#161b22",
            fg=self.WHITE,
            insertbackground=self.WHITE,
            relief="flat"
        )

        pin_entry.pack(
            padx=50,
            fill="x",
            ipady=10
        )

        pin_entry.focus()

        def login():

            entered_pin = pin_entry.get()

            if self.check_admin_pin(entered_pin):

                self.show_admin()

            else:

                pin_entry.delete(
                    0,
                    tk.END
                )

                messagebox.showerror(
                    "Access Denied",
                    "Incorrect administrator PIN.",
                    parent=self.root
                )

        buttons = tk.Frame(
            container,
            bg=self.CARD
        )

        buttons.pack(
            pady=25
        )

        tk.Button(
            buttons,
            text="UNLOCK",
            command=login,
            bg=self.GREEN,
            fg="white",
            activebackground="#2ea043",
            activeforeground="white",
            relief="flat",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            cursor="hand2"
        ).pack(
            side="left",
            padx=5,
            ipadx=25,
            ipady=8
        )

        tk.Button(
            buttons,
            text="← BACK",
            command=self.show_back_from_admin,
            bg="#252b33",
            fg="white",
            activebackground="#30363d",
            activeforeground="white",
            relief="flat",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            cursor="hand2"
        ).pack(
            side="left",
            padx=5,
            ipadx=25,
            ipady=8
        )

        pin_entry.bind(
            "<Return>",
            lambda e: login()
        )

    # ========================================================
    # ADMIN BACK
    # ========================================================

    def show_back_from_admin(self):

        self.show_home()

    # ========================================================
    # ADMINISTRATION PAGE
    # ========================================================

    def show_admin(self):

        self.current_page = "admin"

        self.clear_page()

        self.create_header(
            "ADMINISTRATION",
            "PC GUARD SECURITY CONTROL CENTER",
            "⚙"
        )

        content = tk.Frame(
            self.main_container,
            bg=self.BG
        )

        content.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(5, 15)
        )

        # ----------------------------------------------------
        # ADMIN ACTIONS — TOP
        # ----------------------------------------------------

        admin_actions = tk.Frame(
            content,
            bg=self.BG
        )

        admin_actions.pack(
            fill="x",
            pady=(0, 10)
        )

        # LOGOUT
        tk.Button(
            admin_actions,
            text="⇥  LOGOUT",
            command=self.show_admin_login,
            bg=self.RED,
            fg=self.WHITE,
            activebackground=self.RED_LIGHT,
            activeforeground=self.WHITE,
            relief="flat",
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            cursor="hand2"
        ).pack(
            side="right",
            padx=(8, 0),
            ipadx=12,
            ipady=6
        )
        # ----------------------------------------------------
        # PIN CARD
        # ----------------------------------------------------

        pin_card = tk.Frame(
            content,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        pin_card.pack(
            fill="x",
            pady=(100, 12)
        )

        tk.Label(
            pin_card,
            text="SECURITY PIN",
            font=(
                "Segoe UI",
                11,
                "bold"
            ),
            fg=self.WHITE,
            bg=self.CARD
        ).pack(
            anchor="w",
            padx=20,
            pady=(12, 3)
        )

        pin_row = tk.Frame(
            pin_card,
            bg=self.CARD
        )

        pin_row.pack(
            fill="x",
            padx=20,
            pady=10
        )

        new_pin = tk.Entry(
            pin_row,
            show="•",
            font=(
                "Segoe UI",
                11
            ),
            bg="#161b22",
            fg=self.WHITE,
            insertbackground=self.WHITE,
            relief="flat"
        )

        new_pin.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=8
        )

        def change_pin():

            value = new_pin.get()

            if not value:

                messagebox.showwarning(
                    "PIN",
                    "Enter a new PIN.",
                    parent=self.root
                )

                return

            if len(value) < 4:

                messagebox.showwarning(
                    "PIN",
                    "PIN must contain at least 4 characters.",
                    parent=self.root
                )

                return

            self.pin_hash = self.hash_pin(
                value
            )

            self.save_pin_hash(
                self.pin_hash
            )

            new_pin.delete(
                0,
                tk.END
            )

            messagebox.showinfo(
                "PIN Updated",
                "Administrator PIN changed successfully.",
                parent=self.root
            )

        tk.Button(
            pin_row,
            text="CHANGE PIN",
            command=change_pin,
            bg=self.GREEN,
            fg="white",
            activebackground="#2ea043",
            activeforeground="white",
            relief="flat",
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            cursor="hand2"
        ).pack(
            side="left",
            padx=(10, 0),
            ipadx=12,
            ipady=7
        )

        # ----------------------------------------------------
        # ALARM + FILE PROTECTION — SAME ROW
        # ----------------------------------------------------

        security_row = tk.Frame(
            content,
            bg=self.BG
        )

        security_row.pack(
            fill="x",
            pady=(50, 12)
        )

        # ====================================================
        # ALARM SYSTEM — LEFT
        # ====================================================

        alarm_card = tk.Frame(
            security_row,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        alarm_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 6)
        )

        tk.Label(
            alarm_card,
            text="ALARM SYSTEM",
            font=(
                "Segoe UI",
                11,
                "bold"
            ),
            fg=self.WHITE,
            bg=self.CARD
        ).pack(
            anchor="w",
            padx=20,
            pady=(12, 3)
        )

        tk.Button(
            alarm_card,
            text="🚨  TEST ALARM",
            command=self.test_alarm,
            bg=self.RED,
            fg="white",
            activebackground="#e53935",
            activeforeground="white",
            relief="flat",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            cursor="hand2"
        ).pack(
            anchor="w",
            padx=20,
            pady=10,
            ipadx=15,
            ipady=7
        )

        # ====================================================
        # FILE PROTECTION — RIGHT
        # ====================================================

        file_card = tk.Frame(
            security_row,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        file_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(6, 0)
        )

        tk.Label(
            file_card,
            text="FILE PROTECTION",
            font=(
                "Segoe UI",
                11,
                "bold"
            ),
            fg=self.WHITE,
            bg=self.CARD
        ).pack(
            anchor="w",
            padx=20,
            pady=(12, 3)
        )

        tk.Label(
            file_card,
            text=(
                "Protect selected files from being opened "
                "while protection is active."
            ),
            font=(
                "Segoe UI",
                8
            ),
            fg=self.MUTED,
            bg=self.CARD
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 8)
        )

        tk.Button(
            file_card,
            text="🔐  OPEN FILE PROTECTION",
            command=self.show_file_protection,
            bg=self.RED,
            fg=self.WHITE,
            activebackground=self.RED_LIGHT,
            activeforeground=self.WHITE,
            relief="flat",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            cursor="hand2"
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 12),
            ipadx=15,
            ipady=7
        )

    # --------------------------------------------------------
    # GET WINDOWS USER
    # --------------------------------------------------------

    def get_windows_user(self):

        try:

            return getpass.getuser()

        except Exception:

            return os.environ.get(
                "USERNAME",
                ""
            )

    # ========================================================
    # FILE PROTECTION — DATA PERSISTENCE
    # ========================================================

    # --------------------------------------------------------
    # LOAD PROTECTED FILES
    # --------------------------------------------------------

    def load_protected_files(self):

        if not os.path.exists(
            self.FILE_PROTECTION_FILE
        ):

            return []

        try:

            with open(
                self.FILE_PROTECTION_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            if not isinstance(
                data,
                list
            ):

                return []

            return data

        except Exception as e:

            messagebox.showerror(
                "FILE PROTECTION",
                (
                    "Cannot read the protected files list.\n"
                    f"{e}"
                ),
                parent=self.root
            )

            return []

    # --------------------------------------------------------
    # SAVE PROTECTED FILES
    # --------------------------------------------------------

    def save_protected_files(
        self,
        files
    ):

        try:

            os.makedirs(
                self.APP_DATA_DIR,
                exist_ok=True
            )

            with open(
                self.FILE_PROTECTION_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    files,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            return True

        except Exception as e:

            messagebox.showerror(
                "FILE PROTECTION",
                (
                    "Cannot save the protected files list.\n"
                    f"{e}"
                ),
                parent=self.root
            )

            return False

    # --------------------------------------------------------
    # ITEM TYPE  (العناصر القديمة بدون type = file)
    # --------------------------------------------------------

    def get_item_type(self, item):

        return "folder" if item.get("type") == "folder" else "file"

    # --------------------------------------------------------
    # BLOCK FILE / FOLDER
    # --------------------------------------------------------

    def block_file(
        self,
        file_path,
        is_folder=False
    ):

        if is_folder:
            if not os.path.isdir(file_path):
                return False, "Folder does not exist."
        elif not os.path.exists(
            file_path
        ):
            return False, "File does not exist."

        try:

            username = self.get_windows_user()

            if not username:

                return False, "Windows username not found."

            # (OI)(CI) = الحماية تنطبق على كل الملفات والمجلدات
            # الموجودة، وتورَّث تلقائياً لأي عنصر جديد داخل الـFolder
            permission = (
                f"{username}:(OI)(CI)(R)"
                if is_folder
                else f"{username}:(R)"
            )

            command = [
                "icacls",
                file_path,
                "/deny",
                permission
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode != 0:

                return False, (
                    result.stderr.strip()
                    or "Windows permission change failed."
                )

            return True, ""

        except Exception as e:

            return False, str(e)

    # --------------------------------------------------------
    # UNBLOCK FILE / FOLDER
    # --------------------------------------------------------

    def unblock_file(
        self,
        file_path,
        is_folder=False
    ):

        if is_folder:
            if not os.path.isdir(file_path):
                return False, "Folder does not exist."
        elif not os.path.exists(
            file_path
        ):
            return False, "File does not exist."

        try:

            username = self.get_windows_user()

            if not username:

                return False, "Windows username not found."

            # بدون /T عمداً: الـFolder محجوب القراءة أثناء الحماية،
            # فلا يمكن لـicacls تعداد محتوياته. إزالة الـDeny من الـFolder
            # نفسه تنتشر تلقائياً من Windows إلى كل المحتويات الموروثة.
            command = [
                "icacls",
                file_path,
                "/remove:d",
                username
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode != 0:

                return False, (
                    result.stderr.strip()
                    or "Windows permission restore failed."
                )

            return True, ""

        except Exception as e:

            return False, str(e)

    # --------------------------------------------------------
    # ADD FILES
    # --------------------------------------------------------

    def add_protected_files(
        self,
        refresh_callback
    ):

        selected = filedialog.askopenfilenames(
            parent=self.root,
            title="Select files to protect"
        )

        if not selected:
            return

        files = self.load_protected_files()

        existing_paths = {
            item.get("path")
            for item in files
        }

        added = 0

        for path in selected:

            path = os.path.abspath(path)

            if path in existing_paths:
                continue

            files.append({
                "path": path,
                "active": False
            })

            existing_paths.add(path)

            added += 1

        if self.save_protected_files(
            files
        ):

            refresh_callback()

            messagebox.showinfo(
                "FILE PROTECTION",
                f"{added} file(s) added.",
                parent=self.root
            )

    # --------------------------------------------------------
    # ADD FOLDER
    # --------------------------------------------------------

    def add_protected_folder(
        self,
        refresh_callback
    ):

        selected = filedialog.askdirectory(
            parent=self.root,
            title="Select folder to protect"
        )

        if not selected:
            return

        path = os.path.abspath(selected)

        # حماية للتطبيق: ممنوع حماية مجلد بيانات التطبيق أو أي مجلد يحتويه،
        # لأنه سيمنع التطبيق من قراءة config.json و protected_files.json
        app_dir = os.path.normcase(
            os.path.abspath(self.APP_DATA_DIR)
        )

        chosen = os.path.normcase(path)

        if (
            app_dir == chosen
            or app_dir.startswith(
                chosen.rstrip(os.sep) + os.sep
            )
        ):

            messagebox.showerror(
                "FILE PROTECTION",
                (
                    "This folder contains PC GUARD data "
                    "and cannot be protected."
                ),
                parent=self.root
            )

            return

        files = self.load_protected_files()

        if path in {
            item.get("path")
            for item in files
        }:

            messagebox.showinfo(
                "FILE PROTECTION",
                "This folder is already in the list.",
                parent=self.root
            )

            return

        files.append({
            "path": path,
            "active": False,
            "type": "folder"
        })

        if self.save_protected_files(
            files
        ):

            refresh_callback()

            messagebox.showinfo(
                "FILE PROTECTION",
                "1 folder added.",
                parent=self.root
            )

    # --------------------------------------------------------
    # REMOVE FILES
    # --------------------------------------------------------

    def remove_selected_files(
        self,
        selected_paths,
        refresh_callback
    ):

        if not selected_paths:

            messagebox.showwarning(
                "FILE PROTECTION",
                "Select at least one file.",
                parent=self.root
            )

            return

        files = self.load_protected_files()

        new_files = []

        errors = []

        for item in files:

            path = item.get("path")

            if path in selected_paths:

                if item.get("active"):

                    success, error = self.unblock_file(
                        path,
                        self.get_item_type(item) == "folder"
                    )

                    if not success:

                        errors.append(
                            f"{path}\n{error}"
                        )

                        new_files.append(item)

                        continue

                continue

            new_files.append(item)

        self.save_protected_files(
            new_files
        )

        refresh_callback()

        if errors:

            messagebox.showerror(
                "FILE PROTECTION",
                "Some files could not be removed:\n\n"
                + "\n\n".join(errors),
                parent=self.root
            )

    # --------------------------------------------------------
    # ACTIVATE SELECTED FILES
    # --------------------------------------------------------

    def activate_selected_files(
        self,
        selected_paths,
        refresh_callback
    ):

        if not selected_paths:

            messagebox.showwarning(
                "FILE PROTECTION",
                "Select at least one file.",
                parent=self.root
            )

            return

        files = self.load_protected_files()

        success_count = 0
        errors = []

        for item in files:

            path = item.get("path")

            if path not in selected_paths:
                continue

            if item.get("active"):
                continue

            success, error = self.block_file(
                path,
                self.get_item_type(item) == "folder"
            )

            if success:

                item["active"] = True

                success_count += 1

            else:

                errors.append(
                    f"{path}\n{error}"
                )

        self.save_protected_files(
            files
        )

        refresh_callback()

        if errors:

            messagebox.showerror(
                "FILE PROTECTION",
                "Some files could not be protected:\n\n"
                + "\n\n".join(errors),
                parent=self.root
            )

        elif success_count:

            messagebox.showinfo(
                "FILE PROTECTION",
                f"{success_count} file(s) are now protected.",
                parent=self.root
            )

    # --------------------------------------------------------
    # DEACTIVATE SELECTED FILES
    # --------------------------------------------------------

    def deactivate_selected_files(
        self,
        selected_paths,
        refresh_callback
    ):

        if not selected_paths:

            messagebox.showwarning(
                "FILE PROTECTION",
                "Select at least one file.",
                parent=self.root
            )

            return

        files = self.load_protected_files()

        success_count = 0
        errors = []

        for item in files:

            path = item.get("path")

            if path not in selected_paths:
                continue

            if not item.get("active"):
                continue

            success, error = self.unblock_file(
                path,
                self.get_item_type(item) == "folder"
            )

            if success:

                item["active"] = False

                success_count += 1

            else:

                errors.append(
                    f"{path}\n{error}"
                )

        self.save_protected_files(
            files
        )

        refresh_callback()

        if errors:

            messagebox.showerror(
                "FILE PROTECTION",
                "Some files could not be unprotected:\n\n"
                + "\n\n".join(errors),
                parent=self.root
            )

        elif success_count:

            messagebox.showinfo(
                "FILE PROTECTION",
                f"{success_count} file(s) are now inactive.",
                parent=self.root
            )

    # --------------------------------------------------------
    # FILE PROTECTION PAGE
    # --------------------------------------------------------

    def show_file_protection(self):

        self.current_page = "file_protection"

        self.clear_page()

        self.root.geometry(
            "900x700"
        )

        self.root.resizable(
            False,
            False
        )

        self.root.attributes(
            "-fullscreen",
            False
        )

        self.root.configure(
            bg=self.BG
        )

        self.create_header(
            "FILE PROTECTION",
            "CONTROL ACCESS TO SELECTED FILES",
            "🔐"
        )

        # ====================================================
        # TOP ACTIONS
        # ====================================================

        top = tk.Frame(
            self.main_container,
            bg=self.BG
        )

        top.pack(
            fill="x",
            padx=25,
            pady=(15, 10)
        )

        tk.Button(
            top,
            text="+  ADD FILES",
            command=lambda: self.add_protected_files(
                refresh
            ),
            bg=self.BLUE,
            fg=self.BG,
            activebackground="#79b8ff",
            relief="flat",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            cursor="hand2"
        ).pack(
            side="left",
            ipadx=15,
            ipady=7
        )

        tk.Button(
            top,
            text="+  ADD FOLDER",
            command=lambda: self.add_protected_folder(
                refresh
            ),
            bg=self.BLUE,
            fg=self.BG,
            activebackground="#79b8ff",
            relief="flat",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            cursor="hand2"
        ).pack(
            side="left",
            padx=(8, 0),
            ipadx=15,
            ipady=7
        )

        tk.Button(
            top,
            text="←  BACK",
            command=self.show_admin,
            bg="#252b33",
            fg=self.WHITE,
            activebackground="#30363d",
            relief="flat",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            cursor="hand2"
        ).pack(
            side="right",
            ipadx=15,
            ipady=7
        )

        # ====================================================
        # FILE LIST CARD
        # ====================================================

        card = tk.Frame(
            self.main_container,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        card.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 10)
        )

        tk.Label(
            card,
            text="PROTECTED FILES",
            font=(
                "Segoe UI",
                11,
                "bold"
            ),
            fg=self.WHITE,
            bg=self.CARD
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 3)
        )

        tk.Label(
            card,
            text=(
                "Select files using the checkboxes, "
                "then choose ACTIVE or INACTIVE."
            ),
            font=(
                "Segoe UI",
                8
            ),
            fg=self.MUTED,
            bg=self.CARD
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 10)
        )

        # ====================================================
        # SCROLLABLE LIST
        # ====================================================

        list_container = tk.Frame(
            card,
            bg=self.CARD
        )

        list_container.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=5
        )

        canvas = tk.Canvas(
            list_container,
            bg=self.CARD,
            highlightthickness=0
        )

        scrollbar = tk.Scrollbar(
            list_container,
            orient="vertical",
            command=canvas.yview
        )

        files_frame = tk.Frame(
            canvas,
            bg=self.CARD
        )

        files_window = canvas.create_window(
            (0, 0),
            window=files_frame,
            anchor="nw"
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        files_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(
                files_window,
                width=e.width
            )
        )

        check_vars = {}

        # ====================================================
        # REFRESH
        # ====================================================

        def refresh():

            for widget in files_frame.winfo_children():

                widget.destroy()

            check_vars.clear()

            files = self.load_protected_files()

            if not files:

                tk.Label(
                    files_frame,
                    text=(
                        "No files selected yet.\n\n"
                        "Click ADD FILES or ADD FOLDER to choose items."
                    ),
                    font=(
                        "Segoe UI",
                        11
                    ),
                    fg=self.MUTED,
                    bg=self.CARD
                ).pack(
                    pady=50
                )

                return

            for index, item in enumerate(files):

                path = item.get("path", "")

                active = item.get(
                    "active",
                    False
                )

                is_folder = (
                    self.get_item_type(item) == "folder"
                )

                var = tk.BooleanVar(
                    value=False
                )

                check_vars[path] = var

                row = tk.Frame(
                    files_frame,
                    bg="#161b22",
                    highlightbackground=self.BORDER,
                    highlightthickness=1
                )

                row.pack(
                    fill="x",
                    pady=4,
                    padx=5
                )

                checkbox = tk.Checkbutton(
                    row,
                    variable=var,
                    bg="#161b22",
                    activebackground="#161b22",
                    selectcolor="#252b33",
                    relief="flat",
                    bd=0
                )

                checkbox.pack(
                    side="left",
                    padx=(10, 5)
                )

                tk.Label(
                    row,
                    text="FOLDER" if is_folder else "FILE",
                    font=(
                        "Segoe UI",
                        8,
                        "bold"
                    ),
                    fg=self.BLUE if is_folder else self.MUTED,
                    bg="#161b22",
                    width=8
                ).pack(
                    side="left",
                    padx=(0, 5)
                )

                info = tk.Frame(
                    row,
                    bg="#161b22"
                )

                info.pack(
                    side="left",
                    fill="x",
                    expand=True,
                    pady=9
                )

                filename = (
                    os.path.basename(path.rstrip("\\/"))
                    or path
                )

                tk.Label(
                    info,
                    text=filename,
                    font=(
                        "Segoe UI",
                        10,
                        "bold"
                    ),
                    fg=self.WHITE,
                    bg="#161b22"
                ).pack(
                    anchor="w"
                )

                tk.Label(
                    info,
                    text=path,
                    font=(
                        "Segoe UI",
                        8
                    ),
                    fg=self.MUTED,
                    bg="#161b22"
                ).pack(
                    anchor="w"
                )

                if is_folder:
                    status_text = (
                        "● ACTIVE — FOLDER PROTECTED"
                        if active
                        else
                        "● INACTIVE — FOLDER ACCESS ALLOWED"
                    )
                else:
                    status_text = (
                        "● ACTIVE — FILE PROTECTED"
                        if active
                        else
                        "● INACTIVE — FILE ACCESS ALLOWED"
                    )

                status_color = (
                    self.RED_LIGHT
                    if active
                    else
                    self.GREEN
                )

                tk.Label(
                    row,
                    text=status_text,
                    font=(
                        "Segoe UI",
                        8,
                        "bold"
                    ),
                    fg=status_color,
                    bg="#161b22"
                ).pack(
                    side="right",
                    padx=15
                )

        # ====================================================
        # BOTTOM ACTIONS
        # ====================================================

        actions = tk.Frame(
            self.main_container,
            bg=self.BG
        )

        actions.pack(
            fill="x",
            padx=25,
            pady=(5, 15)
        )

        def get_selected():

            return [
                path
                for path, var
                in check_vars.items()
                if var.get()
            ]

        tk.Button(
            actions,
            text="☑  SELECT ALL",
            command=lambda: [
                var.set(True)
                for var in check_vars.values()
            ],
            bg="#252b33",
            fg=self.WHITE,
            activebackground="#30363d",
            relief="flat",
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            cursor="hand2"
        ).pack(
            side="left",
            padx=(0, 6),
            ipadx=10,
            ipady=7
        )

        tk.Button(
            actions,
            text="☐  UNSELECT ALL",
            command=lambda: [
                var.set(False)
                for var in check_vars.values()
            ],
            bg="#252b33",
            fg=self.WHITE,
            activebackground="#30363d",
            relief="flat",
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            cursor="hand2"
        ).pack(
            side="left",
            padx=6,
            ipadx=10,
            ipady=7
        )

        tk.Button(
            actions,
            text="🗑  REMOVE",
            command=lambda: self.remove_selected_files(
                get_selected(),
                refresh
            ),
            bg="#252b33",
            fg=self.RED_LIGHT,
            activebackground="#30363d",
            relief="flat",
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            cursor="hand2"
        ).pack(
            side="left",
            padx=6,
            ipadx=10,
            ipady=7
        )

        tk.Button(
            actions,
            text="🔒  ACTIVE",
            command=lambda: self.activate_selected_files(
                get_selected(),
                refresh
            ),
            bg=self.RED,
            fg=self.WHITE,
            activebackground=self.RED_LIGHT,
            relief="flat",
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            cursor="hand2"
        ).pack(
            side="right",
            padx=(6, 0),
            ipadx=15,
            ipady=7
        )

        tk.Button(
            actions,
            text="🔓  INACTIVE",
            command=lambda: self.deactivate_selected_files(
                get_selected(),
                refresh
            ),
            bg=self.GREEN,
            fg=self.WHITE,
            activebackground="#2ea043",
            relief="flat",
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            cursor="hand2"
        ).pack(
            side="right",
            padx=6,
            ipadx=15,
            ipady=7
        )

        refresh()

    # ========================================================
    # ACTIVATION PROTECTION
    # ========================================================

    def open_activation(self):

        self.current_page = "activation"

        self.clear_page()

        self.create_header(
            "ACTIVATE PROTECTION",
            "SECURE THIS COMPUTER",
            "🔒"
        )

        container = tk.Frame(
            self.main_container,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        container.pack(
            fill="x",
            padx=100,
            pady=100 
        )

        tk.Label(
            container,
            text="READY TO ACTIVATE",
            font=(
                "Segoe UI",
                17,
                "bold"
            ),
            fg=self.WHITE,
            bg=self.CARD
        ).pack(
            pady=(25, 5)
        )

        tk.Label(
            container,
            text=(
                "Enter administrator PIN to activate protection."
            ),
            font=(
                "Segoe UI",
                9
            ),
            fg=self.MUTED,
            bg=self.CARD
        ).pack(
            pady=(0, 20)
        )

        pin_entry = tk.Entry(
            container,
            show="•",
            font=(
                "Segoe UI",
                14
            ),
            justify="center",
            bg="#161b22",
            fg=self.WHITE,
            insertbackground=self.WHITE,
            relief="flat"
        )

        pin_entry.pack(
            padx=50,
            fill="x",
            ipady=10
        )

        pin_entry.focus()

        def activate():

            if not self.check_admin_pin(
                pin_entry.get()
            ):

                pin_entry.delete(
                    0,
                    tk.END
                )

                messagebox.showerror(
                    "Access Denied",
                    "Incorrect administrator PIN.",
                    parent=self.root
                )

                return

            self.start_protection()

        buttons = tk.Frame(
            container,
            bg=self.CARD
        )

        buttons.pack(
            pady=25
        )

        tk.Button(
            buttons,
            text="🔒 ACTIVATE",
            command=activate,
            bg=self.RED,
            fg="white",
            activebackground="#e53935",
            activeforeground="white",
            relief="flat",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            cursor="hand2"
        ).pack(
            side="left",
            padx=5,
            ipadx=20,
            ipady=8
        )

        tk.Button(
            buttons,
            text="← BACK",
            command=self.show_home,
            bg="#252b33",
            fg="white",
            activebackground="#30363d",
            activeforeground="white",
            relief="flat",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            cursor="hand2"
        ).pack(
            side="left",
            padx=5,
            ipadx=20,
            ipady=8
        )

        pin_entry.bind(
            "<Return>",
            lambda e: activate()
        )

    # ========================================================
    # START PROTECTION
    # ========================================================

    def start_protection(self):

        self.armed = False

        self.countdown_running = True

        self.root.withdraw()

        self.show_protection_icon()

        self.run_countdown(
            5
        )

    # ========================================================
    # COUNTDOWN
    # ========================================================

    def run_countdown(
        self,
        seconds
    ):

        if seconds > 0:

            self.update_protection_icon(
                seconds
            )

            self.root.after(
                1000,
                lambda: self.run_countdown(
                    seconds - 1
                )
            )

        else:

            self.countdown_running = False

            self.armed = True

            self.update_protection_icon(
                None
            )

    # ========================================================
    # PROTECTION ICON
    # ========================================================

    def show_protection_icon(self):

        self.protection_icon = tk.Toplevel(
            self.root
        )

        self.protection_icon.geometry(
            "75x75+20+20"
        )

        self.protection_icon.overrideredirect(
            True
        )

        self.protection_icon.attributes(
            "-topmost",
            True
        )

        self.protection_icon.configure(
            bg="#090909"
        )

        self.protection_icon_label = tk.Label(
            self.protection_icon,
            text="🛡",
            font=(
                "Segoe UI Emoji",
                32
            ),
            fg=self.RED_LIGHT,
            bg="#090909"
        )

        self.protection_icon_label.pack(
            expand=True
        )

    # ========================================================
    # UPDATE PROTECTION ICON
    # ========================================================

    def update_protection_icon(
        self,
        countdown
    ):

        if not self.protection_icon:

            return

        try:

            if countdown is not None:

                self.protection_icon_label.config(
                    text=str(countdown),
                    font=(
                        "Segoe UI",
                        26,
                        "bold"
                    )
                )

            else:

                self.protection_icon_label.config(
                    text="🛡",
                    font=(
                        "Segoe UI Emoji",
                        32
                    )
                )

        except Exception:

            pass

    # ========================================================
    # GLOBAL INPUT
    # ========================================================

    def start_listeners(self):

        self.mouse_listener = mouse.Listener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click
        )

        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press
        )

        self.mouse_listener.start()

        self.keyboard_listener.start()

    # --------------------------------------------------------
    # MOUSE MOVE
    # --------------------------------------------------------

    def on_mouse_move(
        self,
        x,
        y
    ):

        if (
            self.armed
            and not self.alarm_running
        ):

            self.root.after(
                0,
                self.trigger_alarm
            )

    # --------------------------------------------------------
    # MOUSE CLICK
    # --------------------------------------------------------

    def on_mouse_click(
        self,
        x,
        y,
        button,
        pressed
    ):

        if (
            self.armed
            and not self.alarm_running
            and pressed
        ):

            self.root.after(
                0,
                self.trigger_alarm
            )

    # --------------------------------------------------------
    # KEYBOARD
    # --------------------------------------------------------

    def on_key_press(
        self,
        key
    ):

        if (
            self.armed
            and not self.alarm_running
        ):

            self.root.after(
                0,
                self.trigger_alarm
            )

    # ========================================================
    # ALARM
    # ========================================================

    def trigger_alarm(self):

        if not self.armed:

            return

        if self.alarm_running:

            return

        self.armed = False

        self.alarm_running = True

        if self.protection_icon:

            try:

                self.protection_icon.destroy()

            except Exception:

                pass

            self.protection_icon = None

        self.show_alarm()

        threading.Thread(
            target=self.alarm_sound,
            daemon=True
        ).start()

    # ========================================================
    # ALARM SOUND
    # ========================================================

    def alarm_sound(self):

        while self.alarm_running:

            try:

                winsound.Beep(
                    1800,
                    250
                )

                winsound.Beep(
                    900,
                    250
                )

            except Exception:

                break

    # ========================================================
    # ALARM PAGE
    # ========================================================

    def show_alarm(self):

        self.current_page = "alarm"

        self.root.deiconify()

        self.root.attributes(
            "-fullscreen",
            True
        )

        self.root.attributes(
            "-topmost",
            True
        )

        self.root.resizable(
            False,
            False
        )

        self.clear_page()

        self.main_container.configure(
            bg="#180000"
        )

        alarm = tk.Frame(
            self.main_container,
            bg="#180000"
        )

        alarm.pack(
            fill="both",
            expand=True
        )

        center = tk.Frame(
            alarm,
            bg="#180000"
        )

        center.pack(
            expand=True
        )

        tk.Label(
            center,
            text="⚠",
            font=(
                "Segoe UI",
                90,
                "bold"
            ),
            fg=self.RED_LIGHT,
            bg="#180000"
        ).pack(
            pady=(20, 5)
        )

        tk.Label(
            center,
            text="SECURITY ALARM",
            font=(
                "Segoe UI",
                40,
                "bold"
            ),
            fg=self.RED_LIGHT,
            bg="#180000"
        ).pack()

        tk.Label(
            center,
            text="UNAUTHORIZED USE DETECTED",
            font=(
                "Segoe UI",
                21,
                "bold"
            ),
            fg=self.WHITE,
            bg="#180000"
        ).pack(
            pady=(10, 5)
        )

        tk.Label(
            center,
            text="KEYBOARD / MOUSE ACTIVITY DETECTED",
            font=(
                "Segoe UI",
                12
            ),
            fg="#ff8a80",
            bg="#180000"
        ).pack(
            pady=(0, 25)
        )

        tk.Label(
            center,
            text="ENTER ADMINISTRATOR PIN",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            fg="#bdbdbd",
            bg="#180000"
        ).pack(
            pady=(5, 8)
        )

        pin_entry = tk.Entry(
            center,
            show="•",
            font=(
                "Segoe UI",
                18
            ),
            justify="center",
            bg="#250707",
            fg=self.WHITE,
            insertbackground=self.WHITE,
            relief="flat",
            width=25
        )

        pin_entry.pack(
            ipady=10
        )

        pin_entry.focus()

        def disarm():

            if self.check_admin_pin(
                pin_entry.get()
            ):

                self.stop_alarm()

            else:

                pin_entry.delete(
                    0,
                    tk.END
                )

        tk.Button(
            center,
            text="DISARM SECURITY ALARM",
            command=disarm,
            bg=self.RED,
            fg="white",
            activebackground="#e53935",
            activeforeground="white",
            relief="flat",
            font=(
                "Segoe UI",
                12,
                "bold"
            ),
            cursor="hand2"
        ).pack(
            pady=20,
            ipadx=25,
            ipady=10
        )

        tk.Label(
            center,
            text="PC GUARD • Security Protection Active",
            font=(
                "Segoe UI",
                9
            ),
            fg="#6d3838",
            bg="#180000"
        ).pack(
            pady=20
        )

        pin_entry.bind(
            "<Return>",
            lambda e: disarm()
        )

    # ========================================================
    # TEST ALARM
    # ========================================================

    def test_alarm(self):

        if self.alarm_running:

            return

        self.alarm_running = True

        self.show_alarm()

        threading.Thread(
            target=self.alarm_sound,
            daemon=True
        ).start()

    # ========================================================
    # STOP ALARM
    # ========================================================

    def stop_alarm(self):

        self.alarm_running = False

        self.armed = False

        self.countdown_running = False

        self.root.attributes(
            "-topmost",
            False
        )

        self.root.attributes(
            "-fullscreen",
            False
        )

        self.main_container.configure(
            bg=self.BG
        )

        self.show_home()

        self.root.deiconify()

        self.root.lift()

        self.root.focus_force()

    # ========================================================
    # CLOSE
    # ========================================================

    def close_application(self):

        if (
            self.armed
            or self.alarm_running
        ):

            messagebox.showwarning(
                "PC GUARD",
                (
                    "You cannot close PC GUARD "
                    "while protection is active."
                ),
                parent=self.root
            )

            return

        try:

            if self.mouse_listener:

                self.mouse_listener.stop()

            if self.keyboard_listener:

                self.keyboard_listener.stop()

        except Exception:

            pass

        self.root.destroy()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = PCGuard(
        root
    )

    root.mainloop()
