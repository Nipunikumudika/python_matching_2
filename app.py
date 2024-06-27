from flask import Flask, request, jsonify
import spacy
import jsonlines
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})
nlp = spacy.load('en_core_web_sm')

def add_newruler_to_pipeline(skill_pattern_path):
    try:
        ruler = nlp.add_pipe("entity_ruler", after='parser')
        ruler.from_disk(skill_pattern_path)
        print(f"Entity ruler loaded successfully from {skill_pattern_path}")
    except Exception as e:
        print(f"Error loading entity ruler from {skill_pattern_path}: {e}")

def create_skill_set(doc):
    return set([ent.label_.upper()[6:] for ent in doc.ents if 'skill' in ent.label_.lower()])

def match_skills(jd_skills, cv_set):
    if len(jd_skills) < 1:
        return 'Could not extract skills from job offer text'
    
    # Convert both sets of skills to lowercase for case insensitive comparison
    vacature_set_lower = {skill.lower() for skill in jd_skills}
    cv_set_lower = {skill.lower() for skill in cv_set}
    
    # Calculate the intersection of lowercase skills
    matched_skills = vacature_set_lower.intersection(cv_set_lower)
    
    pct_match = round(len(matched_skills) / len(vacature_set_lower) * 100, 2)

    
    return {
        'match_percentage': pct_match,
        'required_skills': list(vacature_set_lower),
        'matched_skills': list(matched_skills)
    }

@app.route('/match-skills', methods=['POST'])
def match_skills_api():
    data = request.json
    
    cv_text = data.get('resume', '')
    jd_text = data.get('jobDescription', '')

    cv_doc = nlp(cv_text)
    jd_doc = nlp(jd_text)
    
    cv_skills = create_skill_set(cv_doc)
    jd_skills = create_skill_set(jd_doc)

    match_result = match_skills(jd_skills, cv_skills)
    print(match_result)
    response = jsonify(match_result)
    response.headers.add('Access-Control-Allow-Origin', 'https://ncs.sasandamanahara.com')
    return response


@app.route('/')
def start():
    try:
        ruler = nlp.add_pipe("entity_ruler", after='parser')
        ruler.from_disk("skill_patterns.jsonl")
        print(f"Entity ruler loaded successfully from")

        # Print the contents of skill_patterns.jsonl
        with jsonlines.open("skill_patterns.jsonl") as reader:
            print("Skill patterns in skill_patterns.jsonl:")
            for obj in reader:
                print(obj)
    except Exception as e:
        print(f"Error loading entity ruler: {e}")
    return "Start matching...."


if __name__ == '__main__':
    # Load skill patterns
    add_newruler_to_pipeline("skill_patterns.jsonl")
    app.run(debug=True)  # You can change debug=True to debug=False in production
