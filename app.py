import flet as ft
import json
from datetime import datetime
import os
import requests
import base64
import asyncio
import pandas as pd
import re


# הגדרת מחלקות בסיסיות
class Contact:
    def __init__(self, name, phone, email="", group=""):
        self.name = name
        self.phone = phone
        self.email = email
        self.group = group

class Event:
    def __init__(self, title, date, time, location, participants=None):
        self.title = title
        self.date = date
        self.time = time
        self.location = location
        self.participants = participants or []
        self.pending_participants = [] 
        self.pending_notes = {}
        
class Group:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.members = []

class LoginManager:
    def __init__(self):
        self.current_user = None
        self.data_folder = "DATA"
        self.github_token = "your_github_token_here"  # יש להחליף בטוקן אמיתי
        self.page = None
        self.organization_field = None
        self.password_field = None
        self.error_text = None
        self.on_login_success = None
        self.temp_notes = {}

    def create_login_page(self, page, on_login_success):
        self.page = page
        self.on_login_success = on_login_success
        
        # הגדרות בסיסיות של החלון
        page.title = "כניסה למערכת"
        page.window_width = 400
        page.window_height = 400
        page.padding = 20
        page.rtl = True
        page.bgcolor = ft.colors.WHITE
        page.controls.clear()
        
        # יצירת שדות הטופס
        self.create_form_fields()
        
        # יצירת והצגת טופס ההתחברות
        login_form = self.create_login_form()
        page.add(
            ft.Container(
                content=login_form,
                alignment=ft.alignment.center
            )
        )
        page.update()

    def create_form_fields(self):
        self.organization_field = ft.TextField(
            label="שם ארגון",
            width=300,
            text_align="right",
            bgcolor=ft.colors.WHITE,
            focused_border_color=ft.colors.BLUE,
            prefix_icon=ft.Icons.BUSINESS
        )
        
        self.password_field = ft.TextField(
            label="סיסמה",
            width=300,
            password=True,
            text_align="right",
            bgcolor=ft.colors.WHITE,
            focused_border_color=ft.colors.BLUE,
            prefix_icon=ft.Icons.LOCK
        )
        
        self.error_text = ft.Text(
            color=ft.colors.RED,
            size=14,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )

# המשך מחלקת LoginManager
    def create_login_form(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Text(
                            "ברוכים הבאים",
                            size=32,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER
                        ),
                        margin=ft.margin.only(bottom=20)
                    ),
                    self.organization_field,
                    ft.Container(height=10),
                    self.password_field,
                    ft.Container(height=10),
                    self.error_text,
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        content=ft.Text(
                            "התחבר",
                            size=16,
                            weight=ft.FontWeight.BOLD
                        ),
                        width=300,
                        height=45,
                        on_click=self.try_login,
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE
                    ),
                    ft.Container(height=20),
                    ft.TextButton(
                        text="להרשמה לחץ כאן",
                        on_click=lambda _: self.page.launch_url("https://github.com/DARTYQO/people/blob/main/DATA/register.html")
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=30,
            bgcolor=ft.colors.WHITE,
            border_radius=10
        )

    def try_login(self, e):
        print("בודק התחברות")
        if self.validate_organization(self.organization_field.value, self.password_field.value):
            self.current_user = self.organization_field.value
            self.on_login_success()
        else:
            self.error_text.value = "שם ארגון או סיסמה שגויים"
            self.page.update()

    def validate_organization(self, org_name, password):
        try:
            if not os.path.exists(self.data_folder):
                return False
            
            org_file_path = os.path.join(self.data_folder, "organizations.json")
            if not os.path.exists(org_file_path):
                return False
            
            with open(org_file_path, 'r', encoding='utf-8') as f:
                orgs_data = json.load(f)
            
            return org_name in orgs_data and orgs_data[org_name]["password"] == password
            
        except Exception as e:
            print(f"שגיאה באימות: {str(e)}")
            return False

    def load_organization_data(self):
        if not self.current_user:
            return None
        
        try:
            # ניסיון לטעון מגיטהאב
            headers = {
                "Authorization": f"Bearer {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            file_path = f"DATA/{self.current_user}/data.json"
            url = f"https://api.github.com/repos/DARTYQO/people/contents/{file_path}"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                content = base64.b64decode(response.json()["content"]).decode('utf-8')
                data = json.loads(content)
                self.show_message("הנתונים נטענו בהצלחה מגיטהאב", ft.colors.GREEN)
                return data
                
        except Exception as e:
            print(f"שגיאה בטעינה מגיטהאב: {str(e)}")
        
        # אם הטעינה מגיטהאב נכשלה, ננסה לטעון מקומית
        try:
            local_path = os.path.join(self.data_folder, self.current_user, "data.json")
            if os.path.exists(local_path):
                with open(local_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.show_message("הנתונים נטענו מהמחשב המקומי", ft.colors.BLUE)
                return data
        except Exception as e:
            print(f"שגיאה בטעינה מקומית: {str(e)}")
        
        return None

    def save_organization_data(self, data):
        if not self.current_user:
            return False
        
        try:
            # שמירה מקומית
            org_folder = os.path.join(self.data_folder, self.current_user)
            if not os.path.exists(org_folder):
                os.makedirs(org_folder)
            
            local_path = os.path.join(org_folder, "data.json")
            json_data = json.dumps(data, ensure_ascii=False, indent=4)
            
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
            
            # שמירה לגיטהאב
            self._save_to_github(json_data)
            return True
            
        except Exception as e:
            print(f"שגיאה בשמירת הנתונים: {str(e)}")
            return False

    def _save_to_github(self, json_data):
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        file_path = f"DATA/{self.current_user}/data.json"
        url = f"https://api.github.com/repos/DARTYQO/people/contents/{file_path}"
        
        try:
            # בדיקה אם הקובץ קיים
            response = requests.get(url, headers=headers)
            sha = response.json()["sha"] if response.status_code == 200 else None
            
            # הכנת התוכן לשמירה
            content = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
            
            data = {
                "message": f"עדכון נתונים - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "content": content
            }
            
            if sha:
                data["sha"] = sha
            
            # שליחת העדכון לגיטהאב
            response = requests.put(url, headers=headers, json=data)
            
            if response.status_code in [200, 201]:
                self.show_message("הנתונים נשמרו בהצלחה בגיטהאב", ft.colors.GREEN)
            else:
                self.show_message(f"שגיאה בשמירה לגיטהאב: {response.status_code}", ft.colors.RED)
                
        except Exception as e:
            self.show_message(f"שגיאה בתקשורת עם גיטהאב: {str(e)}", ft.colors.RED)

    def show_message(self, message, color):
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=color
            )
            self.page.snack_bar.open = True
            self.page.update()

class AppManager:
    def __init__(self):
        self.contacts = []
        self.events = []
        self.groups = []
        self.current_edit_contact = None
        self.login_manager = None
        self.message_banner = None
        self.temp_notes = {}
        self.app_icon = "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"
         
        # משתני ממשק
        self.contacts_list_view = None
        self.events_grid_view = None
        self.groups_list_view = None
        self.tabs = None
        
        # שדות טפסים
        self.name_field = None
        self.phone_field = None
        self.email_field = None
        self.group_field = None
        self.search_field = None
        self.event_title = None
        self.event_date = None
        self.event_time = None
        self.event_location = None
        self.group_name_field = None
        self.group_description_field = None

    def initialize_app(self, page: ft.Page):
        self.login_manager = LoginManager()
        page.window_icon = ft.icons.PERSON 
        self.login_manager.create_login_page(page, self.setup_main_page)
        
        
        page.update()

    def setup_main_page(self):
        # הגדרת המסך הראשי
        self.login_manager.page.title = "מערכת ניהול אנשי קשר ואירועים"
        self.login_manager.page.window_width = 1200
        self.login_manager.page.window_height = 800
        self.login_manager.page.padding = 20
        self.login_manager.page.rtl = True
        self.login_manager.page.bgcolor = ft.colors.WHITE
        
        # יצירת הרכיבים
        self.create_form_fields()
        self.create_list_views()
        self.create_tabs()
        
        # טעינת נתונים
        self.load_data()
        
        # ניקוי והצגת הממשק החדש
        self.login_manager.page.clean()
        self.login_manager.page.add(
            ft.Text(
                "מערכת ניהול אנשי קשר ואירועים",
                size=30,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            self.tabs
        )
        # יצירת באנר להודעות
        self.message_banner = ft.Card(
            visible=False,
            content=ft.Container(
                bgcolor=ft.colors.WHITE,
                padding=10,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(ft.icons.INFO, size=24),
                                ft.Text("", size=16, weight=ft.FontWeight.BOLD)
                            ]
                        ),
                        ft.IconButton(
                            icon=ft.icons.CLOSE,
                            icon_size=20,
                            on_click=lambda _: self.hide_message()
                        )
                    ]
                )
            )
        )
        
        # הוספת הבאנר בתוך Container עם padding
        banner_container = ft.Container(
            content=self.message_banner,
            
            margin=ft.margin.only(bottom=10),
            padding=ft.padding.all(10)
        )
        
        # הוספת הבאנר לתחילת הדף
        self.login_manager.page.controls.insert(0, banner_container)
        self.login_manager.page.update()
        self.login_manager.page.update()

    def create_contact_card(self, contact):
        is_selected = contact == self.current_edit_contact
        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.PERSON,
                            color=ft.colors.BLUE if is_selected else ft.colors.BLACK,
                            size=30
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    contact.name,
                                    size=16,
                                    weight=ft.FontWeight.BOLD
                                ),
                                ft.Text(f"טלפון: {contact.phone}"),
                                ft.Text(f"אימייל: {contact.email}" if contact.email else ""),
                                ft.Text(f"קבוצה: {contact.group}" if contact.group else "")
                            ],
                            spacing=5,
                            expand=True
                        ),
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_color=ft.colors.BLUE,
                                    tooltip="ערוך",
                                    on_click=lambda _, c=contact: self.edit_contact(c)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.colors.RED,
                                    tooltip="מחק",
                                    on_click=lambda _, c=contact: self.delete_contact(c)
                                )
                            ],
                            spacing=0
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=10,
                bgcolor=ft.colors.BLUE_50 if is_selected else None
            )
        )

    def create_event_card(self, event):
        def delete_event(e, event_to_delete):
            self.events.remove(event_to_delete)
            self.events_grid_view.controls = [self.create_event_card(evt) for evt in self.events]
            self.save_data()
            self.show_message("האירוע נמחק בהצלחה", ft.colors.RED)
            self.login_manager.page.update()

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.EVENT, color=ft.colors.BLUE),
                        title=ft.Text(
                            event.title,
                            size=20,
                            weight=ft.FontWeight.BOLD
                        ),
                        subtitle=ft.Text(
                            f"תאריך: {event.date}\nשעה: {event.time}\nמיקום: {event.location}"
                        )
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_color=ft.colors.BLUE,
                                    tooltip="ערוך אירוע",
                                    on_click=lambda e: self.manage_event(event)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.colors.RED,
                                    tooltip="מחק אירוע",
                                    on_click=lambda e, evt=event: delete_event(e, evt)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.END
                        ),
                        padding=ft.padding.only(right=10, bottom=10)
                    )
                ]),
                padding=10,
                bgcolor=ft.colors.WHITE
            ),
            elevation=3
        )


    def create_group_card(self, group):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.GROUP, color=ft.colors.BLUE),
                        title=ft.Text(
                            group.name,
                            size=18,
                            weight=ft.FontWeight.BOLD
                        ),
                        subtitle=ft.Column([
                            ft.Text(group.description) if group.description else ft.Text("אין תיאור"),
                            ft.Text(f"מספר חברים: {len(group.members)}", weight=ft.FontWeight.BOLD),
                            ft.Text("חברי הקבוצה:", weight=ft.FontWeight.BOLD),
                            ft.Text(", ".join([member.name for member in group.members]) if group.members else "אין חברים בקבוצה")
                        ])
                    ),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "כניסה לקבוצה",
                                icon=ft.Icons.LOGIN,
                                on_click=lambda e, g=group: self.enter_group(g)
                            ),
                            ft.ElevatedButton(
                                "ערוך קבוצה",
                                icon=ft.Icons.EDIT,
                                on_click=lambda e, g=group: self.edit_group(g)
                            ),
                            ft.ElevatedButton(
                                "מחק קבוצה",
                                icon=ft.Icons.DELETE,
                                bgcolor=ft.colors.RED,
                                color=ft.colors.WHITE,
                                on_click=lambda e, g=group: self.delete_group(g)
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END
                    )
                ]),
                padding=10
            )
        )

    def create_participant_card(self, participant, status, event, participants_grid):
        is_confirmed = status == "confirmed"
        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE if is_confirmed else ft.Icons.PENDING,
                            color=ft.colors.GREEN if is_confirmed else ft.colors.ORANGE
                        ),
                        ft.Column(
                            [
                                ft.Text(participant.name, size=16, weight=ft.FontWeight.BOLD),
                                ft.Text(f"טלפון: {participant.phone}"),
                                ft.Text(f"אימייל: {participant.email}" if participant.email else ""),
                                ft.Text(
                                    "מאושר" if is_confirmed else "ממתין לאישור",
                                    color=ft.colors.GREEN if is_confirmed else ft.colors.ORANGE
                                )
                            ],
                            spacing=5,
                            expand=True
                        ),
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.CHECK,
                                    icon_color=ft.colors.GREEN,
                                    tooltip="אשר השתתפות",
                                    visible=not is_confirmed,
                                    on_click=lambda _, p=participant: self.confirm_participation(p, event, participants_grid)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.colors.RED,
                                    tooltip="הסר מהאירוע",
                                    on_click=lambda _, p=participant: self.remove_participant(p, event, participants_grid)
                                )
                            ]
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=10,
                bgcolor=ft.colors.GREEN_50 if is_confirmed else ft.colors.ORANGE_50
            )
        )        
    def update_group_options(self):
        """
        מעדכן את האפשרויות בתיבת הבחירה של הקבוצות
        """
        # יצירת רשימת אפשרויות מהקבוצות הקיימות
        group_options = [
            ft.dropdown.Option(group.name) 
            for group in self.groups
        ]
        
        # הוספת אפשרויות ברירת מחדל
        default_options = [
            ft.dropdown.Option("משפחה"),
            ft.dropdown.Option("חברים"),
            ft.dropdown.Option("עבודה"),
            ft.dropdown.Option("אחר")
        ]
        
        # הוספת האפשרויות לרשימה הכללית
        all_options = []
        all_options.extend(group_options)
        
        # הוספת אפשרויות ברירת המחדל רק אם הן לא קיימות כבר
        for option in default_options:
            if option not in all_options:
                all_options.append(option)
        
        # עדכון האפשרויות בשדה הקבוצה
        self.group_field.options = all_options
        
        # אם יש ערך נוכחי שכבר נבחר, נשמור אותו
        current_value = self.group_field.value
        if current_value and current_value not in [opt.key for opt in all_options]:
            self.group_field.value = None
            
        # עדכון התצוגה
        if self.login_manager and self.login_manager.page:
            self.login_manager.page.update()

    def edit_group(self, group):
        """
        פותח חלון לעריכת פרטי הקבוצה
        """
        def save_changes(e):
            if new_name_field.value:
                group.name = new_name_field.value
                group.description = new_description_field.value
                self.update_views()
                self.save_data()
                dlg.open = False
                self.login_manager.page.update()
                self.show_message("הקבוצה עודכנה בהצלחה", ft.colors.GREEN)

        new_name_field = ft.TextField(
            label="שם הקבוצה",
            value=group.name,
            width=300,
            text_align="right"
        )
        
        new_description_field = ft.TextField(
            label="תיאור הקבוצה",
            value=group.description,
            width=300,
            multiline=True,
            text_align="right"
        )

        dlg = ft.AlertDialog(
            title=ft.Text("עריכת קבוצה"),
            content=ft.Column([
                new_name_field,
                new_description_field
            ], tight=True),
            actions=[
                ft.TextButton("ביטול", on_click=lambda e: setattr(dlg, 'open', False)),
                ft.TextButton("שמור", on_click=save_changes)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.login_manager.page.dialog = dlg
        dlg.open = True
        self.login_manager.page.update()

    def delete_group(self, group):
        """
        מוחק קבוצה מהמערכת
        """
        def confirm_delete(e):
            self.groups.remove(group)
            # עדכון אנשי הקשר ששייכים לקבוצה
            for contact in self.contacts:
                if contact.group == group.name:
                    contact.group = None
            self.update_views()
            self.save_data()
            dlg.open = False
            self.login_manager.page.update()
            self.show_message("הקבוצה נמחקה בהצלחה", ft.colors.RED)

        dlg = ft.AlertDialog(
            title=ft.Text("מחיקת קבוצה"),
            content=ft.Text(f"האם אתה בטוח שברצונך למחוק את הקבוצה '{group.name}'?"),
            actions=[
                ft.TextButton("ביטול", on_click=lambda e: setattr(dlg, 'open', False)),
                ft.TextButton("מחק", on_click=confirm_delete)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.login_manager.page.dialog = dlg
        dlg.open = True
        self.login_manager.page.update()

    def toggle_group_member(self, e, group, contact):
        """
        מוסיף או מסיר חבר מקבוצה
        """
        if e.control.value:  # אם הצ'קבוקס נבחר
            if contact not in group.members:
                group.members.append(contact)
                contact.group = group.name
        else:  # אם הצ'קבוקס בוטל
            if contact in group.members:
                group.members.remove(contact)
                if contact.group == group.name:
                    contact.group = None
        
        self.update_views()
        self.save_data()
        
    def create_form_fields(self):
        # שדות טופס אנשי קשר
        self.name_field = ft.TextField(
            label="שם",
            width=200,
            text_align="right",
            prefix_icon=ft.Icons.PERSON
        )
        
        self.phone_field = ft.TextField(
            label="טלפון",
            width=200,
            text_align="right",
            prefix_icon=ft.Icons.PHONE
        )
        
        self.email_field = ft.TextField(
            label="אימייל",
            width=200,
            text_align="right",
            prefix_icon=ft.Icons.EMAIL
        )

        self.group_field = ft.Dropdown(
            label="קבוצה",
            width=200,
            options=[
                ft.dropdown.Option("משפחה"),
                ft.dropdown.Option("חברים"),
                ft.dropdown.Option("עבודה"),
                ft.dropdown.Option("אחר")
            ]
        )

        self.search_field = ft.TextField(
            label="חיפוש",
            width=200,
            prefix_icon=ft.Icons.SEARCH,
            on_change=lambda e: self.filter_contacts(e.control.value)
        )

        # שדות טופס אירועים
        self.event_title = ft.TextField(
            label="כותרת האירוע",
            width=200,
            text_align="right",
            prefix_icon=ft.Icons.EVENT_NOTE
        )

        self.event_date = ft.TextField(
            label="תאריך",
            hint_text="הזן תאריך",
            width=200,
            text_align="right",
            prefix_icon=ft.Icons.CALENDAR_TODAY
        )

        self.event_time = ft.TextField(
            label="שעה",
            hint_text="HH:MM",
            width=200,
            text_align="right",
            prefix_icon=ft.Icons.SCHEDULE
        )

        self.event_location = ft.TextField(
            label="מיקום",
            width=200,
            text_align="right",
            prefix_icon=ft.Icons.LOCATION_ON
        )

        # שדות טופס קבוצות
        self.group_name_field = ft.TextField(
            label="שם הקבוצה",
            width=300,
            text_align="right",
            prefix_icon=ft.Icons.GROUP
        )

        self.group_description_field = ft.TextField(
            label="תיאור הקבוצה",
            width=300,
            text_align="right",
            multiline=True,
            prefix_icon=ft.Icons.DESCRIPTION
        )
    def create_list_views(self):
        # יצירת תצוגת אנשי קשר
        self.contacts_list_view = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
            height=400
        )

        # יצירת תצוגת אירועים
        self.events_grid_view = ft.GridView(
            expand=True,
            runs_count=2,
            max_extent=400,
            child_aspect_ratio=2.0,
            spacing=10,
            run_spacing=10,
            padding=20,
            height=400
        )

        # יצירת תצוגת קבוצות
        self.groups_list_view = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
            height=400
        )

    def create_tabs(self):
        # יצירת טופס אנשי קשר
        contacts_form = self.create_contacts_form()
        events_form = self.create_events_form()
        groups_form = self.create_groups_form()

        # יצירת הכרטיסיות
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="אנשי קשר",
                    icon=ft.Icons.PEOPLE,
                    content=contacts_form
                ),
                ft.Tab(
                    text="קבוצות",
                    icon=ft.Icons.GROUPS,
                    content=groups_form
                ),
                ft.Tab(
                    text="אירועים",
                    icon=ft.Icons.EVENT,
                    content=events_form
                ),
            ],
            expand=1,
            tab_alignment=ft.TabAlignment.START
        )

    def create_contacts_form(self):

        import_excel_btn = ft.ElevatedButton(
            text="XL",
            icon=ft.icons.FILE_UPLOAD,
            on_click=self.import_contacts_from_excel
        )

        # יצירת שורת הכפתורים
        buttons_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.ElevatedButton(
                        text="+",
                        icon=ft.icons.PERSON_ADD,
                        on_click=self.add_or_update_contact,
                        bgcolor=ft.colors.BLUE,
                        color=ft.colors.WHITE
                    ),
                    padding=ft.padding.only(right=10)
                ),
                ft.Container(
                    content=import_excel_btn,
                    padding=ft.padding.only(right=10)
                )
            ]
        )

        # החזרת המבנה המלא
        return ft.Column([
            ft.Container(
                content=ft.Row(
                    controls=[
                        buttons_row,  # שורת הכפתורים
                        ft.Container(
                            content=self.name_field,
                            width=200,
                            padding=5
                        ),
                        ft.Container(
                            content=self.phone_field,
                            width=200,
                            padding=5
                        ),
                        ft.Container(
                            content=self.email_field,
                            width=200,
                            padding=5
                        ),
                        ft.Container(
                            content=self.group_field,
                            width=200,
                            padding=5
                        ),
                        ft.Container(
                            content=self.search_field,
                            padding=ft.padding.only(left=10)
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=10,
            ),
            ft.Container(
                content=self.contacts_list_view,
                expand=True,
                margin=ft.margin.all(10),
                border=ft.border.all(1, ft.colors.BLACK12),
                border_radius=10,
                padding=10
            )
        ])  

    def create_events_form(self):
        add_event_button = ft.ElevatedButton(
            text="+",
            icon=ft.Icons.EVENT_AVAILABLE,
            on_click=self.add_event,
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE
        )

        return ft.Column([
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=add_event_button,
                            padding=ft.padding.only(right=10)
                        ),
                        ft.Container(
                            content=self.event_title,
                            width=200,
                            padding=5
                        ),
                        ft.Container(
                            content=self.event_date,
                            width=200,
                            padding=5
                        ),
                        ft.Container(
                            content=self.event_time,
                            width=200,
                            padding=5
                        ),
                        ft.Container(
                            content=self.event_location,
                            width=200,
                            padding=5
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                padding=10,
            ),
            ft.Container(
                content=self.events_grid_view,
                expand=True,
                margin=ft.margin.all(10),
                border=ft.border.all(1, ft.colors.BLACK12),
                border_radius=10,
                padding=10
            )
        ])
    
    def create_groups_form(self):
        add_group_button = ft.ElevatedButton(
            text="+",
            icon=ft.Icons.GROUP_ADD,
            on_click=self.add_group,
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE
        )

        return ft.Column([
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=add_group_button,
                            padding=ft.padding.only(right=10)
                        ),
                        ft.Container(
                            content=self.group_name_field,
                            padding=5
                        ),
                        ft.Container(
                            content=self.group_description_field,
                            padding=5
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START
                ),
                padding=10
            ),
            ft.Container(
                content=self.groups_list_view,
                expand=True,
                margin=ft.margin.all(10),
                border=ft.border.all(1, ft.colors.BLACK12),
                border_radius=10,
                padding=10
            )
        ])

    # פונקציות ניהול אנשי קשר
    def add_or_update_contact(self, e):
        if not self.name_field.value:
            self.show_message("אנא הזן שם!", ft.colors.RED)
            return
        if not self.phone_field.value:
            self.show_message("אנא הזן מספר טלפון!", ft.colors.RED)
            return

        if self.current_edit_contact:
            # עדכון איש קשר קיים
            if self.current_edit_contact.group:
                old_group = next((g for g in self.groups if g.name == self.current_edit_contact.group), None)
                if old_group and self.current_edit_contact in old_group.members:
                    old_group.members.remove(self.current_edit_contact)

            self.current_edit_contact.name = self.name_field.value
            self.current_edit_contact.phone = self.phone_field.value
            self.current_edit_contact.email = self.email_field.value
            self.current_edit_contact.group = self.group_field.value
            contact = self.current_edit_contact
            self.show_message("איש הקשר עודכן בהצלחה", ft.colors.GREEN)
            self.current_edit_contact = None
        else:
            # הוספת איש קשר חדש
            contact = Contact(
                self.name_field.value,
                self.phone_field.value,
                self.email_field.value,
                self.group_field.value
            )
            self.contacts.append(contact)
            self.show_message("איש הקשר נוסף בהצלחה", ft.colors.GREEN)

        # עדכון שיוך לקבוצה
        if contact.group:
            new_group = next((g for g in self.groups if g.name == contact.group), None)
            if new_group and contact not in new_group.members:
                new_group.members.append(contact)

        self.clear_contact_fields()
        self.update_views()
        self.save_data()

    def edit_contact(self, contact):
        self.current_edit_contact = contact
        self.name_field.value = contact.name
        self.phone_field.value = contact.phone
        self.email_field.value = contact.email
        self.group_field.value = contact.group
        self.filter_contacts("")
        self.login_manager.page.update()

    def delete_contact(self, contact):
        self.contacts.remove(contact)
        self.filter_contacts("")
        self.update_participants_list()
        self.show_message("איש הקשר נמחק בהצלחה", ft.colors.RED)
        self.login_manager.page.update()

    def filter_contacts(self, search_text):
        if not search_text:
            self.contacts_list_view.controls = [self.create_contact_card(contact) for contact in self.contacts]
        else:
            filtered = [
                contact for contact in self.contacts
                if search_text.lower() in contact.name.lower() or
                   search_text in contact.phone or
                   search_text.lower() in contact.email.lower()
            ]
            self.contacts_list_view.controls = [self.create_contact_card(contact) for contact in filtered]
        self.login_manager.page.update()

    def add_event(self, e):
        if not self.event_title.value:
            self.show_message("אנא הזן כותרת לאירוע!", ft.colors.RED)
            return
        if not self.event_date.value:
            self.show_message("אנא הזן תאריך!", ft.colors.RED)
            return
        if not self.event_time.value:
            self.show_message("אנא הזן שעה!", ft.colors.RED)
            return

        # יצירת אירוע חדש עם כל המאפיינים הנדרשים
        new_event = Event(
            self.event_title.value,
            self.event_date.value,
            self.event_time.value,
            self.event_location.value if self.event_location.value else ""
        )
        
        # איתחול רשימות המשתתפים
        new_event.participants = []
        new_event.pending_participants = []
        new_event.pending_notes = {}
        
        # הוספת האירוע לרשימת האירועים
        self.events.append(new_event)
        
        # עדכון התצוגה
        self.events_grid_view.controls = [self.create_event_card(event) for event in self.events]
        
        # שמירת הנתונים
        self.save_data()
        
        # ניקוי השדות והצגת הודעה
        self.clear_event_fields()
        self.show_message("האירוע נוסף בהצלחה", ft.colors.GREEN)
        self.login_manager.page.update()

    def import_contacts_from_excel(self, e):
        """פתיחת חלון בחירת קובץ אקסל"""
        try:
            # יצירת דיאלוג בחירת קבצים
            pick_files_dialog = ft.FilePicker(
                on_result=self.process_excel_file
            )
            
            # הוספת הדיאלוג לדף
            self.login_manager.page.overlay.append(pick_files_dialog)
            self.login_manager.page.update()
            
            # פתיחת הדיאלוג
            pick_files_dialog.pick_files(
                allowed_extensions=["xlsx", "xls"]
            )
            
        except Exception as e:
            print(f"שגיאה: {str(e)}")  # הדפסה לדיבאג
            se
            lf.show_message(f"שגיאה בפתיחת חלון בחירת קובץ: {str(e)}", ft.Colors.RED)

    def process_excel_file(self, e: ft.FilePickerResultEvent):
        try:
            if not e.files or not e.files[0].path:
                print("לא נבחר קובץ")
                return

            file_path = e.files[0].path
            print(f"נבחר קובץ: {file_path}")
            
            df = pd.read_excel(file_path)
            print(f"קראתי את הקובץ. מספר שורות: {len(df)}")
            
            if df.empty:
                self.show_message("הקובץ ריק", ft.Colors.RED)
                return

            # לוקחים את העמודה הראשונה כעמודת שם
            name_column = df.columns[0]
            second_column = df.columns[1] if len(df.columns) > 1 else None
            
            # חיפוש עמודת טלפון
            phone_column = None
            for column in df.columns:
                current_values = df[column].astype(str).str.strip()
                cleaned_values = current_values.str.replace('-', '')
                valid_phones = cleaned_values.str.match(r'^0\d{8,9}$')
                if valid_phones.mean() > 0.5:
                    phone_column = column
                    break

            if not phone_column:
                self.show_message("לא נמצאה עמודת טלפון תקינה", ft.Colors.RED)
                return

            print(f"עמודת טלפון שנבחרה: {phone_column}")

            # ייבוא אנשי הקשר
            success_count = 0
            error_count = 0
            duplicates = 0

            for _, row in df.iterrows():
                # מחברים את העמודה הראשונה עם השנייה אם היא קיימת ומכילה טקסט
                name = str(row[name_column]).strip()
                
                if second_column:
                    second_value = str(row[second_column]).strip()
                    # בודקים אם העמודה השנייה מכילה טקסט (לא מספרים)
                    if second_value and not second_value.replace('-', '').isdigit():
                        name = f"{name} {second_value}"
                
                phone = str(row[phone_column]).strip().replace('-', '')

                if pd.isna(name) or pd.isna(phone):
                    error_count += 1
                    continue

                if not re.match(r'^0\d{8,9}$', phone):
                    error_count += 1
                    continue

                if any(contact.phone == phone for contact in self.contacts):
                    duplicates += 1
                    continue

                new_contact = Contact(
                    name=name,
                    phone=phone,
                    email="",
                    group=""
                )
                
                self.contacts.append(new_contact)
                success_count += 1

            # עדכון הממשק
            self.update_views()
            self.save_data()

            # הצגת סיכום
            summary = f"""ייבוא הסתיים:
            • נוספו בהצלחה: {success_count} אנשי קשר
            • נכשלו: {error_count} רשומות
            • כפילויות שנדחו: {duplicates} רשומות"""
            
            self.show_message(summary, ft.Colors.GREEN if success_count > 0 else ft.Colors.RED)

        except Exception as e:
            print(f"שגיאה בעיבוד הקובץ: {str(e)}")
            self.show_message(f"שגיאה בעיבוד הקובץ: {str(e)}", ft.Colors.RED)
        
    def manage_event(self, event):
        """מנהל את תצוגת האירוע ומשתתפיו בצורה מאורגנת ונוחה יותר"""
        if not event or not self.login_manager or not self.login_manager.page:
            return

        # וידוא שכל המשתנים קיימים
        if not hasattr(event, 'participants'):
            event.participants = []
        if not hasattr(event, 'pending_participants'):
            event.pending_participants = []
        if not hasattr(event, 'pending_notes'):
            event.pending_notes = {}

        event_tab_text = f"אירוע: {event.title}"

        # בדיקה אם הכרטיסייה כבר קיימת
        if self.tabs and self.tabs.tabs:
            for i, tab in enumerate(self.tabs.tabs):
                if tab.text == event_tab_text:
                    self.tabs.selected_index = i
                    self.login_manager.page.update()
                    return

        # יצירת שדות עריכה לאירוע
        edit_event_title = ft.TextField(
            value=event.title,
            label="כותרת האירוע",
            width=200,
            text_align="right"
        )
        
        edit_event_date = ft.TextField(
            value=event.date,
            label="תאריך",
            width=150,
            text_align="right"
        )
        
        edit_event_time = ft.TextField(
            value=event.time,
            label="שעה",
            width=100,
            text_align="right"
        )
        
        edit_event_location = ft.TextField(
            value=event.location,
            label="מיקום",
            width=150,
            text_align="right"
        )

        # יצירת שדה החיפוש
        search_field = ft.TextField(
            label="חיפוש אנשי קשר",
            prefix_icon=ft.Icons.SEARCH,
            width=300,
            border_color=ft.Colors.BLUE,
            focused_border_color=ft.Colors.BLUE,
            height=40
        )

        # יצירת רשימות משתתפים
        confirmed_participants_list = ft.ListView(
            expand=True,
            spacing=10,
            height=300,
            width=350
        )
        
        pending_participants_list = ft.ListView(
            expand=True,
            spacing=10,
            height=300,
            width=350
        )
        
        available_contacts_list = ft.ListView(
            expand=True,
            spacing=10,
            height=300,
            width=350
        )

        def save_event_changes(e):
            event.title = edit_event_title.value
            event.date = edit_event_date.value
            event.time = edit_event_time.value
            event.location = edit_event_location.value
            self.update_views()
            self.save_data()
            self.show_message("פרטי האירוע עודכנו בהצלחה", ft.Colors.GREEN)

        def update_participants_lists():
            # עדכון רשימת משתתפים מאושרים
            confirmed_participants_list.controls = [
                ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN),
                            ft.Column([
                                ft.Text(p.name, size=16, weight=ft.FontWeight.BOLD),
                                ft.Text(f"טלפון: {p.phone}")
                            ], expand=True),
                            ft.IconButton(
                                icon=ft.Icons.REMOVE_CIRCLE,
                                icon_color=ft.Colors.RED,
                                tooltip="הסר מהאירוע",
                                on_click=lambda _, participant=p: remove_participant(participant)
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=10
                    )
                )
                for p in event.participants
            ]
            #
            pending_participants_list.controls = [
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.PENDING, color=ft.Colors.ORANGE),
                                ft.Column([
                                    ft.Text(p.name, size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"טלפון: {p.phone}"),
                                    ft.Text(
                                        f"הערה: {event.pending_notes.get(p.name, '')}",
                                        color=ft.colors.GREY,
                                        italic=True,
                                        visible=bool(event.pending_notes.get(p.name, ''))
                                    )
                                ], expand=True),
                                ft.Row([
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT_NOTE,
                                        icon_color=ft.Colors.BLUE,
                                        tooltip="הוסף/ערוך הערה",
                                        data=p,
                                        # שינוי כאן - הוספת lambda עם e
                                        on_click=lambda e, participant=p: toggle_note_field(e, participant)
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.CHECK,
                                        icon_color=ft.colors.GREEN,
                                        tooltip="אשר השתתפות",
                                        on_click=lambda _, participant=p: confirm_participant(participant)
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.CANCEL,
                                        icon_color=ft.colors.RED,
                                        tooltip="דחה השתתפות",
                                        on_click=lambda _, participant=p: reject_participant(participant)
                                    )
                                ])
                            ]),
                            
                            # אזור ההערות
                            ft.Container(
                                visible=False,
                                content=ft.Column([
                                    ft.TextField(
                                        label="הערה למשתתף",
                                        value=event.pending_notes.get(p.name, ""),
                                        multiline=True,
                                        min_lines=2,
                                        max_lines=3,
                                        text_align="right",
                                        data=p,
                                        on_change=lambda e, participant=p: update_temp_note(e, participant)
                                    ),
                                    ft.Row([
                                        ft.ElevatedButton(
                                            text="שמור",
                                            icon=ft.icons.SAVE,
                                            on_click=lambda e, participant=p: save_note(e, participant)
                                        ),
                                        ft.OutlinedButton(
                                            text="בטל",
                                            icon=ft.icons.CANCEL,
                                            on_click=lambda e, participant=p: cancel_note(e, participant)
                                        )
                                    ], alignment=ft.MainAxisAlignment.END)
                                ]),
                                key=f"note_container_{p.name}",
                                padding=10
                            )
                        ]),
                        padding=10
                    )
                )
                for p in event.pending_participants
            ]
            self.login_manager.page.update()
        
        # עדכון רשימת אנשי קשר זמינים
            available_contacts = [
                c for c in self.contacts 
                if c not in event.participants and c not in event.pending_participants
            ]
            
            available_contacts_list.controls = [
                ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PERSON),
                            ft.Column([
                                ft.Text(contact.name, size=16, weight=ft.FontWeight.BOLD),
                                ft.Text(f"טלפון: {contact.phone}")
                            ], expand=True),
                            ft.IconButton(
                                icon=ft.Icons.ADD_CIRCLE,
                                icon_color=ft.Colors.BLUE,
                                tooltip="הוסף לאירוע",
                                on_click=lambda _, c=contact: add_participant(c)
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=10
                    )
                )
                for contact in available_contacts
            ]
            
            self.login_manager.page.update()



        def toggle_note_field(e, participant):
            """מחליף את מצב התצוגה של שדה ההערה"""
            for card in pending_participants_list.controls:
                note_container = next(
                    (cont for cont in card.content.content.controls 
                     if isinstance(cont, ft.Container) and 
                     hasattr(cont, 'key') and 
                     cont.key == f"note_container_{participant.name}"),
                    None
                )
                if note_container:
                    note_container.visible = not note_container.visible
                    # אם פותחים את שדה העריכה, מעתיקים את ההערה הנוכחית לזיכרון הזמני
                    if note_container.visible:
                        self.temp_notes[participant.name] = event.pending_notes.get(participant.name, "")
                    break
            self.login_manager.page.update()

        def update_temp_note(e, participant):
            """שומר את ההערה באופן זמני בזמן הקלדה"""
            self.temp_notes[participant.name] = e.control.value

        def save_note(e, participant):
            """שומר את ההערה באופן סופי"""
            if participant.name in self.temp_notes:
                note_text = self.temp_notes[participant.name]
                if note_text.strip():
                    event.pending_notes[participant.name] = note_text
                else:
                    event.pending_notes.pop(participant.name, None)
                self.temp_notes.pop(participant.name, None)
                
                # עדכון התצוגה וסגירת שדה העריכה
                update_participants_lists()
                self.save_data()

        def cancel_note(e, participant):
            """מבטל את העריכה"""
            self.temp_notes.pop(participant.name, None)
            toggle_note_field(e, participant)
    
        def confirm_participant(participant):
            """עדכון לאישור משתתף"""
            event.pending_participants.remove(participant)
            event.participants.append(participant)
            event.pending_notes.pop(participant.name, None)  # מוחק את ההערה אם קיימת
            update_participants_lists()
            self.save_data()
            self.show_message(f"אושרה השתתפותו של {participant.name}", ft.Colors.GREEN)

        def reject_participant(participant):
            """עדכון לדחיית משתתף"""
            event.pending_participants.remove(participant)
            event.pending_notes.pop(participant.name, None)  # מוחק את ההערה אם קיימת
            update_participants_lists()
            self.save_data()
            self.show_message(f"נדחתה השתתפותו של {participant.name}", ft.Colors.RED)

        def reject_participant(participant):
            """עדכון לדחיית משתתף - מוחק גם את ההערה אם קיימת"""
            event.pending_participants.remove(participant)
            # מחיקת ההערה אם קיימת
            event.pending_notes.pop(participant.name, None)
            update_participants_lists()
            self.save_data()
            self.show_message(f"נדחתה השתתפותו של {participant.name}", ft.Colors.RED)            

        def add_participant(contact):
            event.pending_participants.append(contact)
            update_participants_lists()
            self.save_data()
            self.show_message(f"{contact.name} נוסף לרשימת הממתינים", ft.Colors.BLUE)

        def confirm_participant(participant):
            event.pending_participants.remove(participant)
            event.participants.append(participant)
            update_participants_lists()
            self.save_data()
            self.show_message(f"אושרה השתתפותו של {participant.name}", ft.Colors.GREEN)

        def reject_participant(participant):
            event.pending_participants.remove(participant)
            update_participants_lists()
            self.save_data()
            self.show_message(f"נדחתה השתתפותו של {participant.name}", ft.Colors.RED)

        def remove_participant(participant):
            event.participants.remove(participant)
            update_participants_lists()
            self.save_data()
            self.show_message(f"{participant.name} הוסר מהאירוע", ft.Colors.RED)

        # פונקציית סינון אנשי קשר
        def filter_available_contacts(search_text: str):
            if not search_text:
                available_contacts = [
                    c for c in self.contacts 
                    if c not in event.participants and c not in event.pending_participants
                ]
            else:
                available_contacts = [
                    c for c in self.contacts 
                    if c not in event.participants and c not in event.pending_participants
                    and (search_text.lower() in c.name.lower() or
                         search_text in c.phone or
                         (hasattr(c, 'email') and c.email and search_text.lower() in c.email.lower()))
                ]
            
            available_contacts_list.controls = [
                ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PERSON),
                            ft.Column([
                                ft.Text(contact.name, size=16, weight=ft.FontWeight.BOLD),
                                ft.Text(f"טלפון: {contact.phone}")
                            ], expand=True),
                            ft.IconButton(
                                icon=ft.Icons.ADD_CIRCLE,
                                icon_color=ft.Colors.BLUE,
                                tooltip="הוסף לאירוע",
                                on_click=lambda _, c=contact: add_participant(c)
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=10
                    )
                )
                for contact in available_contacts
            ]
            self.login_manager.page.update()

        # הגדרת פונקציית החיפוש לשדה החיפוש
        search_field.on_change = lambda e: filter_available_contacts(e.control.value)

        # יצירת תוכן הכרטיסייה
        event_content = ft.Column([
            # כותרת וכפתור סגירה
            ft.Row([
                ft.Text("ניהול אירוע", size=30, weight=ft.FontWeight.BOLD),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color=ft.Colors.RED,
                    tooltip="סגור",
                    on_click=lambda e: self.close_event_tab(event)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            # חלק עליון - פרטי האירוע
            ft.Container(
                content=ft.Column([
                    ft.Text("פרטי האירוע", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        edit_event_title,
                        edit_event_date,
                        edit_event_time,
                        edit_event_location,
                        ft.IconButton(
                            icon=ft.Icons.SAVE,
                            icon_color=ft.Colors.BLUE,
                            tooltip="שמור שינויים",
                            on_click=save_event_changes
                        ),
                    ], spacing=10),
                ]),
                padding=20,
                border=ft.border.all(1, ft.Colors.BLACK12),
                border_radius=10,
                margin=ft.margin.only(bottom=20)
            ),
            
            # חלק תחתון - ניהול משתתפים
            ft.Container(
                content=ft.Column([
                    ft.Text("ניהול משתתפים", size=20, weight=ft.FontWeight.BOLD),
                    # שדה החיפוש
                    ft.Container(
                        content=search_field,
                        alignment=ft.alignment.center_left,
                        margin=ft.margin.only(bottom=10, left=0),
                    ),
                    ft.Row([
                        # משתתפים מאושרים
                        ft.Column([
                            ft.Container(
                                content=ft.Text("משתתפים מאושרים", weight=ft.FontWeight.BOLD),
                                bgcolor=ft.Colors.GREEN_50,
                                padding=10,
                                border_radius=5
                            ),
                            confirmed_participants_list
                        ], expand=True),
                        
                        # משתתפים ממתינים
                        ft.Column([
                            ft.Container(
                                content=ft.Text("ממתינים לאישור", weight=ft.FontWeight.BOLD),
                                bgcolor=ft.Colors.ORANGE_50,
                                padding=10,
                                border_radius=5
                            ),
                            pending_participants_list
                        ], expand=True),
                        
                        # הוספת משתתפים חדשים
                        ft.Column([
                            ft.Container(
                                content=ft.Text("הוסף משתתפים", weight=ft.FontWeight.BOLD),
                                bgcolor=ft.Colors.BLUE_50,
                                padding=10,
                                border_radius=5
                            ),
                            available_contacts_list
                        ], expand=True)
                    ], spacing=20, alignment=ft.MainAxisAlignment.START)
                ]),
                padding=20,
                border=ft.border.all(1, ft.Colors.BLACK12),
                border_radius=10,
                expand=True
            )
        ])

        # יצירת הכרטיסייה והוספתה
        new_tab = ft.Tab(
            text=event_tab_text,
            content=ft.Column(
                [
                    ft.Container(
                        content=event_content,
                        padding=20
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )
        )

        # הוספת הכרטיסייה
        self.tabs.tabs.append(new_tab)
        self.tabs.selected_index = len(self.tabs.tabs) - 1
        
        # עדכון ראשוני של הרשימות
        update_participants_lists()
        filter_available_contacts("")
        
        # עדכון הדף
        self.login_manager.page.update()
        
    def close_event_tab(self, event):
        """סוגר את כרטיסיית האירוע"""
        if self.tabs and self.tabs.tabs:
            for i, tab in enumerate(self.tabs.tabs):
                if tab.text == f"אירוע: {event.title}":
                    self.tabs.tabs.pop(i)
                    self.tabs.selected_index = 2  # חזרה ללשונית האירועים
                    self.login_manager.page.update()
                    break        
        
        def on_tab_change(e):
            update_event_participants()
            self.login_manager.page.update()



    # פונקציות ניהול קבוצות
    def add_group(self, e):
        if not self.group_name_field.value:
            self.show_message("אנא הזן שם קבוצה!", ft.colors.RED)
            return

        new_group = Group(
            self.group_name_field.value,
            self.group_description_field.value
        )
        self.groups.append(new_group)
        self.groups_list_view.controls.append(self.create_group_card(new_group))
        
        self.update_group_options()
        self.clear_group_fields()
        
        self.show_message("הקבוצה נוספה בהצלחה", ft.colors.GREEN)
        self.login_manager.page.update()
        self.save_data()

    def enter_group(self, group):
        dlg = ft.AlertDialog(
            title=ft.Text(f"קבוצה: {group.name}"),
            content=ft.Column(
                [
                    ft.Text("חברי הקבוצה:"),
                    ft.Column([
                        ft.Checkbox(
                            label=contact.name,
                            value=contact in group.members,
                            on_change=lambda e, c=contact: self.toggle_group_member(e, group, c)
                        )
                        for contact in self.contacts
                    ], scroll=ft.ScrollMode.AUTO, height=200)
                ],
                tight=True
            )
        )
        self.login_manager.page.dialog = dlg
        dlg.open = True
        self.login_manager.page.update()

    # פונקציות עזר
    def clear_contact_fields(self):
        self.name_field.value = ""
        self.phone_field.value = ""
        self.email_field.value = ""
        self.group_field.value = None

    def clear_event_fields(self):
        self.event_title.value = ""
        self.event_date.value = ""
        self.event_time.value = ""
        self.event_location.value = ""

    def clear_group_fields(self):
        self.group_name_field.value = ""
        self.group_description_field.value = ""

    def update_views(self):
        self.contacts_list_view.controls = [self.create_contact_card(contact) for contact in self.contacts]
        self.events_grid_view.controls = [self.create_event_card(event) for event in self.events]
        self.groups_list_view.controls = [self.create_group_card(group) for group in self.groups]
        self.update_group_options()
        self.login_manager.page.update()

    def show_message(self, message, color):
        """
        מציג הודעה למשתמש בתחתית המסך עם רוחב דינמי
        """
        if not self.login_manager or not self.login_manager.page:
            return

        # יצירת הודעה בתחתית המסך
        message_container = ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(
                                        ft.icons.CHECK_CIRCLE if color == ft.colors.GREEN else
                                        ft.icons.ERROR if color == ft.colors.RED else
                                        ft.icons.WARNING if color == ft.colors.ORANGE else
                                        ft.icons.INFO,
                                        color=color,
                                        size=24
                                    ),
                                    ft.Text(
                                        message,
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=color,
                                        expand=False  # מונע מהטקסט להתרחב מעבר לגודלו
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.CLOSE,
                                        icon_color=color,
                                        on_click=lambda e: self.close_message(message_container)
                                    )
                                ],
                                spacing=10,  # מרווח בין האלמנטים
                                alignment=ft.MainAxisAlignment.START,  # יישור לשמאל
                                tight=True  # גורם לשורה להיות בדיוק ברוחב התוכן שלה
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.START
                    ),
                    padding=10
                )
            ),
            bottom=30,
            left=20,
            right=None,
            padding=0
        )

        # הוספת ההודעה לדף
        self.login_manager.page.overlay.append(message_container)
        self.login_manager.page.update()

        # סגירה אוטומטית אחרי 3 שניות
        import threading
        threading.Timer(3.0, lambda: self.close_message(message_container)).start()

    def close_message(self, message_container):
        """
        סוגר את הודעת המערכת
        """
        if message_container in self.login_manager.page.overlay:
            self.login_manager.page.overlay.remove(message_container)
            self.login_manager.page.update()        

    
    def hide_message(self):
        """
        מסתיר את הודעת המערכת
        """
        if self.message_banner:
            self.message_banner.visible = False
            self.login_manager.page.update()
        
    def save_data(self):
        try:
            data = {
                "contacts": [
                    {
                        "name": contact.name,
                        "phone": contact.phone,
                        "email": contact.email,
                        "group": contact.group
                    }
                    for contact in self.contacts
                ],
                "events": [
                    {
                        "title": event.title,
                        "date": event.date,
                        "time": event.time,
                        "location": event.location,
                        "participants": [p.name for p in event.participants if p],
                        "pending_participants": [p.name for p in event.pending_participants if p],
                        "pending_notes": event.pending_notes,
                    }
                    for event in self.events
                ],
                "groups": [
                    {
                        "name": group.name,
                        "description": group.description,
                        "members": [member.name for member in group.members if member]
                    }
                    for group in self.groups
                ]
            }
            
            # שמירת הנתונים
            if self.login_manager.save_organization_data(data):
                print("הנתונים נשמרו בהצלחה")
            else:
                print("שגיאה בשמירת הנתונים")
                
        except Exception as e:
            print(f"שגיאה בשמירת הנתונים: {str(e)}")

        
    def load_data(self):
        data = self.login_manager.load_organization_data()
        if data:
            self.contacts = []
            self.events = []
            self.groups = []

            # טעינת אנשי קשר
            for contact_data in data.get("contacts", []):
                contact = Contact(**contact_data)
                self.contacts.append(contact)

            # טעינת אירועים
            for event_data in data.get("events", []):
                event = Event(
                    event_data["title"],
                    event_data["date"],
                    event_data["time"],
                    event_data["location"]
                )
                # טעינת משתתפים מאושרים
                for participant_name in event_data.get("participants", []):
                    participant = next((c for c in self.contacts if c.name == participant_name), None)
                    if participant:
                        event.participants.append(participant)
                
                # טעינת משתתפים ממתינים
                for pending_name in event_data.get("pending_participants", []):
                    pending = next((c for c in self.contacts if c.name == pending_name), None)
                    if pending:
                        event.pending_participants.append(pending)
                
                # טעינת הערות
                event.pending_notes = event_data.get("pending_notes", {})
                
                self.events.append(event)

            # טעינת קבוצות
            for group_data in data.get("groups", []):
                group = Group(group_data["name"], group_data.get("description", ""))
                for member_name in group_data.get("members", []):
                    member = next((c for c in self.contacts if c.name == member_name), None)
                    if member:
                        group.members.append(member)
                self.groups.append(group)

            self.update_views()
            return True
        return False

    def create_event_tab(self, event, update_callback, participants_grid):
        """יוצר כרטיסייה חדשה לניהול אירוע"""
        
        # יצירת רשימת אנשי קשר לבחירה
        contacts_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
            height=200
        )

        def add_participant(contact):
            if contact not in event.participants:
                event.participants.append(contact)
                update_callback()
                self.save_data()
                self.show_message(f"{contact.name} נוסף לאירוע", ft.colors.GREEN)

        # עדכון רשימת אנשי הקשר הזמינים
        for contact in self.contacts:
            if contact not in event.participants:
                contacts_list.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.PERSON),
                        title=ft.Text(contact.name),
                        subtitle=ft.Text(contact.phone),
                        trailing=ft.IconButton(
                            icon=ft.Icons.ADD,
                            tooltip="הוסף לאירוע",
                            on_click=lambda _, c=contact: add_participant(c)
                        )
                    )
                )

        return ft.Tab(
            text=f"אירוע: {event.title}",
            icon=ft.Icons.EVENT_NOTE,
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            f"פרטי האירוע: {event.title}",
                            size=24,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(f"תאריך: {event.date}"),
                        ft.Text(f"שעה: {event.time}"),
                        ft.Text(f"מיקום: {event.location}"),
                        ft.Divider(),
                        ft.Text("משתתפים:", size=20, weight=ft.FontWeight.BOLD),
                        participants_grid,
                        ft.Divider(),
                        ft.Text("הוסף משתתפים:", size=20, weight=ft.FontWeight.BOLD),
                        contacts_list
                    ]),
                    padding=20
                )
            ])
        )



            
# פונקציית main
def main(page: ft.Page):
    app = AppManager()
    app.initialize_app(page)

ft.app(
    target=main,
    assets_dir="assets"  # התיקייה שבה נמצא האייקון
)
