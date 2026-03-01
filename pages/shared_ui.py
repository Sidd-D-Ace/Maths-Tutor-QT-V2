# pages/shared_ui.py

from PyQt5.QtWidgets import ( QWidget, QLabel, QHBoxLayout, QPushButton,
                              QVBoxLayout,QSizePolicy, QDialog, QSlider, QDialogButtonBox
                              ,QSpacerItem,QLineEdit,QMessageBox,QApplication,QShortcut )

from PyQt5.QtCore import Qt, QSize, QPoint, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QKeySequence, QIcon
from PyQt5.QtCore import QPropertyAnimation, QSequentialAnimationGroup
from question.loader import QuestionProcessor
from time import time
import random 
from tts.tts_worker import TextToSpeech
from PyQt5.QtMultimedia import QSound



DIFFICULTY_LEVELS = ["Simple", "Easy", "Medium", "Hard", "Challenging"]

from language.language import set_language,clear_remember_language,tr

from language.language import tr
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtGui import QMovie

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer

def create_entry_ui(main_window) -> QWidget:
    entry_widget = QWidget()
    entry_widget.setProperty("theme", main_window.current_theme) 
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignCenter)

    label = QLabel("Click below to start the quiz")
    label.setFont(QFont("Arial", 24))
    label.setAlignment(Qt.AlignCenter)
    # ✅ ACCESSIBILITY: Screen reader announces instruction
    label.setAccessibleName("Click below to start the quiz")

    def start_quiz():
        print("Start button clicked")  # ✅ DEBUG POINT
        from pages.ques_functions import start_uploaded_quiz
        start_uploaded_quiz(main_window)
    
    button = create_menu_button("Start", start_quiz)
    # BUG FIX: Removed duplicate button.clicked.connect(start_quiz) — already connected in create_menu_button
    # ✅ ACCESSIBILITY: Clear accessible name for start button
    button.setAccessibleName("Start Quiz")
    button.setAccessibleDescription("Begin the uploaded quiz")

    layout.addWidget(label)
    layout.addSpacing(20)
    layout.addWidget(button, alignment=Qt.AlignCenter)

    entry_widget.setLayout(layout)
    apply_theme(entry_widget, main_window.current_theme)
    return entry_widget






# settings_manager.py
class SettingsManager:
    def __init__(self):
        self.difficulty_index = 1  # default Medium
        self.language = "English"

    def set_difficulty(self, index):
        self.difficulty_index = index

    def get_difficulty(self):
        return self.difficulty_index

    def set_language(self, lang):
        self.language = lang

    def get_language(self):
        return self.language


# Singleton instance to be imported anywhere
settings = SettingsManager()


def create_colored_widget(color: str = "#ffffff") -> QWidget:
    widget = QWidget()
    palette = widget.palette()
    palette.setColor(QPalette.Window, QColor(color))
    widget.setAutoFillBackground(True)
    widget.setPalette(palette)
    return widget

def create_label(text: str, font_size=16, bold=True) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)  # allow wrapping of long text
    label.setAlignment(Qt.AlignCenter)  # center text
    font = QFont("Arial", font_size)
    font.setBold(bold)
    label.setFont(font)
    label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  # allow resizing
    return label
   

def create_colored_page(title: str, color: str = "#d0f0c0") -> QWidget:
    page = create_colored_widget(color)
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignCenter)

    title_label = create_label(title, font_size=20)
    answer_input = create_answer_input()

    layout.addWidget(title_label)
    layout.addSpacing(20)
    layout.addWidget(answer_input)

    page.setLayout(layout)
    return page


def create_menu_button(text, callback):
    button = QPushButton(text)
    button.setFixedSize(200, 40)
    button.setProperty("class", "menu-button")
    # ✅ ACCESSIBILITY: Screen reader announces button text
    button.setAccessibleName(text)
    button.clicked.connect(callback)
    return button

def create_vertical_layout(widgets: list) -> QVBoxLayout:
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignTop)  # Align to top so everything is visible
    for widget in widgets:
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(widget)
    return layout
   
def create_footer_buttons(names, callbacks=None, size=(90, 30)) -> QWidget:
    footer = QWidget()
    layout = QHBoxLayout()
    layout.setSpacing(10)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addStretch()

    for name in names:
        btn = QPushButton(name)
        btn.setObjectName(name.lower().replace(" ", "_"))
        btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        btn.adjustSize() 
        btn.setFont(QFont("Arial", 14))  # or bigger
        btn.setProperty("class", "footer-button")
        # ✅ ACCESSIBILITY: Screen reader announces button name
        btn.setAccessibleName(name)
        if callbacks and name in callbacks:
            btn.clicked.connect(callbacks[name])
        layout.addWidget(btn)

    footer.setLayout(layout)
    return footer

def create_main_footer_buttons(self):
        buttons = ["Back to Menu", "Upload", "Settings"]
        translated = {tr(b): b for b in buttons}  

        footer = create_footer_buttons(
            list(translated.keys()),
            callbacks={
                tr("Back to Menu"): self.back_to_main_menu,
                tr("Upload"): self.handle_upload,
                tr("Settings"): self.handle_settings
            }
        )

        audio_btn = self.create_audio_button()
        footer.layout().insertWidget(0, audio_btn, alignment=Qt.AlignLeft)
        return footer

def create_answer_input(width=300, height=40, font_size=14) -> QLineEdit:
    input_box = QLineEdit()
    input_box.setFixedSize(width, height)
    input_box.setAlignment(Qt.AlignCenter)
    input_box.setPlaceholderText(tr("Enter your answer"))
    input_box.setFont(QFont("Arial", font_size))
    input_box.setProperty("class", "answer-input")
    return input_box

def wrap_center(widget):
    container = QWidget()
    layout = QHBoxLayout()
    layout.addStretch()             # Push from the left
    layout.addWidget(widget)        # The centered widget
    layout.addStretch()             # Push from the right
    container.setLayout(layout)
    return container

# In pages/shared_ui.py

# In pages/shared_ui.py
# In pages/shared_ui.py

def setup_exit_handling(window, require_confirmation=False):
    """
    Configures exit behavior.
    - Ctrl+Q: Quits the Application (asks for confirmation if enabled).
    - Window Close (X): Closes the window (asks for confirmation if enabled).
    """

    # 1. Define the Exit Logic
    def check_and_close(event=None):
        if require_confirmation:
            reply = QMessageBox.question(window, "Exit Application", "Are you sure you want to exit?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if event: event.accept()
                else: QApplication.quit()
            else:
                if event: event.ignore()
        else:
            # No confirmation needed
            if event: event.accept()
            else: QApplication.quit()

    # 2. Handle Ctrl+Q (Quit App)
    if hasattr(window, "quit_shortcut"): 
        # Remove old shortcut if it exists to avoid duplicates
        window.quit_shortcut.setParent(None)
        
    window.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), window)
    window.quit_shortcut.setContext(Qt.ApplicationShortcut)
    window.quit_shortcut.setWhatsThis("Press Ctrl+Q to quit the application")
    window.quit_shortcut.activated.connect(lambda: check_and_close(event=None))

    # 3. Handle X Button (Close Window)
    window.closeEvent = check_and_close




# In pages/shared_ui.py

class QuestionWidget(QWidget):
    def __init__(self, processor, window=None, next_question_callback=None, tts=None):
        super().__init__()
        # ✅ ACCESSIBILITY: Prevent NVDA from announcing this container as "grouping"
        self.setAccessibleName("")
        self.setAccessibleDescription("")
        self.processor = processor
        self.answer = None
        self.start_time = time()
        self.next_question_callback = next_question_callback
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.main_window = window
        self.setProperty("theme", window.current_theme)
        if tts:
            self.tts = tts
        else:
            self.tts = TextToSpeech()
        self._question_count = 0  # Track question number for TTS timing
        self.is_bell_mode = (processor.questionType.lower() == "bellring")
        self.bell_press_count = 0
        self._active = True  # Guard flag for stale QTimer callbacks
        self.init_ui()
       
    def init_ui(self):
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setProperty("class", "question-label")
        self.label.setWordWrap(True)

        if self.is_bell_mode:
            # ── Bell Ring Mode: button instead of text input ──
            self.input_box = None  # Guard for code that references input_box

            self.bell_button = QPushButton("")
            self.bell_button.setIcon(QIcon("images/bell.png"))
            self.bell_button.setIconSize(QSize(128, 128))
            self.bell_button.setMinimumSize(150, 150)
            self.bell_button.setFlat(True)
            self.bell_button.setStyleSheet("border: none; background: transparent;")
            self.bell_button.clicked.connect(self._on_bell_pressed)

            # Pause-detection timer (single-shot, 1.5s)
            self.bell_pause_timer = QTimer(self)
            self.bell_pause_timer.setSingleShot(True)
            self.bell_pause_timer.setInterval(1500)
            self.bell_pause_timer.timeout.connect(self._evaluate_bell_answer)
        else:
            # ── Standard Mode: text input ──
            self.bell_button = None
            self.bell_pause_timer = None

            self.input_box = create_answer_input()
            # FIX: Remove visual placeholder to stop "double reading" (Label + Placeholder)
            self.input_box.setPlaceholderText("")
            self.input_box.returnPressed.connect(self.check_answer)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setFont(QFont("Arial", 46))

        # Assemble layout (no wrapper QWidget — prevents NVDA "grouping" announcement)
        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.addWidget(self.label)
        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.addSpacing(20)
        if self.is_bell_mode:
            self.layout.addWidget(self.bell_button, alignment=Qt.AlignCenter)
        else:
            self.layout.addWidget(self.input_box, alignment=Qt.AlignCenter)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.result_label)
        self.layout.addStretch()

        self.gif_feedback_label = QLabel()
        self.gif_feedback_label.setVisible(False)
        self.gif_feedback_label.setAlignment(Qt.AlignCenter)
        self.gif_feedback_label.setScaledContents(True)
        self.gif_feedback_label.setMinimumSize(300, 300)
        self.gif_feedback_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # ✅ ACCESSIBILITY: Mark decorative feedback animation as hidden from screen readers
        self.gif_feedback_label.setAccessibleName("")
        self.gif_feedback_label.setAccessibleDescription("")

        self.layout.addWidget(self.gif_feedback_label, alignment=Qt.AlignCenter)

        self.load_new_question()

    def show_feedback_gif(self, sound_filename):
        if sound_filename == "question":
            gif_name = f"question-{random.choice([1, 2])}.gif"
        else:  
            gif_name = sound_filename.replace(".mp3", ".gif")
        gif_path = f"images/{gif_name}"

        movie = QMovie(gif_path)
        movie.setScaledSize(QSize(200, 200))
        self.gif_feedback_label.setFixedSize(200, 200)
        self.gif_feedback_label.setAlignment(Qt.AlignCenter)
        self.gif_feedback_label.setMovie(movie)
        self.gif_feedback_label.setVisible(True)
        movie.start()
            
    def hide_feedback_gif(self):
        self.gif_feedback_label.setVisible(False)
        self.gif_feedback_label.clear()

    def end_session(self):
        self.main_window.bg_player.stop()   
        if self.main_window:
            self.main_window.back_to_main_menu()

    def set_input_focus(self):
        # FIX: Only set focus if we actually LOST it.
        # Forcing focus on an already focused element causes screen readers to re-announce.
        if self.is_bell_mode:
            if self.bell_button and not self.bell_button.hasFocus():
                self.bell_button.setFocus()
        elif self.input_box:
            if not self.input_box.hasFocus():
                self.input_box.setFocus()

    def load_new_question(self):
        if hasattr(self, "gif_feedback_label"):
            self.hide_feedback_gif()

        question_text, self.answer = self.processor.get_questions()
        self._active = True  # Re-enable for new question
        self.start_time = time()

        # Update Visuals
        self.label.setText(question_text)

        if self.input_box:
            self.input_box.clear()
        self.result_label.setText("")
        self.show_feedback_gif("question")

        # Reset bell press counter for new question
        if self.is_bell_mode:
            self.bell_press_count = 0
            if self.bell_pause_timer and self.bell_pause_timer.isActive():
                self.bell_pause_timer.stop()
        
        # --- TTS START ---
        app_tts_active = False
        if self.main_window and not self.main_window.is_muted:
            app_tts_active = True
        
        print(f"[DEBUG] load_new_question type: '{self.processor.questionType}'")

        if self.processor.questionType.lower() == "bellring":
            print("[BellRing] Mode detected. Suppressing standard TTS.")
            app_tts_active = False

        if app_tts_active:
            # OPTION A: TTS IS ON
            if hasattr(self, 'tts'):
                tts_text = question_text + ". Type your answer"
                if self._question_count == 0:
                    # Brief delay for first question to let UI settle
                    QTimer.singleShot(500, lambda: self.tts.speak(tts_text))
                else:
                    # Subsequent questions: immediate TTS
                    self.tts.speak(tts_text)
                    
        # --- Bell Ring Question Audio ---
        if self.processor.questionType.lower() == "bellring":
             # Delay slightly to allow UI to settle if it's the first question, 
             # matching the TTS delay logic above
             delay = 500 if self._question_count == 0 else 100
             print(f"[BellRing] Scheduling sequence for: {question_text}")
             QTimer.singleShot(delay, lambda: self.play_bell_question_sequence(question_text))

        # Defer focus to the appropriate input widget
        if self.is_bell_mode:
            QTimer.singleShot(100, lambda: self.bell_button.setFocus(Qt.OtherFocusReason))
        elif self.input_box:
            QTimer.singleShot(100, lambda: self.input_box.setFocus(Qt.OtherFocusReason))

        self._question_count += 1
        # --- END ---

   
    def play_bell_sounds(self, count):
        if not hasattr(self, "bell_timer"):
            self.bell_timer = QTimer(self)
            self.bell_timer.timeout.connect(self.do_ring)
        self.current_ring = 0
        self.total_rings = count
        self.bell_timer.start(700)

    def stop_all_activity(self):
        self._active = False  # Prevent stale QTimer.singleShot callbacks

        if hasattr(self, "bell_timer") and self.bell_timer.isActive():
            self.bell_timer.stop()
        
        # Stop Bell Sequence Timer (Phase 1 & 3)
        if hasattr(self, "bell_seq_timer") and self.bell_seq_timer.isActive():
            self.bell_seq_timer.stop()
            
        # Stop Sequence Wait Timer (Phase 2 -> 3 transition)
        if hasattr(self, "seq_timer") and self.seq_timer.isActive():
            self.seq_timer.stop()

        # Stop Bell Pause Timer (user answer pause detection)
        if hasattr(self, "bell_pause_timer") and self.bell_pause_timer and self.bell_pause_timer.isActive():
            self.bell_pause_timer.stop()

    def do_ring(self):
        if self.current_ring < self.total_rings:
            QSound.play("sounds/click-button.wav")
            self.current_ring += 1
        else:
            self.bell_timer.stop()


    def check_answer(self):
            # ✅ Stop any ongoing bell sequences or audio immediately when user answers
            self.stop_all_activity()
            self._active = True  # Re-enable: user is answering, not navigating away

            if not self.input_box:
                return  # Bell mode uses _evaluate_bell_answer instead

            user_input = self.input_box.text().strip()
            elapsed = time() - self.start_time

            result = self.processor.submit_answer(user_input, self.answer, elapsed)

            if not result["valid"]:
                self.result_label.setText("Please enter a valid number.")
                self.result_label.setAccessibleName("Invalid input. Please enter a valid number.")
                return

            correct = result["correct"]

            app_audio_active = False
            if self.main_window and not self.main_window.is_muted:
                app_audio_active = True

            if correct:
                if hasattr(self, 'tts'): self.tts.stop()

                # Visual Feedback
                self.result_label.setText('<span style="font-size:16pt;">Correct!</span>')
                
                # Feedback Sound
                sound_index = random.randint(1, 3)
                if elapsed < 5: feedback_text = "🌟 Excellent"
                elif elapsed < 10: feedback_text = "👏 Very Good"
                elif elapsed < 15: feedback_text = "👍 Good"
                elif elapsed < 20: feedback_text = "👌 Not Bad"
                else: feedback_text = "🙂 Okay"
                
                self.result_label.setText(f'<span style="font-size:16pt;">{feedback_text}</span>')
                # ✅ ACCESSIBILITY: Update accessible name with clean feedback for screen readers
                clean_feedback = feedback_text.replace("🌟", "").replace("👏", "").replace("👍", "").replace("👌", "").replace("🙂", "").strip()
                self.result_label.setAccessibleName(f"Correct! {clean_feedback}")
                
                if app_audio_active:
                    if self.main_window:
                        sound_file = f"excellent-{sound_index}.mp3" 
                        if elapsed < 5: sound_file = f"excellent-{sound_index}.mp3"
                        elif elapsed < 10: sound_file =f"very-good-{sound_index}.mp3"
                        elif elapsed < 15: sound_file =f"good-{sound_index}.mp3"
                        elif elapsed < 20: sound_file =f"not-bad-{sound_index}.mp3"
                        else: sound_file =f"okay-{sound_index}.mp3"

                        self.main_window.play_sound(sound_file)
                        self.show_feedback_gif(sound_file)
                    
                    # ✅ TTS FEEDBACK: Announce feedback after a short delay
                    # (300ms lets the sound effect start first, avoids overlap)
                    if hasattr(self, 'tts'):
                        QTimer.singleShot(300, lambda t=clean_feedback: self.tts.speak(t))

                # Focus remains on Input Box. Screen reader says nothing extra.
                # Audio plays "Excellent".

                self.processor.retry_count = 0
                QTimer.singleShot(2000, self.call_next_question)

            else:
                self.processor.retry_count += 1
                self.result_label.setText('<span style="font-size:16pt;">Try Again.</span>')
                # ✅ ACCESSIBILITY: Update accessible name for screen readers
                self.result_label.setAccessibleName("Incorrect. Try Again.")

                if app_audio_active:
                    sound_index = random.randint(1, 2)
                    if self.processor.retry_count == 1: sound_file = f"wrong-anwser-{sound_index}.mp3"
                    else: sound_file = f"wrong-anwser-repeted-{sound_index}.mp3"
                    
                    self.main_window.play_sound(sound_file)
                    self.show_feedback_gif(sound_file)
                    
                    # ✅ TTS FEEDBACK: Announce "Try Again" after a short delay
                    if hasattr(self, 'tts'):
                        QTimer.singleShot(300, lambda: self.tts.speak("Try Again"))

                # Focus remains on Input Box.
                # Just ensure input is active for typing
                if not self.input_box.hasFocus():
                    self.input_box.setFocus()

       

    def call_next_question(self):
        if not self._active:
            return
        if hasattr(self, "next_question_callback") and self.next_question_callback:
            self.next_question_callback()
        else:
            self.load_new_question()

    # --- Bell Ring Sequence Logic ---
    def play_bell_question_sequence(self, question_text):
        if not self._active:
            return
        # Stop any existing sequence first
        self.stop_all_activity()
        self._active = True  # Re-enable after stop_all_activity sets it False

        print(f"[BellRing] processing sequence for: '{question_text}'")

        import re
        # Parse "3 + 2" or "3 + 2 =" or "3 + 2 = ?"
        match = re.search(r'(\d+)\s*([+\-*/×xX])\s*(\d+)', question_text)
        
        if not match:
            print(f"[BellRing] Could not parse question for audio: '{question_text}' - Type: {self.processor.questionType}")
            # Fallback to just reading it if parsing fails
            if hasattr(self, 'tts') and self.tts: 
                self.tts.speak(question_text)
            return

        num1 = int(match.group(1))
        op_char = match.group(2)
        num2 = int(match.group(3))

        op_map = {
            '+': "Addition",
            '-': "Subtraction",
            '*': "Multiplication",
            '×': "Multiplication",
            'x': "Multiplication",
            'X': "Multiplication",
            '/': "Division",
            '÷': "Division"
        }
        self.seq_op_text = op_map.get(op_char, "Operation")
        self.seq_num2 = num2

        print(f"[BellRing] Parsed: {num1} {op_char} {num2} -> {self.seq_op_text}")

        # Start Sequence: Phase 1 (First Operand Bells)
        self.play_bells_with_callback(num1, self._seq_phase_2_speak_op)

    def _seq_phase_2_speak_op(self):
        if not self._active:
            return
        # Phase 2: Speak Operator
        if hasattr(self, 'tts') and self.tts:
            self.tts.speak(self.seq_op_text)
        # Wait 1.5s for speech to finish, then Phase 3
        self.seq_timer = QTimer(self)
        self.seq_timer.setSingleShot(True)
        self.seq_timer.timeout.connect(self._seq_phase_3_second_operand)
        self.seq_timer.start(1500)

    def _seq_phase_3_second_operand(self):
        if not self._active:
            return
        # Phase 3: Second Operand Bells
        self.play_bells_with_callback(self.seq_num2, self._seq_phase_4_done)

    def _seq_phase_4_done(self):
        if not self._active:
            return
        # Sequence complete — in bell mode, prompt user to ring their answer
        if self.is_bell_mode:
            if hasattr(self, 'tts') and self.tts and self.main_window and not self.main_window.is_muted:
                QTimer.singleShot(300, lambda: self.tts.speak("Now ring your answer"))
            # Focus the bell button after a short delay
            QTimer.singleShot(500, lambda: self.bell_button.setFocus(Qt.OtherFocusReason))

    def play_bells_with_callback(self, count, callback):
        """Plays bell 'count' times, then calls 'callback'."""
        
        # Stop any existing bell sequence timer to prevent overlaps
        if hasattr(self, "bell_seq_timer") and self.bell_seq_timer.isActive():
            self.bell_seq_timer.stop()

        if count <= 0:
            if callback: callback()
            return

        self.bell_seq_counter = 0
        self.bell_seq_total = count
        self.bell_seq_callback = callback
        
        # Use a timer for the intervals
        self.bell_seq_timer = QTimer(self)
        self.bell_seq_timer.timeout.connect(self._on_bell_seq_tick)
        self.bell_seq_timer.start(600) # 600ms gap between bells
        
        # Play first one immediately
        self._on_bell_seq_tick() 

    def _on_bell_seq_tick(self):
        if self.bell_seq_counter < self.bell_seq_total:
            if self.main_window:
                self.main_window.play_sound("BellRing.mp3")
            self.bell_seq_counter += 1
        else:
            self.bell_seq_timer.stop()
            if self.bell_seq_callback:
                self.bell_seq_callback()

    # ── Bell Ring Mode: button press handling ──
    def _on_bell_pressed(self):
        """Called each time user clicks the Ring Bell button."""
        self.bell_press_count += 1
        print(f"[BellRing] Press #{self.bell_press_count}")
        # Vibration animation
        self._shake_bell()
        # Play bell sound on each press
        if self.main_window and not self.main_window.is_muted:
            self.main_window.play_sound("BellRing.mp3")
        # Restart pause timer on each press
        if self.bell_pause_timer:
            self.bell_pause_timer.stop()
            self.bell_pause_timer.start(1500)

    def _shake_bell(self):
        """Subtle vibration animation on the bell button."""
        if not self.bell_button:
            return
        origin = self.bell_button.pos()
        anim_group = QSequentialAnimationGroup(self)

        offsets = [4, -8, 6, -4, 2, 0]  # pixel offsets for shake
        for dx in offsets:
            anim = QPropertyAnimation(self.bell_button, b"pos")
            anim.setDuration(35)
            anim.setEndValue(QPoint(origin.x() + dx, origin.y()))
            anim_group.addAnimation(anim)

        anim_group.start()
        # Keep a reference so it doesn't get garbage collected mid-animation
        self._shake_anim = anim_group

    def _evaluate_bell_answer(self):
        """Called when the pause timer fires after the user stops pressing."""
        count = self.bell_press_count
        self.bell_press_count = 0  # Reset for next sequence

        try:
            correct_answer = int(self.answer)
        except (ValueError, TypeError):
            correct_answer = -1  # Safety fallback

        elapsed = time() - self.start_time
        is_correct = (count == correct_answer)

        app_audio_active = self.main_window and not self.main_window.is_muted

        print(f"[BellRing] Evaluating: pressed {count}, answer {correct_answer}, correct={is_correct}")

        if is_correct:
            if hasattr(self, 'tts'):
                self.tts.stop()

            # Feedback
            sound_index = random.randint(1, 3)
            if elapsed < 5: feedback_text = "🌟 Excellent"
            elif elapsed < 10: feedback_text = "👏 Very Good"
            elif elapsed < 15: feedback_text = "👍 Good"
            elif elapsed < 20: feedback_text = "👌 Not Bad"
            else: feedback_text = "🙂 Okay"

            self.result_label.setText(f'<span style="font-size:16pt;">{feedback_text}</span>')
            clean_feedback = feedback_text.replace("🌟", "").replace("👏", "").replace("👍", "").replace("👌", "").replace("🙂", "").strip()
            self.result_label.setAccessibleName(f"Correct! {clean_feedback}")

            if app_audio_active and self.main_window:
                if elapsed < 5: sound_file = f"excellent-{sound_index}.mp3"
                elif elapsed < 10: sound_file = f"very-good-{sound_index}.mp3"
                elif elapsed < 15: sound_file = f"good-{sound_index}.mp3"
                elif elapsed < 20: sound_file = f"not-bad-{sound_index}.mp3"
                else: sound_file = f"okay-{sound_index}.mp3"

                self.main_window.play_sound(sound_file)
                self.show_feedback_gif(sound_file)

                if hasattr(self, 'tts'):
                    QTimer.singleShot(300, lambda t=clean_feedback: self.tts.speak(t))

            self.processor.retry_count = 0
            QTimer.singleShot(2000, self.call_next_question)

        else:
            self.processor.retry_count += 1
            self.result_label.setText('<span style="font-size:16pt;">Try Again.</span>')
            self.result_label.setAccessibleName("Incorrect. Try Again.")

            if app_audio_active and self.main_window:
                sound_index = random.randint(1, 2)
                if self.processor.retry_count == 1:
                    sound_file = f"wrong-anwser-{sound_index}.mp3"
                else:
                    sound_file = f"wrong-anwser-repeted-{sound_index}.mp3"

                self.main_window.play_sound(sound_file)
                self.show_feedback_gif(sound_file)

                if hasattr(self, 'tts'):
                    QTimer.singleShot(300, lambda: self.tts.speak("Try Again"))

            # Keep focus on bell button for retry
            if self.bell_button and not self.bell_button.hasFocus():
                self.bell_button.setFocus()



def create_dynamic_question_ui(section_name, difficulty_index, back_callback,main_window=None, back_to_operations_callback=None, tts=None):
    container = QWidget()
    # ✅ ACCESSIBILITY: Prevent NVDA from announcing this container as "grouping"
    container.setAccessibleName("")
    container.setAccessibleDescription("")
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignTop)
    container.setLayout(layout)

    # ✅ Temporary: Force difficulty to 1 for Bell Ring mode
    if section_name.lower() == "bellring":
        print(f"[BellRing] Overriding difficulty {difficulty_index} -> 1")
        difficulty_index = 1

    processor = QuestionProcessor(section_name, difficulty_index)
    processor.process_file()
    
    question_widget = QuestionWidget(processor,main_window, tts=tts)

    layout.addWidget(question_widget)
    apply_theme(container, main_window.current_theme)
    return container


def apply_theme(widget, theme):
    if not widget:
        return

    widget.setProperty("theme", theme)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()

    for child in widget.findChildren(QWidget):  # covers all widgets
        child.setProperty("theme", theme)
        child.style().unpolish(child)
        child.style().polish(child)
        child.update()


class SettingsDialog(QDialog):
    def __init__(self, parent=None, initial_difficulty=1, main_window=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 220)

        self.main_window = main_window
        self.updated_language = main_window.language if main_window else "English"

        self.difficulty_slider = QSlider(Qt.Horizontal)
        self.difficulty_slider.setMinimum(0)
        self.difficulty_slider.setMaximum(len(DIFFICULTY_LEVELS) - 1)
        self.difficulty_slider.setSingleStep(1)
        self.difficulty_slider.setPageStep(1)
        self.difficulty_slider.setTickInterval(1)
        self.difficulty_slider.setTickPosition(QSlider.TicksBelow)
        self.difficulty_slider.setTracking(True)
        # Combine instruction into name to ensure it is read
        self.difficulty_slider.setAccessibleName("Difficulty") 
        
        self.difficulty_slider.setValue(initial_difficulty)
        self.difficulty_label = create_label(DIFFICULTY_LEVELS[initial_difficulty], font_size=12)
        self.difficulty_label.setProperty("class", "difficulty-label")
        self.difficulty_label.setProperty("theme", parent.current_theme)
        # ✅ ACCESSIBILITY: Silence this label so it doesn't override the slider's numeric value
        self.difficulty_label.setAccessibleName(" ")

        self.difficulty_slider.valueChanged.connect(self.update_difficulty_label)
        
        # REDUCED DELAY: 250ms for focus (snappier but safe)
        QTimer.singleShot(250, lambda: self.difficulty_slider.setFocus())
        self.setProperty("theme", parent.current_theme)  # pass current theme
        

    

        # 🔁 Reset Language Button
        self.language_reset_btn = QPushButton("Reset Language")
        self.language_reset_btn.setFixedHeight(30)
        self.language_reset_btn.clicked.connect(self.handle_reset_language)
        # ✅ ACCESSIBILITY: Screen reader announces button purpose
        self.language_reset_btn.setAccessibleName("Reset Language")
        self.language_reset_btn.setAccessibleDescription("Clear saved language preference and choose a new language")

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_settings)
        button_box.rejected.connect(self.reject)
        # ✅ ACCESSIBILITY: Set accessible names on OK/Cancel buttons
        ok_btn = button_box.button(QDialogButtonBox.Ok)
        cancel_btn = button_box.button(QDialogButtonBox.Cancel)
        if ok_btn:
            ok_btn.setAccessibleName("OK — Apply settings")
        if cancel_btn:
            cancel_btn.setAccessibleName("Cancel — Discard changes")

        self.setMinimumSize(400, 280)  # Better size for spacing

        layout = QVBoxLayout()
        layout.setSpacing(12)  # Add breathing space between widgets
        layout.setContentsMargins(20, 20, 20, 20)

        difficulty_label = QLabel("Select Difficulty:")
        difficulty_label.setProperty("class", "difficulty-label")
        difficulty_label.setProperty("theme", parent.current_theme)
        # ✅ ACCESSIBILITY: Link label to slider for screen readers and put instruction here
        difficulty_label.setAccessibleName("Select Difficulty. Use left or right arrow keys to select difficulty level.") 
        difficulty_label.setBuddy(self.difficulty_slider)
        layout.addWidget(difficulty_label)
        layout.addWidget(self.difficulty_slider)
        layout.addWidget(self.difficulty_label)


        layout.addWidget(self.language_reset_btn)

        # Add Help and About side by side
        extra_buttons_layout = QHBoxLayout()
        self.help_button = QPushButton("Help")
        self.about_button = QPushButton("About")
        for btn in [self.help_button, self.about_button]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            btn.setFixedHeight(30)
        # ✅ ACCESSIBILITY: Screen reader announces button purpose
        self.help_button.setAccessibleName("Help")
        self.help_button.setAccessibleDescription("View help information about Maths Tutor")
        self.about_button.setAccessibleName("About")
        self.about_button.setAccessibleDescription("View information about the application")
        extra_buttons_layout.addWidget(self.help_button)
        extra_buttons_layout.addWidget(self.about_button)
        layout.addLayout(extra_buttons_layout)

        layout.addStretch()
        layout.addWidget(button_box)

        self.setLayout(layout)

        # ✅ ACCESSIBILITY: Explicit tab order through Settings dialog
        QWidget.setTabOrder(self.difficulty_slider, self.language_reset_btn)
        QWidget.setTabOrder(self.language_reset_btn, self.help_button)
        QWidget.setTabOrder(self.help_button, self.about_button)
        if ok_btn and cancel_btn:
            QWidget.setTabOrder(self.about_button, ok_btn)
            QWidget.setTabOrder(ok_btn, cancel_btn)


    def update_difficulty_label(self, index):
        level = DIFFICULTY_LEVELS[index]
        self.difficulty_label.setText(level)
        # ✅ ACCESSIBILITY: Keep label silent (TTS handles the name, slider handles the number)
        self.difficulty_label.setAccessibleName(" ")



        # ✅ ACCESSIBILITY FIX: Manually announce the level via TTS
        # Use a short delay (200ms) for responsiveness during interaction
        if self.main_window and hasattr(self.main_window, 'tts') and not self.main_window.is_muted:
             # Stop previous speech to prevent queue build-up
             self.main_window.tts.stop()
             QTimer.singleShot(200, lambda: self.main_window.tts.speak(level))
    # In pages/shared_ui.py -> SettingsDialog class
    def handle_reset_language(self):
        print("--- [DEBUG] handle_reset_language START ---")
        from main import RootWindow 
        from language.language import clear_remember_language, set_language

        clear_remember_language()
        
        dialog = RootWindow(minimal=True)
        if dialog.exec_() == QDialog.Accepted:
            new_lang = dialog.language_combo.currentText()
            print(f"--- [DEBUG] Dialog Accepted. New Language: {new_lang}")
            
            set_language(new_lang)
            self.updated_language = new_lang

            QMessageBox.information(self, "Language Changed",
                                    f"Language changed to {new_lang}. The app will now reload.")
            print("--- [DEBUG] Info box closed. Ready to refresh.")

            if self.main_window:
                print("--- [DEBUG] Calling main_window.refresh_ui()...")
                self.main_window.refresh_ui(new_lang)
                print("--- [DEBUG] Returned from refresh_ui().")
            else:
                print("--- [DEBUG] ERROR: self.main_window is None!")

            print("--- [DEBUG] Closing Settings Dialog...")
            self.close() 
            print("--- [DEBUG] Settings Dialog Closed.")

    def accept_settings(self):
        selected_index = self.difficulty_slider.value()
        settings.set_difficulty(selected_index)
        settings.set_language(self.updated_language)
        print(f"[Difficulty] Index set to: {selected_index}")
        self.accept()

    def get_difficulty_index(self):
        return self.difficulty_slider.value()

    def get_selected_language(self):
        return self.updated_language
    