import os
import json
from typing import Optional
from openai import OpenAI

from week7_evaluation.day1_evaluation_framework.config import EVALUATION_MODEL
from .prompts import LLM_JUDGE_SYSTEM_PROMPT, build_judge_user_prompt
from .models import LLMJudgeResult

class LLMJudgeEngine:
    """
    Core LLM Engine for evaluating tutor responses.
    Reuses the OpenAI client pattern established in Week 4.
    """
    
    def __init__(self):
        # We reuse the Groq API key set up in earlier weeks.
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url="https://api.groq.com/openai/v1")
        else:
            self.client = None
            
    def evaluate(self, 
                 student_code: str, 
                 expected_error: str, 
                 expected_behaviour: str, 
                 tutor_response: str) -> Optional[LLMJudgeResult]:
        """
        Calls the LLM with the structured rubrics to evaluate the response.
        """
        if not self.client:
            print("Warning: GROQ_API_KEY not found. Skipping LLM Judge evaluation.")
            return None
            
        user_prompt = build_judge_user_prompt(
            student_code=student_code,
            expected_error=expected_error,
            expected_behaviour=expected_behaviour,
            tutor_response=tutor_response
        )
        
        try:
            # We enforce json_object response format to guarantee structured data
            response = self.client.chat.completions.create(
                model=EVALUATION_MODEL,
                messages=[
                    {"role": "system", "content": LLM_JUDGE_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            result_dict = json.loads(result_text)
            return LLMJudgeResult.from_dict(result_dict)
            
        except Exception as e:
            print(f"LLM Judge Engine Error: {e}")
            return None
