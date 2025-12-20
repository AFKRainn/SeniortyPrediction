import json
import random
import pandas as pd
from collections import defaultdict
random.seed(42)

LEVEL_MAPPING = {
    'junior': 'junior',
    'intern': 'junior',
    'entry': 'junior',
    'entry-level': 'junior',
    'mid': 'mid',
    'mid-level': 'mid',
    'senior': 'senior',
    'mid-senior': 'senior',
    'manager': 'senior',
    'professional': 'senior',
}

IGNORE_VALUES = {'', 'Unknown', 'Not Provided',
                 'unknown', 'not provided', None, 'N/A', 'n/a'}


def is_valid(value):
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() not in IGNORE_VALUES
    return True


def safe_get(value):
    if is_valid(value):
        return value
    return ''


def join_list(lst, separator=', '):
    if not lst:
        return ''
    valid_items = [str(item) for item in lst if is_valid(item)]
    return separator.join(valid_items)


def extract_skills_with_levels(skill_list):
    if not skill_list:
        return ''
    skills = []
    for skill in skill_list:
        if isinstance(skill, dict):
            name = skill.get('name', '')
            level = skill.get('level', '')
            if is_valid(name):
                if is_valid(level):
                    skills.append(f"{name} ({level})")
                else:
                    skills.append(name)
    return ', '.join(skills)


def calculate_job_period(start_date, end_date):
    start_valid = is_valid(start_date)
    end_valid = is_valid(end_date)
    if start_valid and end_valid:
        return f"{start_date} - {end_date}"
    elif start_valid and not end_valid:
        return f"{start_date} - Present"
    else:
        return "Unknown"


def get_summary_category(word_count):
    if word_count < 20:
        return "short"
    elif word_count < 25:
        return "medium"
    else:
        return "large"


def flatten_record(record):
    flat = {}
    personal_info = record.get('personal_info', {})
    flat['name'] = safe_get(personal_info.get('name', ''))
    flat['email'] = safe_get(personal_info.get('email', ''))
    location = personal_info.get('location', {})
    flat['remote_preference'] = safe_get(location.get('remote_preference', ''))
    flat['summary'] = safe_get(personal_info.get('summary', ''))
    flat['linkedin'] = safe_get(personal_info.get('linkedin', ''))
    flat['github'] = safe_get(personal_info.get('github', ''))
    summary = personal_info.get('summary', '')
    if is_valid(summary):
        word_count = len(summary.split())
        flat['summary_word_count'] = word_count
        flat['summary_length_category'] = get_summary_category(word_count)
    else:
        flat['summary_word_count'] = 0
        flat['summary_length_category'] = 'none'
    experiences = record.get('experience', [])
    if experiences:
        exp = experiences[0]
        flat['job_title'] = safe_get(exp.get('title', ''))
        flat['company'] = safe_get(exp.get('company', ''))
        flat['employment_type'] = safe_get(exp.get('employment_type', ''))
        company_info = exp.get('company_info', {})
        flat['company_industry'] = safe_get(company_info.get('industry', ''))
        flat['company_size'] = safe_get(company_info.get('size', ''))
        dates = exp.get('dates', {})
        start_date = safe_get(dates.get('start', ''))
        end_date = safe_get(dates.get('end', ''))
        flat['job_duration'] = safe_get(dates.get('duration', ''))
        flat['job_period'] = calculate_job_period(start_date, end_date)
        flat['responsibilities'] = join_list(
            exp.get('responsibilities', []), ' | ')
        tech_env = exp.get('technical_environment', {})
        flat['technologies'] = join_list(tech_env.get('technologies', []))
        flat['methodologies'] = join_list(tech_env.get('methodologies', []))
        flat['tools'] = join_list(tech_env.get('tools', []))
    else:
        flat['job_title'] = ''
        flat['company'] = ''
        flat['employment_type'] = ''
        flat['company_industry'] = ''
        flat['company_size'] = ''
        flat['job_duration'] = ''
        flat['job_period'] = 'Unknown'
        flat['responsibilities'] = ''
        flat['technologies'] = ''
        flat['methodologies'] = ''
        flat['tools'] = ''
    all_titles = []
    all_companies = []
    for exp in experiences:
        title = exp.get('title', '')
        if is_valid(title):
            all_titles.append(title)
        company = exp.get('company', '')
        if is_valid(company):
            all_companies.append(company)
    flat['all_job_titles'] = join_list(all_titles)
    flat['all_companies'] = join_list(all_companies)
    flat['num_experiences'] = len(experiences)
    education = record.get('education', [])
    all_degrees = []
    all_fields = []
    all_institutions = []
    all_honors = []
    for edu in education:
        degree = edu.get('degree', {})
        level = degree.get('level', '')
        field = degree.get('field', '')
        major = degree.get('major', '')
        if is_valid(level):
            all_degrees.append(level)
        if is_valid(field):
            all_fields.append(field)
        if is_valid(major) and major != field:
            all_fields.append(major)
        institution = edu.get('institution', {})
        inst_name = institution.get('name', '')
        if is_valid(inst_name):
            all_institutions.append(inst_name)
        achievements = edu.get('achievements', {})
        if isinstance(achievements, dict):
            honors = achievements.get('honors', '')
            if is_valid(honors):
                all_honors.append(honors)
    flat['degrees'] = join_list(all_degrees)
    flat['fields_of_study'] = join_list(list(set(all_fields)))
    flat['institutions'] = join_list(all_institutions)
    flat['honors'] = join_list(all_honors)
    flat['num_education'] = len(education)
    skills = record.get('skills', {})
    technical_skills = skills.get('technical', {})
    flat['programming_languages'] = extract_skills_with_levels(
        technical_skills.get('programming_languages', []))
    flat['frameworks'] = extract_skills_with_levels(
        technical_skills.get('frameworks', []))
    flat['databases'] = extract_skills_with_levels(
        technical_skills.get('databases', []))
    flat['cloud_skills'] = extract_skills_with_levels(
        technical_skills.get('cloud', []))
    flat['spoken_languages'] = extract_skills_with_levels(
        skills.get('languages', []))
    projects = record.get('projects', [])
    project_names = []
    project_descriptions = []
    project_roles = []
    project_impacts = []
    for proj in projects:
        name = proj.get('name', '')
        if is_valid(name):
            project_names.append(name)
        desc = proj.get('description', '')
        if is_valid(desc):
            project_descriptions.append(desc)
        role = proj.get('role', '')
        if is_valid(role):
            project_roles.append(role)
        impact = proj.get('impact', '')
        if is_valid(impact):
            project_impacts.append(impact)
    flat['project_names'] = join_list(project_names)
    flat['project_descriptions'] = join_list(project_descriptions, ' | ')
    flat['project_roles'] = join_list(project_roles)
    flat['project_impacts'] = join_list(project_impacts, ' | ')
    flat['num_projects'] = len(projects)
    return flat


def get_seniority_level(record):
    experiences = record.get('experience', [])
    if not experiences:
        return None
    level = experiences[0].get('level', '')
    if isinstance(level, str):
        level = level.lower().strip()
    else:
        return None
    return LEVEL_MAPPING.get(level, None)


def main():
    records_by_seniority = defaultdict(list)
    total_processed = 0
    skipped_no_level = 0
    with open('master_resumes_original.jsonl', 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                record = json.loads(line.strip())
                total_processed += 1
                seniority = get_seniority_level(record)
                if seniority is None:
                    skipped_no_level += 1
                    continue
                flat_record = flatten_record(record)
                flat_record['Seniority'] = seniority

                # Only include if we have complete data (job_title and summary required)
                if not is_valid(flat_record.get('job_title')) or not is_valid(flat_record.get('summary')):
                    continue

                records_by_seniority[seniority].append(flat_record)
            except json.JSONDecodeError as e:
                continue
    SAMPLE_SIZE = 700
    sampled_records = []
    for level in ['junior', 'mid', 'senior']:
        available = records_by_seniority[level]
        # Sort by job_title for deterministic sampling
        available_sorted = sorted(available, key=lambda x: (
            x.get('job_title', ''), x.get('summary', '')))

        if len(available_sorted) < SAMPLE_SIZE:
            sampled_records.extend(available_sorted)
        else:
            sampled = random.sample(available_sorted, SAMPLE_SIZE)
            sampled_records.extend(sampled)
    df = pd.DataFrame(sampled_records)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    output_file = 'cleaned_resumes.csv'
    df.to_csv(output_file, index=False)


if __name__ == '__main__':
    main()
