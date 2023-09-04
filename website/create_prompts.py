from .models import Skill, Project, Workexp

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