from .models import Skill
from fuzzywuzzy import fuzz

def create_matches_prompt(analysis_dict, user_id):
    skills = Skill.query.filter_by(user_id=user_id).all()

    job_ad_skills = analysis_dict.get("Technical skills", [])
    
    print("these are my matching skills lists")
    print(job_ad_skills)
    for skill in skills:
        print(skill.data)
    
    matching_skills = []
    for skill in skills:
        for job_skill in job_ad_skills:
            similarity_ratio = fuzz.ratio(skill.data.lower(), job_skill.lower())
            if similarity_ratio >= 50:  # Adjust the threshold as needed
                matching_skills.append(skill.data)
                break  # Move to the next user skill
            
            print(matching_skills)
            

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
