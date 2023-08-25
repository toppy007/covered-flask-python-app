from .models import Skill
from fuzzywuzzy import fuzz

def formating_response_lower(analysis_dict):
    lowercase_analysis_dict = {key: [skill.lower() for skill in skills] for key, skills in analysis_dict.items()}
    lowercase_dict = {key.lower(): value for key, value in lowercase_analysis_dict.items()}

    job_ad_skills = lowercase_dict.get("keywords for ats analysis", [])
    
    return job_ad_skills
    
def matching_skills(job_ad_skills, user_id):
    skills = Skill.query.filter_by(user_id=user_id).all()
    
    matching_skills = []
    threshold = 70  # Adjust the threshold as needed

    for skill in skills:
        user_skill_lower = skill.data.lower()
        
        for job_skill in job_ad_skills:
            job_skill_lower = job_skill.lower()
            similarity_ratio = fuzz.ratio(user_skill_lower, job_skill_lower)
            
            if similarity_ratio >= threshold:
                matching_skills.append(skill.data)
                break 
    
    return matching_skills

def create_prompt(job_ad_skills, matching_skills):
    system_prompt = "**How suitable am I for this role**\n\n"

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

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return messages
