#!/usr/bin/env python
from deepdive import *
import random
from collections import namedtuple

WorkLabel = namedtuple('WorkLabel', 'p1_id, p2_id, label, type')

@tsv_extractor
@returns(lambda
        p1_id   = "text",
        p2_id   = "text",
        label   = "int",
        rule_id = "text",
    :[])
# heuristic rules for finding positive/negative examples of coworker relationship mentions
def supervise(
        p1_id="text", p1_begin="int", p1_end="int",
        p2_id="text", p2_begin="int", p2_end="int",
        doc_id="text", sentence_index="int", sentence_text="text",
        tokens="text[]", lemmas="text[]", pos_tags="text[]", ner_tags="text[]",
        dep_types="text[]", dep_token_indexes="int[]",
    ):

    # Constants
    # MARRIED = frozenset(["wife", "husband"])
    # FAMILY = frozenset(["mother", "father", "sister", "brother", "brother-in-law"])

    SUPER = frozenset(["boss", "supervisor", "manager"])
    CO = frozenset(["colleague","coworker"])
    SUB = frozenset(["subordinate", "staff"])


    MAX_DIST = 15

    # Common data objects
    p1_end_idx = min(p1_end, p2_end)
    p2_start_idx = max(p1_begin, p2_begin)
    p2_end_idx = max(p1_end,p2_end)
    intermediate_lemmas = lemmas[p1_end_idx+1:p2_start_idx]
    intermediate_ner_tags = ner_tags[p1_end_idx+1:p2_start_idx]
    tail_lemmas = lemmas[p2_end_idx+1:]
    tail_ner_tags = ner_tags[p2_end_idx+1:]
    employment = WorkLabel(p1_id=p1_id, p2_id=p2_id, label=None, type=None)

    ''' CUSTOM RULES '''
    if len(SUPER.intersection(intermediate_lemmas)) > 0 or len(SUB.intersection(intermediate_lemmas)) > 0:
        yield employment._replace(label=1, type='pos:boss_and_subordinate')

    if len(CO.intersection(intermediate_lemmas)) > 0 :
        yield employment._replace(label=1, type='pos:colleagues')    

    if ("and" in intermediate_lemmas) and ("work" in tail_lemmas):
        yield employment._replace(label=1, type='pos:work_together')

    if len(intermediate_lemmas) > MAX_DIST:
        yield employment._replace(label=-1, type='neg:far_apart')

    if 'ORGANIZATION' in intermediate_ner_tags and 'ORGANIZATION' in tail_lemmas: 
        yield employment._replace(label=-1, type='neg:from_different_orgs')


    # ''' FROM SPOUSE EXAMPLE '''
    # # Rule: Candidates that are too far apart
    # if len(intermediate_lemmas) > MAX_DIST:
    #     yield spouse._replace(label=-1, type='neg:far_apart')

    # # Rule: Candidates that have a third person in between
    # if 'PERSON' in intermediate_ner_tags:
    #    # if 'ORGANIZATION' in intermediate_ner_tags:
    #     yield spouse._replace(label=-1, type='neg:third_person_between')

    # # Rule: Sentences that contain wife/husband in between
    # #         (<P1>)([ A-Za-z]+)(wife|husband)([ A-Za-z]+)(<P2>)
    # if len(MARRIED.intersection(intermediate_lemmas)) > 0:
    #     yield spouse._replace(label=1, type='pos:wife_husband_between')

    # # Rule: Sentences that contain and ... married
    # #         (<P1>)(and)?(<P2>)([ A-Za-z]+)(married)
    # if ("and" in intermediate_lemmas) and ("married" in tail_lemmas):
    #     yield spouse._replace(label=1, type='pos:married_after')

    # # Rule: Sentences that contain familial relations:
    # #         (<P1>)([ A-Za-z]+)(brother|stster|father|mother)([ A-Za-z]+)(<P2>)
    # if len(FAMILY.intersection(intermediate_lemmas)) > 0:
    #     yield spouse._replace(label=-1, type='neg:familial_between')
