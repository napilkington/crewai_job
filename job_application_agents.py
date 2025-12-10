from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
import requests
import os
from bs4 import BeautifulSoup
import json
import re
from pathlib import Path
from datetime import date
from models import CV, CoverLetter
from weasyprint import HTML
from PIL import Image
from pdf2image import convert_from_bytes
from pybars import Compiler
from azure_crewai_connect import AzureCrewAILLM
from typing import Type
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Initialize the LLM with Azure AD authentication
model = AzureCrewAILLM()

# Tool Input Schemas
class ReadFileInput(BaseModel):
    file_path: str = Field(..., description="Path to the file to read")

class WriteFileInput(BaseModel):
    file_path: str = Field(..., description="Path to the file to write")
    content: str = Field(..., description="Content to write to the file")

class WebpageInput(BaseModel):
    url: str = Field(..., description="URL of the webpage to fetch")

class RenderDocumentsInput(BaseModel):
    cv_data: dict = Field(..., description="CV data dictionary")
    cover_letter_data: dict = Field(..., description="Cover letter data dictionary")
    output_dir: str = Field(..., description="Output directory path")

# Tools
class ReadTextFileTool(BaseTool):
    name: str = "read_text_file"
    description: str = "Reads a text file and returns the content"
    args_schema: Type[BaseModel] = ReadFileInput

    def _run(self, file_path: str) -> str:
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

class WriteTextFileTool(BaseTool):
    name: str = "write_text_file"
    description: str = "Writes content to a text file"
    args_schema: Type[BaseModel] = WriteFileInput

    def _run(self, file_path: str, content: str) -> str:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as file:
                file.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

class GetWebpageContentsTool(BaseTool):
    name: str = "get_webpage_contents"
    description: str = "Reads the webpage with a given URL and returns the page content"
    args_schema: Type[BaseModel] = WebpageInput

    def _run(self, url: str) -> str:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try multiple common selectors for job details
            title = ''
            company = ''
            location = ''
            description = ''

            # Title selectors
            title_selectors = ['h1', '.job-title', '.position-title', '[data-testid="job-title"]']
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    title = element.text.strip()
                    break

            # Company selectors
            company_selectors = ['.company-name', '.employer', '[data-testid="company-name"]']
            for selector in company_selectors:
                element = soup.select_one(selector)
                if element:
                    company = element.text.strip()
                    break

            # Location selectors
            location_selectors = ['.location', '.job-location', '[data-testid="location"]']
            for selector in location_selectors:
                element = soup.select_one(selector)
                if element:
                    location = element.text.strip()
                    break

            # Description selectors
            description_selectors = ['.job-description', '.description', '#job-description', '[data-testid="job-description"]']
            for selector in description_selectors:
                element = soup.select_one(selector)
                if element:
                    description = element.text.strip()
                    break

            # If we couldn't find the description with specific selectors, try to get the main content
            if not description:
                content_blocks = soup.find_all(['div', 'section', 'article'])
                if content_blocks:
                    description = max(content_blocks, key=lambda x: len(x.text.strip())).text.strip()

            job_content = {
                'title': title or 'Position Title Not Found',
                'company': company or 'Company Name Not Found',
                'location': location or 'Location Not Found',
                'description': description or 'Job Description Not Found'
            }
            
            return json.dumps(job_content, indent=2)
        except Exception as e:
            return f"Error fetching webpage: {str(e)}"

class RenderAndSaveDocumentsTool(BaseTool):
    name: str = "render_and_save_documents"
    description: str = "Renders and saves CV and Cover Letter as PDF and JPEG"
    args_schema: Type[BaseModel] = RenderDocumentsInput

    def _run(self, cv_data: dict, cover_letter_data: dict, output_dir: str) -> str:
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            cv = CV(**cv_data)
            cover_letter = CoverLetter(**cover_letter_data)
            
            def render_template(template_path, data):
                with open(template_path, 'r') as file:
                    template_content = file.read()
                compiler = Compiler()
                template = compiler.compile(template_content)
                return template(data.model_dump())
            
            def html_to_jpeg(html_content, output_path):
                pdf = HTML(string=html_content).write_pdf()
                images = convert_from_bytes(pdf)
                if images:
                    images[0].save(output_path, 'JPEG', quality=95)
            
            def html_to_pdf(html_content, output_path):
                HTML(string=html_content).write_pdf(output_path)
            
            cv_template_path = "templates/cv_template.html"
            cv_html = render_template(cv_template_path, cv)
            
            cv_jpg_path = os.path.join(output_dir, "cv.jpg")
            cv_pdf_path = os.path.join(output_dir, "cv.pdf")
            
            html_to_jpeg(cv_html, cv_jpg_path)
            html_to_pdf(cv_html, cv_pdf_path)
            
            cl_template_path = "templates/cover_letter_template.html"
            cl_html = render_template(cl_template_path, cover_letter)
            
            cl_jpg_path = os.path.join(output_dir, "cover_letter.jpg")
            cl_pdf_path = os.path.join(output_dir, "cover_letter.pdf")
            
            html_to_jpeg(cl_html, cl_jpg_path)
            html_to_pdf(cl_html, cl_pdf_path)
            
            return json.dumps({
                "success": True,
                "files": {
                    "cv_jpg": cv_jpg_path,
                    "cv_pdf": cv_pdf_path,
                    "cover_letter_jpg": cl_jpg_path,
                    "cover_letter_pdf": cl_pdf_path
                }
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class JobApplicationCrew:
    def __init__(self):
        self.model = AzureCrewAILLM()
        
    def job_crawler(self) -> Agent:
        return Agent(
            role='Job Description Crawler',
            goal='Extract and analyze job posting information',
            backstory="""You are an expert at analyzing job postings and extracting key information.
            You focus on identifying essential requirements, qualifications, responsibilities, and company details.
            You also ensure proper formatting of company and job information for file organization.""",
            verbose=True,
            tools=[GetWebpageContentsTool(), ReadTextFileTool()],
            allow_delegation=False,
            llm=self.model
        )

    def cv_writer(self) -> Agent:
        return Agent(
            role='CV Writer',
            goal='Create a professional CV that matches job requirements while maintaining authenticity',
            backstory="""You are an experienced CV writer who specializes in creating compelling CVs that match job requirements.
            You understand the Pydantic model requirements and ensure all data fits within specified constraints.
            
            Key guidelines:
            1. NEVER make up or fabricate specific metrics or statistics
            2. Focus on describing actual responsibilities and achievements without quantification
            3. Use clear, professional language to describe experience
            4. Maintain consistent formatting and style
            5. Ensure content is authentic and verifiable
            
            You understand the following constraints:
            - full_name: 1-50 characters (use full capacity)
            - job_title: 1-50 characters (use full capacity)
            - location: 1-50 characters (use full capacity)
            - email: valid email format
            - phone: 10-20 characters
            - linkedin: 1-100 characters (use full capacity)
            - professional_summary: 50-300 characters (aim for 250-300)
            - technical_skills: 1-5 items, each with:
              - category: 1-30 characters (use 20-30)
              - skills: 1-150 characters (aim for 100-150)
            - experience: 1-3 items, each with:
              - job_title: 1-50 characters (use full capacity)
              - company: 1-50 characters (use full capacity)
              - date_range: 1-30 characters (use full capacity)
              - responsibilities: 1-3 items, each 1-120 characters (aim for 100-120)
            - education: 1-2 items, each with:
              - degree: 1-50 characters (use full capacity)
              - institution: 1-50 characters (use full capacity)
              - year: 4 characters
              - achievements: 0-2 items, each 1-100 characters (aim for 80-100)
            - certifications: 0-5 items, each 1-40 characters (use 30-40)""",
            verbose=True,
            tools=[ReadTextFileTool()],
            allow_delegation=False,
            llm=self.model
        )

    def cover_letter_writer(self) -> Agent:
        return Agent(
            role='Cover Letter Writer',
            goal='Create authentic and compelling cover letters that highlight relevant qualifications',
            backstory="""You are a professional cover letter writer who creates engaging and relevant cover letters.
            You understand the importance of authenticity and avoid making unsubstantiated claims.
            
            Key guidelines:
            1. NEVER include fabricated metrics or statistics
            2. Focus on actual experience and skills
            3. Use specific examples without quantification
            4. Maintain professional and genuine tone
            5. Highlight relevant experience without exaggeration
            
            You understand the following constraints:
            - full_name: 1-50 characters
            - address: 1-100 characters
            - city: 1-50 characters
            - state: 2 characters
            - zip: 5-10 characters
            - email: valid email format
            - phone: 10-20 characters
            - date: valid date format
            - hiring_manager_name: 1-50 characters
            - job_title: 1-50 characters
            - company_name: 1-50 characters
            - company_address: 1-100 characters
            - company_city: 1-50 characters
            - company_state: 2 characters
            - company_zip: 5-10 characters
            - paragraphs: 3 items, each 50-800 characters
            - closing_paragraph: 20-300 characters""",
            verbose=True,
            tools=[ReadTextFileTool()],
            allow_delegation=False,
            llm=self.model
        )

    def document_processor(self) -> Agent:
        return Agent(
            role='Document Processor',
            goal='Generate professionally formatted PDF and JPEG versions of the CV and cover letter',
            backstory="""You are an expert at processing and formatting documents.
            You ensure all documents are properly formatted and validate against the Pydantic models.
            You focus on creating clean, professional layouts with consistent styling.
            
            Key responsibilities:
            1. Ensure proper spacing and alignment
            2. Maintain consistent font usage
            3. Create clear visual hierarchy
            4. Optimize readability
            5. Generate high-quality output files""",
            verbose=True,
            tools=[RenderAndSaveDocumentsTool()],
            allow_delegation=False,
            llm=self.model
        )

    def create_tasks(self, job_url: str, output_dir: str) -> list:
        task_extract_job = Task(
            description=f"""Extract key information from the job posting at {job_url}.
            Focus on required skills, qualifications, responsibilities, and company culture.
            Return the information in a structured format including:
            1. Job requirements and qualifications
            2. Company details and culture
            3. Role responsibilities
            Format the output in JSON format for other agents to use.""",
            expected_output="A JSON string containing structured job posting information",
            agent=self.job_crawler()
        )

        task_create_cv = Task(
            description="""Create a CV that matches the job requirements.
            First, read the base CV from CV.txt using the read_text_file tool.
            Then, modify the content to match the job requirements while following the Pydantic model structure.
            Ensure all content fits within the specified length constraints.
            CRITICAL: Return ONLY valid, complete JSON. Keep experience array to maximum 2 entries. Keep responsibilities to 2-3 items max.
            Return the CV data in valid JSON format that matches the CV model.""",
            expected_output="A complete, valid JSON string containing CV data. Must end with proper closing braces.",
            agent=self.cv_writer(),
            context=[task_extract_job]
        )

        task_create_cover_letter = Task(
        description="Create a cover letter that highlights relevant qualifications. \
            First, read the base cover letter from cover_letter.txt using the read_text_file tool. \
            Then, modify the content to match the job requirements while following the Pydantic model structure. \
            Ensure all content fits within the specified length constraints. \
            CRITICAL: Return ONLY valid, complete JSON. Keep paragraphs array to exactly 3 entries. Ensure closing_paragraph is complete. \
            Return the cover letter data in valid JSON format that matches the CoverLetter model.",
            expected_output="A JSON string containing cover letter data that matches the CoverLetter Pydantic model",
            agent=self.cover_letter_writer(),
            context=[task_extract_job]
        )

        return [task_extract_job, task_create_cv, task_create_cover_letter]

def main():
    # Get job URL from user
    job_url = input("\nPlease enter the job posting URL: ").strip()
    
    # Set up output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\nStarting job application process...")
    print(f"Job URL: {job_url}")
    print(f"Output Directory: {output_dir}")
    
    # Initialize the crew
    application_crew = JobApplicationCrew()
    
    # Create initial tasks
    initial_tasks = application_crew.create_tasks(job_url, output_dir)

    # Create and run the crew
    crew = Crew(
        agents=[
            application_crew.job_crawler(),
            application_crew.cv_writer(),
            application_crew.cover_letter_writer(),
            application_crew.document_processor()
        ],
        tasks=initial_tasks,
        verbose=True
    )

    try:
        # Run document creation
        result = crew.kickoff()
        print("\n✅ Crew execution completed!")
        print("\n📄 Generated Data:")
        print(result)
        print("\n" + "="*80)
        print("✅ SUCCESS: CV and Cover Letter data generated with Azure AD authentication!")
        print("="*80)
        
        # Now render the documents using the tool
        print("\n🎨 Rendering PDF and JPEG documents...")
        try:
            # Get the task outputs - try different methods to extract JSON
            cv_task = crew.tasks[1]
            cl_task = crew.tasks[2]
            
            # Try to get raw output
            if hasattr(cv_task.output, 'raw'):
                cv_output = cv_task.output.raw
            elif hasattr(cv_task.output, 'result'):
                cv_output = cv_task.output.result
            elif hasattr(cv_task.output, 'json_dict'):
                cv_output = cv_task.output.json_dict
            else:
                cv_output = str(cv_task.output)
            
            if hasattr(cl_task.output, 'raw'):
                cl_output = cl_task.output.raw
            elif hasattr(cl_task.output, 'result'):
                cl_output = cl_task.output.result
            elif hasattr(cl_task.output, 'json_dict'):
                cl_output = cl_task.output.json_dict
            else:
                cl_output = str(cl_task.output)
            
            # Parse JSON more carefully
            import re
            
            # If it's a string, try to extract JSON from it
            if isinstance(cv_output, str):
                # Try to find JSON object in the string
                json_match = re.search(r'\{[\s\S]*\}', cv_output)
                if json_match:
                    cv_output = json_match.group(0)
                cv_data = json.loads(cv_output)
            else:
                cv_data = cv_output
                
            if isinstance(cl_output, str):
                # Try to find JSON object in the string
                json_match = re.search(r'\{[\s\S]*\}', cl_output)
                if json_match:
                    cl_output = json_match.group(0)
                cl_data = json.loads(cl_output)
            else:
                cl_data = cl_output
            
            # Render documents
            render_tool = RenderAndSaveDocumentsTool()
            render_result = render_tool._run(cv_data, cl_data, output_dir)
            
            render_info = json.loads(render_result)
            if render_info.get("success"):
                print("\n✅ Documents rendered successfully!")
                print(f"   📄 CV PDF: {render_info['files']['cv_pdf']}")
                print(f"   📄 CV JPEG: {render_info['files']['cv_jpg']}")
                print(f"   📄 Cover Letter PDF: {render_info['files']['cover_letter_pdf']}")
                print(f"   📄 Cover Letter JPEG: {render_info['files']['cover_letter_jpg']}")
            else:
                print(f"\n⚠️ Rendering failed: {render_info.get('error')}")
                
        except Exception as render_error:
            print(f"\n⚠️ Could not render documents: {render_error}")
            print("    JSON data was successfully generated, but PDF/JPEG rendering failed.")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*80)
        print("✅ SUCCESS: Documents generated!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error during execution: {str(e)}")

if __name__ == "__main__":
    main() 