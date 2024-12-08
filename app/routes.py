from flask import Blueprint, render_template, request, current_app, jsonify
from flask_cors import cross_origin
from app.latex.generator import generate_pdf
from app.ai.enhancer import enhance_resume_content
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@cross_origin()
def index():
    current_app.logger.debug("Rendering index page")
    return render_template('index.html')

@main_bp.route('/generate-pdf', methods=['POST', 'OPTIONS'])
@cross_origin()
def create_pdf():
    if request.method == 'OPTIONS':
        return '', 200
        
    current_app.logger.info("Received form submission")
    try:
        # Get form data
        experiences_json = request.form.get('experiences', '[]')
        projects_json = request.form.get('projects', '[]')
        try:
            experiences = json.loads(experiences_json)
            projects = json.loads(projects_json)
        except json.JSONDecodeError:
            experiences = []
            projects = []
            
        data = {
            'name': request.form.get('name'),
            'address': request.form.get('address'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'university': request.form.get('university'),
            'degree': request.form.get('degree'),
            'graduation': request.form.get('graduation'),
            'gpa': request.form.get('gpa'),
            'experiences': [{
                'job_title': exp.get('job_title', ''),
                'company': exp.get('company', ''),
                'job_date': exp.get('job_date', ''),
                'responsibilities': [r.strip() for r in exp.get('responsibilities', '').split('\n') if r.strip()]
            } for exp in experiences],
            'projects': [{
                'project_name': proj.get('project_name', ''),
                'technologies': proj.get('technologies', ''),
                'date': proj.get('date', ''),
                'description': [d.strip() for d in proj.get('description', '').split('\n') if d.strip()]
            } for proj in projects],
            'programming_skills': request.form.get('programming_skills'),
            'web_skills': request.form.get('web_skills'),
            'tools': request.form.get('tools')
        }
        
        current_app.logger.info("Original form data:")
        current_app.logger.info(f"Experiences: {data['experiences']}")
        current_app.logger.info(f"Projects: {data['projects']}")
        current_app.logger.info(f"Skills: {data['programming_skills']}, {data['web_skills']}, {data['tools']}")
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'address']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'fields': missing_fields
            }), 400
        
        # Enhance resume content with AI
        current_app.logger.info("Starting AI enhancement...")
        enhanced_data = enhance_resume_content(data)
        
        current_app.logger.info("Enhanced data:")
        current_app.logger.info(f"Enhanced experiences: {enhanced_data['experiences']}")
        current_app.logger.info(f"Enhanced projects: {enhanced_data['projects']}")
        current_app.logger.info(f"Enhanced skills: {enhanced_data['programming_skills']}, {enhanced_data['web_skills']}, {enhanced_data['tools']}")
        
        # Generate PDF with enhanced content
        current_app.logger.info("Generating PDF with enhanced content...")
        return generate_pdf(enhanced_data)
        
    except Exception as e:
        current_app.logger.error(f"Error processing form: {str(e)}")
        return jsonify({
            'error': 'Error processing form',
            'message': str(e)
        }), 500 