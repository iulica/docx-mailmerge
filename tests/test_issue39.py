import io
import unittest
import zipfile

from mailmerge import MailMerge


def make_docx(document_xml):
    docx = io.BytesIO()
    with zipfile.ZipFile(docx, "w") as archive:
        archive.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>""",
        )
        archive.writestr("word/document.xml", document_xml)
    docx.seek(0)
    return docx


class Issue39Test(unittest.TestCase):
    def test_ignores_simple_field_without_run(self):
        document_xml = """<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:fldSimple w:instr="PAGEREF _Toc1 \\h"/>
    </w:p>
  </w:body>
</w:document>"""

        with MailMerge(make_docx(document_xml)) as document:
            self.assertEqual(document.get_merge_fields(), set())
