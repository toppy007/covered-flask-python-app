from website.create_prompts import threshold_projects_to_include

def test_threshold_projects_to_include():
    input_data = [
        [(2, 'Brolli', 0.16776883802873355), (3, 'Covered', 0.15093333934707948), (4, 'Sentiment Analysis', 0.21527101437610116)]
    ]
    expected_output = [
        (4)
    ]

    result = threshold_projects_to_include(input_data)
    assert result == expected_output