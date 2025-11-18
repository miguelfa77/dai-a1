# DesigningAI-A1

This repository contains two main components focused on natural language processing and knowledge representation.

## Part 1: Named Entity Recognition and Knowledge Graph

Part 1 focuses on extracting structured information from unstructured text and building a knowledge graph.

### Overview
- **NER Models**: Uses Named Entity Recognition models to extract entities from professor/teacher profiles. The official implementation (`ner_model_v2.ipynb`) uses:
  - `dslim/bert-base-NER` for general entity extraction (organizations, locations, etc.)
  - `Jean-Baptiste/camembert-ner-with-dates` for date extraction
- **Knowledge Graph**: A NetworkX-based knowledge graph (`network.ipynb`) that visualizes relationships between professors, companies, universities, locations, and other entities

### Key Features
- Extracts entities such as:
  - Companies and corporate experience
  - Universities and academic background
  - Locations and dates
  - Degrees and qualifications
- Builds a graph structure connecting professors to their associated entities
- Visualizes the knowledge graph using NetworkX

### Files
- `ner_model_v2.ipynb`: Official NER model implementation (updated from `ner_model_v1.ipynb`)
- `network.ipynb`: Knowledge graph construction and visualization
- `teachers_db_practice.parquet`: Input data containing professor profiles
- `ner_predictions_v2.parquet`: Extracted entity predictions
- `knowledge_graph.png`: Visualization of the knowledge graph

## Part 2: ML Knowledge Evaluator Chatbot

Part 2 is an interactive chatbot application built with **Streamlit** that evaluates student answers to machine learning questions.

### Overview
A Streamlit-based web application that:
- Presents ML-related questions to students
- Evaluates student answers using Google's Gemini AI model
- Provides feedback and scores (0-100) based on reference answers
- Maintains chat history with conversation tracking

### Key Features
- **Interactive Chat Interface**: Clean, user-friendly chatbot UI
- **AI-Powered Evaluation**: Uses Gemini 2.5 Flash Lite to evaluate answers
- **Question Bank**: Randomly selects questions from a Q&A database
- **Feedback System**: Provides detailed feedback on correctness, completeness, and precision
- **History Tracking**: View and download chat history as JSON

### Files
- `app.py`: Main Streamlit application
- `models.py`: Contains `Master` and `EvaluatorModel` classes for question selection and answer evaluation
- `Q&A_db_practice.json`: Database of questions and reference answers
- `model_test.ipynb`: Testing notebook for the evaluation models

### Setup
1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up environment variables (e.g., `GEMINI_API_KEY` in `.env`)
3. Run the application:
   ```bash
   streamlit run part2/app.py
   ```

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

