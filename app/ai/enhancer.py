import openai
import os
import logging
from openai import OpenAI

def clean_text(text):
    """Remove any markdown formatting or special characters"""
    # Remove markdown asterisks and underscores
    text = text.replace('*', '').replace('_', '')
    return text.strip()

def enhance_resume_content(data):
    """Enhance resume content using OpenAI's GPT model"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logging.warning("OpenAI API key not found. Returning original content.")
            return data

        client = OpenAI(api_key=api_key)
        logging.info("Starting resume enhancement process...")

        # Format and enhance basic fields
        format_prompt = f"""
        Format the following text fields with proper capitalization and punctuation.
        Follow these rules:
        1. Use title case for proper nouns, organizations, and job titles
        2. Keep technical terms in their correct case (e.g., iOS, JavaScript, PostgreSQL)
        3. Use consistent punctuation
        4. Remove any trailing periods from bullet points
        5. Ensure consistent spacing

        Fields to format:
        University: {data.get('university', '')}
        Degree: {data.get('degree', '')}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are a professional editor who specializes in resume formatting and style."
                }, {
                    "role": "user",
                    "content": format_prompt
                }]
            )

            formatted_text = response.choices[0].message.content.strip()
            for line in formatted_text.split('\n'):
                line = line.strip()
                if line.lower().startswith('university:'):
                    data['university'] = line.split(':', 1)[1].strip()
                elif line.lower().startswith('degree:'):
                    data['degree'] = line.split(':', 1)[1].strip()

        except Exception as e:
            logging.error(f"Error formatting basic fields: {str(e)}")

        # Enhance each work experience
        enhanced_experiences = []
        for exp in data.get('experiences', []):
            logging.info(f"Original experience: {exp}")
            responsibilities = exp.get('responsibilities', [])
            
            if responsibilities:
                prompt = f"""
                Enhance and format the following job responsibilities to be more impactful and professional.
                Follow these rules:
                1. Use strong action verbs at the start of each point
                2. Quantify achievements where possible
                3. Focus on results and impact
                4. Use proper capitalization (including technical terms)
                5. Remove trailing periods
                6. Keep each point concise
                7. Ensure consistent punctuation throughout
                8. DO NOT use any markdown formatting (no asterisks or underscores)
                9. Use plain text for technical terms (e.g., write "Python" not "*Python*")

                Role: {exp['job_title']} at {exp['company']}
                Original responsibilities:
                {' '.join(responsibilities)}
                """

                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{
                            "role": "system",
                            "content": "You are a professional resume writer who specializes in creating impactful job descriptions with consistent formatting. Do not use markdown formatting in your responses."
                        }, {
                            "role": "user",
                            "content": prompt
                        }]
                    )

                    enhanced_responsibilities = response.choices[0].message.content.strip().split('\n')
                    # Clean up the bullet points
                    enhanced_responsibilities = [
                        clean_text(point.strip().strip('•-').strip().rstrip('.'))
                        for point in enhanced_responsibilities
                        if point.strip()
                    ]
                    logging.info(f"Enhanced responsibilities: {enhanced_responsibilities}")
                    
                    # Format job title and company
                    format_job_prompt = f"""
                    Format the following job information with proper capitalization and punctuation:
                    Job Title: {exp['job_title']}
                    Company: {exp['company']}
                    Date: {exp['job_date']}
                    """

                    job_response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{
                            "role": "system",
                            "content": "You are a professional editor who specializes in resume formatting."
                        }, {
                            "role": "user",
                            "content": format_job_prompt
                        }]
                    )

                    formatted_job = job_response.choices[0].message.content.strip()
                    formatted_title = ""
                    formatted_company = ""
                    formatted_date = ""
                    
                    for line in formatted_job.split('\n'):
                        line = line.strip()
                        if line.lower().startswith('job title:'):
                            formatted_title = line.split(':', 1)[1].strip()
                        elif line.lower().startswith('company:'):
                            formatted_company = line.split(':', 1)[1].strip()
                        elif line.lower().startswith('date:'):
                            formatted_date = line.split(':', 1)[1].strip()
                    
                    enhanced_experiences.append({
                        'job_title': formatted_title or exp['job_title'],
                        'company': formatted_company or exp['company'],
                        'job_date': formatted_date or exp['job_date'],
                        'responsibilities': enhanced_responsibilities
                    })

                except Exception as e:
                    logging.error(f"Error enhancing experience: {str(e)}")
                    enhanced_experiences.append(exp)
            else:
                enhanced_experiences.append(exp)

        data['experiences'] = enhanced_experiences

        # Enhance each project
        enhanced_projects = []
        for proj in data.get('projects', []):
            logging.info(f"Original project: {proj}")
            description = proj.get('description', [])
            
            if description:
                prompt = f"""
                Enhance and format the following project description to be more impactful and professional.
                Follow these rules:
                1. Start each point with a strong action verb
                2. Focus on technical achievements and results
                3. Use proper capitalization for technical terms
                4. Remove trailing periods
                5. Keep consistent punctuation
                6. Highlight specific technologies used
                7. DO NOT use any markdown formatting (no asterisks or underscores)
                8. Use plain text for technical terms (e.g., write "React.js" not "*React.js*")
                9. Keep technical terms in their correct case

                Project: {proj['project_name']}
                Technologies: {proj['technologies']}
                Original description:
                {' '.join(description)}
                """

                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{
                            "role": "system",
                            "content": "You are a technical resume writer who specializes in showcasing project achievements with consistent formatting. Do not use any markdown or special formatting in your responses."
                        }, {
                            "role": "user",
                            "content": prompt
                        }]
                    )

                    enhanced_description = response.choices[0].message.content.strip().split('\n')
                    # Clean up the bullet points and remove any markdown
                    enhanced_description = [
                        clean_text(point.strip().strip('•-').strip().rstrip('.'))
                        for point in enhanced_description
                        if point.strip()
                    ]
                    logging.info(f"Enhanced project description: {enhanced_description}")
                    
                    # Format project name and technologies
                    format_proj_prompt = f"""
                    Format the following project information with proper capitalization and punctuation:
                    Project Name: {proj['project_name']}
                    Technologies: {proj['technologies']}
                    Date: {proj['date']}
                    
                    Rules:
                    1. Keep technical terms in their correct case (e.g., React.js, Node.js, MongoDB)
                    2. Use title case for project name
                    3. Ensure consistent formatting of technology lists
                    4. DO NOT use any markdown formatting
                    """

                    proj_response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{
                            "role": "system",
                            "content": "You are a technical editor who specializes in formatting project descriptions. Do not use markdown or special formatting."
                        }, {
                            "role": "user",
                            "content": format_proj_prompt
                        }]
                    )

                    formatted_proj = proj_response.choices[0].message.content.strip()
                    formatted_name = ""
                    formatted_tech = ""
                    formatted_date = ""
                    
                    for line in formatted_proj.split('\n'):
                        line = line.strip()
                        if line.lower().startswith('project name:'):
                            formatted_name = clean_text(line.split(':', 1)[1].strip())
                        elif line.lower().startswith('technologies:'):
                            formatted_tech = clean_text(line.split(':', 1)[1].strip())
                        elif line.lower().startswith('date:'):
                            formatted_date = clean_text(line.split(':', 1)[1].strip())
                    
                    enhanced_projects.append({
                        'project_name': formatted_name or proj['project_name'],
                        'technologies': formatted_tech or proj['technologies'],
                        'date': formatted_date or proj['date'],
                        'description': enhanced_description
                    })

                except Exception as e:
                    logging.error(f"Error enhancing project: {str(e)}")
                    enhanced_projects.append(proj)
            else:
                enhanced_projects.append(proj)

        data['projects'] = enhanced_projects

        # Enhance and format skills
        logging.info("Starting skills enhancement...")
        skills_prompt = f"""
        Enhance and format the following technical skills with proper capitalization and organization.
        Follow these rules:
        1. Keep technical terms in their correct case (e.g., Python, JavaScript, React.js)
        2. Group similar technologies together
        3. Use consistent punctuation in lists (commas between items)
        4. Order from most to least relevant
        5. Use consistent formatting throughout
        6. DO NOT use any markdown formatting or special characters (no asterisks, underscores, etc.)
        7. Separate items with commas only

        Programming: {data.get('programming_skills', '')}
        Web Technologies: {data.get('web_skills', '')}
        Tools: {data.get('tools', '')}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are a technical resume expert who specializes in organizing and formatting technical skills. Do not use any markdown formatting or special characters in your response."
                }, {
                    "role": "user",
                    "content": skills_prompt
                }]
            )

            # Parse the enhanced skills and clean any remaining special characters
            enhanced_skills = response.choices[0].message.content.strip()
            logging.info(f"Enhanced skills response: {enhanced_skills}")

            def clean_skill_text(text):
                """Remove any markdown formatting or special characters"""
                # Remove markdown asterisks and underscores
                text = text.replace('*', '').replace('_', '')
                # Ensure consistent comma spacing
                text = ', '.join(part.strip() for part in text.split(','))
                return text

            for line in enhanced_skills.split('\n'):
                line = line.strip()
                if line.lower().startswith('programming:'):
                    data['programming_skills'] = clean_skill_text(line.split(':', 1)[1].strip())
                elif line.lower().startswith('web technologies:'):
                    data['web_skills'] = clean_skill_text(line.split(':', 1)[1].strip())
                elif line.lower().startswith('tools:'):
                    data['tools'] = clean_skill_text(line.split(':', 1)[1].strip())

            logging.info("Final enhanced data:")
            logging.info(f"Programming: {data['programming_skills']}")
            logging.info(f"Web Tech: {data['web_skills']}")
            logging.info(f"Tools: {data['tools']}")

        except Exception as e:
            logging.error(f"Error enhancing skills: {str(e)}")

        return data

    except Exception as e:
        logging.error(f"Error enhancing resume content: {str(e)}")
        return data  # Return original data if enhancement fails