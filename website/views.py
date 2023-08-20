from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .api_client import send_api_request
from .models import Note, Skill, OpenAiApiKey
from .prompts import personal_statement_prompt, job_analysis_prompt, job_analysis_compare_skill
from .analyzing_prompts import generate_job_info
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
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
                    
    return render_template("profile.html", user=current_user)

@views.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    if request.method == 'POST':
        if 'create' in request.form:
            job_ad = request.form.get('job_ad')
            selected_notes = request.form.get('selectedNotes')
            word_count = request.form.get('flexRadioDefault')
            
            user_id = current_user.id
            api_key_entry = OpenAiApiKey.query.filter_by(user_id=user_id).first()

            if api_key_entry:
                api_key = api_key_entry.key
                
                messages = job_analysis_prompt(job_ad)
                first_api_response = send_api_request(api_key, messages)

                messages = job_analysis_compare_skill(first_api_response, user_id)
                second_response = send_api_request(api_key, messages)
                
                messages = personal_statement_prompt(second_response, selected_notes, word_count)
                perosnal_statement = send_api_request(api_key, messages)
        
                return render_template('results.html', api_response=first_api_response, second_response=second_response, perosnal_statement=perosnal_statement, user=current_user)
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
            
                return render_template('generate.html', user=current_user, analysisResult=first_api_response)
            else:
                return "API key not found"
    
    return render_template('generate.html', user=current_user)
    
    

@views.route('/results', methods=['GET'])
@login_required
def results():
    api_response = "Sample API Response"
    second_response = "Sample Second Response"
    personal_statement = "Sample Personal Statement"
    
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