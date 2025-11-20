from google import genai
import pandas as pd
import random
import os
import evaluate

import dotenv
dotenv.load_dotenv()

class Master:
    def __init__(self, api_key=None):
        """ Contains info and orchestrates Evaluator and Conversational models"""
        # models api_key
        self.API_KEY = api_key

        self.DF_PATH = "part2/Q&A_db_practice.json"
        # load df
        self.df = self.load_df(self.DF_PATH)
        
        self.Evaluator = EvaluatorModel(self.API_KEY)
        self.Conversational = ConversationalModel(self.API_KEY)
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

    def normal_answer(self, answer, history=None):
        """ Delegate answer to ConversationLLM """

        return self.Conversational.answer(answer, history)
        
    def evaluate_answer(self, answer):
        """Delegate evaluation to the EvaluatorLLM and ROUGE."""

        if self.current_index is None:
            raise ValueError("No question selected.")

        question = self.df.loc[self.current_index, "question"]
        ref_answer = self.df.loc[self.current_index, "answer"]

        evaluation = self.Evaluator.evaluate(question, ref_answer, answer)
        #rouge_score = self.Evaluator.get_rouge(ref_answer, answer)  Fix func TODO

        return evaluation



class EvaluatorModel:
    """ Model for evaluating user answers """

    def __init__(self, api_key=None):
        self.LLM = 'gemini-2.5-flash-lite'

        if api_key != None:
            self.API_KEY = api_key
        else:
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


    def get_prompt(self, question, ref_answer, answer):
        """ Forms prompt to input into evaluation model """

        # Rules
        prompt = f"""
                You are an ML Examiner.

                Current evaluation context:
                Question: {question}
                Reference answer: {ref_answer}
                Student message: {answer}

                RULES:
                → Give structured evaluation of the student's answer for correctness, completeness, and precision (using the reference answer)
                → Explain what is missing or incorrect.
                → Give a score from 0 to 100 using this exact format:

                    Score: <number>
                    
                    Feedback: <Structured Explanation>

                Determine whether 'Student message' is answering the question.
                Then follow the rules above.
            """
        return prompt

    """
    Fix TODO
    def get_rouge(self, ref_answer, answer):

        rouge = evaluate.load("rouge") 
        result = rouge.compute(predictions=[answer], references=[ref_answer], rouge_type=['rougeL'], use_stemmer=True)

        return float(result["rougeL"] * 100)
    """
    
    def evaluate(self, question, ref_answer, answer):
        """Calls the GenAI model and returns the raw text response."""
        
        prompt = self.get_prompt(question, ref_answer, answer)

        if prompt != None:
            response = self.client.models.generate_content(
            model=self.LLM,
            contents=prompt
            )
            return response.text
        else:
            print("Error: Either question, ref_answer or answer not defined")


class ConversationalModel:
    """ Responds like a conversational assistant """

    def __init__(self, api_key=None):
        self.LLM = 'gemini-2.5-flash-lite'
        
        if api_key != None:
            self.API_KEY = api_key
        else:
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

    def get_prompt(self, answer, history=None):
        """ Forms prompt to input into evaluation model """

        # Rules
        prompt = f"""
            You are a conversational assistant.
            RULES:
            → You behave as a normal, helpful conversational assistant.
            → Stay friendly, coherent, and keep the conversation going.
            → Keep the conversation history as context.
            """

        # Add history
        if history:
            prompt += "\nConversation history:\n"
            for msg in history:
                role = "User" if msg["role"] == "user" else "Assistant"
                prompt += f"{role}: {msg['content']}\n"

        return prompt

    def answer(self, answer, history):
        """Calls the GenAI model and returns the raw text response."""
        
        prompt = self.get_prompt(answer, history)

        if prompt != None:
            response = self.client.models.generate_content(
            model=self.LLM,
            contents=prompt
            )
            return response.text
        else:
            print("Error: Either question, ref_answer or answer not defined")

