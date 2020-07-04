#!/usr/bin/python
# -*- coding: utf-8 -*-

from Automata import Otomat
import json

def parse_input_file(filepath):
    '''
        Read and parse an Automata from json file
        Args: 
            filepath: path to file that will be parsed
        Returns:
            Otomat
    '''
    with open(filepath, 'r') as f:
        data = json.load(f)
        f.close()
    fields = ["sigma", "S", "S0", "F", "delta"]
    for field in fields:
        if field not in data.keys():
            print(f"Missing \"{field}\". Please check input file.")
            exit(0)
    otomat = {key:data[key] for key in fields}
    return Otomat(**otomat)

def main():
    filepath = input('Input file path: ')
    otomat = parse_input_file(filepath)
    print("Initial Automata")
    otomat.printOtomat()

    # DFA
    # otomat.DFA()
    # print("Otomat sau khi đơn định hóa")
    # otomat.printOtomat()

    # Minimization
    otomat.minimize()
    print("Minimized Automata")
    otomat.printOtomat()

if __name__ == '__main__':
    main()
