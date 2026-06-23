"""
test_inflector.py — Python port of inflector tests from
ritajs/test/analyzer-tests.js  (inflector-related blocks)
"""
import pytest
from rita.inflector import Inflector


@pytest.fixture
def inf():
    return Inflector()


# ── basic API ─────────────────────────────────────────────────────────────────

class TestInflectorBasic:

    def test_empty_inputs(self, inf):
        assert inf.singularize() == ""
        assert inf.singularize("") == ""
        assert inf.pluralize() == ""
        assert inf.pluralize("") == ""

    def test_bad_inputs_raise(self, inf):
        with pytest.raises(TypeError):
            inf.singularize([1])
        with pytest.raises(TypeError):
            inf.singularize(1)
        with pytest.raises(TypeError):
            inf.pluralize([1])
        with pytest.raises(TypeError):
            inf.pluralize(1)

    def test_is_plural_empty(self, inf):
        assert inf.is_plural() == False
        assert inf.is_plural("") == False

    def test_is_plural_basic(self, inf):
        assert inf.is_plural("octopus") == False
        assert inf.is_plural("sheep") == True
        assert inf.is_plural("apples") == True
        assert inf.is_plural("leaves") == True
        assert inf.is_plural("feet") == True
        assert inf.is_plural("beaux") == False
        assert inf.is_plural("child") == False
        assert inf.is_plural("abbots") == True
        assert inf.is_plural("happiness") == True

    def test_is_plural_mass_nouns(self, inf):
        assert inf.is_plural("pasta") == True
        assert inf.is_plural("honey") == True
        assert inf.is_plural("fanfare") == True
        assert inf.is_plural("medicare") == True
        assert inf.is_plural("childcare") == True

    def test_dreariness_is_plural(self, inf):
        assert inf.is_plural("dreariness") == True


# ── already-plural nouns (pluralize should return unchanged) ──────────────────

class TestAlreadyPlural:

    def test_do_nothing_when_already_plural(self, inf):
        tests = ["tidings", "schnapps", "canvases", "censuses", "bonuses",
                 "isthmuses", "thermoses", "circuses", "tongs", "emeriti"]
        for word in tests:
            assert inf.pluralize(word) == word, f"pluralize({word!r}) should be unchanged"

    def test_is_plural_for_already_plural(self, inf):
        tests = ["tidings", "schnapps", "canvases", "censuses", "bonuses",
                 "isthmuses", "thermoses", "circuses", "tongs", "emeriti"]
        for word in tests:
            assert inf.is_plural(word) == True, f"isPlural({word!r}) should be True"


# ── mass / uncountable nouns ──────────────────────────────────────────────────

class TestMassNouns:

    def test_pluralize_uncountables(self, inf):
        assert inf.pluralize("honey") == "honey"
        assert inf.pluralize("pasta") == "pasta"
        assert inf.pluralize("advice") == "advice"
        assert inf.pluralize("fanfare") == "fanfare"
        assert inf.pluralize("medicare") == "medicare"
        assert inf.pluralize("childcare") == "childcare"

    def test_singularize_uncountables(self, inf):
        assert inf.singularize("honey") == "honey"
        assert inf.singularize("pasta") == "pasta"
        assert inf.singularize("advice") == "advice"
        assert inf.singularize("fanfare") == "fanfare"
        assert inf.singularize("medicare") == "medicare"
        assert inf.singularize("childcare") == "childcare"


# ── phrase pluralization ──────────────────────────────────────────────────────

class TestPhrasePluralize:

    def test_pluralize_of_phrases(self, inf):
        assert inf.pluralize_phrase("set of choice") == "set of choices"
        assert inf.pluralize_phrase("bag of chocolate") == "bag of chocolates"
        assert inf.pluralize_phrase("gaggle of goose") == "gaggle of geese"


# ── main test-pairs (singularize + pluralize + isPlural) ─────────────────────

# Each entry: (plural, singular)
TEST_PAIRS = [
    ("abysses", "abyss"),
    ("knives", "knife"),
    ("dazes", "daze"),
    ("hives", "hive"),
    ("dives", "dive"),
    ("octopuses", "octopus"),
    ("abalone", "abalone"),
    ("wildlife", "wildlife"),
    ("minutiae", "minutia"),
    ("spoofs", "spoof"),
    ("proofs", "proof"),
    ("roofs", "roof"),
    ("disbeliefs", "disbelief"),
    ("beliefs", "belief"),
    ("indices", "index"),
    ("accomplices", "accomplice"),
    ("prognoses", "prognosis"),
    ("taxis", "taxi"),
    ("chiefs", "chief"),
    ("monarchs", "monarch"),
    ("lochs", "loch"),
    ("stomachs", "stomach"),
    ("Chinese", "Chinese"),
    ("people", "person"),
    ("humans", "human"),
    ("germans", "german"),
    ("romans", "roman"),
    ("memoranda", "memorandum"),
    ("data", "datum"),
    ("geese", "goose"),
    ("femurs", "femur"),
    ("appendices", "appendix"),
    ("theses", "thesis"),
    ("alumni", "alumnus"),
    ("solos", "solo"),
    ("music", "music"),
    ("oxen", "ox"),
    ("money", "money"),
    ("beef", "beef"),
    ("tobacco", "tobacco"),
    ("cargo", "cargo"),
    ("golf", "golf"),
    ("grief", "grief"),
    ("cakes", "cake"),
    ("tomatoes", "tomato"),
    ("photos", "photo"),
    ("smallpox", "smallpox"),
    ("toes", "toe"),
    ("mice", "mouse"),
    ("lice", "louse"),
    ("children", "child"),
    ("gases", "gas"),
    ("buses", "bus"),
    ("happiness", "happiness"),
    ("apotheoses", "apotheosis"),
    ("stimuli", "stimulus"),
    ("dogs", "dog"),
    ("feet", "foot"),
    ("teeth", "tooth"),
    ("deer", "deer"),
    ("sheep", "sheep"),
    ("shrimp", "shrimp"),
    ("men", "man"),
    ("women", "woman"),
    ("congressmen", "congressman"),
    ("aldermen", "alderman"),
    ("freshmen", "freshman"),
    ("firemen", "fireman"),
    ("grandchildren", "grandchild"),
    ("menus", "menu"),
    ("gurus", "guru"),
    ("hardness", "hardness"),
    ("fish", "fish"),
    ("ooze", "ooze"),
    ("enterprises", "enterprise"),
    ("treatises", "treatise"),
    ("houses", "house"),
    ("chemises", "chemise"),
    ("aquatics", "aquatics"),
    ("mechanics", "mechanics"),
    ("quarters", "quarter"),
    ("motifs", "motif"),
    ("turf", "turf"),
    ("macaroni", "macaroni"),
    ("spaghetti", "spaghetti"),
    ("potpourri", "potpourri"),
    ("electrolysis", "electrolysis"),
    ("series", "series"),
    ("crises", "crisis"),
    ("corpora", "corpus"),
    ("shortness", "shortness"),
    ("dreariness", "dreariness"),
    ("unwillingness", "unwillingness"),
    ("moose", "moose"),
    ("lives", "life"),
    ("additives", "additive"),
    ("epochs", "epoch"),
    ("ranchs", "ranch"),
    ("alcoves", "alcove"),
    ("memories", "memory"),
    ("grooves", "groove"),
    ("universes", "universe"),
    ("toothbrushes", "toothbrush"),
    ("clashes", "clash"),
    ("addresses", "address"),
    ("flashes", "flash"),
    ("conclaves", "conclave"),
    ("promises", "promise"),
    ("spouses", "spouse"),
    ("branches", "branch"),
    ("lapses", "lapse"),
    ("quizes", "quiz"),
    ("spyglasses", "spyglass"),
    ("overpasses", "overpass"),
    ("clones", "clones"),
    ("microwaves", "microwave"),
    ("hypotheses", "hypothesis"),
    ("pretenses", "pretense"),
    ("latches", "latch"),
    ("fetuses", "fetus"),
    ("lighthouses", "lighthouse"),
    ("genuses", "genus"),
    ("zombies", "zombie"),
    ("hearses", "hearse"),
    ("trenches", "trench"),
    ("paradoxes", "paradox"),
    ("hippies", "hippie"),
    ("yuppies", "yuppie"),
    ("purses", "purse"),
    ("hatches", "hatch"),
    ("witches", "witch"),
    ("sinuses", "sinus"),
    ("phrases", "phrase"),
    ("arches", "arch"),
    ("duplexes", "duplex"),
    ("missives", "missive"),
    ("madhouses", "madhouse"),
    ("pauses", "pause"),
    ("heroes", "hero"),
    ("sketches", "sketch"),
    ("meshes", "mesh"),
    ("brasses", "brass"),
    ("marshes", "marsh"),
    ("masses", "mass"),
    ("impulses", "impulse"),
    ("pelvises", "pelvis"),
    ("fetishes", "fetish"),
    ("gashes", "gash"),
    ("directives", "directive"),
    ("calories", "calorie"),
    ("moves", "move"),
    ("expanses", "expanse"),
    ("briefcases", "briefcase"),
    ("media", "medium"),
    ("millennia", "millennium"),
    ("consortia", "consortium"),
    ("concerti", "concerto"),
    ("septa", "septum"),
    ("termini", "terminus"),
    ("larvae", "larva"),
    ("vertebrae", "vertebra"),
    ("memorabilia", "memorabilium"),
    ("hooves", "hoof"),
    ("thieves", "thief"),
    ("rabbis", "rabbi"),
    ("flu", "flu"),
    ("safaris", "safari"),
    ("sheaves", "sheaf"),
    ("uses", "use"),
    ("pinches", "pinch"),
    ("catharses", "catharsis"),
    ("hankies", "hanky"),
    ("whizzes", "whiz"),
    ("selves", "self"),
    ("bookshelves", "bookshelf"),
    ("wheezes", "wheeze"),
    ("diagnoses", "diagnosis"),
    ("blondes", "blonde"),
    ("eyes", "eye"),
    ("swine", "swine"),
    ("cognoscenti", "cognoscenti"),
    ("bonsai", "bonsai"),
    ("rice", "rice"),
    ("clothes", "clothes"),
    ("goddesses", "goddess"),
    ("tresses", "tress"),
    ("murderesses", "murderess"),
    ("kisses", "kiss"),
]

# Mass-noun singulars for which isPlural(singular) == True is expected
_MASS_SINGULAR = {
    "abalone", "wildlife", "music", "money", "beef", "tobacco", "cargo",
    "golf", "grief", "smallpox", "deer", "sheep", "shrimp", "hardness",
    "fish", "ooze", "aquatics", "mechanics", "turf", "macaroni", "spaghetti",
    "potpourri", "electrolysis", "series", "moose", "clones", "clothes",
    "swine", "cognoscenti", "bonsai", "rice", "flu", "chinese",
}

# Singulars ending in -ness for which isPlural(singular) == True is expected
_NESS_SINGULAR = {
    "happiness", "hardness", "shortness", "dreariness", "unwillingness",
}


class TestPairs:

    @pytest.mark.parametrize("plural,singular", TEST_PAIRS)
    def test_singularize(self, inf, plural, singular):
        result = inf.singularize(plural)
        assert result == singular, (
            f"singularize({plural!r}) = {result!r}, expected {singular!r}")

    @pytest.mark.parametrize("plural,singular", TEST_PAIRS)
    def test_pluralize(self, inf, plural, singular):
        result = inf.pluralize(singular)
        assert result == plural, (
            f"pluralize({singular!r}) = {result!r}, expected {plural!r}")

    @pytest.mark.parametrize("plural,singular", TEST_PAIRS)
    def test_is_plural_plural_form(self, inf, plural, singular):
        assert inf.is_plural(plural) == True, (
            f"isPlural({plural!r}) should be True")

    @pytest.mark.parametrize("plural,singular", TEST_PAIRS)
    def test_is_plural_singular_form(self, inf, plural, singular):
        sing_lower = singular.lower()
        if sing_lower in _MASS_SINGULAR or sing_lower in _NESS_SINGULAR:
            return  # mass nouns / -ness forms are considered plural by isPlural
        assert inf.is_plural(singular) == False, (
            f"isPlural({singular!r}) should be False")
