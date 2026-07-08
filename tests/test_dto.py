import unittest
from datetime import UTC, date, datetime, timedelta
import sys
from pathlib import Path
from src.features.milestones.dto import (
    MilestoneCreateDTO,
    today_in_timezone,
    validate_happened_at_not_future,
)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TODAY = date.today()
YESTERDAY = TODAY - timedelta(days=1)


class TitleValidationTest(unittest.TestCase):
    def _make(self, title: str) -> MilestoneCreateDTO:
        return MilestoneCreateDTO(title=title, happened_at=YESTERDAY)

    def test_valid_title(self) -> None:
        dto = self._make("VPN for friends")
        self.assertEqual(dto.title, "VPN for friends")

    def test_title_is_stripped(self) -> None:
        dto = self._make("  Hello  ")
        self.assertEqual(dto.title, "Hello")
    #
    # def test_empty_title_raises(self) -> None:
    #     with self.assertRaises(ValidationError):
    #         self._make("")
    #
    # def test_whitespace_only_title_raises(self) -> None:
    #     with self.assertRaises(ValidationError):
    #         self._make("   ")

    # def test_cyrillic_title_raises(self) -> None:
    #     with self.assertRaises(ValidationError):
    #         self._make("Привет мир")

    def test_allowed_special_chars(self) -> None:
        dto = self._make("Finpipe v1.0 - release")
        self.assertEqual(dto.title, "Finpipe v1.0 - release")


class DateValidationTest(unittest.TestCase):
    def test_past_date_ok(self) -> None:
        dto = MilestoneCreateDTO(title="Test", happened_at=YESTERDAY)
        self.assertEqual(dto.happened_at, YESTERDAY)

    def test_today_ok(self) -> None:
        dto = MilestoneCreateDTO(title="Test", happened_at=TODAY)
        self.assertEqual(dto.happened_at, TODAY)

    def test_today_in_utc_matches_server_utc_date(self) -> None:
        self.assertEqual(today_in_timezone("UTC"), datetime.now(UTC).date())

    def test_invalid_timezone_falls_back_to_utc(self) -> None:
        self.assertEqual(today_in_timezone("Not/A_Zone"), datetime.now(UTC).date())

    def test_future_date_raises(self) -> None:
        with self.assertRaises(ValueError):
            validate_happened_at_not_future(TODAY + timedelta(days=1), "UTC")


class DescriptionValidationTest(unittest.TestCase):
    def test_description_stripped(self) -> None:
        dto = MilestoneCreateDTO(title="Test", happened_at=YESTERDAY, description="  hello  ")
        self.assertEqual(dto.description, "hello")

    def test_description_defaults_to_empty(self) -> None:
        dto = MilestoneCreateDTO(title="Test", happened_at=YESTERDAY)
        self.assertEqual(dto.description, "")


if __name__ == "__main__":
    unittest.main()
