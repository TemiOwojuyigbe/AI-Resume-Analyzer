from flask import Flask, request, jsonify  # Handles file uploads & JSON responses
from flask_cors import CORS  # Allows frontend to communicate with Flask backend
import os  # Helps with file handling
import PyPDF2  # Extracts text from PDFs
import docx  # Extracts text from DOCX
from openai import OpenAI  # OpenAI for AI-powered resume analysis

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enables Cross-Origin Resource Sharing

# Set OpenAI API Key 
client = OpenAI(api_key= "")

# Function to analyze resume using OpenAI
def analyze_resume(resume_text, job_description):
    prompt = f"Compare the following resume with the job description and suggest improvements:\n\nResume:\n{resume_text}\n\nJob Description:\n{job_description}\n\nProvide missing keywords and recommendations."

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# Create "uploads" folder if it doesn't exist
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Function to extract text from PDFs
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

# Function to extract text from DOCX
def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Route for the Home Page
@app.route('/')
def home():
    return "AI Resume Analyzer Backend is Running!"

# Route to Upload Resume and Extract Text
@app.route('/upload', methods=['POST'])
def upload_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume"]
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file.filename.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        return jsonify({"error": "Unsupported file format"}), 400

    return jsonify({"resume_text": text})

# Route to Analyze Resume with AI
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()  # <-- Fixed Typo Here
    resume_text = data.get("resume_text")
    job_description = data.get("job_description")

    if not resume_text or not job_description:
        return jsonify({"error": "Missing resume text or job description"}), 400

    suggestions = analyze_resume(resume_text, job_description)
    return jsonify({"suggestions": suggestions})

# Run the Flask Server
if __name__ == '__main__':
    app.run(debug=True)
