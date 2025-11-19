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

## Part 2: ML Knowledge Evaluator & Study Chatbot

Part 2 delivers an ML tutoring experience that blends a friendly assistant with an exam-style evaluator powered by Google's Gemini family models.

### Functionalities
- **Dual interaction modes**  
  - *Chat mode*: behaves like a normal assistant using a conversational Gemini instance (`ConversationalModel`).  
  - *Exam mode*: cycles through a four-step loop (question → student answer → LLM evaluation → student feedback) and logs every turn in chat history.
- **Exam-mode UX refinements**  
  - Fixed chat input and side-by-side toggle button so controls remain visible while scrolling.  
  - Toggle can activate/deactivate exams on the fly, resetting the queue and ensuring clean state transitions.
- **Feedback capture**  
  - After each grading response, the user is prompted to critique the feedback; those entries are labeled `(Feedback)` in history to enable later review or fine-tuning.
- **History & downloads**  
  - All interactions (including evaluation prompts and user feedback) are persisted in `st.session_state` and can be exported as JSON from the History view.

### Evaluation & Architecture
- `Master` orchestrates question selection, answer evaluation, and conversational fallbacks.  
- Main Evaluator: `EvaluatorModel` calls **Gemini 2.5 Flash Lite** through `google-genai` to compare student answers with reference answers from `Q&A_db_practice.json`, outputting a score plus structured comments. This model is not small and is able to score/evaluate with depth.
- `ConversationalModel` uses the same Gemini endpoint but with a lightweight prompt optimized for free-form tutoring conversations.  
- State management relies on Streamlit session keys (`messages`, `exam_mode`, `awaiting_answer`, `awaiting_feedback`) to guarantee the deterministic four-step loop and to keep UI artifacts (buttons, reruns) synchronized.
- Alternative Evaluator: Used Rouge-L as it rewards correct ordering, conceptual similarity and structure. Thereby making it the best metric for evaluating correctness in short ML answers. Its important to keep in mind that ROUGE works well as a secondary metric, but has many limitations. It measures textual overlap, not meaning. This is why we chose to use the `EvaluatorModel` as the primary evaluator.



### Files
- `part2/app.py`: Streamlit UI, state machine, and sidebar navigation.
- `part2/models.py`: `Master`, `EvaluatorModel`, and `ConversationalModel` implementations plus Gemini client wiring.
- `part2/Q&A_db_practice.json`: Question bank with reference answers used by exam mode.
- `part2/model_test.ipynb`: Notebook for iterating on prompt templates and sanity-checking API responses.

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

