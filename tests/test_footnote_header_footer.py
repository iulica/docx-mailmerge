import unittest

from mailmerge import NAMESPACES
from tests.utils import TEXTS_XPATH, EtreeMixin, get_document_body_part, get_document_body_parts

FOOTNOTE_XPATH = "//w:footnote[@w:id = '1']/w:p/w:r/w:t/text()"


class FootnoteHeaderFooterTest(EtreeMixin, unittest.TestCase):
    # @TODO test missing values
    # @TODO test if separator isn't section
    # @TODO test headers/footers with relations
    def test_all_header_footer(self):
        values = ["one", "two", "three"]
        # header/footer/footnotes don't work with multiple replacements, only with merge
        # fix this when it is implemented
        document, _root_elem = self.merge_templates(
            "test_footnote_header_footer.docx",
            [
                {
                    "fieldname": value,
                    "footerfield": "f_" + value,
                    "headerfield": "h_" + value,
                    "footerfirst": "ff_" + value,
                    "headerfirst": "hf_" + value,
                    "footereven": "fe_" + value,
                    "headereven": "he_" + value,
                }
                for value in values
            ],
            separator="nextPage_section",
            # output="tests/output/test_output_footnote_header_footer.docx"
        )

        footers = sorted(
            [
                "".join(footer_doc_tree.getroot().xpath(TEXTS_XPATH, namespaces=NAMESPACES))
                for footer_doc_tree in get_document_body_parts(document, endswith="ftr")
            ]
        )
        self.assertListEqual(
            footers,
            sorted(
                [
                    footer
                    for value in values
                    for footer in [
                        f"Footer on even page fe_{value}",
                        f"Footer on every page f_{value}",
                        f"Footer on first page ff_{value}",
                    ]
                ]
                + ["Footer on even page ", "Footer on every page ", "Footer on first page "]
            ),
        )

        headers = sorted(
            [
                "".join(header_doc_tree.getroot().xpath(TEXTS_XPATH, namespaces=NAMESPACES))
                for header_doc_tree in get_document_body_parts(document, endswith="hdr")
            ]
        )
        self.assertListEqual(
            headers,
            sorted(
                [
                    header
                    for value in values
                    for header in [
                        f"Header even: he_{value}",
                        f"Header on every page: h_{value}",
                        f"Header on first page: hf_{value}",
                    ]
                ]
                + ["Header even: ", "Header on every page: ", "Header on first page: "]
            ),
        )

    @unittest.expectedFailure
    def test_all_footnote(self):
        values = ["one", "two", "three"]
        # header/footer/footnotes don't work with multiple replacements, only with merge
        # fix this when it is implemented
        document, _root_elem = self.merge_templates(
            "test_footnote_header_footer.docx",
            [
                {
                    "fieldname": value,
                    "footerfield": "f_" + value,
                    "headerfield": "h_" + value,
                    "footerfirst": "ff_" + value,
                    "headerfirst": "hf_" + value,
                    "footereven": "fe_" + value,
                    "headereven": "he_" + value,
                }
                for value in values
            ],
            separator="nextPage_section",
            # output="tests/output/test_output_footnote_header_footer.docx"
        )

        footnote_root_elem = get_document_body_part(document, "footnotes").getroot()
        footnote = "".join(footnote_root_elem.xpath(FOOTNOTE_XPATH, namespaces=NAMESPACES))
        correct_footnote = " Merge : one "
        self.assertEqual(footnote, correct_footnote)

    def test_only_merge(self):
        values = ["one", "two", "three"]
        document, _root_elem = self.merge(
            "test_footnote_header_footer.docx",
            next(
                {
                    "fieldname": value,
                    "footerfield": "f_" + value,
                    "headerfield": "h_" + value,
                    "footerfirst": "ff_" + value,
                    "headerfirst": "hf_" + value,
                    "footereven": "fe_" + value,
                    "headereven": "he_" + value,
                }
                for value in values
            ),
            # output="tests/output/test_output_one_footnote_header_footer.docx"
        )

        footnote_root_elem = get_document_body_part(document, "footnotes").getroot()
        footnote = "".join(footnote_root_elem.xpath(FOOTNOTE_XPATH, namespaces=NAMESPACES))
        self.assertEqual(footnote, " Merge : one")

        footers = sorted(
            [
                "".join(footer_doc_tree.getroot().xpath(TEXTS_XPATH, namespaces=NAMESPACES))
                for footer_doc_tree in get_document_body_parts(document, endswith="ftr")
            ]
        )
        value = values[0]
        self.assertListEqual(
            footers,
            [
                f"Footer on even page fe_{value}",
                f"Footer on every page f_{value}",
                f"Footer on first page ff_{value}",
            ],
        )

        headers = sorted(
            [
                "".join(header_doc_tree.getroot().xpath(TEXTS_XPATH, namespaces=NAMESPACES))
                for header_doc_tree in get_document_body_parts(document, endswith="hdr")
            ]
        )
        self.assertListEqual(
            headers,
            [
                f"Header even: he_{value}",
                f"Header on every page: h_{value}",
                f"Header on first page: hf_{value}",
            ],
        )

    def test_footer(self):
        values = ["one", "two"]
        # header/footer/footnotes don't work with multiple replacements, only with merge
        # fix this when it is implemented
        _document, _root_elem = self.merge_templates(
            "test_footer.docx",
            [
                {
                    "footer": value,
                }
                for value in values
            ],
            separator="nextPage_section",
            # output="tests/output/test_footer.docx"
        )
