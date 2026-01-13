#!/usr/bin/env python3
"""
IssuePilot CLI - Command-line interface for GitHub issue analysis
"""
import argparse
import json
import sys
import os
from typing import Optional

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)


# Default API endpoint
DEFAULT_API_URL = "http://localhost:8000"


class IssuePilotCLI:
    """Command-line interface for IssuePilot"""
    
    def __init__(self, api_url: str = DEFAULT_API_URL):
        self.api_url = api_url
    
    def analyze(
        self,
        repo: str,
        issue_number: int,
        token: Optional[str] = None,
        export: Optional[str] = None,
        output_file: Optional[str] = None
    ) -> dict:
        """
        Analyze a GitHub issue
        
        Args:
            repo: Repository in format 'owner/repo'
            issue_number: Issue number to analyze
            token: GitHub personal access token
            export: Export format (md, json)
            output_file: File to write output to
            
        Returns:
            Analysis result dictionary
        """
        print(f"\n🔍 Analyzing issue #{issue_number} from {repo}...")
        
        # Prepare request
        payload = {
            "repo": repo,
            "issue_number": issue_number
        }
        if token:
            payload["github_token"] = token
        
        # Make request to API
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.api_url}/analyze",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
        except httpx.ConnectError:
            print(f"\n❌ Error: Cannot connect to IssuePilot API at {self.api_url}")
            print("   Make sure the backend server is running:")
            print("   cd backend && uvicorn app.main:app --reload")
            sys.exit(1)
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get("detail", str(e))
            print(f"\n❌ Error: {error_detail}")
            sys.exit(1)
        
        # Display results
        self._display_analysis(result)
        
        # Handle export
        if export:
            output = self._export_result(result, export)
            if output_file:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(output)
                print(f"\n✅ Exported to {output_file}")
            else:
                print(f"\n📄 Exported {export.upper()}:\n")
                print(output)
        
        return result
    
    def _display_analysis(self, result: dict) -> None:
        """Display analysis result in a formatted way"""
        print("\n" + "=" * 60)
        print("📋 ISSUE ANALYSIS REPORT")
        print("=" * 60)
        
        print("\n📝 Summary:")
        print("-" * 40)
        print(result.get("summary", "N/A"))
        
        print("\n🔬 Root Cause:")
        print("-" * 40)
        print(result.get("root_cause", "N/A"))
        
        print("\n🛠️  Solution Steps:")
        print("-" * 40)
        for i, step in enumerate(result.get("solution_steps", []), 1):
            print(f"  {i}. {step}")
        
        print("\n✅ Developer Checklist:")
        print("-" * 40)
        for item in result.get("checklist", []):
            print(f"  [ ] {item}")
        
        print("\n🏷️  Suggested Labels:")
        print("-" * 40)
        labels = result.get("labels", [])
        print(f"  {', '.join(labels)}")
        
        similar_issues = result.get("similar_issues", [])
        if similar_issues:
            print("\n🔗 Similar Issues (Potential Duplicates):")
            print("-" * 40)
            for issue in similar_issues:
                print(f"  • #{issue['issue_number']}: {issue['title']}")
                print(f"    Similarity: {issue['similarity']:.0%}")
                print(f"    URL: {issue['url']}")
        
        print("\n" + "=" * 60)
        print("🚀 Analysis complete!")
        print("=" * 60 + "\n")
    
    def _export_result(self, result: dict, format: str) -> str:
        """Export result to specified format"""
        if format.lower() == "json":
            return json.dumps(result, indent=2)
        elif format.lower() == "md":
            # Request markdown export from API
            try:
                with httpx.Client(timeout=30.0) as client:
                    response = client.post(
                        f"{self.api_url}/export",
                        json={"analysis": result}
                    )
                    response.raise_for_status()
                    return response.json()["markdown"]
            except Exception:
                # Fallback: generate locally
                return self._generate_markdown(result)
        else:
            print(f"⚠️  Unknown format: {format}. Using JSON.")
            return json.dumps(result, indent=2)
    
    def _generate_markdown(self, result: dict) -> str:
        """Generate markdown locally as fallback"""
        lines = [
            "# 🔍 Issue Analysis Report",
            "",
            "## 📋 Summary",
            "",
            result.get("summary", "N/A"),
            "",
            "## 🔬 Root Cause Analysis",
            "",
            result.get("root_cause", "N/A"),
            "",
            "## 🛠️ Solution Steps",
            ""
        ]
        
        for i, step in enumerate(result.get("solution_steps", []), 1):
            lines.append(f"{i}. {step}")
        
        lines.extend(["", "## ✅ Developer Checklist", ""])
        for item in result.get("checklist", []):
            lines.append(f"- [ ] {item}")
        
        lines.extend([
            "",
            "## 🏷️ Suggested Labels",
            "",
            ", ".join([f"`{l}`" for l in result.get("labels", [])]),
            "",
            "---",
            "*Generated by IssuePilot 🚀*"
        ])
        
        return "\n".join(lines)
    
    def health_check(self) -> bool:
        """Check if the API is healthy"""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{self.api_url}/health")
                response.raise_for_status()
                result = response.json()
                if result.get("status") == "ok":
                    print("✅ IssuePilot API is healthy!")
                    return True
        except Exception as e:
            print(f"❌ API health check failed: {e}")
        return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="issuepilot",
        description="🚀 IssuePilot - AI-powered GitHub issue analysis assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  issuepilot analyze --repo facebook/react --issue 12345
  issuepilot analyze --repo vercel/next.js --issue 54321 --export md
  issuepilot analyze --repo owner/repo --issue 100 --token YOUR_TOKEN --output analysis.md
  issuepilot health

For more information, visit: https://github.com/issuepilot/issuepilot
        """
    )
    
    parser.add_argument(
        "--api-url",
        default=os.getenv("ISSUEPILOT_API_URL", DEFAULT_API_URL),
        help=f"API URL (default: {DEFAULT_API_URL})"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a GitHub issue"
    )
    analyze_parser.add_argument(
        "--repo", "-r",
        required=True,
        help="Repository in format 'owner/repo'"
    )
    analyze_parser.add_argument(
        "--issue", "-i",
        type=int,
        required=True,
        help="Issue number to analyze"
    )
    analyze_parser.add_argument(
        "--token", "-t",
        help="GitHub personal access token"
    )
    analyze_parser.add_argument(
        "--export", "-e",
        choices=["md", "json"],
        help="Export format (md or json)"
    )
    analyze_parser.add_argument(
        "--output", "-o",
        help="Output file path for export"
    )
    
    # Health command
    subparsers.add_parser(
        "health",
        help="Check API health status"
    )
    
    # Version command
    subparsers.add_parser(
        "version",
        help="Show version information"
    )
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = IssuePilotCLI(api_url=args.api_url)
    
    # Handle commands
    if args.command == "analyze":
        cli.analyze(
            repo=args.repo,
            issue_number=args.issue,
            token=args.token or os.getenv("GITHUB_TOKEN"),
            export=args.export,
            output_file=args.output
        )
    elif args.command == "health":
        success = cli.health_check()
        sys.exit(0 if success else 1)
    elif args.command == "version":
        print("IssuePilot CLI v1.0.0")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
