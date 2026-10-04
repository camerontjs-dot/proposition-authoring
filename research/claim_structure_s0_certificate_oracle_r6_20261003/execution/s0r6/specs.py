"""Decisive and calibration certificate specs.

Roots are copied from the inspected public sources. Normalization is recorded
on the source location. Synthetic roots are calibration only.
"""

from __future__ import annotations

SCIL = "https://aclanthology.org/2021.scil-1.23.pdf"
SCIL_SHA = "sha256:e6bf489cc259ccbb75ed85fd30b5a33fc11282176806ec9a12b0e683d685063b"
W12 = "https://aclanthology.org/W12-4626.pdf"
W12_SHA = "sha256:64cf16fca478f2e26dd8858dd0e28b6f2ad44de756a51e9486a6409c0cd73f65"
TACL = "https://aclanthology.org/2024.tacl-1.41.pdf"
TACL_SHA = "sha256:54cc530bd2677602fffff47ad0f6d0cbe73b9737bc73bfe2f11cb6dbf56cdd37"
J06 = "https://aclanthology.org/J06-3002.pdf"
J06_SHA = "sha256:50207f1c326fd4040977bc486ac1094084afcd49a34ca476302d9abc5ac6f5b5"
SIG = "https://aclanthology.org/2022.sigtyp-1.6.pdf"
SIG_SHA = "sha256:b5cf83e950a78bc92a3b8648180a615958405524c00ab20f843cff0ceac5ed08"
C08 = "https://aclanthology.org/C08-1055.pdf"
C08_SHA = "sha256:f18245a2f10858839cc699ac0da37a9d74d5c17545570113d2ca062d07abca78"
GUM = "https://github.com/UniversalDependencies/UD_English-GUM"
GUM_SHA = "sha256:cd96a285e7339f401f4803dd0f4f61109c51692e3ef6f9186a1f977544080b69"
UD_NSUBJ = "https://universaldependencies.org/en/dep/nsubj.html"
UD_NSUBJ_SHA = "sha256:c9ee2861edfb04ee8e969a9ea79a5d110987fd4e7fe0d26a660f337a771f10a9"
UD_OBJ = "https://universaldependencies.org/en/dep/obj.html"
UD_OBJ_SHA = "sha256:6f58c1bd61d96fd07c33ceaa839e6f96d591e2e9c2bcc4676bb13030fdd6e467"
UD_CONJ = "https://universaldependencies.org/en/dep/conj.html"
UD_CONJ_SHA = "sha256:31456fffd3ca8307472645f9a7865974173b5678821a275725964d49307e3d42"
UD_CCOMP = "https://universaldependencies.org/en/dep/ccomp.html"
UD_CCOMP_SHA = "sha256:682488859e78b5f043df5856daf690e7e5ebfb256c75ac00400391b84fb6e691"
UD_MARK = "https://universaldependencies.org/en/dep/mark.html"
UD_MARK_SHA = "sha256:d1e3a5b5cf27afc3f4b9bb32a08bc45ee6f53c86d9736beeb17768c9ce2b7b11"
UD_ADVCL = "https://universaldependencies.org/en/dep/advcl.html"
UD_ADVCL_SHA = "sha256:40157e20f15a93a00f14291d309e29415f7a48ce68dc024e8d2a33c77363ea92"
UD_OBL = "https://universaldependencies.org/en/dep/obl.html"
UD_OBL_SHA = "sha256:9a1b6a464458aba5a7b37f365a6d02654dbefaf055b1b934b64313123d7f9e50"

DIDNT = "didn\u2019t"
HORSE = f"Every horse {DIDNT} jump over the fence."
PETER = f"Peter {DIDNT} catch every crook."
FARMER = "Every farmer owns a donkey."
TRUCK = "Each truck is either green or red (but not both)"
TELESCOPE = "I saw the man with the telescope."
BLOCK = "Put the block on the table in the morning."
MUST = "You must upload your homework as a PDF."
COOKIE = "You may have a cookie"
AMBIG_NP = "the old men and women"
CLEAR_NP = "the old men and the old women"
CLINTON = "Clinton defeated Dole"
CAR = "The car is red ."
BILL = "Bill is big and honest"
SAYS = "He says that you like to swim"
CERTAIN = "I am certain that he did it"
COND = "If you know who did it , you should tell the teacher"
GUM_TEXT = (
    "You can keep beating yourself up for your forgetfulness, "
    "or you can put a system in place."
)

# Exact roots from the falsified R1-R5 packets. None may reappear here.
PREDECESSOR_ROOTS = {
    "The Earth orbits the Sun.",
    "Venus orbits the Sun.",
    "Mars orbits the Sun.",
    "Jupiter orbits the Sun.",
    "The valve is open or the pump is running.",
    "It is not true that the server stopped and the alarm sounded.",
    "Every guest didn't leave.",
}


def _source(kind, locator, digest, location):
    return {
        "kind": kind,
        "locator": locator,
        "source_sha256": digest,
        "location": location,
    }


def _basis(kind, locator, claim):
    return {"basis_kind": kind, "locator": locator, "claim": claim}


def _prov(source, bases):
    return {"root_source": source, "analysis_basis": bases}


def _role(role_id, role, surface, **extra):
    item = {"id": role_id, "role": role, "surface": surface}
    item.update(extra)
    return item


def _pred(predicate_id, surface, roles, **extra):
    item = {"id": predicate_id, "surface": surface, "roles": roles}
    item.update(extra)
    return item


def _prop(proposition_id, text, predicates):
    return {"id": proposition_id, "text": text, "predicates": predicates}


def _bind(binding_id, kind, surface, targets, **extra):
    item = {"id": binding_id, "kind": kind, "surface": surface, "targets": targets}
    item.update(extra)
    return item


def _reading(reading_id, operator, propositions, bindings=None, status="MATERIALLY_LIVE"):
    return {
        "id": reading_id,
        "operator": operator,
        "status": status,
        "propositions": propositions,
        "bindings": bindings or [],
    }


def _req_role(surface, role, role_surface):
    return {"predicate_surface": surface, "role": role, "surface": role_surface}


def _req_bind(kind, surface, **extra):
    item = {"kind": kind, "surface": surface}
    item.update(extra)
    return item


def decisive_specs() -> list[dict]:
    return [
        _clinton(),
        _car(),
        _bill(),
        _clear_np(),
        _gum(),
        _truck(),
        _says(),
        _certain(),
        _horse(),
        _peter(),
        _block(),
        _telescope(),
        _farmer(),
        _must(),
        _cookie(),
        _conditional(),
        _ambiguous_np(),
    ]


def calibration_specs() -> list[dict]:
    return [_cal_kim(), _cal_or(), _cal_amb(), _cal_attr(), _cal_must()]


def all_specs() -> list[dict]:
    return decisive_specs() + calibration_specs()


def _clinton():
    return {
        "packet": "decisive",
        "families": ["atomic"],
        "certificate_id": "s0r6-a01-clinton",
        "claim_id": "a01",
        "text": CLINTON,
        "classification": "ATOMIC",
        "source_provenance": _prov(
            _source("published_example", UD_NSUBJ, UD_NSUBJ_SHA, "sdparse 'Clinton defeated Dole'; saved ud/nsubj.md"),
            [
                _basis(
                    "annotation_guideline",
                    UD_NSUBJ,
                    "The nsubj page annotates only nsubj(defeated, Clinton). It does not annotate Dole.",
                ),
                _basis(
                    "annotation_guideline",
                    UD_OBJ,
                    "The obj page defines a direct object with the different example 'She gave me a raise' / obj(gave, raise). Dole is labeled object by that definition, not by an obj annotation of this sentence.",
                ),
            ],
        ),
        "predicates": [
            _pred(
                "p-defeated",
                "defeated",
                [
                    _role("r-clinton", "subject", "Clinton"),
                    _role("r-dole", "object", "Dole"),
                ],
            )
        ],
        "readings": [
            _reading("rd-atomic", "ATOMIC", [_prop("prop-1", CLINTON, ["p-defeated"])])
        ],
        "requirements": {
            "min_live_readings": 1,
            "max_live_readings": 1,
            "required_predicate_surfaces": ["defeated"],
            "required_roles": [
                _req_role("defeated", "subject", "Clinton"),
                _req_role("defeated", "object", "Dole"),
            ],
        },
    }


def _car():
    return {
        "packet": "decisive",
        "families": ["atomic"],
        "certificate_id": "s0r6-a02-car",
        "claim_id": "a02",
        "text": CAR,
        "classification": "ATOMIC",
        "source_provenance": _prov(
            _source(
                "published_example",
                UD_NSUBJ,
                UD_NSUBJ_SHA,
                "sdparse 'The car is red .', including the space before the period; saved ud/nsubj.md",
            ),
            [
                _basis(
                    "annotation_guideline",
                    UD_NSUBJ,
                    "nsubj(red, car). The page says that in a copular clause the complement is the root. 'The' is the determiner of car and 'is' is the copula; neither relation is printed on this sdparse.",
                )
            ],
        ),
        "predicates": [
            _pred(
                "p-red",
                "red",
                [
                    _role("r-the", "determiner", "The"),
                    _role("r-car", "subject", "car"),
                    _role("r-is", "copula", "is"),
                ],
            )
        ],
        "readings": [_reading("rd-atomic", "ATOMIC", [_prop("prop-1", CAR, ["p-red"])])],
        "requirements": {
            "min_live_readings": 1,
            "max_live_readings": 1,
            "required_predicate_surfaces": ["red"],
            "required_roles": [
                _req_role("red", "subject", "car"),
                _req_role("red", "copula", "is"),
                _req_role("red", "determiner", "The"),
            ],
        },
    }


def _bill():
    return {
        "packet": "decisive",
        "families": ["all_of", "conjunction"],
        "certificate_id": "s0r6-j01-bill",
        "claim_id": "j01",
        "text": BILL,
        "classification": "ALL_OF",
        "source_provenance": _prov(
            _source("published_example", UD_CONJ, UD_CONJ_SHA, "sdparse 'Bill is big and honest'; saved ud/conj.md"),
            [
                _basis(
                    "annotation_guideline",
                    UD_CONJ,
                    "conj(big, honest). The page prints no subject and no copula. Bill and is are bound to both adjectival predicates because the nsubj guideline makes a copular complement the clause root and this page coordinates the two complements.",
                )
            ],
        ),
        "predicates": [
            _pred(
                "p-big",
                "big",
                [_role("r-bill-big", "subject", "Bill"), _role("r-is-big", "copula", "is")],
            ),
            _pred(
                "p-honest",
                "honest",
                [_role("r-bill-honest", "subject", "Bill"), _role("r-is-honest", "copula", "is")],
            ),
        ],
        "readings": [
            _reading(
                "rd-and",
                "ALL_OF",
                [
                    _prop("prop-big", "Bill is big", ["p-big"]),
                    _prop("prop-honest", "Bill is honest", ["p-honest"]),
                ],
            )
        ],
        "obligations": [
            {
                "id": "ob-and",
                "kind": "CONJUNCTION",
                "surfaces": ["and"],
                "description": "The coordinator and joins the two adjectival predicates.",
                "preserve": ["rd-and"],
            }
        ],
        "requirements": {
            "min_live_readings": 1,
            "max_live_readings": 1,
            "required_predicate_surfaces": ["big", "honest"],
            "required_roles": [
                _req_role("big", "subject", "Bill"),
                _req_role("honest", "subject", "Bill"),
                _req_role("big", "copula", "is"),
                _req_role("honest", "copula", "is"),
            ],
        },
    }


def _clear_np():
    return {
        "packet": "decisive",
        "families": ["all_of", "conjunction"],
        "certificate_id": "s0r6-j02-old-repeated",
        "claim_id": "j02",
        "text": CLEAR_NP,
        "classification": "ALL_OF",
        "source_provenance": _prov(
            _source(
                "published_example",
                C08,
                C08_SHA,
                "PDF page 7 realisation item (3). The text layer breaks the NP after 'and'; the root joins that break with one space and omits the list punctuation. CC BY-NC-SA 3.0.",
            ),
            [
                _basis(
                    "published_analysis",
                    C08 + "#page-7",
                    "Chantree and Willis realise the unambiguous repeated-modifier NP as 'the old men and the old women'. They say nps (3) and (4) are structurally unambiguous, unlike nps (1) and (2).",
                )
            ],
        ),
        "predicates": [
            _pred(
                "p-men",
                "men",
                [
                    _role("r-the-men", "determiner", "the", occurrence=0),
                    _role("r-old-men", "modifier", "old", occurrence=0),
                ],
            ),
            _pred(
                "p-women",
                "women",
                [
                    _role("r-the-women", "determiner", "the", occurrence=1),
                    _role("r-old-women", "modifier", "old", occurrence=1),
                ],
            ),
        ],
        "readings": [
            _reading(
                "rd-and",
                "ALL_OF",
                [
                    _prop("prop-men", "the old men", ["p-men"]),
                    _prop("prop-women", "the old women", ["p-women"]),
                ],
            )
        ],
        "obligations": [
            {
                "id": "ob-and",
                "kind": "CONJUNCTION",
                "surfaces": ["and"],
                "description": "and coordinates two noun phrases that each contain their own old.",
                "preserve": ["rd-and"],
            }
        ],
        "requirements": {
            "min_live_readings": 1,
            "max_live_readings": 1,
            "required_predicate_surfaces": ["men", "women"],
            "required_roles": [
                _req_role("men", "modifier", "old"),
                _req_role("women", "modifier", "old"),
            ],
        },
    }


def _gum():
    return {
        "packet": "decisive",
        "families": ["disjunction", "conjunction_disjunction_contrast", "modality_condition"],
        "certificate_id": "s0r6-d01-gum-or",
        "claim_id": "d01",
        "text": GUM_TEXT,
        "classification": "NON_ALL_OF",
        "source_provenance": _prov(
            _source(
                "public_document",
                GUM,
                GUM_SHA,
                "UD_English-GUM en_gum-ud-test.conllu sent_id GUM_essay_system-51. The full file is not committed; the sentence block is in execution/sources/excerpts/gum_essay_system-51.txt.",
            ),
            [
                _basis(
                    "published_annotation",
                    GUM + "#GUM_essay_system-51",
                    "Token or is cc of put; put is conj of keep; both can tokens are aux; You is nsubj of keep; you is nsubj of put; yourself is obj of beating; system is obj of put; forgetfulness is obl of beating; place is obl of put.",
                )
            ],
        ),
        "predicates": [
            _pred("p-keep", "keep", [_role("r-you-keep", "subject", "You")]),
            _pred(
                "p-beating",
                "beating",
                [
                    _role("r-yourself", "object", "yourself"),
                    _role("r-up", "particle", "up"),
                    _role("r-forgetfulness", "oblique", "for your forgetfulness"),
                ],
            ),
            _pred(
                "p-put",
                "put",
                [
                    _role("r-you-put", "subject", "you"),
                    _role("r-system", "object", "a system"),
                    _role("r-place", "oblique", "in place"),
                ],
            ),
        ],
        "readings": [
            _reading(
                "rd-or",
                "ANY_OF",
                [
                    _prop(
                        "prop-keep",
                        "You can keep beating yourself up for your forgetfulness",
                        ["p-keep", "p-beating"],
                    ),
                    _prop("prop-put", "you can put a system in place", ["p-put"]),
                ],
                [
                    _bind(
                        "b-can-1",
                        "MODALITY",
                        "can",
                        ["prop-keep"],
                        occurrence=0,
                        description="modal auxiliary can on keep; UD labels it aux.",
                    ),
                    _bind(
                        "b-can-2",
                        "MODALITY",
                        "can",
                        ["prop-put"],
                        occurrence=1,
                        description="modal auxiliary can on put; UD labels it aux.",
                    ),
                ],
            )
        ],
        "obligations": [
            {
                "id": "ob-or",
                "kind": "DISJUNCTION",
                "surfaces": ["or"],
                "description": "or is the coordinating conjunction of the two clauses.",
                "preserve": ["rd-or"],
            }
        ],
        "requirements": {
            "min_live_readings": 1,
            "max_live_readings": 1,
            "required_predicate_surfaces": ["keep", "beating", "put"],
            "required_roles": [
                _req_role("keep", "subject", "You"),
                _req_role("beating", "object", "yourself"),
                _req_role("put", "subject", "you"),
                _req_role("put", "object", "a system"),
            ],
            "required_bindings": [
                _req_bind("MODALITY", "can", occurrence=0, target_must_contain_all=["forgetfulness"]),
                _req_bind(
                    "MODALITY",
                    "can",
                    occurrence=1,
                    target_must_contain_all=["system"],
                    target_must_not_contain=["forgetfulness"],
                ),
            ],
            "modality_descriptions": [
                {"surface": "can", "must_contain": "modal auxiliary", "must_not_contain": ["permission"]}
            ],
        },
    }


def _truck():
    return {
        "packet": "decisive",
        "families": ["disjunction", "conjunction_disjunction_contrast", "negation_scope"],
        "certificate_id": "s0r6-d02-truck",
        "claim_id": "d02",
        "text": TRUCK,
        "classification": "NON_ALL_OF",
        "source_provenance": _prov(
            _source(
                "published_example",
                TACL,
                TACL_SHA,
                "PDF page 6, Table 1, Quantifier-Misc. row. The root has no sentence-final period.",
            ),
            [
                _basis(
                    "published_analysis",
                    TACL + "#page-6",
                    "The published sentence itself says 'either ... or' and '(but not both)'. Exclusivity is the parenthetical, not an inferred quantifier scope.",
                )
            ],
        ),
        "predicates": [
            _pred(
                "p-green",
                "green",
                [
                    _role("r-truck-green", "subject", "Each truck"),
                    _role("r-is-green", "copula", "is"),
                ],
            ),
            _pred(
                "p-red",
                "red",
                [
                    _role("r-truck-red", "subject", "Each truck"),
                    _role("r-is-red", "copula", "is"),
                ],
            ),
        ],
        "readings": [
            _reading(
                "rd-xor",
                "ANY_OF",
                [
                    _prop("prop-green", "Each truck is green", ["p-green"]),
                    _prop("prop-red", "Each truck is red", ["p-red"]),
                ],
                [
                    _bind("b-but", "EXCEPTION", "but", ["prop-green", "prop-red"]),
                    _bind(
                        "b-not-both",
                        "NEGATION",
                        "not both",
                        ["prop-green", "prop-red"],
                        description="The parenthetical not both excludes the reading in which both colours hold.",
                    ),
                ],
            )
        ],
        "obligations": [
            {
                "id": "ob-either-or",
                "kind": "DISJUNCTION",
                "surfaces": ["either", "or"],
                "description": "either and or mark the disjunction of green and red.",
                "preserve": ["rd-xor"],
            }
        ],
        "requirements": {
            "min_live_readings": 1,
            "max_live_readings": 1,
            "required_predicate_surfaces": ["green", "red"],
            "required_roles": [
                _req_role("green", "subject", "Each truck"),
                _req_role("red", "subject", "Each truck"),
            ],
            "required_bindings": [
                _req_bind("NEGATION", "not both", target_must_contain_all=["green", "red"]),
                _req_bind("EXCEPTION", "but", target_must_contain_all=["green", "red"]),
            ],
        },
    }


def _says():
    return {
        "packet": "decisive",
        "families": ["attribution_scope", "atomic"],
        "certificate_id": "s0r6-t01-says",
        "claim_id": "t01",
        "text": SAYS,
        "classification": "ATOMIC",
        "source_provenance": _prov(
            _source("published_example", UD_CCOMP, UD_CCOMP_SHA, "sdparse 'He says that you like to swim'; saved ud/ccomp.md"),
            [
                _basis(
                    "annotation_guideline",
                    UD_CCOMP,
                    "ccomp(says, like) and mark(like, that). One matrix clause takes the complement clause. The certificate keeps both predicates in one proposition and binds says to that proposition.",
                ),
                _basis(
                    "annotation_guideline",
                    UD_MARK,
                    "The mark page annotates the same sentence as mark(swim, that). That disagreement is about the mark head, not about whether that belongs to the complement. This certificate does not choose the mark head.",
                ),
            ],
        ),
        "predicates": [
            _pred(
                "p-says",
                "says",
                [
                    _role("r-he", "subject", "He"),
                    _role("r-complement", "complement", "that you like to swim"),
                ],
            ),
            _pred(
                "p-like",
                "like",
                [
                    _role("r-you", "subject", "you"),
                    _role("r-swim", "complement", "to swim"),
                ],
            ),
        ],
        "readings": [
            _reading(
                "rd-report",
                "ATOMIC",
                [_prop("prop-report", SAYS, ["p-says", "p-like"])],
                [
                    _bind(
                        "b-says",
                        "ATTRIBUTION",
                        "says",
                        ["prop-report"],
                        description="says attributes the complement that you like to swim.",
                    )
                ],
            )
        ],
        "requirements": {
            "min_live_readings": 1,
            "max_live_readings": 1,
            "required_predicate_surfaces": ["says", "like"],
            "required_roles": [
                _req_role("says", "subject", "He"),
                _req_role("like", "subject", "you"),
                _req_role("like", "complement", "to swim"),
            ],
            "required_bindings": [
                _req_bind("ATTRIBUTION", "says", target_must_contain_all=["like", "swim"])
            ],
        },
    }


def _certain():
    return {
        "packet": "decisive",
        "families": ["attribution_scope", "atomic"],
        "certificate_id": "s0r6-t02-certain",
        "claim_id": "t02",
        "text": CERTAIN,
        "classification": "ATOMIC",
        "source_provenance": _prov(
            _source("published_example", UD_CCOMP, UD_CCOMP_SHA, "sdparse 'I am certain that he did it'; saved ud/ccomp.md"),
            [
                _basis(
                    "annotation_guideline",
                    UD_CCOMP,
                    "ccomp(certain, did) and mark(did, that). certain is the attitude predicate. am is the copula and is not printed on this sdparse. it is the remaining nominal of did and is labeled object from the obj guideline, whose example is a different sentence.",
                )
            ],
        ),
        "predicates": [
            _pred(
                "p-certain",
                "certain",
                [
                    _role("r-i", "experiencer", "I"),
                    _role("r-am", "copula", "am"),
                    _role("r-complement", "complement", "that he did it"),
                ],
            ),
            _pred(
                "p-did",
                "did",
                [_role("r-he", "subject", "he"), _role("r-it", "object", "it")],
            ),
        ],
        "readings": [
            _reading(
                "rd-report",
                "ATOMIC",
                [_prop("prop-report", CERTAIN, ["p-certain", "p-did"])],
                [
                    _bind(
                        "b-certain",
                        "ATTRIBUTION",
                        "certain",
                        ["prop-report"],
                        description="certain attributes the complement that he did it.",
                    )
                ],
            )
        ],
        "requirements": {
            "min_live_readings": 1,
            "max_live_readings": 1,
            "required_predicate_surfaces": ["certain", "did"],
            "required_roles": [
                _req_role("certain", "experiencer", "I"),
                _req_role("did", "subject", "he"),
                _req_role("did", "object", "it"),
            ],
            "required_bindings": [
                _req_bind("ATTRIBUTION", "certain", target_must_contain_all=["did", "he"])
            ],
        },
    }


def _horse():
    return {
        "packet": "decisive",
        "families": ["negation_scope", "ambiguous"],
        "certificate_id": "s0r6-n01-horse",
        "claim_id": "n01",
        "text": HORSE,
        "classification": "AMBIGUOUS",
        "source_provenance": _prov(
            _source(
                "published_example",
                SCIL,
                SCIL_SHA,
                "PDF page 1, example (1). The apostrophe in didn't is U+2019.",
            ),
            [
                _basis(
                    "published_analysis",
                    SCIL + "#page-1",
                    "The paper gives two readings: (1a) none, 'None of the horses jumped over the fence', and (1b) not-all, 'Not all horses jumped over the fence'.",
                )
            ],
        ),
        "predicates": [
            _pred(
                "p-jump",
                "jump",
                [
                    _role("r-horse", "subject", "Every horse"),
                    _role("r-path", "path", "over the fence"),
                ],
            )
        ],
        "readings": [
            _reading(
                "rd-none",
                "ATOMIC",
                [_prop("prop-none", HORSE, ["p-jump"])],
                [
                    _bind(
                        "b-every-none",
                        "QUANTIFIER",
                        "Every",
                        ["prop-none"],
                        description="None reading: the universal outscopes negation.",
                    ),
                    _bind(
                        "b-neg-none",
                        "NEGATION",
                        DIDNT,
                        ["prop-none"],
                        description="None reading: negation is inside the universal. Published paraphrase: None of the horses jumped over the fence.",
                    ),
                ],
            ),
            _reading(
                "rd-notall",
                "OTHER",
                [
                    _prop("prop-q", "Every horse", ["p-jump"]),
                    _prop("prop-e", "jump over the fence", ["p-jump"]),
                ],
                [
                    _bind(
                        "b-every-notall",
                        "QUANTIFIER",
                        "Every",
                        ["prop-q"],
                        description="Not-all reading: the universal is the restriction under negation.",
                    ),
                    _bind(
                        "b-neg-notall",
                        "NEGATION",
                        DIDNT,
                        ["prop-q", "prop-e"],
                        description="Not-all reading: negation outscopes the universal. Published paraphrase: Not all horses jumped over the fence.",
                    ),
                ],
            ),
        ],
        "requirements": {
            "min_live_readings": 2,
            "required_predicate_surfaces": ["jump"],
            "required_roles": [
                _req_role("jump", "subject", "Every horse"),
                _req_role("jump", "path", "over the fence"),
            ],
            "required_bindings": [
                _req_bind(
                    "QUANTIFIER",
                    "Every",
                    reading_id="rd-none",
                    target_must_contain_all=[DIDNT, "jump"],
                ),
                _req_bind(
                    "NEGATION",
                    DIDNT,
                    reading_id="rd-none",
                    target_must_contain_all=[DIDNT, "jump"],
                ),
                _req_bind(
                    "NEGATION",
                    DIDNT,
                    reading_id="rd-notall",
                    target_must_contain_all=["horse", "jump"],
                    target_must_not_contain=[DIDNT],
                ),
                _req_bind(
                    "QUANTIFIER",
                    "Every",
                    reading_id="rd-notall",
                    target_must_contain_all=["horse"],
                    target_must_not_contain=["jump"],
                ),
            ],
        },
    }


def _peter():
    return {
        "packet": "decisive",
        "families": ["negation_scope", "atomic"],
        "certificate_id": "s0r6-n02-peter",
        "claim_id": "n02",
        "text": PETER,
        "classification": "ATOMIC",
        "source_provenance": _prov(
            _source(
                "published_example",
                W12,
                W12_SHA,
                "PDF page 1, example (1a). The apostrophe in didn't is U+2019.",
            ),
            [
                _basis(
                    "published_analysis",
                    W12 + "#page-1",
                    "The paper marks Peter didn't catch every crook as (*∀>¬, ¬>∀). Only negation outscoping the object universal is available. The wide-scope universal is recorded as rejected.",
                )
            ],
        ),
        "predicates": [
            _pred(
                "p-catch",
                "catch",
                [
                    _role("r-peter", "subject", "Peter"),
                    _role("r-crook", "object", "every crook"),
                ],
            )
        ],
        "readings": [
            _reading(
                "rd-live",
                "ATOMIC",
                [_prop("prop-live", PETER, ["p-catch"])],
                [
                    _bind(
                        "b-neg",
                        "NEGATION",
                        DIDNT,
                        ["prop-live"],
                        description="Live reading: negation outscopes every. The paper's available scope is ¬>∀.",
                    ),
                    _bind(
                        "b-every",
                        "QUANTIFIER",
                        "every",
                        ["prop-live"],
                        description="every is the object quantifier under negation.",
                    ),
                ],
            ),
            _reading(
                "rd-rejected",
                "OTHER",
                [
                    _prop("prop-q", "every crook", ["p-catch"]),
                    _prop("prop-e", f"Peter {DIDNT} catch", ["p-catch"]),
                ],
                [
                    _bind(
                        "b-every-rejected",
                        "QUANTIFIER",
                        "every",
                        ["prop-e"],
                        description="Rejected reading: the universal would outscope negation. The paper stars that scope.",
                    )
                ],
                status="REJECTED_BY_EXTERNAL_BASIS",
            ),
        ],
        "requirements": {
            "min_live_readings": 1,
            "max_live_readings": 1,
            "required_predicate_surfaces": ["catch"],
            "required_roles": [
                _req_role("catch", "subject", "Peter"),
                _req_role("catch", "object", "every crook"),
            ],
            "required_bindings": [
                _req_bind("NEGATION", DIDNT, target_must_contain_all=["Peter", "every"]),
                _req_bind("QUANTIFIER", "every", reading_id="rd-live", target_must_contain_all=["Peter", "every"]),
            ],
        },
    }


def _block():
    return {
        "packet": "decisive",
        "families": ["temporal_location_scope"],
        "certificate_id": "s0r6-l01-block",
        "claim_id": "l01",
        "text": BLOCK,
        "classification": "ATOMIC",
        "source_provenance": _prov(
            _source("published_example", J06, J06_SHA, "PDF page 2, example (2)."),
            [
                _basis(
                    "published_analysis",
                    J06 + "#page-2",
                    "Merlo and Ferrer say both PPs modify put. on the table is a locative argument required by put. in the morning is an optional time adjunct. The imperative has no overt subject.",
                )
            ],
        ),
        "predicates": [
            _pred(
                "p-put",
                "Put",
                [
                    _role("r-block", "object", "the block"),
                    _role("r-table", "location", "on the table"),
                    _role("r-morning", "temporal", "in the morning"),
                ],
            )
        ],
        "readings": [
            _reading(
                "rd-put",
                "ATOMIC",
                [_prop("prop-put", BLOCK, ["p-put"])],
                [
                    _bind(
                        "b-table",
                        "LOCATION",
                        "on the table",
                        ["prop-put"],
                        description="Locative argument of put.",
                    ),
                    _bind(
                        "b-morning",
                        "TEMPORAL",
                        "in the morning",
                        ["prop-put"],
                        description="Time adjunct of put.",
                    ),
                ],
            )
        ],
        "requirements": {
            "min_live_readings": 1,
            "max_live_readings": 1,
            "required_predicate_surfaces": ["Put"],
            "required_roles": [_req_role("Put", "object", "the block")],
            "required_bindings": [
                _req_bind("LOCATION", "on the table", target_must_contain_all=["Put", "block"]),
                _req_bind("TEMPORAL", "in the morning", target_must_contain_all=["Put"]),
            ],
        },
    }


def _telescope():
    return {
        "packet": "decisive",
        "families": ["temporal_location_scope", "ambiguous"],
        "certificate_id": "s0r6-l02-telescope",
        "claim_id": "l02",
        "text": TELESCOPE,
        "classification": "AMBIGUOUS",
        "source_provenance": _prov(
            _source("published_example", J06, J06_SHA, "PDF page 1, example (1)."),
            [
                _basis(
                    "published_analysis",
                    J06 + "#page-1",
                    "Merlo and Ferrer: with the telescope may attach to the verb as the instrument of saw, or to the noun the man. The certificate uses OTHER because the schema has no instrument kind and the paper does not call this PP a location.",
                )
            ],
        ),
        "predicates": [
            _pred(
                "p-saw",
                "saw",
                [_role("r-i", "subject", "I"), _role("r-man", "object", "the man")],
            ),
            _pred("p-man", "man", [_role("r-the", "determiner", "the")]),
        ],
        "readings": [
            _reading(
                "rd-instrument",
                "ATOMIC",
                [_prop("prop-saw", TELESCOPE, ["p-saw"])],
                [
                    _bind(
                        "b-inst",
                        "OTHER",
                        "with the telescope",
                        ["prop-saw"],
                        description="Instrument reading: the PP attaches to saw.",
                    )
                ],
            ),
            _reading(
                "rd-nominal",
                "OTHER",
                [
                    _prop("prop-see", "I saw the man", ["p-saw"]),
                    _prop("prop-mod", "the man with the telescope", ["p-man"]),
                ],
                [
                    _bind(
                        "b-nom",
                        "OTHER",
                        "with the telescope",
                        ["prop-mod"],
                        description="Nominal reading: the PP attaches to the man.",
                    )
                ],
            ),
        ],
        "requirements": {
            "min_live_readings": 2,
            "required_predicate_surfaces": ["saw", "man"],
            "required_roles": [
                _req_role("saw", "subject", "I"),
                _req_role("saw", "object", "the man"),
            ],
            "required_bindings": [
                _req_bind(
                    "OTHER",
                    "with the telescope",
                    reading_id="rd-instrument",
                    target_must_contain_all=["saw", "telescope"],
                ),
                _req_bind(
                    "OTHER",
                    "with the telescope",
                    reading_id="rd-nominal",
                    target_must_contain_all=["man", "telescope"],
                    target_must_not_contain=["saw"],
                ),
            ],
        },
    }


def _farmer():
    return {
        "packet": "decisive",
        "families": ["ambiguous"],
        "certificate_id": "s0r6-q01-donkey",
        "claim_id": "q01",
        "text": FARMER,
        "classification": "AMBIGUOUS",
        "source_provenance": _prov(
            _source("published_example", TACL, TACL_SHA, "PDF page 1, example (1a)."),
            [
                _basis(
                    "published_analysis",
                    TACL + "#page-1",
                    "Surface scope: every farmer outscopes a donkey. Inverse scope: a donkey outscopes every farmer. The paper prints both logical forms.",
                )
            ],
        ),
        "predicates": [
            _pred(
                "p-owns",
                "owns",
                [
                    _role("r-farmer", "subject", "Every farmer"),
                    _role("r-donkey-obj", "object", "a donkey"),
                ],
            ),
            _pred("p-donkey", "donkey", [_role("r-a", "determiner", "a")]),
        ],
        "readings": [
            _reading(
                "rd-surface",
                "ATOMIC",
                [_prop("prop-surface", FARMER, ["p-owns"])],
                [
                    _bind(
                        "b-every-surface",
                        "QUANTIFIER",
                        "Every",
                        ["prop-surface"],
                        description="Surface scope: the universal outscopes the existential.",
                    ),
                    _bind(
                        "b-a-surface",
                        "QUANTIFIER",
                        "a",
                        ["prop-surface"],
                        description="Surface scope: a donkey is inside the scope of every farmer.",
                    ),
                ],
            ),
            _reading(
                "rd-inverse",
                "OTHER",
                [
                    _prop("prop-donkey", "a donkey", ["p-donkey"]),
                    _prop("prop-owns", "Every farmer owns", ["p-owns"]),
                ],
                [
                    _bind(
                        "b-a-inverse",
                        "QUANTIFIER",
                        "a",
                        ["prop-donkey"],
                        description="Inverse scope: one donkey is outside the universal.",
                    ),
                    _bind(
                        "b-every-inverse",
                        "QUANTIFIER",
                        "Every",
                        ["prop-owns"],
                        description="Inverse scope: every farmer is inside the existential.",
                    ),
                ],
            ),
        ],
        "requirements": {
            "min_live_readings": 2,
            "required_predicate_surfaces": ["owns", "donkey"],
            "required_roles": [
                _req_role("owns", "subject", "Every farmer"),
                _req_role("owns", "object", "a donkey"),
            ],
            "required_bindings": [
                _req_bind(
                    "QUANTIFIER",
                    "Every",
                    reading_id="rd-surface",
                    target_must_contain_all=["farmer", "donkey"],
                ),
                _req_bind(
                    "QUANTIFIER",
                    "a",
                    reading_id="rd-surface",
                    target_must_contain_all=["farmer", "donkey"],
                ),
                _req_bind(
                    "QUANTIFIER",
                    "a",
                    reading_id="rd-inverse",
                    target_must_contain_all=["donkey"],
                    target_must_not_contain=["farmer"],
                ),
                _req_bind(
                    "QUANTIFIER",
                    "Every",
                    reading_id="rd-inverse",
                    target_must_contain_all=["farmer"],
                    target_must_not_contain=["donkey"],
                ),
            ],
        },
    }


def _must():
    return {
        "packet": "decisive",
        "families": ["modality_condition", "atomic"],
        "certificate_id": "s0r6-m01-must",
        "claim_id": "m01",
        "text": MUST,
        "classification": "ATOMIC",
        "source_provenance": _prov(
            _source(
                "published_example",
                SIG,
                SIG_SHA,
                "PDF page 2, Table 1, example (2). The text layer breaks the cell after 'your'; the root joins that break with one space and keeps the period.",
            ),
            [
                _basis(
                    "published_analysis",
                    SIG + "#page-2",
                    "Table 1 labels the example strong deontic. The prose says example (2) has universal force with deontic flavor: the rule-worlds are ones in which you upload a PDF. This certificate records that force as strong deontic necessity and does not call it permission.",
                )
            ],
        ),
        "predicates": [
            _pred(
                "p-upload",
                "upload",
                [
                    _role("r-you", "subject", "You"),
                    _role("r-homework", "object", "your homework"),
                    _role("r-pdf", "form", "as a PDF"),
                ],
            )
        ],
        "readings": [
            _reading(
                "rd-must",
                "ATOMIC",
                [_prop("prop-must", MUST, ["p-upload"])],
                [
                    _bind(
                        "b-must",
                        "MODALITY",
                        "must",
                        ["prop-must"],
                        description="strong deontic necessity; universal force with deontic flavor.",
                    )
                ],
            )
        ],
        "requirements": {
            "min_live_readings": 1,
            "max_live_readings": 1,
            "required_predicate_surfaces": ["upload"],
            "required_roles": [
                _req_role("upload", "subject", "You"),
                _req_role("upload", "object", "your homework"),
                _req_role("upload", "form", "as a PDF"),
            ],
            "required_bindings": [_req_bind("MODALITY", "must", target_must_contain_all=["upload"])],
            "modality_descriptions": [
                {
                    "surface": "must",
                    "must_contain": "strong deontic necessity",
                    "must_not_contain": ["permission"],
                }
            ],
        },
    }


def _cookie():
    return {
        "packet": "decisive",
        "families": ["modality_condition", "atomic"],
        "certificate_id": "s0r6-m02-cookie",
        "claim_id": "m02",
        "text": COOKIE,
        "classification": "ATOMIC",
        "source_provenance": _prov(
            _source(
                "published_example",
                SIG,
                SIG_SHA,
                "PDF page 2, Table 1, example (4). The cell has no sentence-final period.",
            ),
            [
                _basis(
                    "published_analysis",
                    SIG + "#page-2",
                    "Table 1 labels the example weak deontic. The prose says may has weak possibility force, and example (4) is deontic. This certificate records that force as weak deontic permission.",
                )
            ],
        ),
        "predicates": [
            _pred(
                "p-have",
                "have",
                [_role("r-you", "subject", "You"), _role("r-cookie", "object", "a cookie")],
            )
        ],
        "readings": [
            _reading(
                "rd-may",
                "ATOMIC",
                [_prop("prop-may", COOKIE, ["p-have"])],
                [
                    _bind(
                        "b-may",
                        "MODALITY",
                        "may",
                        ["prop-may"],
                        description="weak deontic permission; possibility force with deontic flavor.",
                    )
                ],
            )
        ],
        "requirements": {
            "min_live_readings": 1,
            "max_live_readings": 1,
            "required_predicate_surfaces": ["have"],
            "required_roles": [
                _req_role("have", "subject", "You"),
                _req_role("have", "object", "a cookie"),
            ],
            "required_bindings": [_req_bind("MODALITY", "may", target_must_contain_all=["cookie"])],
            "modality_descriptions": [
                {
                    "surface": "may",
                    "must_contain": "weak deontic permission",
                    "must_not_contain": ["necessity"],
                }
            ],
        },
    }


def _conditional():
    return {
        "packet": "decisive",
        "families": ["modality_condition", "condition"],
        "certificate_id": "s0r6-m03-if",
        "claim_id": "m03",
        "text": COND,
        "classification": "NON_ALL_OF",
        "source_provenance": _prov(
            _source(
                "published_example",
                UD_ADVCL,
                UD_ADVCL_SHA,
                "sdparse includes the space before the comma and has no final period; saved ud/advcl.md",
            ),
            [
                _basis(
                    "annotation_guideline",
                    UD_ADVCL,
                    "advcl(tell, know). If introduces the adverbial clause headed by know. should is the modal auxiliary of the main clause and is not printed on this sdparse. The page does not assign it a force label.",
                )
            ],
        ),
        "predicates": [
            _pred(
                "p-know",
                "know",
                [
                    _role("r-you-know", "subject", "you", occurrence=0),
                    _role("r-who", "complement", "who did it"),
                ],
            ),
            _pred(
                "p-tell",
                "tell",
                [
                    _role("r-you-tell", "subject", "you", occurrence=1),
                    _role("r-teacher", "object", "the teacher"),
                ],
            ),
        ],
        "readings": [
            _reading(
                "rd-if",
                "IF_THEN",
                [
                    _prop("prop-if", "you know who did it", ["p-know"]),
                    _prop("prop-then", "you should tell the teacher", ["p-tell"]),
                ],
                [
                    _bind(
                        "b-if",
                        "CONDITION",
                        "If",
                        ["prop-if"],
                        description="If marks the antecedent headed by know.",
                    ),
                    _bind(
                        "b-should",
                        "MODALITY",
                        "should",
                        ["prop-then"],
                        description="modal auxiliary should in the consequent.",
                    ),
                ],
            )
        ],
        "requirements": {
            "min_live_readings": 1,
            "max_live_readings": 1,
            "required_predicate_surfaces": ["know", "tell"],
            "required_roles": [
                _req_role("know", "subject", "you"),
                _req_role("know", "complement", "who did it"),
                _req_role("tell", "subject", "you"),
                _req_role("tell", "object", "the teacher"),
            ],
            "required_bindings": [
                _req_bind(
                    "CONDITION",
                    "If",
                    target_must_contain_all=["know"],
                    target_must_not_contain=["tell"],
                ),
                _req_bind(
                    "MODALITY",
                    "should",
                    target_must_contain_all=["tell"],
                    target_must_not_contain=["know"],
                ),
            ],
            "modality_descriptions": [
                {"surface": "should", "must_contain": "modal auxiliary", "must_not_contain": ["permission"]}
            ],
        },
    }


def _ambiguous_np():
    return {
        "packet": "decisive",
        "families": ["ambiguous", "coordination_modifier_scope"],
        "certificate_id": "s0r6-am01-old-scope",
        "claim_id": "am01",
        "text": AMBIG_NP,
        "classification": "AMBIGUOUS",
        "source_provenance": _prov(
            _source(
                "published_example",
                C08,
                C08_SHA,
                "PDF page 7 realisation item (1). The text layer has a space before the list comma; the root is the NP without that comma. CC BY-NC-SA 3.0.",
            ),
            [
                _basis(
                    "published_analysis",
                    C08 + "#page-7",
                    "Chantree and Willis say nps (1) and (2) are structurally ambiguous. Wide scope applies old to both nouns. Narrow scope applies old only to the first noun. Their Word Sketch heuristic prefers the wide reading; it does not delete the narrow structure.",
                )
            ],
        ),
        "predicates": [
            _pred(
                "p-men",
                "men",
                [
                    _role("r-the", "determiner", "the"),
                    _role("r-old", "modifier", "old"),
                ],
            ),
            _pred("p-women", "women", [_role("r-women-head", "head", "women")]),
        ],
        "readings": [
            _reading(
                "rd-wide",
                "ALL_OF",
                [
                    _prop("prop-men", "the old men", ["p-men"]),
                    _prop("prop-women-wide", "the old women", ["p-women"]),
                ],
                [
                    _bind(
                        "b-old-wide",
                        "OTHER",
                        "old",
                        ["prop-men", "prop-women-wide"],
                        description="Wide reading: old applies to men and to women.",
                    )
                ],
            ),
            _reading(
                "rd-narrow",
                "ALL_OF",
                [
                    _prop("prop-men-narrow", "the old men", ["p-men"]),
                    _prop("prop-women-narrow", "the women", ["p-women"]),
                ],
                [
                    _bind(
                        "b-old-narrow",
                        "OTHER",
                        "old",
                        ["prop-men-narrow"],
                        description="Narrow reading: old applies only to men.",
                    )
                ],
            ),
        ],
        "obligations": [
            {
                "id": "ob-and",
                "kind": "CONJUNCTION",
                "surfaces": ["and"],
                "description": "and coordinates men and women.",
                "preserve": ["rd-wide", "rd-narrow"],
            }
        ],
        "requirements": {
            "min_live_readings": 2,
            "required_predicate_surfaces": ["men", "women"],
            "required_roles": [_req_role("men", "modifier", "old")],
            "required_bindings": [
                _req_bind(
                    "OTHER",
                    "old",
                    reading_id="rd-wide",
                    target_must_contain_all=["men", "women"],
                ),
                _req_bind(
                    "OTHER",
                    "old",
                    reading_id="rd-narrow",
                    target_must_contain_all=["men"],
                    target_must_not_contain=["women"],
                ),
            ],
        },
    }


def _synthetic(locator, claim):
    return _prov(
        {
            "kind": "synthetic_control",
            "locator": locator,
            "location": "Labeled calibration control. Not a decisive root.",
        },
        [_basis("synthetic_gold_rule", locator, claim)],
    )


def _cal_kim():
    return {
        "packet": "calibration",
        "families": ["calibration"],
        "certificate_id": "s0r6-cal-kim",
        "claim_id": "cal-kim",
        "text": "Kim bought a book on Friday.",
        "classification": "ATOMIC",
        "source_provenance": _synthetic(
            "calibration:kim",
            "Gold rule: Kim is the subject, a book is the object, and on Friday is a temporal modifier of bought.",
        ),
        "predicates": [
            _pred(
                "p-bought",
                "bought",
                [
                    _role("r-kim", "subject", "Kim"),
                    _role("r-book", "object", "a book"),
                ],
            )
        ],
        "readings": [
            _reading(
                "rd-kim",
                "ATOMIC",
                [_prop("prop-kim", "Kim bought a book on Friday.", ["p-bought"])],
                [
                    _bind(
                        "b-friday",
                        "TEMPORAL",
                        "on Friday",
                        ["prop-kim"],
                        description="on Friday modifies bought.",
                    )
                ],
            )
        ],
        "requirements": {
            "min_live_readings": 1,
            "max_live_readings": 1,
            "required_predicate_surfaces": ["bought"],
            "required_roles": [
                _req_role("bought", "subject", "Kim"),
                _req_role("bought", "object", "a book"),
            ],
            "required_bindings": [_req_bind("TEMPORAL", "on Friday", target_must_contain_all=["Friday"])],
        },
    }


def _cal_or():
    return {
        "packet": "calibration",
        "families": ["calibration"],
        "certificate_id": "s0r6-cal-or",
        "claim_id": "cal-or",
        "text": "Kim bought a book or Lee sold a pen.",
        "classification": "NON_ALL_OF",
        "source_provenance": _synthetic(
            "calibration:or",
            "Gold rule: or is a disjunction. It must not be represented as and.",
        ),
        "predicates": [
            _pred(
                "p-bought",
                "bought",
                [_role("r-kim", "subject", "Kim"), _role("r-book", "object", "a book")],
            ),
            _pred(
                "p-sold",
                "sold",
                [_role("r-lee", "subject", "Lee"), _role("r-pen", "object", "a pen")],
            ),
        ],
        "readings": [
            _reading(
                "rd-or",
                "ANY_OF",
                [
                    _prop("prop-kim", "Kim bought a book", ["p-bought"]),
                    _prop("prop-lee", "Lee sold a pen", ["p-sold"]),
                ],
            )
        ],
        "obligations": [
            {
                "id": "ob-or",
                "kind": "DISJUNCTION",
                "surfaces": ["or"],
                "description": "or coordinates the two clauses.",
                "preserve": ["rd-or"],
            }
        ],
        "requirements": {
            "min_live_readings": 1,
            "max_live_readings": 1,
            "required_predicate_surfaces": ["bought", "sold"],
            "required_roles": [
                _req_role("bought", "subject", "Kim"),
                _req_role("bought", "object", "a book"),
                _req_role("sold", "subject", "Lee"),
                _req_role("sold", "object", "a pen"),
            ],
        },
    }


def _cal_amb():
    guest = "Every guest didn't leave."
    return {
        "packet": "calibration",
        "families": ["calibration"],
        "certificate_id": "s0r6-cal-amb",
        "claim_id": "cal-amb",
        "text": guest,
        "classification": "AMBIGUOUS",
        "source_provenance": _synthetic(
            "calibration:every-not",
            "Gold rule: this synthetic sentence follows the published every/not pattern and has two live readings, none and not-all. It is not a decisive root. The apostrophe is ASCII.",
        ),
        "predicates": [
            _pred("p-leave", "leave", [_role("r-guest", "subject", "Every guest")])
        ],
        "readings": [
            _reading(
                "rd-none",
                "ATOMIC",
                [_prop("prop-none", guest, ["p-leave"])],
                [
                    _bind("b-every-none", "QUANTIFIER", "Every", ["prop-none"]),
                    _bind(
                        "b-neg-none",
                        "NEGATION",
                        "didn't",
                        ["prop-none"],
                        description="None reading: every guest failed to leave.",
                    ),
                ],
            ),
            _reading(
                "rd-notall",
                "OTHER",
                [
                    _prop("prop-q", "Every guest", ["p-leave"]),
                    _prop("prop-e", "leave", ["p-leave"]),
                ],
                [
                    _bind("b-every-notall", "QUANTIFIER", "Every", ["prop-q"]),
                    _bind(
                        "b-neg-notall",
                        "NEGATION",
                        "didn't",
                        ["prop-q", "prop-e"],
                        description="Not-all reading: negation outscopes every.",
                    ),
                ],
            ),
        ],
        "requirements": {
            "min_live_readings": 2,
            "required_predicate_surfaces": ["leave"],
            "required_roles": [_req_role("leave", "subject", "Every guest")],
            "required_bindings": [
                _req_bind(
                    "QUANTIFIER",
                    "Every",
                    reading_id="rd-none",
                    target_must_contain_all=["didn't", "guest"],
                ),
                _req_bind("NEGATION", "didn't", reading_id="rd-none", target_must_contain_all=["didn't"]),
                _req_bind(
                    "NEGATION",
                    "didn't",
                    reading_id="rd-notall",
                    target_must_contain_all=["guest", "leave"],
                    target_must_not_contain=["didn't"],
                ),
                _req_bind(
                    "QUANTIFIER",
                    "Every",
                    reading_id="rd-notall",
                    target_must_contain_all=["guest"],
                    target_must_not_contain=["leave"],
                ),
            ],
        },
    }


def _cal_attr():
    text = "Ann said that Bob left and Chris stayed."
    return {
        "packet": "calibration",
        "families": ["calibration"],
        "certificate_id": "s0r6-cal-attr",
        "claim_id": "cal-attr",
        "text": text,
        "classification": "NON_ALL_OF",
        "source_provenance": _synthetic(
            "calibration:attribution",
            "Gold rule: said attributes both Bob left and Chris stayed. An attachment that reaches only Chris stayed is incomplete.",
        ),
        "predicates": [
            _pred(
                "p-said",
                "said",
                [
                    _role("r-ann", "subject", "Ann"),
                    _role("r-complement", "complement", "that Bob left and Chris stayed"),
                ],
            ),
            _pred("p-left", "left", [_role("r-bob", "subject", "Bob")]),
            _pred("p-stayed", "stayed", [_role("r-chris", "subject", "Chris")]),
        ],
        "readings": [
            _reading(
                "rd-said",
                "OTHER",
                [
                    _prop("prop-comp", "that Bob left and Chris stayed", ["p-said", "p-left", "p-stayed"]),
                    _prop("prop-bob", "Bob left", ["p-left"]),
                    _prop("prop-chris", "Chris stayed", ["p-stayed"]),
                ],
                [
                    _bind(
                        "b-said",
                        "ATTRIBUTION",
                        "said",
                        ["prop-comp"],
                        description="said scopes over both complement conjuncts.",
                    )
                ],
            )
        ],
        "obligations": [
            {
                "id": "ob-and",
                "kind": "CONJUNCTION",
                "surfaces": ["and"],
                "description": "and coordinates the two reported clauses.",
                "preserve": ["rd-said"],
            }
        ],
        "requirements": {
            "min_live_readings": 1,
            "max_live_readings": 1,
            "required_predicate_surfaces": ["said", "left", "stayed"],
            "required_roles": [
                _req_role("said", "subject", "Ann"),
                _req_role("left", "subject", "Bob"),
                _req_role("stayed", "subject", "Chris"),
            ],
            "required_bindings": [
                _req_bind("ATTRIBUTION", "said", target_must_contain_all=["Bob", "Chris"])
            ],
        },
    }


def _cal_must():
    text = "Kim must file the form."
    return {
        "packet": "calibration",
        "families": ["calibration"],
        "certificate_id": "s0r6-cal-must",
        "claim_id": "cal-must",
        "text": text,
        "classification": "ATOMIC",
        "source_provenance": _synthetic(
            "calibration:must",
            "Gold rule: must is strong deontic necessity. Representing it as permission is a modality change.",
        ),
        "predicates": [
            _pred(
                "p-file",
                "file",
                [_role("r-kim", "subject", "Kim"), _role("r-form", "object", "the form")],
            )
        ],
        "readings": [
            _reading(
                "rd-must",
                "ATOMIC",
                [_prop("prop-must", text, ["p-file"])],
                [
                    _bind(
                        "b-must",
                        "MODALITY",
                        "must",
                        ["prop-must"],
                        description="strong deontic necessity.",
                    )
                ],
            )
        ],
        "requirements": {
            "min_live_readings": 1,
            "max_live_readings": 1,
            "required_predicate_surfaces": ["file"],
            "required_roles": [_req_role("file", "subject", "Kim"), _req_role("file", "object", "the form")],
            "required_bindings": [_req_bind("MODALITY", "must", target_must_contain_all=["file"])],
            "modality_descriptions": [
                {
                    "surface": "must",
                    "must_contain": "strong deontic necessity",
                    "must_not_contain": ["permission"],
                }
            ],
        },
    }
