import codecs


def from_plain_text(text, sentence_separator_pattern="[।॥!]"):
    import regex
    from indic_transliteration import sanscript
    devanagari = sanscript.SCHEMES[sanscript.DEVANAGARI]
    text = devanagari.fix_lazy_anusvaara(text)
    text = devanagari.fix_lazy_visarga(text)
    return regex.split(sentence_separator_pattern, text)


def from_markdown_file(file_path, ignore_comments=True):
    sentences = []
    import yamldown as yamldown
    import regex
    with codecs.open(file_path, "r", 'utf-8') as in_file_obj:
        (yml, md) = yamldown.load(in_file_obj)
        if "title" in yml:
            sentences.append(yml["title"])

        ## Treat headings as sentences.
        md = regex.sub("^#(.+)\s*$", "$1॥", md)

        if ignore_comments:
            ## Ignore comments.
            md = regex.sub("\+\+\+\(.+?\)\+\+\+", "", md)

        # TODO: Process image alternate texts and captions?
        sentences.extend(from_plain_text(md))
    return sentences