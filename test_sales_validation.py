import csv
import pytest
import sales_validation



@pytest.fixture
def valid_csv(tmp_path):
    filepath = tmp_path / "SALES_DATA_20260827120000.csv"

    headers = [
        "transaction_id",
        "timestamp",
        "store_id",
        "product_id",
        "quantity",
        "unit_price",
        "total_amount",
        "payment_method"
    ]

    rows = [
        ["T001", "2026-08-27 10:00:00", "S001", "P001", "2", "10.00", "20.00", "Cash"],
        ["T002", "2026-08-27 11:00:00", "S002", "P002", "3", "15.00", "45.00", "Card"]
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

    return filepath


@pytest.fixture
def validator():
    return sales_validation.SalesDataValidator()


def test_valid_filename():
    rule = sales_validation.FilenameFormatRule()

    errors = rule.validate(
        "SALES_DATA_20260827120000.csv",
        "SALES_DATA_20260827120000.csv"
    )

    assert errors == []


def test_invalid_filename():
    rule = sales_validation.FilenameFormatRule()

    errors = rule.validate(
        "wrong_file.csv",
        "wrong_file.csv"
    )

    assert errors == ["Incorrect filename format."]


def test_non_empty_file(valid_csv):
    rule = sales_validation.FileIntegrityRule()

    errors = rule.validate(
        str(valid_csv),
        valid_csv.name
    )

    assert errors == []


def test_empty_file(tmp_path):
    filepath = tmp_path / "SALES_DATA_20260827120000.csv"
    filepath.touch()

    rule = sales_validation.FileIntegrityRule()

    errors = rule.validate(
        str(filepath),
        filepath.name
    )

    assert errors == ["CSV file is empty (0-byte file)."]


def test_valid_csv_rows(valid_csv):
    rule = sales_validation.RowContentRule()

    errors = rule.validate(
        str(valid_csv),
        valid_csv.name
    )

    assert errors == []


def test_missing_headers(tmp_path):
    filepath = tmp_path / "SALES_DATA_20260827120000.csv"

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["transaction_id", "timestamp"])

    rule = sales_validation.RowContentRule()

    errors = rule.validate(
        str(filepath),
        filepath.name
    )

    assert "Missing or incorrect header: store_id" in errors
    assert "Missing or incorrect header: product_id" in errors
    assert "Missing or incorrect header: quantity" in errors


def test_duplicate_transaction_id(tmp_path):
    filepath = tmp_path / "SALES_DATA_20260827120000.csv"

    headers = [
        "transaction_id",
        "timestamp",
        "store_id",
        "product_id",
        "quantity",
        "unit_price",
        "total_amount",
        "payment_method"
    ]

    rows = [
        ["T001", "2026-08-27 10:00:00", "S001", "P001", "2", "10", "20", "Cash"],
        ["T001", "2026-08-27 11:00:00", "S002", "P002", "3", "15", "45", "Card"]
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

    rule = sales_validation.RowContentRule()

    errors = rule.validate(
        str(filepath),
        filepath.name
    )

    assert "Row 3: Duplicate transaction_id T001" in errors


def test_invalid_timestamp(tmp_path):
    filepath = tmp_path / "SALES_DATA_20260827120000.csv"

    headers = [
        "transaction_id",
        "timestamp",
        "store_id",
        "product_id",
        "quantity",
        "unit_price",
        "total_amount",
        "payment_method"
    ]

    rows = [
        ["T001", "27-08-2026", "S001", "P001", "2", "10", "20", "Cash"]
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

    rule = sales_validation.RowContentRule()

    errors = rule.validate(
        str(filepath),
        filepath.name
    )

    assert "Row 2: Invalid timestamp format." in errors


def test_negative_quantity(tmp_path):
    filepath = tmp_path / "SALES_DATA_20260827120000.csv"

    headers = [
        "transaction_id",
        "timestamp",
        "store_id",
        "product_id",
        "quantity",
        "unit_price",
        "total_amount",
        "payment_method"
    ]

    rows = [
        ["T001", "2026-08-27 10:00:00", "S001", "P001", "-2", "10", "-20", "Cash"]
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

    rule = sales_validation.RowContentRule()

    errors = rule.validate(
        str(filepath),
        filepath.name
    )

    assert "Row 2: Quantity must be positive." in errors


def test_invalid_numeric_value(tmp_path):
    filepath = tmp_path / "SALES_DATA_20260827120000.csv"

    headers = [
        "transaction_id",
        "timestamp",
        "store_id",
        "product_id",
        "quantity",
        "unit_price",
        "total_amount",
        "payment_method"
    ]

    rows = [
        ["T001", "2026-08-27 10:00:00", "S001", "P001", "abc", "10", "20", "Cash"]
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

    rule = sales_validation.RowContentRule()

    errors = rule.validate(
        str(filepath),
        filepath.name
    )

    assert "Row 2: Invalid numeric value." in errors


def test_incorrect_total_amount(tmp_path):
    filepath = tmp_path / "SALES_DATA_20260827120000.csv"

    headers = [
        "transaction_id",
        "timestamp",
        "store_id",
        "product_id",
        "quantity",
        "unit_price",
        "total_amount",
        "payment_method"
    ]

    rows = [
        ["T001", "2026-08-27 10:00:00", "S001", "P001", "2", "10", "50", "Cash"]
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

    rule = sales_validation.RowContentRule()

    errors = rule.validate(
        str(filepath),
        filepath.name
    )

    assert "Row 2: Total amount calculation incorrect." in errors


def test_missing_field_value(tmp_path):
    filepath = tmp_path / "SALES_DATA_20260827120000.csv"

    headers = [
        "transaction_id",
        "timestamp",
        "store_id",
        "product_id",
        "quantity",
        "unit_price",
        "total_amount",
        "payment_method"
    ]

    rows = [
        ["T001", "2026-08-27 10:00:00", "S001", "P001", "", "10", "20", "Cash"]
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

    rule = sales_validation.RowContentRule()

    errors = rule.validate(
        str(filepath),
        filepath.name
    )

    assert "Row 2: Missing quantity" in errors


def test_inconsistent_timestamp_date(tmp_path):
    filepath = tmp_path / "SALES_DATA_20260827120000.csv"

    headers = [
        "transaction_id",
        "timestamp",
        "store_id",
        "product_id",
        "quantity",
        "unit_price",
        "total_amount",
        "payment_method"
    ]

    rows = [
        ["T001", "2026-08-27 10:00:00", "S001", "P001", "2", "10", "20", "Cash"],
        ["T002", "2026-08-28 11:00:00", "S002", "P002", "3", "15", "45", "Card"]
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

    rule = sales_validation.RowContentRule()

    errors = rule.validate(
        str(filepath),
        filepath.name
    )

    assert "Row 3: Timestamp inconsistent." in errors


def test_validator_accepts_valid_file(validator, valid_csv):
    errors = validator.validate_file(
        str(valid_csv),
        valid_csv.name
    )

    assert errors == []


def test_validator_rejects_invalid_filename(validator, valid_csv):
    errors = validator.validate_file(
        str(valid_csv),
        "wrong.csv"
    )

    assert "Incorrect filename format." in errors


def test_validator_rejects_empty_file(validator, tmp_path):
    filepath = tmp_path / "SALES_DATA_20260827120000.csv"
    filepath.touch()

    errors = validator.validate_file(
        str(filepath),
        filepath.name
    )

    assert "CSV file is empty (0-byte file)." in errors


def test_add_strategy(validator):
    class CustomRule(sales_validation.ValidationStrategy):

        def validate(self, filepath, filename):
            return ["Custom validation error."]

    validator.add_strategy(CustomRule())

    assert len(validator.strategies) == 4



def test_ftp_connect_empty_host():
    manager = sales_validation.FTPClientManager()

    with pytest.raises(ValueError, match="Host address is empty."):
        manager.connect("", "username", "password")


def test_ftp_download_without_connection(tmp_path):
    manager = sales_validation.FTPClientManager()

    filepath = tmp_path / "test.csv"

    with pytest.raises(
        ConnectionError,
        match="FTP server is not connected."
    ):
        manager.download_file(
            "test.csv",
            str(filepath)
        )


def test_ftp_disconnect():
    manager = sales_validation.FTPClientManager()

    manager.disconnect()

    assert manager.is_connected is False
    assert manager.ftp is None
    assert manager.all_files == []



class FakeTextWidget:

    def __init__(self):
        self.messages = []

    def insert(self, position, message):
        self.messages.append(message)

    def see(self, position):
        pass

    def delete(self, start, end):
        self.messages.clear()


def test_logger_log_activity():
    widget = FakeTextWidget()

    logger = sales_validation.LoggerManager(widget)

    logger.log_activity("Test message")

    assert len(widget.messages) == 1
    assert "Test message" in widget.messages[0]


def test_logger_clear():
    widget = FakeTextWidget()

    logger = sales_validation.LoggerManager(widget)

    logger.log_activity("Test message")
    logger.clear()

    assert widget.messages == []


def test_generate_uuid_fallback(monkeypatch):
    widget = FakeTextWidget()

    logger = sales_validation.LoggerManager(widget)

    def fake_get(*args, **kwargs):
        raise Exception("Network error")

    monkeypatch.setattr(
        sales_validation.requests,
        "get",
        fake_get
    )

    result = logger.generate_uuid()

    assert isinstance(result, str)
    assert len(result) > 0


def test_write_and_log_errors(tmp_path, monkeypatch):
    widget = FakeTextWidget()

    logger = sales_validation.LoggerManager(widget)

    monkeypatch.setattr(
        logger,
        "generate_uuid",
        lambda: "TEST-UUID-123"
    )

    log_path = tmp_path / "errors" / "validation_errors.log"

    errors = [
        "Incorrect filename format.",
        ("Data Error", "Invalid quantity.")
    ]

    logger.write_and_log_errors(
        "wrong.csv",
        errors,
        str(log_path)
    )

    assert log_path.exists()

    content = log_path.read_text(encoding="utf-8")

    assert "UUID: TEST-UUID-123" in content
    assert "File: wrong.csv" in content
    assert "Type: Validation Error" in content
    assert "Details: Incorrect filename format." in content
    assert "Type: Data Error" in content
    assert "Details: Invalid quantity." in content