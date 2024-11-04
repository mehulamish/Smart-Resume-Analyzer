import os
import streamlit as st
import spacy
from pdfminer.high_level import extract_text
import base64
import time
from collections import Counter
import matplotlib.pyplot as plt
from textblob import TextBlob
import numpy as np
from PIL import Image, ImageDraw

# Set the directory for uploading files
upload_directory = './uploaded/'

# Load the spaCy model explicitly
nlp = spacy.load("en_core_web_sm")

# Function to ensure the directory exists
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Function to extract text from a PDF using pdfminer.six
def pdf_reader(file_path):
    return extract_text(file_path)

# Function to display PDF in the app
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Function to extract skills from text using spaCy
def extract_skills(text):
    doc = nlp(text)
    skills = [token.text for token in doc if token.pos_ in ['NOUN', 'VERB'] and not token.is_stop]
    return skills

# Function to predict qualities based on the extracted skills
def predict_quality(skills, quality_datasets):
    quality_counts = Counter()
    for skill in skills:
        for quality, skillset in quality_datasets.items():
            if skill.lower() in [s.lower() for s in skillset]:
                quality_counts[quality] += 1

    # Filter qualities with a minimum count (e.g., 2)
    qualities_found = {quality: count for quality, count in quality_counts.items() if count >= 2}

    # Sort qualities by count in descending order
    sorted_qualities = sorted(qualities_found, key=qualities_found.get, reverse=True)

    # Return the dictionary of qualities and skills
    return qualities_found

# Function to create a skill radar chart 
def create_skill_radar(qualities):
    if not qualities:
        st.write("No qualities found to create a radar chart.")
        return

    categories = list(qualities.keys())
    data = [qualities[category] for category in categories]

    # Create the radar chart
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    # Set theta for each category (angle on the radar)
    theta = [i / len(categories) * 2 * np.pi for i in range(len(categories))]

    # Set the values (data) for each category
    values = data 

    ax.plot(theta, values, 'b-o')
    ax.fill(theta, values, alpha=0.25)

    # Set the labels
    ax.set_thetagrids(np.degrees(theta), categories)

    # Adjust axis limits
    ax.set_rlim(0, max(data) + 2)

    # Add a title
    ax.set_title('Predicted Personality Traits')
    plt.tight_layout()  # Adjust layout
    st.pyplot(fig)  # Display the plot

# Function to assess resume tone using TextBlob
def assess_tone(resume_text):
    blob = TextBlob(resume_text)
    sentiment = blob.sentiment.polarity
    
    if sentiment >= 0.5:
        tone = "Positive"
    elif sentiment > 0 and sentiment < 0.5:
        tone = "Slightly Positive"
    elif sentiment == 0:
        tone = "Neutral"
    elif sentiment < 0 and sentiment > -0.5:
        tone = "Slightly Negative"
    else:
        tone = "Negative"

    return tone, sentiment

# Function to create a gradient line with cursor 
def create_tone_line(sentiment):
    color_gradient = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 128, 0), (0, 255, 0)]
    
    # Create a blank image
    line_image = Image.new("RGB", (300, 20), (255, 255, 255))  # White background
    draw = ImageDraw.Draw(line_image)

    # Calculate the cursor position based on sentiment (assuming -1 to 1 range)
    cursor_pos = int(np.interp(sentiment, [-1, 1], [0, line_image.width]))  # Normalized to position
    cursor_width = 5 

    # Draw the gradient line
    draw.rectangle([(0, 0), (line_image.width, line_image.height)], fill=(0, 0, 0, 0))  # Transparent fill
    for x in range(line_image.width):
        color_index = int(np.interp(x / line_image.width, [0, 1], [0, len(color_gradient) - 1]))
        draw.line([(x, 0), (x, line_image.height)], fill=color_gradient[color_index]) 

    # Draw the cursor
    draw.line([(cursor_pos - cursor_width / 2, 0), (cursor_pos + cursor_width / 2, 0)], fill="black", width=3)
    draw.line([(cursor_pos - cursor_width / 2, line_image.height), (cursor_pos + cursor_width / 2, line_image.height)], fill="black", width=3)

    return line_image

def run():
    st.set_page_config(page_title="Smart Resume Analyzer", page_icon="📝")

    st.title("Smart Resume Analyzer")
    st.sidebar.image("C:\\Users\\dell\\OneDrive\\Desktop\\College work\\NLP\\img.jpg", caption="Analyzer Logo", use_column_width=True)
    st.sidebar.markdown("## Analyze resumes and predict professional personalities.")
    
    activities = ["Upload Resume", "About"]
    choice = st.sidebar.selectbox("Select Action", activities)

    # Define datasets for quality prediction (expanded)
    quality_datasets = {
        "Hardworking": ['python', 'sql', 'time management', 'problem solving', 'attention to detail', 'resilience', 'dedication', 'goal-oriented', 'version control', 'git', 'jira', 'agile', 'scrum', 'kanban', 'project management', 'deadline', 'efficient', 'organized', 'self-discipline', 'motivated', 'results-driven', 'driven', 'achievement-oriented', 'work ethic'],
        "Team Player": ['collaboration', 'teamwork', 'communication', 'adaptability', 'active listening', 'cooperation', 'supportive', 'empathy', 'agile methodologies', 'scrum master', 'slack', 'stakeholder', 'relationship', 'interpersonal', 'leadership', 'mentor', 'coaching', 'feedback', 'cross-functional', 'inclusive'],
        "Lone Wolf": ['self motivated', 'independent', 'autonomous', 'initiative', 'self-discipline', 'resourceful', 'risk taker', 'introverted', 'freelancing', 'solo developer', 'self-starter', 'problem-solver', 'proactive', 'innovative', 'entrepreneurial', 'creative', 'visionary'],
        "Innovative": ['creative thinking', 'curiosity', 'visionary', 'out-of-the-box thinking', 'entrepreneurial mindset', 'design thinking', 'ideation', 'UI/UX design', 'prototyping tools', 'product innovation', 'experimentation', 'problem-solving', 'solutions', 'optimization', 'research', 'development', 'new ideas', 'change'],
        "Analytical": ['critical thinking', 'data analysis', 'quantitative reasoning', 'logical problem solving', 'research', 'statistical analysis', 'pattern recognition', 'sql queries', 'excel', 'powerbi', 'tableau', 'data visualization', 'metrics', 'reporting', 'statistics', 'mathematics', 'logic', 'problem-solving', 'decision-making'],
        "Leader": ['decision making', 'inspiring others', 'strategic thinking', 'conflict resolution', 'negotiation', 'delegation', 'vision setting', 'accountability', 'leadership frameworks', 'team management', 'okrs', 'influence', 'motivation', 'coaching', 'mentoring', 'training', 'guidance', 'direction', 'strategy', 'vision'],
        "Optimistic": ['positive attitude', 'resilience', 'motivation', 'solution-oriented', 'encouraging', 'forward-thinking', 'hopeful', 'motivational speaking', 'conflict mitigation', 'growth mindset', 'positive', 'enthusiastic', 'confident', 'adaptable', 'flexible', 'optimistic'],
        "Pessimistic": ['realism', 'risk assessment', 'careful planning', 'skepticism', 'worst-case scenario thinking', 'pragmatism', 'problem-spotting', 'disaster recovery', 'contingency planning', 'critical', 'analyzing', 'evaluation', 'risk management', 'quality assurance', 'process improvement'],
        "Organized": ['planning', 'scheduling', 'time management', 'prioritization', 'goal setting', 'task management', 'efficiency', 'focus', 'project management tools', 'asana', 'notion', 'confluence', 'systematic', 'methodical', 'process', 'workflow', 'documentation', 'details', 'structured'],
        "Creative": ['artistic skills', 'design thinking', 'conceptualization', 'visualization', 'content creation', 'innovation', 'imagination', 'graphic design', 'figma', 'blender', 'adobe suite', 'photoshop', 'illustrator', 'art', 'design', 'media', 'writing', 'photography', 'music', 'video'],
        "Tech-Savvy": ['programming', 'automation', 'troubleshooting', 'machine learning', 'artificial intelligence', 'cybersecurity', 'data science', 'networking', 'aws', 'azure', 'devops', 'docker', 'kubernetes', 'ci/cd', 'terraform', 'cloud computing', 'big data', 'software development', 'coding', 'scripting', 'database', 'web development'],
        "Empathetic": ['emotional intelligence', 'active listening', 'understanding others', 'conflict resolution', 'supportive communication', 'patience', 'kindness', 'team support', 'mentorship', 'peer review', 'communication skills', 'relationship building', 'compassion', 'humanity', 'people skills'],
        "Detail-Oriented": ['meticulous', 'proofreading', 'quality assurance', 'accuracy', 'editing', 'precision', 'data validation', 'consistency', 'unit testing', 'debugging', 'code reviews', 'qa testing', 'thorough', 'organized', 'systematic', 'analytical', 'critical thinking', 'attention to detail'],
        "Flexible": ['adaptability', 'handling ambiguity', 'multitasking', 'open to change', 'quick learning', 'resilience in chaos', 'versatility', 'continuous learning', 'cross-functional skills', 'full-stack development', 'agile', 'fast learner', 'resourceful', 'adaptable', 'flexible', 'willingness to learn'],
        "Competitive": ['drive for success', 'ambition', 'achievement-oriented', 'goal-chasing', 'result-oriented', 'performance tracking', 'winning mindset', 'hackathons', 'coding competitions', 'goal-crushing', 'results-driven', 'performance', 'achievement', 'excellence', 'high-achiever'],
        "Risk-Taker": ['courage', 'experimenting', 'bold decisions', 'venturing into new areas', 'high-stakes problem solving', 'overcoming challenges', 'startup mentality', 'entrepreneurship', 'taking initiative', 'change', 'challenges', 'innovation', 'growth', 'unconventional'],
        "Patient": ['long-term focus', 'calmness under pressure', 'perseverance', 'delayed gratification', 'steady effort', 'understanding timelines', 'mentorship in challenging environments', 'gradual progress', 'endurance', 'persistence', 'dedication', 'focus', 'calm', 'composed', 'understanding'],
        "Pragmatic": ['down-to-earth', 'realism', 'practical problem-solving', 'rationality', 'grounded decisions', 'evidence-based', 'real-world application', 'cost-benefit analysis', 'trade-off evaluation', 'logical', 'analytical', 'problem-solving', 'solution-oriented', 'results-driven', 'practical', 'efficient'],
        "Strategist": ['long-term planning', 'systematic thinking', 'anticipation', 'strategic foresight', 'resource allocation', 'project mapping', 'optimization', 'roadmap planning', 'market strategy', 'competitor analysis', 'vision', 'planning', 'strategy', 'analysis', 'forecast', 'goals', 'objectives', 'future'],
        "Charismatic": ['influencing', 'building rapport', 'inspiring trust', 'persuasive communication', 'engagement', 'magnetism', 'self-confidence', 'public speaking', 'sales pitch', 'client relations', 'communication', 'leadership', 'motivation', 'inspiration', 'confidence', 'persuasion', 'enthusiasm', 'passion'],
        "Curious": ['inquisitiveness', 'research-driven', 'asking questions', 'exploration', 'pursuit of knowledge', 'open-minded', 'seeking answers', 'r&d', 'continuous education', 'self-directed learning', 'learning', 'knowledge', 'research', 'innovation', 'growth', 'development', 'questioning'],
        "Diligent": ['thoroughness', 'consistent effort', 'carefulness', 'focused work', 'disciplined', 'systematic approach', 'methodical', 'error-checking', 'follow-up tasks', 'documentation', 'detailed', 'organized', 'structured', 'efficient', 'productive', 'reliable', 'accurate'],
        "Persuasive": ['convincing others', 'negotiation', 'argumentative skills', 'debate', 'influence', 'assertiveness', 'closing deals', 'sales techniques', 'advertising', 'marketing campaigns', 'communication', 'leadership', 'presentation', 'communication skills', 'influence', 'persuasion', 'advocate'],
        "Adventurous": ['risk-taking', 'outdoor skills', 'spontaneity', 'exploring new opportunities', 'embracing challenges', 'open to new experiences', 'international work experience', 'fieldwork', 'travel for work', 'new challenges', 'growth', 'learning', 'exploration', 'change', 'adaptation'],
        "Decisive": ['quick decision making', 'assertive choices', 'bold actions', 'clarity of thought', 'confidence in judgments', 'action-oriented', 'emergency response', 'crisis management', 'problem-solving', 'decision-making', 'leadership', 'initiative', 'proactive', 'results-driven', 'confident'],
        "Efficient": ['time optimization', 'resource management', 'task prioritization', 'lean operations', 'minimizing waste', 'maximizing productivity', 'process automation', 'workflow optimization', 'kanban', 'organized', 'structured', 'process', 'workflow', 'productivity', 'time management', 'prioritization'],
        "Logical": ['deductive reasoning', 'structured problem solving', 'rational analysis', 'cause-effect understanding', 'evidence-based decision making', 'algorithmic thinking', 'data structures', 'back-end logic', 'problem-solving', 'analytical', 'critical thinking', 'reasoning', 'logic', 'analysis', 'evaluation'],
        "Passionate": ['high energy', 'enthusiasm', 'commitment', 'emotional investment', 'going the extra mile', 'intense focus', 'driven by purpose', 'devotion to cause', 'community involvement', 'passion', 'enthusiasm', 'motivation', 'dedication', 'energy', 'drive', 'commitment', 'purpose'],
        "Visionary": ['future planning', 'big-picture thinking', 'inspiring innovation', 'transformational leadership', 'seeing opportunities', 'goal setting for the long term', 'trend forecasting', 'futurism', 'vision', 'strategy', 'innovation', 'leadership', 'growth', 'future', 'change'],
        "Balanced": ['work-life harmony', 'managing stress', 'emotional stability', 'holistic focus', 'mindfulness', 'consistency', 'sustainability', 'health-conscious work practices', 'mental resilience', 'well-being', 'health', 'fitness', 'lifestyle', 'balance', 'harmony', 'stability'],
        "Technical Expert": ['Python', 'Java', 'C++', 'JavaScript', 'React', 'Node.js', 'Cloud architecture', 'Blockchain', 'Microservices', 'API development', 'TensorFlow', 'PyTorch', 'software development', 'programming', 'coding', 'scripting', 'database', 'network', 'security', 'cloud'],
        "Data-Driven": ['data engineering', 'ETL pipelines', 'big data', 'SQL', 'NoSQL', 'data warehousing', 'Spark', 'Hadoop', 'data lakes', 'data governance', 'machine learning models', 'predictive analytics', 'machine learning', 'data analysis', 'analytics', 'statistics', 'data science', 'visualization']
    }

    if choice == "Upload Resume":
        st.subheader("Upload your Resume for Analysis")
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Processing your resume...'):
                time.sleep(2)

            # Ensure that the upload directory exists
            ensure_directory_exists(upload_directory)

            # Save the uploaded file in the "uploaded" directory
            save_path = os.path.join(upload_directory, pdf_file.name)
            with open(save_path, "wb") as f:
                f.write(pdf_file.getbuffer())

            # Show PDF content
            show_pdf(save_path)

            # Extract text from the resume PDF using pdfminer.six
            resume_text = pdf_reader(save_path)

            # Parse the resume using the extracted text
            if resume_text:
                st.success("Resume Analysis Successful")

                # Display basic information (This can be improved with proper parsing)
                st.subheader("Extracted Resume Text:")
                st.write(resume_text[:300] + "...")  # Display a portion of the text for brevity

                # Extract skills from the resume text
                skills = extract_skills(resume_text)
                st.subheader("Extracted Skills:")
                st.write(skills)  # Display extracted skills

                # Predict qualities based on the extracted skills
                st.subheader("Predicted Qualities:")
                qualities = predict_quality(skills, quality_datasets)
                if qualities:
                    for quality in qualities:
                        st.write(f"- {quality}")

                    # Create Skill Radar
                    st.subheader("Skill Radar:")
                    create_skill_radar(qualities)  # Pass the qualities dictionary directly

                    # Assess Overall Tone (modified)
                    st.subheader("Overall Tone of the Resume:")
                    resume_tone, sentiment = assess_tone(resume_text)
                    st.write(resume_tone)

                    # Display the gradient line with slider
                    st.subheader("Interactive Tone Visualization:")
                    slider_value = st.slider("Tone Value", -1.0, 1.0, sentiment, step=0.01,disabled = True)  # Initial value is sentiment
                    tone_line = create_tone_line(slider_value)
                    st.image(tone_line, use_column_width=True)

                else:
                    st.write("No qualities matched with a minimum count, upload a better elaborated resume.")
            else:
                st.error("Sorry, we could not extract text from the resume.")

    elif choice == "About":
        st.subheader("About this Project")
        st.text("This Smart Resume Analyzer helps analyze resumes to predict\npersonalities of a person based on skills extracted from resumes.")
        st.text("Project made by:\nMehul Mathur 21BCE2099\nMayank Shekhar Raj 21BCE0036")

if __name__ == '__main__':
    run()
