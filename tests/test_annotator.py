# -*- coding: utf-8 -*-

import pytest


@pytest.mark.parametrize("test_input,labels,expected", [
    ('(a, A), (a,A), ("a", B), ("a  , B), (a",  ,  "B),(a",  ,  \'B),(a"\',,,, ,  \'B), (a"\',,,, ,  \'B"    )',
     ['A', 'B'], 
     [('a', 'A'), ('a', 'A'), ('"a"', 'B'), ('"a  ', 'B'), ('a",  ', 'B'),
      ('a",  ', 'B'), ('a"\',,,, ', 'B'), ('a"\',,,, ', 'B')]
    )
])
def test_ner_regex(test_input, labels, expected):
    from lanno import GPTAnnotator

    regex = GPTAnnotator.make_ner_extraction_regex(labels)
    pairs = []
    for match in regex.finditer(test_input):
        entity, entity_type = match.group('entity'), match.group('entity_type')
        pairs.append((entity, entity_type))
    assert pairs == expected
