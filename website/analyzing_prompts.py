from .models import Skill

def generate_job_info(job_advertisement):
    system_prompt = "**Job Information Generation**\n\n"
    
    user_prompt = (
        f"Given the following job advertisement:\n\n"
        f"```\n"
        f"{job_advertisement}\n"
        f"```\n"
        f"Please provide me with the qualifications, requirements, and skills needed for this job."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return messages

