from .models import Project, Skill, Workexp

from fuzzywuzzy import fuzz 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class CalculateProjectSimilarity:
    @staticmethod
    def create_string(data_dict):
        result_string = ' '.join([str(value) for value in data_dict.values()])
        
        return result_string

    @staticmethod
    def create_tuple_array_of_projects(user_id):
        projects = Project.query.filter_by(user_id=user_id).all()
        project_info = [(project.project_title, project.project_description) for project in projects]

        return project_info

    @staticmethod
    def calculate_similarity(user_projects_info, job_ats_keywords_string):
        vectorizer = TfidfVectorizer().fit([info[1] for info in user_projects_info])

        job_vector = vectorizer.transform([job_ats_keywords_string])

        similarity_scores = []

        for project_title, project_description in user_projects_info:
            user_vector = vectorizer.transform([project_description])
            similarity_score = cosine_similarity(user_vector, job_vector)
            similarity_scores.append((project_title, similarity_score[0][0]))

        return similarity_scores

    @staticmethod
    def function_calculate_project_similarity(data, user_id):
        user_projects = CalculateProjectSimilarity.create_tuple_array_of_projects(user_id)
        job_ats_keywords_string = CalculateProjectSimilarity.create_string(data)
        similarity_scores = CalculateProjectSimilarity.calculate_similarity(user_projects, job_ats_keywords_string)
        
        return similarity_scores
    
class CalculateSkillsSimilarity:
    @staticmethod
    def create_array(data_dict, dic_keys):
        lowercase_dict = {key.lower(): value for key, value in data_dict.items()}
        
        for dic_key in dic_keys:
            job_ats_skills = lowercase_dict.get(dic_key.lower(), [])
            if job_ats_skills:
                job_ats_keywords_array = [ats_keyword.lower() for ats_keyword in job_ats_skills if isinstance(ats_keyword, str)]
                
                return job_ats_keywords_array

        return []
    
    @staticmethod
    def create_string_array_of_skills(user_id):
        skills = Skill.query.filter_by(user_id=user_id).all()
        user_skills_from_db = [str(skill.data).lower() for skill in skills]
        
        return user_skills_from_db
    
    @staticmethod
    def find_matching_words(skills_list, ats_keyword_list, threshold=70):
        matching_words = []

        for user_skill in skills_list:
            for ats_keyword in ats_keyword_list:
                similarity_score = fuzz.token_sort_ratio(user_skill, ats_keyword)
                if similarity_score >= threshold:
                    matching_words.append(user_skill)
                    break

        return matching_words
    
    @staticmethod
    def calculate_similarity(data_dict, dic_key, user_id):
        ats_keywords = CalculateSkillsSimilarity.create_array(data_dict, dic_key)
        user_skills = CalculateSkillsSimilarity.create_string_array_of_skills(user_id)
        matching_words = CalculateSkillsSimilarity.find_matching_words(user_skills, ats_keywords)
        
        return matching_words
    
class CalculateWorkexpsSimilarity:
    @staticmethod
    def create_string_workexp(data_dict):
        result_string = ' '.join([str(value) for value in data_dict])
        return result_string

    @staticmethod
    def create_array_of_workexp(user_id):
        workexps = Workexp.query.filter_by(user_id=user_id).all()
        responsibilities_list = []

        for workexp in workexps:
            responsibilities_str = workexp.workexp_responsiblities.lower()
            responsibilities_str = responsibilities_str.replace('"', '').replace('[', '').replace(']', '').replace('\\', '')
            responsibilities = responsibilities_str.split(",")

            for responsibility in responsibilities:
                cleaned_responsibility = responsibility.strip()
                if cleaned_responsibility:
                    responsibilities_list.append((workexp.workexp_title, cleaned_responsibility))

            return responsibilities_list

    @staticmethod
    def calculate_similarity_workexp(user_workexp_info, job_ats_keywords_string):
        vectorizer = TfidfVectorizer().fit([info[1] for info in user_workexp_info])
        job_vector = vectorizer.transform([job_ats_keywords_string])
        similarity_scores = []

        for workexp_title, cleaned_responsibility in user_workexp_info:
            user_vector = vectorizer.transform([cleaned_responsibility])
            similarity_score = cosine_similarity(user_vector, job_vector)
            similarity_scores.append((cleaned_responsibility, similarity_score[0][0]))

        return similarity_scores

    @staticmethod
    def calculate_similarity(data_dict, user_id):
        user_workexps = CalculateWorkexpsSimilarity.create_array_of_workexp(user_id)
        ats_keywords = CalculateWorkexpsSimilarity.create_string_workexp(data_dict) 
        matching_workexp = CalculateWorkexpsSimilarity.calculate_similarity_workexp(user_workexps, ats_keywords)
        
        return matching_workexp






    