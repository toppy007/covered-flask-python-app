def personal_statement_prompt(job_advertisement, important_statements, max_word_count):
    system_prompt = "**Personal Statement Prompt**\n\n"
    
    user_prompt = (
        f"Job Advertisement:\n{job_advertisement}\n\n"
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