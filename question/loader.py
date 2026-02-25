import os
import pandas as pd
import random
import language.language as lang_config

class QuestionProcessor:
    def __init__(self, questionType, difficultyIndex):
        self.questionType = questionType
        self.widget = None
        self.difficultyIndex = difficultyIndex
        self.df = None
        self.variables = []
        self.oprands = []
        self.rowIndex = 0
        self.retry_count = 0
        # DDA-related fields
        self.total_attempts = 0
        self.correct_answers = 0
        self.correct_streak = 0
        self.incorrect_streak = 0
        self.current_performance_rate = 0
        self.current_difficulty = difficultyIndex 

    def get_questions(self):
        self.process_file()
        return self.get_random_question()

    def process_file(self):
        file_path = os.path.join(os.getcwd(), "question", "question.xlsx")
        print(f"Processing file: {file_path}")

        self.df = pd.read_excel(file_path)
        self.df = pd.DataFrame(self.df)

        if self.questionType == "custom":
            print("[Processor] Custom uploaded file detected — skipping filtering.")
            return

        self.df["difficulty"] = pd.to_numeric(self.df["difficulty"], errors="coerce")
        self.df["type"] = self.df["type"].astype(str).str.strip().str.lower()

        print(f"[Processor] Filtering with section: {self.questionType}")
        
        if isinstance(self.difficultyIndex, list):
             valid_difficulties = self.difficultyIndex
        else:
             valid_difficulties = [self.difficultyIndex]

        self.df = self.df[
        (self.df["type"] == self.questionType.lower().strip()) &
        (self.df["difficulty"].isin(valid_difficulties))]

        self.df = self.df.sort_values(by="difficulty", ascending=True)

    def quickplay(self):
        self.process_for_quickplay()
        return self.get_random_question()

    def process_for_quickplay(self):
        file_path = os.path.join(os.getcwd(), "question", "question.xlsx")
        print(f"[QuickPlay] Reloading file fresh: {file_path}")

        df = pd.read_excel(file_path)
        df = pd.DataFrame(df)

        df["type"] = df["type"].astype(str).str.strip().str.lower()
        df["difficulty"] = pd.to_numeric(df["difficulty"], errors="coerce")

        if isinstance(self.difficultyIndex, list):
             valid_difficulties = self.difficultyIndex
        else:
             valid_difficulties = [self.difficultyIndex]

        df = df[df["difficulty"].isin(valid_difficulties)]

        if df.empty:
            print(f"[QuickPlay] No questions found at difficulty {self.difficultyIndex}")
        else:
            print(f"[QuickPlay] {len(df)} questions found at difficulty {self.difficultyIndex}")

        df = df.sample(frac=1).reset_index(drop=True)
        self.df = df

    def get_random_question(self):
        if self.df is None or self.df.empty:
            return "No questions found.", None
 
        self.rowIndex = random.randint(0, len(self.df) - 1)
 
        variable_string = str(self.df.iloc[self.rowIndex]["operands"])
        input_string = ''.join(c for c in variable_string if not c.isalpha())
        self.variables = [c for c in variable_string if c.isalpha()]
        self.oprands = self.parseInputRange(input_string)
 
        # ✅ DYNAMIC LANGUAGE SELECTION USING YOUR EXCEL FILE
        current_lang = getattr(lang_config, 'selected_language', 'English')
        
        # If Hindi is selected AND you have the 'questin_hi' column, use it!
        if current_lang == "हिंदी" and "questin_hi" in self.df.columns:
            question_template = str(self.df.iloc[self.rowIndex]["questin_hi"])
        else:
            # Otherwise default to the English 'question' column
            question_template = str(self.df.iloc[self.rowIndex]["question"])

        for i, var in enumerate(self.variables):
            question_template = question_template.replace(f"{{{var}}}", str(self.oprands[i]))
 
        self.extractAnswer()
        try:
            answer = round(float(self.Pr_answer)) if self.Pr_answer is not None else None
        except (TypeError, ValueError):
            answer = None

        return question_template, answer

    def extractAnswer(self):
        answer_equation = self.getAnswer(self.rowIndex, "equation")
        final_answer = self.solveEquation(answer_equation)
        self.Pr_answer = str(final_answer)
 
    def getAnswer(self, row, column):
        ans_equation = str(self.df.iloc[row][column])
        ans_equation = ans_equation.replace("×", "*")  
        for i in range(len(self.variables)):
            ans_equation = ans_equation.replace(f"{{{self.variables[i]}}}", str(self.oprands[i]))
        return ans_equation

    def solveEquation(self, ans_equation):
        try:
            return eval(ans_equation)
        except Exception as e:
            return None
 
    def removeVariables(self, row, column):
        val = self.df.iloc[row, column]
        return ''.join(c for c in val if not c.isalpha())
 
    def allVariables(self, row, column):
        val = self.df.iloc[row, column]
        return [c for c in val if c.isalpha()]

    def parseInputRange(self, inputRange):
        operands = []
        current = ""
        for c in inputRange:
            if c == "*":
                operands.append(int(self.extractType(current)))
                current = ""
            else:
                current += c
        if current:
            operands.append(int(self.extractType(current)))
        return operands
 
    def extractType(self, inputRange):
        try:
            if "," in inputRange:
                return random.choice(list(map(int, inputRange.split(","))))
            elif ":" in inputRange:
                a, b = map(int, inputRange.split(":"))
                return random.randint(a, b)
            elif ";" in inputRange:
                a, b, c = map(int, inputRange.split(";"))
                return a * random.randint(b, c)
            return int(inputRange)
        except Exception as e:
            return 0  
 
    def replaceVariables(self, rowIndex, columnIndex):
        val = str(self.df.iloc[rowIndex, columnIndex])  
        for i, var in enumerate(self.variables):
            val = val.replace(f"{{{var}}}", str(self.oprands[i]))
        return val
 
    def submit_answer(self, user_answer, correct_answer, time_taken):
        if user_answer is None or str(user_answer).strip() == "":
            return {"valid": False}

        try:
            user_val = float(user_answer)
            correct_val = float(correct_answer)
        except (ValueError, TypeError):
            return {"valid": False}
        
        self.total_attempts += 1
        is_correct = user_val == correct_val
    
        if is_correct:
            self.correct_answers += 1
            self.correct_streak += 1
            self.incorrect_streak = 0
            self.current_performance_rate += 5  
            if time_taken < 5:
                self.current_performance_rate += 5
            elif time_taken < 10:
                self.current_performance_rate += 2
        else:
            self.incorrect_streak += 1
            self.correct_streak = 0
            self.current_performance_rate -= 10  
            if time_taken > 15:
                self.current_performance_rate -= 5 
 
        if self.current_performance_rate >= 30:
            if self.current_difficulty < 5:  
                self.current_difficulty += 1
                self.difficultyIndex = self.current_difficulty
            self.current_performance_rate = 0
 
        elif self.current_performance_rate <= -30:
            if self.current_difficulty > 1:
                self.current_difficulty -= 1
            self.current_performance_rate = 0
        
        return {
        "valid": True,
        "correct": is_correct
    }