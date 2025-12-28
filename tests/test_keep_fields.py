import unittest

from mailmerge import NAMESPACES, OptionKeepFields
from tests.utils import (
    MERGE_FIELDS_TRUE_XPATH,
    SEPARATE_TEXT_FIELDS_XPATH,
    SIMPLE_FIELDS_TEXT_FIELDS_XPATH,
    TEXTS_XPATH,
    EtreeMixin,
)

VALUES = {"first": "one", "three_simple": "three_simple"}
TEST_DOCX = "test_keep_fields.docx"
TEST_DOCX_OUT = "tests/output/test_keep_fields_%s.docx"


class MergeParamsTest(EtreeMixin, unittest.TestCase):
    """Tests the three values of the keep_fields parameter

    The test is done using 4 MERGEFIELD fields
    one - complex field, having data
    two - complex field, no data
    three_simple - simple field, having data
    four_simple - simple field, no data
    """

    def test_keep_fields_all(self):
        """tests if all fields are merged"""
        keep_fields = OptionKeepFields.ALL
        document, root_elem = self.merge(
            TEST_DOCX,
            VALUES,
            mm_kwargs={"keep_fields": keep_fields},
            # output=TEST_DOCX_OUT % keep_fields
        )

        self.assertListEqual(
            document.get_settings().getroot().xpath(MERGE_FIELDS_TRUE_XPATH, namespaces=NAMESPACES),
            [],
        )
        self.assertListEqual(
            root_elem.xpath(TEXTS_XPATH, namespaces=NAMESPACES),
            ["one", "«second»", "three_simple", "«four_simple»"],
        )
        self.assertListEqual(root_elem.xpath(SEPARATE_TEXT_FIELDS_XPATH, namespaces=NAMESPACES), ["one", "«second»"])
        self.assertListEqual(
            root_elem.xpath(SIMPLE_FIELDS_TEXT_FIELDS_XPATH, namespaces=NAMESPACES),
            ["three_simple", "«four_simple»"],
        )

    def test_keep_fields_some(self):
        """tests if all fields are merged"""
        keep_fields = OptionKeepFields.SOME
        document, root_elem = self.merge(
            TEST_DOCX,
            VALUES,
            mm_kwargs={"keep_fields": keep_fields},
            # output=TEST_DOCX_OUT % keep_fields
        )

        self.assertListEqual(
            document.get_settings().getroot().xpath(MERGE_FIELDS_TRUE_XPATH, namespaces=NAMESPACES),
            [],
        )
        self.assertListEqual(
            root_elem.xpath(TEXTS_XPATH, namespaces=NAMESPACES),
            ["one", "«second»", "three_simple", "«four_simple»"],
        )
        self.assertListEqual(root_elem.xpath(SEPARATE_TEXT_FIELDS_XPATH, namespaces=NAMESPACES), ["«second»"])
        self.assertListEqual(
            root_elem.xpath(SIMPLE_FIELDS_TEXT_FIELDS_XPATH, namespaces=NAMESPACES),
            ["«four_simple»"],
        )

    def test_keep_fields_none(self):
        """tests if all fields are merged"""
        keep_fields = OptionKeepFields.NONE
        document, root_elem = self.merge(
            TEST_DOCX,
            VALUES,
            mm_kwargs={"keep_fields": keep_fields},
            # output=TEST_DOCX_OUT % keep_fields
        )

        self.assertListEqual(
            document.get_settings().getroot().xpath(MERGE_FIELDS_TRUE_XPATH, namespaces=NAMESPACES),
            [],
        )
        self.assertListEqual(root_elem.xpath(TEXTS_XPATH, namespaces=NAMESPACES), ["one", "", "three_simple", ""])
        self.assertListEqual(root_elem.xpath(SEPARATE_TEXT_FIELDS_XPATH, namespaces=NAMESPACES), [])
        self.assertListEqual(root_elem.xpath(SIMPLE_FIELDS_TEXT_FIELDS_XPATH, namespaces=NAMESPACES), [])

    def test_keep_fields_all_multiple(self):
        """tests if all fields are merged"""
        keep_fields = OptionKeepFields.ALL
        document, root_elem = self.merge_templates(
            TEST_DOCX,
            [VALUES, VALUES],
            mm_kwargs={"keep_fields": keep_fields},
            # output=TEST_DOCX_OUT % keep_fields,
        )

        self.assertListEqual(
            document.get_settings().getroot().xpath(MERGE_FIELDS_TRUE_XPATH, namespaces=NAMESPACES),
            [],
        )
        self.assertListEqual(
            root_elem.xpath(TEXTS_XPATH, namespaces=NAMESPACES),
            ["one", "«second»", "three_simple", "«four_simple»", "one", "«second»", "three_simple", "«four_simple»"],
        )
        self.assertListEqual(
            root_elem.xpath(SEPARATE_TEXT_FIELDS_XPATH, namespaces=NAMESPACES), ["one", "«second»", "one", "«second»"]
        )
        self.assertListEqual(
            root_elem.xpath(SIMPLE_FIELDS_TEXT_FIELDS_XPATH, namespaces=NAMESPACES),
            ["three_simple", "«four_simple»", "three_simple", "«four_simple»"],
        )

    def test_keep_fields_some_multiple(self):
        """tests if all fields are merged"""
        keep_fields = OptionKeepFields.SOME
        document, root_elem = self.merge_templates(
            TEST_DOCX,
            [VALUES, VALUES],
            mm_kwargs={"keep_fields": keep_fields},
            # output=TEST_DOCX_OUT % keep_fields,
        )

        self.assertListEqual(
            document.get_settings().getroot().xpath(MERGE_FIELDS_TRUE_XPATH, namespaces=NAMESPACES),
            [],
        )
        self.assertListEqual(
            root_elem.xpath(TEXTS_XPATH, namespaces=NAMESPACES),
            ["one", "«second»", "three_simple", "«four_simple»", "one", "«second»", "three_simple", "«four_simple»"],
        )
        self.assertListEqual(
            root_elem.xpath(SEPARATE_TEXT_FIELDS_XPATH, namespaces=NAMESPACES), ["«second»", "«second»"]
        )
        self.assertListEqual(
            root_elem.xpath(SIMPLE_FIELDS_TEXT_FIELDS_XPATH, namespaces=NAMESPACES),
            ["«four_simple»", "«four_simple»"],
        )
