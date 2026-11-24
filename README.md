# AI-Powered Study Assistant

## 📚 Project Overview

The AI-Powered Study Assistant is a Flask web application for studying from personal notes and uploaded course PDFs. Its PDF question-answering flow retrieves relevant passages from the signed-in user's documents, uses those passages as the only answer context, and displays the supporting filename, page, and text. Questions with no sufficiently relevant retrieved passage receive a "not covered / not enough information" response.

### 🎯 Key Features

- **User Management**: Secure registration, login, and profile management
- **Smart Note-Taking**: Create, store, and organize study notes
- **PDF-grounded Q&A**: Upload PDFs, retrieve relevant passages, and ask questions across your documents
- **Evidence Display**: Answers include retrieved passages with document names and page numbers
- **Out-of-scope Handling**: Questions without sufficient matching document evidence are declined
- **AI Integration**: Generate answers using Groq's OpenAI-compatible Responses API
- **Interactive Dashboard**: Visual progress tracking and statistics
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Modern UI/UX**: Bootstrap-powered interface with custom animations

## 🏗️ Technical Architecture

### Technology Stack

- **Backend**: Python 3.12+ with Flask 2.3.3
- **Database**: SQLite (lightweight and portable)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5.3.0
- **AI Integration**: Groq API via the OpenAI SDK; PDF Q&A requires a configured API key and does not use mock answers
- **PDF Extraction**: pypdf
- **Styling**: Custom CSS with blue/white theme and animations

### Object-Oriented Design

The application follows solid OOP principles with three main classes:

#### 1. DatabaseManager
- Handles all SQLite database operations
- Manages user authentication and authorization
- Performs CRUD operations for notes and AI responses
- Implements secure password hashing

#### 2. AIClient
- Integrates with Groq's OpenAI-compatible Responses API
- Answers PDF questions using retrieved source passages
- Does not use mock answers for PDF questions
- Manages API error handling and timeouts

#### 3. AppLogic
- Connects database and AI functionality with Flask routes
- Implements business logic and validation
- Manages user sessions and permissions
- Orchestrates complex operations

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notes table
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- AI Responses table
CREATE TABLE ai_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id INTEGER NOT NULL,
    response_type TEXT NOT NULL,
    response_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES notes (id)
);

-- Uploaded PDFs are stored as extracted, page-attributed text chunks.
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    page_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE document_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    content TEXT NOT NULL
);
```

## 🚀 Installation and Setup

### Prerequisites

- Python 3.12 or higher
- pip (Python package installer)
- Git (optional, for cloning)

### Step-by-Step Installation

1. **Extract the ZIP file** to your desired directory:
   ```
   AI-Study-Assistant/
   ├── app.py
   ├── core_classes.py
   ├── requirements.txt
   ├── .env
   ├── templates/
   ├── static/
   └── database/
   ```

2. **Install dependencies**:
   ```bash
   cd AI-Study-Assistant
   pip install -r requirements.txt
   ```

3. **Configure environment variables** (optional):
   - Open `.env` file
   - Add your Groq API key for AI responses, especially PDF Q&A: `GROQ_API_KEY=your_actual_api_key_here`
   - Set a secure secret key: `SECRET_KEY=your_secure_secret_key_here`

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the application**:
   - Open your web browser
   - Navigate to: `http://127.0.0.1:5000`

## 🎮 User Guide

### Getting Started

1. **Registration**:
   - Click "Get Started" or "Register" on the home page
   - Fill in your name, email, and password (minimum 6 characters)
   - Submit the form to create your account

2. **Login**:
   - Use your email and password to log in
   - You'll be redirected to the dashboard

### Creating Study Notes

1. **Add a New Note**:
   - Click "Add Note" from the navigation or dashboard
   - Enter a descriptive title
   - Write your study content (the more detailed, the better AI responses)
   - Click "Save Note"

2. **Note Best Practices**:
   - Use clear, descriptive titles
   - Include key concepts and definitions
   - Add examples and case studies
   - Structure your content logically

### Using AI Features

1. Open **AI Assistant** from the navigation and upload one or more PDFs (up to 16 MB and 200 pages each).
2. Ask a question across your uploaded documents.
3. Review the answer and the retrieved evidence, including the filename, page, and passage.
4. If no sufficiently relevant passage is retrieved, the assistant says the material is not covered or does not provide enough information. Generated answers are instructed to use the retrieved passages only.
5. Remove documents from the same page. The app extracts text locally with pypdf and stores only the extracted text chunks in SQLite; it does not retain the original PDF.

Retrieval uses BM25 keyword matching. Relevant passages are sent to Groq's API for answer generation, so do not upload documents you are not allowed to share with that service. Scanned PDFs need OCR before upload.

### Dashboard Features

- **Statistics Cards**: View your study progress
- **Recent Notes**: Quick access to your latest notes
- **Progress Tracking**: Monitor your learning journey
- **Quick Actions**: Fast navigation to key features

## 🔧 Configuration Options

### Environment Variables

Edit the `.env` file to customize the application:

```env
# Required for production use with real AI responses
GROQ_API_KEY=your_groq_api_key_here

# Flask session security (change in production)
SECRET_KEY=your_secure_secret_key_here

# Optional: set this to a writable persistent-volume path when deploying
DATABASE_PATH=/path/to/persistent/storage/study_assistant.db

# Debug mode (set to False in production)
DEBUG=True
```

The default SQLite database is stored at `database/study_assistant.db` relative to the application. On deployment, set `DATABASE_PATH` to a writable persistent volume if the host does not preserve files between restarts.

### Groq API Setup

1. **Get API Key**:
   - Create a Groq API key in the [Groq Console](https://console.groq.com/keys)
   - Copy the key to your `.env` file

2. **API Key Benefits**:
   - Real AI-powered responses
   - Better quality summaries and quizzes
   - Personalized answer generation

**Note**: PDF Q&A requires a working Groq API key; it reports a configuration/provider error rather than returning an ungrounded mock answer.

## 🎨 UI/UX Design Guide

### Color Scheme
- **Primary Blue**: #0d6efd (Bootstrap primary)
- **Secondary Blue**: #6c95ff
- **Success Green**: #198754
- **Background**: #f8f9fa (light gray)
- **Text**: #212529 (dark)

### Design Features
- **Responsive Design**: Works on all device sizes
- **Card-Based Layout**: Clean, organized content presentation
- **Smooth Animations**: Hover effects and transitions
- **Bootstrap Icons**: Consistent iconography
- **Modern Typography**: Clean, readable fonts

### Accessibility
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader Friendly**: Proper ARIA labels
- **Color Contrast**: WCAG compliant color ratios
- **Focus States**: Clear focus indicators

## 🔍 Troubleshooting

### Common Issues

1. **Database Not Found**:
   - Ensure the `database/` directory exists
   - The application will create the database automatically

2. **Dependencies Not Installing**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Port Already in Use**:
   - Change the port in `app.py`:
   ```python
   app.run(port=5001)  # Use different port
   ```

4. **AI Responses Not Working**:
   - Check your Groq API key in `.env`
   - Verify internet connection
   - PDF Q&A needs a configured API key; missing keys and provider failures are reported in the assistant

### Error Messages

- **"Invalid email or password"**: Check login credentials
- **"Email already exists"**: Use a different email for registration
- **"Failed to save note"**: Check if title and content are provided
- **"Note not found"**: The note may have been deleted

## 📊 Features Overview

### User Management
- ✅ Secure registration and login
- ✅ Password hashing and validation
- ✅ Session management
- ✅ User profile with statistics
- ✅ Achievement system

### Note Management
- ✅ Create, read, update, delete notes
- ✅ Rich text content support
- ✅ Search and organization
- ✅ Note statistics and analytics
- ✅ Auto-save functionality

### AI Integration
- ✅ Groq Responses API integration
- ✅ PDF text extraction, chunking, and per-user passage retrieval
- ✅ BM25 keyword retrieval with a weak-match refusal threshold
- ✅ PDF answers constrained to retrieved passages and shown with evidence
- ✅ Refusal when no sufficiently relevant passage is retrieved

### User Interface
- ✅ Responsive Bootstrap design
- ✅ Modern blue/white theme
- ✅ Smooth animations and transitions
- ✅ Interactive dashboards
- ✅ Mobile-friendly navigation
- ✅ Accessibility features

## 🔒 Security Features

- **Password Hashing**: SHA-256 encryption for user passwords
- **Session Management**: Secure Flask sessions with secret keys
- **Input Validation**: Server-side validation for all forms
- **SQL Injection Protection**: Parameterized queries
- **CSRF Protection**: Built-in Flask security features
- **Access Control**: User-specific data isolation

## 🚀 Performance Optimizations

- **Database Indexing**: Optimized query performance
- **Static File Caching**: Browser caching for CSS/JS
- **Lazy Loading**: Progressive content loading
- **Minified Assets**: Compressed CSS and JavaScript
- **Efficient Queries**: Optimized database operations

## 📱 Mobile Experience

The application is fully responsive and provides an excellent mobile experience:

- **Touch-Friendly Interface**: Large buttons and touch targets
- **Mobile Navigation**: Collapsible menu for small screens
- **Optimized Layouts**: Content adapts to screen size
- **Fast Loading**: Optimized for mobile networks
- **Swipe Gestures**: Natural mobile interactions

## 🔮 Future Enhancements

Potential features for future versions:

- **Dark Mode**: Toggle between light and dark themes
- **Note Sharing**: Collaborate with other users
- **OCR Support**: Extract text from scanned PDFs
- **Export Options**: PDF and Word export functionality
- **Advanced Search**: Full-text search across all notes
- **Reminder System**: Study schedule and notifications
- **Multiple AI Models**: Support for different AI providers
- **Offline Mode**: Progressive Web App capabilities

## 📞 Support

For questions or issues:

1. **Check this documentation** for common solutions
2. **Review error messages** in the browser console
3. **Verify environment configuration** in `.env` file
4. **Check database permissions** in the `database/` directory

## 📄 License

This project is created for educational purposes. Feel free to modify and use for your learning needs.

---

**Built with ❤️ using Flask, Bootstrap, and Groq AI**

*AI-Powered Study Assistant - Transform your learning experience with intelligent study tools.*