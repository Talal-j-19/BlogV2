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

def generate_blog_content(topic: str, author: str = "Admin", api_key: str = None, 
                       generate_images: bool = True, keyword_data: dict = None) -> Dict[str, Any]:
    """
    Generate a blog post using Gemini 2.5 Pro model with SEO optimization.
    
    Args:
        topic (str): The topic for the blog post
        author (str, optional): Author name. Defaults to "Admin".
        api_key (str, optional): Google AI API key. If not provided, will try to load from .env.
        generate_images (bool, optional): Whether to generate images. Defaults to True.
        keyword_data (dict, optional): Dictionary containing keyword research data.
        
    Returns:
        Dict[str, Any]: Generated blog content in a structured format
        
    Raises:
        ValueError: If API key is not found
    """
    # Get API key from parameter or environment variable
    api_key = api_key or os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro')
    
    # Prepare SEO elements based on keyword research
    seo_keyword = keyword_data.get('keyword', topic) if keyword_data else topic
    seo_meta = f"""
    I'm writing a blog post about '{seo_keyword}'. 
    Please help me create SEO-optimized content that will rank well in search engines.
    
    SEO Requirements:
    - Primary keyword: {seo_keyword}
    - Secondary keywords: {', '.join(keyword_data.get('related_keywords', [])) if keyword_data and 'related_keywords' in keyword_data else 'N/A'}
    - Target audience: People searching for information about {seo_keyword}
    - Content should be informative, engaging, and well-structured
    - Include the primary keyword in the first paragraph
    - Use H2 and H3 headings appropriately
    - Write in a natural, conversational tone
    
    Please generate a comprehensive blog post with the following structure:
    1. An engaging introduction that includes the primary keyword
    2. Main content sections with H2 headings
    3. Sub-sections with H3 headings where appropriate
    4. A conclusion that summarizes the key points
    5. A FAQ section with 3-5 common questions and answers
    
    Make sure to:
    - Use the primary keyword in the first 100 words
    - Include variations of the keyword naturally
    - Write for humans first, search engines second
    - Keep paragraphs short and scannable
    - Use bullet points and numbered lists where appropriate
    - End with a call-to-action
    
    Here's the topic: {topic}
    """
    
    # Configure image generation model
    image_model = genai.GenerativeModel('gemini-2.5-pro-vision')
    
    # Create the prompt
    prompt = f"""
    {seo_meta}
    
    Format the response as a JSON object with these fields:
    - title: The blog post title (include the primary keyword: {seo_keyword})
    - meta_description: A compelling meta description under 160 characters with the primary keyword
    - slug: A URL-friendly version of the title
    - content: An object containing:
        - introduction: The opening paragraph that includes the primary keyword
        - sections: An array of sections, each with:
            - heading: The section heading (H2)
            - content: The section content (can be a string or array of strings)
        - conclusion: A summary or closing thoughts that reinforces the main points
        - faq: An array of 3-5 frequently asked questions with answers
    
    Make sure to naturally include the primary keyword and its variations throughout the content.
    """
    
    try:
        # Generate blog content with SEO optimization
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
