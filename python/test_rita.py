"""
test_rita.py — Python port of ritajs/test/rita-tests.js
"""
import pytest
from rita.rita import RiTa


# ── helpers ───────────────────────────────────────────────────────────────────

def ok(val, msg=None):
    assert val, msg

def eql(a, b, msg=None):
    assert a == b, msg


# ═══════════════════════════════════════════════════════════════════════════════
class TestEvaluate:

    def test_evaluate(self):
        res = RiTa.evaluate('The [ox | ox | ox].pluralize run', {})
        assert res == 'The oxen run'
        res = RiTa.evaluate('It was [honor].art to meet you', {})
        assert res == 'It was an honor to meet you'


class TestAddTransform:

    def test_add_remove_transform(self):
        def add_rhyme(word):
            res = RiTa.lexicon.rhymes_sync(word, {'limit': 1})
            r = RiTa.random(res) if res else word
            return word + ' rhymes with ' + r

        assert 'rhymes' not in RiTa.riscript.extra_transforms
        RiTa.add_transform('rhymes', add_rhyme)
        assert 'rhymes' in RiTa.riscript.extra_transforms

        res = RiTa.evaluate('The [dog | dog | dog].rhymes')
        assert res == 'The dog rhymes with cog'

        RiTa.remove_transform('rhymes')
        assert 'rhymes' not in RiTa.riscript.extra_transforms

        res = RiTa.evaluate('The [dog | dog | dog].rhymes', {}, {'silent': True})
        assert res == 'The dog.rhymes'


class TestRandom:

    def test_random(self):
        assert 0 <= RiTa.random(10) <= 10
        assert 1 <= RiTa.random(1, 10) <= 10
        r = RiTa.random()
        assert 0 <= r <= 1

    def test_randi(self):
        assert 0 <= RiTa.randi(10) <= 9
        assert 1 <= RiTa.randi(1, 10) <= 9
        assert RiTa.randi() == 0
        assert isinstance(RiTa.randi(1, 10), int)
        assert isinstance(RiTa.randi(10), int)

    def test_random_ordering(self):
        assert RiTa.random_ordering(1) == [0]
        assert set(RiTa.random_ordering(2)) == {0, 1}
        assert RiTa.random_ordering(['a']) == ['a']
        assert set(RiTa.random_ordering(['a', 'b'])) == {'a', 'b'}

        ro = RiTa.random_ordering(4)
        assert len(ro) == 4
        assert set(ro) == {0, 1, 2, 3}

        arr = [0, 3, 5, 7]
        ro = RiTa.random_ordering(arr)
        assert len(ro) == 4
        assert set(ro) == set(arr)


class TestIsQuestion:

    def test_is_question(self):
        ok(RiTa.is_question("what"))
        ok(RiTa.is_question("what is this"))
        ok(RiTa.is_question("what is this?"))
        ok(RiTa.is_question("Does it?"))
        ok(RiTa.is_question("Would you believe it?"))
        ok(RiTa.is_question("Have you been?"))
        ok(RiTa.is_question("Is this yours?"))
        ok(RiTa.is_question("Are you done?"))
        ok(RiTa.is_question("what is this? , where is that?"))
        ok(RiTa.is_question("Will you come tomorrow?"))
        ok(RiTa.is_question("Would you do that?"))
        ok(not RiTa.is_question("That is not a toy This is an apple"))
        ok(not RiTa.is_question("string"))
        ok(not RiTa.is_question("?"))
        ok(not RiTa.is_question(""))


class TestArticlize:

    def test_articlize(self):
        tmp = RiTa.SILENCE_LTS
        RiTa.SILENCE_LTS = True
        assert RiTa.articlize('honor') == 'an honor'

        data = [
            "dog", "a dog",
            "ant", "an ant",
            "eagle", "an eagle",
            "ermintrout", "an ermintrout",
            "honor", "an honor",
        ]
        for i in range(0, len(data), 2):
            assert RiTa.articlize(data[i]) == data[i + 1]

        RiTa.SILENCE_LTS = tmp

    def test_articlize_phrases(self):
        data = [
            "black dog",   "a black dog",
            "black ant",   "a black ant",
            "orange ant",  "an orange ant",
            "great honor", "a great honor",
        ]
        for i in range(0, len(data), 2):
            assert RiTa.articlize(data[i]) == data[i + 1]


class TestIsAbbrev:

    def test_is_abbrev(self):
        ok(RiTa.is_abbrev("Dr."))
        ok(RiTa.is_abbrev("dr."))
        ok(RiTa.is_abbrev("DR."))
        ok(RiTa.is_abbrev("Dr. "))
        ok(RiTa.is_abbrev(" Dr."))
        ok(RiTa.is_abbrev("Prof."))
        ok(RiTa.is_abbrev("prof."))

        ok(not RiTa.is_abbrev("Dr"))
        ok(not RiTa.is_abbrev("Doctor"))
        ok(not RiTa.is_abbrev("Doctor."))
        ok(not RiTa.is_abbrev("PRFO."))
        ok(not RiTa.is_abbrev("PrFo."))
        ok(not RiTa.is_abbrev("Professor"))
        ok(not RiTa.is_abbrev("professor"))
        ok(not RiTa.is_abbrev("PROFESSOR"))
        ok(not RiTa.is_abbrev("Professor."))
        ok(not RiTa.is_abbrev("@#$%^&*()"))
        ok(not RiTa.is_abbrev(""))
        ok(not RiTa.is_abbrev(None))
        ok(not RiTa.is_abbrev(1))

        ok(RiTa.is_abbrev("Dr.",  {'caseSensitive': True}))
        ok(RiTa.is_abbrev("Dr. ", {'caseSensitive': True}))
        ok(RiTa.is_abbrev(" Dr.", {'caseSensitive': True}))
        ok(RiTa.is_abbrev("Prof.",{'caseSensitive': True}))

        ok(not RiTa.is_abbrev("dr.",       {'caseSensitive': True}))
        ok(not RiTa.is_abbrev("DR.",       {'caseSensitive': True}))
        ok(not RiTa.is_abbrev("Dr",        {'caseSensitive': True}))
        ok(not RiTa.is_abbrev("Doctor",    {'caseSensitive': True}))
        ok(not RiTa.is_abbrev("Doctor.",   {'caseSensitive': True}))
        ok(not RiTa.is_abbrev("prof.",     {'caseSensitive': True}))
        ok(not RiTa.is_abbrev("PRFO.",     {'caseSensitive': True}))
        ok(not RiTa.is_abbrev("PrFo.",     {'caseSensitive': True}))
        ok(not RiTa.is_abbrev("Professor", {'caseSensitive': True}))
        ok(not RiTa.is_abbrev("professor", {'caseSensitive': True}))
        ok(not RiTa.is_abbrev("PROFESSOR", {'caseSensitive': True}))
        ok(not RiTa.is_abbrev("Professor.",{'caseSensitive': True}))
        ok(not RiTa.is_abbrev("@#$%^&*()", {'caseSensitive': True}))
        ok(not RiTa.is_abbrev("",          {'caseSensitive': True}))
        ok(not RiTa.is_abbrev(None,        {'caseSensitive': True}))
        ok(not RiTa.is_abbrev(1,           {'caseSensitive': True}))


class TestIsPunct:

    def test_is_punct(self):
        ok(not RiTa.is_punct("What the"))
        ok(not RiTa.is_punct("What ! the"))
        ok(not RiTa.is_punct(".#\"\\!@i$%&_+=}<>"))

        ok(RiTa.is_punct("!"))
        ok(RiTa.is_punct("?"))
        ok(RiTa.is_punct("?!"))
        ok(RiTa.is_punct("."))
        ok(RiTa.is_punct(".."))
        ok(RiTa.is_punct("..."))
        ok(RiTa.is_punct("...."))
        ok(RiTa.is_punct("%..."))

        ok(not RiTa.is_punct("! "))
        ok(not RiTa.is_punct(" !"))
        ok(not RiTa.is_punct("!  "))   # double space
        ok(not RiTa.is_punct("  !"))   # double space
        ok(not RiTa.is_punct("!\t"))   # tab
        ok(not RiTa.is_punct("   !"))  # three spaces

        for c in '$%&^,':
            ok(RiTa.is_punct(c), f"fail at: {c}")

        for c in ',;:!?)([].#"\\!@$%&}<>|-/\\*{^':
            ok(RiTa.is_punct(c), f"fail at: {c}")

        # replacement chars + quote-like punctuation
        for c in '"\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd`\'':
            ok(RiTa.is_punct(c), f"fail at: {c!r}")

        for c in '"\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd\ufffd`\',;:!?)([].#"\\!@$%&}<>|-/\\*{^':
            ok(RiTa.is_punct(c), f"fail at: {c!r}")

        ok(not RiTa.is_punct(""))

        assert RiTa.is_punct('你') == False

        chinese = '這是一些隨機的中文字後來開始都會發揮吧首度落後兩分看來都是廢話卡卡聖誕賀卡還是阿塞德就回家啊哈薩克話說快時間啊但我阿拉斯加'
        for c in chinese:
            ok(not RiTa.is_punct(c), f"fail at {c!r}")

        nopunct = 'Helloasdfnals  FgG   \t kjdhfakjsdhf askjdfh aaf98762348576'
        for c in nopunct:
            ok(not RiTa.is_punct(c))


class TestIsStopWord:

    def test_is_stop_word(self):
        stop_words = [
            "and", "a", "of", "in", "i", "you", "is", "to", "that", "it",
            "for", "on", "have", "with", "this", "be", "not", "are", "as",
            "was", "but", "or", "from", "my", "at", "if", "they", "your",
            "all", "he", "by", "one", "me", "what", "so", "can", "will",
            "do", "an", "about", "we", "just", "would", "there", "no",
            "like", "out", "his", "has", "up", "more", "who", "when",
            "don't", "some", "had", "them", "any", "their", "it's", "only",
            "which", "i'm", "been", "other", "were", "how", "then", "now",
            "her", "than", "she", "well", "also", "us", "very", "because",
            "am", "here", "could", "even", "him", "into", "our", "much",
            "too", "did", "should", "over", "want", "these", "may", "where",
            "most", "many", "those", "does", "why", "please", "off", "going",
            "its", "i've", "down", "that's", "can't", "you're", "didn't",
            "another", "around", "must", "few", "doesn't", "the", "every",
            "yes", "each", "maybe", "i'll", "away", "doing", "oh", "else",
            "isn't", "he's", "there's", "hi", "won't", "ok", "they're",
            "yeah", "mine", "we're", "what's", "shall", "she's", "hello",
            "okay", "here's", "less", "said",
        ]
        non_stop_words = ["apple", "orange", "cat", "dog", "play", "study", "worked", "paper"]

        for w in stop_words:
            ok(RiTa.is_stop_word(w), f"{w} should be stop word")
        for w in non_stop_words:
            ok(not RiTa.is_stop_word(w), f"{w} should not be stop word")


class TestIsConsonant:

    def test_is_consonant(self):
        for l in 'aeiou':
            ok(not RiTa.is_consonant(l))
        ok(not RiTa.is_consonant(None))
        ok(not RiTa.is_consonant(""))
        ok(not RiTa.is_consonant("word"))
        for l in 'bdfks':
            ok(RiTa.is_consonant(l))


class TestTokenize:

    def test_tokenize_basic(self):
        assert RiTa.tokenize("") == [""]
        assert RiTa.tokenize("The dog") == ["The", "dog"]

    def test_tokenize_quotes(self):
        inp = "The student said 'learning is fun'"
        exp = ["The", "student", "said", "'", "learning", "is", "fun", "'"]
        assert RiTa.tokenize(inp) == exp

        inp = '"Oh God," he thought.'
        exp = ['"', 'Oh', 'God', ',', '"', 'he', 'thought', '.']
        assert RiTa.tokenize(inp) == exp

    def test_tokenize_commas(self):
        inp = "The boy, dressed in red, ate an apple."
        exp = ["The", "boy", ",", "dressed", "in", "red", ",", "ate", "an", "apple", "."]
        assert RiTa.tokenize(inp) == exp

    def test_tokenize_question_marks(self):
        inp = "why? Me?huh?!"
        exp = ["why", "?", "Me", "?", "huh", "?", "!"]
        assert RiTa.tokenize(inp) == exp

    def test_tokenize_numbers(self):
        inp = "123 123 1 2 3 1,1 1.1 23.45.67 22/05/2012 12th May,2012"
        exp = ["123", "123", "1", "2", "3", "1", ",", "1", "1.1", "23.45", ".", "67",
               "22/05/2012", "12th", "May", ",", "2012"]
        assert RiTa.tokenize(inp) == exp

    def test_tokenize_special_chars(self):
        inp = "it cost $30"
        assert RiTa.tokenize(inp) == ["it", "cost", "$", "30"]

        inp = "calculate 2^3"
        assert RiTa.tokenize(inp) == ["calculate", "2", "^", "3"]

        inp = "30% of the students"
        assert RiTa.tokenize(inp) == ["30", "%", "of", "the", "students"]

    def test_tokenize_abbreviations(self):
        inp = "dog, e.g. the cat."
        assert RiTa.tokenize(inp) == ["dog", ",", "e.g.", "the", "cat", "."]

        inp = "dog, i.e. the cat."
        assert RiTa.tokenize(inp) == ["dog", ",", "i.e.", "the", "cat", "."]

    def test_tokenize_contractions(self):
        txt1 = "Dr. Chan is talking slowly with Mr. Cheng, and they're friends."
        txt2 = "He can't didn't couldn't shouldn't wouldn't eat."
        txt3 = "Wouldn't he eat?"
        txt4 = "It's not that I can't."
        txt5 = "We've found the cat."
        txt6 = "We didn't find the cat."

        RiTa.SPLIT_CONTRACTIONS = True
        assert RiTa.tokenize(txt1) == ["Dr.", "Chan", "is", "talking", "slowly", "with",
                                        "Mr.", "Cheng", ",", "and", "they", "are", "friends", "."]
        assert RiTa.tokenize(txt2) == ["He", "can", "not", "did", "not", "could", "not",
                                        "should", "not", "would", "not", "eat", "."]
        assert RiTa.tokenize(txt3) == ["Would", "not", "he", "eat", "?"]
        assert RiTa.tokenize(txt4) == ["It", "is", "not", "that", "I", "can", "not", "."]
        assert RiTa.tokenize(txt5) == ["We", "have", "found", "the", "cat", "."]
        assert RiTa.tokenize(txt6) == ["We", "did", "not", "find", "the", "cat", "."]

        RiTa.SPLIT_CONTRACTIONS = False
        assert RiTa.tokenize(txt1) == ["Dr.", "Chan", "is", "talking", "slowly", "with",
                                        "Mr.", "Cheng", ",", "and", "they're", "friends", "."]
        assert RiTa.tokenize(txt2) == ["He", "can't", "didn't", "couldn't", "shouldn't",
                                        "wouldn't", "eat", "."]
        assert RiTa.tokenize(txt3) == ["Wouldn't", "he", "eat", "?"]
        assert RiTa.tokenize(txt4) == ["It's", "not", "that", "I", "can't", "."]
        assert RiTa.tokenize(txt5) == ["We've", "found", "the", "cat", "."]
        assert RiTa.tokenize(txt6) == ["We", "didn't", "find", "the", "cat", "."]


class TestUntokenize:

    def test_untokenize_empty(self):
        assert RiTa.untokenize([""]) == ""

    def test_untokenize_possessive(self):
        expected = "We should consider the students' learning"
        inp = ["We", "should", "consider", "the", "students", "'", "learning"]
        assert RiTa.untokenize(inp) == expected

    def test_untokenize_commas(self):
        expected = "The boy, dressed in red, ate an apple."
        inp = ["The", "boy", ",", "dressed", "in", "red", ",", "ate", "an", "apple", "."]
        assert RiTa.untokenize(inp) == expected

    def test_untokenize_questions(self):
        inp = ["why", "?", "Me", "?", "huh", "?", "!"]
        expected = "why? Me? huh?!"
        assert RiTa.untokenize(inp) == expected

    def test_untokenize_double_quotes(self):
        inp = ['"', 'Oh', 'God', ',', '"', 'he', 'thought', '.']
        expected = '"Oh God," he thought.'
        assert RiTa.untokenize(inp) == expected

        inp = ['She', 'screamed', ',', '"', 'Oh', 'God', '!', '"']
        expected = 'She screamed, "Oh God!"'
        assert RiTa.untokenize(inp) == expected

    def test_untokenize_abbreviations(self):
        expected = "dog, e.g. the cat."
        inp = ["dog", ",", "e.g.", "the", "cat", "."]
        assert RiTa.untokenize(inp) == expected

        expected = "dog, i.e. the cat."
        inp = ["dog", ",", "i.e.", "the", "cat", "."]
        assert RiTa.untokenize(inp) == expected

    def test_untokenize_various(self):
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
            ["this", "line", "is", "for", "(", "all", ")", "[", "kind", "]", "{", "of", "}",
             "\u27e8", "brackets", "\u27e9", "done"],
            ["this", "line", "is", "for", "the", "-", "dash"],
            ["30", "%", "of", "the", "student", "love", "day", "-", "dreaming", "."],
            ['"', "that", "test", "line", '"'],
            ["my", "email", "address", "is", "name", "@", "domin", ".", "com"],
            ["it", "is", "www", ".", "google", ".", "com"],
            ["that", "is", "www6", ".", "cityu", ".", "edu", ".", "hk"],
        ]
        assert len(inputs) == len(outputs)
        for i in range(len(inputs)):
            assert RiTa.untokenize(inputs[i]) == outputs[i], f"fail at index {i}"


class TestConcordance:

    def test_concordance_default(self):
        data = RiTa.concordance("The dog ate the cat")
        assert len(data) == 5
        assert data["the"] == 1
        assert data["The"] == 1
        assert data.get("THE") is None

    def test_concordance_options(self):
        data = RiTa.concordance("The dog ate the cat", {
            'ignoreCase': False,
            'ignoreStopWords': False,
            'ignorePunctuation': False,
        })
        assert len(data) == 5
        assert data["the"] == 1
        assert data["The"] == 1
        assert data.get("THE") is None

    def test_concordance_ignore_case(self):
        data = RiTa.concordance("The dog ate the cat", {'ignoreCase': True})
        assert len(data) == 4
        assert data["the"] == 2
        assert data.get("The") is None

    def test_concordance_ignore_all(self):
        data = RiTa.concordance("The Dog ate the cat.", {
            'ignoreCase': True,
            'ignoreStopWords': True,
            'ignorePunctuation': True,
        })
        assert len(data) == 3
        assert data["dog"] == 1
        assert data.get("the") is None

    def test_concordance_default_after_options(self):
        data = RiTa.concordance("The dog ate the cat")
        assert len(data) == 5
        assert data["the"] == 1
        assert data["The"] == 1

    def test_concordance_ignore_punctuation(self):
        data = RiTa.concordance("'What a wonderful world;!:,?.'\"", {'ignorePunctuation': True})
        assert len(data) == 4
        assert data.get("!") is None

    def test_concordance_ignore_stop_words(self):
        data = RiTa.concordance("The dog ate the cat", {'ignoreStopWords': True})
        assert len(data) == 3
        assert data.get("The") is None

    def test_concordance_stop_word_sentence(self):
        data = RiTa.concordance("It was a dream of you.", {'ignoreStopWords': True})
        assert len(data) == 2
        assert data.get("It") is None
        assert data["dream"] == 1
        assert data["."] == 1

    def test_concordance_words_to_ignore(self):
        data = RiTa.concordance("Fresh fried fish, Fish fresh fried.", {
            'wordsToIgnore': ["fish"],
            'ignoreCase': True,
            'ignorePunctuation': True,
        })
        assert len(data) == 2
        assert data.get("fish") is None
        assert data["fresh"] == 2
        assert data["fried"] == 2

    def test_concordance_requires_arg(self):
        with pytest.raises((TypeError, Exception)):
            RiTa.concordance()

    def test_concorder_count(self):
        c = RiTa.concorder
        c.concordance("dog dog dog cat cat cat cat cat")
        assert c.count("cat") == 5
        assert c.count("dog") == 3
        assert c.count("fox") == 0


class TestKwic:

    def test_kwic_basic(self):
        RiTa.concordance("A sentence includes cat.")
        result = RiTa.kwic("cat")
        assert result[0] == "A sentence includes cat."

    def test_kwic_no_match(self):
        RiTa.concordance("Cats are beautiful.")
        result = RiTa.kwic("cat")
        assert len(result) == 0

    def test_kwic_long_sentence(self):
        RiTa.concordance("This is a very very long sentence includes cat with many many words after it and before it.")
        result = RiTa.kwic("cat")
        assert result[0] == "a very very long sentence includes cat with many many words after it"

    def test_kwic_two_occurrences(self):
        RiTa.concordance("A sentence includes cat in the middle. Another sentence includes cat in the middle.")
        result = RiTa.kwic("cat")
        assert result[0] == "A sentence includes cat in the middle. Another sentence"
        assert result[1] == "the middle. Another sentence includes cat in the middle."

    def test_kwic_short_text(self):
        RiTa.concordance("A sentence includes cat. Another sentence includes cat.")
        result = RiTa.kwic("cat")
        assert result[0] == "A sentence includes cat. Another sentence includes cat."
        assert len(result) == 1

    def test_kwic_num_words_int(self):
        RiTa.concordance("A sentence includes cat. Another sentence includes cat.")
        result = RiTa.kwic("cat", 4)
        assert result[0] == "A sentence includes cat. Another sentence includes"
        assert result[1] == ". Another sentence includes cat."

    def test_kwic_num_words_opts(self):
        RiTa.concordance("A sentence includes cat. Another sentence includes cat.")
        result = RiTa.kwic("cat", {'numWords': 4})
        assert result[0] == "A sentence includes cat. Another sentence includes"
        assert result[1] == ". Another sentence includes cat."

    def test_kwic_with_text_opt(self):
        result = RiTa.kwic("fish", {'text': "The dog ate the cat that ate the fish."})
        assert len(result) == 1
        assert result[0] == "ate the cat that ate the fish."

    def test_kwic_with_words_opt(self):
        result = RiTa.kwic("fish", {'words': RiTa.tokenize("The dog ate the cat that ate the fish.")})
        assert len(result) == 1
        assert result[0] == "ate the cat that ate the fish."

    def test_kwic_with_words_and_num_words(self):
        result = RiTa.kwic("fish", {
            'words': RiTa.tokenize("The dog ate the cat that ate the fish. He yelled at the dog and buy a new fish."),
            'numWords': 7,
        })
        assert len(result) == 2
        assert result[0] == "dog ate the cat that ate the fish. He yelled at the dog and"
        assert result[1] == "at the dog and buy a new fish."

    def test_kwic_with_text_and_num_words(self):
        result = RiTa.kwic("fish", {
            'text': "The dog ate the cat that ate the fish. He yelled at the dog and buy a new fish.",
            'numWords': 7,
        })
        assert len(result) == 2
        assert result[0] == "dog ate the cat that ate the fish. He yelled at the dog and"
        assert result[1] == "at the dog and buy a new fish."


class TestSentences:

    def test_sentences_empty(self):
        assert RiTa.sentences('') == ['']

    def test_sentences_multi(self):
        inp = ("Stealth's Open Frame, OEM style LCD monitors are designed for special mounting "
               "applications. The slim profile packaging provides an excellent solution for building "
               "into kiosks, consoles, machines and control panels. If you cannot find an off the "
               "shelf solution call us today about designing a custom solution to fit your exact needs.")
        exp = [
            "Stealth's Open Frame, OEM style LCD monitors are designed for special mounting applications.",
            "The slim profile packaging provides an excellent solution for building into kiosks, consoles, machines and control panels.",
            "If you cannot find an off the shelf solution call us today about designing a custom solution to fit your exact needs.",
        ]
        eql(RiTa.sentences(inp), exp)

    def test_sentences_quoted(self):
        inp = '"The boy went fishing.", he said. Then he went away.'
        exp = ['"The boy went fishing.", he said.', 'Then he went away.']
        eql(RiTa.sentences(inp), exp)

    def test_sentences_single_no_punct(self):
        inp = "The dog"
        eql(RiTa.sentences(inp), [inp])

    def test_sentences_period(self):
        inp = "I guess the dog ate the baby."
        eql(RiTa.sentences(inp), [inp])

    def test_sentences_exclamation(self):
        inp = "Oh my god, the dog ate the baby!"
        eql(RiTa.sentences(inp), ["Oh my god, the dog ate the baby!"])

    def test_sentences_question(self):
        inp = "Which dog ate the baby?"
        eql(RiTa.sentences(inp), ["Which dog ate the baby?"])

    def test_sentences_mr_mrs(self):
        inp = "The baby belonged to Mr. and Mrs. Stevens. They will be very sad."
        exp = ["The baby belonged to Mr. and Mrs. Stevens.", "They will be very sad."]
        eql(RiTa.sentences(inp), exp)


