import os
import json
import time
import random
from typing import Dict, List, Optional, Tuple
import requests
import re
from urllib.parse import quote, urlparse, parse_qs
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# User agents for web requests
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
]

def get_random_user_agent() -> str:
    """Return a random user agent string."""
    return random.choice(USER_AGENTS)

def make_request(url: str, max_retries: int = 3) -> Optional[str]:
    """Make an HTTP request with retries and random delays."""
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
    }
    
    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(1, 3))  # Random delay between requests
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Request failed after {max_retries} attempts: {e}")
                return None
            time.sleep(2 ** attempt)  # Exponential backoff

class KeywordResearcher:
    """
    A class to find low competition keywords related to a given topic.
    Uses a combination of web scraping and Gemini API for analysis.
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the KeywordResearcher with optional API key."""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found. Using basic keyword research only.")
        else:
            genai.configure(api_key=self.api_key)
    
    def get_google_suggestions(self, query: str) -> List[str]:
        """Get search suggestions from Google's autocomplete."""
        try:
            url = f"https://suggestqueries.google.com/complete/search?q={quote(query)}&client=chrome"
            response = requests.get(url, headers={'User-Agent': get_random_user_agent()}, timeout=5)
            response.raise_for_status()
            return [s for s in response.json()[1] if s.lower() != query.lower()][:10]
        except Exception as e:
            print(f"Error getting Google suggestions: {e}")
            return []
    
    def get_related_searches(self, query: str) -> List[str]:
        """Extract related searches from Google search results."""
        try:
            url = f"https://www.google.com/search?q={quote(query)}&gl=us"
            html = make_request(url)
            if not html:
                return []
                
            soup = BeautifulSoup(html, 'html.parser')
            related = []
            
            # Find 'People also ask' section
            for div in soup.find_all('div', {'class': ['related-question-pair', 'Lt3Tzc']}):
                related.append(div.get_text(strip=True))
                
            # Find 'Searches related to' section
            related_div = soup.find('div', {'class': 'e2BEnf U7izfe'})
            if related_div:
                for a in related_div.find_all('a'):
                    related.append(a.get_text(strip=True))
                    
            return list(set(related))[:10]  # Remove duplicates and limit to 10
            
        except Exception as e:
            print(f"Error getting related searches: {e}")
            return []
    
    def analyze_competition_metrics(self, keyword: str) -> Dict[str, float]:
        """Analyze competition metrics without using API."""
        try:
            # Check keyword length (shorter often means more competitive)
            length_score = min(1.0, len(keyword.split()) / 5.0)  # 0-1, higher is better
            
            # Check for commercial intent (more commercial = more competitive)
            commercial_terms = ['buy', 'cheap', 'discount', 'best', 'review', 'price']
            commercial_score = 1.0 - (sum(1 for term in commercial_terms if term in keyword.lower()) / 3.0)
            
            # Check for question keywords (questions often have lower competition)
            question_terms = ['how', 'what', 'why', 'when', 'where', 'which', 'can', 'are', 'do']
            question_bonus = 0.2 if any(term in keyword.lower().split() for term in question_terms) else 0.0
            
            # Calculate final score (0-1, higher is better)
            competition_score = (length_score * 0.3) + (commercial_score * 0.5) + question_bonus
            
            return {
                'competition_score': max(0.1, min(0.9, 1.0 - competition_score)),  # Invert to match previous scale
                'confidence': 0.8  # High confidence in our metrics
            }
            
        except Exception as e:
            print(f"Error in competition analysis: {e}")
            return {'competition_score': 0.5, 'confidence': 0.5}
    
    def refine_with_gemini(self, topic: str, candidates: List[Dict[str, any]]) -> Dict[str, any]:
        """Use Gemini to select the best keyword from pre-filtered candidates."""
        if not self.api_key or not candidates:
            return candidates[0] if candidates else {'keyword': topic, 'competition_score': 0.5, 'confidence': 0.7, 'reason': 'No API key or candidates available'}
        
        try:
            model = genai.GenerativeModel('gemini-2.5-pro')
            
            # Format candidates for the prompt
            candidates_text = '\n'.join(
                f"- {k['keyword']} (Competition: {k['competition_score']:.2f})" 
                for k in candidates[:5]
            )
            
            prompt = f"""
            You are an expert SEO analyst. Select the best keyword from the list below that:
            1. Best represents the topic: "{topic}"
            2. Has the lowest competition score
            3. Has good search volume potential
            
            Candidates (with competition scores, lower is better):
            {candidates_text}
            
            Return a valid JSON object with these exact keys:
            {{
                "best_keyword": "the selected keyword",
                "reason": "brief explanation of your choice",
                "confidence": 0.0  // your confidence in this choice (0-1)
            }}
            
            Only return the JSON object, nothing else.
            """
            
            # Generate the response
            response = model.generate_content(prompt)
            
            # Extract text from the response
            response_text = response.text.strip()
            
            # Clean the response to extract just the JSON
            try:
                # Try to find JSON in the response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    response_text = response_text[json_start:json_end]
                
                # Parse the JSON
                result = json.loads(response_text)
                
                # Find the selected keyword in our candidates
                selected_keyword = result.get('best_keyword', '')
                selected = next(
                    (k for k in candidates if k['keyword'].lower() == selected_keyword.lower()),
                    candidates[0]  # Default to first candidate if not found
                )
                
                return {
                    'keyword': selected['keyword'],
                    'competition_score': selected['competition_score'],
                    'confidence': float(result.get('confidence', 0.7)),
                    'reason': result.get('reason', 'Selected based on analysis')
                }
                
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not parse Gemini response: {e}")
                print(f"Response was: {response_text}")
                # Fall back to the candidate with lowest competition score
                return candidates[0]
            
        except Exception as e:
            print(f"Error refining with Gemini: {e}")
            return candidates[0] if candidates else {'keyword': topic, 'competition_score': 0.5, 'confidence': 0.0}
    
    def find_best_keyword(self, topic: str, num_keywords: int = 15) -> Dict[str, any]:
        """
        Find the best low competition keyword related to the given topic.
        Uses web scraping first, then Gemini for final selection.
        """
        print(f"\n🔍 Researching low competition keywords for: {topic}")
        
        # Step 1: Get keyword candidates from multiple sources
        candidates = set()
        
        # Get Google autocomplete suggestions
        suggestions = self.get_google_suggestions(topic)
        candidates.update(suggestions)
        
        # Add common variations
        common_suffixes = ["for beginners", "guide", "tips", "tricks", "how to", "best", "review"]
        for suffix in common_suffixes:
            candidates.add(f"{topic} {suffix}")
        
        # Add question variations
        for q in ['how', 'what', 'why', 'when', 'where', 'which', 'can', 'are', 'do']:
            if q not in topic.lower():
                candidates.add(f"{q} {topic}")
        
        # Get related searches
        related = self.get_related_searches(topic)
        candidates.update(related)
        
        # Convert to list and limit to num_keywords
        candidates = list(candidates)[:num_keywords]
        
        if not candidates:
            print("No suitable keywords found. Using the original topic.")
            return {
                'keyword': topic,
                'competition_score': 0.5,
                'confidence': 0.0,
                'related_keywords': []
            }
        
        # Analyze competition for each candidate
        keyword_analysis = []
        for keyword in candidates:
            metrics = self.analyze_competition_metrics(keyword)
            keyword_analysis.append({
                'keyword': keyword,
                'competition_score': metrics['competition_score'],
                'confidence': metrics['confidence']
            })
        
        # Sort by competition score (ascending) and confidence (descending)
        keyword_analysis.sort(key=lambda x: (x['competition_score'], -x['confidence']))
        
        # Use Gemini to refine the top candidates (if API key is available)
        best_keyword = self.refine_with_gemini(topic, keyword_analysis[:5])
        
        # Get related keywords (excluding the best one)
        related_keywords = [
            k['keyword'] for k in keyword_analysis 
            if k['keyword'] != best_keyword['keyword']
        ][:4]  # Limit to 4 related keywords
        
        print(f"✅ Best keyword found: {best_keyword['keyword']} (Competition: {best_keyword['competition_score']:.2f})")
        
        return {
            'keyword': best_keyword['keyword'],
            'competition_score': best_keyword['competition_score'],
            'confidence': best_keyword.get('confidence', 0.7),
            'related_keywords': related_keywords,
            'reason': best_keyword.get('reason', 'Selected based on analysis')
        }

def get_keyword_researcher() -> Optional[KeywordResearcher]:
    """Helper function to create a KeywordResearcher instance."""
    try:
        return KeywordResearcher()
    except ValueError as e:
        print(f"⚠️ Keyword research disabled: {str(e)}")
        return None
