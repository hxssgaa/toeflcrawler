from httplib import OK

import requests
import re

BASE_URL = 'http://www.toeflvocabulary.com/'
YOUDAO_URL = 'http://youdao.com/w/eng/%s/#keyfrom=dict2.index'
REGEX_VOCABULARY_CONTENT = re.compile('<div class="post-body entry-content">([\S\s]*?)</div>')
REGEX_HTML_TAG = {
    'h2': re.compile('<h2>([\S\s]*?)</h2>'),
    'p': re.compile('<p>([\S\s]*?)</p>'),
    'li': re.compile('<li>([\S\s]*?)</li>'),
}

REGEX_YOUDAO_MEANING = re.compile('<div class="trans-container">[\S\s]*?</div>')


class Word(object):
    def __init__(self, name=None, meaning=None, synonyms=None, eg_sentence=None):
        self.name = name
        self.meaning = meaning
        self.synonyms = synonyms
        self.eg_sentence = eg_sentence


def _restore_formated_html(html):
    return html.replace('&#8211;', '-').replace('&#8217;', '\'') \
        .replace('&#8220;', '"').replace('&#8221;', '"').replace('&#8216;', '')


def _get_youdao_meaning(name):
    html = requests.get(YOUDAO_URL % name)
    if OK != html.status_code:
        raise RuntimeError("craw youdao meaning failed, please try again.", html.status_code)
    content = html.content
    meaning_res = REGEX_YOUDAO_MEANING.search(content)
    if not meaning_res:
        return ''
    meaning = meaning_res.group()
    cn_meanings = REGEX_HTML_TAG['li'].findall(meaning)
    return ';'.join(cn_meanings)


def _get_vocabulary_from_content(content):
    if not content:
        return []
    vocabulary_content = REGEX_VOCABULARY_CONTENT.search(content).group(1)

    result = []
    word = None
    for l in vocabulary_content.split('\n'):
        l = l.strip()
        if l.startswith('<h2>') and l.endswith('</h2>'):
            name = REGEX_HTML_TAG['h2'].search(l).group(1)
            cn_meaning = _get_youdao_meaning(name)
            word = Word(name=name, meaning={
                'cn': cn_meaning
            })
            result.append(word)
        elif word is None:
            continue
        elif l.startswith('<p>') and l.endswith('</p>'):
            content = REGEX_HTML_TAG['p'].search(l).group(1).strip()
            content = _restore_formated_html(content)
            if content.startswith('Synonym'):
                word.synonyms = content
            elif 'en' not in word.meaning:
                word.meaning['en'] = content
            elif not content.startswith('Antonym:'):
                word.meaning['en'] = word.meaning['en'] + ' ; ' + content
    return result


def get_vocabulary(url):
    html = requests.get(url)
    if OK != html.status_code:
        raise RuntimeError("craw toefl words failed with HTTP status code(%d), please try again.", html.status_code)
    return _get_vocabulary_from_content(html.content)


def write_vocabulary(vocabulary_map):
    with open('vocabulary.txt', 'w') as f:
        for ch in xrange(ord('a'), ord('z') + 1):
            f.write('-----------%s-----------\n' % chr(ch))
            words = vocabulary_map[chr(ch)]
            for word in words:
                f.write('name:%s\n' % word.name)
                f.write('en:%s\n' % word.meaning.get('en', ''))
                f.write('cn:%s\n' % word.meaning.get('cn', ''))
                f.write('%s\n' % word.synonyms)
                f.write('\n')


def main():
    vocabulary_map = {}
    for ch in xrange(ord('a'), ord('z') + 1):
        print 'processing word starting with \'%s\' complete' % (chr(ch))
        vocabulary_map[chr(ch)] = get_vocabulary(BASE_URL + chr(ch))
    write_vocabulary(vocabulary_map)

    # for ch in xrange(ord('a'), ord('a') + 1):
    #     words = vocabulary_map[chr(ch)]
    #     for word in words:
    #         print 'name=%s,meaning=%s,synonyms=%s' % (word.name, word.meaning, word.synonyms)


if __name__ == '__main__':
    main()
