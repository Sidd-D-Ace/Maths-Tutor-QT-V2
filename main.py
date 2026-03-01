import sys, os, subprocess
from PyQt5 import sip

# ── Accessibility: Enable the Qt5 ↔ AT-SPI bridge for Linux screen readers ──
os.environ["QT_LINUX_ACCESSIBILITY_ALWAYS_ON"] = "1"
os.environ["QT_ACCESSIBILITY"] = "1"

if sys.platform.startswith("linux"):
    os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
    try:
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.interface",
             "toolkit-accessibility", "true"],
            check=False, timeout=3, capture_output=True,
        )
    except FileNotFoundError:
        pass  

    _sys_plugins_dir = "/usr/lib/x86_64-linux-gnu/qt5/plugins"
    if os.path.isdir(_sys_plugins_dir):
        os.environ.setdefault("QT_PLUGIN_PATH", _sys_plugins_dir)
        os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", os.path.join(_sys_plugins_dir, "platforms"))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QDialog, QVBoxLayout,
    QPushButton, QComboBox, QHBoxLayout, QCheckBox, QFrame,
    QWidget, QGridLayout,QStackedWidget, QSizePolicy, QShortcut, QMessageBox
)
from PyQt5.QtCore import Qt,QUrl, QSize, QTimer
from question.loader import QuestionProcessor
from pages.shared_ui import create_footer_buttons, apply_theme, SettingsDialog, create_main_footer_buttons,QuestionWidget,setup_exit_handling 
from pages.ques_functions import load_pages, upload_excel   
from tts.tts_worker import TextToSpeech

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from language.language import get_saved_language, save_selected_language_to_file, tr, set_language

from PyQt5.QtGui import QMovie, QKeySequence, QPixmap, QFont, QIcon


class RootWindow(QDialog):
    def __init__(self,minimal=False):
        super().__init__()
        self.minimal = minimal
        self.remember=False
        self.setWindowTitle("Maths Tutor - Language Selection Window")
        self.setFixedSize(400, 250 if not self.minimal else 150)
        self.init_ui()
        self.load_style("language_dialog.qss")
        self.closeEvent = lambda event: event.accept()
 
    def init_ui(self):
        layout = QVBoxLayout()

        if not self.minimal:
            title_label = QLabel("Welcome to Maths Tutor!")
            title_label.setProperty("class", "title")
            title_label.setAccessibleName("Welcome to Maths Tutor")
            layout.addWidget(title_label)
            layout.addSpacing(15)

        language_label = QLabel("Select your preferred language:")
        language_label.setProperty("class", "subtitle")
 
        languages = ["English", "हिंदी", "മലയാളം", "தமிழ்", "عربي", "संस्कृत"]
        self.language_combo = QComboBox()
        self.language_combo.addItems(languages)
        self.language_combo.setProperty("class", "combo-box")
        
        language_label.setBuddy(self.language_combo)
        self.language_combo.setAccessibleName("Language Selection")
        self.language_combo.setAccessibleDescription("Choose from English, Hindi, Malayalam, Tamil, Arabic, or Sanskrit")
        
        layout.addWidget(language_label)
        layout.addWidget(self.language_combo)

        if not self.minimal:
            self.remember_check = QCheckBox("Remember my selection")
            self.remember_check.setChecked(False)
            self.remember_check.setProperty("class", "checkbox")
            self.remember_check.setStyleSheet("color: #ffffff;")
            self.remember_check.setAccessibleName("Remember my selection")
            self.remember_check.setAccessibleDescription("If checked, the app will skip this dialog next time")
            layout.addWidget(self.remember_check)
        
        layout.addStretch()

        if not self.minimal:
            layout.addWidget(self.create_line())
        self.ok_button = QPushButton("Continue")
        self.ok_button.setDefault(True)
        self.ok_button.setAutoDefault(True)
        QTimer.singleShot(100, lambda: self.language_combo.setFocus())
        self.ok_button.setAccessibleName("Continue")
        self.ok_button.setAccessibleDescription("Confirm language selection and continue to the app")

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setAutoDefault(False)
        self.cancel_button.setShortcut(Qt.Key_Escape)
        self.cancel_button.setProperty("class", "danger-button")
        self.cancel_button.setAccessibleName("Cancel")
        self.cancel_button.setAccessibleDescription("Close the dialog without selecting a language")

        btns = QHBoxLayout()
        btns.addStretch()
        btns.addWidget(self.cancel_button)
        btns.addWidget(self.ok_button)
        layout.addLayout(btns)
 
        self.setLayout(layout)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self.handle_continue)

        QWidget.setTabOrder(self.language_combo, self.ok_button)
        if not self.minimal:
            QWidget.setTabOrder(self.language_combo, self.remember_check)
            QWidget.setTabOrder(self.remember_check, self.ok_button)
        QWidget.setTabOrder(self.ok_button, self.cancel_button)

    def handle_continue(self):
        selected = self.language_combo.currentText()
        set_language(selected)
        print("Language selected:", selected)
        self.remember = (hasattr(self, 'remember_check') and self.remember_check.isChecked()) if not self.minimal else False

        if self.remember:
            print("self.remember working")
            save_selected_language_to_file(selected)
        self.accept()

    def create_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line
 
    def load_style(self, qss_file):
        style_path = os.path.join("styles", qss_file)
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())
 
 
class MainWindow(QMainWindow):
    def __init__(self, language="English"):
        super().__init__()
        
        # ✅ BUG FIX: Set global language on startup so it applies everywhere
        self.language = language
        set_language(self.language)

        self.setWindowTitle(f"Maths Tutor - {self.language}")
        self.resize(900, 600)
        self.setMinimumSize(800, 550) 
        self.current_difficulty = 1  
        self.section_pages = {} 
        self.is_muted = False
        
        setup_exit_handling(self, require_confirmation=True)
        self.init_ui()

        self.tts = TextToSpeech()
        self.load_style("main_window.qss")
        self.current_theme = "light"  


        self.media_player = QMediaPlayer()
        self.bg_player = QMediaPlayer()
        self.bg_player.setVolume(30)
        self.is_muted = False 
        self.play_background_music()

        self.difficulty_index = 1 

    def refresh_ui(self, new_language):
        """Rebuilds the entire UI with the new language WITHOUT closing the window."""
        print(f"[System] Refreshing UI to {new_language}...")
        
        # ✅ BUG FIX: Ensure new language is set globally before redrawing
        self.language = new_language
        set_language(new_language)
        
        self.setWindowTitle(f"Maths Tutor - {self.language}")

        if hasattr(self, 'tts'):
            self.tts.stop()
        
        # ✅ BUG FIX: Clear stale widget references before init_ui destroys old central widget
        self.section_pages = {}
        if hasattr(self, 'game_mode_container'):
            del self.game_mode_container
        if hasattr(self, '_quickplay_question_widget'):
            del self._quickplay_question_widget
        if hasattr(self, 'quickplay_container'):
            del self.quickplay_container
        
        self.init_ui()
        
        apply_theme(self.central_widget, self.current_theme)

    def init_ui(self):
        self.central_widget = QWidget()
        self.central_widget.setProperty("class", "central-widget")
        self.central_widget.setProperty("theme", "light")
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.current_theme = "light"

        self.theme_button = QPushButton("🌙")
        self.theme_button.setToolTip("Toggle Light/Dark Theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setAccessibleName("Toggle theme. Currently light mode")
        self.theme_button.setAccessibleDescription("")
        self.theme_button.setProperty("class", "menu-button")
        self.theme_button.setFocusPolicy(Qt.TabFocus)

        self.top_bar = QWidget()
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        self.top_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.top_bar_layout.setSpacing(10)
        self.top_bar_layout.addWidget(self.theme_button, alignment=Qt.AlignLeft)
        self.top_bar_layout.addStretch()

        self.main_layout.addWidget(self.top_bar)

        self.menu_widget = QWidget()
        menu_layout = QVBoxLayout()
        menu_layout.setSpacing(10)
        menu_layout.setAlignment(Qt.AlignTop)

        title = QLabel(tr("welcome"))
        title.setAlignment(Qt.AlignCenter)
        title.setProperty("class", "main-title")

        subtitle = QLabel(tr("ready").format(lang=self.language))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setProperty("class", "subtitle")

        menu_layout.addWidget(title)
        menu_layout.addWidget(subtitle)
        menu_layout.addSpacing(20)

        menu_layout.addLayout(self.create_buttons())
        menu_layout.addSpacing(10)
        menu_layout.addStretch()

        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setAccessibleName("")
        self.gif_label.setAccessibleDescription("")
        self.movie = QMovie("images/welcome-1.gif")
        self.movie.setScaledSize(QSize(150, 150))
        self.gif_label.setMovie(self.movie)
        self.movie.start()

        gif_container = QWidget()
        gif_layout = QHBoxLayout()
        gif_layout.setContentsMargins(0, 0, 0, 0)
        gif_layout.addStretch()
        gif_layout.addWidget(self.gif_label, alignment=Qt.AlignCenter)
        gif_layout.addStretch()
        gif_container.setLayout(gif_layout)

        menu_layout.addWidget(gif_container)
        self.menu_widget.setLayout(menu_layout)

        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stack.setAccessibleName("Content area")

        self.startup_widget = self.create_mode_selection_page()
        self.stack.addWidget(self.startup_widget)  
        
        self.stack.addWidget(self.menu_widget)     

        self.stack.setCurrentWidget(self.startup_widget)

        self.main_layout.addWidget(self.stack)

        self.main_footer = create_main_footer_buttons(self)   
        self.section_footer = self.create_section_footer()     

        for footer in (self.main_footer, self.section_footer):
            footer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            footer.setMinimumHeight(63)

        self.main_layout.addWidget(self.main_footer)
        self.main_layout.addWidget(self.section_footer)
    
        self.section_footer.hide()

        back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
        if back_btn:
            back_btn.hide()

        apply_theme(self.central_widget, self.current_theme)
            
        self.focus_story_button()
        self.focus_quickplay_button()

    def focus_story_button(self):
        for btn in self.menu_buttons:
            if btn.text() == tr("Story"):
                btn.setFocus()
                break
            
    def focus_quickplay_button(self):
        if hasattr(self, "quickPlayButton") and self.quickPlayButton:
            self.quickPlayButton.setFocus()

    def create_mode_selection_page(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        widget.setLayout(layout)

        label = QLabel(tr("Choose Mode"))
        label.setAlignment(Qt.AlignCenter)
        label.setProperty("class", "main-title")
        label.setAccessibleName("Choose Mode Menu")
        layout.addWidget(label)

        buttons = [
            (tr("⚡Quickplay"), self.start_quickplay_mode),
            (tr("🎮 Game Mode"), self.start_game_mode),
            (tr("🎓 Learning Mode"), self.start_learning_mode)
        ]
        for text, callback in buttons:
            btn = QPushButton(text)
            btn.setMinimumSize(240, 65)
            btn.setProperty("class", "menu-button")
            btn.setProperty("theme", self.current_theme)
            btn.clicked.connect(callback)
            
            clean_text = text.replace("⚡", "").replace("🎮", "").replace("🎓", "").strip()
            btn.setAccessibleName(clean_text)
            btn.setAccessibleDescription(f"Start {clean_text}")
            
            layout.addWidget(btn)
            
            if "Quickplay" in text or "त्वरित" in text or "Quickplay" in clean_text:
                self.quickPlayButton = btn

        return widget

    def start_learning_mode(self):
        self.stack.setCurrentWidget(self.menu_widget)
        self.main_footer.show()
        self.section_footer.hide()
        back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
        if back_btn:
            back_btn.show()
        self.play_sound("click-button.wav")

    def start_game_mode(self):
        if hasattr(self, "game_mode_container"):
            self.stack.setCurrentWidget(self.game_mode_container)
            self.main_footer.show()      
            self.section_footer.hide()   
            back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
            if back_btn:
                back_btn.show()
            return

        self.game_mode_container = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.game_mode_container.setLayout(layout)

        title_label = QLabel(tr("Select Game Difficulty"))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setProperty("class", "main-title")
        layout.addWidget(title_label)

        subtitle_label = QLabel(tr("Choose your challenge level"))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setProperty("class", "subtitle")
        layout.addWidget(subtitle_label)

        difficulties = [(tr("Easy"), 1), (tr("Medium"), 2), (tr("Hard"), 3), (tr("Extra Hard"), 4)]
        for text, index in difficulties:
            btn = QPushButton(text)
            btn.setMinimumSize(260, 70)
            btn.setProperty("class", "menu-button")
            btn.setProperty("theme", self.current_theme)
            btn.clicked.connect(lambda _, idx=index: self.load_game_questions(idx))
            btn.setAccessibleName(f"{text} difficulty")
            btn.setAccessibleDescription(f"Start game at {text} difficulty level")
            layout.addWidget(btn)

        mole_label = QLabel()
        mole_label.setPixmap(QPixmap("assets/mole.png").scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        mole_label.setAlignment(Qt.AlignCenter)
        mole_label.setAccessibleName("")
        mole_label.setAccessibleDescription("")
        layout.addWidget(mole_label)

        self.stack.addWidget(self.game_mode_container)
        self.stack.setCurrentWidget(self.game_mode_container)

        self.main_footer.show()
        self.section_footer.hide()   
        back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
        if back_btn:
            back_btn.show()

        apply_theme(self.game_mode_container, self.current_theme)

    def load_game_questions(self, difficulty_index):
        import random

        self.clear_main_layout()

        self.game_types = ["Multiplication", "Percentage", "Division", "Currency", "Story", "Time", "Distance", "Bellring","Addition", "Subtraction", "Remainder"]
        self.game_difficulty = difficulty_index

        random_type = random.choice(self.game_types)
        print("[load_game_question] current random type:", random_type)
        processor = QuestionProcessor(random_type, difficultyIndex=self.game_difficulty)
        processor.process_file()

        def load_next_question():
            new_type = random.choice(self.game_types)
            print("[load_game_question] current random type:", new_type)
            new_processor = QuestionProcessor(new_type, difficultyIndex=self.game_difficulty)
            new_processor.process_file()
            question_widget.processor = new_processor
            question_widget.load_new_question()

        question_widget = QuestionWidget(processor, window=self, next_question_callback=load_next_question, tts=self.tts)
        self.main_layout.addWidget(question_widget)

    def start_quickplay_mode(self):
        self._proceed_to_quickplay()

    def _proceed_to_quickplay(self):
        if hasattr(self, 'tts'):
            self.tts.stop()

        self.main_footer.show()
        self.section_footer.hide()

        upload_btn = self.main_footer.findChild(QPushButton, tr("Upload").lower().replace(" ", "_"))
        if upload_btn:
            upload_btn.hide()

        back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
        if back_btn:
            back_btn.show()

        if not hasattr(self, "quickplay_container"):
            self.quickplay_container = QWidget()
            self.quickplay_container.setAccessibleName("")
            self.quickplay_container.setAccessibleDescription("")
            quickplay_layout = QVBoxLayout()
            self.quickplay_container.setLayout(quickplay_layout)
            self.stack.addWidget(self.quickplay_container)

        if hasattr(self, '_quickplay_question_widget') and self._quickplay_question_widget:
            processor = QuestionProcessor("Story", difficultyIndex=[0, 1])
            processor.process_file()
            self._quickplay_question_widget.processor = processor
            self._quickplay_question_widget.load_new_question()
            self.stack.setCurrentWidget(self.quickplay_container)
            return

        processor = QuestionProcessor("Story", difficultyIndex=[0, 1])
        processor.process_file()

        def load_next_question():
            new_processor = QuestionProcessor("Story", difficultyIndex=[0, 1])
            new_processor.process_file()
            self._quickplay_question_widget.processor = new_processor
            self._quickplay_question_widget.load_new_question()

        self._quickplay_question_widget = QuestionWidget(processor, window=self, next_question_callback=load_next_question, tts=self.tts)
        self.quickplay_container.layout().addWidget(self._quickplay_question_widget)
        self.stack.setCurrentWidget(self.quickplay_container)
        apply_theme(self.quickplay_container, self.current_theme)

    def play_sound(self, filename):
        if self.is_muted:
            return
        
        filepath = os.path.abspath(os.path.join("sounds", filename))
        if os.path.exists(filepath):
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(filepath)))
            self.media_player.play()
        else:
            print(f"[SOUND ERROR] File not found: {filepath}")
    
    def play_background_music(self):
        if self.is_muted:
            return

        filepath = os.path.abspath(os.path.join("sounds", "backgroundmusic.mp3"))
        if os.path.exists(filepath):
            self.bg_player.setMedia(QMediaContent(QUrl.fromLocalFile(filepath)))
            self.bg_player.setVolume(10)
            self.bg_player.play()
            if not getattr(self, '_bg_loop_connected', False):
                self.bg_player.mediaStatusChanged.connect(self.loop_background_music)
                self._bg_loop_connected = True
        else:
            print("[BG MUSIC ERROR] File not found:", filepath)

    def loop_background_music(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.bg_player.setPosition(0)
            self.bg_player.play()
    
    def create_audio_button(self):
        self.audio_button = QPushButton("🔊")
        self.audio_button.setObjectName("audio-button")
        self.audio_button.setToolTip("Toggle Mute/Unmute")
        self.audio_button.clicked.connect(self.toggle_audio)
        self.audio_button.setProperty("class", "footer-button")
        self.audio_button.setFocusPolicy(Qt.StrongFocus)
        self.audio_button.setAccessibleName("Audio Unmuted")
        self.audio_button.setAccessibleDescription("Toggle mute and unmute for sounds and music")
        return self.audio_button

    def set_mute(self, state: bool):
        self.is_muted = state
        if hasattr(self, 'bg_player') and self.bg_player is not None:
            if state:
                self.bg_player.pause()  
            else:
                self.play_background_music()

    def toggle_audio(self):
        new_state = not self.is_muted
        self.set_mute(new_state)
        
        # ✅ FIX RETAINED: Sync all audio buttons across the app
        icon_text = "🔇" if new_state else "🔊"
        accessible_name = "Audio Muted" if new_state else "Audio Unmuted"

        for btn in self.findChildren(QPushButton, "audio-button"):
            btn.setText(icon_text)
            btn.setAccessibleName(accessible_name)

        print("[AUDIO]", "Muted" if new_state else "Unmuted")
        
    def create_buttons(self):
        button_grid = QGridLayout() 
        button_grid.setSpacing(12)
        button_grid.setContentsMargins(6, 6, 6, 6)

        sections = ["Story", "Time", "Currency", "Distance", "Bellring", "Operations"]
        self.menu_buttons = []

        for i, name in enumerate(sections):
            translated_name = tr(name)
            button = QPushButton(translated_name)
            button.setMinimumSize(160, 45)
            button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            button.setProperty("class", "menu-button")
            button.setAccessibleName(translated_name)
            button.clicked.connect(lambda checked, n=name: self.load_section(n))

            self.menu_buttons.append(button)
            row, col = divmod(i, 3)
            button_grid.addWidget(button, row, col)

        return button_grid
    
    def create_section_footer(self):
        buttons = ["Back to Operations", "Back to Home", "Settings"]
        translated = [tr(b) for b in buttons]

        callbacks = {
            tr("Back to Operations"): lambda: self.load_section("Operations"),
            tr("Back to Home"): self.back_to_home,
            tr("Settings"): self.handle_settings
        }

        footer = create_footer_buttons(translated, callbacks=callbacks)

        # ✅ FIX RETAINED: Audio button in section footer
        audio_btn = self.create_audio_button()
        footer.layout().insertWidget(0, audio_btn, alignment=Qt.AlignLeft)

        for btn in footer.findChildren(QPushButton):
            if btn.text() == tr("Back to Operations"):
                btn.setObjectName("back_to_operations")
            elif btn.text() == tr("Back to Home"):
                btn.setObjectName("back_to_home")

        return footer

    def handle_settings(self):
        dialog = SettingsDialog(
            parent=self,
            initial_difficulty=getattr(self, "current_difficulty", 1),
            main_window=self
        )

        if dialog.exec_() == QDialog.Accepted:
            self.current_difficulty = dialog.get_difficulty_index()
            new_language = dialog.get_selected_language()
            
            # ✅ FIX: Refresh the entire UI immediately if language changes
            if new_language != self.language:
                self.refresh_ui(new_language)

    def load_section(self, name):
        if hasattr(self, 'tts'):
            self.tts.stop()
        print(f"[INFO] Loading section: {name}")

        page = load_pages(name, self.back_to_main_menu,  difficulty_index=self.current_difficulty, main_window=self, tts=self.tts)

        if hasattr(self, "current_theme"):
            page.style().unpolish(page)
            page.style().polish(page)
            apply_theme(page, self.current_theme)

        if name in self.section_pages:
            old_page = self.section_pages[name]
            if not sip.isdeleted(old_page):
                self.stack.removeWidget(old_page)
                old_page.deleteLater()
            del self.section_pages[name]

        self.section_pages[name] = page
        self.stack.addWidget(page)

        self.stack.setCurrentWidget(page)
        self.menu_widget.hide()
        self.main_footer.hide()
        self.section_footer.show()
        self.update_back_to_operations_visibility(name)
    
    def back_to_main_menu(self):
        self.top_bar.show()  
        current_page = self.stack.currentWidget()
        if current_page:
            question_widget = current_page.findChild(QuestionWidget)
            if question_widget:
                question_widget.stop_all_activity()

        if hasattr(self, 'tts'):
            self.tts.stop()
            self.tts.reset()
        self.play_sound("home_button_sound.wav")
        self.stack.setCurrentWidget(self.startup_widget)  
        self.section_footer.hide()
        self.main_footer.show()
        
        upload_btn = self.main_footer.findChild(QPushButton, tr("Upload").lower().replace(" ", "_"))
        if upload_btn:
            upload_btn.show()
        
        back_btn = self.main_footer.findChild(QPushButton, tr("Back to Menu").lower().replace(" ", "_"))
        if back_btn:
            back_btn.hide()
        self.focus_quickplay_button()
        
    def back_to_home(self):
        # ✅ FIX RETAINED: "Back to Home" for Uploaded Quizzes goes to Mode Selection
        if isinstance(self.stack.currentWidget(), QuestionWidget):
            self.back_to_main_menu()
            return

        self.top_bar.show()  
        current_page = self.stack.currentWidget()
        if current_page:
            question_widget = current_page.findChild(QuestionWidget)
            if question_widget:
                question_widget.stop_all_activity()

        if hasattr(self, 'tts'):
            self.tts.stop()
            self.tts.reset()
        self.stack.setCurrentWidget(self.menu_widget)     
        self.section_footer.hide()                        
        self.main_footer.show()                           
        
        upload_btn = self.main_footer.findChild(QPushButton, tr("Upload").lower().replace(" ", "_"))
        if upload_btn:
            upload_btn.show()

    def clear_main_layout(self):
        for i in reversed(range(self.main_layout.count())):
            widget = self.main_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def handle_upload(self):
        upload_excel(self)

    def load_style(self, qss_file):
        path = os.path.join("styles", qss_file)
        if os.path.exists(path):
            with open(path, "r") as f:
                self.setStyleSheet(f.read())

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        print("Theme switched to:", self.current_theme)
        self.theme_button.setText("☀️" if self.current_theme == "dark" else "🌙")
        self.theme_button.setAccessibleName(f"Toggle theme. Currently {self.current_theme} mode")
        apply_theme(self.central_widget, self.current_theme)

    def update_back_to_operations_visibility(self, section_name):
        operation_subsections = {
            "addition", "subtraction", "multiplication",
            "division", "remainder", "percentage"
        }
        normalized = section_name.strip().lower()
        back_to_ops_btn = self.section_footer.findChild(QPushButton, "back_to_operations")
        if back_to_ops_btn:
            back_to_ops_btn.setVisible(normalized in operation_subsections)
    

if __name__ == "__main__":

    app = QApplication(sys.argv)
    style_file = os.path.join("styles", "app.qss")
    if os.path.exists(style_file):
        with open(style_file, "r") as f:
            app.setStyleSheet(f.read())
 
    lang = get_saved_language()
    if lang:
        print("Saved language found:", lang)
        window = MainWindow(language=lang)
        window.show()
        window.activateWindow()
        window.raise_()
        sys.exit(app.exec_())
    else:
        dialog = RootWindow()
        if dialog.exec_() == QDialog.Accepted:
            window = MainWindow(language=dialog.language_combo.currentText())
            window.show()
            window.activateWindow()
            window.raise_()
            sys.exit(app.exec_())