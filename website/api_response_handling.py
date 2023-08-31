from .models import Project

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ResponseHandling():
    def is_non_conforming_response(response):
        lines = response.splitlines()
        lines = [line.strip() for line in lines if line.strip()]
        has_sections = any(line.endswith(":") for line in lines)

        return not has_sections or len(lines) <= 1
    
    def convert_pros_cons_to_dict(response):
        lines = response.splitlines()
        lines = [line.strip() for line in lines if line.strip()]
        
        result_dict = {}
        current_section = None
        
        for line in lines:
            if line.endswith(":"):
                current_section = line[:-1]
                result_dict[current_section] = []
            elif current_section:
                result_dict[current_section].append(line)
        
        return result_dict
    
    def formating_response_lower(analysis_dict):
        lowercase_analysis_dict = {key: [skill.lower() for skill in skills] for key, skills in analysis_dict.items()}
        lowercase_dict = {key.lower(): value for key, value in lowercase_analysis_dict.items()}
                
        return lowercase_dict
    
    def rank_projects_to_add(job_ats_skills, user_id):
        projects = Project.query.filter_by(user_id=user_id).all()
        
        user_projects_from_db = [
            f"{project.project_title} {project.project_description} {project.project_core_skill}"
            for project in projects
        ]
        
        def calculate_similarity(user_projects, job_ats_skills):
            vectorizer = TfidfVectorizer().fit_transform(user_projects)
            vectors = vectorizer.toarray()
            similarity = cosine_similarity(vectors)
            
            print(similarity[0][1])
            
            return similarity[0][1]

        similarity_score = calculate_similarity(user_projects_from_db, job_ats_skills)
        
        print(f"Cosine Similarity Score: {similarity_score}")

                    
                
            