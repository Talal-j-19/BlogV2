import os
import json
import datetime
import google.generativeai as genai
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_blog_content(topic: str, author: str = "Admin", api_key: str = None) -> Dict[str, Any]:
    """
    Generate a blog post using Gemini 2.5 Pro model.
    
    Args:
        topic (str): The topic for the blog post
        author (str, optional): Author name. Defaults to "Admin".
        api_key (str, optional): Google AI API key. If not provided, will try to load from .env.
        
    Returns:
        Dict[str, Any]: Generated blog content in a structured format
        
    Raises:
        ValueError: If API key is not found
    """
    # Get API key from parameter or environment variable
    api_key = api_key or os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("API key not found. Please set GEMINI_API_KEY in your .env file or pass it as an argument.")
        
    # Configure the Gemini API
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro')
    
    # Create the prompt
    prompt = f"""You are an expert content writer and SEO specialist. Generate a comprehensive, well-researched, and engaging blog post about {topic} that is optimized for search engines. 

Output the content as a JSON object with the following structure:
{{
  "title": "A compelling, SEO-optimized title under 60 characters",
  "meta_description": "A meta description under 160 characters that includes primary keywords",
  "slug": "seo-friendly-url-slug-based-on-title",
  "publication_date": "{datetime.datetime.now().strftime('%Y-%m-%d')}",
  "author": "{author}",
  "categories": ["Gaming", "Entertainment"],
  "tags": ["video games", "gaming", "2025 games", "new releases", "gaming news"],
  "content": {{
    "introduction": "Engaging introduction that hooks the reader and includes primary keywords naturally. Keep it under 150 words.",
    "sections": [
      {{
        "heading": "H2 heading with focus keyword",
        "content": "Well-structured paragraph with related keywords and internal/external links where relevant."
      }}
    ],
    "faq": [
      {{
        "question": "Common question about the topic",
        "answer": "Detailed, helpful answer (2-3 sentences)."
      }},
      {{
        "question": "Another common question",
        "answer": "Clear and informative response."
      }}
    ],
    "conclusion": "Summarize key points and include a clear call-to-action. Keep it under 150 words."
  }},
  "seo": {{
    "focus_keyword": "primary keyword",
    "secondary_keywords": ["keyword 2", "keyword 3"],
    "word_count": "Aim for 1200-1800 words",
    "readability": "Ensure content is easily scannable with short paragraphs and subheadings"
  }}
}}

Additional Guidelines:
1. Include 3-5 relevant FAQs that address common user queries about the topic
2. Structure FAQs with clear, concise questions and detailed answers
3. Use natural language that matches how people would ask these questions
4. Include relevant keywords in the FAQ section where appropriate
5. Ensure FAQs provide genuine value and address potential concerns
6. Make sure the content is well-structured with proper heading hierarchy (H1, H2, H3)
7. Include relevant keywords naturally throughout the content
8. Add internal/external links to authoritative sources where applicable
9. Ensure the content is mobile-friendly and easy to read
10. Include at least one data point or statistic from a credible source

Topic: {topic}"""

    try:
        # Generate content
        response = model.generate_content(prompt)
        
        # Extract JSON from the response
        content = response.text.strip()
        # Sometimes the response might include markdown code blocks
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].strip()
            
        # Parse the JSON response
        blog_data = json.loads(content)
        return blog_data
        
    except Exception as e:
        print(f"Error generating blog content: {str(e)}")
        raise
