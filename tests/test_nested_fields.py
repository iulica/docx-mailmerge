import unittest
import tempfile
from os import path
from lxml import etree

from mailmerge import MailMerge, NAMESPACES
from tests.utils import EtreeMixin, get_document_body_part

class NestedFieldsTest(EtreeMixin, unittest.TestCase):
    """
    Testing multiple complex fields begin-end, nested or not
    """
    
    def test_field_outside(self):
        """
        Fields are disjoint, no interference between the two complex fields
        """
        with MailMerge(path.join(path.dirname(__file__), 'test_nested_if_outside.docx')) as document:
            self.assertEqual(document.get_merge_fields(),
                             set(['fieldname']))
            
            document.merge(fieldname="one")

            # self.assert_equal_tree_debug(get_document_body_part(document).getroot(), get_document_body_part(document).getroot()[0])
            self.assertEqual(
                get_document_body_part(document).getroot().xpath('.//w:fldChar/@w:fldCharType', namespaces=NAMESPACES),
                ["begin", "separate", "end"])

            self.assertEqual(
                get_document_body_part(document).getroot().xpath('.//w:fldChar[@w:fldCharType="end"]/../following-sibling::w:r/w:t/text()', namespaces=NAMESPACES),
                ["one"])


    def test_field_inside(self):
        """
        begin if
            begin merge fieldname
            end
            <>
            "one"
            
            begin if
                simple fieldname
                =
                "two"
                "two" 
                "more: 
                simple fieldname
                "
            end

            "- one -"
        end
        """
        with MailMerge(path.join(path.dirname(__file__), 'test_nested_if_inside.docx')) as document:
            self.assertEqual(document.get_merge_fields(),
                             set(['fieldname']))

            document.merge(fieldname="five")                

            # debug to force writing down the xml documents
            # self.assert_equal_tree_debug(get_document_body_part(document).getroot(), get_document_body_part(document).getroot()[0])
            self.assertEqual(
                get_document_body_part(document).getroot().xpath('.//w:fldChar/@w:fldCharType', namespaces=NAMESPACES),
                ["begin", "begin", "separate", "end", "separate", "end"])

            self.assertEqual(
                get_document_body_part(document).getroot().xpath(
                    './/w:fldChar[@w:fldCharType="begin"][1]/../following-sibling::w:r/w:t/text()', namespaces=NAMESPACES),
                ["more: "])

            self.assertEqual(
                "".join(get_document_body_part(document).getroot().xpath(
                    './/w:fldChar[@w:fldCharType="begin"][1]/../following-sibling::w:r/w:instrText/text()', namespaces=NAMESPACES)),
                """ IF five <> "one" " IF five = "two" "two" "more: five" \\* MERGEFORMAT more: five" "- one -" \\* MERGEFORMAT five""")
