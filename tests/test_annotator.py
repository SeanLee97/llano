# -*- coding: utf-8 -*-

import pytest


@pytest.mark.parametrize("test_input,labels,expected", [
    ('(a, A), (a,A), ("a", B), ("a  , B), (a",  ,  "B),(a",  ,  \'B),(a"\',,,, ,  \'B), (a"\',,,, ,  \'B"    ),(a,B/C)',
     ['A', 'B', 'B/C'], 
     [('a', 'A'), ('a', 'A'), ('"a"', 'B'), ('"a  ', 'B'), ('a",  ', 'B'),
      ('a",  ', 'B'), ('a"\',,,, ', 'B'), ('a"\',,,, ', 'B'), ('a', 'B/C')]
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

@pytest.mark.parametrize("test_input,labels,expected", [
    (
        '''[(Mr. Li, live in, Shanghai),("Mr. Li", live in, "Shanghai"),(  Mr. Li, work at, HelloWorld  )], others...(Note: The above output is in Chinese language as the given sentence is in Chinese.)''',
        ['live in', 'work at'], 
        [("Mr. Li", "live in", "Shanghai"), ("Mr. Li", "live in", "Shanghai"), ("Mr. Li", "work at", "HelloWorld")]
    ), (
        "[('李华', '居住在', '上海'), ('李华', '工作在', 'HelloWorld公司')]",
        ['居住在', '工作在'],
        [('李华', '居住在', '上海'), ('李华', '工作在', 'HelloWorld公司')]
    ), (
        "[('Mr. Li', 'work at', 'HelloWorld Tech'), ('he', 'live in', 'Shanghai')]",
        ['live in', 'work at'],
        [('Mr. Li', 'work at', 'HelloWorld Tech'), ('he', 'live in', 'Shanghai')]
    )
])
def test_relation_extraction_regex(test_input, labels, expected):
    from lanno import GPTAnnotator

    regex = GPTAnnotator.make_relation_extraction_regex(labels)
    triples = []
    for match in regex.finditer(test_input):
        subject = GPTAnnotator.re_strip(match.group('subject'))
        predicate = GPTAnnotator.re_strip(match.group('predicate'))
        object = GPTAnnotator.re_strip(match.group('object'))
        triples.append((subject, predicate, object))
    assert triples == expected