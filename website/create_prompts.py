from .models import Skill, Project, Workexp

class FormattingProjectPrompts:
    def threshold_projects_to_include(projects_evaluation, threshold=0.2):
        projects_to_include = []

        for tup in projects_evaluation:
            if isinstance(tup, tuple) and len(tup) == 3:
                if tup[2] >= threshold:
                    projects_to_include.append(tup[0])
        
        return projects_to_include


    def threshold_projects_db_queary(project_ids):
        projects = Project.query.filter(Project.id.in_(project_ids)).all()
        
        return projects
    

    def project_to_str(projects):
        project_strings = []
        
        print(projects)
        
        if isinstance(projects, tuple):
            
            print("my_tuple is a tuple.")
        else:
            print("my_tuple is not a tuple.")

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
        filtered_projects_object = FormattingProjectPrompts.threshold_projects_db_queary(filtered_projects)
        formatted_projects_to_include = FormattingProjectPrompts.project_to_str(filtered_projects_object)
        
        return formatted_projects_to_include
    
class FormattingWorkExpPrompts():
    def threshold_workexp_to_include():
        return Workexp
    
class BuildingCreateCLPrompt:
    @staticmethod
    def combine_input_parameters(project_evaluation_score, job_info, job_advertisement):
        
        if not job_info or not job_advertisement:
            return [] 
        
        system_prompt = "Generate a professional covering letter for the following job application:"
        
        company_name = job_info.get('Company Name', 'Unknown')
        job_title = job_info.get('Position', 'Unknown')
        recruiter = job_info.get('recruiters_name', 'Unknown')

        projects_above_score_threshold = FormattingProjectPrompts.create_projects_prompt(project_evaluation_score)
        
        user_prompt = (
            f"Generate a professional covering letter for the following job application:\n"
            f"- Company: {company_name}\n"
            f"- Position: {job_title}\n"
            f"- Recruiter: {recruiter}\n"
            f"Please use the following information to write the letter and consider the job advertisement below:\n"
            f"```\n"
            f"{job_advertisement}\n"
            f"```\n"
            f"Include the following projects:\n"
            f"{projects_above_score_threshold}\n" 
            f"Additionally, provide project links and any other relevant details.\n"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return messages