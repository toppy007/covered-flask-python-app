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
        project_strings = (
            f"Generate a formatted representation of the following projects:\n\n"
            + "\n\n".join(
                f"Project Title: {project.project_title}\n"
                f"Project Date: {project.project_date}\n"
                f"Project Link: {project.project_link}\n\n"
                f"Project Description:\n{project.project_description}\n\n"
                f"Core Skills:\n{project.project_core_skill}\n\n"
                for project in projects
            )
        )

        return project_strings
    
    def create_projects_prompt(project_evaluation_score):
        filtered_projects = FormattingProjectPrompts.threshold_projects_to_include(project_evaluation_score, threshold=0.2)
        print(filtered_projects)
        filtered_projects_object = FormattingProjectPrompts.theshold_projects_db_queary(filtered_projects)
        formatted_projects_to_include = FormattingProjectPrompts.project_to_str(filtered_projects_object)
        
        print('formatted projects')
        print(formatted_projects_to_include)
        return formatted_projects_to_include
    
class FormattingWorkExpPrompts():
    def threshold_workexp_to_include():
        return Workexp
    
class BuildingCreateCLPrompt:
    def combine_input_parameters(project_evaluation_score, job_info, job_advertisement):
        if not job_info or not job_advertisement:
            return [] 
        
        system_prompt = "Generate a professional covering letter for the following job application:"
        
        company_name = job_info.get('Company Name', 'Unknown')
        job_title = job_info.get('Position', 'Unknown')
        recruiter = job_info.get('recruiters_name', 'Unknown')
        
        user_prompt = (
            f"Generate a professional covering letter for the following job application:\n"
            f"- Company: {company_name}\n"
            f"- Position: {job_title}\n"
            f"- Recruiter: {recruiter}\n"
            f"- Project Evaluation Score: {project_evaluation_score}\n"
            f"Please use the following information to write the letter and consider the job advertisement below:\n"
            f"```\n"
            f"{job_advertisement}\n"
            f"```\n"
            f"Include the following projects:\n"
            f"{FormattingProjectPrompts.project_to_str(projects_to_include)}\n"  # Include the projects here
            f"Additionally, provide project links and any other relevant details.\n"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return messages
