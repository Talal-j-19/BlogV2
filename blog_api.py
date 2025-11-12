from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
from datetime import datetime

# Add current directory to path to import local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import the blog generator and converter
try:
    from blog_generator import generate_blog_content
    from markdown_converter import convert_to_markdown
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    raise

# Initialize FastAPI app
app = FastAPI(
    title="Blog Generation API",
    description="API for generating blog posts with SEO optimization",
    version="1.0.0"
)

# CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class BlogRequest(BaseModel):
    topic: str
    author: str = "Admin"
    generate_images: bool = False
    find_keywords: bool = False
    return_markdown: bool = True

@app.post("/api/v1/generate")
async def generate_blog(blog_request: BlogRequest):
    """
    Generate a blog post based on the provided topic.
    
    - **topic**: The main topic of the blog post (required)
    - **author**: Author name (default: "Admin")
    - **generate_images**: Whether to generate images (default: False)
    - **find_keywords**: Whether to find low competition keywords (default: False)
    - **return_markdown**: Whether to return markdown content directly (default: True)
    """
    try:
        # Generate blog content
        blog_data = generate_blog_content(
            topic=blog_request.topic,
            author=blog_request.author,
            generate_images=blog_request.generate_images,
            keyword_data={"find_keywords": blog_request.find_keywords}
        )
        
        # Ensure output directory exists
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() else "_" for c in blog_data.get('title', 'blog_post'))
        filename = f"{safe_title.lower()}_{timestamp}.md"
        
        # Convert to markdown
        markdown_content = convert_to_markdown(blog_data, output_dir)
        
        # Save the markdown file
        markdown_path = os.path.join(output_dir, filename)
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # If return_markdown is True, return the markdown content directly
        if blog_request.return_markdown:
            return Response(
                content=markdown_content,
                media_type="text/markdown",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "X-File-Name": filename,
                    "X-Title": blog_data.get("title", ""),
                    "X-Generated-At": datetime.now().isoformat()
                }
            )
        
        # Otherwise return JSON response
        return {
            "status": "success",
            "message": "Blog post generated successfully",
            "data": {
                "title": blog_data.get("title", ""),
                "slug": blog_data.get("slug", ""),
                "markdown_path": markdown_path,
                "markdown_content": markdown_content,
                "metadata": {
                    "author": blog_request.author,
                    "generated_at": datetime.now().isoformat(),
                    "word_count": len(markdown_content.split())
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating blog post: {str(e)}"
        )

@app.get("/api/v1/list")
async def list_generated_blogs():
    """List all generated blog posts"""
    try:
        output_dir = "output"
        if not os.path.exists(output_dir):
            return {"status": "success", "data": []}
            
        blogs = []
        for filename in os.listdir(output_dir):
            if filename.endswith(".md"):
                file_path = os.path.join(output_dir, filename)
                stats = os.stat(file_path)
                
                # Read the first few lines to get the title
                title = filename.replace("_", " ").replace(".md", "").title()
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                        if first_line.startswith('# '):
                            title = first_line[2:]
                except:
                    pass
                
                blogs.append({
                    "filename": filename,
                    "title": title,
                    "path": file_path,
                    "created_at": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                    "size_kb": round(stats.st_size / 1024, 2)
                })
                
        return {"status": "success", "data": sorted(blogs, key=lambda x: x["created_at"], reverse=True)}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing blog posts: {str(e)}"
        )

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Blog Generation API",
        "endpoints": {
            "generate_blog": {
                "method": "POST",
                "url": "/api/v1/generate",
                "description": "Generate a new blog post"
            },
            "list_blogs": {
                "method": "GET",
                "url": "/api/v1/list",
                "description": "List all generated blog posts"
            }
        },
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting server on http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    uvicorn.run("blog_api:app", host="0.0.0.0", port=8000, reload=True)
