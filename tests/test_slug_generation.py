import unittest

from src.slug import slug_from_title, slug_with_suffix


class SlugGenerationTest(unittest.TestCase):
    def test_slug_from_title(self) -> None:
        self.assertEqual(slug_from_title("VPN for friends"), "VPN_FOR_FRIENDS")
        self.assertEqual(slug_from_title("Finpipe v1.0.0"), "FINPIPE_V1_0_0")

    def test_slug_with_suffix(self) -> None:
        self.assertEqual(slug_with_suffix("VPN_FOR_FRIENDS", 1), "VPN_FOR_FRIENDS")
        self.assertEqual(slug_with_suffix("VPN_FOR_FRIENDS", 2), "VPN_FOR_FRIENDS_2")


if __name__ == "__main__":
    unittest.main()
