from .models import Skill

def generate_job_info(job_advertisement):
    system_prompt = "**Job Information Generation**\n\n"
    
    company_name_question = "What is the company's name?"
    position_question = "What is the position being advertised?"
    keywords_question = "From an ATS analysis perspective, pick out the keywords I should cross-reference."

    user_prompt = (
        f"Given the following job advertisement:\n\n"
        f"```\n"
        f"{job_advertisement}\n"
        f"```\n"
        f"Please provide me with the qualifications, requirements, and technical skills needed for this job."
        f"```\n"
        f"Alos provide me with the following information:\n"
        f"- {company_name_question}\n"
        f"- {position_question}\n"
        f"- {keywords_question}\n"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return messages

