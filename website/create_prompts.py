from .models import Skill
from fuzzywuzzy import fuzz

def get_user_skills(user_id):
    return Skill.query.filter_by(user_id=user_id).all()

def preprocess_analysis_dict(analysis_dict, user_skills):
    lowercase_analysis_dict = {key: [skill.lower() for skill in user_skills] for key, skills in analysis_dict.items()}
    lowercase_dict = {key.lower(): value for key, value in lowercase_analysis_dict.items()}
    return lowercase_dict

def find_matching_skills(user_skills, job_ad_skills, threshold=60):
    matching_skills = []
    
    for user_skill in user_skills:
        user_skill_lower = user_skill.data.lower()
        
        for job_skill in job_ad_skills:
            job_skill_lower = job_skill.lower()
            similarity_ratio = fuzz.ratio(user_skill_lower, job_skill_lower)
            
            if similarity_ratio >= threshold:
                matching_skills.append(user_skill.data)
                break
                
    return matching_skills

def generate_user_prompt(matching_skills, job_ad_skills):
    if matching_skills:
        user_skills_prompt = "My matching technical skills are:\n"
        for skill in matching_skills:
            user_skills_prompt += f"- {skill}\n"
    else:
        user_skills_prompt = "None of my skills match the job's required technical skills."

    job_skills_prompt = "The job advertisement requires the following technical skills:\n"
    for skill in job_ad_skills:
        job_skills_prompt += f"- {skill}\n"

    similarity_prompt = (
        "Please evaluate how well my matching technical skills align with the technical skills "
        "required for this role. Consider the technical skills mentioned above and provide me with a list of the matching skills only."
    )

    user_prompt = user_skills_prompt + "\n" + job_skills_prompt + "\n" + similarity_prompt
    
    return user_prompt

def create_matches_prompt(analysis_dict, user_id):
    user_skills = get_user_skills(user_id)
    
    lowercase_dict = preprocess_analysis_dict(analysis_dict, user_skills)
    job_ad_skills = lowercase_dict.get("technical skills", [])
    
    matching_skills = find_matching_skills(user_skills, job_ad_skills)
    
    system_prompt = "**How suitable am I for this role**\n\n"
    
    user_prompt = generate_user_prompt(matching_skills, job_ad_skills)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    return messages
