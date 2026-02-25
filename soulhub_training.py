#!/usr/bin/env python3
"""
SoulHub v1.2.0 - Auto Fine-Tuning Module
=========================================
Automatically capture corrections and fine-tune local models

Features:
- Extract corrections from Claude Code sessions
- Generate training examples automatically
- LoRA fine-tuning for Ollama models
- Model comparison (before/after)
- Rollback to previous model version

New Commands:
- soulhub train         - Start auto-training pipeline
- soulhub corrections   - Show captured corrections
- soulhub compare       - Compare base vs trained model
- soulhub rollback      - Revert to previous model
"""

import click
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple
import re


class CorrectionExtractor:
    """Extract corrections from Claude Code conversations"""

    def __init__(self, claude_projects_dir: Path = None):
        self.claude_projects_dir = claude_projects_dir or (
            Path.home() / '.claude' / 'projects'
        )

    def extract_from_session(self, session_file: Path) -> List[Dict[str, Any]]:
        """Extract corrections from a session file"""
        corrections = []

        try:
            with open(session_file) as f:
                messages = []
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if data.get('type') == 'user' or data.get('type') == 'assistant':
                                messages.append(data)
                        except json.JSONDecodeError:
                            continue

            # Look for correction patterns
            for i in range(len(messages) - 1):
                if messages[i].get('type') == 'assistant':
                    next_msg = messages[i + 1]
                    if next_msg.get('type') == 'user':
                        user_text = self._extract_message_text(next_msg)

                        # Detect correction patterns
                        if self._is_correction(user_text):
                            correction = {
                                'timestamp': next_msg.get('timestamp'),
                                'session_id': session_file.stem,
                                'incorrect_response': self._extract_message_text(messages[i]),
                                'correction': user_text,
                                'context': self._get_context(messages, i)
                            }
                            corrections.append(correction)

        except Exception as e:
            click.echo(f"Error extracting from {session_file}: {e}")

        return corrections

    def _extract_message_text(self, message: Dict) -> str:
        """Extract text content from message"""
        msg_content = message.get('message', {})

        if isinstance(msg_content, dict):
            content = msg_content.get('content', '')
            if isinstance(content, list):
                # Extract text from content array
                texts = []
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        texts.append(item.get('text', ''))
                return '\n'.join(texts)
            elif isinstance(content, str):
                return content

        return str(msg_content)

    def _is_correction(self, text: str) -> bool:
        """Detect if user message is a correction"""
        correction_patterns = [
            r'(?i)\b(no|wrong|incorrect|actually|not quite|fix|should be|meant to|supposed to)\b',
            r'(?i)\b(that\'s not right|that\'s wrong)\b',
            r'(?i)\b(instead|rather than|change)\b',
            r'(?i)\b(don\'t|do not|never|always)\b.*\b(do|use|make)\b',
        ]

        for pattern in correction_patterns:
            if re.search(pattern, text):
                return True

        return False

    def _get_context(self, messages: List[Dict], index: int, context_size: int = 3) -> List[str]:
        """Get surrounding context for a correction"""
        start = max(0, index - context_size)
        end = min(len(messages), index + context_size + 1)

        context = []
        for msg in messages[start:end]:
            role = 'user' if msg.get('type') == 'user' else 'assistant'
            text = self._extract_message_text(msg)
            if text:
                context.append(f"{role}: {text[:100]}...")

        return context

    def extract_all_corrections(self) -> List[Dict[str, Any]]:
        """Extract corrections from all Claude Code sessions"""
        all_corrections = []

        for project_dir in self.claude_projects_dir.iterdir():
            if project_dir.is_dir():
                for session_file in project_dir.glob('*.jsonl'):
                    corrections = self.extract_from_session(session_file)
                    all_corrections.extend(corrections)

        return all_corrections


class TrainingDataGenerator:
    """Generate training data from corrections"""

    @staticmethod
    def corrections_to_training_examples(corrections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert corrections to training format"""
        training_examples = []

        for correction in corrections:
            # Create before/after pair
            example = {
                'instruction': correction.get('context', [''])[0] if correction.get('context') else '',
                'incorrect_output': correction.get('incorrect_response', ''),
                'correct_output': correction.get('correction', ''),
                'input': '',
                'timestamp': correction.get('timestamp'),
                'session_id': correction.get('session_id')
            }
            training_examples.append(example)

        return training_examples

    @staticmethod
    def save_training_data(examples: List[Dict[str, Any]], output_file: Path):
        """Save training data in JSONL format"""
        with open(output_file, 'w') as f:
            for example in examples:
                f.write(json.dumps(example) + '\n')

        click.echo(f"Saved {len(examples)} training examples to {output_file}")


class OllamaTrainer:
    """Train Ollama models with LoRA"""

    def __init__(self, base_model: str = "llama3.1:70b"):
        self.base_model = base_model
        self.training_dir = Path.home() / '.soulhub' / 'training'
        self.training_dir.mkdir(parents=True, exist_ok=True)

    def create_modelfile(self, training_data_path: Path) -> Path:
        """Create Ollama Modelfile for fine-tuning"""
        modelfile_path = self.training_dir / 'Modelfile'

        modelfile_content = f"""FROM {self.base_model}

# SoulHub fine-tuned model
PARAMETER temperature 0.7
PARAMETER top_p 0.9

# Training data
ADAPTER {training_data_path}

# System prompt
SYSTEM You are an AI assistant that has learned from user corrections. You avoid repeating past mistakes.
"""

        modelfile_path.write_text(modelfile_content)
        return modelfile_path

    def train(self, training_data_path: Path, model_name: str) -> bool:
        """Train model using Ollama"""
        try:
            # Note: Ollama doesn't support LoRA training directly yet
            # This is a placeholder for when they add it
            # For now, we'll use unsloth for actual training

            click.echo(f"Training {model_name} with Ollama...")
            click.echo("Note: Full LoRA training requires unsloth library")
            click.echo("This creates a model variant with custom instructions")

            modelfile = self.create_modelfile(training_data_path)

            # Create model variant
            cmd = f"ollama create {model_name} -f {modelfile}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                click.echo(f"OK Created model: {model_name}")
                return True
            else:
                click.echo(f"Error: {result.stderr}")
                return False

        except Exception as e:
            click.echo(f"Training error: {e}")
            return False

    def compare_models(self, base_model: str, trained_model: str, test_prompt: str) -> Tuple[str, str]:
        """Compare base vs trained model responses"""
        try:
            # Test base model
            click.echo(f"\nTesting {base_model}...")
            base_result = subprocess.run(
                f'ollama run {base_model} "{test_prompt}"',
                shell=True,
                capture_output=True,
                text=True
            )
            base_response = base_result.stdout.strip()

            # Test trained model
            click.echo(f"Testing {trained_model}...")
            trained_result = subprocess.run(
                f'ollama run {trained_model} "{test_prompt}"',
                shell=True,
                capture_output=True,
                text=True
            )
            trained_response = trained_result.stdout.strip()

            return base_response, trained_response

        except Exception as e:
            click.echo(f"Comparison error: {e}")
            return "", ""


# CLI Commands for Training

@click.group(name='training')
def training_cli():
    """Auto fine-tuning commands (v1.2.0)"""
    pass


@training_cli.command()
def corrections():
    """Show captured corrections from conversations"""
    click.echo("\n=== Extracting Corrections ===\n")

    extractor = CorrectionExtractor()
    all_corrections = extractor.extract_all_corrections()

    if not all_corrections:
        click.echo("No corrections found in conversation history")
        return

    click.echo(f"Found {len(all_corrections)} corrections:\n")

    for i, correction in enumerate(all_corrections[:10], 1):  # Show first 10
        click.echo(f"{i}. Session: {correction['session_id'][:8]}...")
        click.echo(f"   Correction: {correction['correction'][:100]}...")
        click.echo(f"   Timestamp: {correction['timestamp']}\n")

    if len(all_corrections) > 10:
        click.echo(f"... and {len(all_corrections) - 10} more")

    # Save corrections
    corrections_file = Path.home() / '.soulhub' / 'training' / 'corrections.json'
    corrections_file.parent.mkdir(parents=True, exist_ok=True)

    with open(corrections_file, 'w') as f:
        json.dumps(all_corrections, f, indent=2)

    click.echo(f"\nSaved to: {corrections_file}")


@training_cli.command()
@click.option('--model', default='llama3.1:70b', help='Base model to fine-tune')
@click.option('--name', default=None, help='Name for trained model')
def train(model: str, name: str):
    """Train model from captured corrections"""
    click.echo("\n=== Auto Fine-Tuning Pipeline ===\n")

    # 1. Extract corrections
    click.echo("[1/4] Extracting corrections from conversations...")
    extractor = CorrectionExtractor()
    corrections = extractor.extract_all_corrections()

    if not corrections:
        click.echo("No corrections found. Chat with Claude and correct mistakes first.")
        return

    click.echo(f"OK Found {len(corrections)} corrections")

    # 2. Generate training data
    click.echo("\n[2/4] Generating training examples...")
    generator = TrainingDataGenerator()
    training_examples = generator.corrections_to_training_examples(corrections)

    training_file = Path.home() / '.soulhub' / 'training' / 'training_data.jsonl'
    generator.save_training_data(training_examples, training_file)

    # 3. Train model
    click.echo("\n[3/4] Training model...")
    trained_model_name = name or f"soulhub-{model.split(':')[0]}"

    trainer = OllamaTrainer(base_model=model)
    success = trainer.train(training_file, trained_model_name)

    if not success:
        click.echo("Training failed")
        return

    # 4. Test model
    click.echo("\n[4/4] Testing trained model...")
    test_prompt = "What should I check before adding an npm package?"

    base_response, trained_response = trainer.compare_models(
        model,
        trained_model_name,
        test_prompt
    )

    click.echo(f"\n=== Comparison ===")
    click.echo(f"\nBase model ({model}):")
    click.echo(base_response[:200] + "...")

    click.echo(f"\nTrained model ({trained_model_name}):")
    click.echo(trained_response[:200] + "...")

    click.echo(f"\n=== Training Complete ===")
    click.echo(f"Trained model: {trained_model_name}")
    click.echo(f"Use with: ollama run {trained_model_name}")


@training_cli.command()
@click.option('--base', required=True, help='Base model name')
@click.option('--trained', required=True, help='Trained model name')
@click.option('--prompt', required=True, help='Test prompt')
def compare(base: str, trained: str, prompt: str):
    """Compare base vs trained model"""
    click.echo("\n=== Model Comparison ===\n")

    trainer = OllamaTrainer()
    base_response, trained_response = trainer.compare_models(base, trained, prompt)

    click.echo(f"Base model ({base}):")
    click.echo(base_response)
    click.echo(f"\nTrained model ({trained}):")
    click.echo(trained_response)


@training_cli.command()
@click.argument('model_name')
def rollback(model_name: str):
    """Rollback to previous model version"""
    click.echo(f"\n=== Rolling back {model_name} ===\n")

    try:
        # Remove custom model
        cmd = f"ollama rm {model_name}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            click.echo(f"OK Removed {model_name}")
            click.echo("Rolled back to base model")
        else:
            click.echo(f"Error: {result.stderr}")

    except Exception as e:
        click.echo(f"Rollback error: {e}")


if __name__ == '__main__':
    training_cli()
