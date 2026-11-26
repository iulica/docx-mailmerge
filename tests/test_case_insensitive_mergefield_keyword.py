import unittest
from os import path

from mailmerge import NAMESPACES, MailMerge
from tests.utils import TEXTS_XPATH, EtreeMixin, get_document_body_parts

VALUES = {"AA": "UPPER_VALUE", "aa": "lower_value"}
# 6 cases: simple and complex fields, with the keyword MERGEFIELD, mergefield and mErGeFiElD.
# Each case has an AA and an aa field. The same 6 cases are in the body, the header and the footer.
# In the body the complex field instruction is in one w:instrText, in the header and footer it is split in three.
TEST_DOCX = "test_case_insensitive_mergefield-keyword.docx"
PARTS = ("document", "hdr", "ftr")


class CaseInsensitiveKeywordTest(EtreeMixin, unittest.TestCase):
    def test_discovery(self):
        with MailMerge(path.join(path.dirname(__file__), TEST_DOCX)) as document:
            self.assertEqual(document.get_merge_fields(), {"AA", "aa"})

    def test_merge(self):
        document, _root_elem = self.merge(TEST_DOCX, VALUES)

        for part_name in PARTS:
            with self.subTest(part=part_name):
                (part,) = get_document_body_parts(document, endswith=part_name)
                texts = part.getroot().xpath(TEXTS_XPATH, namespaces=NAMESPACES)
                self.assertEqual(texts.count("UPPER_VALUE"), 6)
                self.assertEqual(texts.count("lower_value"), 6)
                self.assertNotIn("old", texts)
