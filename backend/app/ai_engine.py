"""
AI Engine for IssuePilot - Handles LLM interactions
Supports OpenAI and Google Gemini
"""

import logging
import os
from typing import Optional

import google.generativeai as genai
from openai import (
    APIError,
    AsyncOpenAI,
    AuthenticationError,
    BadRequestError,
    RateLimitError,
)

from .schemas import AnalysisResult, GitHubIssue
from .utils import clean_json_response, truncate_text

logger = logging.getLogger("issuepilot.ai")

# Valid models for OpenAI
VALID_OPENAI_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
]

# Valid models for Gemini
VALID_GEMINI_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
    "gemini-pro",
]


class AIEngineError(Exception):
    """Base exception for AI Engine errors"""

    pass


class APIKeyError(AIEngineError):
    """Raised when API key is missing or invalid"""

    pass


class RateLimitExceededError(AIEngineError):
    """Raised when rate limit is exceeded"""

    pass


class ModelError(AIEngineError):
    """Raised when model is invalid or unavailable"""

    pass


class ContextLengthError(AIEngineError):
    """Raised when context length is exceeded"""

    pass


class AIEngine:
    """AI Engine for analyzing GitHub issues"""

    SYSTEM_PROMPT = """You are a senior open-source maintainer with extensive experience in triaging and resolving GitHub issues. Your task is to analyze GitHub issues and provide:
1. Clear, concise summaries
2. Accurate root cause analysis
3. Actionable solution steps
4. Developer-friendly checklists
5. Appropriate label suggestions

Always be precise, helpful, and consider the contributor's perspective. Focus on making issues easier to understand and resolve."""

    USER_PROMPT_TEMPLATE = """Analyze the following GitHub issue and provide a structured analysis.

## Issue Title
{title}

## Issue Body
{body}

## Top Comments
{comments}

## Task
Analyze this issue and return a JSON object with the following structure:
{{
    "summary": "A clear 4-6 line summary of what this issue is about",
    "root_cause": "Your analysis of the likely root cause of this issue",
    "solution_steps": [
        "Step 1: ...",
        "Step 2: ...",
        "Step 3: ..."
    ],
    "checklist": [
        "Understand the issue context",
        "Set up development environment",
        "...",
        "..."
    ],
    "labels": ["bug", "enhancement"]
}}

Guidelines:
- Summary should be comprehensive but concise (4-6 lines)
- Root cause should be specific and technical
- Solution steps should be actionable and ordered (minimum 3 steps)
- Checklist should have 6-10 items for a developer to follow
- Labels must be from: bug, docs, enhancement, feature, question, good-first-issue, help-wanted, invalid, wontfix

Return ONLY valid JSON, no additional text."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
    ):
        """
        Initialize AI Engine

        Args:
            api_key: API key for AI provider
            model: Model to use for analysis
            provider: AI provider ('openai' or 'gemini')

        Raises:
            APIKeyError: If API key is not configured
            ModelError: If model is invalid
        """
        self.provider = provider or os.getenv("AI_PROVIDER", "openai")

        # Get appropriate API key based on provider
        if self.provider == "gemini":
            self.api_key = (
                api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            )
            self.model = model or os.getenv("MODEL", "gemini-2.0-flash")
            valid_models = VALID_GEMINI_MODELS
            key_name = "GEMINI_API_KEY"
            key_url = "https://aistudio.google.com/apikey"
        else:
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            self.model = model or os.getenv("MODEL", "gpt-4o-mini")
            valid_models = VALID_OPENAI_MODELS
            key_name = "OPENAI_API_KEY"
            key_url = "https://platform.openai.com/api-keys"

        # Validate API key
        if not self.api_key:
            raise APIKeyError(
                f"{self.provider.capitalize()} API key not configured. "
                f"Set {key_name} in your .env file or environment variables. "
                f"Get your API key at: {key_url}"
            )

        if len(self.api_key) < 20:
            raise APIKeyError(
                f"{self.provider.capitalize()} API key appears to be invalid (too short). "
                f"Please check your {key_name} configuration."
            )

        # Validate model
        if self.model not in valid_models:
            raise ModelError(
                f"Invalid model '{self.model}' for provider '{self.provider}'. "
                f"Valid models are: {', '.join(valid_models)}. "
                "Set MODEL in your .env file to use a different model."
            )

        logger.info(f"AI Engine initialized with {self.provider} model: {self.model}")

        # Initialize the appropriate client
        if self.provider == "gemini":
            genai.configure(api_key=self.api_key)
            self.gemini_model = genai.GenerativeModel(self.model)
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)

    def _build_prompt(self, issue: GitHubIssue) -> str:
        """
        Build the user prompt from issue data

        Args:
            issue: GitHub issue to analyze

        Returns:
            Formatted prompt string
        """
        # Truncate long content
        body = truncate_text(issue.body or "No description provided.", 3000)

        # Format comments
        if issue.comments:
            comments = "\n\n".join(
                [
                    f"Comment {i+1}:\n{truncate_text(comment, 500)}"
                    for i, comment in enumerate(issue.comments[:5])
                ]
            )
        else:
            comments = "No comments yet."

        return self.USER_PROMPT_TEMPLATE.format(
            title=issue.title, body=body, comments=comments
        )

    def get_provider_name(self) -> str:
        """Get the name of the AI provider being used"""
        return self.provider

    async def analyze_issue(self, issue: GitHubIssue) -> AnalysisResult:
        """
        Analyze a GitHub issue using AI

        Args:
            issue: GitHub issue to analyze

        Returns:
            AnalysisResult with structured analysis

        Raises:
            APIKeyError: If API key is invalid
            RateLimitExceededError: If rate limit is exceeded
            ContextLengthError: If input is too long
            AIEngineError: For other AI-related errors
        """
        prompt = self._build_prompt(issue)
        logger.debug(f"Analyzing issue: {issue.title[:50]}...")

        if self.provider == "gemini":
            return await self._analyze_with_gemini(prompt)
        else:
            return await self._analyze_with_openai(prompt)

    async def _analyze_with_gemini(self, prompt: str) -> AnalysisResult:
        """Analyze using Google Gemini"""
        try:
            full_prompt = f"{self.SYSTEM_PROMPT}\n\n{prompt}"

            # Use synchronous API in async context
            import asyncio

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.gemini_model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=2000,
                    ),
                ),
            )

            content = response.text
            result = clean_json_response(content)
            logger.debug("Gemini analysis completed successfully")

            return self._validate_result(result)

        except Exception as e:
            error_msg = str(e).lower()
            logger.error(f"Gemini API error: {e}")

            if "quota" in error_msg or "rate" in error_msg:
                raise RateLimitExceededError(
                    "Gemini rate limit exceeded. Please wait a moment and try again. "
                    "Tips: 1) Wait 20-60 seconds, 2) Check your quota at Google AI Studio."
                )
            elif "api key" in error_msg or "invalid" in error_msg:
                raise APIKeyError(
                    "Gemini API key is invalid or expired. "
                    "Please check your GEMINI_API_KEY and ensure it's active. "
                    "Get a new key at: https://aistudio.google.com/apikey"
                )
            else:
                raise AIEngineError(
                    f"Gemini API error: {str(e)}. "
                    "Please check your configuration and try again."
                )

    async def _analyze_with_openai(self, prompt: str) -> AnalysisResult:
        """Analyze using OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            result = clean_json_response(content)
            logger.debug("AI analysis completed successfully")

            # Validate and build result
            return self._validate_result(result)

        except AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {e}")
            raise APIKeyError(
                "OpenAI API key is invalid or expired. "
                "Please check your OPENAI_API_KEY and ensure it's active. "
                "Get a new key at: https://platform.openai.com/api-keys"
            )
        except RateLimitError as e:
            logger.warning(f"OpenAI rate limit exceeded: {e}")
            raise RateLimitExceededError(
                "OpenAI rate limit exceeded. Please wait a moment and try again. "
                "Tips: 1) Wait 20-60 seconds, 2) Upgrade your OpenAI plan, "
                "3) Use a different API key, 4) Reduce request frequency."
            )
        except BadRequestError as e:
            error_msg = str(e).lower()
            if "context_length" in error_msg or "maximum context" in error_msg:
                logger.error(f"Context length exceeded: {e}")
                raise ContextLengthError(
                    "The issue content is too long for the AI model. "
                    "Try analyzing a shorter issue or upgrade to a model with larger context."
                )
            logger.error(f"OpenAI bad request: {e}")
            raise AIEngineError(f"Invalid request to OpenAI: {str(e)}")
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise AIEngineError(
                f"OpenAI API error: {str(e)}. "
                "This may be a temporary issue. Please try again in a few moments."
            )
        except Exception as e:
            logger.error(f"Unexpected AI error: {e}")
            raise AIEngineError(
                f"Unexpected error during AI analysis: {str(e)}. "
                "Please check your configuration and try again."
            )

    def _validate_result(self, result: dict) -> AnalysisResult:
        """
        Validate and normalize AI response

        Args:
            result: Parsed JSON from AI response

        Returns:
            Validated AnalysisResult
        """
        # Ensure all required fields exist
        summary = result.get("summary", "Unable to generate summary.")
        root_cause = result.get("root_cause", "Unable to determine root cause.")

        # Ensure lists have proper content
        solution_steps = result.get("solution_steps", [])
        if not solution_steps or not isinstance(solution_steps, list):
            solution_steps = [
                "Review the issue description",
                "Investigate the codebase",
                "Implement a fix",
            ]

        checklist = result.get("checklist", [])
        if not checklist or not isinstance(checklist, list):
            checklist = [
                "Read and understand the issue",
                "Set up local development environment",
                "Reproduce the issue locally",
                "Identify affected files",
                "Implement the fix",
                "Write tests",
                "Submit PR",
            ]

        # Validate labels
        valid_labels = {
            "bug",
            "docs",
            "enhancement",
            "feature",
            "question",
            "good-first-issue",
            "help-wanted",
            "invalid",
            "wontfix",
        }
        labels = result.get("labels", [])
        if isinstance(labels, list):
            labels = [label for label in labels if label in valid_labels]
        else:
            labels = []

        if not labels:
            labels = ["bug"]  # Default label

        return AnalysisResult(
            summary=summary,
            root_cause=root_cause,
            solution_steps=solution_steps,
            checklist=checklist,
            labels=labels,
            similar_issues=[],
        )

    async def generate_pr_description(
        self, issue: GitHubIssue, analysis: AnalysisResult
    ) -> str:
        """
        Generate a PR description based on issue analysis

        Args:
            issue: Original GitHub issue
            analysis: Analysis result

        Returns:
            Formatted PR description
        """
        prompt = f"""Based on this issue analysis, generate a professional PR description.

Issue: #{issue.number} - {issue.title}

Analysis Summary:
{analysis.summary}

Root Cause:
{analysis.root_cause}

Solution Steps:
{chr(10).join(f'- {step}' for step in analysis.solution_steps)}

Generate a PR description with:
1. A clear title
2. Description of changes
3. Related issue reference
4. Testing notes
5. Checklist for reviewers"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that writes clear, professional PR descriptions.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1000,
        )

        return response.choices[0].message.content
