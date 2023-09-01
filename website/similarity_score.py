from .models import Project

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class CalculateProjectSimilarity:
    @staticmethod
    def create_string(job_ats_keywords):
        job_ats_keywords_string = ' '.join(job_ats_keywords)
        
        return job_ats_keywords_string

    @staticmethod
    def create_string_array_of_projects(user_id):
        projects = Project.query.filter_by(user_id=user_id).all()
        user_projects_from_db = [
            f"{project.project_title} {project.project_description} {project.project_core_skill}"
            for project in projects
        ]
        
        return user_projects_from_db

    @staticmethod
    def calculate_similarity(user_projects_from_db, job_ats_keywords_string):
        vectorizer = TfidfVectorizer().fit(user_projects_from_db)
        job_vector = vectorizer.transform([job_ats_keywords_string])

        similarity_scores = []

        for user_project in user_projects_from_db:
            user_vector = vectorizer.transform([user_project])
            similarity_score = cosine_similarity(user_vector, job_vector)
            similarity_scores.append(similarity_score[0][0])

        return similarity_scores

    @staticmethod
    def function_calculate_similarity(user_id, job_ats_keywords):
        user_projects = CalculateProjectSimilarity.create_string_array_of_projects(user_id)
        job_ats_keywords_string = CalculateProjectSimilarity.create_string(job_ats_keywords)
        similarity_scores = CalculateProjectSimilarity.calculate_similarity(user_projects, job_ats_keywords_string)
        
        return similarity_scores