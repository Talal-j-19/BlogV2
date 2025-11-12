import requests
import json
import time

def test_generate_blog():
    """Test the blog generation endpoint"""
    # url = "http://localhost:8000/api/v1/generate"
    url = "http://161.35.235.101:8001/api/v1/generate"
    
    # Test data
    payload = {
        "topic": "Best Cars Released in 2025",
        "author": "Talal",
        "generate_images": False,
        "find_keywords": False,
        "return_markdown": True
    }
    
    print("🚀 Testing blog generation...")
    try:
        response = requests.post(url, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Get the filename from headers if available
            filename = response.headers.get('X-File-Name', 'blog_post.md')
            
            # Save the markdown content to a file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"✅ Blog generated successfully!")
            print(f"📄 Saved as: {filename}")
            print(f"📝 Title: {response.headers.get('X-Title', 'N/A')}")
            print(f"⏱️  Generated at: {response.headers.get('X-Generated-At', 'N/A')}")
            
            # Return the filename for further testing
            return filename
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        return None

def test_list_blogs():
    """Test the blog listing endpoint"""
    url = "http://161.35.235.101:8001/api/v1/generate"
    
    print("\n📋 Listing all generated blogs...")
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                blogs = data.get('data', [])
                print(f"Found {len(blogs)} blog(s):")
                for i, blog in enumerate(blogs, 1):
                    print(f"\n{i}. {blog.get('title', 'Untitled')}")
                    print(f"   📁 {blog.get('filename')}")
                    print(f"   📅 Created: {blog.get('created_at')}")
                    print(f"   📊 Size: {blog.get('size_kb')} KB")
                return blogs
            else:
                print(f"❌ Error in response: {data.get('message', 'Unknown error')}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        return None

def test_get_blog_content(filename):
    """Test getting the content of a specific blog"""
    if not filename:
        print("❌ No filename provided")
        return
        
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print(f"\n📄 Content of {filename} (first 200 chars):")
        print("-" * 50)
        print(content[:200] + "...")
        print("-" * 50)
        return content
        
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return None

if __name__ == "__main__":
    print("🔍 Starting API tests...\n")
    
    # Test 1: Generate a new blog
    print("=" * 50)
    print("TEST 1: Generate a new blog post")
    print("=" * 50)
    filename = test_generate_blog()
    
    # Wait a moment for the file to be written
    time.sleep(1)
    
    # Test 2: List all blogs
    print("\n" + "=" * 50)
    print("TEST 2: List all blog posts")
    print("=" * 50)
    test_list_blogs()
    
    # Test 3: Display blog content
    if filename:
        print("\n" + "=" * 50)
        print("TEST 3: Display blog content")
        print("=" * 50)
        test_get_blog_content(filename)
    
    print("\n✅ All tests completed!")
