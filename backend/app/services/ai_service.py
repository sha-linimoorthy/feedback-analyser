# Gemini API integration

import os
import google.generativeai as genai
from typing import Dict
import re
from dotenv import load_dotenv

load_dotenv()

"""
Integrating Google Gemini AI to analyse the event feedback and generate structured sentiment insights

"""

class GeminiAIService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key = api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def analyze_feedback(self, feedback_data: list) -> Dict[str, str]:
        if not feedback_data:
            raise ValueError("No feedback data provided")
        
        # Construct prompt
        prompt = self._build_analysis_prompt(feedback_data)
        
        try:
            # Call Gemini API
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1000,
                )
            )
            
            # Parse response
            result = self._parse_ai_response(response.text)
            return result
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _build_analysis_prompt(self, feedback_data: list) -> str:
        """Build structured prompt for Gemini"""
        
        # Aggregate feedback
        total_responses = len(feedback_data)
        avg_rating = sum(f['rating'] for f in feedback_data) / total_responses
        comments = [f['comment'] for f in feedback_data if f.get('comment')]
        
        prompt = f"""You are an expert event feedback analyzer. Analyze the following attendee feedback and provide insights.

FEEDBACK DATA:
- Total Responses: {total_responses}
- Average Rating: {avg_rating:.2f}/5.0

ATTENDEE COMMENTS:
{self._format_comments(comments)}

Please provide your analysis in the following exact format:

OVERALL_SENTIMENT: [Choose ONLY one: Positive, Neutral, or Negative]

POSITIVE_HIGHLIGHTS:
[List the main positive aspects mentioned by attendees. If none, write "None mentioned"]

COMMON_COMPLAINTS:
[List recurring issues or complaints. If none, write "None mentioned"]

EXECUTIVE_SUMMARY:
[Provide a concise 2-3 sentence summary of the overall feedback]

Important:
- Be specific and data-driven
- Extract actual themes from the comments
- Keep each section concise
- Use the exact format headers shown above
"""
        return prompt
    
    def _format_comments(self, comments: list) -> str:
        """Format comments for the prompt"""
        if not comments:
            return "(No written comments provided)"
        
        formatted = []
        for i, comment in enumerate(comments[:50], 1):  
            formatted.append(f"{i}. {comment}")
        
        return "\n".join(formatted)
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, str]:
        """Parse AI response into structured format"""
        
        # Extract sections using regex
        sentiment_match = re.search(r'OVERALL_SENTIMENT:\s*(\w+)', response_text, re.IGNORECASE)
        highlights_match = re.search(r'POSITIVE_HIGHLIGHTS:(.*?)(?=COMMON_COMPLAINTS:|$)', response_text, re.DOTALL | re.IGNORECASE)
        complaints_match = re.search(r'COMMON_COMPLAINTS:(.*?)(?=EXECUTIVE_SUMMARY:|$)', response_text, re.DOTALL | re.IGNORECASE)
        summary_match = re.search(r'EXECUTIVE_SUMMARY:(.*?)$', response_text, re.DOTALL | re.IGNORECASE)
        
        # Validate and clean extracted data
        sentiment = sentiment_match.group(1).strip() if sentiment_match else "Neutral"
        if sentiment not in ["Positive", "Neutral", "Negative"]:
            sentiment = "Neutral"
        
        highlights = highlights_match.group(1).strip() if highlights_match else "No specific highlights mentioned"
        complaints = complaints_match.group(1).strip() if complaints_match else "No specific complaints mentioned"
        summary = summary_match.group(1).strip() if summary_match else "Analysis completed successfully"
        
        return {
            "overall_sentiment": sentiment,
            "positive_highlights": highlights[:1000],  
            "common_complaints": complaints[:1000],
            "executive_summary": summary[:1000]
        }
