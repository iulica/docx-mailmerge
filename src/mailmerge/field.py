import datetime
import re
import warnings
from copy import deepcopy

from lxml import etree

from .constants import MAKE_TESTS_HAPPY, NAMESPACES

NUMBERFORMAT_RE = re.compile(r"([^0.,'#PN]+)?(P\d+|N\d+|[0.,'#]+%?)([^0.,'#%].*)?")
DATEFORMAT_RE = "|".join([r"{}+".format(switch) for switch in "yYmMdDhHsS"] + [r"am/pm", r"AM/PM"])
DATEFORMAT_MAP = {
    "M": "{d.month}",
    "MM": "%m",
    "MMM": "%b",
    "MMMM": "%B",
    "d": "{d.day}",
    "dd": "%d",
    "ddd": "%a",
    "dddd": "%A",
    "D": "{d.day}",
    "DD": "%d",
    "DDD": "%a",
    "DDDD": "%A",
    "yy": "%y",
    "yyyy": "%Y",
    "YY": "%y",
    "YYYY": "%Y",
    "h": "{hour12}",
    "hh": "%I",
    "H": "{d.hour}",
    "HH": "%H",
    "m": "{d.minute}",
    "mm": "%M",
    "s": "{d.second}",
    "ss": "%S",
    "am/pm": "%p",
    "AM/PM": "%p",
}


class NextRecord(Exception):
    pass


class SkipRecord(Exception):
    pass


class BaseMergeField(object):
    """
    Base MergeField class

    it contains the field name,
    and a method to fill a list of elements (runs) given the data dictionary
    That filled_elements list should be inserted in the document
    """

    def __init__(
        self,
        parent,
        name="",
        key=None,
        instr=None,
        instr_tokens=None,
        nested=False,
        all_elements=None,
        instr_elements=None,
        show_elements=None,
    ):
        """Inits the MergeField class

        Args:
            parent: The parent element of the MergeField in the tree.
            idx: The idx of the MergeField in the parent.
            name: The name of the field, if applicable
            all_elements: The list of all elements that need to be replaced in the parent
            instr_elements: Elements that show the instructions of the field (used to construct the value)
            show_elements: Elements that show the current value of the field
        """
        self.parent = parent
        self.nested = nested
        # the key of this MergeField to be able to identify it. It is used as the name in
        # the replaced MergeField element
        self.key = key
        # the list of elements to add when merging
        self._all_elements = [] if all_elements is None else all_elements
        self._instr_elements = [] if instr_elements is None else instr_elements
        self._nested_elements = [elem for elem in self._instr_elements if elem.tag == "MergeField"]
        self._show_elements = [] if show_elements is None else show_elements
        self._nested_values = {}
        self.instr = instr
        instr_tokens = [] if instr_tokens is None else instr_tokens
        self.instr_tokens = instr_tokens
        self.current_instr_tokens = self.instr_tokens
        self.filled_elements = []
        self.filled_value = None
        self.name = self._get_field_name(name)

    def has_value_in_row(self, merge_data, row):
        sub_elements_have_values = all(
            nested_obj.has_value_in_row(merge_data, row) for key, nested_obj in self.iterate_subelements(merge_data)
        )
        return sub_elements_have_values and not (self.name and (row is None or self.name not in row))

    def _get_field_name(self, name):
        return name

    def reset(self):
        """resets the value"""
        self.filled_elements = []

    def _format(self, value):
        options = self.current_instr_tokens[2:]
        for flag, option in self._walk_options(options):
            if flag in ("\\b", "\\f"):
                value = self._format_bf(value, flag, option)
            if flag in ("\\#"):
                value = self._format_number(value, flag, option)
            if flag in ("\\@"):
                value = self._format_date(value, flag, option)
            if flag in ("\\*"):
                value = self._format_text(value, flag, option)

        return self._format_value(value)

    def _format_value(self, value):
        if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
            # TODO format the date according to the locale -- set the locale
            date_formats = []
            if hasattr(value, "month"):
                date_formats.append("%x")
            if hasattr(value, "hour"):
                date_formats.append("%X")
            value = value.strftime(" ".join(date_formats))

        return value

    def _walk_options(self, options):
        while options:
            flag = options[0][0:2]
            if not flag:
                options = options[1:]
                continue
            if options[0][2:]:  # no space after the flag
                option = options[0][2:]
                options = options[1:]
            else:
                option = options[1]
                options = options[2:]
            yield flag, option

    def _format_bf(self, value, flag, option):
        # print("<{}><{}>".format(value, type(value)))
        if value:
            if flag == "\\b":
                return option + str(value)
            return str(value) + option
        # no value no text
        return None

    def _format_text(self, value, flag, option):
        option = option.lower()
        if option == "caps":
            return str(value).title()
        if option == "firstcap":
            return str(value).capitalize()
        if option == "upper":
            return str(value).upper()
        if option == "lower":
            return str(value).lower()

        return value

    def _format_number(self, value, flag, option):
        format_match = NUMBERFORMAT_RE.match(option)
        if value is None:
            value = 0
        if format_match is None:
            warnings.warn("Non conforming number format <{}>".format(option))
            return value
        format_prefix = format_match.group(1) or ""
        format_number = format_match.group(2)
        format_suffix = format_match.group(3) or ""
        if format_number[0] == "P":
            return "{{}}{{:.{}%}}{{}}".format(int(format_number[1:])).format(format_prefix, value, format_suffix)
        if format_number[0] == "N":
            return "{{}}{{:.{}f}}{{}}".format(int(format_number[1:])).format(format_prefix, value, format_suffix)
        if format_number[-1] == "%":
            return "{}{:.0%}{}".format(format_prefix, value, format_suffix)
        thousand_info = [("_", thousand_char) for thousand_char in "'," if thousand_char in format_number] + [("", "")]
        thousand_flag, thousand_char = thousand_info[0]
        format_number = format_number.replace(",", "")
        digits, decimals = (format_number.split(".") + [""])[0:2]
        zero_digits = len(digits.replace("#", ""))
        _zero_decimals = len(decimals.replace("#", ""))
        len_decimals_plus_dot = 0 if not decimals else 1 + len(decimals)
        number_format_text = "{{}}{{:{zero_digits}{thousand_flag}{decimals}f}}{{}}".format(
            thousand_flag=thousand_flag,
            zero_digits="0>{}".format(zero_digits + len_decimals_plus_dot) if zero_digits > 1 else "",
            decimals=".{}".format(len(decimals)),
        )
        # print(self.name, "<", option, ">", number_format_text)
        try:
            result = number_format_text.format(format_prefix, value, format_suffix)
            if thousand_flag:
                result = result.replace(thousand_flag, thousand_char)
            return result
        except Exception as e:
            raise ValueError("Invalid number format <{}> with error <{}>".format(number_format_text, e))

    def _format_date(self, value, flag, option):
        if value is None:
            return ""

        if not isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
            return str(value)

        # set the locale to be used for time
        # more checking needed before activating
        # locale.setlocale(locale.LC_TIME, "")
        fmt = re.sub(DATEFORMAT_RE, lambda x: DATEFORMAT_MAP[x[0]], option)
        fmt_args = {"d": value, "hour12": 0}
        if isinstance(value, (datetime.datetime, datetime.time)):
            fmt_args["hour12"] = value.hour % 12
        fmt = fmt.format(**fmt_args)
        value = value.strftime(fmt)
        # warnings.warn("Date formatting not yet implemented <{}>".format(option))
        return value

    def iterate_subelements(self, merge_data):
        for nested_elem in self._nested_elements:
            key = nested_elem.attrib["merge_key"]
            nested_obj = merge_data.get_field_obj(key)
            yield key, nested_obj

    def _fill_nested_elements(self, merge_data, row):
        nested_values = {}
        for key, nested_obj in self.iterate_subelements(merge_data):
            nested_obj.fill_data(merge_data, row)
            nested_values[key] = merge_data.get_instr_text(nested_obj.get_elements_to_replace())

        self.current_instr_tokens = [instr_token.format(**nested_values) for instr_token in self.instr_tokens]

    def fill_data(self, merge_data, row):
        """fills the filled_elements with all the elements containing the output text"""
        if self._nested_elements:
            self._fill_nested_elements(merge_data, row)

        self.filled_elements = []
        value = row.get(self.name, "«{}»".format(self.name))
        try:
            value = self._format(value)
        except Exception as e:
            warnings.warn("Invalid formatting for field <{}> with error <{}>".format(self.instr, e))
            # raise

        self.filled_value = value

        if value is None:
            # no elements should be filled ?
            # or empty text ?
            if MAKE_TESTS_HAPPY:
                value = ""
            else:
                return

        self.fill_value(self._instr_elements[0], value)

    def fill_value(self, base_elem, value):
        elem = deepcopy(base_elem)
        for child in elem.xpath("w:instrText", namespaces=NAMESPACES):
            elem.remove(child)
        for child in elem.xpath("w:t", namespaces=NAMESPACES):
            elem.remove(child)

        text_parts = str(value).replace("\r", "").split("\n")
        elem.append(self._make_text(text_parts[0]))
        for text_part in text_parts[1:]:
            elem.append(self._make_br())
            elem.append(self._make_text(text_part))

        self.filled_elements.append(elem)

    def get_elements_to_replace(self, keep_field=False):
        """returns the list of filled elements to put in the document

        three possible outcomes:
        - only the value (keep_field=False)
        - the original field without updating the value(keep_field=True, no value filled in)
        - the field with an updated value(keep_field=True, new value filled in)
        """
        if keep_field:
            if not self.filled_elements:  # we keep the original value
                return self.get_field_without_filled_elements()
            return self.get_field_with_filled_elements()
        return self.filled_elements

    def get_field_without_filled_elements(self):
        return [deepcopy(elem) for elem in self._all_elements]

    def get_field_with_filled_elements(self):
        # for complex fields
        all_elements = [deepcopy(elem) for elem in self._all_elements]  # copy of all elements
        if not self._show_elements:
            separate_element = deepcopy(self._all_elements[-1])
            separate_element.find("w:fldChar", namespaces=NAMESPACES).set("{%(w)s}fldCharType" % NAMESPACES, "separate")
            all_elements[-1:-1] = [separate_element] + self.filled_elements
        else:
            index = self._all_elements.index(self._show_elements[0])
            all_elements[index : index + len(self._show_elements)] = self.filled_elements
        return all_elements

    def _make_br(self):
        return etree.Element("{%(w)s}cr" % NAMESPACES, attrib=None, nsmap=None)

    def _make_text(self, text):
        if self.nested:
            text_node = etree.Element("{%(w)s}instrText" % NAMESPACES, attrib=None, nsmap=None)
            text_node.set("{%(xml)s}space" % NAMESPACES, "preserve")
        else:
            text_node = etree.Element("{%(w)s}t" % NAMESPACES, attrib=None, nsmap=None)

        text_node.text = text
        return text_node

    def insert_into_tree(self):
        """inserts a MergeField element in the original tree at the right position"""
        # Make sure ALL elements from the original tree are removed except for the first useful, that we will replace
        parents_to_remove = []
        current_parent = self.parent
        for subelem in self._all_elements[1:]:
            parent = subelem.getparent()
            parent.remove(subelem)
            if parent != current_parent:
                parents_to_remove.append(parent)
                current_parent = parent

        for parent in parents_to_remove:
            parent.getparent().remove(parent)
        replacement_element = etree.Element("MergeField", attrib=None, nsmap=None, merge_key=self.key, name=self.name)
        self.parent.replace(self._all_elements[0], replacement_element)
        return replacement_element


class MergeField(BaseMergeField):
    def _get_field_name(self, name):
        if not name and self.instr_tokens[1:]:
            return self.instr_tokens[1]
        return name


class SimpleMergeField(MergeField):
    """differences for simple fields"""

    def get_field_with_filled_elements(self):
        # for simple fields
        field_element = deepcopy(self._all_elements[0])
        # remove all child elements
        for child in list(field_element):
            field_element.remove(child)
        for child in self.filled_elements:
            field_element.append(child)
        return [field_element]


class NextField(MergeField):
    def fill_data(self, merge_data, row):
        raise NextRecord()
