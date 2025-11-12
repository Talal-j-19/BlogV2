import json
from datetime import datetime
from typing import Dict, List, Optional

class StructuredDataGenerator:
    """
    A class to generate structured data (JSON-LD) for better SEO.
    """
    
    @staticmethod
    def generate_article_schema(
        title: str,
        description: str,
        url: str,
        published_date: str,
        modified_date: Optional[str] = None,
        author_name: str = "Admin",
        publisher_name: str = "Your Blog Name",
        publisher_logo: str = "https://yourblog.com/logo.png",
        image_url: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        word_count: Optional[int] = None
    ) -> str:
        """
        Generate Article schema.org JSON-LD markup.
        
        Args:
            title: Article title
            description: Article description/meta description
            url: Canonical URL of the article
            published_date: ISO format date string (YYYY-MM-DD)
            modified_date: ISO format date string (YYYY-MM-DD), defaults to published_date
            author_name: Name of the author
            publisher_name: Name of the publisher
            publisher_logo: URL to publisher's logo
            image_url: URL of the article's featured image
            keywords: List of relevant keywords
            word_count: Estimated word count of the article
            
        Returns:
            str: JSON-LD script tag with article schema
        """
        if modified_date is None:
            modified_date = published_date
            
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": description,
            "url": url,
            "datePublished": published_date,
            "dateModified": modified_date,
            "author": {
                "@type": "Person",
                "name": author_name
            },
            "publisher": {
                "@type": "Organization",
                "name": publisher_name,
                "logo": {
                    "@type": "ImageObject",
                    "url": publisher_logo
                }
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": url
            }
        }
        
        if image_url:
            schema["image"] = image_url
            
        if keywords:
            schema["keywords"] = ", ".join(keywords)
            
        if word_count:
            schema["wordCount"] = word_count
            
        return f"""<script type="application/ld+json">
{json.dumps(schema, indent=2, ensure_ascii=False)}
</script>"""
    
    @staticmethod
    def generate_breadcrumb_schema(
        items: List[Dict[str, str]],
        home_url: str = "https://yourblog.com",
        home_name: str = "Home"
    ) -> str:
        """
        Generate BreadcrumbList schema.org JSON-LD markup.
        
        Args:
            items: List of dicts with 'name' and 'url' for each breadcrumb
            home_url: URL of the homepage
            home_name: Display name for the homepage
            
        Returns:
            str: JSON-LD script tag with breadcrumb schema
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": []
        }
        
        # Add home as first item
        schema["itemListElement"].append({
            "@type": "ListItem",
            "position": 1,
            "name": home_name,
            "item": home_url
        })
        
        # Add other items
        for i, item in enumerate(items, 2):
            schema["itemListElement"].append({
                "@type": "ListItem",
                "position": i,
                "name": item['name'],
                "item": item['url']
            })
            
        return f"""<script type="application/ld+json">
{json.dumps(schema, indent=2, ensure_ascii=False)}
</script>"""
    
    @staticmethod
    def generate_faq_schema(questions: List[Dict[str, str]]) -> str:
        """
        Generate FAQPage schema.org JSON-LD markup.
        
        Args:
            questions: List of dicts with 'question' and 'answer' keys
            
        Returns:
            str: JSON-LD script tag with FAQ schema
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": []
        }
        
        for qa in questions:
            schema["mainEntity"].append({
                "@type": "Question",
                "name": qa['question'],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": qa['answer']
                }
            })
            
        return f"""<script type="application/ld+json">
{json.dumps(schema, indent=2, ensure_ascii=False)}
</script>"""

# Helper function
def get_structured_data_generator() -> StructuredDataGenerator:
    """Helper function to create a StructuredDataGenerator instance."""
    return StructuredDataGenerator()
