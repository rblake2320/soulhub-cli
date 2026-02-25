#!/usr/bin/env python3
"""
SoulHub CLI - All-in-One AI Memory & Deployment System
=======================================================
Combines: GitHub + Cloudflare + Tigs + Soul System

Usage:
    soulhub init                    # Initialize project
    soulhub create <name>           # Create new soul project
    soulhub deploy                  # Deploy to Cloudflare via GitHub
    soulhub archive                 # Archive conversations with Tigs
    soulhub sync [agent]            # Sync souls across agents
    soulhub catalog                 # Browse soul catalog
    soulhub install <soul>          # Install soul from catalog
    soulhub publish                 # Publish soul to catalog
    soulhub verify                  # Run verification tests
    soulhub status                  # Show project status
"""

import click
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import sys
import os


class SoulHubConfig:
    """Configuration manager for SoulHub"""

    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or Path.cwd()
        self.config_file = self.project_dir / '.soulhub' / 'config.json'
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration file"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return {
            'version': '1.0',
            'github': {},
            'cloudflare': {},
            'tigs': {'enabled': False},
            'soul_system': {'enabled': True},
            'agents': []
        }

    def save(self):
        """Save configuration"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get(self, key: str, default=None):
        """Get config value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, {})
            if value == {}:
                return default
        return value

    def set(self, key: str, value: Any):
        """Set config value"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save()


class GitHubManager:
    """Manage GitHub repositories"""

    @staticmethod
    def create_repo(name: str, description: str = "", private: bool = False) -> Dict[str, Any]:
        """Create GitHub repository using gh CLI"""
        visibility = "--private" if private else "--public"
        cmd = f"gh repo create {name} {visibility} --description \"{description}\""

        try:
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            return {'success': True, 'url': result.stdout.strip()}
        except subprocess.CalledProcessError as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def push_to_remote():
        """Push to GitHub"""
        try:
            subprocess.run("git push -u origin main", shell=True, check=True)
            return {'success': True}
        except subprocess.CalledProcessError as e:
            return {'success': False, 'error': str(e)}


class CloudflareManager:
    """Manage Cloudflare Pages integration"""

    @staticmethod
    def connect_pages(project_name: str, github_repo: str) -> Dict[str, Any]:
        """Connect GitHub repo to Cloudflare Pages"""
        click.echo(f"\nTo connect Cloudflare Pages:")
        click.echo(f"1. Visit: https://dash.cloudflare.com/")
        click.echo(f"2. Go to: Workers & Pages > Create application > Pages > Connect to Git")
        click.echo(f"3. Select repository: {github_repo}")
        click.echo(f"4. Project name: {project_name}")
        click.echo(f"5. Your site will be: https://{project_name}.pages.dev")

        return {
            'success': True,
            'url': f"https://{project_name}.pages.dev",
            'instructions': 'Manual setup required (see above)'
        }

    @staticmethod
    def get_deployment_status(project_name: str) -> Dict[str, Any]:
        """Get Cloudflare Pages deployment status"""
        # Would use Cloudflare API with proper auth
        return {'status': 'unknown', 'message': 'API integration pending'}


class TigsManager:
    """Manage Tigs conversation archiving"""

    def __init__(self, repo_path: Path = None):
        self.repo_path = repo_path or Path.cwd()

    def enable(self) -> bool:
        """Enable Tigs in repository"""
        try:
            from tigs.store import TigsStore
            store = TigsStore(self.repo_path)
            return True
        except ImportError:
            click.echo("Warning: Tigs not installed. Run: pip install tigs")
            return False

    def archive_claude_sessions(self) -> Dict[str, Any]:
        """Archive Claude Code sessions using Tigs"""
        try:
            from tigs.store import TigsStore
            store = TigsStore(self.repo_path)

            # Find Claude Code sessions
            claude_dir = Path.home() / '.claude' / 'projects'
            sessions = list(claude_dir.glob('*/*.jsonl'))

            archived = 0
            for session_file in sessions:
                # Read session metadata
                with open(session_file) as f:
                    first_line = f.readline()
                    if first_line.strip():
                        try:
                            data = json.loads(first_line)
                            session_id = data.get('sessionId', session_file.stem)

                            # Store session reference in Tigs
                            metadata = {
                                'type': 'claude_code_session',
                                'session_id': session_id,
                                'file': str(session_file),
                                'timestamp': datetime.now().isoformat()
                            }
                            store.store(json.dumps(metadata))
                            archived += 1
                        except json.JSONDecodeError:
                            continue

            return {'success': True, 'archived': archived}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class SoulManager:
    """Manage soul system integration"""

    def __init__(self, project_dir: Path = None):
        self.project_dir = project_dir or Path.cwd()
        self.soul_dir = self.project_dir / '.soulhub' / 'souls'
        self.soul_dir.mkdir(parents=True, exist_ok=True)

    def create_soul_template(self, name: str, role: str = "AI Assistant") -> Path:
        """Create a new SOUL.md template"""
        soul_file = self.soul_dir / f"{name}.md"

        template = f"""# {name} Soul

## Core Identity
**Role**: {role}
**Created**: {datetime.now().strftime('%Y-%m-%d')}
**Version**: 1.0

## Expertise
- [Add your expertise areas]

## Communication Style
- [Define communication preferences]

## Active Context

### Recent Decisions
```yaml
{datetime.now().strftime('%Y-%m-%d')}:
  - decision: Initial soul creation
    rationale: Starting fresh
```

### Learned Preferences
- [Preferences will be learned automatically]

### Pain Points Solved
- [Mistakes to avoid]

## Behavioral Parameters

### Token Optimization
- Prefer concise communication
- Front-load critical information

### Proactivity Level
- Suggest improvements when spotted
- Ask clarifying questions

### Error Handling
- Verify before destructive operations
- Provide clear error explanations

## Memory Hooks
- Cross-agent sync enabled
- Decision archaeology enabled
- Pattern learning enabled

---
*Generated by SoulHub CLI v1.0*
"""

        soul_file.write_text(template)
        return soul_file

    def sync_souls(self, agent_id: str, target: str) -> Dict[str, Any]:
        """Sync souls across agents"""
        # Use our existing soul_engine.py
        soul_engine_path = Path.home() / '.claude' / 'soul-system' / 'soul_engine.py'

        if soul_engine_path.exists():
            try:
                cmd = f"python {soul_engine_path} sync {agent_id} {target}"
                subprocess.run(cmd, shell=True, check=True)
                return {'success': True, 'agent': agent_id, 'target': target}
            except subprocess.CalledProcessError as e:
                return {'success': False, 'error': str(e)}
        else:
            return {'success': False, 'error': 'Soul engine not found'}

    def verify_soul(self) -> Dict[str, Any]:
        """Run verification tests"""
        verify_script = Path.home() / '.claude' / 'soul-system' / 'verify_novelty.py'

        if verify_script.exists():
            try:
                result = subprocess.run(
                    f"python {verify_script}",
                    shell=True,
                    check=True,
                    capture_output=True,
                    text=True
                )
                return {'success': True, 'output': result.stdout}
            except subprocess.CalledProcessError as e:
                return {'success': False, 'error': str(e)}
        else:
            return {'success': False, 'error': 'Verification script not found'}


class CatalogManager:
    """Manage soul catalog registry"""

    CATALOG_URL = "https://raw.githubusercontent.com/soul-registry/catalog/main/catalog.json"

    @staticmethod
    def fetch_catalog() -> Dict[str, Any]:
        """Fetch soul catalog from GitHub"""
        try:
            response = requests.get(CatalogManager.CATALOG_URL, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass

        # Fallback to local catalog-example.json if remote fails
        catalog_paths = [
            Path('catalog-example.json'),  # Current directory
            Path(__file__).parent / 'catalog-example.json',  # Package dir
            Path(__file__).parent.parent / 'catalog-example.json',  # Repo root (for pip install -e .)
        ]

        for catalog_path in catalog_paths:
            if catalog_path.exists():
                try:
                    with open(catalog_path) as f:
                        return json.load(f)
                except Exception:
                    continue

        # Final fallback: minimal example catalog
        return {
            'version': '1.0',
            'souls': {
                'expert-coder': {
                    'repo': 'rblake2320/soul-expert-coder',
                    'description': 'Expert coding assistant',
                    'tags': ['coding', 'python', 'javascript'],
                    'downloads': 0,
                    'rating': 5.0
                }
            },
            'patterns': {},
            'skills': {}
        }

    @staticmethod
    def search(query: str) -> list:
        """Search catalog"""
        catalog = CatalogManager.fetch_catalog()

        if 'error' in catalog:
            return []

        results = []
        for name, info in catalog.get('souls', {}).items():
            if query.lower() in name.lower() or query.lower() in info.get('description', '').lower():
                results.append({'name': name, **info})

        return results

    @staticmethod
    def install_soul(soul_name: str, target_dir: Path) -> Dict[str, Any]:
        """Install soul from catalog"""
        catalog = CatalogManager.fetch_catalog()

        if soul_name not in catalog.get('souls', {}):
            return {'success': False, 'error': f"Soul '{soul_name}' not found in catalog"}

        soul_info = catalog['souls'][soul_name]
        repo = soul_info['repo']

        # Download SOUL.md from GitHub
        url = f"https://raw.githubusercontent.com/{repo}/main/SOUL.md"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soul_file = target_dir / f"{soul_name}.md"
                soul_file.write_text(response.text)
                return {'success': True, 'file': str(soul_file)}
            else:
                return {'success': False, 'error': f"Failed to download: HTTP {response.status_code}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}


# CLI Commands

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """SoulHub - All-in-One AI Memory & Deployment System"""
    pass


@cli.command()
@click.option('--name', prompt='Project name', help='Project name')
@click.option('--private', is_flag=True, help='Create private repository')
def init(name: str, private: bool):
    """Initialize a new SoulHub project"""
    click.echo(f"\n=== Initializing SoulHub Project: {name} ===\n")

    config = SoulHubConfig()

    # 1. Initialize Git
    click.echo("[1/7] Initializing Git repository...")
    if not (Path.cwd() / '.git').exists():
        subprocess.run("git init", shell=True, check=True)
        subprocess.run("git branch -M main", shell=True, check=True)
    click.echo("OK Git initialized")

    # 2. Create GitHub repository
    click.echo("\n[2/7] Creating GitHub repository...")
    gh_result = GitHubManager.create_repo(
        name,
        description=f"SoulHub AI Memory Project - {name}",
        private=private
    )

    if gh_result['success']:
        click.echo(f"OK GitHub repo created: {gh_result['url']}")
        config.set('github.repo', name)
        config.set('github.url', gh_result['url'])
    else:
        click.echo(f"Warning: {gh_result.get('error', 'Unknown error')}")

    # 3. Enable Tigs
    click.echo("\n[3/7] Setting up Tigs conversation archiving...")
    tigs_mgr = TigsManager()
    if tigs_mgr.enable():
        click.echo("OK Tigs enabled")
        config.set('tigs.enabled', True)
    else:
        click.echo("Warning: Tigs not available")

    # 4. Create soul template
    click.echo("\n[4/7] Creating soul template...")
    soul_mgr = SoulManager()
    soul_file = soul_mgr.create_soul_template(name)
    click.echo(f"OK Soul template: {soul_file}")
    config.set('soul_system.soul_file', str(soul_file))

    # 5. Setup Cloudflare Pages instructions
    click.echo("\n[5/7] Cloudflare Pages integration...")
    cf_result = CloudflareManager.connect_pages(name, name)
    click.echo(f"OK Instructions provided")
    config.set('cloudflare.project', name)
    config.set('cloudflare.url', cf_result['url'])

    # 6. Create README
    click.echo("\n[6/7] Creating README...")
    readme_content = f"""# {name}

SoulHub AI Memory Project

## Quick Start

```bash
# Deploy
soulhub deploy

# Archive conversations
soulhub archive

# Sync souls across agents
soulhub sync <agent-id> <target>

# Check status
soulhub status
```

## Features

- OK GitHub version control
- OK Cloudflare Pages CDN
- OK Tigs conversation archiving
- OK Soul system (decision trees, verification, patterns)
- OK Cross-agent sync
- OK Cross-LLM compatibility

## Deployment

Site URL: {cf_result['url']}

---

*Built with [SoulHub CLI](https://github.com/rblake2320/soul-system)*
"""

    Path('README.md').write_text(readme_content)
    click.echo("OK README.md created")

    # 7. Initial commit
    click.echo("\n[7/7] Creating initial commit...")
    subprocess.run("git add .", shell=True, check=True)
    subprocess.run('git commit -m "Initial commit: SoulHub project setup"', shell=True, check=True)

    if gh_result['success']:
        subprocess.run(f"git remote add origin {gh_result['url']}.git", shell=True)
        click.echo("OK Initial commit created")

    # Save config
    config.save()

    click.echo(f"\n=== SoulHub Project Initialized ===")
    click.echo(f"\nNext steps:")
    click.echo(f"1. Push to GitHub: soulhub deploy")
    click.echo(f"2. Connect Cloudflare Pages (see instructions above)")
    click.echo(f"3. Edit soul: {soul_file}")
    click.echo(f"4. Check status: soulhub status")


@cli.command()
def deploy():
    """Deploy to GitHub (auto-triggers Cloudflare Pages)"""
    click.echo("\n=== Deploying to GitHub + Cloudflare ===\n")

    config = SoulHubConfig()

    # 1. Archive conversations with Tigs
    if config.get('tigs.enabled'):
        click.echo("[1/3] Archiving conversations with Tigs...")
        tigs_mgr = TigsManager()
        result = tigs_mgr.archive_claude_sessions()
        if result['success']:
            click.echo(f"OK Archived {result['archived']} sessions")
        else:
            click.echo(f"Warning: {result.get('error')}")

    # 2. Git commit
    click.echo("\n[2/3] Creating git commit...")
    subprocess.run("git add .", shell=True)
    commit_msg = f"Deploy: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    subprocess.run(f'git commit -m "{commit_msg}" || echo "Nothing to commit"', shell=True)
    click.echo("OK Commit created")

    # 3. Push to GitHub
    click.echo("\n[3/3] Pushing to GitHub...")
    result = GitHubManager.push_to_remote()

    if result['success']:
        click.echo("OK Pushed to GitHub")
        click.echo("\nCloudflare Pages will auto-deploy from GitHub.")
        click.echo(f"Check: {config.get('cloudflare.url', 'https://dash.cloudflare.com')}")
    else:
        click.echo(f"Error: {result.get('error')}")


@cli.command()
def archive():
    """Archive Claude Code conversations using Tigs"""
    click.echo("\n=== Archiving Conversations ===\n")

    tigs_mgr = TigsManager()
    result = tigs_mgr.archive_claude_sessions()

    if result['success']:
        click.echo(f"OK Archived {result['archived']} Claude Code sessions")
        click.echo("\nCommit and push to save to Git:")
        click.echo("  git add . && git commit -m 'Archive conversations' && git push")
    else:
        click.echo(f"Error: {result.get('error')}")


@cli.command()
@click.argument('agent_id')
@click.argument('target')
def sync(agent_id: str, target: str):
    """Sync souls across agents"""
    click.echo(f"\n=== Syncing Soul: {agent_id} -> {target} ===\n")

    soul_mgr = SoulManager()
    result = soul_mgr.sync_souls(agent_id, target)

    if result['success']:
        click.echo(f"OK Soul synced to {target}")
    else:
        click.echo(f"Error: {result.get('error')}")


@cli.command()
@click.option('--query', '-q', help='Search query')
def catalog(query: Optional[str]):
    """Browse or search soul catalog"""
    click.echo("\n=== Soul Catalog ===\n")

    if query:
        results = CatalogManager.search(query)
        click.echo(f"Search results for '{query}':\n")

        for soul in results:
            click.echo(f"  {soul['name']}")
            click.echo(f"    {soul.get('description', 'No description')}")
            click.echo(f"    Tags: {', '.join(soul.get('tags', []))}")
            click.echo(f"    Repo: {soul['repo']}\n")
    else:
        catalog_data = CatalogManager.fetch_catalog()

        if 'error' in catalog_data:
            click.echo(f"Error: {catalog_data['error']}")
            return

        souls = catalog_data.get('souls', {})
        click.echo(f"Available souls: {len(souls)}\n")

        for name, info in souls.items():
            click.echo(f"  {name} - {info.get('description', '')}")


@cli.command()
@click.argument('soul_name')
def install(soul_name: str):
    """Install soul from catalog"""
    click.echo(f"\n=== Installing Soul: {soul_name} ===\n")

    soul_mgr = SoulManager()
    result = CatalogManager.install_soul(soul_name, soul_mgr.soul_dir)

    if result['success']:
        click.echo(f"OK Installed to: {result['file']}")
    else:
        click.echo(f"Error: {result.get('error')}")


@cli.command()
def verify():
    """Run installation verification tests"""
    import sys

    click.echo("\n=== Running Installation Verification ===\n")

    # Try to find verify_installation.py
    verify_script = None

    # 1. Check current directory
    if Path('verify_installation.py').exists():
        verify_script = Path('verify_installation.py')

    # 2. Check package installation directory
    if not verify_script:
        package_dir = Path(__file__).parent
        if (package_dir / 'verify_installation.py').exists():
            verify_script = package_dir / 'verify_installation.py'

    # 3. Check repo parent directory (for pip install -e .)
    if not verify_script:
        repo_dir = Path(__file__).parent.parent
        if (repo_dir / 'verify_installation.py').exists():
            verify_script = repo_dir / 'verify_installation.py'

    if not verify_script:
        click.echo("Error: verify_installation.py not found")
        click.echo("\nTry running from the soulhub-cli repository:")
        click.echo("  cd ~/soulhub-cli")
        click.echo("  python verify_installation.py")
        return

    # Run the verification script
    try:
        result = subprocess.run(
            [sys.executable, str(verify_script)],
            check=False,
            capture_output=False
        )
        sys.exit(result.returncode)
    except Exception as e:
        click.echo(f"Error running verification: {e}")


@cli.command()
def status():
    """Show project status"""
    click.echo("\n=== SoulHub Project Status ===\n")

    config = SoulHubConfig()

    # GitHub status
    github_repo = config.get('github.repo')
    if github_repo:
        click.echo(f"GitHub:")
        click.echo(f"  Repository: {github_repo}")
        click.echo(f"  URL: {config.get('github.url')}")
    else:
        click.echo("GitHub: Not connected")

    # Cloudflare status
    cf_project = config.get('cloudflare.project')
    if cf_project:
        click.echo(f"\nCloudflare Pages:")
        click.echo(f"  Project: {cf_project}")
        click.echo(f"  URL: {config.get('cloudflare.url')}")
    else:
        click.echo("\nCloudflare Pages: Not connected")

    # Tigs status
    tigs_enabled = config.get('tigs.enabled')
    click.echo(f"\nTigs: {'Enabled' if tigs_enabled else 'Disabled'}")

    # Soul system status
    soul_file = config.get('soul_system.soul_file')
    if soul_file and Path(soul_file).exists():
        click.echo(f"\nSoul System:")
        click.echo(f"  Soul file: {soul_file}")
        click.echo(f"  Status: Active")
    else:
        click.echo("\nSoul System: Not configured")

    # Git status
    try:
        result = subprocess.run("git status --short", shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            click.echo(f"\nGit Status:")
            click.echo(result.stdout)
        else:
            click.echo(f"\nGit: Clean (no changes)")
    except:
        click.echo(f"\nGit: Not initialized")


if __name__ == '__main__':
    cli()
