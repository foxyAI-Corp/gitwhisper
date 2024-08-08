from PyQt5.QtCore import *
from PyQt5.QtGui import * # type: ignore
from PyQt5.QtWidgets import *
import sys
import json
import jsonpickle # type: ignore
import jsonschema # type: ignore
from pathlib import Path
import os
import uuid
import gitwhisper_ai

class FormatedPath(Path):
    def __str__(self):
        return super().__str__().replace(self._flavour.sep, '/')

class Window(QMainWindow):
    resized = pyqtSignal()
    def  __init__(self, parent=None):
        super(Window, self).__init__(parent=parent)

    def resizeEvent(self, event):
        self.resized.emit()
        return super(Window, self).resizeEvent(event)

class GetResponseThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, message):
        super(GetResponseThread, self).__init__()
        self.message = message

    def run(self):
        response = gitwhisper_ai.send_message(self.message)
        self.finished.emit(response.text)

class AutoResizeWidget(QWidget):
    def __init__(self, parent=None, padding=0):
        super(AutoResizeWidget, self).__init__(parent=parent)
        self.padding = padding

    def childEvent(self, event):
        super().childEvent(event)
        self.update_size()

    def update_size(self):
        QTimer.singleShot(0, self._update_size)

    def _update_size(self):
        scroll_area = self.parent().parent()
        if isinstance(scroll_area, QScrollArea):
            scroll_index = scroll_area.verticalScrollBar().value()

        self.setFixedHeight(0)
        bottom_values = []

        for child in self.children():
            if isinstance(child, QWidget):
                bottom = child.y() + child.height()
                bottom_values.append(bottom)

        new_height = max(bottom_values) - self.y() + self.padding

        if self.height() != new_height:
            self.setFixedHeight(new_height)

        if isinstance(scroll_area, QScrollArea):
            scroll_area.verticalScrollBar().setValue(scroll_index)

class AutoResizeTextEdit(QTextEdit):
    keypressed = pyqtSignal(QEvent)
    def __init__(self, parent=None, padding = 0, direction = 'down'):
        super(AutoResizeTextEdit, self).__init__(parent)
        self.padding = padding
        self.direction = direction
        self._minimumHeight = 0
        self._maximumHeight = float('inf')
        self.accept_event = False

    def keyPressEvent(self, event):
        self.keypressed.emit(event)
        if not self.accept_event: super(AutoResizeTextEdit, self).keyPressEvent(event)
        self.accept_event = False
        self.update_size()

    def resizeEvent(self, event):
        super(AutoResizeTextEdit, self).resizeEvent(event)
        self.update_size()

    def update_size(self):
        content = self.toPlainText()

        height = self.height()
        doc = self.document()
        if content == '':
            doc = QTextDocument()
            doc.setDefaultFont(self.font())
            doc.setHtml(self.toHtml())
        content_height = doc.size().height()
        new_height = max(min(int(content_height + self.padding * 2), self._maximumHeight), self._minimumHeight)
        self.setFixedHeight(new_height)

        if self.direction == 'up':
            self.move(self.x(), self.y() - (new_height - height))

        if content == '':
            del doc

        if self.parent():
            self.parent().update()

    def setMinimumHeight(self, h):
        super(AutoResizeTextEdit, self).setMinimumHeight(h)
        self._minimumHeight = h
        self.update_size()

    def setMaximumHeight(self, h):
        super(AutoResizeTextEdit, self).setMaximumHeight(h)
        self._maximumHeight = h
        self.update_size()

    def append(self, text):
        super(AutoResizeTextEdit, self).append(text)
        self.update_size()

    def clear(self):
        super(AutoResizeTextEdit, self).clear()
        self.update_size()

    def cut(self):
        super(AutoResizeTextEdit, self).cut()
        self.update_size()

    def insertHtml(self, text):
        super(AutoResizeTextEdit, self).insertHtml(text)
        self.update_size()

    def insertPlainText(self, text):
        super(AutoResizeTextEdit, self).insertPlainText(text)
        self.update_size()

    def paste(self):
        super(AutoResizeTextEdit, self).paste()
        self.update_size()

    def redo(self):
        super(AutoResizeTextEdit, self).redo()
        self.update_size()

    def selectAll(self):
        super(AutoResizeTextEdit, self).selectAll()
        self.update_size()

    def setCurrentFont(self, f):
        super(AutoResizeTextEdit, self).setCurrentFont(f)
        self.update_size()

    def setGeometry(self, a0):
        super(AutoResizeTextEdit, self).setGeometry(a0)
        self.update_size()

    def setFontFamily(self, fontFamily):
        super(AutoResizeTextEdit, self).setFontFamily(fontFamily)
        self.update_size()

    def setFontItalic(self, b):
        super(AutoResizeTextEdit, self).setFontItalic(b)
        self.update_size()

    def setFontPointSize(self, s):
        super(AutoResizeTextEdit, self).setFontPointSize(s)
        self.update_size()

    def setFontUnderline(self, b):
        super(AutoResizeTextEdit, self).setFontUnderline(b)
        self.update_size()

    def setFontWeight(self, w):
        super(AutoResizeTextEdit, self).setFontWeight(w)
        self.update_size()

    def setHtml(self, text):
        super(AutoResizeTextEdit, self).setHtml(text)
        self.update_size()

    def setMarkdown(self, markdown):
        super(AutoResizeTextEdit, self).setMarkdown(markdown)
        self.update_size()

    def setPlainText(self, text):
        super(AutoResizeTextEdit, self).setPlainText(text)
        self.update_size()

    def setText(self, text):
        super(AutoResizeTextEdit, self).setText(text)
        self.update_size()

    def undo(self):
        super(AutoResizeTextEdit, self).undo()
        self.update_size()

    def zoomIn(self, range=1):
        super(AutoResizeTextEdit, self).zoomIn(range)
        self.update_size()

    def zoomOut(self, range=1):
        super(AutoResizeTextEdit, self).zoomOut(range)
        self.update_size()

class GitWhisperApp(object):
    def start(self, data_dir = FormatedPath('.gitwhisper_data/')):
        if not data_dir.exists() or not data_dir.is_dir():
            os.makedirs(data_dir)
        
        self.data_dir = data_dir
        self._app = QApplication(sys.argv)
        self._dpi = self._app.primaryScreen().logicalDotsPerInch()
        self.setupUi()
        self._app.exec_()

    def setupUi(self):
        self.MainWindow = Window()
        if self.MainWindow.objectName():
            self.MainWindow.setObjectName("MainWindow")
        self.MainWindow.resize(780, 520)
        self.MainWindow.setMinimumSize(500, 350)
        self.MainWindow.setStyleSheet("background-color: #fff;")
        self.MainWindow.resized.connect(self.on_resize)
        self.centralwidget = QWidget(self.MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.chat_area = QScrollArea(self.centralwidget)
        self.chat_area.setObjectName("chat_area")
        self.chat_area.setGeometry(QRect(200, 0, 580, 490))
        self.chat_area.setStyleSheet("border: none;")
        self.chat_area.setWidgetResizable(True)
        self.scrollAreaWidgetContents = AutoResizeWidget(padding=50)
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        self.bot_message = AutoResizeTextEdit(self.scrollAreaWidgetContents, padding=4)
        self.bot_message.setObjectName("bot_message")
        self.bot_message.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.bot_message.keypressed.connect(self.remove_scroll)
        self.bot_message.setGeometry(QRect(20, 70, 400, 32))
        self.bot_message.setStyleSheet(
            "border: 1px solid #ebebeb;\n"
            "border-radius: 7.5px;\n"
            "background-color: #fafafa;\n"
            "font-size: 13px;\n"
            "padding: 3.49px 6px;\n"
            "color: #111;"
        )
        self.bot_message.setUndoRedoEnabled(False)
        self.bot_message.setReadOnly(True)

        self.user_message = AutoResizeTextEdit(self.scrollAreaWidgetContents, padding=4)
        self.user_message.setObjectName("user_message")
        self.user_message.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.user_message.keypressed.connect(self.remove_scroll)
        self.user_message.setGeometry(QRect(160, 20, 400, 32))
        self.user_message.setStyleSheet(
            "border: 1px solid #ebebeb;\n"
            "border-radius: 7.5px;\n"
            "background-color: #fefefe;\n"
            "font-size: 13px;\n"
            "padding: 3.49px 6px;\n"
            "color: #111;"
        )
        self.user_message.setUndoRedoEnabled(False)
        self.user_message.setReadOnly(True)
        
        self.chat_area.setWidget(self.scrollAreaWidgetContents)
        
        self.message_input = AutoResizeTextEdit(self.centralwidget, padding=4, direction='up')
        self.message_input.setObjectName("message_input")
        self.message_input.setGeometry(QRect(240, 470, 500, 32))
        self.message_input.setEnabled(False)
        self.message_input.setMaximumHeight(272)
        self.message_input.setStyleSheet(
            "border: 1px solid #ebebeb;\n"
            "border-radius: 7.5px;\n"
            "background-color: #fff;\n"
            "font-size: 13px;\n"
            "padding: 3.49px 6px;\n"
            "padding-right: 32px;"
        )
        
        self.send_message_button = QPushButton(self.centralwidget)
        self.send_message_button.setObjectName("send_message_button")
        self.send_message_button.setGeometry(QRect(708, 470, 32, 32))
        self.send_message_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.send_message_button.setEnabled(False)
        self.send_message_button.setStyleSheet(
            "border: 1px solid #ebebeb;\n"
            "border-top-right-radius: 7.5px;\n"
            "border-bottom-right-radius: 7.5px;\n"
            "background-color: #fff;\n"
            "font-size: 13px;\n"
            "padding: 3.49px 6px;"
        )

        self.chat_list_area = QScrollArea(self.centralwidget)
        self.chat_list_area.setObjectName("chat_list_area")
        self.chat_list_area.setGeometry(QRect(0, 0, 200, 520))
        self.chat_list_area.setStyleSheet("border-right: 1px solid #dcdcdc;")
        self.chat_list_area.setFrameShape(QFrame.NoFrame)
        self.chat_list_area.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = AutoResizeWidget(padding=10)
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")

        self.new_chat_button = QPushButton(self.scrollAreaWidgetContents_2)
        self.new_chat_button.setObjectName("new_chat_button")
        self.new_chat_button.setGeometry(QRect(10, 10, 180, 32))
        self.new_chat_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.new_chat_button.setStyleSheet(
            "text-align: left;\n"
            "border: 1px solid #ebebeb;\n"
            "border-radius: 7.5px;\n"
            "background-color: #fff;\n"
            "font-size: 13px;\n"
            "padding: 3.49px 6px;"
        )

        self.chat_list_area.setWidget(self.scrollAreaWidgetContents_2)

        self.dialog_open_background = QPushButton(self.centralwidget)
        self.dialog_open_background.setGeometry(QRect(0, 0, self.MainWindow.width(), self.MainWindow.height()))
        self.dialog_open_background.setStyleSheet(
            "background-color: #11111180;\n"
            "border: none;"
        )
        self.dialog_open_background.setObjectName("dialog_open_background")

        self.new_chat_dialog = QWidget(self.centralwidget)
        self.new_chat_dialog.setObjectName("new_chat_dialog")
        self.new_chat_dialog.setGeometry(QRect(155, 180, 470, 160))
        self.new_chat_dialog.setStyleSheet(
            "border: 1px solid #ebebeb;\n"
            "border-radius: 7.5px;\n"
            "background-color: #fff;\n"
            "font-size: 13px;\n"
            "padding: 3.49px 6px;"
        )
        
        self.repo_path_label = QLabel(self.new_chat_dialog)
        self.repo_path_label.setObjectName("repo_path_label")
        self.repo_path_label.setGeometry(QRect(20, 20, 200, 32))
        self.repo_path_label.setStyleSheet(
            "border: none;\n"
            "font-size: 16px;"
        )

        self.new_chat_dialog_confirm_button = QPushButton(self.new_chat_dialog)
        self.new_chat_dialog_confirm_button.setObjectName("new_chat_dialog_confirm_button")
        self.new_chat_dialog_confirm_button.setGeometry(QRect(270, 110, 180, 32))
        self.new_chat_dialog_confirm_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.new_chat_dialog_confirm_button.setEnabled(False)
        self.new_chat_dialog_confirm_button.setStyleSheet(
            "border: 1px solid #ebebeb;\n"
            "border-radius: 7.5px;\n"
            "background-color: #fff;\n"
            "font-size: 13px;\n"
            "padding: 3.49px 6px;"
        )

        self.repo_path_input = QLineEdit(self.new_chat_dialog)
        self.repo_path_input.setObjectName("repo_path_input")
        self.repo_path_input.setGeometry(QRect(30, 60, 420, 32))
        self.repo_path_input.setStyleSheet(
            "border: 1px solid #ebebeb;\n"
            "border-radius: 7.5px;\n"
            "background-color: #fff;\n"
            "font-size: 13px;\n"
            "padding: 3.49px 6px;"
        )

        self.MainWindow.setCentralWidget(self.centralwidget)

        self.MainWindow.setWindowTitle("GitWhisper")
        self.message_input.setPlaceholderText("Send a message")
        self.new_chat_button.setText("New chat")
        self.repo_path_label.setText("Git Repository path:")
        self.new_chat_dialog_confirm_button.setText("New chat")
        self.repo_path_input.setPlaceholderText("Git Repository path")
        self.send_message_button.setText(u"\u2191")
        
        QMetaObject.connectSlotsByName(self.MainWindow)

        self.to_startup_page()
        self.load_chats_list()
        self.MainWindow.show()

    def on_resize(self):
        self.chat_list_area.setFixedHeight(self.MainWindow.height())
        self.chat_area.setFixedHeight(self.MainWindow.height() - 30)
        self.dialog_open_background.setFixedHeight(self.MainWindow.height())

        self.chat_area.setFixedWidth(self.MainWindow.width() - self.chat_list_area.width())
        self.dialog_open_background.setFixedWidth(self.MainWindow.width())

        self.message_input.setGeometry(QRect(
            240, self.MainWindow.height() - self.message_input.height() + 32 - 50,
            self.MainWindow.width() - 280, 32
        ))
        self.send_message_button.setGeometry(QRect(
            self.MainWindow.width() - 72, self.MainWindow.height() - 50,
            32, 32
        ))
        self.new_chat_dialog.setGeometry(QRect(
            int((self.MainWindow.width() - 470) / 2), int((self.MainWindow.height() - 160) / 2),
            470, 160
        ))

    def get_data(self):
        file_path = self.data_dir / 'chats_data.json'

        if not file_path.exists() or not file_path.is_file() or open(file_path).read().strip() == '':
            with open(file_path, 'w') as file:
                json.dump({}, file, indent=4)

        schema = {
            "type": "object",
            "patternProperties": {
                "^[a-f0-9]{8}_[a-f0-9]{4}_[a-f0-9]{4}_[a-f0-9]{4}_[a-f0-9]{12}_[0-9]+$": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string"
                        },
                        "history": {
                            "type": "array"
                        }
                    },
                    "required": ["path", "history"],
                    "additionalProperties": False
                }
            },
            "additionalProperties": False
        }

        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                for d in data.values():
                    d['history'] = jsonpickle.decode(d['history'])
                jsonschema.validate(instance=data, schema=schema)
                return data
        except (json.decoder.JSONDecodeError, jsonschema.ValidationError):
            with open(self.data_dir / 'chats_data.json', 'w') as file:
                json.dump({}, file, indent=4)
            return self.get_data()

    def save_data(self, data):
        with open(self.data_dir / 'chats_data.json', 'w') as file:
            for d in data.values():
                d['history'] = jsonpickle.encode(d['history'], True)
            json.dump(data, file, indent=4)

    def reset_page(self):
        self.bot_message.hide()
        self.user_message.hide()
        self.new_chat_dialog.hide()
        self.dialog_open_background.hide()

        try:
            self.repo_path_input.textEdited.disconnect()
            self.repo_path_input.returnPressed.disconnect()
            self.new_chat_dialog_confirm_button.clicked.disconnect()
        except Exception:
            pass

    def open_new_chat_dialog(self, *, cancel_allowed = True):
        self.new_chat_dialog.show()
        self.repo_path_input.setFocus()

        try:
            self.dialog_open_background.clicked.disconnect()
        except:
            pass

        if cancel_allowed:
            self.dialog_open_background.clicked.connect(self.close_new_chat_dialog)
        self.dialog_open_background.show()

    def close_new_chat_dialog(self):
        self.new_chat_dialog.hide()
        self.dialog_open_background.hide()

    def remove_scroll(self, event):
        self.MainWindow.sender().accept_event = True

    def select_chat(self):
        self.message_input.setEnabled(True)
        self.send_message_button.setEnabled(True)

        button = self.MainWindow.sender()
        repo_id = button.objectName()[len('chat_button_'):]

        self.repo_id = repo_id

        if not getattr(self, 'selected_chat', None):
            self.selected_chat = None

        def change_bg_color(elem):
            if "background-color: #fafafa;" not in elem.styleSheet():
                elem.setStyleSheet(
                    "text-align: left;\n"
                    "border: 1px solid #ebebeb;\n"
                    "border-radius: 7.5px;\n"
                    "background-color: #fafafa;\n"
                    "font-size: 13px;\n"
                    "padding: 3.49px 6px;"
                )
            else:
                elem.setStyleSheet(
                    "text-align: left;\n"
                    "border: 1px solid #ebebeb;\n"
                    "border-radius: 7.5px;\n"
                    "background-color: #fff;\n"
                    "font-size: 13px;\n"
                    "padding: 3.49px 6px;"
                )
        
        if self.selected_chat not in (button, None): change_bg_color(self.selected_chat)
        if self.selected_chat != button: change_bg_color(button)

        self.selected_chat = button
        self.load_chat_history(repo_id)

    def new_chat(self, repo_path):
        self.reset_page()

        self.message_input.setEnabled(True)
        self.send_message_button.setEnabled(True)
        
        abs_path = str(repo_path.resolve())
        repo_id = str(uuid.uuid5(uuid.UUID('00000000-0000-0000-0000-000000000000'), abs_path)).replace('-', '_')
        
        data = self.get_data()

        if not getattr(self, 'repo_chat_counts', None):
            self.repo_chat_counts = {}
            for d in data.values():
                if d['path'] not in self.repo_chat_counts:
                    self.repo_chat_counts[d['path']] = 0
                self.repo_chat_counts[d['path']] += 1

        if abs_path not in self.repo_chat_counts:
            self.repo_chat_counts[abs_path] = 0
        self.repo_chat_counts[abs_path] += 1

        repo_id = f"{repo_id}_{self.repo_chat_counts[abs_path]}"
        self.repo_id = repo_id

        data[repo_id] = {'path': abs_path, 'history': []}
        self.save_data(data)

        gitwhisper_ai.open_repository(abs_path)
        gitwhisper_ai.start_chat()

        if not getattr(self, 'last_chat_button', None):
            self.last_chat_button = self.new_chat_button

        button = QPushButton(self.last_chat_button.parent())
        button.setObjectName(f'chat_button_{repo_id}')
        button.setText(f'{repo_id.split('_')[-1]} {abs_path}')
        button.setToolTip(f'{repo_id.split('_')[-1]} {abs_path}')
        button.setGeometry(
            self.last_chat_button.geometry().x(),
            self.last_chat_button.geometry().y() + self.last_chat_button.geometry().height() + 6,
            self.last_chat_button.geometry().width(),
            self.last_chat_button.geometry().height()
        )
        button.setStyleSheet(self.last_chat_button.styleSheet())
        button.clicked.connect(self.select_chat)
        button.setCursor(self.last_chat_button.cursor())

        setattr(self, f'chat_button_{repo_id}', button)
        button = getattr(self, f'chat_button_{repo_id}')
        button.show()

        self.last_chat_button = button

        self.load_chat_history(repo_id)

    def load_chats_list(self):
        data = self.get_data()

        if data == {}:
            self.new_chat_dialog_page(cancel_allowed=False)
            return

        for repo_id, properties in data.items():
            abs_path = properties['path']
            if not getattr(self, 'last_chat_button', None):
                self.last_chat_button = self.new_chat_button

            button = QPushButton(self.last_chat_button.parent())
            button.setText(f'{repo_id.split('_')[-1]} {abs_path}')
            button.setToolTip(f'{repo_id.split('_')[-1]} {abs_path}')
            button.setGeometry(
                self.last_chat_button.geometry().x(),
                self.last_chat_button.geometry().y() + self.last_chat_button.geometry().height() + 6,
                self.last_chat_button.geometry().width(),
                self.last_chat_button.geometry().height()
            )
            button.setStyleSheet(self.last_chat_button.styleSheet())
            button.setCursor(self.last_chat_button.cursor())
            button.setObjectName(f'chat_button_{repo_id}')
            button.clicked.connect(self.select_chat)

            setattr(self, f'chat_button_{repo_id}', button)
            button = getattr(self, f'chat_button_{repo_id}')
            button.show()

            self.last_chat_button = button

    def load_chat_history(self, repo_id):
        data = self.get_data()

        for child in self.chat_area.widget().children():
            if child in (self.bot_message, self.user_message):
                continue
            child.setParent(None)
            del child

        if getattr(self, 'last_message', None):
            del self.last_message

        history = data[repo_id]['history']
        gitwhisper_ai.open_repository(data[repo_id]['path'])
        gitwhisper_ai.start_chat(history)

        def remove_context(msg):
            start = msg.find('[[== Context ==]]\n')
            end = msg.rfind('[[== END Context ==]]\n') + len('[[== END Context ==]]\n')

            if start == -1 or end == -1:
                return msg
            
            return msg[:start] + msg[end:]
        
        for i in history:
            self.add_message_ui(remove_context(i.parts[0].text), 'bot' if i.role == 'model' else 'user')

    def add_message_ui(self, message, role):
        if role not in ("user", "bot"):
            return
        
        if not getattr(self, 'last_message', None):
            if role == 'user':
                msg = self.user_message
                msg.setMarkdown(message)
                msg.show()
                msg.parent().update()
                self.last_message = msg
                return

        msg = getattr(self, f'{role}_message')

        msg_id = str(uuid.uuid4()).replace('-', '_')
        
        message_ = AutoResizeTextEdit(self.scrollAreaWidgetContents, padding=4)
        message_.setObjectName(f"{role}_message_{msg_id}")
        message_.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        message_.setGeometry(QRect(
            msg.x(), self.last_message.y() + self.last_message.height() + 6, 400, 32
        ))
        message_.setStyleSheet(msg.styleSheet())
        message_.setMarkdown(message)
        message_.setUndoRedoEnabled(False)
        message_.setReadOnly(True)
        message_.keypressed.connect(self.remove_scroll)

        setattr(self, f"{role}_message_{msg_id}", message_)
        message_ = getattr(self, f"{role}_message_{msg_id}")
        message_.show()
        message_.parent().update()
                
        self.last_message = message_

    def send_message(self):
        data = self.get_data()
        message = self.message_input.toPlainText()
        self.message_input.clear()
        self.add_message_ui(message, 'user')
        
        def save_message(resp):
            self.add_message_ui(resp, 'bot')
            data[self.repo_id]['history'] = gitwhisper_ai.chat.history
            self.save_data(data)

        self.thread = GetResponseThread(message)
        self.thread.start()
        self.thread.finished.connect(save_message)

    def new_chat_dialog_page(self, *, cancel_allowed = True):
        self.open_new_chat_dialog(cancel_allowed=cancel_allowed)

        self.repo_path_input.setText('')

        def check():
            path_str = self.repo_path_input.text().replace('\\', '/').strip()
            repo_path = FormatedPath(
                path_str
                + ('/' if not path_str.endswith('/') else '')
            )
            if repo_path.exists() and repo_path.is_dir() and \
               (repo_path / '.git').exists() and (repo_path / '.git').is_dir() and \
               path_str != '':
                self.new_chat_dialog_confirm_button.setEnabled(True)
            else:
                self.new_chat_dialog_confirm_button.setEnabled(False)
        
        self.repo_path_input.textEdited.connect(check)
        self.new_chat_dialog_confirm_button.clicked.connect(
            lambda: self.new_chat(FormatedPath(
                (path_str := self.repo_path_input.text().replace('\\', '/'))
                + ('/' if not path_str.endswith('/') else '')
            )))
        self.repo_path_input.returnPressed.connect(
            lambda: self.new_chat(FormatedPath(
                (path_str := self.repo_path_input.text().replace('\\', '/'))
                + ('/' if not path_str.endswith('/') else '')
            )))
        
    def message_input_check(self, event):
        if self.message_input.toPlainText().strip() != '' and \
           event.key() == Qt.Key_Return and not event.modifiers():
            self.MainWindow.sender().accept_event = True
            self.send_message()

    def to_startup_page(self):
        self.reset_page()

        self.new_chat_button.clicked.connect(self.new_chat_dialog_page)
        self.send_message_button.clicked.connect(self.send_message)
        self.message_input.keypressed.connect(self.message_input_check)

app = GitWhisperApp()
app.start()