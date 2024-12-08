def escape_latex(text):
    """Escape special LaTeX characters"""
    if not text:
        return ""
    chars = {
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '~': '\\textasciitilde{}',
        '^': '\\textasciicircum{}',
        '\\': '\\textbackslash{}',
        '·': '$\\cdot$',
    }
    return ''.join(chars.get(c, c) for c in str(text))

def create_resume_template(data):
    """Create a minimal LaTeX template using user data"""
    # Escape special characters in text fields
    escaped_data = {
        'name': escape_latex(data['name']),
        'address': escape_latex(data['address']),
        'phone': escape_latex(data['phone']),
        'email': escape_latex(data['email']),
        'university': escape_latex(data['university']),
        'degree': escape_latex(data['degree']),
        'graduation': escape_latex(data['graduation']),
        'gpa': escape_latex(data['gpa']),
        'programming_skills': escape_latex(data['programming_skills']),
        'web_skills': escape_latex(data['web_skills']),
        'tools': escape_latex(data['tools'])
    }
    
    # Create experience sections
    experience_sections = []
    for exp in data['experiences']:
        responsibilities = '\n'.join([
            f"\\item {escape_latex(resp.strip())}" 
            for resp in exp['responsibilities'] 
            if resp.strip()
        ])
        
        experience_section = f"""
\\textbf{{{escape_latex(exp['job_title'])}}} \\hfill \\textit{{{escape_latex(exp['job_date'])}}}
\\\\
\\textbf{{{escape_latex(exp['company'])}}}

\\begin{{itemize}}
{responsibilities}
\\end{{itemize}}
"""
        experience_sections.append(experience_section)
    
    # Create project sections
    project_sections = []
    for proj in data['projects']:
        description = '\n'.join([
            f"\\item {escape_latex(desc.strip())}" 
            for desc in proj['description'] 
            if desc.strip()
        ])
        
        project_section = f"""
\\textbf{{{escape_latex(proj['project_name'])}}} \\hfill \\textit{{{escape_latex(proj['date'])}}}
\\\\
\\textit{{Technologies:}} {escape_latex(proj['technologies'])}

\\begin{{itemize}}
{description}
\\end{{itemize}}
"""
        project_sections.append(project_section)
    
    # Join all sections with spacing
    all_experiences = '\\vspace{0.5em}'.join(experience_sections)
    all_projects = '\\vspace{0.5em}'.join(project_sections)
    
    template = r"""
\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[margin=0.5in]{geometry}
\usepackage{parskip}
\usepackage{textcomp}
\usepackage{enumitem}

% Adjust spacing
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.3em}
\setlength{\baselineskip}{1.1em}

% Custom section formatting
\makeatletter
\renewcommand{\section}{\@startsection{section}{1}{0pt}
  {-1.5ex plus -1ex minus -.2ex}{0.7ex plus .2ex}{\Large\bf}}
\makeatother

% Adjust list spacing
\setlist{nosep,leftmargin=*,topsep=0.3em,itemsep=0.2em,parsep=0em}

\begin{document}
"""

    # Add content with proper formatting
    content = f"""
{{\LARGE \\textbf{{{escaped_data['name']}}}}}\\hfill
{{\\small {escaped_data['address']}}}

{{\\small {escaped_data['phone']} $\\cdot$ {escaped_data['email']}}}

\\vspace{{0.3em}}
\\noindent\\rule{{\\textwidth}}{{0.4pt}}
\\vspace{{0.3em}}

\\section*{{Education}}
\\textbf{{{escaped_data['university']}}} \\hfill \\textit{{{escaped_data['graduation']}}}
{escaped_data['degree']} $\\cdot$ GPA: {escaped_data['gpa']}

\\vspace{{0.2em}}
\\noindent\\rule{{0.6\\textwidth}}{{0.2pt}}
\\vspace{{0.2em}}

\\section*{{Professional Experience}}
{all_experiences}

\\vspace{{0.2em}}
\\noindent\\rule{{0.6\\textwidth}}{{0.2pt}}
\\vspace{{0.2em}}

\\section*{{Projects}}
{all_projects}

\\vspace{{0.2em}}
\\noindent\\rule{{0.6\\textwidth}}{{0.2pt}}
\\vspace{{0.2em}}

\\section*{{Technical Skills}}
\\textbf{{Programming Languages:}} {escaped_data['programming_skills']}
\\vspace{{0.2em}}
\\textbf{{Web Technologies:}} {escaped_data['web_skills']}
\\vspace{{0.2em}}
\\textbf{{Development Tools:}} {escaped_data['tools']}
"""

    # Add closing document tag
    footer = r"""
\end{document}
"""

    return template + content + footer 