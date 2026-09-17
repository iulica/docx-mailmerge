import unittest

from mailmerge import NAMESPACES
from tests.utils import EtreeMixin

DOCPR_TAG = "wp:docPr"


class MergeTemplatesWithPicturesTest(EtreeMixin, unittest.TestCase):
    def test_duplicate_docPr(self):
        _document, root_elem = self.merge_templates(
            "test_input_duplicate_id.docx", [{"field": "test1"}, {"field": "test2"}]
        )

        docPr_ids = root_elem.xpath("//wp:docPr/@id", namespaces=NAMESPACES)

        self.assertEqual(len(docPr_ids), len(set(docPr_ids)))
