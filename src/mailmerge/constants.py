NAMESPACES = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
    "rr": "http://schemas.openxmlformats.org/package/2006/relationships",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "xml": "http://www.w3.org/XML/1998/namespace",
}

ATTACHMENT_TAGS = [
    "hdr",  # header
    "ftr",  # footer
    "footnotes",  # footnotes
    "endnotes",  # endnotes
]

ATTACHMENT_TAGS_WITH_NAMESPACE = {"{{{w}}}".format(**NAMESPACES) + tag for tag in ATTACHMENT_TAGS}

CONTENT_TYPES_PARTS = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml": "main",
    "application/vnd.ms-word.document.macroEnabled.main+xml": "main",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml": "header_footer",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml": "header_footer",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml": "notes",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.endnotes+xml": "notes",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml": "settings",
}

VALID_SEPARATORS = {
    "page_break",
    "column_break",
    "textWrapping_break",
    "continuous_section",
    "evenPage_section",
    "nextColumn_section",
    "nextPage_section",
    "oddPage_section",
}

TAGS_WITH_ID = {"wp:docPr": {"name": "Picture {id}"}}

MAKE_TESTS_HAPPY = True
