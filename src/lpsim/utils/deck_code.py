"""
Convert between deck codes and deck strings.
"""
import base64
from typing import List
import random
import json


# load name map and forbid list
deck_code_data = json.load(open(__file__.replace('deck_code.py', 
                                                 'deck_code_data.json')))
name_map = deck_code_data['name_map'][:]
forbid_list = deck_code_data['forbid_list'][:]
charactors_idx = []
for i in range(len(name_map)):
    if name_map[i].startswith('charactor:'):
        charactors_idx.append(i)
        name_map[i] = name_map[i][10:]


# create forbid word trie
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def match(self, word):
        """
        test if word start with any word in trie
        """
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
            if node.is_end_of_word:
                return True
        return False

    def search(self, word):
        """
        test if word contains any word in trie
        """
        for i in range(len(word)):
            if self.match(word[i:]):
                return True
        return False


forbidden_trie = Trie()
for forbid in forbid_list:
    forbidden_trie.insert(forbid)


def deck_code_to_deck_str(deck_code: str, version: str | None = None) -> str:
    """
    Convert the base64 deck code to deck str. If version is set, add
    default_version.
    """
    binary = base64.b64decode(deck_code)
    bb = []
    for b in binary:
        bb.append((256 + b - binary[-1]) % 256)
    bb = bb[:-1]
    binary = bb[::2] + bb[1::2]
    res = ''
    for i in binary:
        res += '{:08b} '.format(i)
    # print(res)
    res = res.replace(' ', '')
    decode = []
    for i in range(0, len(res), 12):
        # print(res[i:i + 12], end = ' ')
        decode.append(int(res[i:i + 12], 2))
    decode = decode[:-1]
    results = []
    if version is not None:
        results.append(f'default_version:{version}')
    for x in decode:
        if x > 0 and x <= len(name_map):
            if x - 1 in charactors_idx:
                results.append(f'charactor:{name_map[x - 1]}')
            else:
                results.append(name_map[x - 1])
    return '\n'.join(results)


def _deck_str_to_deck_code_one(name_list: List[str], checksum: int) -> str:
    """
    Convert deck str to deck code. Versions about deck_str will be ignored.
    """
    binary = ''
    for i in name_list:
        if i not in name_map:
            # not found, use 0
            binary += '{:012b} '.format(0)
        else:
            idx = name_map.index(i)
            binary += '{:012b} '.format(idx + 1)
    binary = binary.replace(' ', '')
    b8 = []
    for i in range(0, len(binary), 8):
        b8.append(int(binary[i:i + 8], 2))
    b8[-1] = b8[-1] * 16  # 4 zeros
    uint = list(zip(b8[:25], b8[25:]))
    uint = [list(x) for x in uint]
    uint = sum(uint, start = [])
    uint.append(0)
    uint = [(x + checksum) % 256 for x in uint]
    res = base64.b64encode(bytes(uint)).decode()
    return res


def deck_str_to_deck_code(deck_str: str, max_retry_time: int = 10000) -> str:
    """
    convert deck str to deck code. Versions about deck_str will be ignored.
    As generated deck code may illegal, retry for max_retry_time times.
    If retry_time exceeded, raise ValueError.
    """
    deck_str_list = deck_str.strip().split('\n')
    deck_str_list = [x.strip() for x in deck_str_list]
    # remove empty line and comment
    deck_str_list = [x for x in deck_str_list if x != '' and x[0] != '#']
    # remove default version
    deck_str_list = [x for x in deck_str_list 
                     if not x.startswith('default_version:')]
    # remove version mark
    deck_str_list = [x.split('@')[0] for x in deck_str_list]
    charactor_str_l = [x[10:] for x in deck_str_list 
                       if x.startswith('charactor:')]
    card_str_l = [x for x in deck_str_list if not x.startswith('charactor:')]
    charactor_str: List[str] = []
    card_str: List[str] = []
    for i in charactor_str_l:
        number = 1
        if '*' in i:
            i, number_str = i.split('*')
            number = int(number_str)
        charactor_str += [i] * number
    for i in card_str_l:
        number = 1
        if '*' in i:
            i, number_str = i.split('*')
            number = int(number_str)
        card_str += [i] * number
    if len(charactor_str) > 3 or len(card_str) > 30:
        raise ValueError('too many charactors or cards')
    for _ in range(max_retry_time):
        # generate random checksum and shuffle cards
        checksum = random.randint(0, 255)
        random.shuffle(card_str)
        # fill empty with ''
        name_list = (
            charactor_str + [''] * (3 - len(charactor_str))
            + card_str + [''] * (30 - len(card_str))
        )
        deck_code = _deck_str_to_deck_code_one(name_list, checksum)
        if not forbidden_trie.search(deck_code):
            return deck_code
    raise ValueError('in generating deck code: retry time exceeded')


__all__ = ['deck_code_to_deck_str', 'deck_str_to_deck_code', 'deck_code_data']


if __name__ == '__main__':
    # descs = json.load(open(__file__.replace('deck_code.py', 
    #                                         'default_desc.json'),
    #                        encoding = 'utf8'))
    # map_eng = [''] * len(map_chinese)
    # for key, value in descs.items():
    #     if 'names' not in value:
    #         continue
    #     name_c = value['names']['zh-CN']
    #     if name_c in map_chinese:
    #         idx = map_chinese.index(name_c)
    #         map_eng[idx] = value['names']["en-US"]
    # print(map_eng)

    # import json
    # res = json.dumps({
    #     'name_map': name_map,
    #     'forbid_list': forbid_list,
    # }, indent = 2)
    # open('deck_code_data.json', 'w', encoding = 'utf8').write(res)

    ...
