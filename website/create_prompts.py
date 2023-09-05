from .models import Skill, Project, Workexp

class FormattingProjectPrompts:
    def threshold_projects_to_include(projects_evaluation, threshold=0.2):
        projects_to_include = []

        for project_evaluation in projects_evaluation:
            for tup in project_evaluation:
                if tup[2] >= threshold:
                    projects_to_include.append(tup[0])

        return projects_to_include

    def theshold_projects_db_queary(project_ids):
        projects = Project.query.filter(Project.id.in_(project_ids)).all()
        
        return projects

    def project_to_str(projects):
        project_strings = []

        for project in projects:
            project_str = f"Project Title: {project.project_title}\n"
            project_str += f"Project Date: {project.project_date}\n"
            project_str += f"Project Link: {project.project_link}\n\n"
            project_str += f"Project Description:\n{project.project_description}\n\n"
            project_str += f"Core Skills:\n{project.project_core_skill}\n"

            project_strings.append(project_str)

        return "\n".join(project_strings)
    
    def create_projects_prompt(project_evaluation_score):
        filtered_projects = FormattingProjectPrompts.threshold_projects_to_include(project_evaluation_score)
        filtered_projects_object = FormattingProjectPrompts.theshold_projects_db_queary(filtered_projects)
        formatted_projects_to_include = FormattingProjectPrompts.project_to_str():
        
        return 