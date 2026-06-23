"""test_tagger.py — ported from ritajs/test/tagger-tests.js"""
import pytest
from rita.tagger import Tagger

tagger = Tagger()

def pos(text, **opts):
    return tagger.tag(text, opts if opts else None)

def pos_inline(text, **opts):
    opts['inline'] = True
    return tagger.tag(text, opts)

# ── pos.array ────────────────────────────────────────────────────────────────

def test_pos_array():
    assert pos([]) == []
    assert pos(["deal"]) == ["nn"]
    assert pos(["freed"]) == ["jj"]
    assert pos(["the"]) == ["dt"]
    assert pos(["a"]) == ["dt"]
    assert pos("the top seed".split()) == ["dt", "jj", "nn"]
    assert pos("by illegal means".split()) == ["in", "jj", "nn"]
    assert pos("He outnumbers us".split()) == ["prp", "vbz", "prp"]
    assert pos("I outnumber you".split()) == ["prp", "vbp", "prp"]
    assert pos("Elephants dance".split()) == ["nns", "vbp"]
    assert pos("the boy dances".split()) == ["dt", "nn", "vbz"]
    assert pos("Dave dances".split()) == ["nnp", "vbz"]

def test_pos_array_simple():
    assert pos([], simple=True) == []
    assert pos(["freed"], simple=True) == ["a"]
    assert pos(["the"], simple=True) == ["-"]
    assert pos(["a"], simple=True) == ["-"]
    assert pos("the top seed".split(), simple=True) == ["-", "a", "n"]
    assert pos("by illegal means".split(), simple=True) == ["-", "a", "n"]
    assert pos("He outnumbers us".split(), simple=True) == ["-", "v", "-"]
    assert pos("I outnumber you".split(), simple=True) == ["-", "v", "-"]
    assert pos("Elephants dance".split(), simple=True) == ["n", "v"]
    assert pos("the boy dances".split(), simple=True) == ["-", "n", "v"]

# ── posInline.array.simple ───────────────────────────────────────────────────

def test_pos_inline_array_simple():
    assert pos_inline([], simple=True) == ""
    assert pos_inline(["asdfaasd"], simple=True) == "asdfaasd/n"
    assert pos_inline(["clothes"], simple=True) == "clothes/n"
    assert pos_inline(["teeth"], simple=True) == "teeth/n"
    assert pos_inline("There is a cat".split(), simple=True) == "There/- is/v a/- cat/n"
    result = pos_inline(tagger._get_tokenizer().tokenize("The boy, dressed in red, ate an apple."), simple=True)
    assert result == "The/- boy/n , dressed/v in/- red/a , ate/v an/- apple/n ."
    txt = "The dog ran faster than the other dog. But the other dog was prettier."
    result = pos_inline(tagger._get_tokenizer().tokenize(txt), simple=True)
    assert result == "The/- dog/n ran/v faster/r than/- the/- other/a dog/n . But/- the/- other/a dog/n was/v prettier/a ."

# ── inflected verbs ──────────────────────────────────────────────────────────

def test_inflected_verbs():
    assert pos("disbelieves") == ["vbz"]
    assert pos("disbelieves", simple=1) == ["v"]
    assert pos("fates") == ["nns"]
    assert pos("fates", simple=1) == ["n"]
    assert pos("hates") == ["vbz"]
    assert pos("hates", simple=1) == ["v"]
    assert pos("hated") == ["vbd"]
    assert pos("hated", simple=1) == ["v"]
    assert pos("hating") == ["vbg"]
    assert pos("hating", simple=1) == ["v"]
    assert pos("He rode the horse") == ['prp', 'vbd', 'dt', 'nn']
    assert pos("He has ridden the horse") == ['prp', 'vbz', 'vbn', 'dt', 'nn']
    assert pos("He rowed the boat") == ['prp', 'vbd', 'dt', 'nn']
    assert pos("He has rowed the boat") == ['prp', 'vbz', 'vbn', 'dt', 'nn']

# ── pos (string input) ───────────────────────────────────────────────────────

def test_pos():
    assert pos("") == []
    assert pos(",") == [',']
    assert pos(" ") == []

    assert pos("freed") == ["jj"]
    assert pos("biped") == ["nn"]
    assert pos("greed") == ["nn"]
    assert pos("creed") == ["nn"]
    assert pos("weed") == ["nn"]

    assert pos("broke") == ["vbd"]
    assert pos("broke", simple=1) == ["v"]
    assert pos("committed") == ["vbn"]
    assert pos("committed", simple=1) == ["v"]
    assert pos("outpaced") == ["vbd"]
    assert pos("outpaced", simple=1) == ["v"]
    assert pos("concerned") == ["vbd"]
    assert pos("concerned", simple=1) == ["v"]

    assert pos("the top seed") == ["dt", "jj", "nn"]
    assert pos("by illegal means") == ["in", "jj", "nn"]
    assert pos('Joannie Smith ran away') == ['nnp', 'nnp', 'vbd', 'rb']

    assert pos("mammal") == ["nn"]
    assert pos("asfaasd") == ["nn"]
    assert pos("innings") == ["nns"]
    assert pos("clothes") == ["nns"]
    assert pos("teeth") == ["nns"]
    assert pos("memories") == ["nns"]

    assert pos("flunks") == ["vbz"]
    assert pos("outnumbers") == ["vbz"]
    assert pos("He outnumbers us") == ["prp", "vbz", "prp"]
    assert pos("I outnumber you") == ["prp", "vbp", "prp"]
    assert pos("Elephants dance") == ["nns", "vbp"]
    assert pos("the boy dances") == ["dt", "nn", "vbz"]
    assert pos("he dances") == ["prp", "vbz"]
    assert pos("Dave dances") == ["nnp", "vbz"]

    assert pos("running") == ["vbg"]
    assert pos("asserting") == ["vbg"]
    assert pos("assenting") == ["vbg"]
    assert pos("Dave") == ["nnp"]

    assert pos("They feed the cat") == ["prp", "vbp", "dt", "nn"]
    assert pos("There is a cat.") == ["ex", "vbz", "dt", "nn", "."]
    assert pos("The boy, dressed in red, ate an apple.") == ["dt", "nn", ",", "vbn", "in", "jj", ",", "vbd", "dt", "nn", "."]

    txt = "The dog ran faster than the other dog.  But the other dog was prettier."
    assert pos(txt) == ["dt", "nn", "vbd", "rbr", "in", "dt", "jj", "nn", ".", "cc", "dt", "jj", "nn", "vbd", "jjr", "."]

    assert pos("is") == ["vbz"]
    assert pos("am") == ["vbp"]
    assert pos("be") == ["vb"]

    assert pos("There is a cat.") == ["ex", "vbz", "dt", "nn", "."]
    assert pos("There was a cat.") == ["ex", "vbd", "dt", "nn", "."]
    assert pos("I am a cat.") == ["prp", "vbp", "dt", "nn", "."]
    assert pos("I was a cat.") == ["prp", "vbd", "dt", "nn", "."]

    assert pos("flunk") == ["vb"]
    assert pos("He flunks the test") == ["prp", "vbz", "dt", "nn"]
    assert pos("he") == ["prp"]
    assert pos("outnumber") == ["vb"]
    assert pos("I outnumbered you") == ["prp", "vbd", "prp"]
    assert pos("She outnumbered us") == ["prp", "vbd", "prp"]
    assert pos("I am outnumbering you") == ["prp", "vbp", "vbg", "prp"]
    assert pos("I have outnumbered you") == ["prp", "vbp", "vbd", "prp"]

    for w in ["emphasis", "stress", "discus", "colossus", "fibrosis", "digitalis",
              "pettiness", "mess", "cleanliness", "orderliness", "bronchitis",
              "preparedness", "highness"]:
        assert pos(w) == ["nn"], f"failed: {w}"

    assert pos('a light blue sky') == ['dt', 'jj', 'jj', 'nn']

    assert pos("He is running toward me") == ["prp", "vbz", "vbg", "in", "prp"]
    assert pos("She is riding a bike") == ["prp", "vbz", "vbg", "dt", "nn"]
    assert pos("he stands still, thinking about the words") == ["prp", "vbz", "rb", ",", "vbg", "in", "dt", "nns"]
    assert pos("She walked out of the room smoking") == ["prp", "vbd", "in", "in", "dt", "nn", "vbg"]
    assert pos("He kept saying his adventure story") == ["prp", "vbd", "vbg", "prp$", "nn", "nn"]
    assert pos("Drinking is his hobby") == ["vbg", "vbz", "prp$", "nn"]
    assert pos("The kid playing at the corner is the boss") == ["dt", "nn", "vbg", "in", "dt", "nn", "vbz", "dt", "nn"]
    assert pos("She is the leader of the reading group") == ["prp", "vbz", "dt", "nn", "in", "dt", "vbg", "nn"]
    assert pos("I love working") == ["prp", "vbp", "vbg"]
    assert pos("I was thinking about buying a car") == ["prp", "vbd", "vbg", "in", "vbg", "dt", "nn"]

    assert pos("lancer") == ["nn"]
    assert pos("dancer") == ["nn"]
    assert pos("builder") == ["nn"]
    assert pos("programmer") == ["nn"]
    assert pos("mixer") == ["nn"]
    assert pos("He is a dancer") == ["prp", "vbz", "dt", "nn"]
    assert pos("She is a body bulider") == ["prp", "vbz", "dt", "nn", "nn"]
    assert pos("I am a programmer") == ["prp", "vbp", "dt", "nn"]

    assert pos("I have gone alone in there") == ["prp", "vbp", "vbn", "rb", "in", "nn"]
    assert pos("We stopped and went on from there") == ["prp", "vbd", "cc", "vbd", "in", "in", "nn"]
    assert pos("She lives there") == ["prp", "vbz", "rb"]
    assert pos("He was standing there") == ["prp", "vbd", "vbg", "rb"]
    assert pos("There are good reasons to save the world") == ["ex", "vbp", "jj", "nns", "to", "vb", "dt", "nn"]
    assert pos("There is a pig") == ["ex", "vbz", "dt", "nn"]
    assert pos("There isn't a world that is worth saving") == ["ex", "vbz", "dt", "nn", "in", "vbz", "jj", "vbg"]

# ── posInline ────────────────────────────────────────────────────────────────

def test_pos_inline():
    assert pos_inline("") == ""
    assert pos_inline(" ") == ""
    assert pos_inline("asdfaasd") == "asdfaasd/nn"
    assert pos_inline("clothes") == "clothes/nns"
    assert pos_inline("teeth") == "teeth/nns"
    assert pos_inline("There is a cat.") == "There/ex is/vbz a/dt cat/nn ."
    assert pos_inline("The boy, dressed in red, ate an apple.") == "The/dt boy/nn , dressed/vbn in/in red/jj , ate/vbd an/dt apple/nn ."
    txt = "The dog ran faster than the other dog.  But the other dog was prettier."
    assert pos_inline(txt) == "The/dt dog/nn ran/vbd faster/rbr than/in the/dt other/jj dog/nn . But/cc the/dt other/jj dog/nn was/vbd prettier/jjr ."
    assert pos_inline("The mosquito bit me.") == "The/dt mosquito/nn bit/vbd me/prp ."
    assert pos_inline("Give the duck a bit of bread.") == "Give/vb the/dt duck/nn a/dt bit/nn of/in bread/nn ."
    assert pos_inline("The show has ended.") == "The/dt show/nn has/vbz ended/vbn ."
    assert pos_inline("She remade this video.") == "She/prp remade/vbd this/dt video/nn ."
    assert pos_inline("Her apartment was sold.") == "Her/prp$ apartment/nn was/vbd sold/vbn ."
    assert pos_inline("She resold her apartment.") == "She/prp resold/vbd her/prp$ apartment/nn ."
    assert pos_inline("He led a team of crows into battle.") == "He/prp led/vbd a/dt team/nn of/in crows/nns into/in battle/nn ."

# ── pos.simple ───────────────────────────────────────────────────────────────

def test_pos_simple():
    assert pos("biped", simple=True) == ["n"]
    assert pos("greed", simple=True) == ["n"]
    assert pos("creed", simple=True) == ["n"]
    assert pos("weed", simple=True) == ["n"]
    assert pos("is", simple=True) == ["v"]
    assert pos("am", simple=True) == ["v"]
    assert pos("be", simple=True) == ["v"]
    assert pos("freed", simple=True) == ["a"]
    assert pos("the top seed", simple=True) == ["-", "a", "n"]
    assert pos("", simple=True) == []

# ── posInline.simple ─────────────────────────────────────────────────────────

def test_pos_inline_simple():
    assert pos_inline("", simple=True) == ""
    assert pos_inline("asdfaasd", simple=True) == "asdfaasd/n"
    assert pos_inline("clothes", simple=True) == "clothes/n"
    assert pos_inline("teeth", simple=True) == "teeth/n"
    assert pos_inline("There is a cat.", simple=True) == "There/- is/v a/- cat/n ."
    assert pos_inline("The boy, dressed in red, ate an apple.", simple=True) == "The/- boy/n , dressed/v in/- red/a , ate/v an/- apple/n ."
    txt = "The dog ran faster than the other dog.  But the other dog was prettier."
    assert pos_inline(txt, simple=True) == "The/- dog/n ran/v faster/r than/- the/- other/a dog/n . But/- the/- other/a dog/n was/v prettier/a ."

# ── isAdverb ─────────────────────────────────────────────────────────────────

def test_is_adverb():
    assert not tagger.is_adverb("")
    assert not tagger.is_adverb(None)
    assert not tagger.is_adverb(42)
    assert not tagger.is_adverb(["lively"])
    for w in ["swim","walk","walker","beautiful","dance","dancing","dancer",
              "wash","play","throw","drink","eat","chew",
              "wet","dry","furry","sad","happy",
              "dogs","wind","dolls","frogs","ducks","flowers","fish"]:
        assert not tagger.is_adverb(w), f"is_adverb({w!r}) should be False"
    for w in ["truthfully","kindly","bravely","doggedly","sleepily","scarily",
              "excitedly","energetically","hard"]:
        assert tagger.is_adverb(w), f"is_adverb({w!r}) should be True"

# ── isNoun ───────────────────────────────────────────────────────────────────

def test_is_noun():
    assert tagger.is_noun("thieves")
    assert tagger.is_noun("calves")
    assert not tagger.is_noun("scarily")
    for w in ["boxes","swim","walk","walker","dance","dancer","cats","teeth",
              "apples","buses","prognoses","oxen","theses","stimuli","crises"]:
        assert tagger.is_noun(w), f"is_noun({w!r}) should be True"
    for w in ["wash","walk","play","throw","duck","dog","drink"]:
        assert tagger.is_noun(w)
    assert not tagger.is_noun("abates")
    for w in ["eat","chew","moved","went","spent"]:
        assert not tagger.is_noun(w), f"is_noun({w!r}) should be False"
    for w in ["hard","dry","furry","sad","happy","beautiful"]:
        assert not tagger.is_noun(w)
    for w in ["dogs","wind","dolls","frogs","ducks","flower","fish",
              "wet","ducks","flowers"]:
        assert tagger.is_noun(w)
    for w in ["truthfully","kindly","bravely","scarily","sleepily","excitedly","energetically"]:
        assert not tagger.is_noun(w)
    assert not tagger.is_noun("")
    assert not tagger.is_noun(None)
    assert not tagger.is_noun(42)
    assert not tagger.is_noun(["rabbit"])
    assert not tagger.is_noun("heard")
    assert not tagger.is_noun("deterred")

# ── isVerb ───────────────────────────────────────────────────────────────────

def test_is_verb():
    assert tagger.is_verb("abandons")
    for w in ["dance","swim","walk","dances","swims","walks","costs"]:
        assert tagger.is_verb(w)
    for w in ["danced","swam","walked","costed","satisfies","falsifies","beautifies","repossesses"]:
        assert tagger.is_verb(w)
    assert not tagger.is_verb("dancer")
    assert not tagger.is_verb("walker")
    assert not tagger.is_verb("beautiful")
    for w in ["eat","chew","throw","walk","wash","drink","fish","wind","wet","dry"]:
        assert tagger.is_verb(w)
    for w in ["hard","furry","sad","happy"]:
        assert not tagger.is_verb(w)
    assert not tagger.is_verb("dolls")
    assert not tagger.is_verb("frogs")
    assert tagger.is_verb("flowers")
    assert tagger.is_verb("ducks")
    for w in ["truthfully","kindly","bravely","scarily","sleepily","excitedly","energetically"]:
        assert not tagger.is_verb(w)
    for w in ["hates","hated","hating","dancing","flowers"]:
        assert tagger.is_verb(w)
    for w in ["hates","hated","ridden","rode","abetted","abetting",
              "abutted","abutting","abuts","abut","misdeal","misdeals","misdealt"]:
        assert tagger.is_verb(w), f"is_verb({w!r}) should be True"
    assert not tagger.is_verb("")
    assert not tagger.is_verb(None)
    assert not tagger.is_verb(42)
    assert not tagger.is_verb(["work"])

# ── isAdjective ──────────────────────────────────────────────────────────────

def test_is_adjective():
    for w in ["swim","walk","walker","dance","dancing","dancer",
              "wash","play","throw","drink","eat","chew"]:
        assert not tagger.is_adjective(w)
    assert tagger.is_adjective("beautiful")
    for w in ["hard","wet","dry","furry","sad","happy","kindly"]:
        assert tagger.is_adjective(w), f"is_adjective({w!r}) should be True"
    for w in ["dogs","wind","dolls","frogs","ducks","flowers","fish"]:
        assert not tagger.is_adjective(w)
    for w in ["truthfully","bravely","scarily","sleepily","excitedly","energetically"]:
        assert not tagger.is_adjective(w)
    assert not tagger.is_adjective("")
    assert not tagger.is_adjective(None)
    assert not tagger.is_adjective(42)
    assert not tagger.is_adjective(["happy"])

# ── allTags ──────────────────────────────────────────────────────────────────

def test_all_tags():
    assert tagger.all_tags('monkey') == ["nn"]
    assert tagger.all_tags('monkeys') == ["nns"]
    assert tagger.all_tags('') == []
    assert tagger.all_tags(['monkey']) == []
    assert tagger.all_tags("hates", {'noDerivations': True}) == []
    assert tagger.all_tags("satisfies") == ["vbz"]
    assert tagger.all_tags("falsifies") == ["vbz"]
    assert "vbz" in tagger.all_tags("hates")
    assert "nns" in tagger.all_tags("hates")
    assert "nns" in tagger.all_tags("cakes")
    assert "vbz" in tagger.all_tags("repossesses")
    assert "nns" in tagger.all_tags("thieves")
    assert "vbz" in tagger.all_tags("thieves")
    assert "vbd" in tagger.all_tags("hated")
    assert "vbn" in tagger.all_tags("hated")
    assert "vbd" in tagger.all_tags("owed")
    assert "vbn" in tagger.all_tags("owed")
    assert "vbg" in tagger.all_tags("assenting")
    assert "vbg" in tagger.all_tags("hating")
    assert "nns" in tagger.all_tags("feet")
    assert "nns" in tagger.all_tags("men")
    assert "nn" in tagger.all_tags("ashdj")
    assert "rb" in tagger.all_tags("kahsdly")
    assert "nns" in tagger.all_tags("asdkasws")

    assert tagger.all_tags("bit") == ['vbd', 'nn', 'rb']
    assert tagger.all_tags("broke") == ['vbd', 'jj', 'rb']
    assert tagger.all_tags("called") == ['vbd', 'vbn']
    assert tagger.all_tags("committed") == ['vbn', 'jj', 'vbd']
    assert tagger.all_tags("computerized") == ['jj', 'vbd', 'vbn']
    assert tagger.all_tags("concerned") == ['vbd', 'jj', 'vbn']
    assert tagger.all_tags("discriminated") == ['vbd', 'vbn', 'jj']
    assert tagger.all_tags("ended") == ['vbd', 'jj', 'vbn']
    assert tagger.all_tags("expected") == ['vbn', 'vbd', 'jj']
    assert tagger.all_tags("finished") == ['vbd', 'jj', 'vbn']
    assert tagger.all_tags("gained") == ['vbd', 'vbn']
    assert tagger.all_tags("got") == ['vbd', 'vbn']
    assert tagger.all_tags("increased") == ['vbn', 'jj', 'vbd']
    assert tagger.all_tags("involved") == ['vbn', 'vbd', 'jj']
    assert tagger.all_tags("launched") == ['vbn', 'vbd']
    assert tagger.all_tags("led") == ['vbd', 'vbn']
    assert tagger.all_tags("lived") == ['vbd', 'vbn']
    assert tagger.all_tags("oversaw") == ['vbd']
    assert tagger.all_tags("paled") == ['vbd', 'vbn']
    assert tagger.all_tags("prepaid") == ['jj', 'vbd', 'vbn']
    assert tagger.all_tags("pressured") == ['vbn', 'jj', 'vbd']
    assert tagger.all_tags("proliferated") == ['vbn', 'vbd']
    assert tagger.all_tags("remade") == ['vbd', 'vbn']
    assert tagger.all_tags("reopened") == ['vbd', 'vbn']
    assert tagger.all_tags("reported") == ['vbd', 'jj', 'vbn']
    assert tagger.all_tags("resold") == ['vbd', 'vbn']
    assert tagger.all_tags("settled") == ['vbd', 'vbn', 'jj']
    assert tagger.all_tags("started") == ['vbd', 'jj', 'vbn']

    for w in ["tiding", "census", "bonus", "thermos", "circus"]:
        assert "nn" in tagger.all_tags(w), f"expected 'nn' in all_tags({w!r})"

# ── hasTag ───────────────────────────────────────────────────────────────────

def test_has_tag():
    assert not tagger.has_tag(None, 'nn')
    assert not tagger.has_tag('nn adj', 'nn')
    assert tagger.has_tag(tagger.all_tags('monkey'), 'nn')

# ── inlineTags ───────────────────────────────────────────────────────────────

def test_inline_tags():
    assert tagger.inline_tags() == ""
    assert tagger.inline_tags([]) == ""
    with pytest.raises(ValueError):
        tagger.inline_tags(["I", "am", "Pikachu"], [], "/")
    assert tagger.inline_tags(["I", "am", "happy", "."], ["prp", "vbp", "jj", "."]) == "I/prp am/vbp happy/jj ."
    assert tagger.inline_tags(["I", "am", "happy", "."], ["prp", "vbp", "jj", "."], ";") == "I;prp am;vbp happy;jj ."

# ── tag ──────────────────────────────────────────────────────────────────────

def test_tag():
    assert tagger.tag([]) == []
    assert tagger.tag(None) == []
    assert tagger.tag([], {'inline': True}) == ""
    assert tagger.tag(["I", "am", "happy", "."], {'simple': True}) == ["-", "v", "a", "-"]
    assert tagger.tag(["I", "am", "happy", "."], {'simple': True, 'inline': True}) == "I/- am/v happy/a ."
    assert tagger.tag(["I", "roll", "a", "9", "."], {'inline': True}) == "I/prp roll/vbp a/dt 9/cd ."
    assert tagger.tag(["A", "badguy", "."], {'inline': True}) == "A/dt badguy/nn ."
    assert tagger.tag(["A", "C", "level", "grade", "."], {'inline': True}) == "A/dt C/C level/jj grade/nn ."
    # rule 1
    assert tagger.tag(["The", "run", "was", "great", "."], {'inline': True}) == "The/dt run/nn was/vbd great/jj ."
    assert tagger.tag(["They", "are", "the", "beaten", "."], {'inline': True}) == "They/prp are/vbp the/dt beaten/nn ."
    assert tagger.tag(["A", "diss", "."], {'inline': True}) == "A/dt diss/nns ."
    assert tagger.tag(["The", "soon", "."], {'inline': True}) == "The/dt soon/jj ."
    assert tagger.tag(["The", "sooner", "."], {'inline': True}) == "The/dt sooner/jjr ."
    assert tagger.tag(["The", "soonest", "."], {'inline': True}) == "The/dt soonest/jjs ."
    # rule 2
    assert tagger.tag(["It", "is", "59876", "."], {'inline': True}) == "It/prp is/vbz 59876/cd ."
    # rule 3
    assert tagger.tag(["I", "teabaged", "."], {'inline': True}) == "I/prp teabaged/vbn ."
    assert tagger.tag(["Sun", "teabaged", "."], {'inline': True}) == "Sun/nn teabaged/vbn ."
    assert tagger.tag(["The", "worker", "proletarianized", "."], {'inline': True}) == "The/dt worker/nn proletarianized/vbn ."
    # rule 4
    assert tagger.tag(["The", "fortunately", "."], {'inline': True}) == "The/dt fortunately/rb ."
    assert tagger.tag(["He", "is", "goodly", "working", "."], {'inline': True}) == "He/prp is/vbz goodly/rb working/vbg ."
    # rule 5
    assert tagger.tag(["It", "is", "nonexistional", "."], {'inline': True}) == "It/prp is/vbz nonexistional/jj ."
    assert tagger.tag(["It", "is", "mammal", "."], {'inline': True}) == "It/prp is/vbz mammal/nn ."
    assert tagger.tag(["It", "is", "onal", "."], {'inline': True}) == "It/prp is/vbz onal/nn ."
    # rule 6
    assert tagger.tag(["We", "must", "place", "it", "."], {'inline': True}) == "We/prp must/md place/vb it/prp ."
    assert tagger.tag(["We", "must", "teabag", "him", "."], {'inline': True}) == "We/prp must/md teabag/vb him/prp ."
    # rule 7
    assert tagger.tag(["He", "has", "played", "it", "."], {'inline': True}) == "He/prp has/vbz played/vbn it/prp ."
    assert tagger.tag(["He", "gets", "played", "."], {'inline': True}) == "He/prp gets/vbz played/vbn ."
    # rule 8
    assert tagger.tag(["The", "morning", "."], {'inline': True}) == "The/dt morning/nn ."
    assert tagger.tag(["They", "are", "fishing", "."], {'inline': True}) == "They/prp are/vbp fishing/vbg ."
    # rule 9
    assert tagger.tag(["He", "dances", "."], {'inline': True}) == "He/prp dances/vbz ."
    assert tagger.tag(["The", "dog", "dances", "."], {'inline': True}) == "The/dt dog/nn dances/vbz ."
    assert tagger.tag(["Dave", "dances", "."], {'inline': True}) == "Dave/nnp dances/vbz ."
    # rule 10
    assert tagger.tag(["Taipei", "."], {'inline': True}) == "Taipei/nnp ."
    assert tagger.tag(["Buddhas", "."], {'inline': True}) == "Buddhas/nnps ."
    assert tagger.tag(["In", "Beijing", "."], {'inline': True}) == "In/in Beijing/nnp ."
    assert tagger.tag(["One", "of", "the", "Beats", "."], {'inline': True}) == "One/cd of/in the/dt Beats/nnps ."
    assert tagger.tag(["Taipei", "is", "a", "big", "city", "."], {'inline': True}) == "Taipei/nnp is/vbz a/dt big/jj city/nn ."
    assert tagger.tag(["Buddhas", "in", "this", "temple", "have", "a", "history", "of", "500", "years", "."], {'inline': True}) == "Buddhas/nnps in/in this/dt temple/nn have/vbp a/dt history/nn of/in 500/cd years/nns ."
    assert tagger.tag(["Balls", "on", "the", "floor", "."], {'inline': True}) == "Balls/nns on/in the/dt floor/nn ."
    # rule 11
    assert tagger.tag(["dances", "."], {'inline': True}) == "dances/nns ."
    assert tagger.tag(["dances", "and", "performances", "."], {'inline': True}) == "dances/nns and/cc performances/nns ."
    assert tagger.tag(["cakes", "quickly", "."], {'inline': True}) == "cakes/nns quickly/rb ."
    assert tagger.tag(["dances", "quickly", "."], {'inline': True}) == "dances/vbz quickly/rb ."
    # rule 12
    assert tagger.tag(["David", "cakes", "."], {'inline': True}) == "David/nnp cakes/nns ."
    assert tagger.tag(["David", "laughs", "and", "dances", "."], {'inline': True}) == "David/nnp laughs/vbz and/cc dances/vbz ."
    assert tagger.tag(["counterattacks", "."], {'inline': True}) == "counterattacks/nns ."
    # rule 13
    assert tagger.tag(["Monkeys", "run", "."], {'inline': True}) == "Monkeys/nns run/vbp ."
    assert tagger.tag(["Monkeys", "attack", "."], {'inline': True}) == "Monkeys/nns attack/vbp ."
    assert tagger.tag(["A", "light", "blue", "sky", "."], {'inline': True}) == "A/dt light/jj blue/jj sky/nn ."
    # issue#177
    assert tagger.tag(["It", "broke", "."], {'inline': True}) == "It/prp broke/vbd ."
    assert tagger.tag(["It", "outpaced", "that", "."], {'inline': True}) == "It/prp outpaced/vbd that/in ."
    assert tagger.tag(["She", "remade", "this", "video", "."], {'inline': True}) == "She/prp remade/vbd this/dt video/nn ."
    assert tagger.tag(["She", "has", "remade", "this", "video", "."], {'inline': True}) == "She/prp has/vbz remade/vbn this/dt video/nn ."

# ── hyphenated words ─────────────────────────────────────────────────────────

def test_hyphenated_words():
    pool = [
        'He is my father-in-law.',
        'We have a off-site meeting yesterday.',
        'I know a great place for an off-site.',
        'a state-of-the-art computer',
        'The girls wanted the merry-go-round to go faster.',
        'He ate twenty-one burgers today.',
        'The politician arrived by high-speed railway.',
        'People doing yoga benefit from an increased feeling of well-being.',
        'There is a life-size statue of the dragon in the park.',
        'He has a king-size bed in his room.',
        'I am taking a full-time job now',
        'The cost for the round-trip ticket is 2000 dollars.',
        'The cost is 2000 dollars for the round-trip.',
        'He come back empty-handed',
        'She is left-handed',
        'I like the dress of the long-haired girl in the photo.',
        'His move was breath-taking.',
        'Snakes are cold-blooded.',
        'People liked to wear bell-bottoms in the 80s.',
        'This shop mainly sells corn-fed meat.',
        'I withdraw the application and re-apply for another position.',
        'Our co-manager believe in neo-liberalism.',
        'He did a u-turn.',
        'We are not going to get down to the nitty-gritty analysis of value for money.',
        'The game require co-op with your teammates.',
        'He was a roly-poly little man.'
    ]
    answers = [
        ["prp", "vbz", "prp$", "nn", "."],
        ["prp", "vbp", "dt", "jj", "vbg", "nn", "."],
        ["prp", "vbp", "dt", "jj", "nn", "in", "dt", "nn", "."],
        ["dt", "jj", "nn"],
        ["dt", "nns", "vbd", "dt", "nn", "to", "vb", "rbr", "."],
        ["prp", "vbd", "cd", "nns", "nn", "."],
        ["dt", "nn", "vbd", "in", "jj", "nn", "."],
        ["nn", "vbg", "nn", "nn", "in", "dt", "jj", "vbg", "in", "nn", "."],
        ["ex", "vbz", "dt", "jj", "nn", "in", "dt", "nn", "in", "dt", "nn", "."],
        ["prp", "vbz", "dt", "jj", "nn", "in", "prp$", "nn", "."],
        ["prp", "vbp", "vbg", "dt", "jj", "nn", "rb"],
        ["dt", "nn", "in", "dt", "jj", "nn", "vbz", "cd", "nns", "."],
        ["dt", "nn", "vbz", "cd", "nns", "in", "dt", "nn", "."],
        ["prp", "vbp", "rb", "jj"],
        ["prp", "vbz", "jj"],
        ["prp", "vbp", "dt", "nn", "in", "dt", "jj", "nn", "in", "dt", "nn", "."],
        ["prp$", "nn", "vbd", "jj", "."],
        ["nns", "vbp", "jj", "."],
        ["nn", "vbd", "to", "vb", "nn", "in", "dt", "nns", "."],
        ["dt", "nn", "rb", "nns", "jj", "nn", "."],
        ["prp", "vbp", "dt", "nn", "cc", "vb", "in", "dt", "nn", "."],
        ["prp$", "nn", "vbp", "in", "nn", "."],
        ["prp", "vbd", "dt", "nn", "."],
        ["prp", "vbp", "rb", "vbg", "to", "vb", "rb", "to", "dt", "nn", "nn", "in", "nn", "in", "nn", "."],
        ["dt", "nn", "vb", "nn", "in", "prp$", "nns", "."],
        ["prp", "vbd", "dt", "jj", "jj", "nn", "."]
    ]
    for i, sentence in enumerate(pool):
        result = pos(sentence)
        assert result == answers[i], f"failed at [{i}]: {sentence!r}\n  got {result}\n  exp {answers[i]}"
