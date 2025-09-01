import csv
import os
import subprocess
import tempfile
import pytest
from main import parse_contacts


def test_parse_contacts_creates_csv():
    """Проверяет, что парсет создает CSV, в котором есть заголовки и хотя бы одна строка с офисом"""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "offices.csv")

        parse_contacts(output_path)

        assert os.path.exists(output_path), "CSV файл не был создан"

        with open(output_path, encoding="utf-8") as f:
            reader = list(csv.reader(f, delimiter=";"))
            assert len(reader) > 1, "Файл пуст или нет строк с офисами"
            assert reader[0] == ["Country", "CompanyName", "FullAddress"], "Неверные заголовки"


def test_cli_execution():
    """Проверяет, что скрипт main.py корректно работает при вызове через CLI."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "offices.csv")

        result = subprocess.run(
            ["python", "main.py", output_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        assert result.returncode == 0, f"Скрипт завершился с ошибкой: {result.stderr}"

        assert os.path.exists(output_path), "CSV файл не был создан"

        with open(output_path, encoding="utf-8") as f:
            reader = list(csv.reader(f, delimiter=";"))
            assert len(reader) > 1, "CSV файл пуст"

