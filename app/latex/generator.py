import os
import tempfile
import subprocess
import logging
from flask import send_file, jsonify
from .template import create_resume_template

def run_pdflatex(tex_path, temp_dir):
    """Run pdflatex and capture output"""
    try:
        # Run pdflatex twice to resolve references
        for _ in range(2):
            process = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', tex_path],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                encoding='latin-1'
            )
            
            # Log the complete output for debugging
            logging.debug(f"LaTeX stdout: {process.stdout}")
            if process.stderr:
                logging.debug(f"LaTeX stderr: {process.stderr}")
            
            if process.returncode != 0:
                # Try to extract the actual error message from the output
                output = process.stdout or process.stderr
                error_lines = []
                for line in output.split('\n'):
                    if any(x in line.lower() for x in ['error', 'fatal', 'undefined']):
                        error_lines.append(line.strip())
                
                error_msg = '\n'.join(error_lines) if error_lines else "Unknown LaTeX error"
                raise Exception(error_msg)
                
        return True
    except Exception as e:
        raise Exception(f"LaTeX compilation failed: {str(e)}")

def generate_pdf(data):
    """Generate PDF from LaTeX template using user data"""
    try:
        # Create a temporary directory for our files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create the LaTeX file
            tex_path = os.path.join(temp_dir, 'resume.tex')
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(create_resume_template(data))
            
            # Run pdflatex with better error handling
            try:
                run_pdflatex(tex_path, temp_dir)
            except Exception as e:
                logging.error(f"LaTeX Error: {str(e)}")
                return jsonify({
                    'error': 'PDF generation failed',
                    'message': str(e)
                }), 500
            
            # Read the generated PDF
            pdf_path = os.path.join(temp_dir, 'resume.pdf')
            if not os.path.exists(pdf_path):
                return jsonify({
                    'error': 'PDF generation failed',
                    'message': 'PDF file was not generated'
                }), 500
            
            # Create a temporary file to store the PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                with open(pdf_path, 'rb') as pdf:
                    tmp_file.write(pdf.read())
                tmp_path = tmp_file.name
            
            # Send the PDF file
            return_value = send_file(
                tmp_path,
                download_name='resume.pdf',
                mimetype='application/pdf'
            )
            
            # Clean up
            os.unlink(tmp_path)
            return return_value

    except Exception as e:
        logging.exception("Error during PDF generation")
        return jsonify({
            'error': 'PDF generation failed',
            'message': str(e)
        }), 500 