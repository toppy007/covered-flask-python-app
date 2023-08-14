from .models import Skill

def personal_statement_prompt(job_advertisement, important_statements, max_word_count):
    system_prompt = "**Personal Statement Prompt**\n\n"
    
    user_prompt = (
        f"Job Advertisement Key Techinical Skills Required:\n{job_advertisement}\n\n"
        f"Important Statements to Include:\n{important_statements}\n\n"
        f"Max Word Count: {max_word_count}\n\n"
        f"Write a personal statement that addresses the job requirements mentioned in the advertisement and avoid's flowery language."
        f"Include the important statements provided and ensure that the statement does not exceed {max_word_count} words."
        f"ensure the statements word count does not exceed {max_word_count} words."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return messages

def job_analysis_prompt(job_advertisement):
    system_prompt = "**Job Analysis Prompt**\n\n"
    
    user_prompt = (
        f"Job Advertisement:\n{job_advertisement}\n\n"
        "Based on the job description, please provide comma-separated lists of:\n\n"
        "- Technical Skills\n"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return messages

def job_analysis_compare_skill(job_ad_keywords, user_id):
    user_skills = Skill.query.filter_by(user_id=user_id).all()
    
    user_skills_list = ", ".join(skill.data for skill in user_skills)
    
    prompt = (
        f"Job Advertisement Keywords: {job_ad_keywords}\n\n"
        f"User Skills: {user_skills_list}\n\n"
        "Compare the user's technical skills with the job advertisement keywords and provide a list of technical matching skills.\n"
        "Only include skills that match exactly between the two lists, provided as a comma-separated list.\n\n"
        "Matching Skills: "
        )

    messages = [
            {"role": "system", "content": "**Job Analysis Prompt**"},
            {"role": "user", "content": prompt}
        ]

    return messages
        