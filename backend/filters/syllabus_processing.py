import os
import pypdf
from pdf2image import convert_from_path
import pytesseract
import google.generativeai as genai
from models import db, Keyword

# Configure the Generative AI API
genai.configure(api_key=os.environ.get("GENAI_API_KEY", "AIzaSyCfDWgpd8BNO0LgjaarswjzKK3oFsc02v4"))

# Function to load text files
def load_text(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading text file {filepath}: {e}")
        return None

# Function to load PDF files
def load_pdf_text(filepath):
    text = ""
    try:
        reader = pypdf.PdfReader(filepath)
        for page in reader.pages:
            text += page.extract_text() + "\n"
        if not text.strip():  # If no text was extracted, use OCR
            print("No text found in PDF. Falling back to OCR...")
            images = convert_from_path(filepath)
            for image in images:
                text += pytesseract.image_to_string(image) + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF file {filepath}: {e}")
        return None

# Prompts for extracting topics and keywords
prompt_simple = """
Analyze the following syllabus text and extract the main topics and keywords discussed.
Provide the output as a clean list.

Syllabus Text:
---
{syllabus_text}
---

Topics and Keywords:
"""

prompt_structured = """
Act as an academic assistant analyzing a course syllabus.
From the syllabus text provided below, identify:
1. The main topics covered, ideally based on a weekly schedule if present.
2. Key concepts, theories, or specific terminology mentioned.
3. Any software, tools, or techniques explicitly listed.

Present the output in JSON format with keys: "weekly_topics" (list of strings or objects with week/topic), "key_concepts" (list of strings), and "tools_techniques" (list of strings).

Syllabus Text:
---
{syllabus_text}
---

JSON Output:
```json
"""

def process_syllabus(filepath, user_id, syllabus_name, use_structured_prompt=True):
    syllabus_content = load_text(filepath) if filepath.endswith('.txt') else load_pdf_text(filepath)
    if not syllabus_content:
        print("Syllabus content could not be loaded.")
        return None

    # Choose the appropriate prompt
    if use_structured_prompt:
        final_prompt = prompt_structured.format(syllabus_text=syllabus_content)
        final_prompt += "```json\n"
    else:
        final_prompt = prompt_simple.format(syllabus_text=syllabus_content)

    try:
        # Configure generation settings
        generation_config = genai.types.GenerationConfig(temperature=0.2)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Generate content using the AI model
        print(f"Sending prompt to Gemini API:\n{final_prompt}")
        response = model.generate_content(final_prompt, generation_config=generation_config)

        if response.parts:
            extracted_data = response.text
            print(f"Raw response from Gemini API:\n{extracted_data}")

            # Save extracted keywords to the database
            keywords = extracted_data.split("\n")  # Assuming simple list output
            for keyword in keywords:
                if keyword.strip():
                    new_keyword = Keyword(user_id=user_id, syllabus_name=syllabus_name, keyword=keyword.strip())
                    db.session.add(new_keyword)
            db.session.commit()

            return {"success": True, "keywords": keywords}
        else:
            print("Warning: Received empty response or content was blocked.")
            return {"success": False, "message": "No content received from Gemini API."}

    except Exception as e:
        print(f"An error occurred during API call: {e}")
        return {"success": False, "message": str(e)}