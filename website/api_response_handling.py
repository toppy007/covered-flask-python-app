# these are functions that help format infomation for api promps and respones

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ResponseHandling():
    def is_non_conforming_response(response):
        lines = response.splitlines()
        lines = [line.strip() for line in lines if line.strip()]
        has_sections = any(line.endswith(":") for line in lines)

        return not has_sections or len(lines) <= 1
    
    def formating_response_lower(analysis_dict):
        lowercase_analysis_dict = {key: [skill.lower() for skill in skills] for key, skills in analysis_dict.items()}
        lowercase_dict = {key.lower(): value for key, value in lowercase_analysis_dict.items()}
                
        return lowercase_dict
    
    def calculate_similarity(user_skills, job_skills):
        vectorizer = CountVectorizer().fit_transform([user_skills, job_skills])
        vectors = vectorizer.toarray()
        similarity = cosine_similarity(vectors)
        
        return similarity[0][1]
    
        
    
    