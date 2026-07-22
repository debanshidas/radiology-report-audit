"""
server.py — Flask backend for AI Radiology Report Audit & Quality Analyzer
Run: python server.py  →  http://localhost:5000
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
import os, io, sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, static_folder='static', static_url_path='')


# ── Static serving ────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


# ── API: Upload + extract text ────────────────────────────────────────────────
@app.route('/api/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    filename = file.filename or ''
    if not filename.lower().endswith(('.pdf', '.docx', '.txt')):
        return jsonify({'error': 'Unsupported file type. Upload PDF, DOCX, or TXT.'}), 400

    file_bytes = file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        return jsonify({'error': 'File exceeds 10 MB limit.'}), 400

    try:
        from utils.extractor import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
        if filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_bytes)
        elif filename.lower().endswith('.docx'):
            text = extract_text_from_docx(file_bytes)
        else:
            text = extract_text_from_txt(file_bytes)

        if not text.strip():
            return jsonify({'error': 'File is empty or unreadable.'}), 400
        return jsonify({'text': text, 'filename': filename, 'chars': len(text)})
    except Exception as e:
        return jsonify({'error': f'Extraction failed: {str(e)}'}), 500


# ── API: Run Gemini audit ─────────────────────────────────────────────────────
@app.route('/api/analyze', methods=['POST'])
def analyze():
    data     = request.get_json(silent=True) or {}
    provider = data.get('provider', 'gemini').lower()
    env_key  = 'GROQ_API_KEY' if provider == 'groq' else 'GEMINI_API_KEY'
    api_key  = (data.get('api_key') or '').strip() or os.environ.get(env_key, '')
    report   = (data.get('report_text') or '').strip()
    modality = data.get('modality', 'Chest X-Ray')
    sections = data.get('mandatory_sections', [])

    if not api_key:
        return jsonify({'error': f'{provider.title()} API key required. Enter it in Settings.'}), 400
    if not report:
        return jsonify({'error': 'Report text is required.'}), 400

    try:
        from utils.analyzer import audit_report
        result = audit_report(api_key=api_key, report_text=report, modality=modality,
                              mandatory_sections=sections, provider=provider)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 502
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


# ── API: Generate PDF ─────────────────────────────────────────────────────────
@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.get_json(silent=True) or {}
    filename     = data.get('filename', 'report.txt')
    modality     = data.get('modality', 'Unknown')
    audit_result = data.get('audit_result', {})

    if not audit_result:
        return jsonify({'error': 'No audit result provided.'}), 400

    try:
        from utils.pdf_generator import generate_audit_pdf
        pdf_bytes = generate_audit_pdf(
            report_filename=filename, modality=modality,
            audit_result=audit_result, audit_timestamp=datetime.now()
        )
        safe = filename.rsplit('.', 1)[0].replace(' ', '_')
        return send_file(io.BytesIO(pdf_bytes), mimetype='application/pdf',
                         as_attachment=True, download_name=f'radiology_audit_{safe}.pdf')
    except Exception as e:
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500


# ── API: Test API key ─────────────────────────────────────────────────────────
@app.route('/api/test-key', methods=['POST'])
def test_key():
    data     = request.get_json(silent=True) or {}
    api_key  = (data.get('api_key') or '').strip()
    provider = data.get('provider', 'gemini').lower()
    if not api_key:
        return jsonify({'error': 'No key provided.'}), 400
    try:
        if provider == 'groq':
            from groq import Groq
            client = Groq(api_key=api_key)
            resp = client.chat.completions.create(
                model='llama-3.3-70b-versatile',
                messages=[{'role': 'user', 'content': 'Reply: OK'}],
                max_tokens=5,
            )
            if resp.choices[0].message.content:
                return jsonify({'status': 'ok', 'message': 'Groq API key is valid! (Llama 3.3 70B ready)'})
        else:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key)
            resp = client.models.generate_content(
                model='gemini-2.0-flash', contents='Reply: OK',
                config=types.GenerateContentConfig(temperature=0, max_output_tokens=5)
            )
            if resp.text:
                return jsonify({'status': 'ok', 'message': 'Gemini API key is valid and connected!'})
        return jsonify({'error': 'Empty response from provider.'}), 502
    except Exception as e:
        return jsonify({'error': str(e)}), 401


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('\n AI Radiology Report Audit & Quality Analyzer')
    print('   Open: http://localhost:5000\n')
    app.run(debug=True, port=5000, host='0.0.0.0')
