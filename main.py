import os
import json
import sys
from datetime import datetime
from blog_generator import generate_blog_content
from markdown_converter import convert_to_markdown

def save_blog_to_file(blog_data: dict, output_dir: str = "output") -> str:
    """
    Save the generated blog content to a JSON file.
    
    Args:
        blog_data (dict): The blog content to save
        output_dir (str, optional): Directory to save the file. Defaults to "output".
        
    Returns:
        str: Path to the saved file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a filename from the blog title
    safe_title = "".join(c if c.isalnum() else "_" for c in blog_data.get('title', 'blog_post'))
    filename = f"{safe_title.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Save to file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(blog_data, f, indent=2, ensure_ascii=False)
    
    return filepath

def generate_blog():
    """Generate a new blog post and convert it to markdown."""
    try:
        # Get blog topic from user
        topic = input("Enter the blog topic: ")
        author = input("Enter author name (or press Enter for default): ").strip() or "Admin"
        
        # Generate blog content
        print(f"\nGenerating blog post about: {topic}")
        blog_content = generate_blog_content(topic, author)
        
        # Save JSON file
        json_path = save_blog_to_file(blog_content)
        print(f"\n✅ Blog post generated successfully!")
        
        # Convert to markdown
        markdown_path = convert_to_markdown(blog_content)
        
        # Print summary
        print("\n--- Blog Post Summary ---")
        print(f"Title: {blog_content.get('title')}")
        print(f"Author: {blog_content.get('author')}")
        print(f"Word Count: ~{len(str(blog_content).split())}")
        print(f"\n📄 JSON file saved to: {os.path.abspath(json_path)}")
        print(f"📝 Markdown file saved to: {os.path.abspath(markdown_path)}")
        
        return json_path, markdown_path
        
    except ValueError as e:
        print(f"\n❌ Configuration error: {str(e)}")
        print("Please make sure you have a .env file with GEMINI_API_KEY set or pass it as an argument.")
        return None, None
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        return None, None

def convert_existing_blog(json_file: str):
    """Convert an existing blog JSON file to markdown."""
    try:
        if not os.path.exists(json_file):
            print(f"Error: File not found: {json_file}")
            return None
            
        print(f"Converting {json_file} to markdown...")
        markdown_path = convert_to_markdown(json.load(open(json_file, 'r', encoding='utf-8')))
        print(f"✅ Markdown file saved to: {os.path.abspath(markdown_path)}")
        return markdown_path
    except Exception as e:
        print(f"❌ Error converting file: {str(e)}")
        return None

def print_help():
    """Print help information."""
    print("\nBlog Generator - Usage:")
    print("  python main.py           - Generate a new blog post")
    print("  python main.py convert <path_to_json>  - Convert existing JSON to markdown")
    print("  python main.py help     - Show this help message\n")

def main():
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'convert':
        if len(sys.argv) < 3:
            print("Error: Please provide the path to a JSON file to convert.")
            print_help()
            return
        convert_existing_blog(sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1].lower() == 'help':
        print_help()
    else:
        generate_blog()

if __name__ == "__main__":
    main()
