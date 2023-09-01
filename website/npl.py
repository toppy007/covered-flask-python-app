from .models import Project, Skill, Workexp

from fuzzywuzzy import fuzz 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class CalculateProjectSimilarity:
    @staticmethod
    def create_string(data_dict, dic_keys):
        lowercase_dict = {key.lower(): value for key, value in data_dict.items()}

        # Check each possible key and return the first one found
        for dic_key in dic_keys:
            job_ats_skills = lowercase_dict.get(dic_key.lower(), [])
            if job_ats_skills:
                # Join the list of keywords into a single string
                job_ats_keywords_string = ' '.join([ats_keyword.lower() for ats_keyword in job_ats_skills if isinstance(ats_keyword, str)])
                return job_ats_keywords_string

        return ""


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
        vectorizer = TfidfVectorizer().fit(user_projects_from_db)  # Fit the vectorizer on user projects

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
    def create_array(data_dict, dic_keys):
        lowercase_dict = {key.lower(): value for key, value in data_dict.items()}

        # Check each possible key and return the first one found
        for dic_key in dic_keys:
            job_ats_skills = lowercase_dict.get(dic_key.lower(), [])
            if job_ats_skills:
                job_ats_keywords_array = [ats_keyword.lower() for ats_keyword in job_ats_skills if isinstance(ats_keyword, str)]
                
                return job_ats_keywords_array

        # If none of the keys are found, return an empty list
        return []
    
    @staticmethod
    def create_string_array_of_skills(user_id):
        skills = Skill.query.filter_by(user_id=user_id).all()
        user_skills_from_db = [str(skill.data).lower() for skill in skills]
        
        return user_skills_from_db
    
    @staticmethod
    def find_matching_words(skills_list, ats_keyword_list, threshold=80):
        matching_words = []

        for user_skill in skills_list:
            for ats_keyword in ats_keyword_list:
                similarity_score = fuzz.token_sort_ratio(user_skill, ats_keyword)
                if similarity_score >= threshold:
                    matching_words.append(user_skill)
                    break  # Break out of the inner loop when a match is found

        return matching_words
    
    @staticmethod
    def calculate_similarity(data_dict, dic_key, user_id):
        ats_keywords = CalculateSkillsSimilarity.create_array(data_dict, dic_key)
        print(ats_keywords)
        user_skills = CalculateSkillsSimilarity.create_string_array_of_skills(user_id)
        print(user_skills)
        matching_words = CalculateSkillsSimilarity.find_matching_words(user_skills, ats_keywords)
        
        return matching_words