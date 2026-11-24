# Quick Start Guide - AI Study Assistant

## 🚀 Get Started in 3 Steps

### Step 1: Installation
1. Extract the ZIP file to your computer
2. Open terminal/command prompt in the extracted folder
3. Run: `pip install -r requirements.txt`

### Step 2: Launch Application
1. Run: `python app.py`
2. Open browser and go to: `http://127.0.0.1:5000`

### Step 3: Start Learning
1. **Register** a new account
2. Open **AI Assistant** and upload a course PDF
3. Ask a question, then inspect the answer's retrieved passages and page numbers

## 📋 Requirements
- Python 3.12+
- Internet connection (for AI features)

## 🎯 Core Features
- ✅ PDF uploads with text extraction
- ✅ Answers grounded in retrieved passages, with sources
- ✅ Out-of-scope question refusal
- ✅ Smart note-taking system
- ✅ AI-powered summaries and quizzes  
- ✅ Progress tracking dashboard
- ✅ Mobile-friendly design
- ✅ Secure user accounts

## 🔑 Configure AI
AI responses require a Groq API key:
1. Get a Groq API key from: https://console.groq.com/keys
2. Edit `.env` file and add: `GROQ_API_KEY=your_key_here`
3. Restart the application

PDFs must contain selectable text; scanned PDFs need OCR first. Upload limit: 16 MB and 200 pages per PDF.

## 🆘 Need Help?
- Check `README.md` for detailed documentation
- Ensure Python 3.12+ is installed
- Make sure all files are extracted properly

## 🎨 Try the PDF Assistant
1. Upload a course PDF in **AI Assistant**
2. Ask a question that the PDF answers and review the supporting passages
3. Ask an unrelated question and check that the assistant says it is not covered
4. Upload another PDF and ask questions across your collection

---
**Ready to transform your study experience? Start the app and begin learning!**