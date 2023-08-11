from unittest.mock import patch
from website.api_client import send_api_request

# Mock the openai module and its dependencies
@patch('website.api_client.openai.ChatCompletion.create')
def test_send_api_request(mock_openai):
    
    # Mock the response from OpenAI API
    mock_openai.return_value.choices = [
        type('MockMessage', (object,), {'message': {'content': 'Test response'}})()
    ]

    user_api_key = 'your_api_key'
    messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}]

    result = send_api_request(user_api_key, messages)

    assert result == 'Test response'
    mock_openai.assert_called_once_with(
        model='gpt-3.5-turbo-0301',
        messages=messages,
        temperature=0.3,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )