import os
from datetime import datetime
from typing import Dict, Any
import json

def convert_to_markdown(blog_data: Dict[str, Any], output_dir: str = "output") -> str:
    """
    Convert blog data from JSON to Markdown format.
    
    Args:
        blog_data (Dict[str, Any]): Blog content in dictionary format
        output_dir (str, optional): Directory to save the markdown file. Defaults to "output".
        
    Returns:
        str: Path to the generated markdown file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a filename from the blog title
    safe_title = "".join(c if c.isalnum() else "_" for c in blog_data.get('title', 'blog_post'))
    filename = f"{safe_title.lower().replace(' ', '_')}.md"
    filepath = os.path.join(output_dir, filename)
    
    # Prepare front matter
    front_matter = "---\n"
    front_matter += f"title: {blog_data.get('title', '')}\n"
    front_matter += f"date: {blog_data.get('publication_date', '')}\n"
    front_matter += f"author: {blog_data.get('author', '')}\n"
    front_matter += f"categories: {', '.join(blog_data.get('categories', []))}\n"
    front_matter += f"tags: {', '.join(blog_data.get('tags', []))}\n"
    front_matter += f"slug: {blog_data.get('slug', '')}\n"
    front_matter += f"description: {blog_data.get('meta_description', '')}\n"
    
    # Add featured image if exists
    if 'featured_image' in blog_data and blog_data['featured_image'].get('url'):
        front_matter += f"image: {blog_data['featured_image']['url']}\n"
        front_matter += f"image_alt: {blog_data['featured_image'].get('alt_text', '')}\n"
    
    front_matter += "---\n\n"
    
    # Start building markdown content
    markdown_content = front_matter
    
    # Add title as H1
    markdown_content += f"# {blog_data.get('title', '')}\n\n"
    
    # Add introduction
    if 'content' in blog_data and 'introduction' in blog_data['content']:
        markdown_content += f"{blog_data['content']['introduction']}\n\n"
    
    # Add sections
    if 'content' in blog_data and 'sections' in blog_data['content']:
        for section in blog_data['content']['sections']:
            markdown_content += f"## {section.get('heading', '')}\n\n"
            # Check if content is a list or plain text
            if isinstance(section.get('content'), list):
                for item in section['content']:
                    markdown_content += f"- {item}\n"
                markdown_content += "\n"
            else:
                markdown_content += f"{section.get('content', '')}\n\n"
    
    # Add FAQ section if exists
    if 'content' in blog_data and 'faq' in blog_data['content'] and blog_data['content']['faq']:
        markdown_content += "## Frequently Asked Questions\n\n"
        for faq in blog_data['content']['faq']:
            markdown_content += f"### {faq.get('question', '')}\n\n"
            markdown_content += f"{faq.get('answer', '')}\n\n"
    
    # Add conclusion if exists
    if 'content' in blog_data and 'conclusion' in blog_data['content']:
        markdown_content += "## Conclusion\n\n"
        markdown_content += f"{blog_data['content']['conclusion']}\n\n"
    
    # Add SEO metadata as HTML comments
    if 'seo' in blog_data:
        markdown_content += "\n<!-- SEO Metadata -->\n"
        markdown_content += f"<!-- Focus Keyword: {blog_data['seo'].get('focus_keyword', '')} -->\n"
        markdown_content += f"<!-- Word Count: {blog_data['seo'].get('word_count', '')} -->\n"
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return filepath

def json_to_markdown(json_file: str, output_dir: str = "output") -> str:
    """
    Convert a JSON file containing blog data to a Markdown file.
    
    Args:
        json_file (str): Path to the JSON file containing blog data
        output_dir (str, optional): Directory to save the markdown file. Defaults to "output".
        
    Returns:
        str: Path to the generated markdown file
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        blog_data = json.load(f)
    
    return convert_to_markdown(blog_data, output_dir)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python markdown_converter.py <path_to_json_file> [output_directory]")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    
    try:
        output_path = json_to_markdown(json_file, output_dir)
        print(f"Successfully converted to Markdown: {output_path}")
    except Exception as e:
        print(f"Error converting to Markdown: {str(e)}")
        sys.exit(1)
