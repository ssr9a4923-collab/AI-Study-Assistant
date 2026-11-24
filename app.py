"""
AI-Powered Study Assistant
Main Flask Application
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
from io import BytesIO
from dotenv import load_dotenv
import os
from core_classes import AppLogic, chunk_document_pages

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here_for_flask_sessions')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Initialize application logic
app_logic = AppLogic()


@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([name, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        try:
            result = app_logic.register_user(name, email, password)
        except Exception:
            app.logger.exception('Account registration failed')
            flash(
                'Account registration could not be completed. Please try again later.',
                'error'
            )
            return render_template('register.html')
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('login'))
        else:
            flash(result['message'], 'error')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('login.html')
        
        # Authenticate user
        result = app_logic.login_user(email, password)
        
        if result['success']:
            user = result['user']
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(result['message'], 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        flash('Please log in to access the dashboard', 'warning')
        return redirect(url_for('login'))
    
    # Get dashboard data
    dashboard_data = app_logic.get_user_dashboard_data(session['user_id'])
    
    return render_template('dashboard.html', 
                         user_name=session['user_name'],
                         notes=dashboard_data['notes'],
                         total_notes=dashboard_data['total_notes'])


@app.route('/add_note', methods=['GET', 'POST'])
def add_note():
    """Add new study note"""
    if 'user_id' not in session:
        flash('Please log in to add notes', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        # Create note
        result = app_logic.create_note(session['user_id'], title, content)
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(result['message'], 'error')
    
    return render_template('add_note.html')


@app.route('/note/<int:note_id>')
def view_note(note_id):
    """View specific note with AI history"""
    if 'user_id' not in session:
        flash('Please log in to view notes', 'warning')
        return redirect(url_for('login'))
    
    # Get note with AI history
    result = app_logic.get_note_with_ai_history(note_id)
    
    if not result['success']:
        flash(result['message'], 'error')
        return redirect(url_for('dashboard'))
    
    # Check if note belongs to current user
    if result['note']['user_id'] != session['user_id']:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('view_note.html', 
                         note=result['note'],
                         ai_responses=result['ai_responses'])


@app.route('/ai_assistant')
def ai_assistant():
    """PDF-grounded AI assistant page."""
    if 'user_id' not in session:
        flash('Please log in to access AI Assistant', 'warning')
        return redirect(url_for('login'))

    documents = app_logic.db.get_user_documents(session['user_id'])
    return render_template('ai_assistant.html', documents=documents)


@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    """Extract and store text from a user's uploaded PDF."""
    if 'user_id' not in session:
        flash('Please log in to upload documents', 'warning')
        return redirect(url_for('login'))

    uploaded_file = request.files.get('pdf_file')
    if not uploaded_file or not uploaded_file.filename:
        flash('Choose a PDF file to upload.', 'error')
        return redirect(url_for('ai_assistant'))

    filename = secure_filename(uploaded_file.filename)
    if not filename or not filename.lower().endswith('.pdf'):
        flash('Only PDF files can be uploaded.', 'error')
        return redirect(url_for('ai_assistant'))

    file_bytes = uploaded_file.read()
    if not file_bytes.startswith(b'%PDF-'):
        flash('The selected file is not a valid PDF.', 'error')
        return redirect(url_for('ai_assistant'))

    try:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(file_bytes))
        if reader.is_encrypted:
            flash('Encrypted PDFs are not supported. Upload an unlocked PDF.', 'error')
            return redirect(url_for('ai_assistant'))
        if not reader.pages:
            flash('The PDF contains no pages.', 'error')
            return redirect(url_for('ai_assistant'))
        if len(reader.pages) > 200:
            flash('PDFs can contain at most 200 pages.', 'error')
            return redirect(url_for('ai_assistant'))

        pages = []
        extracted_characters = 0
        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ''
            extracted_characters += len(page_text)
            if extracted_characters > 2_000_000:
                flash('The extracted PDF text is too large to process.', 'error')
                return redirect(url_for('ai_assistant'))
            if page_text.strip():
                pages.append({'page_number': page_number, 'content': page_text})

        chunks = chunk_document_pages(pages)
        if not chunks:
            flash(
                'No readable text was found. Scanned PDFs need OCR before uploading.',
                'error'
            )
            return redirect(url_for('ai_assistant'))

        document_id = app_logic.db.add_document(
            session['user_id'], filename, len(reader.pages), chunks
        )
        if document_id is None:
            flash('The PDF could not be saved. Please try again.', 'error')
        else:
            flash(f'{filename} was uploaded and is ready for questions.', 'success')
    except ImportError:
        app.logger.exception('PDF reader dependency is unavailable')
        flash('PDF support is unavailable. Install the project requirements.', 'error')
    except Exception:
        app.logger.exception('Failed to process uploaded PDF')
        flash('The PDF could not be read. Check that it is a valid, unlocked PDF.', 'error')

    return redirect(url_for('ai_assistant'))


@app.route('/delete_document/<int:document_id>', methods=['POST'])
def delete_document(document_id):
    """Delete an uploaded document belonging to the logged-in user."""
    if 'user_id' not in session:
        flash('Please log in to manage documents', 'warning')
        return redirect(url_for('login'))
    if app_logic.db.delete_user_document(document_id, session['user_id']):
        flash('Document deleted.', 'success')
    else:
        flash('Document not found or you do not have permission to delete it.', 'error')
    return redirect(url_for('ai_assistant'))


@app.route('/pdf_query', methods=['POST'])
def pdf_query():
    """Answer a question using only retrieved passages from the user's PDFs."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in'}), 401

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'success': False, 'message': 'Send a valid JSON request.'}), 400
    question = data.get('question')
    if not isinstance(question, str) or not question.strip():
        return jsonify({'success': False, 'message': 'Enter a question.'}), 400
    if len(question) > 1000:
        return jsonify({'success': False, 'message': 'Questions must be 1,000 characters or fewer.'}), 400

    try:
        return jsonify(app_logic.process_document_question(
            session['user_id'], question.strip()
        ))
    except RuntimeError as error:
        app.logger.error('PDF question could not be answered: %s', error)
        return jsonify({'success': False, 'message': str(error)}), 503
    except Exception:
        app.logger.exception('PDF question processing failed')
        return jsonify({'success': False, 'message': 'Could not process the question.'}), 500


@app.route('/ai_query', methods=['POST'])
def ai_query():
    """Process AI queries"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in'})
    
    try:
        data = request.get_json()
        note_id = data.get('note_id')
        request_type = data.get('request_type')
        question = data.get('question', '')
        
        if not note_id or not request_type:
            return jsonify({'success': False, 'message': 'Missing required parameters'})
        
        # Process AI request
        result = app_logic.process_ai_request(note_id, request_type, question)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"AI query error: {e}")
        return jsonify({'success': False, 'message': 'Failed to process request'})


@app.route('/profile')
def profile():
    """User profile page"""
    if 'user_id' not in session:
        flash('Please log in to view profile', 'warning')
        return redirect(url_for('login'))
    
    # Get user statistics
    dashboard_data = app_logic.get_user_dashboard_data(session['user_id'])
    
    return render_template('profile.html',
                         user_name=session['user_name'],
                         user_email=session['user_email'],
                         total_notes=dashboard_data['total_notes'])


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500


@app.errorhandler(RequestEntityTooLarge)
def request_too_large(error):
    """Show a useful message when a PDF exceeds the upload limit."""
    flash('The upload is too large. PDF files must be 16 MB or smaller.', 'error')
    return redirect(url_for('ai_assistant'))


if __name__ == '__main__':
    # Initialize database on startup
    print("Starting AI-Powered Study Assistant...")
    print("Database initializing...")
    
    # Run the application
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    app.run(
        debug=os.getenv('DEBUG', 'False').lower() == 'true',
        host=host,
        port=port
    )