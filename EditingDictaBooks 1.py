1from logging import info
import sys
import ctypes
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QMainWindow, QProgressBar, QScrollArea, QGroupBox,
    QLayout, QFileDialog, QLineEdit, QMessageBox, QComboBox, QHBoxLayout, QProgressDialog,QTextBrowser,
    QCheckBox, QTextEdit, QDialog, QFrame, QSplitter, QGridLayout, QSpacerItem, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QCursor, QColor, QPalette, QTextDocument, QFont, QTextOption, QTextCursor,  QTextCharFormat, QFontDatabase
from PyQt5.QtWinExtras import QtWin 
from PyQt5.QtWidgets import QProxyStyle, QMessageBox, QTreeWidget
from PyQt5.QtCore import pyqtSignal, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRegExp
from pyluach import gematria
from bs4 import BeautifulSoup
from functools import partial
import subprocess
import re
import os
import ssl
import requests
import requests.adapters
import certifi
import shutil
import logging
from packaging import version
from ctypes import wintypes
import base64
from urllib3.util.ssl_ import create_urllib3_context
import urllib.request
import traceback
  

    


app = QApplication(sys.argv)

# הגדרת התכונה לכל החלונות העתידיים באפליקציה
app.setAttribute(Qt.AA_DisableWindowContextHelpButton)

 #  פונקצייה גלובלית לטיפול בשגיאות
 
def handle_exception(exc_type, exc_value, exc_traceback):
    """טיפול בשגיאות לא מטופלות"""
    print(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    
sys.excepthook = handle_exception

    # עידכון סטטוס גלובלי

def update_global_status(message, status_type="info"):
    """
    פונקציה גלובלית לעדכון סטטוס עם סוגי סטטוס שונים
    Global function for updating status with different status types
    """
    styles = {
        "success": "color: green; font-size: 18pt; font-family: Segoe UI;",
        "error": "color: red; font-size: 18pt; font-family: Segoe UI;",
        "warning": "color: orange; font-size: 18pt; font-family: Segoe UI;",
        "info": "color: black; font-size: 18pt; font-family: Segoe UI;"
    }
    
    for widget in QApplication.topLevelWidgets():
        if isinstance(widget, MainMenu):
            widget.status_label.setText(message)
            widget.status_label.setStyleSheet(styles.get(status_type, styles["info"]))
            widget._safe_update_history(widget.text_display.toHtml(), message)
            return True
    return False

 #עיצוב גלובלי
GLOBAL_STYLE = """
    QWidget {
        font-family: "Segoe UI", Arial;
        font-size: 20px;
    }
    QPushButton {
        font-size: 20px;
    }
    QLabel {
        font-size: 40px;
    }
    QComboBox {
        font-size: 20px;
    }
    QLineEdit {    
    }   font-size: 20px;
    QCheckBox {
        font-size: 20px;
    
"""

# מזהה ייחודי לאפליקציה
myappid = 'MIT.LEARN_PYQT.dictatootzaria'

# מחרוזת Base64 של האייקון (החלף את זה עם המחרוזת שתקבל אחרי המרת הקובץ שלך ל־Base64)
icon_base64 = "iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAGP0lEQVR4Ae2dfUgUaRjAn2r9wkzs3D4OsbhWjjKk7EuCLY9NrETJzfujQzgNBBEEIQS9/EOM5PCz68Ly44gsNOjYXVg/2NDo6o8iWg/ME7/WVtJ1XTm7BPUky9tnQLG7dnd2dnee9eb9waDs7DzPu/ObnX3nnZlnZMADpVIZLpfLUywWyzejo6MHbDZbtP3lED7LMpwjczYzNTX1q+np6R+ePn36HbAV7hMcCkhJSSnQ6/U/2v8NErE9kuM/Avbv3x8YEBDQ0N7e/j1Fg6TGJwJw5QcFBf1qNBpTqRokNT4RYN/yf2ErX1xWBSQnJxcaDIZMysZIEU6AWq3+WqPRXKVujBThBLx+/brE/ieAuC2SRHbq1Kkvurq6vqVuiFSRRUREpAHr65MhGx8fT6RuhJSRmUymA9SNkDIym832JWUD9u7diweAYD8AFC3nwsIC9PT0YOdDtJyOwF6Qy09eU1MDCoXC4fyqqip48uSJW4k3b94MN2/ehKSkJLeW8xbLy8tw//59KCwshKWlJUExXK2XsrIyePnypdMYTkdDVzhx4gQcOnTI4fzW1lY+YVbZtGkTt8yRI0fcWs6bbNiwAS5cuAAhISGQm5srKIar9dLQ0OAyBi8B3iYzM5N05a/l3Llz0NLS4vY32FuQCEhLS6NI6xCUICkBO3fupEjrkOjoaLLcJALwB9Cf2LhxI1luEgGOaGpqgvLycp/Fb2xsBJVK5bP4QvArAe/fv4f5+Xmfxf/w4YPPYgvFrwRIESaAGCaAGCaAGCaAGCaAGCaAGCaAGCaAGCaAGCaAGL8SsG/fPu5kja+IioryWWyh+JWAkydPcpOUYOcDgLY9JAIGBwedXk0gNkNDQ2S5SQTU19fDmTNnSM9ErYDnIG7fvk2Wn0TAixcvoKKiAoqKiijSr/Lx40e4fPmy9L4ByLVr12BsbAwKCgogJiZG1G8Drvj+/n6orKwEg8EgWt7PQdoL0mq13CSTySAwMFC0vIuLi35zetIvuqF4aaDQywPXO34hQMowAcQwAcQwAcQwAcSQCjh8+DAWBSHLj13g3t5esvwIqYCjR49CaWkpWX6z2SxtAQwmgBwmgBgmgBgmgBhSAXizNA4JU/Hq1Suy3CuQCnj+/Dk3SRm2CyKGCSCGCSCGCSCGCSCGVACWCNi9ezdZ/oGBAbDZbGT5EVIB2dnZpKOhWVlZcOfOHbL8CNsFEcMEEMMEEMMEEMMEEMMEEEMqYHZ2FiwWC1l+rB9KDamA2tpabpIybBdEDBNADC8Brm5mELPusz8RFhbmcQxeAt6+fet0fmxsrMcNWW8EBwfDrl27nL5nbm7OZRxeAkwmk9P5GRkZUFxcLKm7XPAzu/rmj4yMuIzDSwDe1ZiXl+dwPg4po4ArV67wCbfu2bp1K1y96vyZR1NTU/DmzRuXsXgJwDsJ8c5CZ3cy4rAy1uO/d+8en5DrFrlcDm1tbS7LHXd0dPCKx0uA1WrlLuU+f/68w/egnObmZq4kvE6n43ZbnuyS8AbqZ8+eCV5+LUqlkitX7wnh4eGQkJAAFy9ehB07djh9L5Y+uHXrFq+4vLuhuIVjlXGs/e8I/JBnz57lJk/BM1Xbt2/3OA7S2dkJoaGhXonFB71ez+22+cBbQF9fH9TV1UF+fr7ghkkBHN64dOkS7/e7dSCGpQVw696zZ4/bDZMKuPL59H5WcEsAFtbGgkqPHz+W7MGXM+7evcs9F8cd3B6KwGs58QkYDx48gC1btri7+P8W7PXk5OS4vZygsaCHDx9CXFwcVFdXQ3p6ul+UnaEC+/vYQcESPAIKP80IHozDSid4NBgfHw8lJSX4/Hmu6IZUmJiYgBs3bsD169cFP/PAfiwx7PEaw2v81Wo1bNu2jfuLNd/wR9rT3dPMzIynTVtleHiYe1yVJ+CA5OTkJBiNRq5biw/9wYNTT1AoFD1e22Sx344HH3wPQMTk4MGD1E34LJGRkY+ks8/wP2bNZnMnE0CESqX6ubu7e44JIMD+e/nHu3fvuMdFMQHi89fx48fTdTod13ViAsRl3t5TVGs0muGVF5gAkbB3g2dOnz6NK/+3ta8zASJg3+f/fuzYsQytVjv673lMgA+xb/V/JiYm/mS1Wiv1ev3fn3vPP+R95FTm9cojAAAAAElFTkSuQmCC="




# מחלקה עבור נווט כותרות
class NavigationLoader(QThread):
    """מחלקה לטעינת וניתוח כותרות ברקע"""
    finished = pyqtSignal(dict)
    log_signal = pyqtSignal(str)  # סיגנל חדש להדפסות

    def __init__(self, document):
        super().__init__()
        self.document = document

    def log(self, message):
        """פונקציית עזר להדפסה מבוקרת"""
        self.log_signal.emit(message)

    def run(self):
        result = {
            'success': False,
            'headers': [],
            'error': None
        }
        label_style = """
            QLabel {
                color: #1a365d;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                margin-bottom: 5px;
            }
        """

        
        try:
            self.log("התחלת ניתוח כותרות...")
            block = self.document.begin()
            while block.isValid():
                block_format = block.blockFormat()
                if block_format.headingLevel() > 0:
                    header_info = {
                        'level': block_format.headingLevel(),
                        'text': block.text(),
                        'position': block.position()
                    }
                    result['headers'].append(header_info)
                    self.log(f"נמצאה כותרת: {header_info['text']}")
                block = block.next()
            
            result['success'] = True
            self.log(f"נמצאו {len(result['headers'])} כותרות")
        except Exception as e:
            result['error'] = f"שגיאה בניתוח הכותרות: {str(e)}"
            self.log(f"שגיאה: {result['error']}")
        finally:
            self.finished.emit(result)
            self.log("סיום ניתוח כותרות") 


#מחלקה לגימטרייה
'''
class Gematria:
    # יצירת מופע סטטי יחיד של המחלקה
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Gematria, cls).__new__(cls)
            cls._instance._init_values()
        return cls._instance

    def _init_values(self):
        """אתחול המילונים של המרות גימטריה"""
        # מילון המרה מאותיות עבריות למספרים
        self._letter_values = {
            'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
            'י': 10, 'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80, 'צ': 90,
            'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400,
            'ך': 20, 'ם': 40, 'ן': 50, 'ף': 80, 'ץ': 90,  # סופיות
        }

        # מילון הפוך - ממספרים לאותיות (ללא אותיות סופיות)
        self._number_values = {
            1: 'א', 2: 'ב', 3: 'ג', 4: 'ד', 5: 'ה', 6: 'ו', 7: 'ז', 8: 'ח', 9: 'ט',
            10: 'י', 20: 'כ', 30: 'ל', 40: 'מ', 50: 'נ', 60: 'ס', 70: 'ע', 80: 'פ', 90: 'צ',
            100: 'ק', 200: 'ר', 300: 'ש', 400: 'ת'
        }

    @staticmethod
    def to_number(text):
        """ממיר מחרוזת בגימטריה למספר"""
        if not isinstance(text, str):
            return 0
            
        instance = Gematria()
        # ניקוי הטקסט מתווים מיוחדים
        text = text.strip().replace('"', '').replace("'", '')
        
        total = 0
        for letter in text:
            if letter in instance._letter_values:
                total += instance._letter_values[letter]
        return total

    @staticmethod
    def to_letter(number):
        """ממיר מספר לייצוג גימטרי"""
        if not isinstance(number, (int, float)) or number <= 0:
            return ''
            
        instance = Gematria()
        number = int(number)
        result = []
        remaining = number
        
        # מעבר על המספרים מהגדול לקטן
        for value in sorted(instance._number_values.keys(), reverse=True):
            while remaining >= value:
                result.append(instance._number_values[value])
                remaining -= value
                
        return ''.join(result)

# יצירת מופע גלובלי של המחלקה כדי שהקוד הקיים ימשיך לעבוד
gematria = Gematria()     
'''
# עד כאן

# ==========================================
# Script 1: יצירת כותרות לאוצריא
# ==========================================

class CreateHeadersOtZria(QWidget):
    changes_made = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = ""
        self.setWindowTitle("יצירת כותרות לאוצריא")
        self.setWindowIcon(self.load_icon_from_base64(icon_base64))
        #self.setGeometry(100, 100, 500, 450)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFixedWidth(800)

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        
        self.init_ui()

        if parent:
            parent_center = parent.mapToGlobal(parent.rect().center())
            self.move(parent_center.x() - self.width() // 2,
                     parent_center.y() - self.height() // 2)        

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        explanation = QLabel(
            "שים לב!\n\n"
            "בתיבת 'מילה לחפש' יש לבחור או להקליד את המילה בה אנו רוצים שתתחיל הכותרת.\n"
            "לדוג': פרק/פסוק/סימן/סעיף/הלכה/שאלה/עמוד/סק\n\n"
            "אין להקליד רווח אחרי המילה, וכן אין להקליד את התו גרש (') או גרשיים (\"), "
            "וכן אין להקליד יותר ממילה אחת"
        )
        explanation.setStyleSheet("""
            QLabel {
                color: #8B0000;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                padding: 20px;
                background-color: #FFE4E1;
                border: 2px solid #CD5C5C;
                border-radius: 15px;
                font-weight: bold;
            }
        """)
        explanation.setAlignment(Qt.AlignCenter)
        explanation.setWordWrap(True)
        layout.addWidget(explanation)


        label_style = """
            QLabel {
                color: #1a365d;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                margin-bottom: 5px;
            }
        """

        combo_style = """
            QComboBox {
                border: 2px solid #2b4c7e;
                border-radius: 15px;
                padding: 5px 15px;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                min-height: 30px;
                max-height: 30px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2b4c7e;
                margin-right: 5px;
            }
        """

        # מילה לחיפוש
        search_container = QVBoxLayout()
        search_label = QLabel("מילה לחפש:")
        search_label.setStyleSheet(label_style)
        
        self.level_var = QComboBox()
        self.level_var.setStyleSheet(combo_style)
        self.level_var.setFixedWidth(150)
        search_choices = ["דף", "עמוד", "פרק", "פסוק", "שאלה", "סימן", "סעיף", "הלכה", "הלכות", "סק"]
        self.level_var.addItems(search_choices)
        self.level_var.setEditable(True)
        
        search_container.addWidget(search_label, alignment=Qt.AlignCenter)
        search_container.addWidget(self.level_var, alignment=Qt.AlignCenter)
        layout.addLayout(search_container)

        # מספר סימן מקסימלי
        end_container = QVBoxLayout()
        end_label = QLabel("מספר סימן מקסימלי:")
        end_label.setStyleSheet(label_style)
        
        self.end_var = QComboBox()
        self.end_var.setStyleSheet(combo_style)
        self.end_var.setFixedWidth(100)
        self.end_var.addItems([str(i) for i in range(1, 1000)])
        self.end_var.setCurrentText("999")
        
        end_container.addWidget(end_label, alignment=Qt.AlignCenter)
        end_container.addWidget(self.end_var, alignment=Qt.AlignCenter)
        layout.addLayout(end_container)

        # רמת כותרת
        heading_container = QVBoxLayout()
        heading_label = QLabel("רמת כותרת:")
        heading_label.setStyleSheet(label_style)
        
        self.heading_level_var = QComboBox()
        self.heading_level_var.setStyleSheet(combo_style)
        self.heading_level_var.setFixedWidth(100)
        self.heading_level_var.addItems([str(i) for i in range(2, 7)])
        self.heading_level_var.setCurrentText("2")
        
        heading_container.addWidget(heading_label, alignment=Qt.AlignCenter)
        heading_container.addWidget(self.heading_level_var, alignment=Qt.AlignCenter)
        layout.addLayout(heading_container)

        # כפתור הפעלה
        button_container = QHBoxLayout()
        run_button = QPushButton("הפעל")
        run_button.clicked.connect(self.run_script)
        run_button.setStyleSheet("""
            QPushButton {
                border-radius: 15px;
                padding: 5px;
                background-color: #eaeaea;
                color: black;
                font-weight: bold;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                min-height: 30px;
                max-height: 30px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #b7b5b5;
            }
            QPushButton:pressed {
                background-color: #a0a0a0;
            }
        """)
        button_container.addStretch(1)
        button_container.addWidget(run_button)
        button_container.addStretch(1)
        layout.addLayout(button_container)


        layout.addStretch()

        self.setLayout(layout)

    def set_file_path(self, path):
        """מקבלת את נתיב הקובץ מהחלון הראשי"""
        self.file_path = path

    def show_custom_message(self, title, message_parts, window_size=("560x330")):
        msg = QMessageBox(self)
        msg.setStyleSheet(GLOBAL_STYLE)  
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Information)

        full_message = ""
        for part in message_parts:
            if len(part) == 3 and part[2] == "bold":
                full_message += f"<b><span style='font-size:{part[1]}pt'>{part[0]}</span></b><br>"
            else:
                full_message += f"<span style='font-size:{part[1]}pt'>{part[0]}</span><br>"

        msg.setTextFormat(Qt.RichText)
        msg.setText(full_message)
        msg.exec_()

    def ot(self, text, end):
        remove = ["<b>", "</b>", "<big>", "</big>", ":", '"', ",", ";", "[", "]", "(", ")", "'", ".", "״", "‚", "”", "’"]
        aa = ["ק", "ר", "ש", "ת", "תק", "תר", "תש", "תת", "תתק", "יה", "יו", "קיה", "קיו", "ריה", "ריו", "שיה", "שיו", "תיה", "תיו", "תקיה", "תקיו", "תריה", "תריו", "תשיה", "תשיו", "תתיה", "תתיו", "תתקיה", "תתקיו"]
        bb = ["ם", "ן", "ץ", "ף", "ך"]
        cc = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "ששי", "שביעי", "שמיני", "תשיעי", "עשירי", "יוד", "למד", "נון", "דש", "חי", "טל", "שדמ", "ער", "שדם", "תשדם", "תשדמ", "ערב", "ערה", "עדר", "רחצ"]
        append_list = []
        for i in aa:
            for ot_sofit in bb:
                append_list.append(i + ot_sofit)

        for tage in remove:
            text = text.replace(tage, "")
        withaute_gershayim = [gematria.to_letter(i) for i in range(1, end)] + bb + cc + append_list
        return text in withaute_gershayim

    def strip_html_tags(self, text):
        html_tags = ["<b>", "</b>", "<big>", "</big>", ":", '"', ",", ";", "[", "]", "(", ")", "'", "״", ".", "‚", "”", "’"]
        for tag in html_tags:
            text = text.replace(tag, "")
        return text

    def main(self, book_file, finde, end, level_num):
        found = False
        count_headings = 0
        finde_cleaned = self.strip_html_tags(finde).strip()
        
        with open(book_file, "r", encoding="utf-8") as file_input:
            content = file_input.read().splitlines()
            all_lines = content[0:2]
            
            for line in content[2:]:
                words = line.split()
                try:
                    if self.strip_html_tags(words[0]) == finde and self.ot(words[1], end):
                        found = True
                        count_headings += 1
                        heading_line = f"<h{level_num}>{self.strip_html_tags(words[0])} {self.strip_html_tags(words[1])}</h{level_num}>"
                        all_lines.append(heading_line)
                        if words[2:]:
                            fix_2 = " ".join(words[2:])
                            all_lines.append(fix_2)
                    else:
                        all_lines.append(line)
                except IndexError:
                    all_lines.append(line)
                    
        join_lines = "\n".join(all_lines)
        with open(book_file, "w", encoding="utf-8") as autpoot:
            autpoot.write(join_lines)

        return found, count_headings
    
    def run_script(self):
        try:
            if not self.file_path:
                self.show_custom_message(
                    "שגיאה",
                    [("לא נבחר קובץ", 12)],
                    "250x80"
                )
                return

            finde = self.level_var.currentText()
            
            try:
                end = int(self.end_var.currentText())
                level_num = int(self.heading_level_var.currentText())
            except ValueError:
                self.show_custom_message(
                    "קלט לא תקין",
                    [("אנא הזן 'מספר סימן מקסימלי' ו'רמת כותרת' תקינים", 12)],
                    "250x150"
                )
                return

            if not finde:
                self.show_custom_message(
                    "קלט לא תקין",
                    [("אנא מלא את כל השדות", 12)],
                    "250x80"
                )
                return

            # הפעלת הפונקציה הראשית
            found, count_headings = self.main(self.file_path, finde, end + 1, level_num)

            # אם נבחרה המילה "דף" והיו שינויים, הפעל את סקריפט 3
            if finde == "דף" and found and count_headings > 0:
                add_page_number = AddPageNumberToHeading()
                add_page_number.set_file_path(self.file_path)
                add_page_number.process_file(self.file_path, "נקודה ונקודותיים")
                
                detailed_message = [
                    ("<div style='text-align: center;'>התוכנה רצה בהצלחה!</div>", 12),
                    (f"<div style='text-align: center;'>נוצרו {count_headings} כותרות והוספו מספרי עמודים</div>", 15, "bold"),
                    ("<div style='text-align: center;'>כעת פתח את הספר בתוכנת 'אוצריא', והשינויים ישתקפו ב'ניווט' שבתפריט הצידי.</div>", 11)
                ]
            elif found and count_headings > 0:
                detailed_message = [
                    ("<div style='text-align: center;'>התוכנה רצה בהצלחה!</div>", 12),
                    (f"<div style='text-align: center;'>נוצרו {count_headings} כותרות</div>", 15, "bold"),
                    ("<div style='text-align: center;'>כעת פתח את הספר בתוכנת 'אוצריא', והשינויים ישתקפו ב'ניווט' שבתפריט הצידי.</div>", 11)
                ]
                
            if found and count_headings > 0:
                self.show_custom_message("!מזל טוב", detailed_message, "560x310")
                update_global_status(f"נוצרו {count_headings} כותרות")  
                self.changes_made.emit()
            else:
                
                self.show_custom_message("!שים לב", [("לא נמצא מה להחליף", 12)], "250x80")

        except Exception as e:
            self.show_custom_message("שגיאה", [("אירעה שגיאה: " + str(e), 12)], "250x150")

    def load_icon_from_base64(self, base64_string):
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(base64_string))
        return QIcon(pixmap)
   
# ==========================================
# Script 2: יצירת כותרות לאותיות בודדות
# ==========================================

class CreateSingleLetterHeaders(QWidget):
    changes_made = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.file_path = ""
        self.setWindowTitle("יצירת כותרות לאותיות בודדות")
        self.setWindowIcon(self.load_icon_from_base64(icon_base64))
        #self.setGeometry(100, 100, 500, 600)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFixedWidth(600)

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        explanation = QLabel(
            "שים לב!\n\n"
            "הבחירה בברירת מחדל [השורה הריקה], משמעותה סימון כל האפשרויות."
        )
        explanation.setStyleSheet("""
            QLabel {
                color: #8B0000;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                padding: 20px;
                background-color: #FFE4E1;
                border: 2px solid #CD5C5C;
                border-radius: 15px;
                font-weight: bold;
            }
        """)
        explanation.setAlignment(Qt.AlignCenter)
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        label_style = """
            QLabel {
                color: #1a365d;
                font-family: "Segoe UI", Arial;
                font-size: 14px;
                margin-bottom: 5px;
            }
        """

        combo_style = """
            QComboBox {
                border: 2px solid #2b4c7e;
                border-radius: 15px;
                padding: 5px 15px;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                min-height: 30px;
                max-height: 30px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2b4c7e;
                margin-right: 5px;
            }
        """

        entry_style = """
            QLineEdit {
                border: 2px solid #2b4c7e;
                border-radius: 15px;
                padding: 5px 15px;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                min-height: 30px;
                background-color: white;
            }
        """

        # תו בתחילת וסוף האות + רמת כותרת באותה שורה
        chars_container = QHBoxLayout()

        start_container = QVBoxLayout()
        start_label = QLabel("תו בתחילת האות:")
        start_label.setStyleSheet(label_style)
        self.start_var = QComboBox()
        self.start_var.addItems(["", "(", "["])
        self.start_var.setStyleSheet(combo_style)
        self.start_var.setFixedWidth(100)
        start_container.addWidget(start_label, alignment=Qt.AlignCenter)
        start_container.addWidget(self.start_var, alignment=Qt.AlignCenter)
        

        end_container = QVBoxLayout()
        end_label = QLabel("תו/ים בסוף האות:")
        end_label.setStyleSheet(label_style)
        self.finde_var = QComboBox()
        self.finde_var.addItems(['', '.', ',', "'", "',", "'.", ']', ')', "']", "')", "].", ").", "],", "),", "'),", "').", "'],", "']."])
        self.finde_var.setStyleSheet(combo_style)
        self.finde_var.setFixedWidth(100)
        end_container.addWidget(end_label, alignment=Qt.AlignCenter)
        end_container.addWidget(self.finde_var, alignment=Qt.AlignCenter)
        

        heading_container = QVBoxLayout()
        heading_label = QLabel("רמת כותרת:")
        heading_label.setStyleSheet(label_style)
        self.level_var = QComboBox()
        self.level_var.setStyleSheet(combo_style)
        self.level_var.setFixedWidth(100)
        self.level_var.addItems([str(i) for i in range(2, 7)])
        self.level_var.setCurrentText("3")
        heading_container.addWidget(heading_label, alignment=Qt.AlignCenter)
        heading_container.addWidget(self.level_var, alignment=Qt.AlignCenter)


        chars_container.addStretch(1)
        chars_container.addLayout(start_container)
        chars_container.addStretch(1)
        chars_container.addLayout(end_container)
        chars_container.addStretch(1)
        chars_container.addLayout(heading_container)
        chars_container.addStretch(1)
        
        layout.addLayout(chars_container)

        # תיבת סימון לחיפוש עם תווי הדגשה
        self.bold_var = QCheckBox("לחפש עם תווי הדגשה בלבד")
        self.bold_var.setStyleSheet("""
            QCheckBox {
                color: #1a365d;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        self.bold_var.setChecked(True)
        layout.addWidget(self.bold_var, alignment=Qt.AlignCenter)

        # התעלם מהתווים
        ignore_container = QVBoxLayout()
        ignore_label = QLabel("התעלם מהתווים הבאים:")
        ignore_label.setStyleSheet(label_style)
        
        self.ignore_entry = QLineEdit()
        self.ignore_entry.setStyleSheet(entry_style)
        self.ignore_entry.setText('<big> </big> " ')
        
        ignore_container.addWidget(ignore_label, alignment=Qt.AlignCenter)
        ignore_container.addWidget(self.ignore_entry)
        layout.addLayout(ignore_container)

        # הסרת תווים
        remove_container = QVBoxLayout()
        remove_label = QLabel("הסר את התווים הבאים:")
        remove_label.setStyleSheet(label_style)
        
        self.remove_entry = QLineEdit()
        self.remove_entry.setStyleSheet(entry_style)
        self.remove_entry.setText('<b> </b> <big> </big> , : " \' . ( ) [ ] { }')
        
        remove_container.addWidget(remove_label, alignment=Qt.AlignCenter)
        remove_container.addWidget(self.remove_entry)
        layout.addLayout(remove_container)

        # מספר סימן מקסימלי
        end_container = QVBoxLayout()
        end_label = QLabel("מספר סימן מקסימלי:")
        end_label.setStyleSheet(label_style)
        
        self.end_var = QComboBox()
        self.end_var.setStyleSheet(combo_style)
        self.end_var.setFixedWidth(100)
        self.end_var.addItems([str(i) for i in range(1, 1000)])
        self.end_var.setCurrentText("999")
        
        end_container.addWidget(end_label, alignment=Qt.AlignCenter)
        end_container.addWidget(self.end_var, alignment=Qt.AlignCenter)
        layout.addLayout(end_container)

        # כפתור הפעלה
        button_container = QHBoxLayout()
        run_button = QPushButton("הפעל")
        run_button.clicked.connect(self.run_script)
        run_button.setStyleSheet("""
            QPushButton {
                border-radius: 15px;
                padding: 5px;
                background-color: #eaeaea;
                color: black;
                font-weight: bold;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                min-height: 30px;
                max-height: 30px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #b7b5b5;
            }
            QPushButton:pressed {
                background-color: #a0a0a0;
            }
        """)
        button_container.addStretch(1)
        button_container.addWidget(run_button)
        button_container.addStretch(1)
        layout.addLayout(button_container)

        # מרווח גמיש בתחתית
        layout.addStretch()

        self.setLayout(layout)


        
    def set_file_path(self, file_path):
        """מקבלת את נתיב הקובץ מהחלון הראשי"""
        if not file_path or not os.path.isfile(file_path):
            QMessageBox.critical(self, "שגיאה", "נתיב קובץ לא תקין")
            return False
        
        if not file_path.lower().endswith('.txt'):
            QMessageBox.critical(self, "שגיאה", "יש לבחור קובץ טקסט (txt) בלבד")
            return False
        
        self.file_path = file_path
        return True

    def run_script(self):
        if not self.set_file_path:
            self.show_error_message("שגיאה", "אנא בחר קובץ תחילה")
            return
        
        finde = self.finde_var.currentText()
        remove = ["<b>", "</b>"] + self.remove_entry.text().split()
        ignore = self.ignore_entry.text().split()
        start = self.start_var.currentText()
        is_bold_checked = self.bold_var.isChecked()

        if is_bold_checked:
            finde += "</b>"
            start = "<b>" + start
        else:
            ignore += ["<b>", "</b>"]

        try:
            end = int(self.end_var.currentText())
            level_num = int(self.level_var.currentText())
        except ValueError:
            QMessageBox.critical(self, "קלט לא תקין", "אנא הזן 'מספר סימן מקסימלי' ו'רמת כותרת' תקינים")
            return

        try:
            self.main(self.file_path, finde, end + 1, level_num, ignore, start, remove)
            QMessageBox.information(self, "!מזל טוב", "התוכנה רצה בהצלחה!")
            update_global_status("כותרות לאותיות בודדות")
            self.changes_made.emit() 
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"אירעה שגיאה: {str(e)}")

    def ot(self, text, end):
        remove = ["<b>", "</b>", "<big>", "</big>", ":", '"', ",", ";", "[", "]", "(", ")", "'", ".", "״", "‚", "”", "’"]
        aa = ["ק", "ר", "ש", "ת", "תק", "תר", "תש", "תת", "תתק", "יו", "קיה", "קיו"]
        bb = ["ם", "ן", "ץ", "ף", "ך"]
        cc = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "ששי", "שביעי", "שמיני", "תשיעי", "עשירי", "חי", "יוד", "למד", "נון", "טל", "דש", "שדמ", "ער", "שדם", "תשדם", "תשדמ", "ערה", "ערב", "עדר", "רחצ"]
        append_list = []
        for i in aa:
            for ot_sofit in bb:
                append_list.append(i + ot_sofit)

        for tage in remove:
            text = text.replace(tage, "")
        withaute_gershayim = [gematria.to_letter(i) for i in range(1, end)] + bb + cc + append_list
        return text in withaute_gershayim

    def strip_html_tags(self, text, ignore=None):
        if ignore is None:
            ignore = []
        for tag in ignore:
            text = text.replace(tag, "")
        return text

    def main(self, book_file, finde, end, level_num, ignore, start, remove):
        with open(book_file, "r", encoding="utf-8") as file_input:
            content = file_input.read().splitlines()
            all_lines = content[0:1]
            for line in content[1:]:
                words = line.split()
                try:
                    if self.strip_html_tags(words[0], ignore).endswith(finde) and self.ot(words[0], end) and self.strip_html_tags(words[0], ignore).startswith(start):
                        heading_line = f"<h{level_num}>{self.strip_html_tags(words[0], remove)}</h{level_num}>"
                        all_lines.append(heading_line)
                        if words[1:]:
                            fix_2 = " ".join(words[1:])
                            all_lines.append(fix_2)
                    else:
                        all_lines.append(line)
                except IndexError:
                    all_lines.append(line)
        join_lines = "\n".join(all_lines)
        with open(book_file, "w", encoding="utf-8") as autpoot:
            autpoot.write(join_lines)

    # פונקציה לטעינת אייקון ממחרוזת Base64
    def load_icon_from_base64(self, base64_string):
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(base64_string))
        return QIcon(pixmap)
   

# ==========================================
# Script 3: הוספת מספר עמוד בכותרת הדף משומש על ידי סריפט 1
# ==========================================
class AddPageNumberToHeading(QWidget):
    changes_made = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.file_path = ""
        self.setWindowTitle("הוספת מספר עמוד בכותרת הדף")
        self.setWindowIcon(self.load_icon_from_base64(icon_base64))
        self.setGeometry(100, 100, 600, 500)  
        self.setLayoutDirection(Qt.RightToLeft)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20) 

        # הסבר למשתמש
        explanation = QLabel(
            "התוכנה מחליפה בקובץ בכל מקום שיש כותרת 'דף' ובתחילת שורה הבאה כתוב: ע\"א או ע\"ב, כגון:\n\n"
            "<h2>דף ב</h2>\n"
            "ע\"א [טקסט כלשהו]\n\n"
            "הפעלת התוכנה תעדכן את הכותרת ל:\n\n"
            "<h2>דף ב.</h2>\n"
            "[טקסט כלשהו]\n"
        )
        explanation.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px solid black;
                border-radius: 15px;
                padding: 20px;
                font-family: "David CLM", Arial;
                font-size: 14px;
            }
        """)
        explanation.setAlignment(Qt.AlignCenter)
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        # מרווח קטן
        layout.addSpacing(15)

        # תיבת בחירה
        self.replace_option = QComboBox()
        self.replace_option.addItems(["נקודה ונקודותיים", "ע\"א וע\"ב"])
        self.replace_option.setStyleSheet("""
            QComboBox {
                border: 2px solid black;
                border-radius: 15px;
                padding: 5px;
                font-family: "Segoe UI", Arial;
                font-size: 12px;
                min-height: 30px;
            }
        """)
        self.replace_option.setFixedWidth(200)
        
        # מיכל למרכוז תיבת הבחירה
        combo_container = QHBoxLayout()
        combo_container.addStretch()
        combo_container.addWidget(self.replace_option)
        combo_container.addStretch()
        layout.addLayout(combo_container)

        # מרווח קטן
        layout.addSpacing(15)

        # כפתור הפעלה
        run_button = QPushButton("בצע החלפה")
        run_button.clicked.connect(self.run_script)
        run_button.setStyleSheet("""
            QPushButton {
                background-color: #eaeaea;
                border-radius: 15px;
                padding: 5px;
                font-family: "Segoe UI", Arial;
                font-weight: bold;
                font-size: 12px;
                min-height: 30px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        
        # מיכל למרכוז הכפתור
        button_container = QHBoxLayout()
        button_container.addStretch()
        button_container.addWidget(run_button)
        button_container.addStretch()
        layout.addLayout(button_container)

        # מרווח גמיש בסוף
        layout.addStretch()

        self.setLayout(layout)



    def set_file_path(self, path):
        self.file_path = path

    def process_file(self, filename, replace_with):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.readlines()
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בפתיחת הקובץ: {str(e)}")
            return

        changes_made = False
        updated_content = []
        i = 0

        while i < len(content):
            line = content[i]
            match = re.match(r'<h([2-9])>(דף \S+)</h\1>', line)
            
            if match and i + 1 < len(content):
                level = match.group(1)
                title = match.group(2)
                next_line = content[i + 1].strip()
                
                if re.match(r'ע["\']א|ע["\']ב', next_line):
                    changes_made = True
                    if replace_with == "נקודה ונקודותיים":
                        suffix = "." if "א" in next_line else ":"
                    else:
                        suffix = " ע\"א" if "א" in next_line else " ע\"ב"
                    
                    updated_line = f"<h{level}>{title}{suffix}</h{level}>\n"
                    updated_content.append(updated_line)
                    
                    remaining_text = re.sub(r'^ע["\']א|ע["\']ב\s*', '', next_line)
                    if remaining_text:
                        updated_content.append(remaining_text + "\n")
                    i += 2
                    continue
            
            updated_content.append(line)
            i += 1

        if changes_made:
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.writelines(updated_content)
                self.changes_made.emit()
                QMessageBox.information(self, "הצלחה", "ההחלפות בוצעו בהצלחה!")
            except Exception as e:
                QMessageBox.critical(self, "שגיאה", f"שגיאה בשמירת הקובץ: {str(e)}")
        else:
            QMessageBox.information(self, "מידע", "לא נמצאו החלפות לביצוע")

    def run_script(self):
        if not self.file_path:
            QMessageBox.warning(self, "שגיאה", "נא לבחור קובץ תחילה")
            return
        
        replace_with = self.replace_option.currentText()
        self.process_file(self.file_path, replace_with)

    def load_icon_from_base64(self, base64_string):
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(base64_string))
        return QIcon(pixmap)
   
# ==========================================
# Script 3: שינוי רמת כותרת(4 לשעבר)
# ==========================================
class ChangeHeadingLevel(QWidget):
    changes_made = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.file_path = ""
        self.setWindowTitle("שינוי רמת כותרת")
        self.setWindowIcon(self.load_icon_from_base64(icon_base64))
        #self.setGeometry(100, 100, 500, 400)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFixedWidth(600)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        explanation = QLabel(
            "שים לב!\n"
            "הכותרות יוחלפו מרמה נוכחית לרמה החדשה.\n"
            "למשל: מ-H2 ל-H3"
        )
        explanation.setStyleSheet("""
            QLabel {
                color: #8B0000;  /* צבע טקסט אדום כהה */
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                padding: 20px;
                background-color: #FFE4E1;  /* רקע אדום בהיר */
                border: 2px solid #CD5C5C;  /* מסגרת אדומה */
                border-radius: 15px;
                font-weight: bold;
            }
        """)
        explanation.setAlignment(Qt.AlignCenter)
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        label_style = """
            QLabel {
                color: #1a365d;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                margin-bottom: 5px;
            }
        """

        combo_style = """
            QComboBox {
                border: 2px solid #2b4c7e;
                border-radius: 15px;
                padding: 5px 15px;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                min-height: 30px;
                max-height: 30px;
                min-width: 70px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2b4c7e;
                margin-right: 5px;
            }
        """

 
        current_level_container = QVBoxLayout()
        current_level_label = QLabel("רמת כותרת נוכחית:")
        current_level_label.setStyleSheet(label_style)
        
        self.current_level_var = QComboBox()
        self.current_level_var.addItems([str(i) for i in range(1, 10)])
        self.current_level_var.setCurrentText("2")
        self.current_level_var.setStyleSheet(combo_style)
        
        current_level_container.addWidget(current_level_label, alignment=Qt.AlignCenter)
        current_level_container.addWidget(self.current_level_var, alignment=Qt.AlignCenter)
        layout.addLayout(current_level_container)


        new_level_container = QVBoxLayout()
        new_level_label = QLabel("רמת כותרת חדשה:")
        new_level_label.setStyleSheet(label_style)
        
        self.new_level_var = QComboBox()
        self.new_level_var.addItems([str(i) for i in range(1, 10)])
        self.new_level_var.setCurrentText("3")
        self.new_level_var.setStyleSheet(combo_style)
        
        new_level_container.addWidget(new_level_label, alignment=Qt.AlignCenter)
        new_level_container.addWidget(self.new_level_var, alignment=Qt.AlignCenter)
        layout.addLayout(new_level_container)

        # כפתור הפעלה
        button_container = QHBoxLayout()
        run_button = QPushButton("שנה רמת כותרת")
        run_button.clicked.connect(self.run_script)
        run_button.setStyleSheet("""
            QPushButton {
                border-radius: 15px;
                padding: 5px;
                background-color: #eaeaea;
                color: black;
                font-weight: bold;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                min-height: 30px;
                max-height: 30px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #b7b5b5;
            }
            QPushButton:pressed {
                background-color: #a0a0a0;
            }
        """)
        button_container.addStretch(1)
        button_container.addWidget(run_button)
        button_container.addStretch(1)
        layout.addLayout(button_container)


        layout.addStretch()

        self.setLayout(layout)

    def set_file_path(self, file_path):
        """מקבלת את נתיב הקובץ מהחלון הראשי"""
        if not file_path or not os.path.isfile(file_path):
            QMessageBox.critical(self, "שגיאה", "נתיב קובץ לא תקין")
            return False
        
        if not file_path.lower().endswith('.txt'):
            QMessageBox.critical(self, "שגיאה", "יש לבחור קובץ טקסט (txt) בלבד")
            return False
        
        self.file_path = file_path
        return True

    def run_script(self):
        if not self.file_path:
            QMessageBox.warning(self, "שגיאה", "נא לבחור קובץ תחילה")
            return

        current_level = self.current_level_var.currentText()
        new_level = self.new_level_var.currentText()

        try:
            changes_count = self.change_heading_level_func(
                self.file_path, 
                int(current_level), 
                int(new_level)
            )
            
            if changes_count > 0:
                QMessageBox.information(
                    self, 
                    "!מזל טוב", 
                    f"בוצעו {changes_count} החלפות בהצלחה!"
                )
                update_global_status("שינוי רמת כותרות")
                self.changes_made.emit() 
            else:
                QMessageBox.information(
                    self, 
                    "!שים לב", 
                    "לא נמצאו כותרות להחלפה"
                )
        except Exception as e:
            QMessageBox.critical(
                self, 
                "שגיאה", 
                f"אירעה שגיאה: {str(e)}"
            )

    def change_heading_level_func(self, file_path, current_level, new_level):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # יצירת דפוס חיפוש דינמי
            current_tag = f"h{current_level}"
            new_tag = f"h{new_level}"
            
            # ביטוי רגולרי להחלפת תגי כותרות
            pattern = re.compile(
                rf'<{current_tag}>(.*?)</{current_tag}>', 
                re.DOTALL | re.IGNORECASE
            )
            
            # ביצוע ההחלפה
            updated_content, changes_count = pattern.subn(
                lambda match: f'<{new_tag}>{match.group(1)}</{new_tag}>', 
                content
            )

            # אם בוצעו שינויים, שמירת הקובץ
            if changes_count > 0:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(updated_content)

            return changes_count

        except FileNotFoundError:
            QMessageBox.critical(self, "שגיאה", "הקובץ לא נמצא")
            return 0
        except UnicodeDecodeError:
            QMessageBox.critical(self, "שגיאה", "קידוד הקובץ אינו נתמך. יש להשתמש בקידוד UTF-8.")
            return 0
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בעיבוד הקובץ: {str(e)}")
            return 0

    def load_icon_from_base64(self, base64_string):
        """טעינת אייקון ממחרוזת Base64"""
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(base64_string))
        return QIcon(pixmap)
# ==========================================
# Script 4: הדגשת מילה ראשונה וניקוד בסוף קטע (5 לשעבר)
# ==========================================
class EmphasizeAndPunctuate(QWidget):
    changes_made = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.file_path = ""
        self.setWindowTitle("הדגשה וניקוד")
        self.setWindowIcon(self.load_icon_from_base64(icon_base64))
        #self.setGeometry(100, 100, 500, 400)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFixedWidth(600)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)


        explanation = QLabel(
            "הסבר:\n\n"
            "• הדגשת תחילת קטעים: מדגיש את המילה הראשונה בקטעים\n"
            "• הוספת סימן סוף: מוסיף נקודה או נקודותיים בסוף קטעים ארוכים"
        )
        explanation.setStyleSheet("""
            QLabel {
                color: #1e4620;  /* ירוק כהה לטקסט */
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                padding: 20px;
                background-color: #e8f5e9;  /* ירוק בהיר לרקע */
                border: 2px solid #81c784;  /* ירוק בינוני למסגרת */
                border-radius: 15px;
                font-weight: bold;
            }
        """)
        explanation.setAlignment(Qt.AlignCenter)
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        label_style = """
            QLabel {
                color: #1a365d;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                margin-bottom: 5px;
            }
        """


        combo_style = """
            QComboBox {
                border: 2px solid #2b4c7e;
                border-radius: 15px;
                padding: 5px 15px;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                min-height: 30px;
                max-height: 30px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2b4c7e;
                margin-right: 5px;
            }
        """

        ending_container = QVBoxLayout()
        ending_label = QLabel("בחר פעולה לסוף קטע:")
        ending_label.setStyleSheet(label_style)
        
        self.ending_var = QComboBox()
        self.ending_var.addItems(["הוסף נקודותיים", "הוסף נקודה", "ללא שינוי"])
        self.ending_var.setStyleSheet(combo_style)
        self.ending_var.setFixedWidth(170)
        
        ending_container.addWidget(ending_label, alignment=Qt.AlignCenter)
        ending_container.addWidget(self.ending_var, alignment=Qt.AlignCenter)
        layout.addLayout(ending_container)

        # הדגשת תחילת קטע
        self.emphasize_var = QCheckBox("הדגש את תחילת הקטעים")
        self.emphasize_var.setStyleSheet("""
            QCheckBox {
                color: #1a365d;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        self.emphasize_var.setChecked(True)
        layout.addWidget(self.emphasize_var, alignment=Qt.AlignCenter)

        # כפתור הפעלה
        button_container = QHBoxLayout()
        run_button = QPushButton("הפעל")
        run_button.clicked.connect(self.run_script)
        run_button.setStyleSheet("""
            QPushButton {
                border-radius: 15px;
                padding: 5px;
                background-color: #eaeaea;
                color: black;
                font-weight: bold;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                min-height: 30px;
                max-height: 30px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #b7b5b5;
            }
            QPushButton:pressed {
                background-color: #a0a0a0;
            }
        """)
        button_container.addStretch(1)
        button_container.addWidget(run_button)
        button_container.addStretch(1)
        layout.addLayout(button_container)


        layout.addStretch()

        self.setLayout(layout)
        
    def set_file_path(self, file_path):
        """מקבלת את נתיב הקובץ מהחלון הראשי"""
        if not file_path or not os.path.isfile(file_path):
            QMessageBox.critical(self, "שגיאה", "נתיב קובץ לא תקין")
            return False
        
        if not file_path.lower().endswith('.txt'):
            QMessageBox.critical(self, "שגיאה", "יש לבחור קובץ טקסט (txt) בלבד")
            return False
        
        self.file_path = file_path
        return True

    def run_script(self):
        if not self.file_path:
            QMessageBox.warning(self, "שגיאה", "נא לבחור קובץ תחילה")
            return

        try:
            changes_count = self.process_file(
                self.file_path, 
                self.ending_var.currentText(), 
                self.emphasize_var.isChecked()
            )
            
            if changes_count > 0:
                QMessageBox.information(
                    self, 
                    "!מזל טוב", 
                    f"בוצעו {changes_count} שינויים בהצלחה!"
                )
                update_global_status("הדגשת מילה ראשונה וניקוד סוף קטע")
                self.changes_made.emit()  # שליחת סיגנל על שינויים
            else:
                QMessageBox.information(
                    self, 
                    "!שים לב", 
                    "לא נמצאו שינויים מתאימים בקובץ"
                )
        except Exception as e:
            QMessageBox.critical(
                self, 
                "שגיאה", 
                f"אירעה שגיאה בעיבוד הקובץ: {str(e)}"
            )

    def process_file(self, file_path, add_ending, emphasize_start):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            changes_count = 0
            new_lines = []

            for line in lines:
                line = line.rstrip()
                words = line.split()

                # בדיקה אם יש יותר מעשר מילים ושאין סימן כותרת בהתחלה
                if (len(words) > 10 and 
                    not any(line.startswith(f'<h{n}>') for n in range(2, 10))):
                    
                    # הסרת רווחים ותווים מיותרים בסוף השורה
                    line = line.rstrip(" .,;:!?)</small></big></b>")

                    # הוספת סימן סוף
                    if add_ending != "ללא שינוי":
                        if line.endswith(','):
                            line = line[:-1]
                            line += '.' if add_ending == "הוסף נקודה" else ':'
                            changes_count += 1
                        elif not line.endswith(('.', ':', '!', '?')) and \
                             not any(line.endswith(tag) for tag in ['</small>', '</big>', '</b>']):
                            line += '.' if add_ending == "הוסף נקודה" else ':'
                            changes_count += 1

                    # הדגשת המילה הראשונה
                    if emphasize_start:
                        first_word = words[0]
                        if not any(tag in first_word for tag in ['<b>', '<small>', '<big>', '<h2>', '<h3>', '<h4>', '<h5>', '<h6>']):
                            if not (first_word.startswith('<') and first_word.endswith('>')):
                                line = f'<b>{first_word}</b> ' + ' '.join(words[1:])
                                changes_count += 1

                new_lines.append(line + '\n')

            # שמירת השינויים
            if changes_count > 0:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.writelines(new_lines)

            return changes_count

        except FileNotFoundError:
            QMessageBox.critical(self, "שגיאה", "הקובץ לא נמצא")
            return 0
        except UnicodeDecodeError:
            QMessageBox.critical(self, "שגיאה", "קידוד הקובץ אינו נתמך. יש להשתמש בקידוד UTF-8.")
            return 0
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בעיבוד הקובץ: {str(e)}")
            return 0

    def load_icon_from_base64(self, base64_string):
        """טעינת אייקון ממחרוזת Base64"""
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(base64_string))
        return QIcon(pixmap)
# ==========================================
# Script 5: יצירת כותרות לעמוד ב (6 לשעבר)
# ==========================================
class CreatePageBHeaders(QWidget):
    changes_made = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.file_path = ""
        self.setWindowTitle("יצירת כותרות עמוד ב")
        self.setWindowIcon(self.load_icon_from_base64(icon_base64))
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFixedWidth(600)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # הסבר למשתמש - שילוב של שני ההסברים בעיצוב המודרני
        explanation = QLabel(
            "הסבר:\n\n"
            "• התוכנה תוסיף כותרת 'עמוד ב' במקרים הבאים:\n"
            "• בתחילת שורה שכתוב בה 'עמוד ב' או 'ע\"ב'\n"
            "• אם כתוב 'שם' לפני המילים הנ\"ל, המילה 'שם' תימחק\n"
            "• אם כתוב 'גמרא' לפני המילים הנ\"ל, המילה 'גמרא' תועבר לשורה הבאה"
        )
        explanation.setStyleSheet("""
            QLabel {
                color: #1e4620;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                padding: 20px;
                background-color: #e8f5e9;
                border: 2px solid #81c784;
                border-radius: 15px;
                font-weight: bold;
            }
        """)
        explanation.setAlignment(Qt.AlignCenter)
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        label_style = """
            QLabel {
                color: #1a365d;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                margin-bottom: 5px;
            }
        """

        combo_style = """
            QComboBox {
                border: 2px solid #2b4c7e;
                border-radius: 15px;
                padding: 5px 15px;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                min-height: 30px;
                max-height: 30px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2b4c7e;
                margin-right: 5px;
            }
        """

        # רמת כותרת
        level_container = QHBoxLayout()
        level_label = QLabel("רמת כותרת:")
        level_label.setStyleSheet(label_style)
        
        self.level_var = QComboBox()
        self.level_var.addItems([str(i) for i in range(2, 7)])
        self.level_var.setCurrentText("3")
        self.level_var.setStyleSheet(combo_style)
        self.level_var.setFixedWidth(100)
        
        level_container.addStretch(1)
        level_container.addWidget(self.level_var)
        level_container.addWidget(level_label)
        level_container.addStretch(1)
        
        layout.addLayout(level_container)

        # כפתור הפעלה
        button_container = QHBoxLayout()
        run_button = QPushButton("הפעל")
        run_button.clicked.connect(self.run_script)
        run_button.setStyleSheet("""
            QPushButton {
                border-radius: 15px;
                padding: 5px;
                background-color: #eaeaea;
                color: black;
                font-weight: bold;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                min-height: 30px;
                max-height: 30px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #b7b5b5;
            }
            QPushButton:pressed {
                background-color: #a0a0a0;
            }
        """)
        button_container.addStretch(1)
        button_container.addWidget(run_button)
        button_container.addStretch(1)
        layout.addLayout(button_container)

        layout.addStretch()
        self.setLayout(layout)

    def set_file_path(self, file_path):
        """מקבלת את נתיב הקובץ מהחלון הראשי"""
        if not file_path or not os.path.isfile(file_path):
            QMessageBox.critical(self, "שגיאה", "נתיב קובץ לא תקין")
            return False
        
        if not file_path.lower().endswith('.txt'):
            QMessageBox.critical(self, "שגיאה", "יש לבחור קובץ טקסט (txt) בלבד")
            return False
        
        self.file_path = file_path
        return True

    def build_tag_agnostic_pattern(self, word, optional_end_chars="['\"']*"):
        """בניית תבנית שמתעלמת מתגיות HTML"""
        ANY_TAGS_SPACES = r'(?:<[^>]+>\s*)*'
        pattern = ''
        for char in word:
            pattern += ANY_TAGS_SPACES + re.escape(char)
        pattern += ANY_TAGS_SPACES
        if optional_end_chars:
            pattern += optional_end_chars + ANY_TAGS_SPACES
        return pattern

    def strip_and_replace(self, text, header_level, counter):
        """עיבוד הטקסט והחלפת המילים בכותרות"""
        ANY_TAGS_SPACES = r'(?:<[^>]+>\s*)*'
        NON_WORD = r'(?:[^\w<>]|$)'
        pattern = r"^\s*" + ANY_TAGS_SPACES

        # אופציונלי: המילה 'שם'
        shem_pattern = self.build_tag_agnostic_pattern('שם', optional_end_chars='')
        pattern += r"(?P<shem>" + shem_pattern + r"\s*)?"

        # אופציונלי: 'גמרא' וגרסאותיה
        gmarah_variants = ['גמרא', 'בגמרא', "גמ'", "בגמ'"]
        gmarah_patterns = [self.build_tag_agnostic_pattern(word, optional_end_chars='') for word in gmarah_variants]
        gmarah_pattern = r"(?P<gmarah>" + '|'.join(gmarah_patterns) + r")\s*"
        pattern += r"(?:" + gmarah_pattern + r")?"

        # 'עמוד ב' או 'ע"ב'
        ab_variants = ['עמוד ב', 'ע"ב', "ע''ב", "ע'ב"]
        ab_patterns = [r"(?<!\w)" + self.build_tag_agnostic_pattern(word) + r"(?!\w)" for word in ab_variants]
        ab_pattern = r"(?P<ab>" + '|'.join(ab_patterns) + r")"

        pattern += ab_pattern
        pattern += NON_WORD
        pattern += r"(?P<rest>.*)"

        match_pattern = re.compile(pattern, re.IGNORECASE | re.UNICODE)

        def replace_function(match):
            header = f"<h{header_level}>עמוד ב</h{header_level}>"
            rest_of_line = match.group('rest').lstrip()

            gmarah_text = match.group('gmarah')
            if gmarah_text:
                gmarah_text = re.sub(ANY_TAGS_SPACES, '', gmarah_text).strip()

            counter[0] += 1

            if gmarah_text:
                return f"{header}\n{gmarah_text} {rest_of_line}\n" if rest_of_line else f"{header}\n{gmarah_text}\n"
            else:
                return f"{header}\n{rest_of_line}\n" if rest_of_line else f"{header}\n"

        if re.search(r"<h\d>.*?</h\d>", text, re.IGNORECASE):
            return text

        new_text = match_pattern.sub(replace_function, text)
        new_text = re.sub(r'\n\s*\n', '\n', new_text)

        return new_text

    def process_file(self, file_path, header_level):
        """עיבוד הקובץ ויצירת הכותרות"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            new_lines = []
            counter = [0]

            for line in lines:
                new_line = self.strip_and_replace(line, header_level, counter)
                new_lines.append(new_line)

            if counter[0] > 0:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.writelines(new_lines)
                
                QMessageBox.information(self, "!מזל טוב", f"בוצעו {counter[0]} שינויים בהצלחה!")
                update_global_status("כותרות לעמוד ב")
                self.changes_made.emit()
            else:
                QMessageBox.information(self, "!שים לב", "לא נמצאו שינויים מתאימים בקובץ")

        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"אירעה שגיאה בעיבוד הקובץ: {str(e)}")

    def run_script(self):
        """הפעלת הסקריפט"""
        if not self.file_path:
            QMessageBox.warning(self, "שגיאה", "נא לבחור קובץ תחילה")
            return

        try:
            header_level = int(self.level_var.currentText())
            if header_level < 2 or header_level > 6:
                QMessageBox.warning(self, "שגיאה", "רמת הכותרת צריכה להיות בין 2 ל-6")
                return
            
            self.process_file(self.file_path, header_level)

        except ValueError:
            QMessageBox.warning(self, "שגיאה", "רמת הכותרת צריכה להיות מספר בין 2 ל-6")
            return

    def load_icon_from_base64(self, base64_string):
        """טעינת אייקון ממחרוזת Base64"""
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(base64_string))
        return QIcon(pixmap)
    
# ==========================================
# Script 6: החלפת כותרות לעמוד ב (7 לשעבר)
# ==========================================
class ReplacePageBHeaders(QWidget):
    changes_made = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.file_path = ""
        self.setWindowTitle("החלפת כותרות לעמוד ב")
        self.setWindowIcon(self.load_icon_from_base64(icon_base64))
        self.setGeometry(100, 100, 500, 500)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFixedWidth(600)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)


        attention = QLabel(
            "שים לב!\n"
            "התוכנה פועלת רק אם הדפים והעמודים הוגדרו כבר ככותרות\n"
            "[לא משנה באיזו רמת כותרת]\n"
            "כגון:  <h3>עמוד ב</h3> או: <h2>עמוד ב</h2> וכן הלאה"
        )
        attention.setStyleSheet("""
            QLabel {
                color: #8B0000;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                padding: 20px;
                background-color: #FFE4E1;
                border: 2px solid #CD5C5C;
                border-radius: 15px;
                font-weight: bold;
            }
        """)
        attention.setAlignment(Qt.AlignCenter)
        attention.setWordWrap(True)
        layout.addWidget(attention)

        warning = QLabel(
            "זהירות!\n"
            "בדוק היטב שלא פספסת שום כותרת של 'דף' לפני שאתה מריץ תוכנה זו\n"
            "כי במקרה של פספוס, הכותרת 'עמוד ב' שאחרי הפספוס תהפך לכותרת שגויה"
        )
        warning.setStyleSheet("""
            QLabel {
                color: #8B0000;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                padding: 20px;
                background-color: #FFE4E1;
                border: 2px solid #CD5C5C;
                border-radius: 15px;
                font-weight: bold;
            }
        """)
        warning.setAlignment(Qt.AlignCenter)
        warning.setWordWrap(True)
        layout.addWidget(warning)

        label_style = """
            QLabel {
                color: #1a365d;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                margin-bottom: 5px;
            }
        """

        combo_style = """
            QComboBox {
                border: 2px solid #2b4c7e;
                border-radius: 15px;
                padding: 5px 15px;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                min-height: 30px;
                max-height: 30px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2b4c7e;
                margin-right: 5px;
            }
        """

        # סוג ההחלפה
        replace_container = QVBoxLayout()
        replace_label = QLabel("בחר את סוג ההחלפה:")
        replace_label.setStyleSheet(label_style)
        
        self.replace_type = QComboBox()
        self.replace_type.addItems(["נקודותיים", "ע\"ב"])
        self.replace_type.setStyleSheet(combo_style)
        self.replace_type.setFixedWidth(140)
        
        replace_container.addWidget(replace_label, alignment=Qt.AlignCenter)
        replace_container.addWidget(self.replace_type, alignment=Qt.AlignCenter)
        layout.addLayout(replace_container)

        # דוגמאות
        example1 = QLabel("לדוגמא:\nדף ב:   דף ג:   דף ד:   דף ה:\nוכן הלאה")
        example1.setStyleSheet("""
            QLabel {
                font-family: "Segoe UI", Arial;
                font-size: 18px;
                color: #666;
            }
        """)
        example1.setAlignment(Qt.AlignCenter)
        layout.addWidget(example1)

        example2 = QLabel("או:\nדף ב ע\"ב   דף ג ע\"ב   דף ד ע\"ב   דף ה ע\"ב\nוכן הלאה")
        example2.setStyleSheet("""
            QLabel {
                font-family: "Segoe UI", Arial;
                font-size: 18px;
                color: #666;
            }
        """)
        example2.setAlignment(Qt.AlignCenter)
        layout.addWidget(example2)

        # כפתור הפעלה
        button_container = QHBoxLayout()
        run_button = QPushButton("בצע החלפה")
        run_button.clicked.connect(self.run_script)
        run_button.setStyleSheet("""
            QPushButton {
                border-radius: 15px;
                padding: 5px;
                background-color: #eaeaea;
                color: black;
                font-weight: bold;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                min-height: 30px;
                max-height: 30px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #b7b5b5;
            }
            QPushButton:pressed {
                background-color: #a0a0a0;
            }
        """)
        button_container.addStretch(1)
        button_container.addWidget(run_button)
        button_container.addStretch(1)
        layout.addLayout(button_container)


        layout.addStretch()

        self.setLayout(layout)


    def set_file_path(self, file_path):
        """מקבלת את נתיב הקובץ מהחלון הראשי"""
        if not file_path or not os.path.isfile(file_path):
            QMessageBox.critical(self, "שגיאה", "נתיב קובץ לא תקין")
            return False
        
        if not file_path.lower().endswith('.txt'):
            QMessageBox.critical(self, "שגיאה", "יש לבחור קובץ טקסט (txt) בלבד")
            return False
        
        self.file_path = file_path
        return True

    def run_script(self):
        if not self.file_path:
            QMessageBox.warning(self, "שגיאה", "נא לבחור קובץ תחילה")
            return

        replace_type = self.replace_type.currentText()

        try:
            replacements_made = self.update_file(self.file_path, replace_type)
            
            if replacements_made > 0:
                QMessageBox.information(
                    self, 
                    "!מזל טוב", 
                    f"בוצעו {replacements_made} החלפות בהצלחה!"
                )
                update_global_status("החלפות כותרת עמוד ב")
                self.changes_made.emit()  # שליחת סיגנל על שינויים
            else:
                QMessageBox.information(
                    self, 
                    "!שים לב", 
                    "לא נמצאו כותרות להחלפה"
                )
        except Exception as e:
            QMessageBox.critical(
                self, 
                "שגיאה", 
                f"אירעה שגיאה בעיבוד הקובץ: {str(e)}"
            )

    def update_file(self, file_path, replace_type):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            previous_title = ""
            previous_level = ""
            replacements_made = 0  # ספירת כמות ההחלפות

            def replace_match(match):
                nonlocal previous_title, previous_level, replacements_made
                level = match.group(1)
                title = match.group(2)

                # בדיקה אם הכותרת היא "דף"
                if re.match(r"דף \S+\.?", title):
                    previous_title = title.strip()
                    previous_level = level
                    return match.group(0)

                # בדיקה אם הכותרת היא "עמוד ב"
                elif title == "עמוד ב":
                    replacements_made += 1  # הוחלפה כותרת
                    if replace_type == "נקודותיים":
                        return f'<h{previous_level}>{previous_title.rstrip(".")}:</h{previous_level}>'
                    elif replace_type == "ע\"ב":
                        # הסרת "ע\"א" או "עמוד א" מהכותרת הקודמת אם קיימים
                        modified_title = re.sub(r'( ע\"א| עמוד א)$', '', previous_title)
                        return f'<h{previous_level}>{modified_title.rstrip(".")} ע\"ב</h{previous_level}>'

                # אם זה לא אחד המקרים למעלה, נשאיר את הכותרת כפי שהיא
                return match.group(0)

            content = re.sub(r'<h([1-9])>(.*?)</h\1>', replace_match, content)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

            return replacements_made

        except FileNotFoundError:
            QMessageBox.critical(self, "שגיאה", "הקובץ לא נמצא")
            return 0
        except UnicodeDecodeError:
            QMessageBox.critical(self, "שגיאה", "קידוד הקובץ אינו נתמך. יש להשתמש בקידוד UTF-8.")
            return 0
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בעיבוד הקובץ: {str(e)}")
            return 0

    def load_icon_from_base64(self, base64_string):
        """טעינת אייקון ממחרוזת Base64"""
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(base64_string))
        return QIcon(pixmap)



    
   
def create_labeled_widget(label_text, widget):
    """יוצר widget עם תווית"""
    container = QWidget()
    v_layout = QVBoxLayout()
    v_layout.setContentsMargins(0, 0, 0, 0)
    v_layout.setSpacing(2)
    label = QLabel(label_text)
    label.setStyleSheet("font-size: 24px;")
    v_layout.addWidget(label)
    v_layout.addWidget(widget)
    container.setLayout(v_layout)
    return container

class בדיקת_שגיאות_בכותרות(QWidget):
    changes_made = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = ""
        self.setWindowTitle("בדיקת שגיאות בכותרות")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # תווים בתחילת וסוף הכותרת
        regex_layout = QHBoxLayout()
        
        re_start_label = QLabel("תו/ים בתחילת הכותרת:")
        re_start_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.re_start_entry = QLineEdit()
        self.re_start_entry.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        re_end_label = QLabel("תו/ים בסוף הכותרת:")
        self.re_end_entry = QLineEdit()
        self.re_end_entry.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.gershayim_var = QCheckBox("כולל גרשיים")
        
        regex_layout.addWidget(self.gershayim_var)
        regex_layout.addWidget(self.re_end_entry)
        regex_layout.addWidget(re_end_label)
        regex_layout.addWidget(self.re_start_entry)
        regex_layout.addWidget(re_start_label)
        layout.addLayout(regex_layout)

        # יצירת תיבות טקסט להצגת תוצאות
        self.unmatched_regex_text = QTextEdit()
        self.unmatched_regex_text.setReadOnly(True)
        self.unmatched_tags_text = QTextEdit()
        self.unmatched_tags_text.setReadOnly(True)

        # יצירת מכולות עם תוויות
        regex_container = create_labeled_widget(
            "פירוט הכותרות שיש בהן תווים מיותרים (חוץ ממה שנכתב בתיבות הבחירה למעלה)\n"
            "אם יש רווח לפני או אחרי הכותרת, זה גם יוצג כשגיאה",
            self.unmatched_regex_text
        )
        tags_container = create_labeled_widget(
            "פירוט הכותרות שאינן לפי הסדר",
            self.unmatched_tags_text
        )

        # יצירת מפריד אנכי
        v_splitter = QSplitter(Qt.Vertical)
        v_splitter.setHandleWidth(10)
        v_splitter.addWidget(regex_container)
        v_splitter.addWidget(tags_container)
        layout.addWidget(v_splitter)

        self.setLayout(layout)

    def load_file_and_process(self, file_path):
        """עיבוד הקובץ והצגת התוצאות"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                html_content = file.read()
            
            re_start = self.re_start_entry.text()
            re_end = self.re_end_entry.text()
            gershayim = self.gershayim_var.isChecked()

            unmatched_regex, unmatched_tags = self.process_html(html_content, re_start, re_end, gershayim)
            
            # הצגת התוצאות
            if unmatched_regex:
                self.unmatched_regex_text.setPlainText("\n".join(unmatched_regex))
            else:
                self.unmatched_regex_text.setPlainText("לא נמצאו שגיאות")
                
            if unmatched_tags:
                self.unmatched_tags_text.setPlainText("\n".join(unmatched_tags))
            else:
                self.unmatched_tags_text.setPlainText("לא נמצאו שגיאות")

        except Exception as e:
            QMessageBox.critical(None, "שגיאה", f"שגיאה בעיבוד הקובץ: {str(e)}")

    def process_html(self, html_content, re_start, re_end, gershayim):
        """עיבוד תוכן ה-HTML ובדיקת שגיאות"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # יצירת תבנית regex
        if re_start and re_end:
            pattern = re.compile(f"^{re_start}.+[{re_end}]$")
        elif re_start:
            pattern = re.compile(f"^{re_start}.+['א-ת]$")
        elif re_end:
            pattern = re.compile(f"^[א-ת].+[{re_end}]$")
        else:
            pattern = re.compile(r"^[א-ת].+[א-ת']$")

        unmatched_regex = []
        unmatched_tags = []

        # בדיקת כותרות h2-h6
        for level in range(2, 7):
            headers = soup.find_all(f"h{level}")
            
            if not headers:
                unmatched_tags.append(f"מידע: אין בקובץ כותרות ברמה {level}")
                continue

            for i in range(len(headers) - 1):
                curr_header = headers[i].string or ""
                next_header = headers[i + 1].string or ""
                
                if not curr_header or not next_header:
                    continue

                # בדיקת תבנית
                if not re.match(pattern, curr_header):
                    unmatched_regex.append(curr_header)

                # חילוץ המספר מהכותרת
                curr_parts = curr_header.split()
                next_parts = next_header.split()
                
                curr_num = curr_parts[1] if len(curr_parts) > 1 else curr_header
                next_num = next_parts[1] if len(next_parts) > 1 else next_header

                # בדיקת גרשיים
                if gershayim:
                    if gematria.to_number(curr_num) <= 9:
                        if "'" not in curr_num:
                            unmatched_tags.append(curr_num)
                    elif '"' not in curr_num:
                        unmatched_tags.append(curr_num)
                elif "'" in curr_num or '"' in curr_num:
                    unmatched_tags.append(curr_num)

                # בדיקת רצף
                if not gematria.to_number(curr_num) + 1 == gematria.to_number(next_num):
                    unmatched_tags.append(f"כותרת נוכחית - {curr_header}, כותרת הבאה - {next_header}")

            # בדיקת הכותרת האחרונה
            if headers:
                last_header = headers[-1].string or ""
                if last_header and not re.match(pattern, last_header):
                    unmatched_regex.append(last_header)

                last_num = last_header.split()[1] if len(last_header.split()) > 1 else last_header
                if gershayim:
                    if gematria.to_number(last_num) <= 9:
                        if "'" not in last_num:
                            unmatched_tags.append(last_num)
                    elif '"' not in last_num:
                        unmatched_tags.append(last_num)
                elif "'" in last_num or '"' in last_num:
                    unmatched_tags.append(last_num)

        return unmatched_regex, unmatched_tags
    
class בדיקת_שגיאות_בתגים(QWidget):
    changes_made = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = ""
        self.setWindowTitle("בודק שגיאות בעיצוב")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # יצירת תיבות טקסט
        self.opening_without_closing = QTextEdit()
        self.opening_without_closing.setReadOnly(True)

        self.closing_without_opening = QTextEdit()
        self.closing_without_opening.setReadOnly(True)

        self.heading_errors = QTextEdit()
        self.heading_errors.setReadOnly(True)

        # יצירת מכולות עם תוויות
        opening_container = create_labeled_widget(
            "תגים פותחים ללא תגים סוגרים",
            self.opening_without_closing
        )
        closing_container = create_labeled_widget(
            "תגים סוגרים ללא תגים פותחים",
            self.closing_without_opening
        )
        heading_container = create_labeled_widget(
            "טקסט שאינו חלק מכותרת, שנמצא באותה שורה עם הכותרת",
            self.heading_errors
        )

        # יצירת מפריד אנכי
        v_splitter = QSplitter(Qt.Vertical)
        v_splitter.setHandleWidth(10)
        v_splitter.addWidget(opening_container)
        v_splitter.addWidget(closing_container)
        v_splitter.addWidget(heading_container)

        main_layout.addWidget(v_splitter)
        self.setLayout(main_layout)

    def load_file_and_check(self, file_path):
        """בדיקת שגיאות בקובץ"""
        # ניקוי תוצאות קודמות
        self.opening_without_closing.clear()
        self.closing_without_opening.clear()
        self.heading_errors.clear()

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            opening_without_closing_list = []
            closing_without_opening_list = []
            heading_errors_list = []

            for line_num, line in enumerate(lines, 1):
                # בדיקת תגים
                tags_in_line = re.findall(r'<(/?\w+)>', line)
                stack = []

                for tag in tags_in_line:
                    if not tag.startswith('/'):  # תג פותח
                        stack.append(tag)
                    else:  # תג סוגר
                        if stack and stack[-1] == tag[1:]:
                            stack.pop()
                        else:
                            closing_without_opening_list.append(
                                f"שורה {line_num}: </{tag[1:]}> || {line.strip()}"
                            )

                # תגים שנשארו פתוחים
                for tag in stack:
                    opening_without_closing_list.append(
                        f"שורה {line_num}: <{tag}> || {line.strip()}"
                    )

                # בדיקת טקסט מחוץ לכותרות
                for tag in ["h2", "h3", "h4", "h5", "h6"]:
                    heading_pattern = rf'<{tag}>.*?</{tag}>'
                    match = re.search(heading_pattern, line)
                    if match:
                        start, end = match.span()
                        before = line[:start].strip()
                        after = line[end:].strip()
                        if before or after:
                            heading_errors_list.append(f"שורה {line_num}: {line.strip()}")

            # הצגת תוצאות
            self.opening_without_closing.setPlainText(
                "\n".join(opening_without_closing_list) if opening_without_closing_list 
                else "לא נמצאו שגיאות"
            )
            
            self.closing_without_opening.setPlainText(
                "\n".join(closing_without_opening_list) if closing_without_opening_list 
                else "לא נמצאו שגיאות"
            )
            
            self.heading_errors.setPlainText(
                "\n".join(heading_errors_list) if heading_errors_list 
                else "לא נמצאו שגיאות"
            )

        except Exception as e:
            QMessageBox.critical(None, "שגיאה", f"שגיאה בבדיקת הקובץ: {str(e)}")


class CheckHeadingErrorsOriginal(QWidget):
    changes_made = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.file_path = ""
        self.setWindowTitle("בודק כותרות + בודק תגים ביחד")
        self.setWindowIcon(self.get_app_icon())
        self.resize(1250, 700)

        # יצירת הווידג'טים המשניים
        self.check_headings_widget = בדיקת_שגיאות_בכותרות()
        self.html_tag_checker_widget = בדיקת_שגיאות_בתגים()
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # יצירת מפריד אופקי
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle:horizontal {
                width: 5px;
                margin: 1.5px;
                background: gray;
            }
        """)
        
        splitter.setChildrenCollapsible(False)
        
        # הגדרת מינימום רוחב
        self.html_tag_checker_widget.setMinimumWidth(10)
        self.check_headings_widget.setMinimumWidth(10)

        # הוספת הווידג'טים למיכל
        html_container = QWidget()
        self.html_container_layout = QVBoxLayout(html_container)
        self.html_container_layout.setContentsMargins(0, 0, 0, 0)
        self.html_container_layout.addWidget(self.html_tag_checker_widget)

        # תווית לציורים בספר
        self.pic_count_label = QLabel("")
        self.pic_count_label.setStyleSheet("font-size: 18px; color: blue;")
        self.pic_count_label.setVisible(False)
        
        splitter.addWidget(html_container)
        splitter.addWidget(self.check_headings_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def set_file_path(self, file_path):
        """קבלת נתיב הקובץ ועיבודו"""
        self.file_path = file_path
        self.process_file(file_path)

    def process_file(self, file_path):
        """עיבוד הקובץ ובדיקת שגיאות"""
        try:
            # הפעלת בדיקות בשני הווידג'טים
            self.check_headings_widget.load_file_and_process(file_path)
            self.html_tag_checker_widget.load_file_and_check(file_path)

            # בדיקת ציורים בספר
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                count = content.count("ציור בספר")
                
                if count > 0:
                    text = (f'שים לב! יש בספר {count} ציורים.\n'
                           'חפש בתוך הספר את המילים "ציור בספר",\n'
                           'הורד את הספר מהיברובוקס, עשה צילום מסך לתמונה,\n'
                           'והמר אותה לטקסט ע"י תוכנה מספר 10')
                    self.pic_count_label.setText(text)
                    self.pic_count_label.setVisible(True)
                    if self.pic_count_label.parent() is None:
                        self.html_container_layout.addWidget(self.pic_count_label)
                else:
                    self.pic_count_label.setVisible(False)

        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בעיבוד הקובץ: {str(e)}")

    def get_app_icon(self):
        """טעינת אייקון מקידוד Base64"""
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(icon_base64))
        return QIcon(pixmap)
    
# ==========================================
# Script 8: בדיקת שגיאות בכותרות מותאם לספרים על השס (9 לשעבר)
# ==========================================

def create_labeled_widget(label_text, widget):
    """יוצר widget עם תווית בעיצוב אחיד"""
    container = QWidget()
    v_layout = QVBoxLayout()
    v_layout.setContentsMargins(0, 0, 0, 0)
    v_layout.setSpacing(5)
    
    label = QLabel(label_text)
    label.setStyleSheet("""
        QLabel {
            color: #1a365d;
            font-family: "Segoe UI", Arial;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }
    """)
    
    # עיצוב ל-QTextEdit
    widget.setStyleSheet("""
        QTextEdit {
            border: 2px solid #2b4c7e;
            border-radius: 15px;
            padding: 10px;
            background-color: white;
            font-family: "Segoe UI", Arial;
            font-size: 24px;
        }
    """)
    
    v_layout.addWidget(label)
    v_layout.addWidget(widget)
    container.setLayout(v_layout)
    return container

class בדיקת_שגיאות_בכותרות_לשס(QWidget):
    changes_made = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = ""
        self.setWindowTitle("בדיקת שגיאות בכותרות לש\"ס")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # תווים בתחילת וסוף הכותרת
        regex_layout = QHBoxLayout()
        
        re_start_label = QLabel("תו/ים בתחילת הכותרת:")
        re_start_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.re_start_entry = QLineEdit()
        self.re_start_entry.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        re_end_label = QLabel("תו/ים בסוף הכותרת:")
        self.re_end_entry = QLineEdit()
        self.re_end_entry.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.re_end_entry.setText('. :')
        
        self.gershayim_var = QCheckBox("כולל גרשיים")
        
        regex_layout.addWidget(self.gershayim_var)
        regex_layout.addWidget(self.re_end_entry)
        regex_layout.addWidget(re_end_label)
        regex_layout.addWidget(self.re_start_entry)
        regex_layout.addWidget(re_start_label)
        layout.addLayout(regex_layout)

        # יצירת תיבות טקסט להצגת תוצאות
        self.unmatched_regex_text = QTextEdit()
        self.unmatched_regex_text.setReadOnly(True)
        self.unmatched_tags_text = QTextEdit()
        self.unmatched_tags_text.setReadOnly(True)

        # יצירת מכולות עם תוויות
        regex_container = create_labeled_widget(
            "פירוט הכותרות שיש בהן תווים מיותרים (חוץ ממה שנכתב בתיבות הבחירה למעלה)\n"
            "אם יש רווח לפני או אחרי הכותרת, זה גם יוצג כשגיאה",
            self.unmatched_regex_text
        )
        tags_container = create_labeled_widget(
            "פירוט הכותרות שאינן לפי הסדר\n"
            "התוכנה מדלגת בבדיקה בכל פעם על כותרת אחת, בגלל הכותרות הכפולות לעמוד ב",
            self.unmatched_tags_text
        )

        # יצירת מפריד אנכי
        v_splitter = QSplitter(Qt.Vertical)
        v_splitter.setHandleWidth(10)
        v_splitter.addWidget(regex_container)
        v_splitter.addWidget(tags_container)
        layout.addWidget(v_splitter)

        self.setLayout(layout)

    def load_file_and_process(self, file_path):
        """עיבוד הקובץ והצגת התוצאות"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                html_content = file.read()
            
            re_start = self.re_start_entry.text()
            re_end = self.re_end_entry.text()
            gershayim = self.gershayim_var.isChecked()

            unmatched_regex, unmatched_tags = self.process_html(html_content, re_start, re_end, gershayim)
            
            # הצגת התוצאות
            if unmatched_regex:
                self.unmatched_regex_text.setPlainText("\n".join(unmatched_regex))
            else:
                self.unmatched_regex_text.setPlainText("לא נמצאו שגיאות")
                
            if unmatched_tags:
                self.unmatched_tags_text.setPlainText("\n".join(unmatched_tags))
            else:
                self.unmatched_tags_text.setPlainText("לא נמצאו שגיאות")

        except Exception as e:
            QMessageBox.critical(None, "שגיאה", f"שגיאה בעיבוד הקובץ: {str(e)}")

    def process_html(self, html_content, re_start, re_end, gershayim):
        """עיבוד תוכן ה-HTML ובדיקת שגיאות"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # יצירת תבנית regex
        if re_start and re_end:
            pattern = re.compile(f"^{re_start}.+[{re_end}]$")
        elif re_start:
            pattern = re.compile(f"^{re_start}.+['א-ת]$")
        elif re_end:
            pattern = re.compile(f"^[א-ת].+[{re_end}]$")
        else:
            pattern = re.compile(r"^[א-ת].+[א-ת']$")

        unmatched_regex = []
        unmatched_tags = []

        # בדיקת כותרות h2-h6
        for level in range(2, 7):
            headers = soup.find_all(f"h{level}")
            
            if not headers:
                unmatched_tags.append(f"מידע: אין בקובץ כותרות ברמה {level}")
                continue

            # עיבוד כל הכותרות למעט שתי האחרונות
            for i in range(len(headers) - 2):
                curr_header = headers[i].string or ""
                next_header = headers[i + 2].string or ""  # דילוג על כותרת אחת
                
                if not curr_header or not next_header:
                    continue

                # בדיקת תבנית
                if not re.match(pattern, curr_header):
                    unmatched_regex.append(curr_header)

                # חילוץ המספר מהכותרת
                curr_parts = curr_header.split()
                next_parts = next_header.split()
                
                curr_num = curr_parts[1] if len(curr_parts) > 1 else curr_header
                next_num = next_parts[1] if len(next_parts) > 1 else next_header

                # בדיקת גרשיים
                if gershayim:
                    if gematria.to_number(curr_num) <= 9:
                        if "'" not in curr_num:
                            unmatched_tags.append(curr_num)
                    elif '"' not in curr_num:
                        unmatched_tags.append(curr_num)
                elif "'" in curr_num or '"' in curr_num:
                    unmatched_tags.append(curr_num)

                # בדיקת רצף (עם דילוג על כותרת אחת)
                if not gematria.to_number(curr_num) + 1 == gematria.to_number(next_num):
                    unmatched_tags.append(f"כותרת נוכחית - {curr_header}, כותרת הבאה - {next_header}")

            # בדיקת שתי הכותרות האחרונות
            if len(headers) >= 2:
                for last_header in [headers[-2].string or "", headers[-1].string or ""]:
                    if last_header and not re.match(pattern, last_header):
                        unmatched_regex.append(last_header)
                    
                    parts = last_header.split()
                    last_num = parts[1] if len(parts) > 1 else last_header
                    
                    if gershayim:
                        if gematria.to_number(last_num) <= 9:
                            if "'" not in last_num:
                                unmatched_tags.append(last_num)
                        elif '"' not in last_num:
                            unmatched_tags.append(last_num)
                    elif "'" in last_num or '"' in last_num:
                        unmatched_tags.append(last_num)

        return unmatched_regex, unmatched_tags
class בדיקת_שגיאות_בתגים_לשס(QWidget):
    changes_made = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = ""
        self.setWindowTitle("בודק שגיאות בעיצוב לש\"ס")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # יצירת תיבות טקסט
        self.opening_without_closing = QTextEdit()
        self.opening_without_closing.setReadOnly(True)

        self.closing_without_opening = QTextEdit()
        self.closing_without_opening.setReadOnly(True)

        self.heading_errors = QTextEdit()
        self.heading_errors.setReadOnly(True)

        # יצירת מכולות עם תוויות
        opening_container = create_labeled_widget(
            "תגים פותחים ללא תגים סוגרים",
            self.opening_without_closing
        )
        closing_container = create_labeled_widget(
            "תגים סוגרים ללא תגים פותחים",
            self.closing_without_opening
        )
        heading_container = create_labeled_widget(
            "טקסט שאינו חלק מכותרת, שנמצא באותה שורה עם הכותרת",
            self.heading_errors
        )

        # יצירת מפריד אנכי
        v_splitter = QSplitter(Qt.Vertical)
        v_splitter.setHandleWidth(10)
        v_splitter.addWidget(opening_container)
        v_splitter.addWidget(closing_container)
        v_splitter.addWidget(heading_container)

        main_layout.addWidget(v_splitter)
        self.setLayout(main_layout)

    def load_file_and_check(self, file_path):
        """בדיקת שגיאות בקובץ"""
        # ניקוי תוצאות קודמות
        self.opening_without_closing.clear()
        self.closing_without_opening.clear()
        self.heading_errors.clear()

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            opening_without_closing_list = []
            closing_without_opening_list = []
            heading_errors_list = []

            for line_num, line in enumerate(lines, 1):
                # בדיקת תגים
                tags_in_line = re.findall(r'<(/?\w+)>', line)
                stack = []

                for tag in tags_in_line:
                    if not tag.startswith('/'):  # תג פותח
                        stack.append(tag)
                    else:  # תג סוגר
                        if stack and stack[-1] == tag[1:]:
                            stack.pop()
                        else:
                            closing_without_opening_list.append(
                                f"שורה {line_num}: </{tag[1:]}> || {line.strip()}"
                            )

                # תגים שנשארו פתוחים
                for tag in stack:
                    opening_without_closing_list.append(
                        f"שורה {line_num}: <{tag}> || {line.strip()}"
                    )

                # בדיקת טקסט מחוץ לכותרות
                for tag in ["h2", "h3", "h4", "h5", "h6"]:
                    heading_pattern = rf'<{tag}>.*?</{tag}>'
                    match = re.search(heading_pattern, line)
                    if match:
                        start, end = match.span()
                        before = line[:start].strip()
                        after = line[end:].strip()
                        if before or after:
                            heading_errors_list.append(f"שורה {line_num}: {line.strip()}")

            # הצגת תוצאות
            self.opening_without_closing.setPlainText(
                "\n".join(opening_without_closing_list) if opening_without_closing_list 
                else "לא נמצאו שגיאות"
            )
            
            self.closing_without_opening.setPlainText(
                "\n".join(closing_without_opening_list) if closing_without_opening_list 
                else "לא נמצאו שגיאות"
            )
            
            self.heading_errors.setPlainText(
                "\n".join(heading_errors_list) if heading_errors_list 
                else "לא נמצאו שגיאות"
            )

        except Exception as e:
            QMessageBox.critical(None, "שגיאה", f"שגיאה בבדיקת הקובץ: {str(e)}")


class CheckHeadingErrorsCustom(QWidget):
    changes_made = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.file_path = ""
        self.setWindowTitle("בודק כותרות + בודק תגים לש\"ס")
        self.setWindowIcon(self.get_app_icon())
        self.resize(1250, 700)

        # יצירת הווידג'טים המשניים
        self.check_headings_widget = בדיקת_שגיאות_בכותרות_לשס()
        self.html_tag_checker_widget = בדיקת_שגיאות_בתגים_לשס()
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # יצירת מפריד אופקי
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle:horizontal {
                width: 5px;
                margin: 1.5px;
                background: gray;
            }
        """)
        
        splitter.setChildrenCollapsible(False)
        
        # הגדרת מינימום רוחב
        self.html_tag_checker_widget.setMinimumWidth(10)
        self.check_headings_widget.setMinimumWidth(10)

        # הוספת הווידג'טים למיכל
        html_container = QWidget()
        self.html_container_layout = QVBoxLayout(html_container)
        self.html_container_layout.setContentsMargins(0, 0, 0, 0)
        self.html_container_layout.addWidget(self.html_tag_checker_widget)

        # תווית לציורים בספר
        self.pic_count_label = QLabel("")
        self.pic_count_label.setStyleSheet("font-size: 18px; color: blue;")
        self.pic_count_label.setVisible(False)
        
        splitter.addWidget(html_container)
        splitter.addWidget(self.check_headings_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def set_file_path(self, file_path):
        """קבלת נתיב הקובץ ועיבודו"""
        self.file_path = file_path
        self.process_file(file_path)

    def process_file(self, file_path):
        """עיבוד הקובץ ובדיקת שגיאות"""
        try:
            # הפעלת בדיקות בשני הווידג'טים
            self.check_headings_widget.load_file_and_process(file_path)
            self.html_tag_checker_widget.load_file_and_check(file_path)

            # בדיקת ציורים בספר
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                count = content.count("ציור בספר")
                
                if count > 0:
                    text = (f'שים לב! יש בספר {count} ציורים.\n'
                           'חפש בתוך הספר את המילים "ציור בספר",\n'
                           'הורד את הספר מהיברובוקס, עשה צילום מסך לתמונה,\n'
                           'והמר אותה לטקסט ע"י תוכנה מספר 10')
                    self.pic_count_label.setText(text)
                    self.pic_count_label.setVisible(True)
                    if self.pic_count_label.parent() is None:
                        self.html_container_layout.addWidget(self.pic_count_label)
                else:
                    self.pic_count_label.setVisible(False)

        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בעיבוד הקובץ: {str(e)}")

    def get_app_icon(self):
        """טעינת אייקון מקידוד Base64"""
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(icon_base64))
        return QIcon(pixmap)    
# ==========================================
# Script 9: המרת תמונה לטקסט 10(לשעבר)
# ==========================================

class ImageToHtmlApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.file_path = "" 
        self.setWindowTitle("המרת תמונה לטקסט")
        self.setWindowIcon(self.load_icon_from_base64(icon_base64))
        #self.setGeometry(100, 100, 350,350)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFixedWidth(600)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)  

        label_style = """
            QLabel {
                color: #1a365d;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                padding: 10px;
            }
        """

        button_style = """
           QPushButton {
               border-radius: 15px;
               padding: 5px;
               background-color: #eaeaea;
               color: black;
               font-weight: bold;
               font-family: "Segoe UI", Arial;
               font-size: 24px;
               min-height: 30px;
              max-height: 30px;
             }
           QPushButton:hover {
               background-color: #b7b5b5;
           }
           QPushButton:disabled {
               background-color: #cccccc;
               color: #666666;
             }
          """

        # תווית מידע
        self.information_label = QLabel("לפניך מספר אפשרויות לבחירת התמונה\nבחר אחת מהן")
        self.information_label.setAlignment(Qt.AlignCenter)
        self.information_label.setStyleSheet(label_style)
        self.layout.addWidget(self.information_label)

        # אזור גרירה
        self.label = QLabel("גרור ושחרר את הקובץ", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #2b4c7e;
                border-radius: 15px;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                padding: 40px;
                background-color: #f8f9fa;
            }
        """)
        self.layout.addWidget(self.label)

        # תווית הוראות
        self.instruction_label = QtWidgets.QLabel("הדבק נתיב קובץ [או קישור מקוון לתמונה]\nאו הדבק את התמונה (Ctrl+V):")
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setStyleSheet(label_style)
        self.layout.addWidget(self.instruction_label)

        # תיבת טקסט
        self.url_edit = QtWidgets.QLineEdit()
        self.url_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #2b4c7e;
                border-radius: 15px;
                padding: 10px;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #1a73e8;
            }
        """)
        self.url_edit.textChanged.connect(self.on_text_changed)
        self.url_edit.returnPressed.connect(self.convert_image)
        self.layout.addWidget(self.url_edit)

        # כפתורים
        # כפתור עיון
        browse_container = QHBoxLayout()
        self.add_files_button = QPushButton('עיון', self)
        self.add_files_button.setStyleSheet(button_style)
        self.add_files_button.setFixedSize(80, 30)
        self.add_files_button.clicked.connect(self.open_file_dialog)
        browse_container.addStretch(1)
        browse_container.addWidget(self.add_files_button)
        browse_container.addStretch(1)
        self.layout.addLayout(browse_container)

        # כפתור המרה
        convert_container = QHBoxLayout()
        self.convert_btn = QtWidgets.QPushButton("המר")
        self.convert_btn.setEnabled(False)
        self.convert_btn.setStyleSheet(button_style)
        self.convert_btn.setFixedSize(80, 30)
        self.convert_btn.clicked.connect(self.convert_image)
        convert_container.addStretch(1)
        convert_container.addWidget(self.convert_btn)
        convert_container.addStretch(1)
        self.layout.addLayout(convert_container)

        # תוויות תוצאה
        success_label_style = """
            QLabel {
                color: #28a745;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                padding: 10px;
                background-color: #e8f5e9;
                border-radius: 10px;
            }
        """

        self.nextInFocusChain = QLabel("ההמרה בוצעה בהצלחה!")
        self.nextInFocusChain.setVisible(False)
        self.nextInFocusChain.setAlignment(Qt.AlignCenter)
        self.nextInFocusChain.setStyleSheet(success_label_style)
        self.layout.addWidget(self.nextInFocusChain)
        
        # כפתור העתקה
        copy_container = QHBoxLayout()
        self.copy_btn = QtWidgets.QPushButton("העתק")
        self.copy_btn.setEnabled(False)
        self.copy_btn.setStyleSheet(button_style)
        self.copy_btn.setFixedSize(80, 30)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        copy_container.addStretch(1)
        copy_container.addWidget(self.copy_btn)
        copy_container.addStretch(1)
        self.layout.addLayout(copy_container)

        # תווית אישור העתקה
        self.cop = QLabel("הטקסט הועתק ללוח, ניתן להדביקו במסמך")  # הוספת התווית החסרה
        self.cop.setVisible(False)
        self.cop.setAlignment(Qt.AlignCenter)
        self.cop.setStyleSheet(success_label_style)
        self.layout.addWidget(self.cop)        

        # כפתור המרה חדשה
        new_convert_container = QHBoxLayout()
        self.convert_new_button = QPushButton('המרה חדשה', self)
        self.convert_new_button.setVisible(False)
        self.convert_new_button.setStyleSheet(button_style)
        self.convert_new_button.setFixedSize(100, 30)
        self.convert_new_button.clicked.connect(self.reset_for_new_convert)
        new_convert_container.addStretch(1)
        new_convert_container.addWidget(self.convert_new_button)
        new_convert_container.addStretch(1)
        self.layout.addLayout(new_convert_container)

        self.setAcceptDrops(True)
        self.img_data = None
        self.image_files = []

    def on_text_changed(self):
        text = self.url_edit.text().strip()
        if text.startswith("file:///"):
            text = text[8:]  # הסרת "file:///"
            self.url_edit.setText(text)  # עדכון השדה לאחר התיקון

        if os.path.exists(text):  # בדיקת קובץ מקומי
            self.label.setText("התמונה נטענה בהצלחה!")
            self.convert_btn.setEnabled(True)
        elif text.lower().startswith("http://") or text.lower().startswith("https://"):
            try:
                req = urllib.request.Request(text, method="HEAD")  # שליחה רק של בקשת HEAD לבדיקה
                urllib.request.urlopen(req)
                self.label.setText("הקישור תקין ונטען בהצלחה!")
                self.convert_btn.setEnabled(True)
            except Exception:
                self.label.setText("לא ניתן לפתוח את הקישור, ודא שהוא תקין")
                self.convert_btn.setEnabled(False)
        else:
            self.label.setText("הנתיב שסיפקת אינו קיים")
            self.convert_btn.setEnabled(False)

    def open_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "בחר קבצי תמונה", "", 
                                                "קבצי תמונה (*.png;*.jpg;*.jpeg;*.svg;*.tif;*.heic;*.heif;*.ico;*.webp;*.tiff;*.gif;*.bmp)")
        if files:
            supported_extensions = ('.png', '.jpg', '.jpeg', '.svg', '.tif', '.tiff', '.heic', '.heif', '.ico', '.webp', '.gif', '.bmp')
            for file in files:
                if file.lower().endswith(supported_extensions):
                    self.image_files.append(file)
                    with open(file, 'rb') as f:
                        self.img_data = f.read()
                    self.label.setText("התמונה נטענה בהצלחה!")
                    self.convert_btn.setEnabled(True)
                else:
                    self.label.setText("הסיומת של הקובץ אינה נתמכת.\nבחר קובץ אחר")

    # פונקציה שמופעלת כשגוררים קובץ לחלון
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    # פונקציה שמופעלת כשמשחררים את הקבצים בחלון
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            supported_extensions = ('.png', '.jpg', '.jpeg', '.svg', '.tif', '.tiff', '.heic', '.heif', '.ico', '.webp', '.gif', '.bmp')
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path and os.path.exists(file_path):
                    if file_path.lower().endswith(supported_extensions):
                        with open(file_path, 'rb') as f:
                            self.img_data = f.read()
                        self.image_files.append(file_path)
                        self.label.setText("התמונה נטענה בהצלחה!")
                        self.convert_btn.setEnabled(True)
                    else:
                        self.label.setText("הסיומת של הקובץ אינה נתמכת.\nבחר קובץ אחר")

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Paste):
            clipboard = QtWidgets.QApplication.clipboard()
            mime_data = clipboard.mimeData()
            # בדיקה אם מדובר בתמונה שהועתקה
            if mime_data.hasImage():
                image = clipboard.image()
                if not image.isNull():
                    buffer = QtCore.QBuffer()
                    buffer.open(QtCore.QBuffer.WriteOnly)
                    image.save(buffer, "PNG")
                    self.img_data = buffer.data().data()
                    self.label.setText("התמונה הודבקה בהצלחה!")
                    self.convert_btn.setEnabled(True)
            else:
                text = clipboard.text().strip().strip('"')
                self.url_edit.setText(text)
            event.accept()

    def convert_image(self):
        path = self.url_edit.text().strip().strip('"')
        if path.startswith("file:///"):  # טיפול בפרוטוקול file:///
            path = path[8:]  # הסרת "file:///"

        if not self.img_data and path:
            if path.lower().startswith("http://") or path.lower().startswith("https://"):
                try:
                    with urllib.request.urlopen(path) as resp:
                        self.img_data = resp.read()
                    self.label.setText("הקישור נטען בהצלחה!")
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "שגיאה", f"לא ניתן לפתוח את הקישור:\n{e}")
                    return
            elif os.path.exists(path):  # בדיקה אם הקובץ קיים
                with open(path, 'rb') as f:
                    self.img_data = f.read()
                self.label.setText("התמונה נטענה בהצלחה!")
            else:
                QtWidgets.QMessageBox.warning(self, "שגיאה", "לא ניתן לאתר קובץ בנתיב שסיפקת, ודא שהנתיב נכון")
                return

        if not self.img_data:
            QtWidgets.QMessageBox.warning(self, "שגיאה", "לא נמצאה תמונה להמרה")
            return

        # זיהוי סוג הקובץ על בסיס הסיומת
        file_extension = "png"  # ברירת מחדל
        if self.image_files:
            file_extension = os.path.splitext(self.image_files[0])[-1].lstrip(".").lower()
        elif path:
            file_extension = os.path.splitext(path)[-1].lstrip(".").lower()

        encoded = base64.b64encode(self.img_data).decode('utf-8')
        self.html_code = f'<img src="data:image/{file_extension};base64,{encoded}" >'
        self.copy_btn.setEnabled(True)
        self.nextInFocusChain.setVisible(True)

    def copy_to_clipboard(self):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.html_code)
        self.cop.setVisible(True)
        self.show_post_convert_buttons()

    # פונקציה להצגת כפתורים אחרי ההמרה
    def show_post_convert_buttons(self):
        self.add_files_button.setEnabled(True)
        self.convert_btn.setEnabled(False)
        self.convert_new_button.setVisible(True)

    # פונקציה לאיפוס עבור המרת קבצים חדשים
    def reset_for_new_convert(self):
        self.img_data = None
        self.image_files = []
        self.label.setText("גרור ושחרר קבצי תמונה")
        self.convert_btn.setEnabled(False)
        self.convert_new_button.setVisible(False)
        self.nextInFocusChain.setVisible(False)
        self.copy_btn.setEnabled(False)
        self.cop.setVisible(False)
        self.url_edit.clear()

    # פונקציה לטעינת אייקון ממחרוזת Base64
    def load_icon_from_base64(self, base64_string):
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(base64_string))
        return QIcon(pixmap)

# ==========================================
# Script 10: תיקון שגיאות נפוצות (11 לשעבר)
# ==========================================

class TextCleanerApp(QWidget):
    changes_made = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.file_path = ""
        self.originalText = ""
        self.setWindowTitle("תיקון שגיאות נפוצות")
        self.setWindowIcon(self.load_icon_from_base64(icon_base64))
        self.setLayoutDirection(Qt.RightToLeft)
        #self.setGeometry(100, 100, 500, 500)
        self.setFixedWidth(600)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        explanation = QLabel(
            "שים לב!\n\n"
            "התוכנה תיקון שגיאות נפוצות בטקסט.\n"
            "סמן את האפשרויות הרצויות ולחץ על 'הרץ כעת'.\n"
            "ניתן לבטל את השינוי האחרון באמצעות הכפתור 'בטל שינוי אחרון'."
        )
        explanation.setStyleSheet("""
            QLabel {
                color: #8B0000;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                padding: 20px;
                background-color: #FFE4E1;
                border: 2px solid #CD5C5C;
                border-radius: 15px;
                font-weight: bold;
            }
        """)
        explanation.setAlignment(Qt.AlignCenter)
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        # כפתורי בחירת הכל/ביטול הכל
        button_container = QHBoxLayout()
        
        self.selectAllBtn = QPushButton("בחר הכל")
        self.selectAllBtn.clicked.connect(self.selectAll)
        self.selectAllBtn.setStyleSheet("""
            QPushButton {
                border-radius: 15px;
                padding: 5px;
                background-color: #eaeaea;
                color: black;
                font-weight: bold;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                min-height: 30px;
                max-height: 30px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #b7b5b5;
            }
            QPushButton:pressed {
                background-color: #a0a0a0;
            }
        """)
        
        self.deselectAllBtn = QPushButton("בטל הכל")
        self.deselectAllBtn.clicked.connect(self.deselectAll)
        self.deselectAllBtn.setStyleSheet(self.selectAllBtn.styleSheet())
        
        button_container.addStretch(1)
        button_container.addWidget(self.selectAllBtn)
        button_container.addWidget(self.deselectAllBtn)
        button_container.addStretch(1)
        layout.addLayout(button_container)

        checkbox_style = """
            QCheckBox {
                color: #1a365d;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                padding: 5px;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #2b4c7e;
                border-radius: 5px;
            }
            QCheckBox::indicator:unchecked {
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #2b4c7e;
                image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath fill='white' d='M3.5 8.5l3 3 6-6-1-1-5 5-2-2z'/%3E%3C/svg%3E");
            }
        """
        # תיבות סימון לאפשרויות שונות
        self.checkBoxes = {
            "remove_empty_lines": QCheckBox("מחיקת שורות ריקות"),
            "remove_double_spaces": QCheckBox("מחיקת רווחים כפולים"),
            "remove_spaces_before": QCheckBox("\u202Bמחיקת רווחים לפני - . , : ) ]"),
            "remove_spaces_after": QCheckBox("\u202Bמחיקת רווחים אחרי - [ ("),
            "remove_spaces_around_newlines": QCheckBox("מחיקת רווחים לפני ואחרי אנטר"),
            "replace_double_quotes": QCheckBox("החלפת 2 גרשים בודדים בגרשיים"),
            "normalize_quotes": QCheckBox("המרת גרשיים מוזרים לגרשיים רגילים"),
        }

        # הוספת תיבות הסימון לממשק
        checkbox_container = QVBoxLayout()
        for checkbox in self.checkBoxes.values():
            checkbox.setStyleSheet(checkbox_style)
            checkbox.setChecked(True)
            checkbox_container.addWidget(checkbox)
        layout.addLayout(checkbox_container)

        # כפתורי הפעלה וביטול
        action_buttons_container = QVBoxLayout()
        
        self.cleanBtn = QPushButton("הרץ כעת")
        self.cleanBtn.clicked.connect(self.runCleanText)
        self.cleanBtn.setStyleSheet("""
            QPushButton {
                border-radius: 15px;
                padding: 5px;
                background-color: #4CAF50;  /* ירוק */
                color: white;
                font-weight: bold;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                min-height: 30px;
                max-height: 30px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        self.undoBtn = QPushButton("בטל שינוי אחרון")
        self.undoBtn.clicked.connect(self.undoChanges)
        self.undoBtn.setEnabled(False)
        self.undoBtn.setStyleSheet("""
            QPushButton {
                border-radius: 15px;
                padding: 5px;
                background-color: #f44336;  /* אדום */
                color: white;
                font-weight: bold;
                font-family: "Segoe UI", Arial;
                font-size: 24px;
                min-height: 30px;
                max-height: 30px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c41810;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        action_buttons_container.addWidget(self.cleanBtn, alignment=Qt.AlignCenter)
        action_buttons_container.addWidget(self.undoBtn, alignment=Qt.AlignCenter)
        layout.addLayout(action_buttons_container)

        layout.addStretch()

        self.setLayout(layout)


    def set_file_path(self, path):
        """מקבלת את נתיב הקובץ מהחלון הראשי"""
        self.file_path = path

    def runCleanText(self):
        """הפעלת פונקציית הניקוי"""
        if not self.file_path:
            QMessageBox.warning(self, "שגיאה", "נא לבחור קובץ תחילה")
            return
        self.cleanText()

    def cleanText(self):
        """פונקציית הניקוי העיקרית"""
        try:
            # קריאת הקובץ
            with open(self.file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            # שמירת הטקסט המקורי לצורך ביטול
            self.originalText = text
            self.undoBtn.setEnabled(True)
            
            # ביצוע כל הפעולות שנבחרו
            if self.checkBoxes["remove_empty_lines"].isChecked():
                text = re.sub(r'\n\s*\n', '\n', text)
            
            if self.checkBoxes["remove_double_spaces"].isChecked():
                text = re.sub(r' +', ' ', text)
            
            if self.checkBoxes["remove_spaces_before"].isChecked():
                text = re.sub(r'\s+([)\],.:])', r'\1', text)
            
            if self.checkBoxes["remove_spaces_after"].isChecked():
                text = re.sub(r'([\[(])\s+', r'\1', text)
            
            if self.checkBoxes["remove_spaces_around_newlines"].isChecked():
                text = re.sub(r'\s*\n\s*', '\n', text)
            
            if self.checkBoxes["replace_double_quotes"].isChecked():
                text = text.replace("''", '"').replace("``", '"').replace("''", '"')
            
            if self.checkBoxes["normalize_quotes"].isChecked():
                text = text.replace(""", '"').replace(""", '"').replace("'", "'").replace("'", "'").replace("„", '"')
            
            # מחיקת רווחים בסוף הקובץ
            text = text.rstrip()

            # בדיקה אם היו שינויים
            if text == self.originalText:
                QMessageBox.information(self, "שינויי טקסט", "אין מה להחליף בקובץ זה.")
                return

            # שמירת השינויים
            with open(self.file_path, 'w', encoding='utf-8') as file:
                file.write(text)
            
            QMessageBox.information(self, "שינויי טקסט", "השינויים בוצעו בהצלחה.")
            self.changes_made.emit()

        except FileNotFoundError:
            QMessageBox.critical(self, "שגיאה", "הקובץ לא נמצא")
        except UnicodeDecodeError:
            QMessageBox.critical(self, "שגיאה", "קידוד הקובץ אינו נתמך. יש להשתמש בקידוד UTF-8.")
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בעיבוד הקובץ: {str(e)}")
    
    def selectAll(self):
        """בחירת כל האפשרויות"""
        for checkbox in self.checkBoxes.values():
            checkbox.setChecked(True)
    
    def deselectAll(self):
        """ביטול כל האפשרויות"""
        for checkbox in self.checkBoxes.values():
            checkbox.setChecked(False)
    
    def undoChanges(self):
        """ביטול השינוי האחרון"""
        if not self.file_path or not self.originalText:
            return
            
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                file.write(self.originalText)
            QMessageBox.information(self, "ביטול שינויים", "השינויים בוטלו בהצלחה.")
            self.changes_made.emit()
            self.undoBtn.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בביטול השינויים: {str(e)}")

    def load_icon_from_base64(self, base64_string):
        """טעינת אייקון מקידוד Base64"""
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(base64_string))
        return QIcon(pixmap)

# ==========================================
# Main Menu: תפריט ראשי ופונקציות מרכזיות
# ==========================================
class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.document_history = []
        self.redo_history = []        
        self.current_file_path = ""
        self.current_index = -1
        self.current_content = "" 
        self.last_processor_title = ""
        self.current_version = "2.0.0"
        self._frozen = getattr(sys, 'frozen', False)
        
        if self._frozen:
            print(f"Running as compiled executable, version: {self.current_version}")
        else:
            print(f"Running in Python environment, version: {self.current_version}")
        self.navigation_updated = False
        self.text_display = QTextBrowser()
        self.navigation_loader = None
        QApplication.instance().main_window = self

                # ניסיון לטעון את הגופן
        if not self.load_temp_font():
            # אם נכשל, שימוש בגופן חלופי
            fallback_style = """
                QTextBrowser {
                    font-family: "David CLM", "Times New Roman", Arial;
                    font-size: 18px;
                }
            """
            self.text_display.setStyleSheet(fallback_style)

        
        # הגדרת החלון
        self.setWindowTitle("עריכת ספרי דיקטה עבור אוצריא")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setWindowIcon(self.load_icon_from_base64(icon_base64))

        # חישוב גודל החלון באופן דינמי בהתאם לגודל המסך
        screen = QApplication.primaryScreen().geometry()
        window_width = int(screen.width() * 0.8)  
        window_height = int(screen.height() * 0.8)  
        self.setGeometry(100, 50, window_width, window_height)

        self.create_side_menu()

        # יצירת תצוגת הטקסט
        self.text_display = QTextBrowser() 
        self.text_display.setReadOnly(False)
        self.text_display.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.text_display.document().setDefaultTextOption(QTextOption(Qt.AlignmentFlag.AlignRight))
        self.text_display.setInputMethodHints(Qt.ImhHiddenText | Qt.ImhPreferNumbers | Qt.ImhNoAutoUppercase)
        self.text_display.setInputMethodHints(Qt.InputMethodHint.ImhNone)
        #self.text_display.textChanged.connect(self.on_text_changed)

        base_font = QFont('"Frank Ruehl CLM","Segoe UI"', 18)
        
        self.text_display.setFont(base_font)
    
        self.text_display.setStyleSheet("""
                QTextBrowser {
                    background-color: transparent;
                    white-space: pre-line;
                    border: 2px solid black;
                    border-radius: 15px;
                    padding: 20px 40px;
                    text-align: right;
                }
        """)
    
         
        self.editing_buttons = []
         # אתחול ממשק המשתמש
        self.init_ui()       

        if sys.platform == 'win32':
            QtWin.setCurrentProcessExplicitAppUserModelID(myappid)

        # בדיקת עדכונים אוטומטית בהפעלה
        QTimer.singleShot(3000, self.check_for_updates)



    def load_temp_font(self):
        try:
            # הנתיב לגופן באוצריא
            font_path = r"C:\Program Files\WindowsApps\sivan22.Otzaria_0.2.3.0_x64__r8w7chw81rmdt\data\flutter_assets\fonts\FrankRuehlCLM-Medium.ttf"
            
            # טעינה זמנית של הגופן
            font_id = QFontDatabase.addApplicationFont(font_path)
            
            if font_id != -1:

                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                print(f"הגופן {font_family} נטען בהצלחה")
                
                # הגדרת הגופן לתצוגה
                font = QFont(font_family, 18)
                self.text_display.setFont(font)
                return True
            else:
                print("שגיאה בטעינת הגופן")
                return False
                
        except Exception as e:
            print(f"שגיאה בטעינת הגופן: {str(e)}")
            return False
          
    def check_for_updates(self, silent=True):
        """
        בדיקת עדכונים חדשים
        """
        self.status_label.setText("בודק עדכונים...")
        self.update_checker = UpdateChecker(self.current_version)

        # חיבור הסיגנלים
        self.update_checker.update_available.connect(self.handle_update_available)
        self.update_checker.no_update.connect(self.handle_no_update)
        self.update_checker.error.connect(lambda msg: self.handle_update_error(msg, silent))

        self.update_checker.start()

    def handle_no_update(self):
        """טיפול במקרה שאין עדכון"""
        self.status_label.setText("התוכנה מעודכנת")  

    def handle_update_error(self, error_msg, silent=False):
        """טיפול בשגיאות בתהליך העדכון"""
        if not silent:
            QMessageBox.warning(
                self,
                "שגיאה",
                error_msg
            )
        self.status_label.setText("שגיאה בבדיקת עדכונים")

    def init_ui(self):
        """אתחול ממשק המשתמש"""
        # יצירת מיכל ראשי
        main_container = QWidget()
        main_layout = QHBoxLayout(main_container)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # מיכל ימני לכפתורים
        right_container = QWidget()
        right_container.setFixedWidth(300)
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # יצירת כפתורי הגריד בתוך המיכל הימני
        buttons_grid_widget = QWidget()
        buttons_grid_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        grid_layout = QGridLayout(buttons_grid_widget)
        grid_layout.setSpacing(5)

        # יצירת כפתורי תפריט בגריד
        button_info = [
            ("1\nיצירת כותרות לאוצריא", self.open_create_headers_otzria),
            ("2\nיצירת כותרות לאותיות בודדות", self.open_create_single_letter_headers),
            ("3\nשינוי רמת כותרת", self.open_change_heading_level),
            ("4\nטיפול בתחילת וסוף קטעים", self.open_emphasize_and_punctuate),
            ("5\nיצירת כותרות לעמוד ב", self.open_create_page_b_headers),
            ("6\nהחלפת כותרות לעמוד ב", self.open_replace_page_b_headers),
            ("7\nבדיקת שגיאות", self.open_check_heading_errors_original),
            ("8\n בדיקת שגיאות לספרים על השס", self.open_check_heading_errors_custom),
            ("9\nהמרת תמונה לטקסט", self.open_Image_To_Html_App),
            ("10\nתיקון שגיאות נפוצות", self.open_Text_Cleaner_App)
        ]

        # הוספת הכפתורים לגריד
        for i, (text, func) in enumerate(button_info):
            button = QPushButton(text)
            button.setFixedSize(250, 70)
            button.clicked.connect(func)
            button.setStyleSheet("""
                QPushButton {
                    border-radius: 30px;
                    padding: 10px;
                    margin: 5;
                    background-color: #eaeaea;
                    color: black;
                    font-weight: bold;
                    font-family: "Segoe UI", Arial;
                    font-size: 8.5pt;
                }
                QPushButton:hover {
                    background-color: #b7b5b5;
                }
            """)
            grid_layout.addWidget(button, i, 0)

        # מיכל לתצוגת טקסט ותפריט
        text_container = QWidget()
        text_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(15, 15, 0, 20)

        # יצירת הכפתורים העליונים
        self.menu_button = QPushButton("☰")
        self.menu_button.setStyleSheet("""
            QPushButton {
                font-size: 30px;
                padding: 5px;
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #eaeaea;
            }
        """)
        self.menu_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.menu_button.clicked.connect(self.toggle_side_menu)
        self.menu_button.setFixedSize(60, 60)
        self.menu_button.setToolTip("תפריט")

        # יצירת כפתורי פעולה
        self.refresh_button = QPushButton("🔄")  # או "⟳"
        self.refresh_button.setStyleSheet("font-weight: bold; font-size: 14pt; padding: 5px;")

        self.refresh_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.refresh_button.clicked.connect(self.refresh_file)
        self.refresh_button.setFixedSize(60, 60)
        self.refresh_button.setToolTip("ריענון")
        
        self.undo_button = QPushButton("⟲")
        self.undo_button.setStyleSheet("font-weight: bold; font-size: 14pt; padding: 5px;")
        self.undo_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.undo_button.clicked.connect(self.undo_action)
        self.undo_button.setFixedSize(60, 60)
        self.undo_button.setToolTip("בטל")
        self.undo_button.setEnabled(False)

        self.redo_button = QPushButton("⟳")
        self.redo_button.setStyleSheet("font-weight: bold; font-size: 14pt; padding: 5px;")
        self.redo_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.redo_button.clicked.connect(self.redo_action)
        self.redo_button.setFixedSize(60, 60)
        self.redo_button.setToolTip("חזור")
        self.redo_button.setEnabled(False)

        self.save_button = QPushButton("🖫")
        self.save_button.setStyleSheet("font-weight: bold; font-size: 14pt; padding: 5px;")
        self.save_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.save_button.clicked.connect(self.save_file)
        self.save_button.setFixedSize(60, 60)
        self.save_button.setToolTip("שמור")
        self.save_button.setEnabled(False)

        # כפתור הוספת קובץ
        add_file_button = QPushButton("הוסף קובץ")
        add_file_button.setFixedSize(150, 60)
        add_file_button.setCursor(QCursor(Qt.PointingHandCursor))
        add_file_button.setStyleSheet("""
            QPushButton {
                border-radius: 20px;
                padding: 5px;
                background-color: #eaeaea;
                color: black;
                font-weight: bold;
                font-size: 8.5pt;
            }
            QPushButton:hover {
                background-color: #b7b5b5;
            }
        """)
        add_file_button.clicked.connect(self.select_file)

        # כפתור עריכה בפנקס רשימות
        edit_in_notepad_button = QPushButton("ערוך בפנקס רשימות")
        edit_in_notepad_button.setFixedSize(200, 60)
        edit_in_notepad_button.setCursor(QCursor(Qt.PointingHandCursor))
        edit_in_notepad_button.setStyleSheet("""
            QPushButton {
                border-radius: 20px;
                padding: 5px;
                background-color: #eaeaea;
                color: black;
                font-weight: bold;
                font-size: 8.5pt;
            }
            QPushButton:hover {
                background-color: #b7b5b5;
            }
        """)
        edit_in_notepad_button.clicked.connect(self.open_in_notepad)

        # תווית סטטוס
        self.status_label = QLabel("לא בוצעו עדיין פעולות")
        self.status_label.setStyleSheet("""
            color: #666666;
            font-size: 24px;
            padding: 5px 15px;
            background-color: transparent;
            border-radius: 10px;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)

        # יצירת מיכל לכפתורי פעולה
        action_buttons_container = QWidget()
        action_buttons_layout = QHBoxLayout(action_buttons_container)
        action_buttons_layout.setContentsMargins(10, 10, 10, 10)

        # הוספת הכפתורים ללייאאוט
        action_buttons_layout.addWidget(self.menu_button)
        action_buttons_layout.addWidget(add_file_button)
        action_buttons_layout.addWidget(edit_in_notepad_button)
        action_buttons_layout.addStretch(1)
        action_buttons_layout.addWidget(self.status_label)
        action_buttons_layout.addStretch(1)
        action_buttons_layout.addWidget(self.refresh_button)
        action_buttons_layout.addWidget(self.undo_button)
        action_buttons_layout.addWidget(self.redo_button)
        action_buttons_layout.addWidget(self.save_button)

        # מיכל לתוכן הראשי - תפריט וטקסט
        main_content = QWidget()
        main_content_layout = QVBoxLayout(main_content)
        main_content_layout.setContentsMargins(0, 0, 0, 0)
        main_content_layout.setSpacing(0)

        # יצירת כפתורי עריכה 
        editing_buttons_container = QWidget()
        text_bottom_buttons = QHBoxLayout(editing_buttons_container)
        text_bottom_buttons.setSpacing(10)
        text_bottom_buttons.setContentsMargins(15, 10, 15, 10)

        # הגדרת כפתורי עריכה
        buttons_data = [
            ("הסר", self.remove_formatting),
            ("קטן", self.button1_function),
            ("גדול", self.button2_function),
            ("נטוי", self.button3_function),
            ("דגש", self.button4_function),
            ("H6", self.button5_function),
            ("H5", self.button6_function),
            ("H4", self.button7_function),
            ("H3", self.button8_function),
            ("H2", self.button9_function),
            ("H1", self.button10_function)
        ]

        # סגנון כפתורי עריכה
        button_style = """
            QPushButton {
                border-radius: 15px;
                padding: 6px 12px;
                background-color: #E8F0FE;
                color: #1a365d;
                font-weight: bold;
                font-family: "Segoe UI", Arial;
                font-size: 12pt;
                min-width: 20px;
                min-height: 12px;

                border: 1px solid #c2d3f0;
            }
            QPushButton:hover {
                background-color: #d3e3fc;
            }
            QPushButton:pressed {
                background-color: #bbd1f8;
                padding: 7px 11px 5px 13px;
            }
        """

        # כפתור חיפוש
        search_button_style = """
            QPushButton {
                border-radius: 15px;
                padding: 6px 15px;
                background-color: #e0e0e0;
                color: #333333;
                font-weight: bold;
                font-family: "Segoe UI", Arial;
                font-size: 12pt;
                min-width: 60px;
                min-height: 12px;
                width: 60px;
                height: 20px;
                border: 1px solid #cccccc;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
                padding: 7px 14px 5px 16px;
            }
        """

        # יצירת כפתור החיפוש
        search_button = QPushButton("חיפוש")
        search_button.setFixedSize(100, 60)
        search_button.setStyleSheet(search_button_style)
        search_button.setCursor(QCursor(Qt.PointingHandCursor))
        search_button.clicked.connect(self.open_find_replace)
        search_button.hide()
        
        self.editing_buttons = [search_button]
        
        # הוספת כפתור החיפוש עם מרווח
        text_bottom_buttons.addWidget(search_button)
        text_bottom_buttons.addSpacing(20)

        # יצירת כפתורי העריכה
        for button_text, func in reversed(buttons_data):
            button = QPushButton(button_text)
            button.setFixedSize(80, 60)
            button.setStyleSheet(button_style)
            button.setCursor(QCursor(Qt.PointingHandCursor))
            button.clicked.connect(func)
            button.hide()
            self.editing_buttons.insert(0, button)
            text_bottom_buttons.addWidget(button)

        text_bottom_buttons.addStretch(1)

        # מיכל לתצוגת טקסט
        text_display_container = QWidget()
        text_display_layout = QHBoxLayout(text_display_container)
        text_display_layout.setContentsMargins(20, 5, 5, 20)
        text_display_layout.setSpacing(0)

        # תווית לשם הקובץ (מעל הכל)
        self.file_name_label = QLabel()
        self.file_name_label.setStyleSheet("""
            QLabel {
                color: #1a365d;
                font-family: "Segoe UI", Arial;
                font-size: 30px;
                font-weight: bold;
                padding: 2px;
                margin: 0;
                background-color: transparent;
            }
        """)
        self.file_name_label.setAlignment(Qt.AlignCenter)
        self.file_name_label.hide()

        # מיכל לכל התוכן (כולל תפריט צד וטקסט)
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self.side_menu)
        content_layout.addWidget(self.text_display)

        # מיכל אנכי ראשי שמכיל את התווית והתוכן
        main_display_container = QWidget()
        main_display_layout = QVBoxLayout(main_display_container)
        main_display_layout.setContentsMargins(0, 0, 0, 0)
        main_display_layout.setSpacing(5)
        main_display_layout.addWidget(self.file_name_label)
        main_display_layout.addWidget(content_container)

       # הוספת המיכל הראשי למיכל התצוגה
        text_display_layout.addWidget(main_display_container)

        # סידור סופי של הרכיבים
        main_content_layout.addWidget(action_buttons_container)
        main_content_layout.addWidget(editing_buttons_container)
        main_content_layout.addWidget(text_display_container)

        # סידור כפתורי התפריט הימני
        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.setContentsMargins(10, 20, 10, 20)
        
        about_button = QPushButton("i")
        about_button.setStyleSheet("font-weight: bold; font-size: 12pt;")
        about_button.setCursor(QCursor(Qt.PointingHandCursor))
        about_button.clicked.connect(self.open_about_dialog)
        about_button.setFixedSize(60, 60)
        
        update_button = QPushButton("⭳")
        update_button.setStyleSheet("font-weight: bold; font-size: 14pt;")
        update_button.setCursor(QCursor(Qt.PointingHandCursor))
        update_button.clicked.connect(self.check_for_updates)
        update_button.setFixedSize(60, 60)
        update_button.setToolTip("עדכונים")

        self.edit_button = QPushButton("✍")
        self.edit_button.setStyleSheet("font-weight: bold; font-size: 14pt;")
        self.edit_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.edit_button.setFixedSize(60, 60)
        self.edit_button.setToolTip("עריכה")
        self.edit_button.clicked.connect(self.edit_text)

        bottom_buttons_layout.addSpacing(10)
        bottom_buttons_layout.addWidget(about_button)
        bottom_buttons_layout.addWidget(update_button)
        bottom_buttons_layout.addSpacing(120)
        bottom_buttons_layout.addWidget(self.edit_button)
        bottom_buttons_layout.addStretch()

        # סידור כפתורי התפריט הימני
        right_layout.addWidget(buttons_grid_widget)
        right_layout.addLayout(bottom_buttons_layout)

        # הוספה למיכל הראשי
        main_layout.addWidget(right_container)
        main_layout.addWidget(main_content)

        self.setCentralWidget(main_container)



    def create_side_menu(self):
        """יצירת תפריט הצד לניווט בכותרות"""
        self.side_menu = QWidget()
        self.side_menu.setFixedWidth(0)
        

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("נווט")
        title_label.setLayoutDirection(Qt.RightToLeft)
        
        text_option = QTextOption()
        text_option.setAlignment(Qt.AlignRight)
        

        document = QTextDocument()
        document.setDefaultTextOption(text_option)
        title_label.setStyleSheet("""
            QLabel {
                font-family: "Segoe UI", Arial;
                font-size: 30px;
                font-weight: bold;
                color: #333333;
                padding: 5px 20px 5px 0px;  /* top, right, bottom, left */
                background-color: transparent;
            }
        """)
        
        layout.addWidget(title_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        
        self.headers_widget = QWidget()
        self.headers_widget.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
        """)
        self.headers_layout = QVBoxLayout(self.headers_widget)
        self.headers_layout.setContentsMargins(0, 0, 0, 0)
        self.headers_layout.setSpacing(4)
        
        scroll_area.setWidget(self.headers_widget)
        layout.addWidget(scroll_area)
        
        # עיצוב כללי לתפריט
        self.side_menu.setStyleSheet("""
            QWidget#side_menu {
                background-color: transparent;
                border: 2px solid black;
                border-radius: 15px;
            }
            QPushButton {
                text-align: right;
                padding: 8px 15px;
                background-color: transparent;
                border: none;
                font-family: "Segoe UI", Arial;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: rgba(232, 240, 254, 0.7);
            }
        """)
        self.side_menu.setObjectName("side_menu")
        
        self.side_menu.setLayout(layout)
        self.side_menu.hide()

    def update_navigation_menu(self):
        """עדכון תפריט הניווט פעם אחת בלבד"""
        if self.navigation_updated or self.navigation_loader is not None:  
            return
            
        try:
            # ניקוי הפריטים הקיימים
            for i in reversed(range(self.headers_layout.count())):
                widget = self.headers_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            self.navigation_loader = NavigationLoader(self.text_display.document())
            self.navigation_loader.finished.connect(self.on_navigation_loaded)
            self.navigation_loader.start()
            
        except Exception as e:
            print(f"שגיאה בעדכון תפריט ניווט: {str(e)}")


    def remove_formatting(self):
        """הסרת עיצוב מהטקסט המסומן"""
        cursor = self.text_display.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            self.apply_tag_to_file("remove", selected_text)
                
    def button1_function(self):
        """הקטנת הטקסט המסומן"""
        cursor = self.text_display.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            self.apply_tag_to_file('small', selected_text)

    def button2_function(self):
        """הגדלת הטקסט המסומן"""
        cursor = self.text_display.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            self.apply_tag_to_file('big"', selected_text)
            
    def button3_function(self):
        """הפיכת הטקסט לנטוי"""
        cursor = self.text_display.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            self.apply_tag_to_file('i', selected_text)

    def button4_function(self):
        """הדגשת הטקסט"""
        cursor = self.text_display.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            self.apply_tag_to_file('b', selected_text)

    def button5_function(self):
        """הוספת כותרת H6"""
        cursor = self.text_display.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            self.apply_tag_to_file('h6', selected_text)

    def button6_function(self):
        """הוספת כותרת H5"""
        cursor = self.text_display.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            self.apply_tag_to_file('h5', selected_text)

    def button7_function(self):
        """הוספת כותרת H4"""
        cursor = self.text_display.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            self.apply_tag_to_file('h4', selected_text)

    def button8_function(self):
        """הוספת כותרת H3"""
        cursor = self.text_display.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            self.apply_tag_to_file('h3', selected_text)

    def button9_function(self):
        """הוספת כותרת H2"""
        cursor = self.text_display.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            self.apply_tag_to_file('h2', selected_text)

    def button10_function(self):
        """הוספת כותרת H1"""
        cursor = self.text_display.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            self.apply_tag_to_file('h1', selected_text)
            

    def on_navigation_loaded(self, result):
        """מטפל בתוצאות טעינת הכותרות"""
        try:
            if not result['success']:
                return

            # יצירת הכפתורים עבור כל כותרת
            for header in result['headers']:
                button = QPushButton(header['text'])
                button.setStyleSheet(f"""
                    QPushButton {{
                        font-size: {24 - header['level']}px;
                        font-weight: {700 if header['level'] <= 2 else 400};
                        color: #1a365d;
                        padding-right: {(header['level']-1) * 20}px;
                        text-align: right;
                    }}
                """)
                button.setCursor(Qt.CursorShape.PointingHandCursor)
                
                position = header['position']
                button.clicked.connect(lambda checked, pos=position: self.scroll_to_header(pos))
                
                self.headers_layout.addWidget(button)

            # הוספת מרווח בסוף
            self.headers_layout.addStretch()
            self.navigation_updated = True  # סימון שהניווט עודכן
            self.navigation_loader = None  # איפוס ה-loader

        except Exception as e:
            print(f"שגיאה בטיפול בתוצאות הניווט: {str(e)}")



    def scroll_to_header(self, position):
        """גלילה למיקום המדויק של הכותרת"""
        cursor = self.text_display.textCursor()
        cursor.setPosition(position)
        self.text_display.setTextCursor(cursor)
        self.text_display.ensureCursorVisible()

    def toggle_side_menu(self):
        """הצגה/הסתרה של תפריט הצד"""
        try:
            if self.side_menu.isHidden():
                self.side_menu.setFixedWidth(300)
                self.side_menu.show()
            else:
                self.side_menu.hide()
                self.side_menu.setFixedWidth(0)
        except Exception as e:
            print(f"Error in toggle_side_menu: {e}")
        
    def apply_tag_to_file(self, tag_name, selected_text):
        """פונקציית עזר להחלפת או הוספת תג לקובץ"""
        try:
            # קריאת תוכן הקובץ
            with open(self.current_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            import re
            
            # חיפוש משופר שמזהה גם תגיות מקוננות
            def find_text_with_tags(content, text):
                # מחפש את הטקסט עם כל התגיות שאולי עוטפות אותו
                pattern = f'(?:<[^>]*>)*{re.escape(text)}(?:</[^>]*>)*'
                match = re.search(pattern, content)
                return match

            match = find_text_with_tags(content, selected_text)
            
            if match:
                old_text = match.group(0)  # הטקסט המקורי עם כל התגיות
                
                # יצירת הטקסט החדש בהתאם לסוג התג
                if tag_name == "remove":
                    new_text = selected_text  # הסרת כל העיצוב
                else:
                    # ניקוי התג מתווים לא רצויים
                    clean_tag = tag_name.strip().replace('"', '').replace('\\', '')
                    
                    # שמירה על תגיות קיימות אלא אם זו כותרת
                    if clean_tag.startswith('h'):
                        # כותרות מחליפות את כל העיצוב הקיים
                        new_text = f'<{clean_tag}>{selected_text}</{clean_tag}>'
                    else:
                        # שילוב התג החדש עם התגים הקיימים
                        inner_text = re.sub(r'<[^>]*>|</[^>]*>', '', old_text)  # הסרת תגיות
                        existing_tags = re.findall(r'<([^/>]+)>', old_text)  # מציאת תגיות קיימות
                        
                        # בדיקה אם התג כבר קיים
                        if clean_tag not in existing_tags:
                            new_text = f'<{clean_tag}>{old_text}</{clean_tag}>'
                        else:
                            new_text = old_text  # אם התג כבר קיים, לא נוסיף אותו שוב
                
                # החלפת הטקסט הישן בחדש
                new_content = content.replace(old_text, new_text)
                
                # שמירה לקובץ
                with open(self.current_file_path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                
                # עדכון התצוגה
                self.text_display.setHtml(new_content)
                
                # עדכון היסטוריה
                if tag_name == "remove":
                    action_description = "הסרת עיצוב"
                elif clean_tag in ['big', 'small']:
                    action_description = "שינוי גודל טקסט"
                else:
                    action_description = f"הוספת עיצוב {clean_tag}"
                    
                self._safe_update_history(new_content, action_description)
            
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בעדכון התגית: {str(e)}")
    
#---------------------חיפוש והחלפה----------------
    def open_find_replace(self):
        """פתיחת חלונית חיפוש והחלפה משופרת"""
        if not self.text_display.isReadOnly():
            dialog = QDialog(self)
            dialog.setWindowTitle("חיפוש והחלפה מתקדם")
            dialog.setFixedWidth(700)
            dialog.setMinimumHeight(600)
            dialog.setLayoutDirection(Qt.RightToLeft)
            
            # סגנונות בסיסיים
            label_style = """
                QLabel {
                    color: #1a365d;
                    font-family: "Segoe UI", Arial;
                    font-size: 14px;
                    margin-bottom: 5px;
                }
            """
            
            input_style = """
                QLineEdit, QComboBox {
                    border: 2px solid #2b4c7e;
                    border-radius: 15px;
                    padding: 5px 15px;
                    font-family: "Segoe UI", Arial;
                    font-size: 12px;
                    min-height: 30px;
                    background-color: white;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid #2b4c7e;
                    margin-right: 5px;
                }
            """
            
            button_style = """
                QPushButton {
                    border-radius: 15px;
                    padding: 5px;
                    background-color: #eaeaea;
                    color: black;
                    font-weight: bold;
                    font-family: "Segoe UI", Arial;
                    font-size: 12px;
                    min-height: 30px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #b7b5b5;
                }
                QPushButton:pressed {
                    background-color: #a0a0a0;
                }
            """
            
            checkbox_style = """
                QCheckBox {
                    font-family: "Segoe UI", Arial;
                    font-size: 12px;
                    color: #1a365d;
                }
                QCheckBox::indicator {
                    width: 15px;
                    height: 15px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #2b4c7e;
                    border-radius: 4px;
                    background-color: white;
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #2b4c7e;
                    border-radius: 4px;
                    background-color: #2b4c7e;
                }
            """

            layout = QVBoxLayout()
            layout.setContentsMargins(15, 15, 15, 15)
            layout.setSpacing(15)

            # תיבת הסבר
            help_text = QLabel(
                "עזרה לחיפוש תווים מיוחדים:\n"
                "\\n או \\enter - ירידת שורה\n"
                "\\t - טאב\n"
                "\\s - רווח\n"
                "\\r או \\CR - חזרה לתחילת שורה\n"
                "\\CRLF - ירידת שורה בסגנון Windows"
            )
            help_text.setStyleSheet("""
                QLabel {
                    color: #666666;
                    font-family: "Segoe UI", Arial;
                    font-size: 11px;
                    padding: 10px;
                    background-color: #f5f5f5;
                    border-radius: 5px;
                }
            """)
            help_text.setVisible(False)  # מוסתר כברירת מחדל

            # כפתור עזרה
            help_button = QPushButton("?")
            help_button.setFixedSize(25, 25)
            help_button.setStyleSheet("""
                QPushButton {
                    border-radius: 12px;
                    background-color: #2b4c7e;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1a365d;
                }
            """)
            help_button.clicked.connect(lambda: help_text.setVisible(not help_text.isVisible()))

            # תיבות חיפוש והחלפה
            search_label = QLabel("חפש:")
            search_label.setStyleSheet(label_style)
            self.search_text = QLineEdit()
            self.search_text.setStyleSheet(input_style)
            
            replace_label = QLabel("החלף ב:")
            replace_label.setStyleSheet(label_style)
            self.replace_input = QLineEdit()
            self.replace_input.setStyleSheet(input_style)

            layout.addWidget(search_label)
            layout.addWidget(self.search_text)
            layout.addWidget(replace_label)
            layout.addWidget(self.replace_input)

            # אפשרויות חיפוש
            options_group = QGroupBox("אפשרויות חיפוש")
            options_group.setStyleSheet("""
                QGroupBox {
                    font-family: "Segoe UI", Arial;
                    font-size: 13px;
                    color: #1a365d;
                    border: 2px solid #2b4c7e;
                    border-radius: 15px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
            """)
            
            options_layout = QVBoxLayout()
            
            self.case_sensitive = QCheckBox("התאמת רישיות")
            self.whole_words = QCheckBox("מילים שלמות בלבד")
            self.use_regex = QCheckBox("חיפוש עם ביטויים רגולריים")
            self.include_special = QCheckBox("כולל תווים מיוחדים (\\n, \\t)")
            
            for checkbox in [self.case_sensitive, self.whole_words, self.use_regex, self.include_special]:
                checkbox.setStyleSheet(checkbox_style)
                options_layout.addWidget(checkbox)
            
            options_group.setLayout(options_layout)
            layout.addWidget(options_group)

            # כפתורי פעולה
            button_container = QHBoxLayout()
            
            find_next_btn = QPushButton("חפש הבא")
            find_prev_btn = QPushButton("חפש הקודם")
            replace_btn = QPushButton("החלף")
            replace_all_btn = QPushButton("החלף הכל")
            
            for btn in [find_next_btn, find_prev_btn, replace_btn, replace_all_btn]:
                btn.setStyleSheet(button_style)
                button_container.addWidget(btn)

            layout.addLayout(button_container)

            # חיבור אירועים
            find_next_btn.clicked.connect(lambda: self.find_text(True))
            find_prev_btn.clicked.connect(lambda: self.find_text(False))
            replace_btn.clicked.connect(self.replace_text)
            replace_all_btn.clicked.connect(self.replace_all)
            
            # מקש Enter לחיפוש
            self.search_text.returnPressed.connect(lambda: self.find_text(True))

            # הוספה לממשק
            help_layout = QHBoxLayout()
            help_layout.addStretch()
            help_layout.addWidget(help_button)
            layout.addLayout(help_layout)
            layout.addWidget(help_text)

            dialog.setLayout(layout)
            dialog.show()           

    def find_text(self, forward=True):
        """חיפוש טקסט עם אפשרויות מתקדמות"""
        text = self.search_text.text()
        if not text:
            return

        # ניקוי הדגשות קודמות
        self.text_display.setExtraSelections([])
        
        # קבלת הטקסט המלא
        content = self.text_display.toPlainText()
        search_text = text
        
        # המרת תווים מיוחדים
        if self.include_special.isChecked():
            search_text = text.replace("\\n", "\n",).replace("\\t", "\t").replace("\\r", "\r")
        
        # התאמה לתנאי החיפוש
        if not self.case_sensitive.isChecked():
            content = content.lower()
            search_text = search_text.lower()
        
        # חיפוש רגיל או regex
        if self.use_regex.isChecked():
            try:
                import re
                if forward:
                    matches = list(re.finditer(search_text, content))
                    pos = -1
                    for match in matches:
                        if match.start() > self.text_display.textCursor().position():
                            pos = match.start()
                            length = len(match.group())
                            break
                    if pos == -1 and matches:  # אם לא נמצא אחרי המיקום הנוכחי, נחזור להתחלה
                        pos = matches[0].start()
                        length = len(matches[0].group())
                else:
                    matches = list(re.finditer(search_text, content[:self.text_display.textCursor().position()]))
                    if matches:
                        pos = matches[-1].start()
                        length = len(matches[-1].group())
                    else:
                        pos = -1
            except re.error:
                QMessageBox.warning(self, "שגיאה", "ביטוי רגולרי לא תקין")
                return False
        else:
            # חיפוש רגיל
            if forward:
                pos = content.find(search_text, self.text_display.textCursor().position())
                if pos == -1:  # אם לא נמצא, מנסה מההתחלה
                    pos = content.find(search_text, 0)
            else:
                text_before = content[:self.text_display.textCursor().position()]
                pos = text_before.rfind(search_text)
            length = len(search_text)

        if pos != -1:
            cursor = self.text_display.textCursor()
            cursor.setPosition(pos)
            cursor.setPosition(pos + length, QTextCursor.KeepAnchor)
            self.text_display.setTextCursor(cursor)
            
            # הדגשה
            extra = QTextEdit.ExtraSelection()
            extra.format.setBackground(QColor("#FFD700"))
            extra.format.setForeground(QColor("#000000"))
            extra.cursor = cursor
            self.text_display.setExtraSelections([extra])
            return True
        else:
            QMessageBox.information(self, "חיפוש", "הטקסט לא נמצא")
            return False

    def replace_text(self):
        """החלפת הטקסט המסומן בטקסט חדש"""
        if not self.search_text.text():
            return
            
        replace_with = self.replace_input.text()
        cursor = self.text_display.textCursor()
        
        if cursor.hasSelection():
            cursor.insertText(replace_with)
            self.find_text()  # חיפוש הבא
        else:
            if self.find_text():
                cursor = self.text_display.textCursor()
                cursor.insertText(replace_with)
                self.find_text()  # חיפוש הבא

    def replace_all(self):
        """החלפת כל המופעים של הטקסט"""
        if not self.search_text.text():
            return
            
        search_text = self.search_text.text()
        replace_with = self.replace_input.text()
        content = self.text_display.toPlainText()
        
        if self.include_special.isChecked():
            search_text = search_text.replace("\\n", "\n").replace("\\t", "\t").replace("\\r", "\r")
            replace_with = replace_with.replace("\\n", "\n").replace("\\t", "\t").replace("\\r", "\r")
        
        if not self.case_sensitive.isChecked():
            import re
            content = re.sub(re.escape(search_text), replace_with, content, flags=re.IGNORECASE)
        else:
            content = content.replace(search_text, replace_with)
            
        self.text_display.setPlainText(content)


    def refresh_file(self):
        """ריענון הקובץ הנוכחי"""
        try:
            if not self.current_file_path:
                return
                
            # שמירת המיקום הנוכחי של הסמן
            cursor = self.text_display.textCursor()
            current_position = cursor.position()
            
            # טעינה מחדש של הקובץ
            with open(self.current_file_path, 'r', encoding='utf-8') as file:
                self.original_content = file.read()
            
            # המרת ירידות שורה לתצוגת HTML
            display_content = self.original_content.replace('\n', '<br>')
            
            # עדכון התצוגה
            self.text_display.setHtml(display_content)
            
            # החזרת הסמן למיקום הקודם
            # נצטרך להתאים את המיקום בגלל תגיות ה-HTML
            adjusted_position = current_position
            if '<br>' in display_content[:current_position]:
                # מספר תגיות ה-<br> לפני המיקום הנוכחי
                br_count = display_content[:current_position].count('<br>')
                # התאמת המיקום (כל <br> מוסיף 3 תווים יותר מ-\n)
                adjusted_position = current_position + (br_count * 3)
            
            cursor = self.text_display.textCursor()
            cursor.setPosition(adjusted_position)
            self.text_display.setTextCursor(cursor)
            
            # עדכון תפריט הניווט
            self.navigation_updated = False
            self.update_navigation_menu()
            
            self.status_label.setText("הקובץ רוענן בהצלחה")
            
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בריענון הקובץ: {str(e)}")       
        

    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # קריאת התוכן המקורי
                self.original_content = file.read()

                # עדכון שם הקובץ בתווית
                file_name = os.path.basename(file_path)
                file_name = file_name.rsplit('.', 1)[0]
                self.file_name_label.setText(f"קובץ נוכחי: {file_name}")
                self.file_name_label.setText(f"{file_name}")
                self.file_name_label.show()          
            
                # המרה ל-HTML לתצוגה תוך שמירה על ירידות שורה
                html_content = self.original_content.replace('\n', '<br>')
                self.text_display.setHtml(html_content)
                self.current_file_path = file_path
            
                # שמירת התוכן המקורי בהיסטוריה
                self.document_history = [(self.original_content, "מצב התחלתי")]
                self.current_index = 0
            
                self.navigation_updated = False
                self.update_navigation_menu()
                self.update_buttons_state()

                
        except Exception as e:
                QMessageBox.critical(self, "שגיאה", f"שגיאה בטעינת הקובץ: {str(e)}")

    def save_file(self):
        if not self.current_file_path:
            return
                
        try:
            # לקחת את התוכן כמו שהוא מתוך הקובץ הנוכחי
            with open(self.current_file_path, 'r', encoding='utf-8') as file:
                 content = file.read()
                 
            with open(self.current_file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            self.status_label.setText("הקובץ נשמר בהצלחה")
                    
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בשמירת הקובץ: {str(e)}")

    def refresh_after_processing(self):
        try:
            # קריאת התוכן המעודכן מהקובץ
            with open(self.current_file_path, 'r', encoding='utf-8') as file:
                self.original_content = file.read()
        
            # המרה ל-HTML לתצוגה תוך שמירה על ירידות שורה
            html_content = self.original_content.replace('\n', '<br>')
            self.text_display.setHtml(html_content)
        
            # עדכון הסטטוס בהתאם לחלון האחרון שהיה פעיל
            if hasattr(self, 'last_processor_title') and self.last_processor_title:
                action_description = self._get_action_description(self.last_processor_title)
                self.status_label.setText(action_description)
            
                # עדכון ההיסטוריה עם התוכן המקורי (לא ה-HTML)
                self._safe_update_history(self.original_content, action_description)
        
                # ניקוי שם החלון האחרון כדי למנוע כפילויות
                self.last_processor_title = None
                
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בעדכון התצוגה: {str(e)}")

            
    def edit_text(self):
        """פונקציה לניהול מצב העריכה"""
        is_editing_mode = self.editing_buttons[0].isHidden()
        self.text_display.setReadOnly(not is_editing_mode)
        
        if is_editing_mode:
            # עיצוב למצב עריכה
            self.text_display.setStyleSheet("""
                QTextBrowser {
                    background-color: white;
                    border: 2px solid #2b4c7e;
                    border-radius: 15px;
                    padding: 20px 40px;
                    text-align: right; /* Align text to the right */
                }
            """)
            
            self.text_display.textChanged.connect(self.on_text_edit_changed)
            self.edit_button.setText("✗")
            self.edit_button.setToolTip("סגור מצב עריכה")
            self.status_label.setText("מצב עריכה פעיל")
            
            
            for button in self.editing_buttons:
                button.show()
        else:
            # עיצוב למצב תצוגה
            self.text_display.setStyleSheet("""
                QTextBrowser {
                    background-color: transparent;
                    border: 2px solid black;
                    border-radius: 15px;
                    padding: 20px 40px;
                    text-align: right; /* Align text to the right */
                }
            """)
            
            self.edit_button.setText("✍")
            self.edit_button.setToolTip("עריכה")
            self.status_label.setText("מצב תצוגה בלבד")
            
            for button in self.editing_buttons:
                button.hide()
        
        self.update_buttons_state()



    def setup_editor_shortcuts(self):
        """הגדרת קיצורי מקשים לעורך הטקסט"""
        # מאפשרים Undo/Redo בעורך עצמו
        self.text_display.setUndoRedoEnabled(True)
        
        # חיבור הפעולות לאירועים שלנו
        self.text_display.undoAvailable.connect(self.on_undo_available)
        self.text_display.redoAvailable.connect(self.on_redo_available)
        
        # הגדרת הפעולות הסטנדרטיות של העורך
        self.text_display.createStandardContextMenu()

    def on_undo_available(self, available):
        """מופעל כשמשתנה האפשרות לבטל פעולה"""
        if available:
            # נעדכן את הסטטוס שיש אפשרות לבטל
            self.status_label.setText("ניתן לבטל שינוי (Ctrl+Z)")
        self.update_buttons_state()

    def on_redo_available(self, available):
        """מופעל כשמשתנה האפשרות לחזור על פעולה"""
        if available:
            # נעדכן את הסטטוס שיש אפשרות לחזור
            self.status_label.setText("ניתן לחזור על שינוי (Ctrl+Y)")
        self.update_buttons_state()        


    def on_text_edit_changed(self):
        """מטפל בשינויי תוכן בזמן אמת"""
        if not self.current_file_path or self.text_display.isReadOnly():
            return
    
        try:
            # נחסום זמנית את האירועים כדי למנוע לולאה אינסופית
            self.text_display.blockSignals(True)
        
            # נשמור את התוכן כמו שהוא כרגע בקובץ - בדיוק כמו ב-refresh_after_processing
            with open(self.current_file_path, 'r', encoding='utf-8') as file:
                current_content = file.read()
        
            # שמירת התוכן החדש לקובץ
            with open(self.current_file_path, 'w', encoding='utf-8') as file:
                file.write(current_content)
            
            # עדכון ההיסטוריה עם התוכן החדש
            self._safe_update_history(current_content, "עריכת טקסט")
        
            # מאפשרים שוב את האירועים
            self.text_display.blockSignals(False)
    
        except Exception as e:
            print(f"שגיאה בשמירת השינויים: {str(e)}")
            # מאפשרים שוב את האירועים גם במקרה של שגיאה
            self.text_display.blockSignals(False)

    def _safe_update_history(self, new_content, description):
        """שמירת מצב בהיסטוריה"""
        try:
            # נשווה עם המצב הנוכחי בהיסטוריה
            if len(self.document_history) > 0:
                current_state = self.document_history[self.current_index][0]
            else:
                current_state = ""
            
            # רק אם יש שינוי בתוכן, נוסיף לרשימה
            if new_content != current_state:
                # מחיקת כל ההיסטוריה אחרי המיקום הנוכחי
                self.document_history = self.document_history[:self.current_index + 1]
                # הוספת המצב החדש
                self.document_history.append((new_content, description))
                self.current_index = len(self.document_history) - 1
            
            self.update_buttons_state()
        
        except Exception as e:
            print(f"שגיאה בעדכון ההיסטוריה: {str(e)}")
            
    def process_text(self, processor_widget):
        if not self.current_file_path:
            QMessageBox.warning(self, "שגיאה", "נא לבחור קובץ תחילה")
            return
            
        try:
            # שמירת התוכן המקורי למקרה של כישלון
            original_content = ""
            if self.current_index >= 0 and self.current_index < len(self.document_history):
                original_content = self.document_history[self.current_index][0]
            

            processor_widget.set_file_path(self.current_file_path)
            self.last_processor_title = processor_widget.windowTitle()
            processor_widget.changes_made.connect(self.refresh_after_processing)
            
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בעיבוד הטקסט: {str(e)}")
            
    def on_text_changed(self):
        try:
            # קריאת התוכן מהקובץ ולא מהתצוגה
            with open(self.current_file_path, 'r', encoding='utf-8') as file:
                current_content = file.read()
            
            self._safe_update_history(current_content, "שינוי טקסט")
            
        except Exception as e:
            print(f"שגיאה בעדכון הטקסט: {str(e)}")
            





    def undo_action(self):
        """ביטול פעולה אחרונה"""
        try:
            if self.current_index > 0:
                self.current_index -= 1
                content = self.document_history[self.current_index][0]

                # שמירה לקובץ בדיוק כמו ב-save_file
                with open(self.current_file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                # קריאה מחדש בדיוק כמו ב-save_file
                with open(self.current_file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # הצגת התוכן
                self.text_display.setHtml(content)

                self.status_label.setText(f"בוטל: {self.document_history[self.current_index][1]}")
                update_global_status("בוצע ביטול פעולה")
                self.update_buttons_state()
                
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בביטול פעולה: {str(e)}")
                
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בביטול פעולה: {str(e)}")

    def redo_action(self):
        """שחזור פעולה שבוטלה"""
        try:
            if self.current_index < len(self.document_history) - 1:
                self.current_index += 1
                content, description = self.document_history[self.current_index]
                
                # שמירת הטקסט בקובץ כמו שהוא (ללא שינוי פורמט)
                with open(self.current_file_path, 'w', encoding='utf-8') as file:
                    file.write(content)

                # טעינה מחדש של הקובץ לתצוגה
                with open(self.current_file_path, 'r', encoding='utf-8') as file:
                    display_content = file.read()
                
                # הצגת התוכן כ-HTML
                self.text_display.setHtml(display_content)
                
                # עדכון סטטוס
                self.status_label.setText(f"שוחזר: {description}")
                
                # עדכון תפריט הניווט
                self.navigation_updated = False
                self.update_navigation_menu()
                
                # עדכון מצב כפתורים
                self.update_buttons_state()
                
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בשחזור פעולה: {str(e)}")

    def update_buttons_state(self):
        try:
            # עדכון כפתורי ביטול וחזרה
            self.undo_button.setEnabled(self.current_index > 0)
            self.redo_button.setEnabled(self.current_index < len(self.document_history) - 1)
            
            # עדכון כפתור שמירה - פעיל אם יש קובץ נוכחי ויש שינויים
            has_changes = len(self.document_history) > 0
            self.save_button.setEnabled(bool(self.current_file_path) and has_changes)
            
            print(f"עדכון מצב כפתורים - קובץ: {bool(self.current_file_path)}, "
                  f"שינויים: {has_changes}, "
                  f"אינדקס: {self.current_index}")
            
        except Exception as e:
            print(f"שגיאה בעדכון מצב הכפתורים: {str(e)}")
            
    def select_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "בחר קובץ טקסט",
            "",
            "קבצי טקסט (*.txt)",
            
            options=options
        )
        
        if file_path:
            self.current_file_path = file_path
            self.load_file(file_path)
            self.update_navigation_menu() 
            
    def open_in_notepad(self):
        """פתיחת הקובץ הנוכחי בפנקס רשימות"""
        if not self.current_file_path:
            QMessageBox.warning(self, "שגיאה", "נא לבחור קובץ תחילה")
            return
        
        try:
            # פתיחת הקובץ בפנקס רשימות
            subprocess.Popen(['notepad.exe', self.current_file_path])
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בפתיחת פנקס רשימות: {str(e)}")
            

    def save_action(self):
        if not self.current_file_path:
            self.save_file_as()
            return
            
        try:
            content = self.text_display.toHtml()

            content = content.replace('<br>\n', '\n')
            
            with open(self.current_file_path, 'w', encoding='utf-8') as file:
                file.write(content)
                
            self.status_label.setText("הקובץ נשמר בהצלחה")
            QMessageBox.information(self, "שמירה", "הקובץ נשמר בהצלחה!")
        except Exception as e:
            QMessageBox.critical(self, "שגיאה", f"שגיאה בשמירת הקובץ: {str(e)}")



   
    def update_content_from_child(self):
        """עדכון התצוגה לאחר שינויים בחלונות המשנה"""
        if not self.current_file_path:
            return
            
        try:
               # קריאת התוכן המקורי מהקובץ
            with open(self.current_file_path, 'r', encoding='utf-8') as file:
                self.original_content = file.read()
        
            # המרת ירידות שורה לתצוגת HTML
            display_content = self.original_content.replace('\n', '<br>')
            self.text_display.setHtml(display_content)

            # הגדרת תיאור הפעולה
            action_description = self.last_processor_title if self.last_processor_title else "עדכון תוכן"
        
            # עדכון ההיסטוריה פעם אחת בלבד עם התוכן המקורי
            self._safe_update_history(self.original_content, action_description)

            print(f"עודכן תוכן חדש - תיאור: {action_description}")
            print(f"גודל היסטוריה: {len(self.document_history)}")
            
        except Exception as e:
            print(f"שגיאה בעדכון התוכן: {str(e)}")
            QMessageBox.critical(self, "שגיאה", f"שגיאה בעדכון התוכן: {str(e)}")
            
    def open_about_dialog(self):
        """פתיחת חלון 'אודות'"""
        dialog = AboutDialog(self)
        dialog.exec_()

            
    # סקריפט 1 - יצירת כותרות לאוצריא
    def open_create_headers_otzria(self):
        if not self.current_file_path:
            QMessageBox.warning(self, "שגיאה", "נא לבחור קובץ תחילה")
            return
        self.create_headers_window = CreateHeadersOtZria()
        self.create_headers_window.set_file_path(self.current_file_path)
        self.create_headers_window.changes_made.connect(self.refresh_after_processing)
        self.create_headers_window.show()

    # סקריפט 2 - יצירת כותרות לאותיות בודדות
    def open_create_single_letter_headers(self):
        if not self.current_file_path:
            QMessageBox.warning(self, "שגיאה", "נא לבחור קובץ תחילה")
            return
        self.create_single_letter_headers_window = CreateSingleLetterHeaders()
        self.create_single_letter_headers_window.set_file_path(self.current_file_path)
        self.create_single_letter_headers_window.changes_made.connect(self.update_content_from_child)
        self.create_single_letter_headers_window.show()

    # סקריפט 3 - הוספת מספר עמוד בכותרת הדף
    def open_add_page_number_to_heading(self):
        if not self.current_file_path:
            QMessageBox.warning(self, "שגיאה", "נא לבחור קובץ תחילה")
            return
        self.add_page_number_window = AddPageNumberToHeading()
        self.add_page_number_window.set_file_path(self.current_file_path)
        self.add_page_number_window.changes_made.connect(self.update_content_from_child)
        self.add_page_number_window.show()

    # סקריפט 4 - שינוי רמת כותרת
    def open_change_heading_level(self):
        if not self.current_file_path:
            QMessageBox.warning(self, "שגיאה", "נא לבחור קובץ תחילה")
            return
        self.change_heading_level_window = ChangeHeadingLevel()
        self.change_heading_level_window.set_file_path(self.current_file_path)
        self.change_heading_level_window.changes_made.connect(self.update_content_from_child)
        self.change_heading_level_window.show()

    # סקריפט 5 - הדגשת מילה ראשונה וניקוד בסוף קטע
    def open_emphasize_and_punctuate(self):
        if not self.current_file_path:
            QMessageBox.warning(self, "שגיאה", "נא לבחור קובץ תחילה")
            return
        self.emphasize_and_punctuate_window = EmphasizeAndPunctuate()
        self.emphasize_and_punctuate_window.set_file_path(self.current_file_path)
        self.emphasize_and_punctuate_window.changes_made.connect(self.update_content_from_child)
        self.emphasize_and_punctuate_window.show()

    # סקריפט 6 - יצירת כותרות לעמוד ב
    def open_create_page_b_headers(self):
        if not self.current_file_path:
            QMessageBox.warning(self, "שגיאה", "נא לבחור קובץ תחילה")
            return
        self.create_page_b_headers_window = CreatePageBHeaders()
        self.create_page_b_headers_window.set_file_path(self.current_file_path)
        self.create_page_b_headers_window.changes_made.connect(self.update_content_from_child)
        self.create_page_b_headers_window.show()

    # סקריפט 7 - החלפת כותרות לעמוד ב
    def open_replace_page_b_headers(self):
        if not self.current_file_path:
            QMessageBox.warning(self, "שגיאה", "נא לבחור קובץ תחילה")
            return
        self.replace_page_b_headers_window = ReplacePageBHeaders()
        self.replace_page_b_headers_window.set_file_path(self.current_file_path)
        self.replace_page_b_headers_window.changes_made.connect(self.update_content_from_child)
        self.replace_page_b_headers_window.show()

    # סקריפט 8 - בדיקת שגיאות בכותרות
    def open_check_heading_errors_original(self):
        if not self.current_file_path:
            QMessageBox.warning(self, "שגיאה", "נא לבחור קובץ תחילה")
            return
        self.check_heading_errors_original_window = CheckHeadingErrorsOriginal()
        self.check_heading_errors_original_window.set_file_path(self.current_file_path)
        self.check_heading_errors_original_window.process_file(self.current_file_path)
        self.check_heading_errors_original_window.show()

    # סקריפט 9 - בדיקת שגיאות בכותרות מותאם לספרים על הש"ס
    def open_check_heading_errors_custom(self):
        if not self.current_file_path:
            QMessageBox.warning(self, "שגיאה", "נא לבחור קובץ תחילה")
            return
        self.check_heading_errors_custom_window = CheckHeadingErrorsCustom()
        self.check_heading_errors_custom_window.set_file_path(self.current_file_path)
        self.check_heading_errors_custom_window.process_file(self.current_file_path)
        self.check_heading_errors_custom_window.show()

    # סקריפט 10 - המרת תמונה לטקסט
    def open_Image_To_Html_App(self):
        self.Image_To_Html_App_window = ImageToHtmlApp()
        self.Image_To_Html_App_window.show()

    # סקריפט 11 - תיקון שגיאות נפוצות
    def open_Text_Cleaner_App(self):
        if not self.current_file_path:
            QMessageBox.warning(self, "שגיאה", "נא לבחור קובץ תחילה")
            return
        self.Text_Cleaner_App_window = TextCleanerApp()
        self.Text_Cleaner_App_window.set_file_path(self.current_file_path)
        self.Text_Cleaner_App_window.changes_made.connect(self.update_content_from_child)
        self.Text_Cleaner_App_window.show()

    def load_icon_from_base64(self, base64_string):
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(base64_string))
        return QIcon(pixmap)
    
    #עדכונים
    def check_for_update_ready(self):
        """בדיקה אם העדכון מוכן להתקנה"""
        current_dir = os.path.dirname(sys.executable)
        marker_file = os.path.join(current_dir, "update_ready.txt")
        
        if os.path.exists(marker_file):
            try:
                with open(marker_file, "r", encoding="utf-8") as f:
                    new_version = f.readline().strip()
                
                # מחיקת קובץ הסימון
                os.remove(marker_file)
                
                # הפעלת העדכון
                temp_exe = os.path.join(current_dir, f'new_version_{new_version}.exe')
                current_exe = sys.executable
                
                if os.path.exists(temp_exe):
                    try:
                        # שחרור הקובץ הנוכחי מהזיכרון
                        import win32api
                        import win32con
                        import win32gui
                        
                        # שליחת הודעת סגירה לכל החלונות של התוכנה
                        def enum_windows_callback(hwnd, _):
                            if win32gui.IsWindowVisible(hwnd):
                                t, w = win32gui.GetWindowText(hwnd), win32gui.GetClassName(hwnd)
                                if "עריכת ספרי דיקטה" in t: 
                                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                        
                        win32gui.EnumWindows(enum_windows_callback, None)
                        
                        # המתנה קצרה לסגירת החלונות
                        time.sleep(1)
                        
                        # העתקת הקובץ החדש
                        shutil.copy2(temp_exe, current_exe)
                        os.remove(temp_exe)
                        
                        # הפעלה מחדש של התוכנה
                        os.startfile(current_exe)
                        
                        # סגירה מסודרת
                        QApplication.quit()
                        
                    except Exception as e:
                        print(f"שגיאה בהחלפת הקובץ: {e}")
                        
            except Exception as e:
                print(f"שגיאה בהתקנת העדכון: {e}")

    def handle_update_available(self, download_url, new_version):
        """טיפול בעידכון"""
        reply = QMessageBox.question(
            self,
            "נמצא עדכון",
            f"נמצאה גרסה חדשה ({new_version})!\nהאם ברצונך לעדכן כעת?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.download_and_install_update(download_url, new_version)
        else:
            self.status_label.setText("עדכון זמין")

    def handle_no_update(self):
        """טיפול במקרה שאין עדכון"""

        self.status_label.setText("התוכנה מעודכנת")

    def download_and_install_update(self, download_url, new_version):
        """הורדת והתקנת העדכון"""
        try:
            current_exe = sys.executable
            updater_path = os.path.join(os.path.dirname(current_exe), 'updater.exe')
            
            # בדיקה והורדת תוכנת העדכון אם לא קיימת
            if not os.path.exists(updater_path):
                try:
                    # קישור להורדת תוכנת העדכון
                    updater_url = "https://mitmachim.top/assets/uploads/files/1741337852484-updater.exe"
                    
                    # שימוש באותה תעודת נטפרי שכבר הוגדרה ב-UpdateChecker
                    netfree_cert = self.update_checker.netfree_cert if hasattr(self.update_checker, 'netfree_cert') else None
                    
                    # יצירת חלון העדכון המעוצב
                    updater_window = QMainWindow(self)
                    updater_window.setWindowTitle("הורדת תוכנת עדכון")
                    updater_window.setFixedWidth(600)
                    updater_window.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
                    updater_window.setLayoutDirection(Qt.RightToLeft)

                    # מיקום החלון במרכז החלון ההורה
                    parent_center = self.mapToGlobal(self.rect().center())
                    updater_window.move(
                        parent_center.x() - updater_window.width() // 2,
                        parent_center.y() - 150 // 2
                    )

                    # יצירת הממשק
                    central_widget = QWidget()
                    updater_window.setCentralWidget(central_widget)
                    
                    layout = QVBoxLayout()
                    layout.setContentsMargins(15, 15, 15, 15)
                    layout.setSpacing(15)

                    # כותרת ראשית
                    main_status = QLabel("מוריד את תוכנת העדכון...")
                    main_status.setStyleSheet("""
                        QLabel {
                            color: #1a365d;
                            font-family: "Segoe UI", Arial;
                            font-size: 16px;
                            font-weight: bold;
                            padding: 10px;
                        }
                    """)
                    main_status.setAlignment(Qt.AlignCenter)
                    layout.addWidget(main_status)

                    # פירוט המשימה הנוכחית
                    detail_status = QLabel("מתחבר לשרת...")
                    detail_status.setStyleSheet("""
                        QLabel {
                            color: #666666;
                            font-family: "Segoe UI", Arial;
                            font-size: 12px;
                            padding: 5px;
                        }
                    """)
                    detail_status.setAlignment(Qt.AlignCenter)
                    detail_status.setWordWrap(True)
                    layout.addWidget(detail_status)

                    # סרגל התקדמות
                    progress_bar = QProgressBar()
                    progress_bar.setStyleSheet("""
                        QProgressBar {
                            border: 2px solid #2b4c7e;
                            border-radius: 15px;
                            padding: 5px;
                            text-align: center;
                            background-color: white;
                            height: 30px;
                        }
                        QProgressBar::chunk {
                            background-color: #4CAF50;
                            border-radius: 13px;
                        }
                    """)
                    layout.addWidget(progress_bar)

                    central_widget.setLayout(layout)
                    updater_window.show()

                    # הורדת הקובץ
                    response = requests.get(
                        updater_url,
                        verify=netfree_cert if netfree_cert and os.path.exists(netfree_cert) else True,
                        stream=True
                    )
                    response.raise_for_status()
                    
                    # חישוב גודל הקובץ
                    total_size = int(response.headers.get('content-length', 0))
                    block_size = 8192
                    downloaded = 0
                    
                    # הורדה עם עדכון התקדמות
                    with open(updater_path, 'wb') as f:
                        for data in response.iter_content(block_size):
                            downloaded += len(data)
                            f.write(data)
                            progress = int((downloaded / total_size) * 100) if total_size > 0 else 0
                            progress_bar.setValue(progress)
                            
                            # עדכון תיאור ההתקדמות
                            downloaded_mb = downloaded / (1024 * 1024)
                            total_mb = total_size / (1024 * 1024)
                            detail_status.setText(
                                f"מוריד: {downloaded_mb:.1f}MB מתוך {total_mb:.1f}MB"
                            )
                            
                            QApplication.processEvents()
                    
                    # סגירת חלון ההורדה
                    updater_window.close()
                    
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "שגיאה בהורדת תוכנת העדכון",
                        f"לא ניתן להוריד את תוכנת העדכון:\n{str(e)}"
                    )
                    self.status_label.setText("שגיאה בהורדת תוכנת העדכון")
                    return

            # עדכון התווית בחלון הראשי
            self.status_label.setText("מתחיל בתהליך העדכון...")

            # הפעלת תוכנת העדכון עם הרשאות מנהל - ללא סגירת התוכנה הנוכחית
            if sys.platform == 'win32':
                import ctypes
                if ctypes.windll.shell32.IsUserAnAdmin():
                    subprocess.Popen([updater_path, download_url, current_exe, new_version])
                else:
                    ctypes.windll.shell32.ShellExecuteW(
                        None, 
                        "runas", 
                        updater_path,
                        f"{download_url} {current_exe} {new_version}",
                        None,
                        1
                    )
                
                # עדכון התווית בחלון הראשי
                self.status_label.setText("מתבצע עדכון ברקע...")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "שגיאה",
                f"שגיאה בהפעלת תהליך העדכון: {str(e)}"
            )
            self.status_label.setText("שגיאה בהורדת העדכון")




            
            
class AboutDialog(QDialog):
    """חלון 'אודות'"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("אודות התוכנה")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFixedWidth(800)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 15px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # כותרת ראשית
        title_label = QLabel("עריכת ספרי דיקטה עבור 'אוצריא'")
        title_label.setStyleSheet("""
            QLabel {
                color: #1a365d;
                font-family: "Segoe UI", Arial;
                font-size: 32px;
                font-weight: bold;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # מידע על הגרסה והתאריך
        info_container = QHBoxLayout()
        
        version_label = QLabel("גירסה: v3.2")
        version_label.setStyleSheet("""
            QLabel {
                color: #2b4c7e;
                font-family: "Segoe UI", Arial;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        
        date_label = QLabel("תאריך: כט שבט תשפה")
        date_label.setStyleSheet(version_label.styleSheet())
        
        info_container.addWidget(version_label, alignment=Qt.AlignCenter)
        info_container.addWidget(date_label, alignment=Qt.AlignCenter)
        layout.addLayout(info_container)

        # פיתוח
        dev_label = QLabel("נכתב על ידי 'מתנדבי אוצריא', להצלחת לומדי התורה הקדושה")
        dev_label.setStyleSheet("""
            QLabel {
                color: #1a365d;
                font-family: "Segoe UI", Arial;
                font-size: 18px;
                margin: 10px 0;
            }
        """)
        dev_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(dev_label)

        # סגנון משותף לקישורים
        link_style = """
            QLabel {
                color: #1a365d;
                font-family: "Segoe UI", Arial;
                font-size: 18px;
                padding: 5px;
            }
            QLabel a {
                color: #2b4c7e;
                text-decoration: none;
            }
            QLabel a:hover {
                color: #1a365d;
                text-decoration: underline;
            }
        """

        # קישורים להורדה
        github_label = QLabel('ניתן להוריד את הגירסא האחרונה, וכן קובץ הדרכה, בקישור הבא: <a href="https://github.com/YOSEFTT/EditingDictaBooks/releases">GitHub</a>')
        github_label.setStyleSheet(link_style)
        github_label.setOpenExternalLinks(True)
        github_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(github_label)

        mitmachimtop_label = QLabel('או כאן: <a href="https://mitmachim.top/topic/77509/הסבר-הוספת-וטיפול-בספרים-ל-אוצריא-כעת-זה-קל">מתמחים.טופ</a>')
        mitmachimtop_label.setStyleSheet(link_style)
        mitmachimtop_label.setOpenExternalLinks(True)
        mitmachimtop_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(mitmachimtop_label)

        drive_label = QLabel('או בדרייב: <a href="http://did.li/otzaria-">כאן</a> או <a href="https://drive.google.com/open?id=1KEKudpCJUiK6Y0Eg44PD6cmbRsee1nRO&usp=drive_fs">כאן</a>')
        drive_label.setStyleSheet(link_style)
        drive_label.setOpenExternalLinks(True)
        drive_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(drive_label)

        # מידע נוסף
        info_text = "אפשר לבקש את התוכנה\nוכן להירשם לקבלת עדכון במייל כשיוצא עדכון לתוכנות אלו\nוכן לקבל תמיכה וסיוע בכל הקשור לתוכנה זו ולתוכנת 'אוצריא'\nבמייל הבא:"
        info_label = QLabel(info_text)
        info_label.setStyleSheet("""
            QLabel {
                color: #1a365d;
                font-family: "Segoe UI", Arial;
                font-size: 18px;
                margin: 15px 0 5px 0;
            }
        """)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        # כתובת מייל
        gmail_label = QLabel('<a href="https://mail.google.com/mail/u/0/?view=cm&fs=1&to=otzaria.1%40gmail.com%E2%80%AC">otzaria.1@gmail.com</a>')
        gmail_label.setStyleSheet("""
            QLabel {
                color: #2b4c7e;
                font-family: "Segoe UI", Arial;
                font-size: 18px;
                font-weight: bold;
            }
            QLabel a {
                color: #2b4c7e;
                text-decoration: none;
            }
            QLabel a:hover {
                color: #1a365d;
                text-decoration: underline;
            }
        """)
        gmail_label.setOpenExternalLinks(True)
        gmail_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(gmail_label)

        self.setLayout(layout)

        
class DocumentHistory:
    def __init__(self, max_stack_size=100):
        self.undo_stack = []  
        self.redo_stack = []
        self.max_stack_size = max_stack_size
        self.current_content = ""
        self.current_description = "לא בוצעו עדיין פעולות"

    def push_state(self, content, description):

        if content != self.current_content:
            self.undo_stack.append((self.current_content, self.current_description))
            self.current_content = content
            self.current_description = description
            self.redo_stack.clear()

            if len(self.undo_stack) > self.max_stack_size:
                self.undo_stack.pop(0)

    def undo(self):
        """ביטול פעולה אחרונה"""
        if not self.can_undo():
            return None, None

        self.redo_stack.append((self.current_content, self.current_description))
        self.current_content, self.current_description = self.undo_stack.pop()
        return self.current_content, self.current_description

    def redo(self):
        """חזרה על פעולה שבוטלה"""
        if not self.can_redo():
            return None, None

        self.undo_stack.append((self.current_content, self.current_description))
        self.current_content, self.current_description = self.redo_stack.pop()
        return self.current_content, self.current_description

    def get_current_description(self):
        """קבלת תיאור הפעולה הנוכחית"""
        return self.current_description

 
    
# ==========================================
#  update
# ==========================================
class UpdateChecker(QThread):
    update_available = pyqtSignal(str, str)  
    no_update = pyqtSignal()  
    error = pyqtSignal(str)  

    def __init__(self, current_version, parent=None):
        super().__init__(parent)
        self.current_version = current_version
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'EditingDictaBooks-UpdateChecker'
        }

        # קביעת נתיב קבוע לתעודת נטפרי
        self.setup_netfree_cert()

    def setup_netfree_cert(self):
        """הגדרת תעודת נטפרי בנתיב קבוע"""
        try:
            # יצירת תיקיית נטפרי קבועה ב-C: אם לא קיימת
            netfree_dir = r"C:\ProgramData\NetFree\CA"
            if not os.path.exists(netfree_dir):
                os.makedirs(netfree_dir)
            
            # נתיב קבוע לתעודת נטפרי
            self.netfree_cert = os.path.join(netfree_dir, 'netfree-ca-list.crt')
            
            # בדיקה אם התעודה קיימת וריקה
            if not os.path.exists(self.netfree_cert) or os.path.getsize(self.netfree_cert) == 0:
                help_message = f"""
תעודת האבטחה של נטפרי חסרה או ריקה.
נא לבצע את הפעולות הבאות:

1. הורד את תעודת נטפרי מהאתר הרשמי
2. העתק את התעודה לנתיב הבא:
   {self.netfree_cert}
3. הפעל מחדש את התוכנה

שים לב: אין צורך לבצע פעולה זו שוב בעתיד, התעודה תישמר בנתיב הקבוע.
"""
                print(help_message)
                # יצירת קובץ ריק אם לא קיים
                with open(self.netfree_cert, 'a') as f:
                    pass
            
            # הגדרת משתני הסביבה
            os.environ['REQUESTS_CA_BUNDLE'] = self.netfree_cert
            os.environ['SSL_CERT_FILE'] = self.netfree_cert
            
            # החלפת פונקציית התעודות של requests
            def custom_where():
                return self.netfree_cert
            
            requests.certs.where = custom_where
            
            print(f"משתמש בתעודת SSL מ: {self.netfree_cert}")
            
        except Exception as e:
            print(f"שגיאה בהגדרת תעודת SSL: {e}")
            if "Access is denied" in str(e):
                self.error.emit(
                    "אין הרשאות ליצור את תיקיית התעודות.\n"
                    "נא להפעיל את התוכנה כמנהל מערכת (Run as Administrator)"
                )

    def run(self):
        try:
            api_url = "https://api.github.com/repos/YOSEFTT/EditingDictaBooks/releases/latest"
            
            print("מנסה להתחבר לשרת GitHub...")
            print(f"URL: {api_url}")
            
            # בדיקה אם קובץ התעודה ריק
            if os.path.getsize(self.netfree_cert) == 0:
                raise requests.exceptions.SSLError(
                    "קובץ תעודת האבטחה ריק. נא להעתיק את תעודת נטפרי לקובץ"
                )
            
            response = requests.get(
                api_url,
                headers=self.headers,
                timeout=30,
                verify=self.netfree_cert
            )
            
            response.raise_for_status()
            
            latest_release = response.json()
            latest_version = latest_release['tag_name'].replace('v', '')
            
            print(f"גרסה נוכחית: {self.current_version}")
            print(f"גרסה אחרונה: {latest_version}")
            
            if self._compare_versions(latest_version, self.current_version):
                download_url = None
                for asset in latest_release['assets']:
                    if asset['name'].lower().endswith('.exe'):
                        download_url = asset['browser_download_url']
                        break
                
                if download_url:
                    print("נמצאה גרסה חדשה!")
                    self.update_available.emit(download_url, latest_version)
                else:
                    self.error.emit("נמצאה גרסה חדשה אך לא נמצא קובץ הורדה מתאים")
            else:
                print("אין גרסה חדשה")
                self.no_update.emit()
                
        except requests.exceptions.SSLError as e:
            error_message = str(e)
            print(f"SSL Error details: {error_message}")
            
            help_message = f"""
              שגיאת SSL בתקשורת עם שרת GitHub. 
              נא לבצע את הפעולות הבאות:

              1. הורד את תעודת נטפרי מהאתר הרשמי
              2. העתק את התעודה לנתיב הבא:
                {self.netfree_cert}
              3. הפעל מחדש את התוכנה

             הערה: התעודה תישמר בנתיב קבוע ואין צורך להעתיק אותה שוב בעתיד.
            """
            self.error.emit(help_message)
                
        except requests.exceptions.ConnectionError as e:
            print(f"Connection Error: {str(e)}")
            self.error.emit("בעיית חיבור לשרת GitHub. אנא בדוק את חיבור האינטרנט שלך")
            
        except Exception as e:
            print(f"General Error: {str(e)}")
            self.error.emit(f"שגיאה כללית: {str(e)}")

    def _compare_versions(self, latest_version, current_version):
        """
        השוואת גרסאות
        """
        try:
            latest_version = latest_version.upper().strip('V')
            current_version = current_version.upper().strip('V')
            
            latest_parts = [int(x) for x in latest_version.split('.')]
            current_parts = [int(x) for x in current_version.split('.')]
            
            while len(latest_parts) < 3:
                latest_parts.append('0')
            while len(current_parts) < 3:
                current_parts.append('0')
            
            for i in range(3):
                if latest_parts[i] > current_parts[i]:
                    return True
                elif latest_parts[i] < current_parts[i]:
                    return False
                
            return False  # הגרסאות זהות
        
        except Exception as e:
            print(f"שגיאה בהשוואת גרסאות: {str(e)}")
            print(f"גרסה אחרונה: {latest_version}, גרסה נוכחית: {current_version}")
            return False
# ==========================================
# Main Application
# ==========================================
def main():
    if sys.platform == 'win32':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    main_menu = MainMenu()
    main_menu.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
