# Finite State Automata Minimize and Simple Flex Bison Compiler
## Finite Automata Minimize
* Automata is stored in Automata/test.txt
* To minimize finite state automata in test.txt, simply run:
```bash
cd Automata
python Automata.py
```
## Simple Flex Bison Compiler
```
<identifier> = <natural integer>
<identifier> <operator (+-*/)> <natural integer>
<natural integer> (This output is the result of the above expression)
```
* To compile and run this program
```bash
cd "Flex Bison"
bash build.sh
test
```
