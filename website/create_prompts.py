from .models import Skill, Project, Workexp

class FormattingProjectPrompts:
    def threshold_projects_to_include(projects_evaluation, threshold=0.2):
        projects_to_include = []

        for tup in projects_evaluation:
            if isinstance(tup, tuple) and len(tup) == 3:
                if tup[2] >= threshold:
                    projects_to_include.append(tup[0])

        return projects_to_include


    def theshold_projects_db_queary(project_ids):
        projects = Project.query.filter(Project.id.in_(project_ids)).all()
        
        print('project objects')
        print(projects)
        return projects

    def project_to_str(projects):
        project_strings = []

        for project in projects:
            project_str = f"Project Title: {project.project_title}\n"
            project_str += f"Project Date: {project.project_date}\n"
            project_str += f"you must include this link in the covering letter Project Link: {project.project_link}\n\n"
            project_str += f"Project Description:\n{project.project_description}\n\n"
            project_str += f"Core Skills:\n{project.project_core_skill}\n"

            project_strings.append(project_str)

        return "\n".join(project_strings)
    
    def create_projects_prompt(project_evaluation_score):
        filtered_projects = FormattingProjectPrompts.threshold_projects_to_include(project_evaluation_score, threshold=0.2)
        print(filtered_projects)
        filtered_projects_object = FormattingProjectPrompts.theshold_projects_db_queary(filtered_projects)
        formatted_projects_to_include = FormattingProjectPrompts.project_to_str(filtered_projects_object)
        
        print('formatted projects')
        print(formatted_projects_to_include)
        return formatted_projects_to_include
    
class BuildingCreateCLPrompt:
    @staticmethod
    def combine_input_parameters(project_evaluation_score, job_info, job_advertisement):
       
        """
        Combine input parameters to generate system and user prompts for creating a covering letter.

        Args:
            project_evaluation_score (float): The score for the project evaluation.
            job_info (dict): Dictionary containing job-related information.
            job_advertisement (str): The job advertisement text.

        Returns:
            list: A list of messages containing system and user prompts.
        """
        
        system_prompt = "Generate a professional covering letter for the following job application:"
        
        company_name = job_info.get('Company Name', [None])[0]
        job_title = job_info.get('Position', [None])[0]
        recruiter = job_info.get('recruiters_name', [None])[0]
        
        company_name_info = f"The company I am applying to is {company_name}"
        job_title_info = f"The position I am applying for is {job_title}"
        recruiter_info = f"You should address the covering letter to {recruiter}"
        print("project evaluation score")
        print(project_evaluation_score)
        projects_to_include = FormattingProjectPrompts.create_projects_prompt(project_evaluation_score)

        user_prompt = (
            f"Given the following job advertisement:\n\n"
            f"```\n"
            f"{job_advertisement}\n"
            f"```\n"
            f"Please use the following information to create a covering letter:\n"
            f"- {company_name_info}\n"
            f"- {recruiter_info}\n"
            f"- {job_title_info}\n"
            f"Include the following projects:\n"
            f"{projects_to_include}\n"
            f"also include the project link:\n"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return messages
