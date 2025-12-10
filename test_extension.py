#!/usr/bin/env python3
"""
Test script to simulate browser extension sending a job to the server
"""

import requests
import json

# Sample job data (like what the browser extension would send)
test_job = {
    "title": "Senior Software Engineer",
    "company": "TechCorp Inc",
    "location": "San Francisco, CA",
    "description": """
    About the Role:
    We are seeking a talented Senior Software Engineer to join our growing team.
    
    Responsibilities:
    - Design and implement scalable web applications
    - Collaborate with cross-functional teams
    - Mentor junior developers
    - Write clean, maintainable code
    
    Requirements:
    - 5+ years of software development experience
    - Strong proficiency in Python, JavaScript, or similar languages
    - Experience with cloud platforms (AWS, Azure, GCP)
    - Excellent problem-solving skills
    - Bachelor's degree in Computer Science or related field
    
    Nice to Have:
    - Experience with React, Node.js
    - Knowledge of containerization (Docker, Kubernetes)
    - Prior experience in a startup environment
    
    What We Offer:
    - Competitive salary and equity
    - Health, dental, and vision insurance
    - Flexible work arrangements
    - Professional development opportunities
    """,
    "url": "https://www.linkedin.com/jobs/view/test-job-123",
    "extractedAt": "2024-12-01T21:00:00Z"
}

print("\n" + "="*80)
print("🧪 Testing Browser Extension → Server → CrewAI Pipeline")
print("="*80 + "\n")

print("📤 Sending test job to server...")
print(f"   Title: {test_job['title']}")
print(f"   Company: {test_job['company']}")
print(f"   Location: {test_job['location']}\n")

try:
    response = requests.post(
        'http://localhost:5000/process-job',
        json=test_job,
        timeout=300  # 5 minutes timeout
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n" + "="*80)
        print("✅ SUCCESS!")
        print("="*80)
        print(f"\nStatus: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        print("\n📁 Check the 'output' folder for generated documents:")
        print("   - cv.pdf")
        print("   - cv.jpg")
        print("   - cover_letter.pdf")
        print("   - cover_letter.jpg")
    else:
        print(f"\n❌ Server returned error: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ Could not connect to server!")
    print("Make sure the server is running: python server.py")
except requests.exceptions.Timeout:
    print("\n⏱️  Request timed out (processing takes time)")
    print("Check server.log for progress")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*80 + "\n")
