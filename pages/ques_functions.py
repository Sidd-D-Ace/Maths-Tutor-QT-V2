import os, shutil
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFileDialog, QMessageBox, QInputDialog, QHBoxLayout, QWidget,
    QVBoxLayout, QGridLayout, QPushButton, QLabel, QSizePolicy
)
from question.loader import QuestionProcessor
# pages/ques_functions.py

from pages.shared_ui import (
    create_colored_widget,
    create_label,
    create_menu_button,
    create_vertical_layout,
    create_dynamic_question_ui,
    create_entry_ui, apply_theme,
    QuestionWidget
)

from language.language import tr


def load_pages(section_name, back_callback, difficulty_index,
               main_window=None, tts=None):

    page = create_colored_widget("#e0f7fa")
 
    widgets = []
 
    # 👉 Custom logic for "Operations"
    if section_name.lower() == "operations":
        title = create_label(tr("Choose an Operation"), bold=True)
        title.setProperty("class", "subtitle")
        title.setAlignment(Qt.AlignCenter)
        # ✅ ACCESSIBILITY: Screen reader announces operations heading
        title.setAccessibleName(tr("Choose an Operation"))

        grid = QGridLayout()
        grid.setSpacing(20)

        operations = ["Addition", "Subtraction", "Multiplication", "Division", "Remainder", "Percentage"]

        for i, sub in enumerate(operations):
            translated=tr(sub)
            btn = create_menu_button(translated, lambda _, s=sub: main_window.load_section(s))
            btn.setFixedSize(180, 60)
            # ✅ ACCESSIBILITY: Screen reader announces each operation button
            btn.setAccessibleName(translated)
            btn.setAccessibleDescription(f"Practice {translated} problems")
            grid.addWidget(btn, i // 2, i % 2)  # 2 columns

        wrapper = QWidget()
        wrapper.setLayout(grid)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(wrapper)
        layout.addSpacing(30)

        page.setLayout(layout)
        return page

    # ✅ For other sections
    return create_dynamic_question_ui(section_name, difficulty_index, back_callback, main_window=main_window, tts=tts)

uploaded_df = None

def upload_excel(parent_widget):
    file_path, _ = QFileDialog.getOpenFileName(parent_widget, "Select Excel File", "", "Excel Files (*.xlsx)")
    if not file_path:
        return

    df = pd.read_excel(file_path)
    global uploaded_df
    uploaded_df = df

    print(uploaded_df)
  
    required = {"question", "operands", "equation"}
    if not required.issubset(df.columns):
        QMessageBox.critical(parent_widget, "Invalid File", "Excel must have columns titled: question, operands, equation")
        return

    QMessageBox.information(parent_widget, "Success", "Questions uploaded successfully!")
    
    main_window = parent_widget
    entry_ui = create_entry_ui(main_window)
    apply_theme(entry_ui, main_window.current_theme)
    
    # 🔴 BUG FIX: Do NOT use setCentralWidget. It wipes the top bar and footers.
    # ✅ FIX: Add to the stack and switch to it.
    main_window.stack.addWidget(entry_ui)
    main_window.stack.setCurrentWidget(entry_ui)
    
    # Ensure correct footer visibility (Start page is like a menu, so show Main Footer)
    if hasattr(main_window, 'main_footer'):
        main_window.main_footer.show()
    if hasattr(main_window, 'section_footer'):
        main_window.section_footer.hide()


def load_entry_page(main_window):
    entry_ui = create_entry_ui(main_window)
    # 🔴 BUG FIX: Same fix as above
    main_window.stack.addWidget(entry_ui)
    main_window.stack.setCurrentWidget(entry_ui)

  # global storage

def start_uploaded_quiz(main_window):
    global uploaded_df
    if uploaded_df is None:
        print('no uploaded_df')
        return

    processor = QuestionProcessor("custom", 0)  # pass dummy type and difficulty
    print('dummy value passed to init of processor')
    processor.df = uploaded_df  # manually inject uploaded data
    print(processor.df)

    question_widget = QuestionWidget(processor, window=main_window, tts=main_window.tts)
    apply_theme(question_widget, main_window.current_theme)
    
    # 🔴 BUG FIX: Do NOT use setCentralWidget. It wipes the top bar and footers.
    # ✅ FIX: Add to stack.
    main_window.stack.addWidget(question_widget)
    main_window.stack.setCurrentWidget(question_widget)
    
    # ✅ FIX: Update footers so "Back to Home", "Settings", and "Mute" are visible
    if hasattr(main_window, 'main_footer'):
        main_window.main_footer.hide()
    
    if hasattr(main_window, 'section_footer'):
        main_window.section_footer.show()
        # Hide "Back to Operations" since this is a custom quiz, not an operation
        if hasattr(main_window, 'update_back_to_operations_visibility'):
            main_window.update_back_to_operations_visibility("uploaded_quiz")