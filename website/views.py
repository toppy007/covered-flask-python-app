from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .api_client import send_api_request
from .models import Note, Skill, OpenAiApiKey, Project
from .create_prompts import create_matches_prompt
from .analyzing_prompts import generate_job_info
from .api_response_handling import ResponseHandling
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html", user=current_user)
    
@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
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
    
    return render_template("profile.html", user=current_user)

@views.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    sections = {}
    if request.method == 'POST':
        if 'create' in request.form:
            user_id = current_user.id
            api_key_entry = OpenAiApiKey.query.filter_by(user_id=user_id).first()

            if api_key_entry:
                api_key = api_key_entry.key
                
                messages = create_matches_prompt(sections, user_id)
                create_matches_response = send_api_request(api_key, messages)
                
                print(create_matches_response)
        
                return render_template('results.html', user=current_user, skills_matcher=create_matches_response)
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
                
                print(first_api_response)
                
                current_section = None
                
                if ResponseHandling.is_non_conforming_response(first_api_response):
                    error_message = "I'm sorry, but the response from the AI does not conform to the expected format. Please provide a valid job advertisement."
                    return render_template('generate.html', user=current_user, sections=sections, analysisResult=first_api_response, input_value=job_ad, error_message=error_message)
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
                                
                    print(sections)
                    
                    return render_template('generate.html', user=current_user, sections=sections, analysisResult=first_api_response, input_value=job_ad)
            else:
                return "API key not found"
    
    return render_template('generate.html', user=current_user, sections=sections)
    
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