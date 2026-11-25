from typing import List
from uuid import UUID
from training_data_bot.core.models import QualityReport, TrainingExample


class QualityEvaluator:
    """Basic transparent checks; these are heuristic, not an ML quality judge."""

    def __init__(self, pass_threshold: float = 0.6):
        if not 0 <= pass_threshold <= 1:
            raise ValueError("pass_threshold must be between 0 and 1.")
        self.pass_threshold = pass_threshold

    def evaluate_examples(self, examples: List[TrainingExample], target_id: UUID) -> QualityReport:
        issues = []
        warnings = []
        if not examples:
            issues.append("Dataset contains no training examples.")
            score = 0.0
        else:
            scores = []
            for index, example in enumerate(examples):
                input_ok = bool(example.input_text.strip())
                output_ok = bool(example.output_text.strip())
                score = (int(input_ok) + int(output_ok)) / 2
                scores.append(score)
                if not input_ok:
                    issues.append(f"Example {index} has empty input text.")
                if not output_ok:
                    issues.append(f"Example {index} has empty output text.")
                if input_ok and output_ok and len(example.output_text) < 4:
                    warnings.append(f"Example {index} has a very short output.")
            score = sum(scores) / len(scores)

        passed = score >= self.pass_threshold and not issues
        return QualityReport(
            target_id=target_id,
            overall_score=score,
            passed=passed,
            metric_scores={
                "completeness": score,
                "non_empty_examples": score,
            },
            issues=issues,
            warnings=warnings,
        )

    def filter_examples(self, examples: List[TrainingExample]) -> List[TrainingExample]:
        """Remove examples whose input or generated output is empty."""
        return [
            example for example in examples
            if example.input_text.strip() and example.output_text.strip()
        ]

    async def evaluate_dataset(self, dataset, detailed_report: bool = True) -> QualityReport:
        return self.evaluate_examples(dataset.examples, dataset.id)
