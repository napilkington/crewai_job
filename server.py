#!/usr/bin/env python3
"""
Local server to receive job data from browser extension and process with CrewAI
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from pathlib import Path
import subprocess
import tempfile

app = Flask(__name__)
CORS(app)  # Allow requests from browser extension

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'CrewAI server is running'})

@app.route('/process-job', methods=['POST'])
def process_job():
    """
    Receive job data from browser extension and process it
    """
    try:
        job_data = request.json
        
        if not job_data:
            return jsonify({'error': 'No job data provided'}), 400
        
        print(f"\n{'='*80}")
        print(f"📥 Received job from browser extension")
        print(f"Title: {job_data.get('title', 'N/A')}")
        print(f"Company: {job_data.get('company', 'N/A')}")
        print(f"Location: {job_data.get('location', 'N/A')}")
        print(f"{'='*80}\n")
        
        # Save job data to a temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, dir='.') as f:
            html_content = generate_html_from_job_data(job_data)
            f.write(html_content)
            temp_file = f.name
        
        try:
            # Get absolute path
            temp_file_path = Path(temp_file).absolute()
            file_url = f"file://{temp_file_path}"
            
            print(f"📝 Created temporary file: {temp_file_path}")
            print(f"🚀 Processing with CrewAI...\n")
            
            # Run the job application script with real-time output
            process = subprocess.Popen(
                ['python', 'job_application_agents.py'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            # Send the file URL as input
            process.stdin.write(file_url + '\n')
            process.stdin.close()
            
            # Stream output in real-time
            output_lines = []
            for line in process.stdout:
                print(line, end='')  # Print to server console
                output_lines.append(line)
            
            process.wait()
            result_stdout = ''.join(output_lines)
            result_returncode = process.returncode
            
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
            
            if result_returncode == 0:
                print(f"\n{'='*80}")
                print(f"✅ SUCCESS: Documents generated!")
                print(f"{'='*80}\n")
                
                return jsonify({
                    'status': 'success',
                    'message': 'CV and cover letter generated successfully',
                    'output': result_stdout
                })
            else:
                print(f"\n{'='*80}")
                print(f"❌ ERROR: Processing failed")
                print(f"Error output: {result_stdout}")
                print(f"{'='*80}\n")
                
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to process job',
                    'error': result_stdout
                }), 500
                
        except Exception as e:
            # Clean up temp file in case of error
            try:
                os.unlink(temp_file)
            except:
                pass
            raise e
            
    except Exception as e:
        print(f"❌ Server error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def generate_html_from_job_data(job_data):
    """Generate HTML content from job data"""
    title = job_data.get('title', 'Job Title')
    company = job_data.get('company', 'Company Name')
    location = job_data.get('location', 'Location')
    description = job_data.get('description', 'No description provided')
    url = job_data.get('url', '')
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title} - {company}</title>
</head>
<body>
    <h1>{title}</h1>
    <h2>{company}</h2>
    <p><strong>Location:</strong> {location}</p>
    {f'<p><strong>Source:</strong> <a href="{url}">{url}</a></p>' if url else ''}
    <hr>
    <div class="job-description">
        {description.replace(chr(10), '<br>')}
    </div>
</body>
</html>"""
    
    return html

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 CrewAI Job Processing Server")
    print("="*80)
    print("\n📡 Server starting on http://localhost:5000")
    print("\n✅ Ready to receive jobs from browser extension!")
    print("\n💡 Make sure to:")
    print("   1. Install the browser extension")
    print("   2. Navigate to a LinkedIn job posting")
    print("   3. Click the extension icon and 'Extract & Process Job'")
    print("\n" + "="*80 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
