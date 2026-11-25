import csv
import json
from pathlib import Path
from typing import Union
from training_data_bot.core.models import Dataset, ExportFormat


class DatasetExporter:
    """Exports datasets as JSON, JSONL, or CSV."""

    async def export_dataset(
        self,
        dataset: Dataset,
        output_path: Union[str, Path],
        format: ExportFormat = ExportFormat.JSONL,
        split_data: bool = False,
    ) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        export_format = ExportFormat(format)

        rows = [
            {
                "input_text": item.input_text,
                "output_text": item.output_text,
                "task_type": item.task_type.value,
                "source_document_id": str(item.source_document_id),
                "source_chunk_id": str(item.source_chunk_id) if item.source_chunk_id else None,
                "quality_scores": item.quality_scores,
            }
            for item in dataset.examples
        ]

        if split_data:
            total = len(rows)
            train_end = int(total * dataset.train_split)
            validation_end = train_end + int(total * dataset.validation_split)
            for index, row in enumerate(rows):
                if index < train_end:
                    row["split"] = "train"
                elif index < validation_end:
                    row["split"] = "validation"
                else:
                    row["split"] = "test"

        if export_format == ExportFormat.JSON:
            path.write_text(json.dumps({
                "dataset": dataset.model_dump(mode="json"),
                "examples": rows,
            }, ensure_ascii=False, indent=2), encoding="utf-8")
        elif export_format == ExportFormat.JSONL:
            path.write_text(
                "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                encoding="utf-8",
            )
        elif export_format == ExportFormat.CSV:
            with path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=list(rows[0]) if rows else [
                    "input_text", "output_text", "task_type",
                    "source_document_id", "source_chunk_id", "quality_scores",
                ])
                writer.writeheader()
                for row in rows:
                    row = dict(row)
                    row["quality_scores"] = json.dumps(row["quality_scores"], ensure_ascii=False)
                    writer.writerow(row)
        return path
