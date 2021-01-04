#!/usr/bin/env python
from math import ceil, log2
from typing import List, Set, Tuple
import re
import sys

if len(sys.argv) < 2:
    print('Potrebno je zadati putanju do datoteke sa mikrokodom kao prvi argument komandne linije.')
    exit(1)

step_regex = re.compile(r'^\s*step\s*([0-9A-Fa-f]+)\s*=>\s*(.*)$')
case_regex = re.compile(r'^br\s*\(\s*case\s*\(')
if_regex = re.compile(r'^br\s*\(if\s*([^\s]+) then\s*step\s*([0-9A-Fa-f]+)\s*\)$')
uncond_regex = re.compile(r'^br\s*step\s*([0-9A-Fa-f]+)$')
signals = {}
cc = [None, 'uncnd']

lines: List[Tuple[Set[str], int, int]] = []

def split_before_bracket(line: str) -> List[str]:
    spl: List[str] = []
    while len(line) > 0:
        bracket_index = len(line) + 7
        if '(' in line:
            bracket_index = line.index('(')
        if ',' in line:
            index = line.index(',')
            if index > bracket_index:
                spl.append(line)
                break
            spl.append(line[:index])
            line = line[index+1:]
        else:
            spl.append(line)
            break
    return spl

with open(sys.argv[1], 'r', encoding='utf-8') as mic_file:
    for line in mic_file:
        stripped_line = line.strip()
        if len(stripped_line) == 0 or stripped_line.startswith('!'):
            # Komentar ili prazna linija
            continue
        line_cc = 0
        line_ba = 0
        line_signals: Set[str] = set()
        step_match = step_regex.match(stripped_line)
        if step_match is None:
            print('Nedostaje broj koraka na liniji:', stripped_line)
            exit(1)
        step_number = int(step_match.group(1), 16)
        if step_number != len(lines):
            print('Koraci ne idu po redosledu na liniji:', stripped_line)
            exit(1)
        split_line = split_before_bracket(step_match.group(2))
        for i in range(0, len(split_line)-1):
            stripped_signal = split_line[i].strip()
            signals[stripped_signal] = True
            line_signals.add(stripped_signal)
        br = split_line[-1].strip()
        case_match = case_regex.match(br)
        if_match = if_regex.match(br)
        uncond_match = uncond_regex.match(br)
        if case_match is not None:
            # br (case(signal1, signal2, ...)) then (signal1, stepXX), (signal2, stepYY), ...
            if 'mul' in cc:
                line_cc = cc.index('mul')
            else:
                cc.append('mul')
                line_cc = len(cc)-1
        elif if_match is not None:
            # br (if cc then)
            signal = if_match.group(1)
            line_ba = int(if_match.group(2), 16)
            if signal in cc:
                line_cc = cc.index(signal)
            else:
                cc.append(signal)
                line_cc = len(cc)-1
        elif uncond_match is not None:
            # br stepXX
            line_cc = 1
            line_ba = int(uncond_match.group(1), 16)
        else:
            # Ovo je bio samo običan signal na kraju linije
            signals[br] = True
            line_signals.add(br)
        lines.append((line_signals, line_cc, line_ba))

cc_width = ceil(log2(len(cc)))
ba_width = ceil(log2(len(lines)))

def format_binary(num: int, width: int):
    fmt = '{:0' + str(width) + 'b}'
    return fmt.format(num)

print('================== Instrukcija ======================')
print('Širina instrukcije:', cc_width + ba_width + len(signals))
print('Signali:')
for signal in signals.keys():
    print(f'- {signal}')
print('CC:')
for index, code in enumerate(cc):
    if index > 0:
        print(f'- {index}: br{code}')
print('=================== Mikrokod ========================')
for curr_signals, cc, ba in lines:
    line_bin = ''
    line_bin += format_binary(ba, ba_width)
    line_bin += format_binary(cc, cc_width)
    for signal in reversed(signals.keys()):
        if signal in curr_signals:
            line_bin += '1'
        else:
            line_bin += '0'
    # print(line_bin)
    print(hex(int(line_bin, 2)).split('x')[1].upper())
    # print(curr_signals, cc, ba)
