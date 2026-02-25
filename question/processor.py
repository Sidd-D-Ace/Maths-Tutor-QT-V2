import os
import pandas as pd
import random


class QuestionProcessor:
    # ✅ Added difficultyIndex to match your shared_ui.py
    def __init__(self, questionType, difficultyIndex=1):
        self.questionType = questionType
        self.difficultyIndex = difficultyIndex
        self.df = None
        self.variables = []
        self.oprands = []
        self.rowIndex = 0

    def process_file(self):
        file_path = os.path.join(os.getcwd(), "question", "question.xlsx")
        self.df = pd.read_excel(file_path)
        self.df = self.df[self.df["type"] == self.questionType]
        self.df = self.df.reset_index(drop=True)
        

    def get_random_question(self):
        if self.df.empty:
            return "No questions found."

        self.rowIndex = random.randint(0, len(self.df) - 1)
        self.variables = self.allVariables(self.rowIndex, 2)
        inputRange = self.removeVariables(self.rowIndex, 2)
        self.parseInputRange(inputRange)
        return self.replaceVariables(self.rowIndex, 0)

    def removeVariables(self, row, column):
        val = str(self.df.iloc[row, column]) # Wrapped in str() for safety
        return ''.join(c for c in val if not c.isalpha())

    def allVariables(self, row, column):
        val = str(self.df.iloc[row, column]) # Wrapped in str() for safety
        return [c for c in val if c.isalpha()]

    def parseInputRange(self, inputRange):
        self.oprands = []
        current = ""
        for c in inputRange:
            if c == "*":
                self.oprands.append(int(self.extractType(current)))
                current = ""
            else:
                current += c
        if current:
            self.oprands.append(int(self.extractType(current)))

    def extractType(self, inputRange):
        if "," in inputRange:
            return random.choice(list(map(int, inputRange.split(","))))
        elif ":" in inputRange:
            a, b = map(int, inputRange.split(":"))
            return random.randint(a, b)
        elif ";" in inputRange:
            a, b, c = map(int, inputRange.split(";"))
            return a * random.randint(b, c)
        return int(inputRange)

    def replaceVariables(self, row, column):
        # ✅ Fetch the live selected language from your language module
        import language.language as lang_module
        current_language = lang_module.selected_language
        
        # Default to the English column header
        target_col = self.df.columns[column]

        # ✅ Map the selected language to the correct Excel column
        if current_language == "हिंदी":
            target_col = "question_hi"
        elif current_language == "മലയാളം":
            target_col = "question_mal"
        elif current_language == "தமிழ்":
            target_col = "question_ta"
        elif current_language == "عربي":
            target_col = "question_ar"
        elif current_language == "संस्कृत":
            target_col = "question_sa"

        # Check if that translated column exists in your Excel file
        if target_col in self.df.columns:
            val = str(self.df.loc[row, target_col])
        else:
            # Fallback to English if the translation column is missing
            print(f"[WARNING] '{target_col}' not found. Falling back to English.")
            val = str(self.df.iloc[row, column])

        # Replace variables like {a}, {b} with actual numbers
        for i, var in enumerate(self.variables):
            val = val.replace(f"{{{var}}}", str(self.oprands[i]))
        return val