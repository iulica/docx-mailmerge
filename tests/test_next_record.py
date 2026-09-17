import unittest

from mailmerge import NAMESPACES
from tests.utils import EtreeMixin


class NextRecordsTest(EtreeMixin, unittest.TestCase):
    """
    Testing next records
    """

    def test_next_record(self):
        """
        Tests if the next record field works
        """
        values = ["one", "two", "three", "four", "five"]
        _document, root_elem = self.merge_templates(
            "test_next_record.docx",
            [{"field": value} for value in values],
            # output="tests/test_output_next_record.docx"
        )

        self.assertFalse(root_elem.xpath("//MergeField", namespaces=NAMESPACES))
        fields = root_elem.xpath("//w:t/text()", namespaces=NAMESPACES)
        expected = [v for value in values + [""] * 3 for v in [value, "/", value]]
        self.assertListEqual(fields, expected)

    def test_next_if_record(self):
        """
        Tests if the next record field works
        """
        values = ["one", "two", "three", "four", "five"]
        _document, root_elem = self.merge_templates(
            "test_nextif.docx",
            [{"fieldname": value} for value in values],
            # output="tests/test_output_next_record.docx"
        )

        self.assertFalse(root_elem.xpath("//MergeField", namespaces=NAMESPACES))
        fields = root_elem.xpath("//w:t/text()", namespaces=NAMESPACES)
        expected = ["one", "two", "three", "three", "four", "four", "five", "five"]
        self.assertListEqual(fields, expected)

    def test_skip_if_record(self):
        """
        Tests if the next record field works
        """
        values = ["one", "two", "three", "four", "five"]
        _document, root_elem = self.merge_templates(
            "test_skipif.docx",
            [{"fieldname": value} for value in values],
            # output="tests/test_output_next_record.docx"
        )

        self.assertFalse(root_elem.xpath("//MergeField", namespaces=NAMESPACES))
        fields = root_elem.xpath("//w:t/text()", namespaces=NAMESPACES)
        expected = ["two", "two", "three", "three", "four", "four", "five", "five"]
        self.assertListEqual(fields, expected)
