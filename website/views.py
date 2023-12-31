from flask import Blueprint, render_template, request, flash, jsonify, session, redirect, url_for
from flask_login import login_required, current_user
from flask_mail import Mail, Message
from datetime import datetime
from .api_client import send_api_request
from .models import Note, Skill, OpenAiApiKey, Project, Workexp, JobHistoryData
from .analyzing_prompts import generate_job_info
from .api_response_handling import ResponseHandling
from .create_prompts import BuildingCreateCLPrompt
from .npl import CalculateSkillsSimilarity, CalculateProjectSimilarity, CalculateWorkexpsSimilarity
from collections import Counter
from . import db
from . import mail
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
            skills = skill_list.split(',')

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
                flash('API Key added!', category='success')
                
        elif 'project_title' in request.form:
            project_title = request.form['project_title']
            project_date = f"{request.form['project_date_from_month']}/{request.form['project_date_from_year']} to {request.form['project_date_to_month']}/{request.form['project_date_to_year']}"
            project_link = request.form['project_link']
            project_description = request.form['project_description']
            project_core_skill = request.form['project_core_skill']
            if len(project_title) < 1 or len(project_date) < 1 or len(project_link) < 1 or len(project_description) < 1 or len(project_core_skill) < 1:
                flash('All fields must be entered!', category='error')
            else:
                new_project = Project(project_title=project_title, project_date=project_date, project_link=project_link, project_description=project_description, project_core_skill=project_core_skill, user_id=current_user.id)
            
                db.session.add(new_project)
                db.session.commit()

                flash('Project added!', category='success')
            
        elif 'workexp_title' in request.form:
            workexp_title = request.form['workexp_title']
            workexp_dates = request.form['workexp_company']
            workexp_company = f"{request.form['workexp_date_from_month']}/{request.form['workexp_date_from_year']} to {request.form['workexp_date_to_month']}/{request.form['workexp_date_to_year']}"
            workexp_responsiblities = "\n".join(request.form.getlist('string_array'))
            
            if  len(workexp_title) < 1 or len(workexp_dates) < 1 or len(workexp_company) < 1 or len(workexp_responsiblities) < 1:
                flash('All fields must be entered!', category='error')
            else:
                new_workexp = Workexp(workexp_title=workexp_title, workexp_company=workexp_company, workexp_dates=workexp_dates, workexp_responsiblities=workexp_responsiblities, user_id=current_user.id)
                
                db.session.add(new_workexp)
                db.session.commit()

                flash('Project added!', category='success')
    
    return render_template("profile/profile_main.html", user=current_user)

@views.route('/ana_cre_main', methods=['GET', 'POST'])
@login_required
def ana_cre_main(): 
    if 'sections' not in session:
        session['sections'] = {}
    sections = session['sections']
    
    if request.method == 'POST':
        if 'create' in request.form:
            
            user_id = current_user.id
            project_count = (db.session.query(Project).filter(Project.user_id == user_id).count())
            workexp_count = (db.session.query(Workexp).filter(Workexp.user_id == user_id).count())
            skills_count = (db.session.query(Skill).filter(Skill.user_id == user_id).count())

            if project_count == 0 or workexp_count == 0 or skills_count == 0:
                flash('For chatgpt to create a covering letter you must complete your profile.', category='error')
                return render_template('profile/profile_main.html', user=current_user)
            
            else:
                api_key_entry = OpenAiApiKey.query.filter_by(user_id=user_id).first()

                selected_notes = request.form.get('selectedNotes')
                added_extra = request.form.get('added_extra')
                recruiters_name = request.form.get('project_title')
                word_count = request.form.get('wordcount')
                threshold_workexp = request.form.get('workexpthreshold')
                threshold_project = request.form.get('projectthreshold')
                
                threshold_project_float = float(threshold_project)
                threshold_workexp_float = float(threshold_workexp)

                if api_key_entry:
                    
                    api_key = api_key_entry.key
                    
                    session['recruiters_name'] = recruiters_name
                    session['threshold_workexp'] = threshold_workexp
                    session['threshold_project'] = threshold_project
                    
                    data = (session['sections'])
                    raw_data = (session['job_ad'])
                    
                    data['Selected Notes'] = [selected_notes]
                    data['Added Extra'] = [added_extra]
                    data['recruiters_name'] = [recruiters_name]
                    data['Word Count'] = [word_count]
                    
                    dic_key = ["keywords for ats analysis", "ats keywords"]

                    skills_match = CalculateSkillsSimilarity.calculate_similarity(data, dic_key, user_id)
                    project_match = CalculateProjectSimilarity.function_calculate_project_similarity(raw_data, user_id)
                    workexp_match = CalculateWorkexpsSimilarity.calculate_similarity(raw_data, user_id)
                    
                    covering_letter_message = BuildingCreateCLPrompt.combine_input_parameters(project_match, workexp_match, skills_match, data, raw_data, threshold_project_float, threshold_workexp_float)
                    covering_letter = send_api_request(api_key, covering_letter_message)
                    
                    print(covering_letter)
                    
                    session['covering_letter'] = covering_letter
                    
                    return redirect(url_for('views.results'))
                else:
                    return "API key not found"
            
        elif 'job_ad' in request.form:
            
            session.clear()
            
            api_count = db.session.query(OpenAiApiKey).count()
            
            if api_count == 0:
                flash('No API key exists! Please add an OpenAi API key.', category='error')
                return render_template('profile/profile_main.html', user=current_user)
            
            else:
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
                        session['job_ad'] = job_ad
                        
                        dic_key = ["keywords for ats analysis", "ats keywords"]

                        skills_match = CalculateSkillsSimilarity.calculate_similarity(sections, dic_key, user_id)
                        project_match = CalculateProjectSimilarity.function_calculate_project_similarity(job_ad, user_id)
                        workexp_match = CalculateWorkexpsSimilarity.calculate_similarity(job_ad, user_id)
                        
                        return render_template('analysis_create/ana_cre_main.html', user=current_user, sections=sections, analysisResult=first_api_response, input_value=job_ad)
    
    session.clear()
    return render_template('analysis_create/ana_cre_main.html', user=current_user, sections=sections)
    
@views.route('/results', methods=['GET', 'POST'])
@login_required
def results():
    if request.method == 'POST':
        
        covering_letter = session.get('covering_letter')
        job_ad = session.get('job_ad')
        
        position = session.get('sections', {}).get('Position', '') 
        recruiters_name = session.get('recruiters_name')
        company_name = session.get('sections', {}).get('Company Name')
        
        possible_keys = ['Keywords for ATS analysis', 'ATS Analysis']

        ats_keyword = None

        for key in possible_keys:
            try:
                ats_keyword = session['sections'][key]
                break
            except KeyError:
                continue
            
        technical_skills = session.get('sections', {}).get('Technical Skills')
        requirements = session.get('sections', {}).get('Requirements')
        qualifications = session.get('sections', {}).get('Qualifications')
        
        combined_data = f"Technical Skills: {technical_skills}\nRequirements: {requirements}\nQualifications: {qualifications}\nRequirements: {requirements}\nATS keyword: {ats_keyword}"
        
        company_name = ','.join(company_name)
        position = ','.join(position)
        
        try:
            technical_skills = ','.join(technical_skills)
            ats_keyword = ','.join(ats_keyword)
        except Exception as e:
            # Handle the exception here, you can print or log the error message
            print(f"An error occurred while joining lists: {e}")
            technical_skills = None
            ats_keyword = None
        
        new_job_history_data = JobHistoryData(
            sessions_data=combined_data,
            covering_letter=covering_letter,
            job_ad=job_ad,
            recruiters_name=recruiters_name,
            company_name=company_name,
            ats_keywords=ats_keyword,
            position=position,
            technical_skills=technical_skills,
            user_id=current_user.id
        )
        
        db.session.add(new_job_history_data)
        db.session.commit()

        return redirect(url_for('views.history'))
    
    covering_letter = session.get('covering_letter')

    return render_template('results.html', user=current_user, covering_letter=covering_letter)

@views.route('/history', methods=['GET'])
@login_required
def history():

    job_history_data = JobHistoryData.query.filter_by(user_id=current_user.id).all()
    
    for history_entry in job_history_data:
        sessions_data = history_entry.sessions_data
        lines = sessions_data.split('\n')
        result_dict = {}

        for line in lines:
            parts = line.split(': ')

            if len(parts) == 2:
                key = parts[0].strip()
                value_str = parts[1].strip()

                if value_str.startswith('[') and value_str.endswith(']'):
                    value = [item.strip("' ") for item in value_str[1:-1].split(',')]
                else:
                    value = value_str

                result_dict[key] = value

        timestamp_data = history_entry.timestamp
        formatted_date = timestamp_data.strftime("%Y-%m-%d")
        
        history_entry.result_dict = result_dict
        history_entry.formatted_date = formatted_date

    return render_template('history/history_main.html', user=current_user, job_history_data=job_history_data)

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

@views.route('/get-doughnut-core-skills-data')
def get_doughnut_core_skills_data():
    user_id = current_user.id
    skills_count = (db.session.query(Skill).filter(Skill.user_id == user_id).count())
    
    if skills_count == 0:
        print("no data Avalible")
        return jsonify(None)
    else:
        dic_key = ["technical skills", "technical skills keywords"]

        skills_data = CalculateSkillsSimilarity.calculate_similarity(session['sections'], dic_key, user_id)
        tech_skills = CalculateSkillsSimilarity.create_array(session['sections'], dic_key)
        
        length_skills = len(skills_data)
        length_tech_skills = len(tech_skills)
        missing_tech_skills = (length_tech_skills - length_skills) 
        percentage = (100//length_tech_skills) * length_skills

        data = {
            'Matched': length_skills,
            'No Match': missing_tech_skills,
            'percentage': percentage
        }
        
        return jsonify(data)

@views.route('/get-bar-project-score-data')
def get_bar_project_score_data():

    user_id = current_user.id
    project_count = (db.session.query(Project).filter(Project.user_id == user_id).count())
    if project_count == 0:
        print("no data avalible")
        return jsonify(None)
    else:
        project_match = CalculateProjectSimilarity.function_calculate_project_similarity(session['job_ad'], user_id)
        project_match_with_threshold = [(project[0], project[1], project[2], 0.2) for project in project_match]
        
        return jsonify(project_match_with_threshold)

@views.route('/get-bar-workexp-score-data')
def get_bar_workexp_score_data():

    user_id = current_user.id
    workexp_count = (db.session.query(Workexp).filter(Workexp.user_id == user_id).count())
    if workexp_count == 0:
        print("no data avalible")
        return jsonify(None)
    else:   
        workexp_match = CalculateWorkexpsSimilarity.calculate_similarity(session['job_ad'], user_id)
        workexp_match_with_threshold = [(workexp[0], workexp[1][:25] + '...' if len(workexp[1]) > 25 else workexp[1], workexp[2], 0.2) for workexp in workexp_match]

        return jsonify(workexp_match_with_threshold)

@views.route('/delete-application', methods=['POST'])
def delete_application():
    jobHistory = json.loads(request.data)
    historyId = jobHistory['historyId']

    jobHistoryinfo = JobHistoryData.query.get(historyId)

    if jobHistoryinfo:
        if jobHistoryinfo.user_id == current_user.id:
            db.session.delete(jobHistoryinfo)
            db.session.commit()

    return jsonify({})

@views.route('/submit_form', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        email = request.form.get('email')

        subject = 'Join the Covered project'
        sender = 'your_email@example.com'
        recipients = [email]
        message_body = '''
            Dear Emailer,

            Thank you for your interest in joining our project. Your enthusiasm is greatly appreciated. 
            
            To learn more, please visit our GitHub repository here: https://github.com/toppy007/covered-flask-python-app. 
            
            Explore ongoing tasks, ask questions, and collaborate with our team. Your contributions are invaluable, and we're excited about the potential impact. 
            If you have any queries or need assistance, feel free to reach out. We look forward to working together to achieve our shared goals.
            
            Best regards
            
            Christopher Topplisek'''

        message = Message(subject, sender=sender, recipients=recipients)
        message.body = message_body

        try:
            mail.send(message)
            flash('Email sent to recipient', category='success')

        except Exception as e:
            return f"An error occurred: {str(e)}"

    return '', 204

@views.route('/update-covering-letter', methods=['POST'])
def save_edited_cl():
    save_edit = json.loads(request.data)
    new_covering_letter = save_edit.get('covering_letter')

    session['covering_letter'] = new_covering_letter
    
    return jsonify({})

@views.route('/true-contacted', methods=['POST'])
def true_contacted():
    jobHistory = json.loads(request.data)
    historyId = jobHistory['historyId']
    contactedState = jobHistory.get('contactedState', False)

    jobHistoryinfo = JobHistoryData.query.get(historyId)

    if jobHistoryinfo:
        if jobHistoryinfo.user_id == current_user.id:
            jobHistoryinfo.contact_viewed = contactedState
            db.session.commit()

    return jsonify({})

@views.route('/true-tech', methods=['POST'])
def true_tech():
    jobHistory = json.loads(request.data)
    historyId = jobHistory['historyId']
    contactedState = jobHistory.get('contactedState', False) 

    jobHistoryinfo = JobHistoryData.query.get(historyId)

    if jobHistoryinfo:
        if jobHistoryinfo.user_id == current_user.id:
            jobHistoryinfo.tech_interview = contactedState 
            db.session.commit()

    return jsonify({})

@views.route('/true-interviewed', methods=['POST'])
def true_interview():
    jobHistory = json.loads(request.data)
    historyId = jobHistory['historyId']
    contactedState = jobHistory.get('contactedState', False)  # Get the contactedState value, default to False

    jobHistoryinfo = JobHistoryData.query.get(historyId)

    if jobHistoryinfo:
        if jobHistoryinfo.user_id == current_user.id:
            jobHistoryinfo.interview = contactedState  # Set interview to the value of contactedState
            db.session.commit()

    return jsonify({})

@views.route('/true-rejected', methods=['POST'])
def true_rejected():
    jobHistory = json.loads(request.data)
    historyId = jobHistory['historyId']
    contactedState = jobHistory.get('contactedState', False)  

    jobHistoryinfo = JobHistoryData.query.get(historyId)

    if jobHistoryinfo:
        if jobHistoryinfo.user_id == current_user.id:
            jobHistoryinfo.rejested = contactedState  
            db.session.commit()

    return jsonify({})

@views.route('/get-contacted-state/<int:historyId>', methods=['GET'])
def get_contacted_state(historyId):
    jobHistoryinfo = JobHistoryData.query.get(historyId)

    if jobHistoryinfo:
        if jobHistoryinfo.user_id == current_user.id:
            return jsonify({'contactedState': jobHistoryinfo.contact_viewed})

@views.route('/get-interviewed-state/<int:historyId>', methods=['GET'])
def get_tech_state(historyId):
    jobHistoryinfo = JobHistoryData.query.get(historyId)

    if jobHistoryinfo:
        if jobHistoryinfo.user_id == current_user.id:
            return jsonify({'contactedState': jobHistoryinfo.interview})

@views.route('/get-tech-state/<int:historyId>', methods=['GET'])
def get_interview_state(historyId):
    jobHistoryinfo = JobHistoryData.query.get(historyId)

    if jobHistoryinfo:
        if jobHistoryinfo.user_id == current_user.id:
            return jsonify({'contactedState': jobHistoryinfo.tech_interview})

@views.route('/get-rejected-state/<int:historyId>', methods=['GET'])
def get_rejected_state(historyId):
    jobHistoryinfo = JobHistoryData.query.get(historyId)

    if jobHistoryinfo:
        if jobHistoryinfo.user_id == current_user.id:
            return jsonify({'contactedState': jobHistoryinfo.rejested})

@views.route('/get-line-jobapplication-submit-date-data', methods=['GET'])
def get_submit_date_data():
    user_id = current_user.id
    job_history_records = JobHistoryData.query.filter_by(user_id=user_id).all()
    
    formatted_date_data = []

    for record in job_history_records:
        formatted_date = record.timestamp.strftime("%Y-%m-%d")
        formatted_date_data.append(formatted_date)

    date_counts = Counter(formatted_date_data)
    
    print({'formattedDates': formatted_date_data, 'dateCounts': date_counts})

    return jsonify({'formattedDates': formatted_date_data, 'dateCounts': date_counts})