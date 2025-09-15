# Local Development Guide for NSM Career Fair Employers Data analysis

This guide explains how to set up and run the project locally.

---

## 1. Clone the repository

```bash
git clone https://github.com/Darrenf040/employers_research_ai_agent.git
cd employers_research_ai_agent
```
## 2. Set up virtual enviornment
```bash
python -m venv venv
# Activate the environment
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

## 3. Install packages
```bash
pip install -r requirements.txt
```

## 4. Run the web scraper

```bash
python browser_agent.py
```
Wait for the script to complete. It will output a CSV file (e.g., output.csv) in the project directory.

## 5. Install Ollama (Optional: for chatbot only)
https://ollama.com/download
### Verify installation
```bash
ollama
```
### Install model llama3.2
```bash
ollama pull llama3.2
```

### Verify model was installed 
```bash
ollama list
```
 ### Run your model
 ```bash
ollama run llama3.2
```
## 6. Render the ui
```bash
streamlit run analyze_data.py
```
Use the sidebar filters to query the dataset.
Switch to the "Chatbot" tab to ask questions about the companies.

