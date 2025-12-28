import unittest

from mailmerge import NAMESPACES, OptionKeepFields
from tests.utils import (
    MERGE_FIELDS_XPATH,
    SEPARATE_TEXT_FIELDS_XPATH,
    SIMPLE_FIELDS_TEXT_FIELDS_XPATH,
    TEXTS_XPATH,
    EtreeMixin,
)


class IfTest(EtreeMixin, unittest.TestCase):
    """
    Testing next records

    """

    def test_if_record(self):
        """
        Tests the IF record with paragraphs
        """
        values = ["one", "two", "three", "four", "five"]
        document, root_elem = self.merge_templates(
            "test_if_with_paragraph.docx",
            [{"fieldname": value} for value in values],
            mm_kwargs=dict(merge_if_fields=True),
            # output="tests/test_output_next_record.docx"
        )

        self.assertListEqual(root_elem.xpath(MERGE_FIELDS_XPATH, namespaces=NAMESPACES), [])
        fields = root_elem.xpath(TEXTS_XPATH, namespaces=NAMESPACES)
        expected = [
            v for value in values for v in [value, f"{value}" + (" is " if value == "one" else " is not "), "one"]
        ]
        self.assertListEqual(fields, expected)

    def test_if_record_with_missing_value(self):
        """
        Tests the IF record with paragraphs
        """
        values = ["one", "two", "three", "four", "five"]
        document, root_elem = self.merge_templates(
            "test_if_with_paragraph.docx",
            [{}] + [{"fieldname": value} for value in values] + [{}],
            mm_kwargs=dict(merge_if_fields=True),
            # output="tests/test_output_next_record.docx"
        )

        self.assertListEqual(root_elem.xpath(MERGE_FIELDS_XPATH, namespaces=NAMESPACES), [])
        fields = root_elem.xpath(TEXTS_XPATH, namespaces=NAMESPACES)
        expected = [
            v
            for value in [""] + values + [""]
            for v in [value, f"{value}" + (" is " if value == "one" else " is not "), "one"]
        ]
        self.assertListEqual(fields, expected)

    def test_if_record_with_missing_value_keep_some(self):
        """
        Tests the IF record with paragraphs
        """
        values = ["one", "two"]
        document, root_elem = self.merge_templates(
            "test_if_with_paragraph.docx",
            [{}] + [{"fieldname": value} for value in values] + [{}],
            mm_kwargs=dict(merge_if_fields=True, keep_fields=OptionKeepFields.SOME),
            # output="tests/output/test_output_if_with_paragraph_keep_some.docx",
        )

        self.assertListEqual(root_elem.xpath(MERGE_FIELDS_XPATH, namespaces=NAMESPACES), [])
        self.assertListEqual(
            root_elem.xpath(SIMPLE_FIELDS_TEXT_FIELDS_XPATH, namespaces=NAMESPACES),
            ["«fieldname»", "«fieldname»"],
        )
        self.assertListEqual(
            root_elem.xpath(SEPARATE_TEXT_FIELDS_XPATH, namespaces=NAMESPACES),
            ["«fieldname»", " is not ", "one"] + ["«fieldname»", " is not ", "one"],
        )

    def test_if_record_with_missing_value_keep_all(self):
        """
        Tests the IF record with paragraphs
        """
        values = ["one", "two"]
        document, root_elem = self.merge_templates(
            "test_if_with_paragraph.docx",
            [{}] + [{"fieldname": value} for value in values] + [{}],
            mm_kwargs=dict(merge_if_fields=True, keep_fields=OptionKeepFields.ALL),
            # output="tests/output/test_output_if_with_paragraph_keep_all.docx",
        )

        self.assertListEqual(root_elem.xpath(MERGE_FIELDS_XPATH, namespaces=NAMESPACES), [])
        self.assertListEqual(
            root_elem.xpath(SIMPLE_FIELDS_TEXT_FIELDS_XPATH, namespaces=NAMESPACES),
            ["«fieldname»", "one", "two", "«fieldname»"],
        )
        self.assertListEqual(
            root_elem.xpath(SEPARATE_TEXT_FIELDS_XPATH, namespaces=NAMESPACES),
            ["«fieldname»", " is not ", "one"]
            + ["one is ", "one", "two is not ", "one"]
            + ["«fieldname»", " is not ", "one"],
        )
