#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

dictionary = [
    {
        'term': 'nukare',
        'type': 'verb', 
        'valency': 2,
    }, 
    {
        'term': 'arpa',
        'type': 'verb',
        'valency': 1,
        'plural': 'paye',
    },
    {
        'term': 'paye',
        'link': 'arpa',
    },
    {
        'term': 'cikap',
        'type': 'noun',
        'posession': 'kor',
    },
    {
        'term': 'arka',
        'type': 'verb',
        'valency': 1
    },
    {
        'term': 'askepet',
        'type': 'noun',
        'posession': 'prefix',
    },
    {
        'term': 'teke',
        'type': 'noun',
        'posession': 'prefix',
    }
]

def normalize_spacing(string):
    # replace all whitespace, including unicode spaces, with ASCII spaces
    return re.sub(r'\s', ' ', string.strip())

def find_punctuation(string):
    punctuation = []
    new_string = ''
    for (i, c) in enumerate(string):
        if c in ',.?!、。？！':
            punctuation.append((i, c))
        else:
            new_string += c
    return punctuation, new_string

def restore_punctuation(string, punctuation):
    string = list(string)
    for (i, c) in punctuation:
        print(i, c)
        string.insert(i, c)
    return ''.join(string)

def kana_to_roma(string):
    kana_table = {
        'イェ': 'ye', 'ウェ': 'we', 'チャ': 'ca', 'チェ': 'ce', 'チョ': 'co', 'ㇷ゚': 'p',
        'ア':  'a', 'イ':  'i', 'ウ':  'u', 'エ':  'e', 'オ':  'o', 'ィ': 'y',
        'カ': 'ka', 'キ': 'ki', 'ク': 'ku', 'ケ': 'ke', 'コ': 'ko', 'ㇰ': 'k',
        'サ': 'sa', 'シ': 'si', 'ス': 'su', 'セ': 'se', 'ソ': 'so', 'ㇱ': 's',
        'タ': 'ta', 'チ': 'ci', 'ツ': 'tu', 'テ': 'te', 'ト': 'to', 'ッ': 't',
        'ナ': 'na', 'ニ': 'ni', 'ヌ': 'nu', 'ネ': 'ne', 'ノ': 'no', r'[ㇴン]': 'n',
        'ハ': 'ha', 'ヒ': 'hi', 'フ': 'hu', 'ヘ': 'he', 'ホ': 'ho',
        'パ': 'pa', 'ピ': 'pi', 'プ': 'pu', 'ペ': 'pe', 'ポ': 'po',
        r'[ㇵㇶㇷㇸㇹ]': 'h',
        'マ': 'ma', 'ミ': 'mi', 'ム': 'mu', 'メ': 'me', 'モ': 'mo',
        'ヤ': 'ya', 'ユ': 'yu', 'ヨ': 'yo',
        'ラ': 'ra', 'リ': 'ri', 'ル': 'ru', 'レ': 're', 'ロ': 'ro',
        r'[ㇻㇼㇽㇾㇿ]': 'r',
        'ワ': 'wa', 'ヱ': 'we', 'ヲ': 'wo',
    }

    for kana, roma in kana_table.items():
        string = re.sub(kana, roma, string)

    # replace all whitespace, including unicode spaces, with ASCII spaces
    string = re.sub(r'\s', ' ', string.strip())

    return string

def search_dictionary(term):
    results = []
    for e in dictionary:
        if e['term'] == term:
            if 'link' in e:
                results += search_dictionary(e['link'])
            else:
                results.append(e)
    return results

def is_verb(word):
    results = search_dictionary(word)
    for term in results:
        if term['type'] == 'verb':
            return True
    return False

def lookup_phrase(phrase):
    results = []
    for word in phrase.split(' '):
        if not '=' in word:
            # user has not provided '=' so we need to generate candidates
            for candidate in generate_candidates(word):
                results += search_dictionary(candidate)
            continue
        results += search_dictionary(word)        
    return results
    
def split_cvc(word):
    # splits word into a list of (C)V(C) pairs
    pairs = []
    vowels = ['a', 'i', 'u', 'e', 'o']
    consonants = ['k', 's', 't', 'h', 'p', 'm', 'y', 'c', 'n', 'r', 'w']
    _illegals = ['ti', 'yi', 'wi', 'wu']
    # TODO: implement checks for illegals i.e. change ti to t=i, a=yi to ay=i 
    # NOTE: 'p' can be free-standing

    # detect syllable boundaries
    cur = []
    for (i, c) in enumerate(word):
        cur += c
        if len(cur) == 3:
            # possible: vvv, vvc, vcv, vcc, cvv, cvc
            # not possible: ccv, ccc            
            # [1]   : vvv, vvc, vcv
            # [1..2]: vcc, cvv, cvc(v)
            # [1..3]: cvc(c)
            pattern = [ l in vowels for l in cur ]
            if pattern in [
                [True, True, True],  # VVV
                [True, True, False], # VVC
                [True, False, True], # VCV
            ]:
                pairs.append(cur.pop(0))
            elif pattern in [
                [True, False, False], # VCC
                [False, True, True],  # CVV
            ] or (
                pattern == [False, True, False] # CVC(V)
                and (i+1 < len(word))
                and word[i+1] in vowels
            ):
                pairs.append(cur.pop(0) + cur.pop(0))
            elif (
                pattern == [False, True, False] # CVC(C)
                and (i+1 >= len(word) or word[i+1] in consonants)
            ):
                pairs.append(''.join(cur))
                cur = []
    if cur:
        pairs.append(''.join(cur))

    return pairs


def generate_candidates(term):
    # this function enumerate all possible prefixes/suffixes
    # in order to obtain every possible stem a term could have
    # NOTE: avoid calling for terms that already have '=' in them
    term = re.sub('=', '', term)
    # candidates = [term]

    # verb_prefixes = [
    #     # in order of longer prefixes to shorter prefixes
    #     'ecien', 'eciun', 
    #     'aeci', 'ecii', 
    #     'een', 'aen', 'eun', 'aun', 'eci',
    #     'ae', 'ki', 'ei', 'ai', 'ku', 'en', 'ci', 'un', 
    #     'k', 'e', 'c', 'a', 'i',
    #     # NOTE: 1人称 複数 主格 ci= が4人称を目的語にするとき c=a= になるの？
    # ]

    return list(set(generate_noun_deflections(term) + generate_verb_deflections(term)))

def generate_verb_deflections(term):
    candidates = []
    prefix_pattern = r'^(eci|ku?|ci?|e|a)?(en|un|i)?(?![ksthpmycnrw][ksthpmycnrw])'
    suffix_pattern = r'.*(as|an)$'

    prefixes = re.match(prefix_pattern, term) or ''
    suffix = re.match(suffix_pattern, term) or ''
    if prefixes:
        prefixes = [prefixes.group(1) or '', prefixes.group(2) or '']
    if suffix:
        suffix = suffix.group(2)
    
    stem = term
    if prefixes:
        stem = stem[len(''.join(prefixes)):]
    if suffix:
        stem = stem[:-len(suffix)]

    split = '='.join(filter(None, prefixes + [stem, suffix]))
    print(f'[verb] | {term} : {split}')
    candidates.append(stem)
    return candidates[::-1]

def generate_noun_deflections(term):
    candidates = []

    # Try to find noun prefixes/suffixes to remove
    prefix_pattern = r'^(eci|ku?|ci?|e|a)(?![ksthpmycnrw][ksthpmycnrw])'
    suffix_pattern = r'.*([aiueo])(h\1)$'
    # if suffix is hi, the previous vowel might also need to be changed
    # e.g. nipi = nip, askepeci = askepet

    prefix = re.match(prefix_pattern, term) or ''
    suffix = re.match(suffix_pattern, term) or ''
    if prefix:
        prefix = prefix.group(1)
    if suffix:
        suffix = suffix.group(2)
    
    stem = term
    if prefix:
        stem = stem[len(prefix):]
    if suffix:
        stem = stem[:-len(suffix)]

    split = '='.join(filter(None, [prefix, stem, suffix]))
    print(f'[noun] | {term} : {split}')

    # add this stem
    candidates.append(stem)
    if suffix == 'hi':
        # maybe the stem is in genitive case
        stem2 = stem[:-1]
        if stem2[-1] == 'c':
            stem2 = stem2[:-1] + 't'
        candidates.append(stem2)
    
    return candidates[::-1]

if __name__ == '__main__':
    phrase = 'カㇱケペチヒ アㇻカ'
    # phrase = 'エテケヘ エエンヌカレ'

    phrase = normalize_spacing(phrase)
    print(f'Original phrase: {phrase}')

    roma = kana_to_roma(phrase)
    print(f'Romanized phrase: {roma}')

    results = lookup_phrase(roma)
    print(results)
