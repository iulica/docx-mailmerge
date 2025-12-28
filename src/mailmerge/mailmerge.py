import os
import warnings
from typing import Optional

# import locale
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree

from .constants import CONTENT_TYPES_PARTS, NAMESPACES
from .field import SkipRecord
from .mergedata import MergeData
from .mergeoptions import MailMergeOptions, OptionAutoUpdateFields, OptionKeepFields
from .part import MergeDocument, MergeHeaderFooterDocument, Part
from .rels import RelationsDocument


class MailMergeDocx:
    """
    DOCX specific operations
    """

    def __init__(self, file):
        self.zip = ZipFile(file)
        self.zip_is_closed = False
        self.parts = {}  # zi_part: ElementTree
        self.category_part_map = {}  # category: [zi, ...]

    def fill_parts(self):
        content_types_zi = self.zip.getinfo("[Content_Types].xml")
        content_types = etree.parse(self.zip.open(content_types_zi), parser=None)
        self.category_part_map["content_types"] = [content_types_zi]
        self.parts[content_types_zi] = dict(part=content_types)
        for file in content_types.findall("{%(ct)s}Override" % NAMESPACES):
            part_type = file.attrib["ContentType" % NAMESPACES]
            category = CONTENT_TYPES_PARTS.get(part_type)
            if category:
                zi, self.parts[zi] = self.__get_tree_of_file(file)
                self.category_part_map.setdefault(category, []).append(zi)

    def __get_tree_of_file(self, file):
        fn = file.attrib["PartName" % NAMESPACES].split("/", 1)[1]
        zi = self.zip.getinfo(fn)
        return zi, dict(zi=zi, file=file, part=etree.parse(self.zip.open(zi), parser=None))

    def get_parts(self, category_part_map=None):
        """return all the parts based on category_part_map"""
        if category_part_map is None:
            category_part_map = ["main", "header_footer", "notes"]
        elif isinstance(category_part_map, str):
            category_part_map = [category_part_map]
        return [self.parts[zi] for category in category_part_map for zi in self.category_part_map.get(category, [])]

    def get_relations_part(self, part_zi):
        """returns the relations document for the given part"""

        rel_fn = "word/_rels/%s.rels" % os.path.basename(part_zi.filename)
        if rel_fn in self.zip.namelist():
            zi = self.zip.getinfo(rel_fn)
            rel_root = etree.parse(self.zip.open(zi), parser=None)
            self.parts[zi] = dict(zi=zi, part=rel_root)
            return rel_root
        # else:
        #     print(rel_fn, self.zip.namelist())

    def write(self, output, new_parts):
        for zi in self.zip.filelist:
            if zi in self.parts:
                xml = etree.tostring(
                    self.parts[zi]["part"].getroot(),
                    encoding="UTF-8",
                    xml_declaration=True,
                )
                output.writestr(zi.filename, xml)
            else:
                output.writestr(zi.filename, self.zip.read(zi))

        for new_part in new_parts:
            xml = etree.tostring(new_part.content.getroot(), encoding="UTF-8", xml_declaration=True)
            output.writestr(new_part.path, xml)
            # TODO add relations

    def close(self):
        if not self.zip_is_closed:
            try:
                self.zip.close()
            finally:
                self.zip_is_closed = True


class MailMerge:
    """
    MailMerge class to write an output docx document by merging data rows to a template

    The class uses the builtin MergeFields in Word. There are two kind of data fields, simple and complex.
    http://officeopenxml.com/WPfields.php
    The MERGEFIELD can have MERGEFORMAT
    MERGEFIELD can be nested inside other "complex" fields, in which case those fields should be updated
    in the saved docx

    MailMerge implements this by finding all Fields and replacing them with placeholder Elements of type
    MergeElement

    Those MergeElement elements will then be replaced for each run with a list of elements containing run
    elements with texts.
    The MergeElement value (list of run Elements) should be computed recursively for the inner MergeElements

    """

    # add options parameter and deprecate the individual parameters set to the main MailMerge
    def __init__(
        self,
        file,
        options: Optional[MailMergeOptions] = None,
        remove_empty_tables=None,
        auto_update_fields_on_open=None,
        keep_fields=None,
        enable_experimental=None,
    ):
        """
        auto_update_fields_on_open : no, auto, always - auto = only when needed
        keep_fields : none - merge all fields even if no data, some - keep fields with no data, all - keep all fields
        """
        self.options = options or MailMergeOptions()
        # assert self.options.keep_fields == "none", self.options.keep_fields
        self._set_deprecated_options(remove_empty_tables, auto_update_fields_on_open, keep_fields, enable_experimental)
        self.docx = MailMergeDocx(file)
        self.merge_data = MergeData(options=self.options)
        self.new_parts = []  # list of [(filename, part)]
        self._has_unmerged_fields = False

        try:
            self.docx.fill_parts()

            for part_info in self.docx.get_parts():
                Part(self.merge_data, part_info["part"]).parse()

        except Exception:
            self.docx.close()
            raise

    def _set_deprecated_options(
        self, remove_empty_tables, auto_update_fields_on_open, keep_fields, enable_experimental
    ):
        if remove_empty_tables is not None:
            warnings.warn(
                "Passing specific options directly through constructor has been deprecated. Use options=MailMergeOptions(remove_empty_tables={remove_empty_tables}) instead or set the option later",
                category=DeprecationWarning,
                stacklevel=2,
            )
            self.options.remove_empty_tables = remove_empty_tables

        if auto_update_fields_on_open is not None:
            warnings.warn(
                "Passing specific options directly through constructor has been deprecated. Use options=MailMergeOptions(auto_update_fields_on_open={auto_update_fields_on_open}) instead or set the option later",
                category=DeprecationWarning,
                stacklevel=2,
            )
            self.options.auto_update_fields_on_open = OptionAutoUpdateFields(auto_update_fields_on_open)

        if keep_fields is not None:
            warnings.warn(
                "Passing specific options directly through constructor has been deprecated. Use options=MailMergeOptions(keep_fields={keep_fields}) instead or set the option later",
                category=DeprecationWarning,
                stacklevel=2,
            )
            self.options.keep_fields = OptionKeepFields(keep_fields)

        if enable_experimental is not None:
            warnings.warn(
                "Passing specific options directly through constructor has been deprecated. Also the enable_experimental option has been deprecated in favor of merge_if_fields. Use options=MailMergeOptions(merge_if_fields={auto_update_fields_on_open}) instead or set the option later",
                category=DeprecationWarning,
                stacklevel=2,
            )
            self.options.enable_experimental = enable_experimental

    def __getattr__(self, name):
        if name == "settings":
            warnings.warn(
                ".settings has been deprecated. Use .options",
                category=DeprecationWarning,
                stacklevel=2,
            )
            return self.options
        return getattr(self.options, name)

    def __setattr__(self, name, value):
        if name in MailMergeOptions.__annotations__:
            warnings.warn(
                "setting configuration values has been deprecated. Use .options.{} = <value>".format(name),
                category=DeprecationWarning,
                stacklevel=2,
            )
            setattr(self.options, name, value)
            return
        super().__setattr__(name, value)

    def get_settings(self):
        """returns the settings part"""
        return self.docx.parts[self.docx.category_part_map["settings"][0]]["part"]

    def get_content_types(self):
        """ " returns the content types part"""
        return self.docx.parts[self.docx.category_part_map["content_types"][0]]["part"]

    def get_relations(self, part_zi):
        """returns the relations document for the given part"""
        rel_root = self.docx.get_relations_part(part_zi)
        if rel_root is not None:
            relations = RelationsDocument(rel_root)
            for relation in relations.get_all():
                self.merge_data.unique_id_manager.register_id_str(relation.attrib["Id"])
            return relations

    def __fix_settings(self):
        settings_part = self.get_settings()
        if settings_part:
            settings_root = settings_part.getroot()
            if not self._has_unmerged_fields:
                mail_merge = settings_root.find("{%(w)s}mailMerge" % NAMESPACES)
                if mail_merge is not None:
                    settings_root.remove(mail_merge)

            add_update_fields_setting = (
                self.auto_update_fields_on_open == OptionAutoUpdateFields.AUTO
                and self.merge_data.has_nested_fields
                or self.auto_update_fields_on_open == OptionAutoUpdateFields.ALWAYS
            )
            if add_update_fields_setting:
                update_fields_elem = settings_root.find("{%(w)s}updateFields" % NAMESPACES)
                if not update_fields_elem:
                    update_fields_elem = etree.SubElement(
                        settings_root, "{%(w)s}updateFields" % NAMESPACES, attrib=None, nsmap=None
                    )
                update_fields_elem.set("{%(w)s}val" % NAMESPACES, "true")

    def write(self, file, empty_value=""):
        self._has_unmerged_fields = bool(self.get_merge_fields())

        if empty_value is not None:
            if self.keep_fields == OptionKeepFields.NONE:
                # we use empty values to replace all fields having no data
                self.merge(**{field: empty_value for field in self.get_merge_fields()})
            else:
                # we keep the fields having no data with the original value
                self.merge_data.replace_fields_with_missing_data = True
                self.merge()
                self.merge_data.replace_fields_with_missing_data = False

        # Remove mail merge settings to avoid error messages when opening document in Winword
        self.__fix_settings()

        # add the new files in the content types
        content_types = self.get_content_types().getroot()
        for new_part in self.new_parts:
            content_types.append(new_part.part_content_type)

        with ZipFile(file, "w", ZIP_DEFLATED) as output:
            self.docx.write(output, self.new_parts)

    def get_merge_fields(self):
        """ " get the fields from the document"""
        return self._get_merge_fields()

    def _get_merge_fields(self, parts=None):
        if not parts:
            parts = self.docx.get_parts()

        fields = set()
        for part in parts:
            for mf in part["part"].findall(".//MergeField"):
                fields.add(mf.attrib["name"])
                # for name in self.merge_data.get_merge_fields(mf.attrib['merge_key']):
                #     fields.add(name)
        return fields

    def merge_templates(self, replacements, separator):
        """mailmerge one document with MULTIPLE data sets, and separate the output

        is NOT compatible with header/footer/footnotes/endnotes
        separator must be :
        - page_break : Page Break.
        - column_break : Column Break. ONLY HAVE EFFECT IF DOCUMENT HAVE COLUMNS
        - textWrapping_break : Line Break.
        - continuous_section : Continuous section break. Begins the section on the next paragraph.
        - evenPage_section : evenPage section break. section begins on the next even-numbered page, leaving the next
            odd page blank if necessary.
        - nextColumn_section : nextColumn section break. section begins on the following column on the page.
            ONLY HAVE EFFECT IF DOCUMENT HAVE COLUMNS
        - nextPage_section : nextPage section break. section begins on the following page.
        - oddPage_section : oddPage section break. section begins on the next odd-numbered page, leaving the next even
            page blank if necessary.
        """
        assert replacements, "empty data"
        # TYPE PARAM CONTROL AND SPLIT

        # prepare the side documents, like headers, footers, etc
        rel_docs = []
        for part_info in self.docx.get_parts(["header_footer"]):
            relations = self.get_relations(part_info["zi"])
            merge_header_footer_doc = MergeHeaderFooterDocument(part_info, relations, separator)
            rel_docs.append(merge_header_footer_doc)
            self.merge_data.unique_id_manager.register_id(
                merge_header_footer_doc.id_type, int(merge_header_footer_doc.part_id)
            )

        # Duplicate template. Creates a copy of the template, does a merge, and separates them by a new paragraph,
        # a new break or a new section break.

        # GET ROOT - WORK WITH DOCUMENT
        for part_info in self.docx.get_parts(["main"]):
            root = part_info["part"].getroot()
            relations = self.get_relations(part_info["zi"])

            # the mailmerge is done with the help of the MergeDocument class
            # that handles the document duplication
            with MergeDocument(self.merge_data, root, relations, separator) as merge_doc:
                row = self.merge_data.start_merge(replacements)
                while row is not None:
                    merge_doc.prepare(self.merge_data, first=self.merge_data.is_first())

                    finish_rels = []
                    for rel_doc in rel_docs:
                        rel_doc.prepare(self.merge_data, first=self.merge_data.is_first())
                        rel_doc.merge(self.merge_data, row)
                        finish_rels.extend(rel_doc.finish(self.merge_data))

                    try:
                        merge_doc.merge(self.merge_data, row)
                        merge_doc.finish(finish_rels)
                    except SkipRecord:
                        merge_doc.finish(finish_rels, abort=True)

                    row = self.merge_data.next_row()

        # add all new files in the zip
        for rel_doc in rel_docs:
            self.new_parts.extend(rel_doc.new_parts)

    def merge_pages(self, replacements):
        """
        Deprecated method.
        """
        warnings.warn(
            "merge_pages has been deprecated in favour of merge_templates",
            category=DeprecationWarning,
            stacklevel=2,
        )
        self.merge_templates(replacements, "page_break")

    def merge(self, **replacements):
        """mailmerge one document with one set of values

        is compatible with header/footer/footnotes/endnotes
        """
        self._merge(replacements)

    def _merge(self, replacements):
        for part_info in self.docx.get_parts():
            self.merge_data.replace(part_info["part"], replacements)

        for new_part in self.new_parts:
            self.merge_data.replace(new_part.content, replacements)

    def merge_rows(self, anchor, rows):
        """anchor is one of the fields in the table"""

        for part_info in self.docx.get_parts():
            self.merge_data.replace_table_rows(part_info["part"], anchor, rows)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.docx.close()

    def close(self):
        self.docx.close()
        warnings.warn(
            "close() has been deprecated. Use the *with* statement.",
            category=DeprecationWarning,
            stacklevel=2,
        )
