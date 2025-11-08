import os
import json
import datetime
import base64
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv
from urllib.parse import quote

# Load environment variables from .env file
load_dotenv()

def generate_image(prompt: str, output_dir: str = "output/images") -> Optional[Dict[str, str]]:
    """
    Generate an image using Pollinations.AI image generation API.
    
    Args:
        prompt (str): Description of the image to generate
        output_dir (str): Directory to save the generated image
        
    Returns:
        Optional[Dict[str, str]]: Dictionary containing image path and alt text, or None if failed
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Prepare the API URL and parameters
        base_url = "https://image.pollinations.ai/prompt/"
        url = base_url + quote(f"{prompt}, high quality, 4k, photorealistic")
        params = {
            "model": "flux",
            "width": 1024,
            "height": 576,  # 16:9 aspect ratio for blog images
            "nologo": "true"
        }
        
        # Generate the image
        response = requests.get(url, params=params, stream=True)
        
        if response.status_code != 200:
            print(f"Failed to generate image: {response.status_code} - {response.text}")
            return None
        
        # Generate a filename based on the prompt
        safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt.lower()[:50])
        filename = f"{safe_prompt}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        image_path = os.path.join(output_dir, filename)
        
        # Save the image
        with open(image_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Generated image: {filename}")
        return {
            "path": image_path,
            "alt_text": prompt,
            "filename": filename
        }
        
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None

def generate_blog_content(topic: str, author: str = "Admin", api_key: str = None, generate_images: bool = True) -> Dict[str, Any]:
    """
    Generate a blog post using Gemini 2.5 Pro model.
    
    Args:
        topic (str): The topic for the blog post
        author (str, optional): Author name. Defaults to "Admin".
        api_key (str, optional): Google AI API key. If not provided, will try to load from .env.
        generate_images (bool, optional): Whether to generate images. Defaults to True.
        
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
    
    # Configure image generation model
    image_model = genai.GenerativeModel('gemini-2.5-pro-vision')
    
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
        
        # Generate images if enabled
        if generate_images:
            # Generate featured image
            featured_image_prompt = f"A high-quality featured image for a blog post about {topic}"
            featured_image = generate_image(featured_image_prompt)
            if featured_image:
                blog_data['featured_image'] = {
                    'url': f"images/{featured_image['filename']}",
                    'alt_text': f"Featured image for {blog_data.get('title', topic)}"
                }
            
            # Generate images for sections
            if 'content' in blog_data and 'sections' in blog_data['content']:
                for i, section in enumerate(blog_data['content']['sections']):
                    if 'heading' in section:
                        image_prompt = f"A high-quality image for a blog section about {section['heading']} in the context of {topic}"
                        section_image = generate_image(image_prompt)
                        if section_image:
                            section['image'] = {
                                'url': f"images/{section_image['filename']}",
                                'alt_text': f"Image showing {section['heading']}"
                            }
        
        return blog_data
        
    except Exception as e:
        print(f"Error generating blog content: {str(e)}")
        raise
