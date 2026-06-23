"""
test_tokenizer.py — Python port of ritajs/test/tokenizer-tests.js
"""
import pytest
from rita.tokenizer import Tokenizer


@pytest.fixture
def t():
    return Tokenizer()


# ── tokens ────────────────────────────────────────────────────────────────────

class TestTokens:

    def test_tokens_basic(self, t):
        tokens = t.tokens("A small one is like a big one.")
        assert tokens == ['a', 'small', 'one', 'is', 'like', 'big']

    def test_tokens_split_contractions(self, t):
        tokens = t.tokens("One escaped, she'd thought.", {'splitContractions': True})
        assert tokens == ['one', 'escaped', 'she', 'had', 'thought']

    def test_tokens_long(self, t):
        inp = 'She wrote: "I don\'t paint anymore. For a while she thought it was just a phase that she\'d gotten over."'
        assert t.tokens(inp) == [
            'she', 'wrote', 'i',
            "don't", 'paint', 'anymore',
            'for', 'a', 'while',
            'thought', 'it', 'was',
            'just', 'phase', 'that',
            "she'd", 'gotten', 'over',
        ]

    def test_tokens_sort(self, t):
        inp = 'She wrote: "I don\'t paint anymore. For a while she thought it was just a phase that she\'d gotten over."'
        assert t.tokens(inp, {'sort': True}) == [
            'a', 'anymore', "don't",
            'for', 'gotten', 'i',
            'it', 'just',
            'over', 'paint', 'phase',
            'she', "she'd", 'that', 'thought',
            'was', 'while', 'wrote',
        ]

    def test_tokens_case_sensitive(self, t):
        inp = 'She wrote: "I don\'t paint anymore. For a while she thought it was just a phase that she\'d gotten over."'
        assert t.tokens(inp, {'caseSensitive': True}) == [
            'She', 'wrote', 'I',
            "don't", 'paint', 'anymore',
            'For', 'a', 'while',
            'she', 'thought', 'it',
            'was', 'just', 'phase',
            'that', "she'd", 'gotten',
            'over',
        ]

    def test_tokens_case_sensitive_sort(self, t):
        inp = 'She wrote: "I don\'t paint anymore. For a while she thought it was just a phase that she\'d gotten over."'
        assert t.tokens(inp, {'caseSensitive': True, 'sort': True}) == [
            'For', 'I', 'She',
            'a', 'anymore', "don't",
            'gotten', 'it', 'just',
            'over', 'paint', 'phase',
            'she', "she'd", 'that',
            'thought', 'was', 'while',
            'wrote',
        ]

    def test_tokens_split_contractions_sort(self, t):
        inp = 'She wrote: "I don\'t paint anymore. For a while she thought it was just a phase that she\'d gotten over."'
        assert t.tokens(inp, {'splitContractions': True, 'sort': True}) == [
            'a', 'anymore', 'do',
            'for', 'gotten', 'had', 'i',
            'it', 'just', 'not',
            'over', 'paint', 'phase',
            'she', 'that', 'thought',
            'was', 'while',
            'wrote',
        ]

    def test_tokens_ignore_stopwords(self, t):
        inp = 'She wrote: "I don\'t paint anymore. For a while she thought it was just a phase that she\'d gotten over."'
        assert t.tokens(inp, {'ignoreStopWords': True}) == [
            'wrote', 'paint',
            'anymore', 'while',
            'thought', 'phase',
            "she'd", 'gotten'
        ]

    def test_tokens_split_contractions_long(self, t):
        inp = 'She wrote: "I don\'t paint anymore. For a while she thought it was just a phase that she\'d gotten over."'
        assert t.tokens(inp, {'splitContractions': True}) == [
            'she', 'wrote', 'i',
            'do', 'not', 'paint', 'anymore',
            'for', 'a', 'while',
            'thought', 'it', 'was',
            'just', 'phase', 'that',
            'had', 'gotten', 'over',
        ]

    def test_tokens_include_punct(self, t):
        inp = 'She wrote: "I don\'t paint anymore. For a while she thought it was just a phase that she\'d gotten over."'
        assert t.tokens(inp, {'splitContractions': True, 'includePunct': True}) == [
            'she', 'wrote', ':',
            '"', 'i', 'do',
            'not', 'paint', 'anymore',
            '.', 'for', 'a',
            'while', 'thought', 'it',
            'was', 'just', 'phase',
            'that', 'had', 'gotten',
            'over',
        ]


# ── tokenize ─────────────────────────────────────────────────────────────────

class TestTokenize:

    def test_tokenize_empty(self, t):
        assert t.tokenize("") == [""]
        assert t.tokenize(" ") == [""]

    def test_tokenize_basic(self, t):
        assert t.tokenize("The dog") == ["The", "dog"]
        assert t.tokenize("The programs.") == ["The", "programs", "."]
        assert t.tokenize("The find.") == ["The", "find", "."]
        assert t.tokenize("The bancor.") == ["The", "bancor", "."]

    def test_tokenize_abbreviations(self, t):
        assert t.tokenize("The prof. ate.") == ["The", "prof.", "ate", "."]

    def test_tokenize_hyphenated(self, t):
        assert t.tokenize("snow-capped") == ["snow-capped"]
        assert t.tokenize("whole-hearted") == ["whole-hearted"]
        assert t.tokenize("dun-colored") == ["dun-colored"]
        assert t.tokenize("The snow-capped peaks") == ["The", "snow-capped", "peaks"]
        assert t.tokenize("The whole-hearted sighs") == ["The", "whole-hearted", "sighs"]
        assert t.tokenize("The dun-colored hills") == ["The", "dun-colored", "hills"]

    def test_tokenize_prof_sentence(self, t):
        inp = "According to the prof. climate change was real."
        expected = ['According', 'to', 'the', 'prof.', 'climate', 'change', 'was', 'real', '.']
        assert t.tokenize(inp) == expected

    def test_tokenize_single_quotes(self, t):
        inp = "The student said 'learning is fun'"
        expected = ["The", "student", "said", "'", "learning", "is", "fun", "'"]
        assert t.tokenize(inp) == expected

    def test_tokenize_double_quotes(self, t):
        inp = '"Oh God," he thought.'
        expected = ['"', 'Oh', 'God', ',', '"', 'he', 'thought', '.']
        assert t.tokenize(inp) == expected

    def test_tokenize_comma_phrases(self, t):
        inp = "The boy, dressed in red, ate an apple."
        expected = ["The", "boy", ",", "dressed", "in", "red", ",", "ate", "an", "apple", "."]
        assert t.tokenize(inp) == expected

    def test_tokenize_multiple_punct(self, t):
        inp = "why? Me?huh?!"
        expected = ["why", "?", "Me", "?", "huh", "?", "!"]
        assert t.tokenize(inp) == expected

    def test_tokenize_numbers(self, t):
        inp = "123 123 1 2 3 1,1 1.1 23.45.67 22/05/2012 12th May,2012"
        expected = ["123", "123", "1", "2", "3", "1", ",", "1", "1.1", "23.45", ".", "67", "22/05/2012", "12th", "May", ",", "2012"]
        assert t.tokenize(inp) == expected

    def test_tokenize_screamed_double_quotes(self, t):
        inp = 'The boy screamed, "Where is my apple?"'
        expected = ["The", "boy", "screamed", ",", '"', "Where", "is", "my", "apple", "?", '"']
        assert t.tokenize(inp) == expected

    def test_tokenize_curly_double_quotes(self, t):
        inp = "The boy screamed, \u201CWhere is my apple?\u201D"
        expected = ["The", "boy", "screamed", ",", "\u201C", "Where", "is", "my", "apple", "?", "\u201D"]
        assert t.tokenize(inp) == expected

    def test_tokenize_single_quote_apple(self, t):
        inp = "The boy screamed, 'Where is my apple?'"
        expected = ["The", "boy", "screamed", ",", "'", "Where", "is", "my", "apple", "?", "'"]
        assert t.tokenize(inp) == expected

    def test_tokenize_curly_single_quotes(self, t):
        inp = "The boy screamed, \u2018Where is my apple?\u2019"
        expected = ["The", "boy", "screamed", ",", "\u2018", "Where", "is", "my", "apple", "?", "\u2019"]
        assert t.tokenize(inp) == expected

    def test_tokenize_eg(self, t):
        assert t.tokenize("dog, e.g. the cat.") == ["dog", ",", "e.g.", "the", "cat", "."]

    def test_tokenize_ie(self, t):
        assert t.tokenize("dog, i.e. the cat.") == ["dog", ",", "i.e.", "the", "cat", "."]

    def test_tokenize_eg_sentence(self, t):
        inp = "What does e.g. mean? E.g. is used to introduce a few examples, not a complete list."
        expected = ["What", "does", "e.g.", "mean", "?", "E.g.", "is", "used", "to", "introduce", "a", "few", "examples", ",", "not", "a", "complete", "list", "."]
        assert t.tokenize(inp) == expected

    def test_tokenize_ie_sentence(self, t):
        inp = "What does i.e. mean? I.e. means in other words."
        expected = ["What", "does", "i.e.", "mean", "?", "I.e.", "means", "in", "other", "words", "."]
        assert t.tokenize(inp) == expected

    def test_tokenize_batch(self, t):
        inputs = [
            "A simple sentence.",
            "that's why this is our place).",
            "most, punctuation; is. split: from! adjoining words?",
            'double quotes "OK"',
            "face-to-face class",
            '"it is strange", said John, "Katherine does not drink alchol."',
            '"What?!", John yelled.',
        ]
        outputs = [
            ["A", "simple", "sentence", "."],
            ["that's", "why", "this", "is", "our", "place", ")", "."],
            ["most", ",", "punctuation", ";", "is", '.', 'split', ':', "from", "!", "adjoining", "words", "?"],
            ["double", "quotes", '"', "OK", '"'],
            ["face-to-face", "class"],  # single hyphens keep compound words together
            ['"', "it", "is", "strange", '"', ",", "said", "John", ",", '"', "Katherine", "does", "not", "drink", "alchol", ".", '"'],
            ['"', "What", "?", "!", '"', ",", "John", "yelled", "."],
        ]
        for i, (inp, exp) in enumerate(zip(inputs, outputs)):
            assert t.tokenize(inp) == exp, f"case {i}: {inp!r}"

    def test_tokenize_common_abbreviations(self, t):
        # Test the abbreviations that the regex rules reliably handle
        inp = "more abbreviations: a.m. p.m. Cap. c. et al. etc. P.S. Ph.D R.I.P vs. v. Mr. Ms. Dr. Pf. Mx. Ind. Inc. Corp. Ltd."
        expected = ["more", "abbreviations", ":", "a.m.", "p.m.", "Cap.", "c.", "et al.", "etc.", "P.S.", "Ph.D", "R.I.P", "vs.", "v.", "Mr.", "Ms.", "Dr.", "Pf.", "Mx.", "Ind.", "Inc.", "Corp.", "Ltd."]
        assert t.tokenize(inp) == expected

    def test_tokenize_co_ltd(self, t):
        # Standard Co. Ltd. and Corp. abbreviations
        assert t.tokenize("ABC Corp. is great.") == ["ABC", "Corp.", "is", "great", "."]
        assert t.tokenize("Jones Ltd. was sold.") == ["Jones", "Ltd.", "was", "sold", "."]
        assert t.tokenize("Co., Ltd. is here.") == ["Co., Ltd.", "is", "here", "."]
        assert t.tokenize("ABC Co. was great.") == ["ABC", "Co.", "was", "great", "."]

    def test_tokenize_brackets(self, t):
        inp = "(testing) [brackets] {all} \u27e8kinds\u27e9"
        expected = ["(", "testing", ")", "[", "brackets", "]", "{", "all", "}", "\u27e8", "kinds", "\u27e9"]
        assert t.tokenize(inp) == expected

    def test_tokenize_ellipsis(self, t):
        inp = "elipsis dots... another elipsis dots\u2026"
        expected = ["elipsis", "dots", "...", "another", "elipsis", "dots", "\u2026"]
        assert t.tokenize(inp) == expected

    def test_tokenize_contractions_split_on(self, t):
        t.rita = type('R', (), {'SPLIT_CONTRACTIONS': True, 'ABRV': []})()
        txt1 = "Dr. Chan is talking slowly with Mr. Cheng, and they're friends."
        assert t.tokenize(txt1) == ["Dr.", "Chan", "is", "talking", "slowly", "with", "Mr.", "Cheng", ",", "and", "they", "are", "friends", "."]
        txt2 = "He can't didn't couldn't shouldn't wouldn't eat."
        assert t.tokenize(txt2) == ["He", "can", "not", "did", "not", "could", "not", "should", "not", "would", "not", "eat", "."]
        assert t.tokenize("Wouldn't he eat?") == ["Would", "not", "he", "eat", "?"]
        assert t.tokenize("It's not that I can't.") == ["It", "is", "not", "that", "I", "can", "not", "."]
        assert t.tokenize("We've found the cat.") == ["We", "have", "found", "the", "cat", "."]
        assert t.tokenize("We didn't find the cat.") == ["We", "did", "not", "find", "the", "cat", "."]

    def test_tokenize_contractions_split_off(self, t):
        t.rita = type('R', (), {'SPLIT_CONTRACTIONS': False, 'ABRV': []})()
        txt1 = "Dr. Chan is talking slowly with Mr. Cheng, and they're friends."
        assert t.tokenize(txt1) == ["Dr.", "Chan", "is", "talking", "slowly", "with", "Mr.", "Cheng", ",", "and", "they're", "friends", "."]
        txt2 = "He can't didn't couldn't shouldn't wouldn't eat."
        assert t.tokenize(txt2) == ["He", "can't", "didn't", "couldn't", "shouldn't", "wouldn't", "eat", "."]
        assert t.tokenize("Wouldn't he eat?") == ["Wouldn't", "he", "eat", "?"]
        assert t.tokenize("It's not that I can't.") == ["It's", "not", "that", "I", "can't", "."]
        assert t.tokenize("We've found the cat.") == ["We've", "found", "the", "cat", "."]
        assert t.tokenize("We didn't find the cat.") == ["We", "didn't", "find", "the", "cat", "."]

    def test_tokenize_splitContractions_opt(self, t):
        inputs = [
            "That's why this is our place.",
            "that's why he'll win.",
            "that's why I'd lost.",
        ]
        outputs = [
            ["That", "is", "why", "this", "is", "our", "place", "."],
            ["that", "is", "why", "he", "will", "win", "."],
            ["that", "is", "why", "I", "had", "lost", "."],
        ]
        for inp, exp in zip(inputs, outputs):
            assert t.tokenize(inp, {'splitContractions': True}) == exp

    def test_tokenize_html_tags(self, t):
        inputs = [
            "<br>",
            "<br/>",
            "</br>",
            "<a>link</a>",
            "<!DOCTYPE html>",
            "<span>inline</span>",
            "<h1>header</h1>",
            "<!-- this is a comment -->",
            '<a href="www.google.com">a link to google</a>',
            "<p>this<br>is</br>a<br>paragraph<br/></p>",
            '<p>Link <a herf="https://hk.search.yahoo.com/search?p=cute+cat">here</a> is about <span class="cat">cute cat</span></p><img src="cutecat.com/catpic001.jpg" width="600" />',
            "1 < 2 and 3 > 2.",
        ]
        outputs = [
            ["<br>"],
            ["<br/>"],
            ["</br>"],
            ["<a>", "link", "</a>"],
            ["<!DOCTYPE html>"],
            ["<span>", "inline", "</span>"],
            ["<h1>", "header", "</h1>"],
            ["<!-- this is a comment -->"],
            ['<a href="www.google.com">', "a", "link", "to", "google", "</a>"],
            ["<p>", "this", "<br>", "is", "</br>", "a", "<br>", "paragraph", "<br/>", "</p>"],
            ['<p>', 'Link', '<a herf="https://hk.search.yahoo.com/search?p=cute+cat">', 'here', '</a>', 'is', 'about', '<span class="cat">', 'cute', 'cat', '</span>', '</p>', '<img src="cutecat.com/catpic001.jpg" width="600" />'],
            ["1", "<", "2", "and", "3", ">", "2", "."],
        ]
        for i, (inp, exp) in enumerate(zip(inputs, outputs)):
            assert t.tokenize(inp) == exp, f"tag case {i}: {inp!r}"

    def test_tokenize_underscores_to_spaces(self, t):
        assert t.tokenize("a_là") == ["a là"]
        assert t.tokenize("a_la") == ["a la"]
        assert t.tokenize("à_la") == ["à la"]
        assert t.tokenize("lá_bas") == ["lá bas"]
        assert t.tokenize("la_bas") == ["la bas"]
        assert t.tokenize("la_bas") == ["la bas"]  # duplicate as in JS
        assert t.tokenize("comment_ça-va") == ["comment ça-va"]
        assert t.tokenize("el_águila") == ["el águila"]
        assert t.tokenize("9_inches") == ["9 inches"]

    def test_tokenize_urls_emails(self, t):
        assert t.tokenize("example.example@gmail.com") == ["example.example@gmail.com"]
        assert t.tokenize("an.example-email_address@gmail.com") == ["an.example-email_address@gmail.com"]
        assert t.tokenize("an.email.address@yahoo.com") == ["an.email.address@yahoo.com"]
        out4 = t.tokenize("MY.EMAIL.ADDRESS@YAHOO.COM")
        assert out4 == ["MY.EMAIL.ADDRESS@YAHOO.COM"]
        assert t.untokenize(out4) == "MY.EMAIL.ADDRESS@YAHOO.COM"
        out5 = t.tokenize("This is my email address: email-address@gmail.com.")
        assert out5 == ["This", "is", "my", "email", "address", ":", "email-address@gmail.com", "."]
        assert t.untokenize(out5) == "This is my email address: email-address@gmail.com."
        assert t.tokenize("www.example.com/an_example_page") == ["www.example.com/an_example_page"]
        assert t.tokenize("https://example.com/an_example_page") == ["https://example.com/an_example_page"]
        assert t.tokenize("https://example.org/index.html") == ["https://example.org/index.html"]
        assert t.tokenize("http://example.com/An_Example_Page") == ["http://example.com/An_Example_Page"]

    def test_tokenize_decimal_numbers(self, t):
        assert t.tokenize("27.3") == ["27.3"]
        assert t.tokenize("-27.3") == ["-27.3"]
        assert t.tokenize("1.9e10") == ["1.9e10"]
        assert t.tokenize("200,000.51") == ["200,000.51"]
        assert t.tokenize("-200,000.51") == ["-200,000.51"]
        assert t.tokenize("His score was 91.2") == ["His", "score", "was", "91.2"]
        assert t.tokenize("He owed 200,000 dollars.") == ['He', 'owed', '200,000', 'dollars', '.']
        assert t.tokenize("He owed 200,000.") == ['He', 'owed', '200,000', '.']
        assert t.tokenize("He owed 200,000.50.") == ['He', 'owed', '200,000.50', '.']
        assert t.tokenize("A 4.7 inch gun.") == ['A', '4.7', 'inch', 'gun', '.']

    def test_tokenize_numbers_with_commas(self, t):
        inp = "It was 19,700 square inches, the equivalent of 409 A5 pages."
        expected = ['It', 'was', '19,700', 'square', 'inches', ',', 'the', 'equivalent', 'of', '409', 'A5', 'pages', '.']
        assert t.tokenize(inp) == expected

    def test_tokenize_dashes(self, t):
        sentence = "Type two hyphens--without a space\u2014before, after, or between them."
        expected = ['Type', 'two', 'hyphens', '--', 'without', 'a', 'space', '\u2014', 'before', ',', 'after', ',', 'or', 'between', 'them', '.']
        assert t.tokenize(sentence) == expected

        phones = "Phones, hand-held computers, and built-in TVs\u2014each a possible distraction\u2014can lead to a dangerous situation if used while driving."
        phones_toks = ['Phones', ',', 'hand-held', 'computers', ',', 'and', 'built-in', 'TVs', '\u2014', 'each', 'a', 'possible', 'distraction', '\u2014', 'can', 'lead', 'to', 'a', 'dangerous', 'situation', 'if', 'used', 'while', 'driving', '.']
        assert t.tokenize(phones) == phones_toks

        sentence2 = "He is afraid of two things--spiders and senior prom."
        expected2 = ['He', 'is', 'afraid', 'of', 'two', 'things', '--', 'spiders', 'and', 'senior', 'prom', '.']
        assert t.tokenize(sentence2) == expected2

        sentence3 = "The teacher assigned pages 101\u2013181 for tonight's reading material."
        expected3 = ['The', 'teacher', 'assigned', 'pages', '101', '\u2013', '181', 'for', "tonight's", 'reading', 'material', '.']
        assert t.tokenize(sentence3) == expected3


# ── untokenize ────────────────────────────────────────────────────────────────

class TestUntokenize:

    def test_untokenize_empty(self, t):
        assert t.untokenize(None) == ""
        assert t.untokenize(0) == ""
        assert t.untokenize([""]) == ""
        assert t.untokenize([" "]) == ""

    def test_untokenize_students_possessive(self, t):
        assert t.untokenize(["We", "should", "consider", "the", "students", "'", "learning"]) == \
            "We should consider the students' learning"

    def test_untokenize_comma_phrase(self, t):
        assert t.untokenize(["The", "boy", ",", "dressed", "in", "red", ",", "ate", "an", "apple", "."]) == \
            "The boy, dressed in red, ate an apple."

    def test_untokenize_unicode_apos(self, t):
        assert t.untokenize(["We", "should", "consider", "the", "students", "\u2019", "learning"]) == \
            "We should consider the students\u2019 learning"

    def test_untokenize_single_quoted_question(self, t):
        assert t.untokenize(["The", "boy", "screamed", ",", "'", "Where", "is", "my", "apple", "?", "'"]) == \
            "The boy screamed, 'Where is my apple?'"

    def test_untokenize_dr_mr(self, t):
        inp = ["Dr", ".", "Chan", "is", "talking", "slowly", "with", "Mr", ".", "Cheng", ",", "and", "they're", "friends", "."]
        assert t.untokenize(inp) == "Dr. Chan is talking slowly with Mr. Cheng, and they're friends."

    def test_untokenize_numbers(self, t):
        inp = ["123", "123", "1", "2", "3", "1", ",", "1", "1", ".", "1", "23", ".", "45", ".", "67", "22/05/2012", "12th", "May", ",", "2012"]
        assert t.untokenize(inp) == "123 123 1 2 3 1, 1 1. 1 23. 45. 67 22/05/2012 12th May, 2012"

    def test_untokenize_student_said(self, t):
        inp = ["The", "student", "said", "'", "learning", "is", "fun", "'"]
        assert t.untokenize(inp) == "The student said 'learning is fun'"

    def test_untokenize_multiple_question_marks(self, t):
        assert t.untokenize(["why", "?", "Me", "?", "huh", "?", "!"]) == "why? Me? huh?!"

    def test_untokenize_oh_god(self, t):
        assert t.untokenize(['"', 'Oh', 'God', ',', '"', 'he', 'thought', '.']) == '"Oh God," he thought.'

    def test_untokenize_she_screamed_comma(self, t):
        assert t.untokenize(['She', 'screamed', ',', '"', 'Oh', 'God', '!', '"']) == 'She screamed, "Oh God!"'
        assert t.untokenize(['She', 'screamed', ':', '"', 'Oh', 'God', '!', '"']) == 'She screamed: "Oh God!"'

    def test_untokenize_nested_quotes(self, t):
        inp = ['"', 'Oh', ',', 'God', '"', ',', 'he', 'thought', ',', '"', 'not', 'rain', '!', '"']
        assert t.untokenize(inp) == '"Oh, God", he thought, "not rain!"'

    def test_untokenize_eg_ie(self, t):
        assert t.untokenize(["dog", ",", "e.g.", "the", "cat", "."]) == "dog, e.g. the cat."
        assert t.untokenize(["dog", ",", "i.e.", "the", "cat", "."]) == "dog, i.e. the cat."

    def test_untokenize_eg_sentence(self, t):
        inp = ["What", "does", "e.g.", "mean", "?", "E.g.", "is", "used", "to", "introduce", "a", "few", "examples", ",", "not", "a", "complete", "list", "."]
        assert t.untokenize(inp) == "What does e.g. mean? E.g. is used to introduce a few examples, not a complete list."
        inp2 = ["What", "does", "i.e.", "mean", "?", "I.e.", "means", "in", "other", "words", "."]
        assert t.untokenize(inp2) == "What does i.e. mean? I.e. means in other words."

    def test_untokenize_batch(self, t):
        outputs = [
            "A simple sentence.",
            "that's why this is our place).",
            "this is for semicolon; that is for else",
            "this is for 2^3 2*3",
            "this is for $30 and #30",
            "this is for 30\u00b0C or 30\u2103",
            "this is for a/b a\u2044b",
            "this is for \u00abguillemets\u00bb",
            "this... is\u2026 for ellipsis",
            "this line is 'for' single 'quotation' mark",
            "Katherine's cat and John's cat",
            "this line is for (all) [kind] {of} \u27e8brackets\u27e9 done",
            "this line is for the-dash",
            "30% of the student love day-dreaming.",
            '"that test line"',
            "my email address is name@domin.com",
            "it is www.google.com",
            "that is www6.cityu.edu.hk",
        ]
        inputs = [
            ["A", "simple", "sentence", "."],
            ["that's", "why", "this", "is", "our", "place", ")", "."],
            ["this", "is", "for", "semicolon", ";", "that", "is", "for", "else"],
            ["this", "is", "for", "2", "^", "3", "2", "*", "3"],
            ["this", "is", "for", "$", "30", "and", "#", "30"],
            ["this", "is", "for", "30", "\u00b0", "C", "or", "30", "\u2103"],
            ["this", "is", "for", "a", "/", "b", "a", "\u2044", "b"],
            ["this", "is", "for", "\u00ab", "guillemets", "\u00bb"],
            ["this", "...", "is", "\u2026", "for", "ellipsis"],
            ["this", "line", "is", "'", "for", "'", "single", "'", "quotation", "'", "mark"],
            ["Katherine", "'", "s", "cat", "and", "John", "'", "s", "cat"],
            ["this", "line", "is", "for", "(", "all", ")", "[", "kind", "]", "{", "of", "}", "\u27e8", "brackets", "\u27e9", "done"],
            ["this", "line", "is", "for", "the", "-", "dash"],
            ["30", "%", "of", "the", "student", "love", "day", "-", "dreaming", "."],
            ['"', "that", "test", "line", '"'],
            ["my", "email", "address", "is", "name", "@", "domin", ".", "com"],
            ["it", "is", "www", ".", "google", ".", "com"],
            ["that", "is", "www6", ".", "cityu", ".", "edu", ".", "hk"],
        ]
        for i, (inp, exp) in enumerate(zip(inputs, outputs)):
            assert t.untokenize(inp) == exp, f"batch case {i}: expected {exp!r}"

    def test_untokenize_decimal_numbers(self, t):
        assert t.untokenize(["27.3"]) == "27.3"
        assert t.untokenize(["-27.3"]) == "-27.3"
        assert t.untokenize(["1.9e10"]) == "1.9e10"
        assert t.untokenize(["200,000.51"]) == "200,000.51"
        assert t.untokenize(["-200,000.51"]) == "-200,000.51"
        assert t.untokenize(["His", "score", "was", "91.2"]) == "His score was 91.2"
        assert t.untokenize(['He', 'owed', '200,000', 'dollars', '.']) == "He owed 200,000 dollars."
        assert t.untokenize(['He', 'owed', '200,000', '.']) == "He owed 200,000."
        assert t.untokenize(['He', 'owed', '200,000.50', '.']) == "He owed 200,000.50."

    def test_untokenize_tags(self, t):
        inputs = [
            ["1", "<", "2"],
            ["<", "a", ">"],
            ["<", "a", ">", "link", "<", "/", "a", ">"],
            ["<", "span", ">", "some", "text", "here", "<", "/", "span", ">"],
            ["<", "p", ">", "some", "text", "<", "br", "/", ">", "new", "line", "<", "/", "p", ">"],
            ["something", "<", "a", "href", "=", '"', "www", ".", "google", ".", "com", '"', ">", "link", "to", "google", "<", "/", "a", ">"],
            ["<", "!", "DOCTYPE", "html", ">"],
            ["<", "p", ">", "1", "<", "2", "is", "truth", "<", "/", "p", ">"],
            ["a", "<", "!", "-", "-", "code", "comment", "-", "-", ">", "b"],
        ]
        outputs = [
            "1 < 2",
            "<a>",
            "<a>link</a>",
            "<span>some text here</span>",
            "<p>some text <br/> new line</p>",
            'something <a href = "www.google.com">link to google</a>',
            "<!DOCTYPE html>",
            "<p>1 < 2 is truth</p>",
            "a <!--code comment--> b",
        ]
        for i, (inp, exp) in enumerate(zip(inputs, outputs)):
            assert t.untokenize(inp) == exp, f"tag case {i}: expected {exp!r}"

    def test_untokenize_dashes(self, t):
        sentence = "Type two hyphens--without a space\u2014before, after, or between them."
        tokens = ['Type', 'two', 'hyphens', '--', 'without', 'a', 'space', '\u2014', 'before', ',', 'after', ',', 'or', 'between', 'them', '.']
        assert t.untokenize(tokens) == sentence

        sentence2 = "He is afraid of two things--spiders and senior prom."
        tokens2 = ['He', 'is', 'afraid', 'of', 'two', 'things', '--', 'spiders', 'and', 'senior', 'prom', '.']
        assert t.untokenize(tokens2) == sentence2

        sentence3 = "The teacher assigned pages 101\u2013181 for tonight's reading material."
        tokens3 = ['The', 'teacher', 'assigned', 'pages', '101', '\u2013', '181', 'for', "tonight's", 'reading', 'material', '.']
        assert t.untokenize(tokens3) == sentence3

    def test_roundtrip_www(self, t):
        for s in ["this is www.google.com", "it is 'hell'"]:
            toks = t.tokenize(s)
            assert t.untokenize(toks) == s

    def test_roundtrip_html_tags(self, t):
        strings = [
            "<a>link</a>",
            '<span class="test">in line</span>',
            "<!DOCTYPE html> <head><title>Test Page</title></head>",
            "<!--comment lines-->",
            "<p>this <br>is</br> a <br>paragraph <br/></p>",
            '<p>Link <a herf="https://hk.search.yahoo.com/search?p=cute+cat">here</a> is about <span class="cat">cute cat</span></p> <img src="cutecat.com/catpic001.jpg" width="600" />',
            '<p>a paragraph with an <span class="test">in line element</span> and a <a href="https://www.google.com">link to google</a>.</p>',
            "a <br/> b",
        ]
        for s in strings:
            toks = t.tokenize(s)
            assert t.untokenize(toks) == s, f"roundtrip failed for: {s!r}"


# ── sentences ─────────────────────────────────────────────────────────────────

class TestSentences:

    def test_sentences_basic_multi(self, t):
        inp = ("Stealth's Open Frame, OEM style LCD monitors are designed for special mounting applications. "
               "The slim profile packaging provides an excellent solution for building into kiosks, consoles, machines and control panels. "
               "If you cannot find an off the shelf solution call us today about designing a custom solution to fit your exact needs.")
        expected = [
            "Stealth's Open Frame, OEM style LCD monitors are designed for special mounting applications.",
            "The slim profile packaging provides an excellent solution for building into kiosks, consoles, machines and control panels.",
            "If you cannot find an off the shelf solution call us today about designing a custom solution to fit your exact needs.",
        ]
        assert t.sentences(inp) == expected

    def test_sentences_newlines(self, t):
        inp = ("Stealth's Open Frame, OEM style LCD monitors are designed for special mounting applications.\n\n"
               "The slim profile packaging provides an excellent solution for building into kiosks, consoles, machines and control panels.\r\n "
               "If you cannot find an off the shelf solution call us today about designing a custom solution to fit your exact needs.")
        expected = [
            "Stealth's Open Frame, OEM style LCD monitors are designed for special mounting applications.",
            "The slim profile packaging provides an excellent solution for building into kiosks, consoles, machines and control panels.",
            "If you cannot find an off the shelf solution call us today about designing a custom solution to fit your exact needs.",
        ]
        assert t.sentences(inp) == expected

    def test_sentences_quoted(self, t):
        inp = '"The boy went fishing.", he said. Then he went away.'
        expected = ['"The boy went fishing.", he said.', 'Then he went away.']
        assert t.sentences(inp) == expected

    def test_sentences_single(self, t):
        assert t.sentences("The dog") == ["The dog"]
        assert t.sentences("I guess the dog ate the baby.") == ["I guess the dog ate the baby."]
        assert t.sentences("Oh my god, the dog ate the baby!") == ["Oh my god, the dog ate the baby!"]
        assert t.sentences("Which dog ate the baby?") == ["Which dog ate the baby?"]
        assert t.sentences("'Yes, it was a dog that ate the baby', he said.") == ["'Yes, it was a dog that ate the baby', he said."]

    def test_sentences_mr_mrs(self, t):
        inp = "The baby belonged to Mr. and Mrs. Stevens. They will be very sad."
        expected = ["The baby belonged to Mr. and Mrs. Stevens.", "They will be very sad."]
        assert t.sentences(inp) == expected

    def test_sentences_quotes_double(self, t):
        inp = '"The baby belonged to Mr. and Mrs. Stevens. They will be very sad."'
        expected = ['"The baby belonged to Mr. and Mrs. Stevens.', 'They will be very sad."']
        assert t.sentences(inp) == expected

    def test_sentences_quotes_curly(self, t):
        inp = "\u201CThe baby belonged to Mr. and Mrs. Stevens. They will be very sad.\u201D"
        expected = ["\u201CThe baby belonged to Mr. and Mrs. Stevens.", "They will be very sad.\u201D"]
        assert t.sentences(inp) == expected

    def test_sentences_bennet(self, t):
        inp = '"My dear Mr. Bennet. Netherfield Park is let at last."'
        expected = ['"My dear Mr. Bennet.', 'Netherfield Park is let at last."']
        assert t.sentences(inp) == expected

    def test_sentences_bennet_curly(self, t):
        inp = "\u201CMy dear Mr. Bennet. Netherfield Park is let at last.\u201D"
        expected = ["\u201CMy dear Mr. Bennet.", "Netherfield Park is let at last.\u201D"]
        assert t.sentences(inp) == expected

    def test_sentences_she_wrote(self, t):
        inp = 'She wrote: "I don\'t paint anymore. For a while I thought it was just a phase that I\'d get over."'
        expected = ['She wrote: "I don\'t paint anymore.', "For a while I thought it was just a phase that I'd get over.\""]
        assert t.sentences(inp) == expected

    def test_sentences_friend(self, t):
        assert t.sentences(' I had a visit from my "friend" the tax man.') == ['I had a visit from my "friend" the tax man.']

    def test_sentences_empty(self, t):
        assert t.sentences("") == [""]

    def test_sentences_decimal(self, t):
        assert t.sentences("Today I would make something. A 4.7 inch gun. It was noon.") == \
            ["Today I would make something.", "A 4.7 inch gun.", "It was noon."]

    def test_sentences_dashes(self, t):
        inp = "Type two hyphens\u2014without a space before, after, or between them."
        assert t.sentences(inp) == [inp]
        inp2 = "After a split second of hesitation, the second baseman leaped for the ball\u2014or, rather, limped for it."
        assert t.sentences(inp2) == [inp2]


# ── line breaks ───────────────────────────────────────────────────────────────

class TestLineBreaks:

    def test_linebreak_lf(self, t):
        s = 'A CARAFE, THAT IS A BLIND GLASS.\nA kind in glass and a cousin.'
        assert t.untokenize(t.tokenize(s)) == s

    def test_linebreak_crlf(self, t):
        s = 'A CARAFE, THAT IS A BLIND GLASS.\r\nA kind in glass and a cousin.'
        assert t.untokenize(t.tokenize(s)) == s
