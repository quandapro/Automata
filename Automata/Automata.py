#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np

def remove_duplicates(arr_list):
    return sorted(list(set(arr_list)))

class Otomat:
    def __init__(self, sigma, S, S0, F, delta):
        # Check if input automata is valid
        assert len(sigma) > 0, 'Sigma must not be empty'
        assert len(S) > 0, 'S must not be empty'
        assert S0 in S, f'Initial state {S0} is not in S'
        for state in F:
            assert state in S, f'Final state {state} is not in S'
        for state in delta.keys():
            assert state in S, f'Unknown state in transition table: {state}'
            for symbol in delta[state].keys():
                assert symbol in sigma, f'Unknown symbol in transition table: {symbol}, in state {state}'
                assert len(delta[state][symbol]) < 2, f'Automata is not deterministic (delta[{state}][{symbol}] has len of {len(delta[state][symbol])})'
                for next_state in delta[state][symbol]:
                    assert next_state in S, f'Unknown state in transition table: {next_state}, in delta[{state}][{symbol}]'

        self.sigma = remove_duplicates(sigma)
        self.S = remove_duplicates(S)
        self.S0 = S0 
        self.F = remove_duplicates(F)
        self.delta = delta 
        self.extraState = 'ES'        

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
                            if len(self.delta[state_A][symbol]) * len(self.delta[state_B][symbol]) == 0:
                                continue
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

    def can_reach_final(self, state, visited=[]):
        '''
            Check if a state can reach final state
        '''
        flag = False
        for symbol in self.delta[state].keys():
            if len(self.delta[state][symbol]) == 1:
                next_state = self.delta[state][symbol][0]
                if next_state in visited:
                    continue
                if next_state in self.F:
                    return True
                visited.append(next_state)
                flag = flag or self.can_reach_final(next_state, visited)
        return flag

    def minimize(self):
        '''
            Automata minimization using table filling method
            https://www.youtube.com/watch?v=UiXkJUTkp44
        '''
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

        # Remove state that cannot reach final state
        for state in self.S:
            if not self.can_reach_final(state):
                self.S.remove(state)
                del self.delta[state]

        for state in self.S:
            for symbol in self.delta[state].keys():
                if len(self.delta[state][symbol]) == 1:
                    if self.delta[state][symbol][0] not in self.S:
                        self.delta[state][symbol] = []

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

                

    
