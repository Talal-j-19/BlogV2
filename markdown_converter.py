import os
import re
from datetime import datetime
from typing import Any, Dict, List
import json
from urllib.parse import urljoin

from structured_data import StructuredDataGenerator


def flatten_content(content: Any) -> str:
    """Flatten nested blog content structures into a plain text string."""
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        parts = [flatten_content(value) for value in content.values()]
        return "\n".join(part for part in parts if part)
    if isinstance(content, list):
        parts = [flatten_content(item) for item in content]
        return "\n".join(part for part in parts if part)
    return str(content) if content is not None else ""


def count_words(text: Any) -> int:
    """Count the number of words in a text-like structure."""
    flattened = flatten_content(text)
    return len(re.findall(r'\w+', flattened))


def generate_toc(headers: List[Dict[str, str]]) -> str:
    """Generate a table of contents from headers."""
    if not headers:
        return ""
    
    toc = "## Table of Contents\n\n"
    for header in headers:
        indent = '  ' * (header['level'] - 2)  # Start from h2
        toc += f"{indent}- [{header['text']}](#{header['anchor']})\n"
    return toc + "\n"


def extract_headers(content: str) -> List[Dict[str, str]]:
    """Extract headers from markdown content."""
    headers = []
    for line in content.split('\n'):
        if line.startswith('## '):
            level = 2
            text = line[3:].strip()
        elif line.startswith('### '):
            level = 3
            text = line[4:].strip()
        elif line.startswith('#### '):
            level = 4
            text = line[5:].strip()
        else:
            continue
            
        # Create anchor (simple version, could be improved)
        anchor = text.lower().replace(' ', '-')
        anchor = re.sub(r'[^\w-]', '', anchor)
        headers.append({
            'level': level,
            'text': text,
            'anchor': anchor
        })
    return headers


def add_anchor_ids(content: str) -> str:
    """Add IDs to headers for anchor linking."""
    if not isinstance(content, str):
        content = flatten_content(content)

    lines = content.split('\n')
    result = []
    
    for line in lines:
        if line.startswith('## '):
            anchor = line[3:].lower().replace(' ', '-')
            anchor = re.sub(r'[^\w-]', '', anchor)
            result.append(f"{line} {{#{anchor}}}")
        else:
            result.append(line)
            
    return '\n'.join(result)


def convert_to_markdown(blog_data: Dict[str, Any], output_dir: str = "output") -> str:
    """
    Convert blog data from JSON to Markdown format with enhanced structure and SEO.
    
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
    
    # Extract content for word count and header analysis
    raw_content = blog_data.get('content', '')
    word_count = count_words(flatten_content(raw_content))
    
    # Prepare front matter with enhanced metadata
    front_matter = "---\n"
    front_matter += f"title: {blog_data.get('title', '')}\n"
    front_matter += f"date: {blog_data.get('publication_date', datetime.now().strftime('%Y-%m-%d'))}\n"
    front_matter += f"lastmod: {datetime.now().strftime('%Y-%m-%d')}\n"
    front_matter += f"author: {blog_data.get('author', '')}\n"
    # Add categories and tags if they exist
    categories = blog_data.get('categories', [])
    if categories:
        front_matter += f"categories: {json.dumps(categories)}\n"
    
    tags = blog_data.get('tags', [])
    if tags:
        front_matter += f"tags: {json.dumps(tags)}\n"
    
    # Add slug and description
    front_matter += f"slug: {blog_data.get('slug', safe_title.lower().replace('_', '-'))}\n"
    meta_description = blog_data.get('meta_description', '')
    if not meta_description and 'excerpt' in blog_data:
        meta_description = blog_data['excerpt']
    front_matter += f"description: {meta_description}\n"
    
    # Add featured image if exists
    if 'featured_image' in blog_data and blog_data['featured_image'].get('url'):
        front_matter += f"image: {blog_data['featured_image']['url']}\n"
        alt_text = blog_data['featured_image'].get('alt_text', '')
        if not alt_text and 'title' in blog_data['featured_image']:
            alt_text = blog_data['featured_image']['title']
        if alt_text:
            front_matter += f"image_alt: {alt_text}\n"
    
    # Add reading time estimate (assuming 200 words per minute)
    reading_time = max(1, round(word_count / 200))
    front_matter += f"reading_time: {reading_time}\n"
    
    front_matter += "---\n\n"
    
    # Process main content
    main_content = blog_data.get('content', {})
    content_parts = []
    
    # Handle introduction if it exists
    if isinstance(main_content, dict) and 'introduction' in main_content:
        intro_text = flatten_content(main_content['introduction'])
        if intro_text:
            content_parts.append(f"## Introduction\n\n{intro_text}")
    
    # Handle sections if they exist
    if isinstance(main_content, dict) and 'sections' in main_content and isinstance(main_content['sections'], list):
        for section in main_content['sections']:
            if not isinstance(section, dict):
                continue
                
            # Add section heading if it exists
            heading = flatten_content(section.get('heading', ''))
            if heading:
                content_parts.append(f"## {heading}")
            
            # Add section content if it exists
            if 'content' in section and section['content']:
                section_text = flatten_content(section['content'])
                if section_text:
                    content_parts.append(section_text)
    
    # If no content was processed, use the entire content as a string
    if not content_parts and main_content:
        content = str(main_content)
    else:
        content = '\n\n'.join(content_parts)
    
    # Process content to extract headers and add anchor IDs
    content = add_anchor_ids(content)
    headers = extract_headers(content)
    
    # Generate structured data
    structured_data = ""
    try:
        base_url = "https://yourblog.com"  # Replace with your actual blog URL
        post_url = urljoin(base_url, f"posts/{blog_data.get('slug', '')}")
        
        # Article schema
        schema_generator = StructuredDataGenerator()
        
        # Generate article schema
        article_schema = schema_generator.generate_article_schema(
            title=blog_data.get('title', ''),
            description=meta_description,
            url=post_url,
            published_date=blog_data.get('publication_date', datetime.now().strftime('%Y-%m-%d')),
            author_name=blog_data.get('author', ''),
            publisher_name="Your Blog Name",  # Replace with your blog name
            publisher_logo=urljoin(base_url, "images/logo.png"),
            image_url=blog_data.get('featured_image', {}).get('url', ''),
            keywords=tags,
            word_count=word_count
        )
        
        # Generate breadcrumb schema
        breadcrumb_items = [
            {"name": "Blog", "url": urljoin(base_url, "blog/")},
            {"name": blog_data.get('title', 'Post'), "url": post_url}
        ]
        breadcrumb_schema = schema_generator.generate_breadcrumb_schema(breadcrumb_items, home_url=base_url)
        
        # Combine all structured data
        structured_data = f"""
<!-- Structured Data -->
{article_schema}
{breadcrumb_schema}
"""
    except Exception as e:
        print(f"Warning: Could not generate structured data: {e}")
    
    # Start building markdown content
    markdown_content = front_matter
    
    # Add structured data
    markdown_content += structured_data
    
    # Add title as H1
    markdown_content += f"# {blog_data.get('title', '')}\n\n"
    
    # Add featured image if exists
    if 'featured_image' in blog_data and blog_data['featured_image'].get('url'):
        alt_text = blog_data['featured_image'].get('alt_text', '')
        if not alt_text and 'title' in blog_data['featured_image']:
            alt_text = blog_data['featured_image']['title']
        if not alt_text:
            alt_text = blog_data.get('title', 'Featured image')
            
        markdown_content += f"![{alt_text}]({blog_data['featured_image']['url']})\n\n"
    
    # Add meta description as introduction if available
    if meta_description:
        markdown_content += f"> {meta_description}\n\n"
    
    # Add table of contents if there are headers
    if headers:
        markdown_content += generate_toc(headers) + "\n"
    
    # Add the main content
    markdown_content += content + "\n\n"
    
    # Add FAQ section if exists
    if isinstance(blog_data.get('content'), dict) and 'faq' in blog_data['content']:
        faqs = blog_data['content']['faq']
        if isinstance(faqs, list) and faqs:
            markdown_content += "## Frequently Asked Questions\n\n"
            for i, faq in enumerate(faqs, 1):
                if isinstance(faq, dict):
                    question = flatten_content(faq.get('question', f'Question {i}'))
                    answer = flatten_content(faq.get('answer', ''))
                    if question:
                        markdown_content += f"### {question}\n\n{answer}\n\n"

    # Add conclusion if exists
    if isinstance(blog_data.get('content'), dict) and 'conclusion' in blog_data['content']:
        conclusion_text = flatten_content(blog_data['content']['conclusion'])
        if conclusion_text:
            markdown_content += "## Conclusion\n\n"
            markdown_content += f"{conclusion_text}\n\n"
    
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
