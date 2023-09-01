from .models import Project, Skill, Workexp

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class CalculateProjectSimilarity:
    @staticmethod
    def create_string(data_dict, dic_key):
        lowercase_dict = {key.lower(): value for key, value in data_dict.items()}
        job_ats_skills = lowercase_dict.get(dic_key, [])
        job_ats_keywords = [ats_keyword.lower() for ats_keyword in job_ats_skills if isinstance(ats_keyword, str)]
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
    def function_calculate_project_similarity(user_id, dict_key, job_ats_keywords):
        user_projects = CalculateProjectSimilarity.create_string_array_of_projects(user_id)
        job_ats_keywords_string = CalculateProjectSimilarity.create_string(job_ats_keywords, dict_key)
        similarity_scores = CalculateProjectSimilarity.calculate_similarity(user_projects, job_ats_keywords_string)
        
        return similarity_scores
    
class CalculateSkillsSimilarity:
    @staticmethod
    def create_array(data_dict, dic_key):
        lowercase_dict = {key.lower(): value for key, value in data_dict.items()}
        job_ats_skills = lowercase_dict.get(dic_key, [])
        job_ats_keywords_array = [ats_keyword.lower() for ats_keyword in job_ats_skills if isinstance(ats_keyword, str)]
        
        return job_ats_keywords_array
    
    @staticmethod
    def create_string_array_of_skills(user_id):
        skills = Skill.query.filter_by(user_id=user_id).all()
        user_skills_from_db = [skill.data for skill in skills]
        
        return user_skills_from_db
    
    @staticmethod
    def find_matching_words(skills_list, ats_keyword_list, threshold=0.5):
        set1 = set(skills_list)
        set2 = set(ats_keyword_list)

        jaccard_similarity = len(set1.intersection(set2)) / len(set1.union(set2))

        if jaccard_similarity >= threshold:
            matching_words = list(set1.intersection(set2))
            return matching_words
        else:
            return []
    
    @staticmethod
    def calculate_similarity(data_dict, dic_key, user_id, threshold=0.5):
        ats_keywords = CalculateSkillsSimilarity.create_array(data_dict, dic_key)
        user_skills = CalculateSkillsSimilarity.create_string_array_of_skills(user_id)
        matching_words = CalculateSkillsSimilarity.find_matching_words(user_skills, ats_keywords, threshold)

        return matching_words