from .models import Project, Skill, Workexp
from . import db

import nltk
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from fuzzywuzzy import fuzz 

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('stopwords')
nltk.download('punkt')

class CalculateProjectSimilarity:
    @staticmethod
    def create_string(input_text):
        tokens = word_tokenize(input_text)
        tokens = [word.lower() for word in tokens if word.isalnum()]
        
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]
        cleaned_text = ' '.join(tokens)
        result_string = ' '.join(cleaned_text.split())
        
        return result_string

    @staticmethod
    def create_tuple_array_of_projects(user_id):
        projects = Project.query.filter_by(user_id=user_id).all()
        project_info = [(project.id, project.project_title, project.project_description, project.project_core_skill) for project in projects]

        return project_info

    @staticmethod
    def calculate_similarity(user_projects_info, job_ats_keywords_string):
        vectorizer = TfidfVectorizer().fit([info[2] + " " + info[3] for info in user_projects_info])

        job_vector = vectorizer.transform([job_ats_keywords_string])

        similarity_scores = []

        for id, project_title, project_description, project_core_skill in user_projects_info:
            user_vector = vectorizer.transform([project_description, project_core_skill])
            similarity_score = cosine_similarity(user_vector, job_vector)
            similarity_scores.append((id, project_title, similarity_score[0][0]))

        return similarity_scores
    
    @staticmethod
    def threshold(projects, threshold=0.2):
        
        print(projects)
        
        projects_to_include = []
        
        for project in projects:
            similarity_score = project[2]
            print(similarity_score)
            print(type(similarity_score))
            if similarity_score >= threshold:
                projects_to_include.append(project)
                
        print(projects_to_include)   
            
        return projects_to_include
        

    @staticmethod
    def function_calculate_project_similarity(data, user_id):
        project_count = (db.session.query(Project).filter(Project.user_id == user_id).count())
        
        if project_count == 0:
            return None
        else:
            try:
                user_projects = CalculateProjectSimilarity.create_tuple_array_of_projects(user_id)
                job_ats_keywords_string = CalculateProjectSimilarity.create_string(data)
                similarity_scores = CalculateProjectSimilarity.calculate_similarity(user_projects, job_ats_keywords_string)
                return similarity_scores
            except Exception as e:
                print(f"An error occurred: {e}")
                return None
    
class CalculateSkillsSimilarity:
    @staticmethod
    def remove_numbers_and_special_characters(data_dict):
        word_pattern = re.compile(r'\b[a-zA-Z]+\b')
        words = word_pattern.findall(data_dict.lower())
    
        return ' '.join(words)
    
    def create_array(data_dict, dic_keys):
        lowercase_dict = {key.lower(): value for key, value in data_dict.items()}
        
        individual_words = []
        joined_keywords = []

        for dic_key in dic_keys:
            job_ats_skills = lowercase_dict.get(dic_key.lower(), [])
            if job_ats_skills:
                for ats_keyword in job_ats_skills:
                    if isinstance(ats_keyword, str):
                        cleaned_keyword = CalculateSkillsSimilarity.remove_numbers_and_special_characters(ats_keyword)
                        words = cleaned_keyword.split()
                        individual_words.extend(words)
                        joined_keywords.append(' '.join(words)) 

        combined_keywords = list(set(joined_keywords + individual_words))
        
        return combined_keywords
    
    @staticmethod
    def create_string_array_of_skills(user_id):
        skills = Skill.query.filter_by(user_id=user_id).all()
        user_skills_from_db = [str(skill.data).lower() for skill in skills]
        
        return user_skills_from_db
    
    @staticmethod
    def find_matching_words(skills_list, ats_keyword_list, threshold=60):
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
        skill_count = (db.session.query(Skill).filter(Skill.user_id == user_id).count())
        
        if skill_count == 0:
            return None
        else:
            ats_keywords = CalculateSkillsSimilarity.create_array(data_dict, dic_key)
            user_skills = CalculateSkillsSimilarity.create_string_array_of_skills(user_id)
            matching_words = CalculateSkillsSimilarity.find_matching_words(user_skills, ats_keywords)
            
            return matching_words
    
class CalculateWorkexpsSimilarity:
    @staticmethod
    def create_string_workexp(input_text):
        tokens = word_tokenize(input_text)
        
        tokens = [word.lower() for word in tokens if word.isalnum()]
        
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]
        
        cleaned_text = ' '.join(tokens)
        result_string = ' '.join(cleaned_text.split())
        
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
                    
                    responsibilities_list.append((workexp.id, cleaned_responsibility))
                    
        return responsibilities_list

    @staticmethod
    def calculate_similarity_workexp(user_workexp_info, job_ats_keywords_string):
        vectorizer = TfidfVectorizer().fit([info[1] for info in user_workexp_info])
        job_vector = vectorizer.transform([job_ats_keywords_string])
        similarity_scores = []

        for id, cleaned_responsibility in user_workexp_info:
            user_vector = vectorizer.transform([cleaned_responsibility])
            similarity_score = cosine_similarity(user_vector, job_vector)
            similarity_scores.append((id, cleaned_responsibility, similarity_score[0][0]))

        return similarity_scores

    @staticmethod
    def calculate_similarity(data_dict, user_id):
        workexp_count = (db.session.query(Workexp).filter(Workexp.user_id == user_id).count())
        
        if workexp_count == 0:
            return None
        else:
            user_workexps = CalculateWorkexpsSimilarity.create_array_of_workexp(user_id)
            ats_keywords = CalculateWorkexpsSimilarity.create_string_workexp(data_dict) 
            matching_workexp = CalculateWorkexpsSimilarity.calculate_similarity_workexp(user_workexps, ats_keywords)
        
            return matching_workexp






    