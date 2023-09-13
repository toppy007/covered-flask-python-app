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
    def threshold_workexp_to_include(workexps_evaluation, threshold=0.2):
        workexp_to_include = [] 

        for tup in workexps_evaluation:
            if isinstance(tup, tuple) and len(tup) == 3:
                if tup[2] >= threshold:
                    workexp_to_include.append(tup)

        return (workexp_to_include)
    
    def threshold_workexp_db_queary(workexps_to_include):
        modified_tuples = []

        for workexp in workexps_to_include:
            workexp_id = workexp[0]
            workexps = Workexp.query.filter(Workexp.id == workexp_id).first()  # Assuming there's only one result per ID
            
            if workexps:
                modified_tuple = (workexp[0], workexp[1], workexp[2], workexps.workexp_title, workexps.workexp_dates)
                modified_tuples.append(modified_tuple)
        
        return modified_tuples
    
    def workexp_to_str(workexps):
        workexp_strings = []
        
        for workexp in workexps:
            workexp_str = f"this was my job title where i gained the experience: {workexp[3]}\n"
            workexp_str += f"this was the company I was working for to gain the experience: {workexp[4]}\n"
            workexp_str += f"this is the experience id like to include in the covering letter: {workexp[1]}\n\n"

            workexp_strings.append(workexp_str)

        return "\n".join(workexp_strings)
    
    def create_workexp_prompt(workexp_evaluation_score):
        filtered_workexp = FormattingWorkExpPrompts.threshold_workexp_to_include(workexp_evaluation_score, threshold=0.2)
        filtered_workexp_object = FormattingWorkExpPrompts.threshold_workexp_db_queary(filtered_workexp)
        formatted_workexp_to_include = FormattingWorkExpPrompts.workexp_to_str(filtered_workexp_object)
        
        return formatted_workexp_to_include
    
class BuildingCreateCLPrompt:
    @staticmethod
    def combine_input_parameters(project_evaluation_score, workexp_evaluation_score, skills_match, job_info, job_advertisement):
        
        if not job_info or not job_advertisement:
            return [] 
        
        print('job info')
        print(job_info)
        
        system_prompt = "Generate a professional covering letter for the following job application:"
        
        company_name = job_info.get('Company Name', 'Unknown')
        job_title = job_info.get('Position', 'Unknown')
        recruiter = job_info.get('recruiters_name', 'Unknown')
        selected_notes = job_info.get('Selected Notes', 'Unknown')
        extra_notes = job_info.get('Added Extra', 'Unknown')
        word_count = job_info.get('Word Count', 'Unknown')

        projects_above_score_threshold = FormattingProjectPrompts.create_projects_prompt(project_evaluation_score)
        workexps_above_score_threshold = FormattingWorkExpPrompts.create_workexp_prompt(workexp_evaluation_score)
        
        user_prompt = (
            "Please generate a professional covering letter for the following job application:\n\n"
            f"Company: {company_name}\n"
            f"Position: {job_title}\n"
            f"Recruiter: {recruiter}\n\n"
            "Job Advertisement:\n"
            "```\n"
            f"{job_advertisement}\n"
            "```\n\n"
            "In your letter, please incorporate the following key points and consider the job advertisement provided:\n\n"
            f"Mention these passages from the job advertisement:\n"
            f"{selected_notes}\n\n"
            "Additionally, add these extra notes:\n"
            f"{extra_notes}\n\n"
            "Highlight the following core skills:\n"
            f"{skills_match}\n\n"
            "Include the following projects, providing project links and relevant details for each:\n"
            f"{projects_above_score_threshold}\n\n"
            "Include the following work experience:\n"
            f"{workexps_above_score_threshold}\n\n"
            f"Please ensure the letter's word count does not exceed {word_count}.\n"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return messages