"""
test_conjugator.py — Tests for rita/conjugator.py
Ported from ritajs/test/conjugator-tests.js
"""
import pytest
from rita.conjugator import (
    Conjugator,
    FIRST, SECOND, THIRD,
    PAST, PRESENT, FUTURE,
    SINGULAR, PLURAL, NORMAL,
    INFINITIVE, GERUND,
)

conj = Conjugator()


class TestPastPart:
    def test_basic(self):
        assert conj.past_part("pen") == "penned"
        assert conj.past_part("red") == "red"
        assert conj.past_part("sleep") == "slept"
        assert conj.past_part("withhold") == "withheld"
        assert conj.past_part("cut") == "cut"
        assert conj.past_part("go") == "gone"
        assert conj.past_part("swim") == "swum"
        assert conj.past_part("would") == "would"
        assert conj.past_part("might") == "might"
        assert conj.past_part("run") == "run"
        assert conj.past_part("speak") == "spoken"
        assert conj.past_part("break") == "broken"
        assert conj.past_part("plead") == "pled"
        assert conj.past_part("") == ""
        assert conj.past_part("shrink") == "shrunk"
        assert conj.past_part("stink") == "stunk"
        assert conj.past_part("study") == "studied"
        assert conj.past_part("bite") == "bitten"
        assert conj.past_part("break") == "broken"
        assert conj.past_part("call") == "called"
        assert conj.past_part("commit") == "committed"
        assert conj.past_part("computerize") == "computerized"
        assert conj.past_part("concern") == "concerned"
        assert conj.past_part("discriminate") == "discriminated"
        assert conj.past_part("end") == "ended"
        assert conj.past_part("expect") == "expected"
        assert conj.past_part("finish") == "finished"
        assert conj.past_part("gain") == "gained"
        assert conj.past_part("get") == "gotten"
        assert conj.past_part("increase") == "increased"
        assert conj.past_part("involve") == "involved"
        assert conj.past_part("launch") == "launched"
        assert conj.past_part("lead") == "led"
        assert conj.past_part("live") == "lived"
        assert conj.past_part("outpace") == "outpaced"
        assert conj.past_part("oversee") == "overseen"
        assert conj.past_part("oversell") == "oversold"
        assert conj.past_part("pale") == "paled"
        assert conj.past_part("prepay") == "prepaid"
        assert conj.past_part("pressure") == "pressured"
        assert conj.past_part("proliferate") == "proliferated"
        assert conj.past_part("remake") == "remade"
        assert conj.past_part("reopen") == "reopened"
        assert conj.past_part("report") == "reported"
        assert conj.past_part("resell") == "resold"
        assert conj.past_part("settle") == "settled"
        assert conj.past_part("build") == "built"
        assert conj.past_part("enter") == "entered"
        assert conj.past_part("own") == "owned"
        assert conj.past_part("plan") == "planned"
        assert conj.past_part("rent") == "rented"
        assert conj.past_part("repurchase") == "repurchased"
        assert conj.past_part("roast") == "roasted"
        assert conj.past_part("start") == "started"
        assert conj.past_part("bust") == "busted"
        assert conj.past_part("heart") == "hearted"
        assert conj.past_part("closet") == "closeted"
        assert conj.past_part("bear") == "borne"

    def test_already_past_part(self):
        # is already past participle — should return unchanged
        assert conj.past_part("hopped") == "hopped"
        assert conj.past_part("hated") == "hated"
        assert conj.past_part("created") == "created"
        assert conj.past_part("committed") == "committed"
        assert conj.past_part("submitted") == "submitted"
        assert conj.past_part("come") == "come"
        assert conj.past_part("forgotten") == "forgotten"
        assert conj.past_part("arisen") == "arisen"
        assert conj.past_part("eaten") == "eaten"
        assert conj.past_part("chosen") == "chosen"
        assert conj.past_part("frozen") == "frozen"
        assert conj.past_part("stolen") == "stolen"
        assert conj.past_part("worn") == "worn"
        assert conj.past_part("broken") == "broken"
        assert conj.past_part("written") == "written"
        assert conj.past_part("ridden") == "ridden"
        assert conj.past_part("drawn") == "drawn"
        assert conj.past_part("known") == "known"
        assert conj.past_part("grown") == "grown"
        assert conj.past_part("done") == "done"
        assert conj.past_part("gone") == "gone"
        assert conj.past_part("awake") == "awoken"
        assert conj.past_part("become") == "become"
        assert conj.past_part("drink") == "drunk"
        assert conj.past_part("run") == "run"
        assert conj.past_part("shine") == "shone"
        assert conj.past_part("grown") == "grown"
        assert conj.past_part("heard") == "heard"


class TestPresentPart:
    def test_basic(self):
        assert conj.present_part("") == ""
        assert conj.present_part("sleep") == "sleeping"
        assert conj.present_part("withhold") == "withholding"
        assert conj.present_part("cut") == "cutting"
        assert conj.present_part("go") == "going"
        assert conj.present_part("run") == "running"
        assert conj.present_part("speak") == "speaking"
        assert conj.present_part("break") == "breaking"
        assert conj.present_part("become") == "becoming"
        assert conj.present_part("plead") == "pleading"
        assert conj.present_part("awake") == "awaking"
        assert conj.present_part("study") == "studying"
        assert conj.present_part("lie") == "lying"
        assert conj.present_part("swim") == "swimming"
        assert conj.present_part("dig") == "digging"
        assert conj.present_part("set") == "setting"
        assert conj.present_part("bring") == "bringing"
        assert conj.present_part("study ") == "studying"   # trim
        assert conj.present_part(" study") == "studying"   # trim
        assert conj.present_part("hoe") == "hoeing"
        assert conj.present_part("shoe") == "shoeing"


class TestConjugateVBDs:
    def test_past_irregular(self):
        assert conj.conjugate("go", {
            "number": SINGULAR, "person": FIRST, "tense": PAST
        }) == "went"
        assert conj.conjugate("run", {
            "number": SINGULAR, "person": FIRST, "tense": PAST
        }) == "ran"


class TestConjugate:
    def test_no_args(self):
        assert conj.conjugate("walk") == "walk"

    def test_errors(self):
        with pytest.raises((ValueError, Exception)):
            conj.conjugate("")
        with pytest.raises((ValueError, Exception)):
            conj.conjugate("walk", "invalid args")

    def test_gerund(self):
        assert conj.conjugate("be", {"form": GERUND}) == "being"

    def test_are_past(self):
        assert conj.conjugate("are", {
            "number": PLURAL, "person": SECOND, "tense": PAST
        }) == "were"

    def test_3rd_sing_present(self):
        s = ["swim", "need", "open"]
        a = ["swims", "needs", "opens"]
        args = {"tense": PRESENT, "number": SINGULAR, "person": THIRD}
        for i, w in enumerate(s):
            assert conj.conjugate(w, args) == a[i]

    def test_passive_present(self):
        s = ["swim", "need", "open"]
        a = ["is swum", "is needed", "is opened"]
        args = {"tense": PRESENT, "number": SINGULAR, "person": THIRD, "passive": True}
        for i, w in enumerate(s):
            assert conj.conjugate(w, args) == a[i]

    def test_past_1st_sing(self):
        assert conj.conjugate("swim", {
            "number": SINGULAR, "person": FIRST, "tense": PAST
        }) == "swam"

    def test_past_general(self):
        s = ["swim", "need", "open"]
        a = ["swam", "needed", "opened"]
        args = {"number": SINGULAR, "person": FIRST, "tense": PAST}
        for i, w in enumerate(s):
            assert conj.conjugate(w, args) == a[i]

    def test_future(self):
        s = ["swim", "need", "open"]
        a = ["will swim", "will need", "will open"]
        args = {"number": PLURAL, "person": SECOND, "tense": FUTURE}
        for i, w in enumerate(s):
            assert conj.conjugate(w, args) == a[i]

    def test_infinitive(self):
        s = ["swim", "need", "open"]
        a = ["to swim", "to need", "to open"]
        args = {"tense": PAST, "number": SINGULAR, "person": THIRD, "form": INFINITIVE}
        for i, w in enumerate(s):
            assert conj.conjugate(w, args) == a[i]

    def test_passive_past(self):
        s = ["scorch", "burn", "hit"]
        a = ["was scorched", "was burned", "was hit"]
        args = {"tense": PAST, "number": SINGULAR, "person": THIRD, "passive": True}
        for i, w in enumerate(s):
            assert conj.conjugate(w, args) == a[i]

    def test_infinitive_progressive(self):
        s = ["swim", "need", "open"]
        a = ["to be swimming", "to be needing", "to be opening"]
        args = {"tense": PRESENT, "number": SINGULAR, "person": THIRD,
                "form": INFINITIVE, "progressive": True}
        for i, w in enumerate(s):
            assert conj.conjugate(w, args) == a[i]

    def test_infinitive_perfect(self):
        s = ["swim", "need", "open"]
        a = ["to have swum", "to have needed", "to have opened"]
        args = {"tense": PRESENT, "number": SINGULAR, "person": THIRD,
                "form": INFINITIVE, "perfect": True}
        for i, w in enumerate(s):
            assert conj.conjugate(w, args) == a[i]

    def test_barter_run_past(self):
        args = {"number": PLURAL, "person": SECOND, "tense": PAST}
        assert conj.conjugate("barter", args) == "bartered"
        assert conj.conjugate("run", args) == "ran"

    def test_compete_past(self):
        args = {"number": PLURAL, "person": SECOND, "tense": PAST}
        s = ["compete", "complete", "eject"]
        a = ["competed", "completed", "ejected"]
        for i, w in enumerate(s):
            assert conj.conjugate(w, args) == a[i]

    def test_interrogative(self):
        args = {"number": PLURAL, "person": SECOND, "tense": PAST, "interrogative": True}
        s = ["compete", "complete", "eject"]
        for w in s:
            assert conj.conjugate(w, args) == w

    def test_string_args(self):
        assert conj.conjugate("walk", "1SPr") == "walk"
        assert conj.conjugate("walk", "1PPr") == "walk"
        assert conj.conjugate("walk", "2SPr") == "walk"
        assert conj.conjugate("walk", "3SPr") == "walks"
        assert conj.conjugate("walk", "1SFu") == "will walk"
        assert conj.conjugate("walk", "1SPa") == "walked"
        assert conj.conjugate("walk", "2PPa") == "walked"
        assert conj.conjugate("is", "3PPa") == "were"
        assert conj.conjugate("is", "2SPa") == "were"
        assert conj.conjugate("is", "3SPa") == "was"
        assert conj.conjugate("is", "2PPa") == "were"

    def test_4param_passive(self):
        original = ["run", "walk", "swim", "create"]
        expected = ["is run", "is walked", "is swum", "is created"]
        for i, w in enumerate(original):
            assert conj.conjugate(w, {"person": THIRD, "passive": True}) == expected[i]

    def test_4param_progressive(self):
        original = ["run", "walk", "swim", "create"]
        expected = ["is running", "is walking", "is swimming", "is creating"]
        for i, w in enumerate(original):
            assert conj.conjugate(w, {"person": THIRD, "progressive": True}) == expected[i]

    def test_4param_interrogative(self):
        original = ["run", "walk", "swim", "create"]
        expected = ["run", "walk", "swim", "create"]
        for i, w in enumerate(original):
            assert conj.conjugate(w, {"person": THIRD, "interrogative": True}) == expected[i]

    def test_4param_perfect(self):
        original = ["run", "walk", "swim", "create"]
        expected = ["has run", "has walked", "has swum", "has created"]
        for i, w in enumerate(original):
            assert conj.conjugate(w, {"person": THIRD, "perfect": True}) == expected[i]

    def test_gerund_passive(self):
        original = ["run", "walk", "swim", "create"]
        expected = ["being run", "being walked", "being swum", "being created"]
        for i, w in enumerate(original):
            assert conj.conjugate(w, {"person": THIRD, "passive": True, "form": GERUND}) == expected[i]

    def test_gerund_progressive(self):
        original = ["run", "walk", "swim", "create"]
        expected = ["being running", "being walking", "being swimming", "being creating"]
        for i, w in enumerate(original):
            assert conj.conjugate(w, {"person": THIRD, "progressive": True, "form": GERUND}) == expected[i]

    def test_gerund_interrogative(self):
        original = ["run", "walk", "swim", "create"]
        expected = ["running", "walking", "swimming", "creating"]
        for i, w in enumerate(original):
            assert conj.conjugate(w, {"person": THIRD, "interrogative": True, "form": GERUND}) == expected[i]

    def test_gerund_perfect(self):
        original = ["run", "walk", "swim", "create"]
        expected = ["having run", "having walked", "having swum", "having created"]
        for i, w in enumerate(original):
            assert conj.conjugate(w, {"person": THIRD, "perfect": True, "form": GERUND}) == expected[i]

    def test_infinitive_passive(self):
        original = ["run", "walk", "swim", "create"]
        expected = ["to be run", "to be walked", "to be swum", "to be created"]
        for i, w in enumerate(original):
            assert conj.conjugate(w, {"person": THIRD, "passive": True, "form": INFINITIVE}) == expected[i]

    def test_infinitive_progressive(self):
        original = ["run", "walk", "swim", "create"]
        expected = ["to be running", "to be walking", "to be swimming", "to be creating"]
        for i, w in enumerate(original):
            assert conj.conjugate(w, {"person": THIRD, "progressive": True, "form": INFINITIVE}) == expected[i]

    def test_infinitive_interrogative(self):
        original = ["run", "walk", "swim", "create"]
        expected = ["to run", "to walk", "to swim", "to create"]
        for i, w in enumerate(original):
            assert conj.conjugate(w, {"person": THIRD, "interrogative": True, "form": INFINITIVE}) == expected[i]

    def test_infinitive_perfect(self):
        original = ["run", "walk", "swim", "create"]
        expected = ["to have run", "to have walked", "to have swum", "to have created"]
        for i, w in enumerate(original):
            assert conj.conjugate(w, {"person": THIRD, "perfect": True, "form": INFINITIVE}) == expected[i]

    def test_non_base_form(self):
        assert conj.conjugate("walked", "3SPr") == "walks"
        assert conj.conjugate("changed", "3SPr") == "changes"
        assert conj.conjugate("spent", "3SPr") == "spends"
        assert conj.conjugate("eaten", "3SPr") == "eats"


class TestToString:
    def test_tostring(self):
        # state is set after conjugate("swim", "2PPa") per JS test
        conj.conjugate("swim", "2PPa")
        expected = (
            "  ---------------------\n"
            "  Passive = false\n"
            "  Perfect = false\n"
            "  Progressive = false\n"
            "  ---------------------\n"
            "  Number = 8\n"
            "  Person = 2\n"
            "  Tense = 4\n"
            "  ---------------------\n"
        )
        assert str(conj) == expected


class TestUnconjugate:
    def test_3rd_person_singular(self):
        assert conj.unconjugate("trepanning") == "trepan"
        assert conj.unconjugate("plays") == "play"
        assert conj.unconjugate("takes") == "take"
        assert conj.unconjugate("gets") == "get"
        assert conj.unconjugate("comes") == "come"
        assert conj.unconjugate("goes") == "go"
        assert conj.unconjugate("teaches") == "teach"
        assert conj.unconjugate("fixes") == "fix"
        assert conj.unconjugate("misses") == "miss"
        assert conj.unconjugate("studies") == "study"
        assert conj.unconjugate("tries") == "try"
        assert conj.unconjugate("carries") == "carry"
        assert conj.unconjugate("wishes") == "wish"
        assert conj.unconjugate("blitzes") == "blitz"

    def test_ed_regular(self):
        assert conj.unconjugate("watched") == "watch"
        assert conj.unconjugate("planted") == "plant"
        assert conj.unconjugate("watered") == "water"
        assert conj.unconjugate("pulled") == "pull"
        assert conj.unconjugate("picked") == "pick"
        assert conj.unconjugate("liked") == "like"
        assert conj.unconjugate("moved") == "move"
        assert conj.unconjugate("tasted") == "taste"
        assert conj.unconjugate("tried") == "try"
        assert conj.unconjugate("studied") == "study"
        assert conj.unconjugate("carried") == "carry"
        assert conj.unconjugate("digged") == "dig"
        assert conj.unconjugate("flagged") == "flag"

    def test_ing_regular(self):
        assert conj.unconjugate("blowing") == "blow"
        assert conj.unconjugate("raining") == "rain"
        assert conj.unconjugate("coming") == "come"
        assert conj.unconjugate("having") == "have"
        assert conj.unconjugate("running") == "run"
        assert conj.unconjugate("putting") == "put"
        assert conj.unconjugate("sitting") == "sit"
        assert conj.unconjugate("pulling") == "pull"

    def test_irregular(self):
        assert conj.unconjugate("has") == "have"
        assert conj.unconjugate("had") == "have"
        assert conj.unconjugate("sat") == "sit"
        assert conj.unconjugate("shown") == "show"
        assert conj.unconjugate("ate") == "eat"
        assert conj.unconjugate("went") == "go"
        assert conj.unconjugate("met") == "meet"

    def test_base_forms_unchanged(self):
        assert conj.unconjugate("have") == "have"
        assert conj.unconjugate("eat") == "eat"
        assert conj.unconjugate("play") == "play"
        assert conj.unconjugate("go") == "go"
        assert conj.unconjugate("do") == "do"

    def test_not_in_lexicon(self):
        assert conj.unconjugate("spooning") == "spoon"
        assert conj.unconjugate("mepanning") == "mepan"
        assert conj.unconjugate("muddling") == "muddle"

    def test_issue_177(self):
        assert conj.unconjugate("bitten") == "bite"
        assert conj.unconjugate("broken") == "break"
        assert conj.unconjugate("committed") == "commit"
        assert conj.unconjugate("computerized") == "computerize"
        assert conj.unconjugate("concerned") == "concern"
        assert conj.unconjugate("discriminated") == "discriminate"
        assert conj.unconjugate("ended") == "end"
        assert conj.unconjugate("expected") == "expect"
        assert conj.unconjugate("finished") == "finish"
        assert conj.unconjugate("gained") == "gain"
        assert conj.unconjugate("gotten") == "get"
        assert conj.unconjugate("increased") == "increase"
        assert conj.unconjugate("involved") == "involve"
        assert conj.unconjugate("launched") == "launch"
        assert conj.unconjugate("led") == "lead"
        assert conj.unconjugate("lived") == "live"
        assert conj.unconjugate("outpaced") == "outpace"
        assert conj.unconjugate("overseen") == "oversee"
        assert conj.unconjugate("paled") == "pale"
        assert conj.unconjugate("prepaid") == "prepay"
        assert conj.unconjugate("pressured") == "pressure"
        assert conj.unconjugate("proliferated") == "proliferate"
        assert conj.unconjugate("remade") == "remake"
        assert conj.unconjugate("reopened") == "reopen"
        assert conj.unconjugate("reported") == "report"
        assert conj.unconjugate("sold") == "sell"
        assert conj.unconjugate("resold") == "resell"
        assert conj.unconjugate("settled") == "settle"
        assert conj.unconjugate("started") == "start"
        assert conj.unconjugate("were") == "be"
        assert conj.unconjugate("owned") == "own"
        assert conj.unconjugate("planned") == "plan"
        assert conj.unconjugate("rented") == "rent"
        assert conj.unconjugate("repurchased") == "repurchase"
        assert conj.unconjugate("roasted") == "roast"
        assert conj.unconjugate("busted") == "bust"
        assert conj.unconjugate("grown") == "grow"
        assert conj.unconjugate("blown") == "blow"
        assert conj.unconjugate("heard") == "hear"


class TestConjugateVerbs:
    def test_past(self):
        opt = {"number": SINGULAR, "person": FIRST, "tense": PAST}
        assert conj.conjugate("bite", opt) == "bit"
        assert conj.conjugate("break", opt) == "broke"
        assert conj.conjugate("call", opt) == "called"
        assert conj.conjugate("commit", opt) == "committed"
        assert conj.conjugate("computerize", opt) == "computerized"
        assert conj.conjugate("concern", opt) == "concerned"
        assert conj.conjugate("discriminate", opt) == "discriminated"
        assert conj.conjugate("end", opt) == "ended"
        assert conj.conjugate("expect", opt) == "expected"
        assert conj.conjugate("finish", opt) == "finished"
        assert conj.conjugate("gain", opt) == "gained"
        assert conj.conjugate("get", opt) == "got"
        assert conj.conjugate("increase", opt) == "increased"
        assert conj.conjugate("involve", opt) == "involved"
        assert conj.conjugate("launch", opt) == "launched"
        assert conj.conjugate("lead", opt) == "led"
        assert conj.conjugate("live", opt) == "lived"
        assert conj.conjugate("oversee", opt) == "oversaw"
        assert conj.conjugate("pale", opt) == "paled"
        assert conj.conjugate("prepay", opt) == "prepaid"
        assert conj.conjugate("pressure", opt) == "pressured"
        assert conj.conjugate("proliferate", opt) == "proliferated"
        assert conj.conjugate("remake", opt) == "remade"
        assert conj.conjugate("reopen", opt) == "reopened"
        assert conj.conjugate("report", opt) == "reported"
        assert conj.conjugate("resell", opt) == "resold"
        assert conj.conjugate("settle", opt) == "settled"
        assert conj.conjugate("start", opt) == "started"

    def test_present_perfect(self):
        opt = {"tense": PRESENT, "number": SINGULAR, "perfect": True}
        assert conj.conjugate("bite", opt) == "have bitten"
        assert conj.conjugate("break", opt) == "have broken"
        assert conj.conjugate("build", opt) == "have built"
        assert conj.conjugate("enter", opt) == "have entered"
        assert conj.conjugate("own", opt) == "have owned"
        assert conj.conjugate("plan", opt) == "have planned"
        assert conj.conjugate("rent", opt) == "have rented"
        assert conj.conjugate("repurchase", opt) == "have repurchased"
        assert conj.conjugate("roast", opt) == "have roasted"


# ── accept stems ─────────────────────────────────────────────────────────────

class TestAcceptStems:
    def test_accept_stems(self):
        from rita.rita import RiTa

        plur_past2  = {"number": PLURAL,    "person": SECOND, "tense": PAST}
        plur_pres2  = {"number": PLURAL,    "person": SECOND, "tense": PRESENT}
        sing_pres3  = {"number": SINGULAR,  "person": THIRD,  "tense": PRESENT}

        stem = RiTa.stem("walking")
        assert conj.conjugate(stem, plur_past2) == "walked",  f"{stem} => walked"
        assert conj.conjugate(stem, plur_pres2) == "walk",    f"{stem} => walk"
        assert conj.conjugate(stem, sing_pres3) == "walks",   f"{stem} => walks"

        stem = RiTa.stem("writing")
        assert conj.conjugate(stem, plur_past2) == "wrote",   f"{stem} => wrote"
        assert conj.conjugate(stem, plur_pres2) == "write",   f"{stem} => write"
        assert conj.conjugate(stem, sing_pres3) == "writes",  f"{stem} => writes"

        stem = RiTa.stem("asked")
        assert conj.conjugate(stem, plur_past2) == "asked",   f"{stem} => asked"
        assert conj.conjugate(stem, plur_pres2) == "ask",     f"{stem} => ask"
        assert conj.conjugate(stem, sing_pres3) == "asks",    f"{stem} => asks"

        stem = RiTa.stem("changed")
        assert conj.conjugate(stem, plur_past2) == "changed", f"{stem} => changed"
        assert conj.conjugate(stem, plur_pres2) == "change",  f"{stem} => change"
        assert conj.conjugate(stem, sing_pres3) == "changes", f"{stem} => changes"

        stem = RiTa.stem("admired")
        assert conj.conjugate(stem, plur_past2) == "admired", f"{stem} => admired"
        assert conj.conjugate(stem, plur_pres2) == "admire",  f"{stem} => admire"
        assert conj.conjugate(stem, sing_pres3) == "admires", f"{stem} => admires"

        stem = RiTa.stem("cured")
        assert conj.conjugate(stem, plur_past2) == "cured",   f"{stem} => cured"
        assert conj.conjugate(stem, plur_pres2) == "cure",    f"{stem} => cure"
        assert conj.conjugate(stem, sing_pres3) == "cures",   f"{stem} => cures"

        stem = RiTa.stem("studies")
        assert conj.conjugate(stem, plur_past2) == "studied", f"{stem} => studied"
        assert conj.conjugate(stem, plur_pres2) == "study",   f"{stem} => study"
        assert conj.conjugate(stem, sing_pres3) == "studies", f"{stem} => studies"

    def test_stem_pairs(self):
        from rita.rita import RiTa

        opts = {"number": PLURAL, "person": SECOND, "tense": PAST}
        pairs = [
            ("accompanying", "accompanied"),
            ("feeling",       "felt"),
            ("placating",     "placated"),
            ("centralizing",  "centralized"),
            ("humanized",     "humanized"),
            ("boosted",       "boosted"),
            ("wearing",       "wore"),
            ("aroused",       "aroused"),
            ("rising",        "rose"),
            ("raising",       "raised"),
            ("vibrating",     "vibrated"),
            ("injection",     "injected"),
            ("vibration",     "vibrated"),
        ]
        for word, expected in pairs:
            stem = RiTa.stem(word)
            result = conj.conjugate(stem, opts)
            assert result == expected, f"{word} => {stem} => {result} (expected {expected})"
