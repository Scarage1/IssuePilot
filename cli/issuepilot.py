#!/usr/bin/env python3
"""
IssuePilot CLI - Command-line interface for GitHub issue analysis
"""
import argparse
import json
import sys
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    from rich.panel import Panel
    from rich.table import Table
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# Default API endpoint
DEFAULT_API_URL = "http://localhost:8000"
CONFIG_FILENAME = ".issuepilotrc"


def load_config() -> Dict[str, Any]:
    """
    Load configuration from .issuepilotrc file
    
    Searches in order:
    1. Current directory
    2. User's home directory
    
    Returns:
        Configuration dictionary
    """
    config = {}
    
    # Search paths
    search_paths = [
        Path.cwd() / CONFIG_FILENAME,
        Path.home() / CONFIG_FILENAME,
    ]
    
    for config_path in search_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Try YAML first, then JSON
                if YAML_AVAILABLE:
                    try:
                        config = yaml.safe_load(content) or {}
                        break
                    except yaml.YAMLError:
                        pass
                
                # Try JSON
                try:
                    config = json.loads(content)
                    break
                except json.JSONDecodeError:
                    pass
                    
            except Exception:
                pass
    
    return config


class IssuePilotCLI:
    """Command-line interface for IssuePilot"""
    
    def __init__(self, api_url: str = DEFAULT_API_URL):
        self.api_url = api_url
        self.console = Console() if RICH_AVAILABLE else None
    
    def _print(self, message: str, style: str = None):
        """Print message using rich if available, else plain print"""
        if self.console:
            self.console.print(message, style=style)
        else:
            print(message)
    
    def _show_spinner(self, description: str):
        """Create a progress spinner context manager"""
        if RICH_AVAILABLE:
            return Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                TimeElapsedColumn(),
                console=self.console,
                transient=True
            )
        return None
    
    def analyze(
        self,
        repo: str,
        issue_number: int,
        token: Optional[str] = None,
        export: Optional[str] = None,
        output_file: Optional[str] = None,
        no_cache: bool = False
    ) -> dict:
        """
        Analyze a GitHub issue
        
        Args:
            repo: Repository in format 'owner/repo'
            issue_number: Issue number to analyze
            token: GitHub personal access token
            export: Export format (md, json)
            output_file: File to write output to
            no_cache: Bypass cache if True
            
        Returns:
            Analysis result dictionary
        """
        self._print(f"\n🔍 Analyzing issue #{issue_number} from {repo}...", style="bold cyan")
        
        # Prepare request
        payload = {
            "repo": repo,
            "issue_number": issue_number
        }
        if token:
            payload["github_token"] = token
        
        # Add cache bypass header
        headers = {}
        if no_cache:
            headers["X-No-Cache"] = "true"
        
        # Make request to API with spinner
        result = None
        start_time = time.time()
        
        try:
            if RICH_AVAILABLE:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]{task.description}"),
                    TimeElapsedColumn(),
                    console=self.console,
                    transient=True
                ) as progress:
                    task = progress.add_task("Fetching issue from GitHub...", total=None)
                    
                    with httpx.Client(timeout=60.0) as client:
                        progress.update(task, description="Analyzing issue with AI...")
                        response = client.post(
                            f"{self.api_url}/analyze",
                            json=payload,
                            headers=headers
                        )
                        response.raise_for_status()
                        result = response.json()
                        progress.update(task, description="Analysis complete!")
            else:
                print("   ⏳ Please wait...")
                with httpx.Client(timeout=60.0) as client:
                    response = client.post(
                        f"{self.api_url}/analyze",
                        json=payload,
                        headers=headers
                    )
                    response.raise_for_status()
                    result = response.json()
                    
        except httpx.ConnectError:
            self._print(f"\n❌ Error: Cannot connect to IssuePilot API at {self.api_url}", style="bold red")
            self._print("   Make sure the backend server is running:")
            self._print("   cd backend && uvicorn app.main:app --reload", style="dim")
            sys.exit(1)
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get("detail", str(e))
            self._print(f"\n❌ Error: {error_detail}", style="bold red")
            sys.exit(1)
        
        elapsed = time.time() - start_time
        self._print(f"✨ Analysis completed in {elapsed:.2f}s", style="bold green")
        
        elapsed = time.time() - start_time
        self._print(f"✨ Analysis completed in {elapsed:.2f}s", style="bold green")
        
        # Display results
        self._display_analysis(result)
        
        # Handle export
        if export:
            output = self._export_result(result, export)
            if output_file:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(output)
                self._print(f"\n✅ Exported to {output_file}", style="bold green")
            else:
                self._print(f"\n📄 Exported {export.upper()}:\n")
                print(output)
        
        return result
    
    def _display_analysis(self, result: dict) -> None:
        """Display analysis result in a formatted way"""
        if RICH_AVAILABLE:
            self._display_analysis_rich(result)
        else:
            self._display_analysis_plain(result)
    
    def _display_analysis_rich(self, result: dict) -> None:
        """Display analysis using rich formatting"""
        # Summary Panel
        self.console.print()
        self.console.print(Panel(
            result.get("summary", "N/A"),
            title="📋 Summary",
            border_style="blue"
        ))
        
        # Root Cause Panel
        self.console.print(Panel(
            result.get("root_cause", "N/A"),
            title="🔬 Root Cause Analysis",
            border_style="yellow"
        ))
        
        # Solution Steps Table
        steps_table = Table(title="🛠️ Solution Steps", show_header=False, box=None)
        steps_table.add_column("", style="cyan", width=4)
        steps_table.add_column("")
        for i, step in enumerate(result.get("solution_steps", []), 1):
            steps_table.add_row(f"{i}.", step)
        self.console.print(steps_table)
        self.console.print()
        
        # Checklist Table
        checklist_table = Table(title="✅ Developer Checklist", show_header=False, box=None)
        checklist_table.add_column("", style="green", width=4)
        checklist_table.add_column("")
        for item in result.get("checklist", []):
            checklist_table.add_row("☐", item)
        self.console.print(checklist_table)
        self.console.print()
        
        # Labels
        labels = result.get("labels", [])
        if labels:
            label_str = " ".join([f"[bold magenta]`{l}`[/bold magenta]" for l in labels])
            self.console.print(f"🏷️  Labels: {label_str}")
            self.console.print()
        
        # Similar Issues
        similar_issues = result.get("similar_issues", [])
        if similar_issues:
            similar_table = Table(title="🔗 Similar Issues (Potential Duplicates)", box=None)
            similar_table.add_column("Issue", style="cyan")
            similar_table.add_column("Title")
            similar_table.add_column("Similarity", style="green")
            for issue in similar_issues:
                similar_table.add_row(
                    f"#{issue['issue_number']}",
                    issue['title'][:50] + "..." if len(issue['title']) > 50 else issue['title'],
                    f"{issue['similarity']:.0%}"
                )
            self.console.print(similar_table)
            self.console.print()
        
        self.console.print("─" * 60)
        self.console.print("🚀 Analysis complete!", style="bold green")
        self.console.print()
    
    def _display_analysis_plain(self, result: dict) -> None:
        """Display analysis using plain text formatting"""
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
            if RICH_AVAILABLE:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]{task.description}"),
                    console=self.console,
                    transient=True
                ) as progress:
                    task = progress.add_task("Checking API health...", total=None)
                    with httpx.Client(timeout=10.0) as client:
                        response = client.get(f"{self.api_url}/health")
                        response.raise_for_status()
                        result = response.json()
            else:
                with httpx.Client(timeout=10.0) as client:
                    response = client.get(f"{self.api_url}/health")
                    response.raise_for_status()
                    result = response.json()
            
            if result.get("status") == "ok":
                self._print("✅ IssuePilot API is healthy!", style="bold green")
                
                # Display enhanced health info if available
                if "version" in result:
                    self._print(f"   Version: {result['version']}")
                if "dependencies" in result:
                    deps = result["dependencies"]
                    self._print("   Dependencies:")
                    for key, value in deps.items():
                        status = "✓" if value else "✗"
                        color = "green" if value else "red"
                        self._print(f"     {status} {key.replace('_', ' ').title()}", style=color)
                return True
        except Exception as e:
            self._print(f"❌ API health check failed: {e}", style="bold red")
        return False


def main():
    """Main CLI entry point"""
    # Load configuration from file
    config = load_config()
    
    parser = argparse.ArgumentParser(
        prog="issuepilot",
        description="🚀 IssuePilot - AI-powered GitHub issue analysis assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  issuepilot analyze --repo facebook/react --issue 12345
  issuepilot analyze --repo vercel/next.js --issue 54321 --export md
  issuepilot analyze --repo owner/repo --issue 100 --token YOUR_TOKEN --output analysis.md
  issuepilot analyze --repo owner/repo --issue 100 --no-cache
  issuepilot health
  issuepilot config

Configuration:
  Create a .issuepilotrc file in your home directory or current directory with:
    api_url: http://localhost:8000
    github_token: ghp_xxxxx
    default_export_format: md

For more information, visit: https://github.com/Scarage1/IssuePilot
        """
    )
    
    # Get default API URL from config or environment
    default_api_url = config.get("api_url", os.getenv("ISSUEPILOT_API_URL", DEFAULT_API_URL))
    
    parser.add_argument(
        "--api-url",
        default=default_api_url,
        help=f"API URL (default: {default_api_url})"
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
        default=config.get("default_export_format"),
        help="Export format (md or json)"
    )
    analyze_parser.add_argument(
        "--output", "-o",
        help="Output file path for export"
    )
    analyze_parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Bypass cache and force fresh analysis"
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
    
    # Config command - show current configuration
    subparsers.add_parser(
        "config",
        help="Show current configuration"
    )
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = IssuePilotCLI(api_url=args.api_url)
    
    # Handle commands
    if args.command == "analyze":
        # Get token from args, config, or environment
        token = args.token or config.get("github_token") or os.getenv("GITHUB_TOKEN")
        cli.analyze(
            repo=args.repo,
            issue_number=args.issue,
            token=token,
            export=args.export,
            output_file=args.output,
            no_cache=args.no_cache
        )
    elif args.command == "health":
        success = cli.health_check()
        sys.exit(0 if success else 1)
    elif args.command == "version":
        print("IssuePilot CLI v1.1.0")
        if RICH_AVAILABLE:
            print("  ✓ Rich formatting enabled")
        if YAML_AVAILABLE:
            print("  ✓ YAML config support enabled")
    elif args.command == "config":
        print("🔧 Current Configuration:")
        print(f"   API URL: {args.api_url}")
        print(f"   Config file: {CONFIG_FILENAME}")
        if config:
            print("   Loaded settings:")
            for key, value in config.items():
                if "token" in key.lower():
                    value = value[:8] + "..." if len(str(value)) > 8 else "***"
                print(f"     {key}: {value}")
        else:
            print("   No configuration file found.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
