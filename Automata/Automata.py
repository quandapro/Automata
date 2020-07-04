#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np

def remove_duplicates(arr_list):
    return sorted(list(set(arr_list)))

class Otomat:
    def __init__(self, sigma, S, S0, F, delta):
        assert len(sigma) > 0, 'Sigma must not be empty'
        assert len(S) > 0, 'S must not be empty'
        assert S0 in S, f'Initial state {S0} is not in S'
        for state in F:
            assert state in S, f'Final state {state} is not in S'
        self.sigma = remove_duplicates(sigma)
        self.S = remove_duplicates(S)
        self.S0 = S0 
        self.F = remove_duplicates(F)
        self.delta = delta 
        self.extraState = 'ES'

    def remove_epsilon(self):
        '''
            Remove epsilon edges
        '''
        for state in self.S:
            if '$' in self.delta[state].keys():
                target_states = self.delta[state]['$']
                for t_state in target_states:
                    for symbol in self.sigma:
                        self.delta[state][symbol] += self.delta[t_state][symbol]
                    if t_state in self.F:
                        if state not in self.F:
                            self.F.append(state)
                for symbol in self.sigma:
                    self.delta[state][symbol] = remove_duplicates(self.delta[state][symbol])

                # S0 -> $S2, S1 -> aS0. -> S1 -> aS2
                for other_state in self.S:
                    for symbol in self.delta[other_state].keys():
                        if state in self.delta[other_state][symbol]:
                            self.delta[other_state][symbol] += self.delta[state]['$']

                del self.delta[state]['$']                

    def fill(self):
        '''
            Fill Automata
        '''
        for state in self.S:
            if state not in self.delta.keys():
                self.delta[state] = {}
            for symbol in self.sigma:
                if symbol not in self.delta[state].keys():
                    self.delta[state][symbol] = [self.extraState]
                    if self.extraState not in self.S:
                        self.S.append(self.extraState)
                elif len(self.delta[state][symbol]) == 0:
                    self.delta[state][symbol] = [self.extraState]
                    if self.extraState not in self.S:
                        self.S.append(self.extraState)

    def DFA(self):
        '''
            To deterministic finite automation
        '''
        # First we must fill automata
        self.fill()

        # Remove epsilon edges
        self.remove_epsilon()
        
        # Process start here
        queue = [self.S0]
        visited = []
        while len(queue) > 0:
            current_state = queue.pop(0)
            # If already visited current state, do nothing
            if current_state in visited:
                continue 
            visited.append(current_state)

            for symbol in self.sigma:
                targets = self.delta[current_state][symbol]
                for i in range(len(targets)):
                    if '_' in targets[i]:
                        current = targets.pop(i)
                        targets += current.split('_')
                targets = remove_duplicates(targets)
                # If delta(current_state, symbol) is not deterministic
                if len(targets) > 1:
                    # ['S1', 'S2'] -> 'S1_S2'
                    new_state = '_'.join(targets)
                    # If already visited this new_state
                    if new_state in visited:
                        # Replace current delta(current_state, symbol) with new_state
                        self.delta[current_state][symbol] = [new_state]
                        continue
                    
                    # Create new transition table for new_state
                    self.delta[new_state] = {}

                    # Fill transition table for new_state
                    for character in self.sigma:
                        new_targets_for_new_state = []
                        for state in targets:
                            for target in self.delta[state][character]:
                                if target not in new_targets_for_new_state:
                                    new_targets_for_new_state.append(target)
                        new_targets_for_new_state = remove_duplicates(new_targets_for_new_state)
                        self.delta[new_state][character] = new_targets_for_new_state
                    
                    # Replace current delta(current_state, symbol) with new_state
                    self.delta[current_state][symbol] = [new_state]

                    # Append new state to queue
                    queue.append(new_state)

                # Do nothing if current_state is already deterministic
                elif len(targets) == 1:
                    queue.append(targets[0])

        # Remove excess states
        for state in self.S:
            if state not in visited:
                del self.delta[state]

        self.S = sorted(visited)

        # Append new final states
        for state in self.S:
            for f in self.F:
                if f in state:
                    if state not in self.F:
                        self.F.append(state)

        # Remove final states which is not in new set of states
        for f in self.F:
            if f not in self.S:
                self.F.remove(f)

    def fill_table(self):
        '''
            Table filling, mark pairs of states satisfy: 
            table(A, B) = 1 if A nor B is not in F, or exists a symbol such that table(delta(A, symbol), delta(B, symbol)) = 1
            Returns:
                table: Filled table
        '''
        num_of_states = len(self.S)
        table = np.zeros((num_of_states, num_of_states), dtype=np.bool)
        while True:
            '''
                Loop until can't mark any pair of state
            '''
            stop = True
            for i in range(num_of_states):
                state_A = self.S[i]
                for j in range(num_of_states):
                    state_B = self.S[j]
                    if table[i, j]:
                        continue
                    if state_A in self.F and state_B not in self.F:
                        stop = False
                        table[i, j] = 1
                    else:
                        for symbol in self.sigma:
                            next_state_A = self.delta[state_A][symbol][0]
                            next_state_B = self.delta[state_B][symbol][0]
                            if table[self.S.index(next_state_A), self.S.index(next_state_B)] \
                              or table[self.S.index(next_state_B), self.S.index(next_state_A)]:
                                stop = False
                                table[i, j] = 1
                                break
            if stop:
                break  

        return table

    def combine_unmarked_pairs(self, table):
        '''
            Combine unmarked pairs into groups
            Args:
                table: Marking table
            Returns:
                unmarked_states_group: Unmarked states group
        '''
        unmarked_states_group = []
        num_of_states = len(self.S)
        for i in range(num_of_states):
            for j in range(num_of_states):
                if i == j:
                    continue
                if not table[i, j]:
                    if [self.S[i], self.S[j]] not in unmarked_states_group \
                        and [self.S[j], self.S[i]] not in unmarked_states_group:
                        # [C, D], [D, E] -> [C, D, E]
                        flag = False
                        for k in range(len(unmarked_states_group)):
                            if self.S[i] in unmarked_states_group[k] or self.S[j] in unmarked_states_group[k]:
                                flag = True
                                unmarked_states_group[k] += [self.S[i], self.S[j]]
                                unmarked_states_group[k] = remove_duplicates(unmarked_states_group[k])
                                break
                        if not flag:
                            unmarked_states_group.append([self.S[i], self.S[j]])
        return unmarked_states_group

    def minimize(self):
        '''
            Automata minimization using table filling method
            https://www.youtube.com/watch?v=UiXkJUTkp44
        '''
        self.DFA()
        table = self.fill_table()
        unmarked_states_group = self.combine_unmarked_pairs(table)

        # Build new automata
        for group in unmarked_states_group:
            # Create new state and replace old state (Ex: C_D_E to replace C, D, E) 
            new_state = '_'.join(group)
            self.S.append(new_state)
            self.delta[new_state] = {}
            for state in group:
                self.S.remove(state)
                for symbol in self.sigma:
                    if symbol not in self.delta[new_state]:
                        self.delta[new_state][symbol] = []
                    self.delta[new_state][symbol] += self.delta[state][symbol]
                del self.delta[state]

        # Replace old state in transition table delta
        for state in self.S:
            for symbol in self.sigma:
                for idx, trans_state in enumerate(self.delta[state][symbol]):
                    if trans_state not in self.S:
                        for new_state in self.S:
                            if trans_state in new_state:
                                self.delta[state][symbol][idx] = new_state
                self.delta[state][symbol] = remove_duplicates(self.delta[state][symbol])


        # Replace old final state (Ex: C_D_E to replace C, D, E) 
        for idx, final_state in enumerate(self.F):
            if final_state not in self.S:
                for state in self.S:
                    if final_state in state:
                        self.F[idx] = state
        self.F = remove_duplicates(self.F)

    def printOtomat(self):
        print('States: ', self.S)
        print('Final states: ', self.F)
        print('Transitions table:')
        print('{:>10}'.format('delta'), end='')
        for symbol in self.sigma:
            print('{:>10}'.format(symbol), end='')
        print()

        for state in self.S:
            print('{:>10}'.format(state), end='')
            for symbol in self.sigma:
                if symbol not in self.delta[state]:
                    print('{:>10}'.format('-'), end='')
                else:
                    print('{:>10}'.format(','.join(self.delta[state][symbol])), end='')
            print()
        print('\n-------------------------------------------\n')

                

    
