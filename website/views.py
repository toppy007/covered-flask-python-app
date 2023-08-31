from flask import Blueprint, render_template, request, flash, jsonify, session
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .api_client import send_api_request
from .models import Note, Skill, OpenAiApiKey, Project, Workexp
from .create_prompts import formating_response_lower, matching_skills, create_prompt, suitability_checker, create_gpt_prompt, project_match
from .analyzing_prompts import generate_job_info
from .api_response_handling import ResponseHandling
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html", user=current_user)
    
@views.route('/profile_main', methods=['GET', 'POST'])
@login_required
def profile_main():
    
    session.clear()
    
    if request.method == 'POST':
        if 'note' in request.form:
            note = request.form.get('note')
            if len(note) < 1:
                flash('Note is too short!', category='error')
            else:
                new_note = Note(data=note, user_id=current_user.id)
                db.session.add(new_note)
                db.session.commit()
                flash('Note added!', category='success')
        elif 'skill' in request.form:
            skill_list = request.form.get('skill')
            skills = skill_list.split(',')  # Split the comma-separated string into a list

            for skill in skills:
                if len(skill) < 1:
                    flash('Skill is too short!', category='error')
                else:
                    new_skill = Skill(data=skill, user_id=current_user.id)
                    db.session.add(new_skill)
                    db.session.commit()
                    flash('Skill added!', category='success')
        
        elif 'api_key' in request.form:
            key = request.form.get('api_key')
            if len(key) < 1:
                flash('api_key is too short!', category='error')
            else:
                new_api_key = OpenAiApiKey(user_id=current_user.id, key=key)
                db.session.add(new_api_key)
                db.session.commit()
                flash('Api Key Added!', category='success')
                
        elif 'project_title' in request.form:
            project_title = request.form['project_title']
            project_date = f"{request.form['project_date_from_month']}/{request.form['project_date_from_year']} to {request.form['project_date_to_month']}/{request.form['project_date_to_year']}"
            project_link = request.form['project_link']
            project_description = request.form['project_description']
            project_core_skill = request.form['project_core_skill']

            new_project = Project(project_title=project_title, project_date=project_date, project_link=project_link, project_description=project_description, project_core_skill=project_core_skill, user_id=current_user.id)
            
            db.session.add(new_project)
            db.session.commit()

            flash('Project added!', category='success')
            
        elif 'workexp_title' in request.form:
            workexp_title = request.form['workexp_title']
            workexp_dates = request.form['workexp_company']
            workexp_company = f"{request.form['workexp_date_from_month']}/{request.form['workexp_date_from_year']} to {request.form['workexp_date_to_month']}/{request.form['workexp_date_to_year']}"
            
            print(request.form.getlist('string_array'))
            workexp_responsiblities = "\n".join(request.form.getlist('string_array'))

            print(workexp_responsiblities)
            new_workexp = Workexp(workexp_title=workexp_title, workexp_company=workexp_company, workexp_dates=workexp_dates, workexp_responsiblities=workexp_responsiblities, user_id=current_user.id)
            
            db.session.add(new_workexp)
            db.session.commit()

            flash('Project added!', category='success')
    
    return render_template("profile/profile_main.html", user=current_user)

@views.route('/ana_cre_main', methods=['GET', 'POST'])
@login_required
def ana_cre_main():
    pros_cons_dict = {}
    
    if 'sections' not in session:
        session['sections'] = {}  # Initialize 'sections' in session if not present
    sections = session['sections']
    
    if request.method == 'POST':
        if 'create' in request.form:
            user_id = current_user.id
            api_key_entry = OpenAiApiKey.query.filter_by(user_id=user_id).first()

            selected_notes = request.form.get('selectedNotes')
            added_extra = request.form.get('added_extra')
            recruiters_name = request.form.get('project_title')
            word_count = request.form.get('wordcount')

            if api_key_entry:
                
                api_key = api_key_entry.key
                
                data = (session['sections'])
                
                data['Selected Notes'] = [selected_notes]
                data['Added Extra'] = [added_extra]
                data['recruiters_name'] = [recruiters_name]
                data['Word Count'] = [word_count]
                
                formated_response = formating_response_lower(data)
                matches = matching_skills(formated_response, user_id)
                messages = create_prompt(matches, formated_response)
                
                print(formated_response)
                
                create_matches_response = send_api_request(api_key, messages)
                
                suitiblity = suitability_checker(data, user_id)
                suitibility_response = send_api_request(api_key, suitiblity)
                
                projects_match = project_match(suitibility_response, user_id)
                projects_matched = send_api_request(api_key, projects_match)
                
                covering_letter_message = create_gpt_prompt(data, user_id)
                create_covering_letter = send_api_request(api_key, covering_letter_message)
                
                if ResponseHandling.is_non_conforming_response(suitibility_response):
                    error_message = "I'm sorry, but the response from the AI does not conform to the expected format. Please provide a valid job advertisement."
                    return render_template('results.html', user=current_user, skills_matcher=create_matches_response, suitibility_response=suitibility_response, create_covering_letter=create_covering_letter, projects_matched=projects_matched, error_message=error_message)
                else:
                    pros_cons_section = None
                    for line in suitibility_response.splitlines():
                        if line.strip():
                            if ":" in line:
                                if line.endswith(":"):
                                    pros_cons_section = line.strip(":")   
                                    pros_cons_dict[pros_cons_section] = [] 
                                else:
                                    split_result = line.split(":")
                                    pros_cons_dict[split_result[0]] = []
                                    pros_cons_dict[split_result[0]].append(split_result[1])
                            elif pros_cons_section is not None:
                                pros_cons_dict[pros_cons_section].append(line.strip("- "))
                
                print(pros_cons_dict)
                
                session.clear()
                
                return render_template('results.html', pros=pros_cons_dict['Pros'], cons=pros_cons_dict['Cons'], user=current_user, skills_matcher=create_matches_response, create_covering_letter=create_covering_letter, projects_matched=projects_matched)
            else:
                return "API key not found"
            
        elif 'job_ad' in request.form:
            job_ad = request.form.get('job_ad')
            
            user_id = current_user.id
            api_key_entry = OpenAiApiKey.query.filter_by(user_id=user_id).first()
            
            if api_key_entry:
                api_key = api_key_entry.key
                
                messages = generate_job_info(job_ad)
                first_api_response = send_api_request(api_key, messages)
                
                if ResponseHandling.is_non_conforming_response(first_api_response):
                    error_message = "I'm sorry, but the response from the AI does not conform to the expected format. Please provide a valid job advertisement."
                    return render_template('analysis_create/ana_cre_main.html', user=current_user, sections=sections, analysisResult=first_api_response, input_value=job_ad, error_message=error_message)
                else:
                    current_section = None
                    for line in first_api_response.splitlines():
                        if line.strip():
                            if ":" in line:
                                if line.endswith(":"):
                                    current_section = line.strip(":")   
                                    sections[current_section] = [] 
                                else:
                                    split_result = line.split(":")
                                    sections[split_result[0]] = []
                                    sections[split_result[0]].append(split_result[1])
                            elif current_section is not None:
                                sections[current_section].append(line.strip("- "))
                                
                    session['sections'] = sections
                    
                    return render_template('analysis_create/ana_cre_main.html', user=current_user, sections=sections, analysisResult=first_api_response, input_value=job_ad)
            else:
                return "API key not found"
            
    session.clear()
    
    return render_template('analysis_create/ana_cre_main.html', user=current_user, sections=sections)
    
@views.route('/results', methods=['GET'])
@login_required
def results():
    api_response = request.args.get('api_response')
    second_response = request.args.get('second_response')
    personal_statement = request.args.get('personal_statement')
    
    return render_template('results.html', api_response=api_response, second_response=second_response, personal_statement=personal_statement, user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/delete-skill', methods=['POST'])
def delete_skill():  
    skill = json.loads(request.data)
    skillId = skill['skillId']
    skill = Skill.query.get(skillId)
    if skill:
        if skill.user_id == current_user.id:
            db.session.delete(skill)
            db.session.commit()

    return jsonify({})

@views.route('/delete-api_key', methods=['POST'])
def delete_api_key():  
    api_key = json.loads(request.data)
    api_keyId = api_key['api_keyId']
    api_key = OpenAiApiKey.query.get(api_keyId)
    if api_key:
        if api_key.user_id == current_user.id:
            db.session.delete(api_key)
            db.session.commit()

    return jsonify({})

@views.route('/delete-project', methods=['POST'])
def delete_project():  
    project = json.loads(request.data)
    projectId = project['projectId']
    project = Project.query.get(projectId)
    if project:
        if project.user_id == current_user.id:
            db.session.delete(project)
            db.session.commit()

    return jsonify({})

@views.route('/delete-workexp', methods=['POST'])
def delete_workexp():  
    workexp = json.loads(request.data)
    workexpId = workexp['workexpId']
    workexp = Workexp.query.get(workexpId)
    if workexp:
        if workexp.user_id == current_user.id:
            db.session.delete(workexp)
            db.session.commit()

    return jsonify({})