import unittest
from datetime import date
from unittest.mock import MagicMock, patch

from src.models import Milestone


class SlugGenerationTest(unittest.TestCase):
    def test_slug_from_title(self) -> None:
        self.assertEqual(Milestone.slug_from_title("VPN for friends"), "VPN_FOR_FRIENDS")
        self.assertEqual(Milestone.slug_from_title("Finpipe v1.0.0"), "FINPIPE_V1_0_0")

    def test_create_with_title_appends_suffix_when_slug_exists(self) -> None:
        existing = MagicMock()
        existing.scalars.return_value.first.side_effect = [object(), None]

        session = MagicMock()
        session.execute.return_value = existing
        session.__enter__.return_value = session
        session.__exit__.return_value = None

        with patch("src.models.Session", return_value=session):
            milestone = Milestone.create_with_title(
                title="VPN for friends",
                happened_at=date(2026, 6, 22),
            )

        self.assertEqual(milestone.slug, "VPN_FOR_FRIENDS_2")


if __name__ == "__main__":
    unittest.main()
