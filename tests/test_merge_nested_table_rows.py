import tempfile
import unittest
from os import path

from mailmerge import NAMESPACES, MailMerge
from tests.utils import EtreeMixin, get_document_body_part


class MergeNestedTableRowsTest(EtreeMixin, unittest.TestCase):
    def setUp(self):
        self.document = MailMerge(path.join(path.dirname(__file__), "test_merge_nested_table_rows.docx"))

    def test_merge_rows(self):
        self.assertEqual(
            self.document.get_merge_fields(),
            {
                "name",
                "version",
                "note",
                "desc",
            },
        )

        self.document.merge(
            name=[
                {"name": "Jon", "version": "1", "note": "A", "desc": "Hey"},
                {"name": "Snow", "version": "2", "note": "A+", "desc": "Wow"},
            ],
        )

        if True:
            with tempfile.TemporaryFile() as outfile:
                self.document.write(outfile)
        else:
            with open("tests/output/test_output_merge_nested_table_rows.docx", "wb") as outfile:
                self.document.write(outfile)

        root_elem = get_document_body_part(self.document).getroot()
        self.assertEqual(len(root_elem.findall(".//{{{w}}}tbl".format(**NAMESPACES))), 2)

    def test_merge_rows_replace_mode_false(self):
        self.document.options.table_rows_replace_mode = False

        self.document.merge(
            name=[
                {"name": "Jon", "version": "1", "note": "A", "desc": "Hey"},
                {"name": "Snow", "version": "2", "note": "A+", "desc": "Wow"},
            ],
        )

        if True:
            with tempfile.TemporaryFile() as outfile:
                self.document.write(outfile)
        else:
            with open("tests/output/test_output_merge_nested_table_rows.docx", "wb") as outfile:
                self.document.write(outfile)

        root_elem = get_document_body_part(self.document).getroot()
        self.assertEqual(len(root_elem.findall(".//{{{w}}}tbl".format(**NAMESPACES))), 2)
        second_table_rows = root_elem.findall(".//{{{w}}}tbl//{{{w}}}tbl//{{{w}}}tr".format(**NAMESPACES))
        self.assertEqual(len(second_table_rows), 3)

    def test_merge_rows_replace_mode_true(self):
        self.document.options.table_rows_replace_mode = True

        self.document.merge(
            name=[
                {"name": "Jon", "version": "1", "note": "A", "desc": "Hey"},
                {"name": "Snow", "version": "2", "note": "A+", "desc": "Wow"},
            ],
        )

        if True:
            with tempfile.TemporaryFile() as outfile:
                self.document.write(outfile)
        else:
            with open("tests/output/test_output_merge_nested_table_rows.docx", "wb") as outfile:
                self.document.write(outfile)

        root_elem = get_document_body_part(self.document).getroot()
        self.assertEqual(len(root_elem.findall(".//{{{w}}}tbl".format(**NAMESPACES))), 2)
        second_table_rows = root_elem.findall(".//{{{w}}}tbl//{{{w}}}tbl//{{{w}}}tr".format(**NAMESPACES))
        self.assertEqual(len(second_table_rows), 2)

    def test_merge_rows_replace_mode_overflow(self):
        self.document.options.table_rows_replace_mode = True

        with self.assertRaises(IndexError):
            self.document.merge(
                name=[
                    {"name": "Jon", "version": "1", "note": "A", "desc": "Hey"},
                    {"name": "Snow", "version": "2", "note": "A+", "desc": "Wow"},
                    {"name": "Stark", "version": "3", "note": "F", "desc": "Ohhh"},
                ],
            )

    def tearDown(self):
        self.document.docx.close()
