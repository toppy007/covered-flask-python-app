import openai

def send_api_request(user_api_key, messages):
    openai.api_key = user_api_key
    model = 'gpt-3.5-turbo-16k'

    response = openai.ChatCompletion.create(
        model=model, 
        messages=messages, 
        temperature=0.0, 
        top_p=1, 
        frequency_penalty=0, 
        presence_penalty=0
    )

    return response.choices[0].message['content']
