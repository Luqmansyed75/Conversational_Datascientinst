# Conversational Data Scientist

Version 1 is a Streamlit chatbot powered by LangGraph.

## Features

- Chat interface with current-session conversation memory
- Intent router for normal, RAG, SQL, and hybrid questions
- RAG over PDFs in `data/docs`
- SQL agent over `data/cleaned_data.db`
- Natural language response generation with SQL shown for transparency

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Set your OpenAI key:

```bash
set OPENAI_API_KEY=your_api_key_here
```

Optional model override:

```bash
set OPENAI_MODEL=gpt-4o-mini
```

Start the app:

```bash
streamlit run app.py
```

## Try

- `What is today's date?`
- `What is the return policy?`
- `Top 5 selling products`
- `Which products have the highest revenue?`
