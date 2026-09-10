import unittest

from app.importers.csv_importer import is_valid_mobile, normalize_phone


class PhoneNormalizationTests(unittest.TestCase):
    def test_brazilian_mobile_receives_country_code(self) -> None:
        self.assertEqual("5514991139046", normalize_phone("(14) 99113-9046"))

    def test_existing_country_code_is_not_duplicated(self) -> None:
        self.assertEqual("5514991139046", normalize_phone("+55 14 99113-9046"))

    def test_international_dialing_prefix_is_removed(self) -> None:
        self.assertEqual("5514991139046", normalize_phone("0055 14 99113-9046"))

    def test_excel_integer_float_is_normalized(self) -> None:
        self.assertEqual("5514991139046", normalize_phone(14991139046.0))

    def test_mobile_validation_uses_number_after_country_code_and_ddd(self) -> None:
        self.assertTrue(is_valid_mobile("5514991139046"))
        self.assertFalse(is_valid_mobile("551433331234"))


if __name__ == "__main__":
    unittest.main()
