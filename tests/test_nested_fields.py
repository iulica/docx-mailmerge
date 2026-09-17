import unittest
from os import path

from mailmerge import NAMESPACES, MailMerge, MailMergeOptions, OptionAutoUpdateFields
from tests.utils import EtreeMixin, get_document_body_part

UPDATE_FIELDS_TRUE_XPATH = './w:updateFields[@w:val="true"]'
UPDATE_FIELDS_XPATH = "./w:updateFields/@w:val"


class NestedFieldsTest(EtreeMixin, unittest.TestCase):
    """
    Testing multiple complex fields begin-end, nested or not
    """

    def test_field_outside(self):
        """
        Fields are disjoint, no interference between the two complex fields
        """
        with MailMerge(
            path.join(path.dirname(__file__), "test_nested_if_outside.docx"),
            options=MailMergeOptions(merge_if_fields=True),
        ) as document:
            # self.assertEqual(document.get_merge_fields(), set(["fieldname"]))
            self.assertEqual(document.get_merge_fields(), {"", "fieldname"})

            document.merge(fieldname="one")

            # self.assert_equal_tree_debug(get_document_body_part(document).getroot(), get_document_body_part(document).getroot()[0])
            self.assertEqual(
                get_document_body_part(document).getroot().xpath(".//w:fldChar/@w:fldCharType", namespaces=NAMESPACES),
                # ["begin", "separate", "end"],
                [],
            )

            # self.assertEqual(
            #     get_document_body_part(document)
            #     .getroot()
            #     .xpath(
            #         './/w:fldChar[@w:fldCharType="end"]/../following-sibling::w:r/w:t/text()',
            #         namespaces=NAMESPACES,
            #     ),
            #     ["one"],
            # )
            self.assertEqual(
                get_document_body_part(document)
                .getroot()
                .xpath(
                    ".//w:r/w:t/text()",
                    namespaces=NAMESPACES,
                ),
                ["true", "one"],
            )

    def test_outside_auto_update_fields(self):
        """
        Fields are disjoint, no interference between the two complex fields
        """
        values = {"fieldname": "one"}
        document, root_elem = self.merge(
            "test_nested_if_outside.docx",
            values,
            mm_kwargs={"enable_experimental": True},
            # output="tests/output/test_output_nested_if_outside.docx"
        )
        self.assertListEqual(
            document.get_settings().getroot().xpath(UPDATE_FIELDS_TRUE_XPATH, namespaces=NAMESPACES),
            [],
        )

        document, root_elem = self.merge(
            "test_nested_if_outside.docx",
            values,
            mm_kwargs={'auto_update_fields_on_open': OptionAutoUpdateFields.AUTO, 'merge_if_fields': True},
            # output="tests/output/test_output_nested_if_outside.docx"
        )
        self.assertListEqual(
            document.get_settings().getroot().xpath(UPDATE_FIELDS_TRUE_XPATH, namespaces=NAMESPACES),
            [],
        )

        document, _root_elem = self.merge(
            "test_nested_if_outside.docx",
            values,
            mm_kwargs={'auto_update_fields_on_open': OptionAutoUpdateFields.ALWAYS, 'merge_if_fields': True},
            # output="tests/output/test_output_nested_if_outside.docx"
        )
        self.assertListEqual(
            document.get_settings().getroot().xpath(UPDATE_FIELDS_XPATH, namespaces=NAMESPACES),
            ["true"],
        )

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
        with MailMerge(
            path.join(path.dirname(__file__), "test_nested_if_inside.docx"),
            options=MailMergeOptions(merge_if_fields=True),
        ) as document:
            self.assertEqual(document.get_merge_fields(), {""})

            document.merge(fieldname="five")

            # debug to force writing down the xml documents
            # self.assert_equal_tree_debug(get_document_body_part(document).getroot(), get_document_body_part(document).getroot()[0])
            self.assertEqual(
                get_document_body_part(document).getroot().xpath(".//w:fldChar/@w:fldCharType", namespaces=NAMESPACES),
                [],
                # ["begin", "begin", "separate", "end", "separate", "end"],
            )

            self.assertEqual(
                get_document_body_part(document)
                .getroot()
                .xpath(
                    ".//w:r/w:t/text()",
                    namespaces=NAMESPACES,
                ),
                ["more: five"],
            )

            self.assertEqual(
                "".join(
                    get_document_body_part(document)
                    .getroot()
                    .xpath(
                        './/w:fldChar[@w:fldCharType="begin"][1]/../following-sibling::w:r/w:instrText/text()',
                        namespaces=NAMESPACES,
                    )
                ),
                "",
                # """ IF five <> "one" " IF five = "two" "two" "more: five" \\* MERGEFORMAT more: five" "- one -" \\* MERGEFORMAT five""",
            )

    def test_inside_auto_update_fields(self):
        """
        Fields are nested, auto update fields
        """
        values = {"fieldname": "one"}
        document, root_elem = self.merge(
            "test_nested_if_inside.docx",
            values,
            mm_kwargs={},
            # output="tests/output/test_output_nested_if_inside.docx"
        )
        self.assertListEqual(
            document.get_settings().getroot().xpath(UPDATE_FIELDS_TRUE_XPATH, namespaces=NAMESPACES),
            [],
        )

        document, _root_elem = self.merge(
            "test_nested_if_inside.docx",
            values,
            mm_kwargs={'auto_update_fields_on_open': OptionAutoUpdateFields.AUTO, 'merge_if_fields': True},
            # output="tests/output/test_output_nested_if_inside.docx"
        )
        self.assertListEqual(
            document.get_settings().getroot().xpath(UPDATE_FIELDS_XPATH, namespaces=NAMESPACES),
            ["true"],
        )
