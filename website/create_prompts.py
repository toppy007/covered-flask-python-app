from .models import Skill

def create_matches_prompt(analysis_dict, user_id):
    skills = Skill.query.filter_by(user_id=user_id).all()
    
    system_prompt = "**How suitable am I for this role**\n\n"

    user_skills_prompt = "I have the following skills: "
    for skill in skills:
        user_skills_prompt += f"- {skill.data}\n"
    
    job_ad_skills = analysis_dict.get("Skills", [])
    job_skills_prompt = "The job advertisement requires the following skills:\n"
    for skill in job_ad_skills:
        job_skills_prompt += f"- {skill}\n"

    similarity_prompt = (
        "Please evaluate how well my skills match the skills required for this role. "
        "Consider the skills mentioned above and provide a rating or feedback."
    )

    user_prompt = user_skills_prompt + "\n" + job_skills_prompt + "\n" + similarity_prompt

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return messages
