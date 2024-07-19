import tempfile
import unittest
from os import path

from mailmerge import NAMESPACES, MailMerge
from tests.utils import EtreeMixin, get_document_body_part


class MergeMultipleTableRowsTest(EtreeMixin, unittest.TestCase):
    def setUp(self):
        self.document = MailMerge(
            path.join(path.dirname(__file__), "test_merge_multiple_table_rows.docx")
        )

    def test_merge_rows(self):
        self.assertEqual(
            self.document.get_merge_fields(),
            {
                "student_name",
                "study_name",
                "class_name",
                "class_code",
                "class_grade",
                "thesis_grade",
            },
        )

        self.document.merge(
            student_name="Bouke Haarsma",
            study="Industrial Engineering and Management",
            thesis_grade="A",
        )

        self.document.merge_rows(
            "class_code",
            [
                {
                    "class_code": "ECON101",
                    "class_name": "Economics 101",
                    "class_grade": "A",
                },
                {
                    "class_code": "ECONADV",
                    "class_name": "Economics Advanced",
                    "class_grade": "B",
                },
                {
                    "class_code": "OPRES",
                    "class_name": "Operations Research",
                    "class_grade": "A",
                },
            ],
        )

        with tempfile.TemporaryFile() as outfile:
            self.document.write(outfile)

        root_elem = get_document_body_part(self.document).getroot()
        self.assertFalse(root_elem.xpath("//MergeField", namespaces=NAMESPACES))
        fields = root_elem.xpath("//w:t/text()", namespaces=NAMESPACES)
        field_count = len([f for f in fields if f == "ECON101"])
        self.assertEqual(field_count, 2)
