from google import genai
import pandas as pd
import random
import os

import dotenv
dotenv.load_dotenv()


class Master:
    def __init__(self):

        self.DF_PATH = "part2/Q&A_db_practice.json"
        # load df
        self.df = self.load_df(self.DF_PATH)
        
        self.Evaluator = EvaluatorModel()
        self.current_index = None

    def load_df(self, df_path):
        return pd.read_json(df_path)

    def choose_question(self):
        """Randomly select a question row from the DataFrame."""

        self.current_index = random.randint(0, len(self.df) - 1)
        return self.df.loc[self.current_index, "question"]

    def get_reference(self):
        if self.current_index is None:
            raise ValueError("No question selected.")
        return self.df.loc[self.current_index, "answer"]

    def evaluate_answer(self, student_answer, history):
        """Delegate evaluation to the EvaluatorLLM."""

        if self.current_index is None:
            raise ValueError("No question selected.")

        question = self.df.loc[self.current_index, "question"]
        ref_answer = self.df.loc[self.current_index, "answer"]

        return self.Evaluator.evaluate(question, ref_answer, student_answer, history)



class EvaluatorModel:
    """ Model for evaluating user answers """

    def __init__(self):
        self.LLM = 'gemini-2.5-flash-lite'
        self.API_KEY = os.environ.get("GEMINI_API_KEY")

        # load API client
        self.client = self.get_client()

    def get_client(self):
        """ Initializes GenAI client """
        try:
            client = genai.Client(api_key=self.API_KEY)
            return client
        except Exception as e:
            print("Error initializing client:", e)
            return None


    def get_prompt(self, question, ref_answer, answer, history=None):
        """ Forms prompt to input into evaluation model """
        
        prompt = f"""

        Question: {question}
        Reference answer: {ref_answer}
        Student answer: {answer}

        First step is figure out if 'Student answer' is an attempt at responding the 'Question'.
        - If it is not: Then you are a normal conversational assistant, and should attempt to keep the conversation going.
        - If it is: Then you are an ML Examiner and should respond the following way:
            Evaluate the student's answer for correctness, completeness, and precision.
            Explain briefly what is missing or incorrect.
            Then provide a numeric score from 0 to 100 (using the Reference answer as a reference) in the format:
            Score: <number> n\
            Feedback: <short explanation>
        """
        if history != None:
            for msg in history:
                prompt += f"{msg['role']}: {msg['content']}\n"

                prompt += f"\nUser just said: {answer}\n"
                prompt += "Respond appropriately."
        return prompt
    
    def evaluate(self, question, ref_answer, answer, history):
        """Calls the GenAI model and returns the raw text response."""
        
        prompt = self.get_prompt(question, ref_answer, answer, history)

        if prompt != None:
            response = self.client.models.generate_content(
            model=self.LLM,
            contents=prompt
            )
            return response.text
        else:
            print("Error: Either question, ref_answer or answer not defined")

