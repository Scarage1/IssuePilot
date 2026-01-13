"""
AI Engine for IssuePilot - Handles LLM interactions
"""

import os
from typing import Optional

from openai import AsyncOpenAI

from .schemas import AnalysisResult, GitHubIssue
from .utils import clean_json_response, truncate_text


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
        provider: str = "openai",
    ):
        """
        Initialize AI Engine

        Args:
            api_key: API key for AI provider
            model: Model to use for analysis
            provider: AI provider (currently supports 'openai')
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("MODEL", "gpt-4o-mini")
        self.provider = provider or os.getenv("AI_PROVIDER", "openai")

        if not self.api_key:
            raise ValueError(
                "AI API key is required. Set OPENAI_API_KEY environment variable."
            )

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

    async def analyze_issue(self, issue: GitHubIssue) -> AnalysisResult:
        """
        Analyze a GitHub issue using AI

        Args:
            issue: GitHub issue to analyze

        Returns:
            AnalysisResult with structured analysis
        """
        prompt = self._build_prompt(issue)

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

        # Validate and build result
        return self._validate_result(result)

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
