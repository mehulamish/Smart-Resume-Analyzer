# Smart Resume Analyzer

The Smart Resume Analyzer is a web application developed with Streamlit that helps users analyze resumes to identify key skills and predict potential personality traits. It leverages NLP (Natural Language Processing) with spaCy and text sentiment analysis using TextBlob. It provides visual feedback in the form of a radar chart to represent personality traits and a color-coded tone assessment.

## Features

- **PDF Upload & Text Extraction**: Upload PDF resumes, which are then processed and analyzed.
- **Skill Extraction**: Extracts notable skills and competencies from the resume text.
- **Personality Prediction**: Uses extracted skills to predict personality traits based on pre-defined categories.
- **Tone Analysis**: Assesses the sentiment of the resume text and displays it on a color-coded line.
- **Visual Outputs**:
  - **Radar Chart**: Visual representation of predicted personality traits.
  - **Sentiment Line**: Gradient line that indicates the tone of the resume (positive, neutral, or negative).

## Installation

### Prerequisites

Ensure you have Python installed and install the required packages. You can do this by running:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file should include the following libraries:

```
streamlit
spacy
pdfminer.six
textblob
matplotlib
pillow
numpy
```

Additionally, you may need to download the spaCy model if it’s not already available:

```bash
python -m spacy download en_core_web_sm
```

### Directory Setup

The application uses an `uploaded` directory to store uploaded files temporarily. Make sure the directory exists:

```bash
mkdir uploaded
```

## Usage

1. **Run the Application**: Start the Streamlit app by running:

   ```bash
   streamlit run app.py
   ```

2. **Upload a Resume**: On the app’s sidebar, select "Upload Resume" and upload a PDF file for analysis.
3. **View PDF**: The app will display the uploaded PDF content for verification.
4. **Analyze Resume**: The app extracts skills, predicts personality traits, and provides a sentiment analysis.
5. **View Results**:
   - **Radar Chart**: Displays identified personality traits.
   - **Tone Line**: A gradient line shows the sentiment score of the resume text.

## Files

- `app.py`: Main script for the Streamlit application.
- `uploaded/`: Directory for temporarily storing uploaded resumes.

## Functions

### `pdf_reader(file_path)`
Reads and extracts text from a PDF file.

### `show_pdf(file_path)`
Displays the PDF file within the app.

### `extract_skills(text)`
Extracts keywords (skills) from the resume text.

### `predict_quality(skills, quality_datasets)`
Predicts qualities/personality traits based on extracted skills.

### `create_skill_radar(qualities)`
Creates and displays a radar chart of identified personality traits.

### `assess_tone(resume_text)`
Analyzes the sentiment (tone) of the resume text.

### `create_tone_line(sentiment)`
Creates a gradient line indicating sentiment, with a cursor to show the score.

## Customization

The `quality_datasets` dictionary in the code can be updated to add or modify personality traits and associated skills for improved analysis.
Further `all_data_skill_and_non_skills.csv` csv file can be used to identify more skills to get better results.

