import numpy as np

'''
    Class Otomat 
'''
class Otomat:
    def __init__(self, sigma, S, S0, F, delta):
        assert len(sigma) > 0, 'Bảng chữ cái sigma rỗng'
        assert len(S) > 0, 'Tập trạng thái S rỗng'
        assert S0 in S, f'Trạng thái khởi đầu {S0} không thuộc S'
        for state in F:
            assert state in S, f'Trạng thái kết {state} không thuộc S'
        self.sigma = sigma
        self.S = S 
        self.S0 = S0 
        self.F = F 
        self.delta = delta 
        self.extraState = 'ES'

    '''
        Đơn định hóa otomat
    '''

    def remove_epsilon(self):
        '''
            Xóa các cạnh epsilon
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
                    self.delta[state][symbol] = list(set(self.delta[state][symbol]))

                # S0 -> $S2, S1 -> aS0. -> S1 -> aS2
                for other_state in self.S:
                    for symbol in self.delta[other_state].keys():
                        if state in self.delta[other_state][symbol]:
                            self.delta[other_state][symbol] += self.delta[state]['$']

                del self.delta[state]['$']                

    def fill(self):
        '''
            Điền hàm chuyển trạng thái rỗng
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
            Đầy đủ và đơn định hóa otomat
        '''
        # Đầy đủ hóa otomat
        self.fill()

        # Khử epsilon
        self.remove_epsilon()
        
        # Đơn định hóa
        queue = [self.S0]
        visited = []
        while len(queue) > 0:
            current_state = queue.pop(0)
            # Nếu đã thăm trạng thái hiện tại thì không làm gì cả
            if current_state in visited:
                continue 
            visited.append(current_state)

            for symbol in self.sigma:
                targets = self.delta[current_state][symbol]
                for i in range(len(targets)):
                    if '_' in targets[i]:
                        current = targets.pop(i)
                        targets += current.split('_')
                targets = list(set(targets))
                # Trường hợp hàm chuyển trạng thái delta(current_state, symbol) không đơn định
                if len(targets) > 1:
                    # ['S1', 'S2'] -> 'S1_S2'
                    new_state = '_'.join(sorted(targets))
                    # Nếu đã thăm trạng thái này rồi thì không thăm lại
                    if new_state in visited:
                        # Thay kết quả của hàm chuyển trạng thái cũ thành trạng thái mới
                        self.delta[current_state][symbol] = [new_state]
                        continue
                    
                    # Khởi tạo hàm chuyển trạng thái cho trạng thái mới
                    self.delta[new_state] = {}

                    # Xây dựng hàm chuyển trạng thái cho trạng thái mới
                    for character in self.sigma:
                        new_targets_for_new_state = []
                        for state in targets:
                            for target in self.delta[state][character]:
                                if target not in new_targets_for_new_state:
                                    new_targets_for_new_state.append(target)
                        new_targets_for_new_state = list(set(new_targets_for_new_state))
                        self.delta[new_state][character] = new_targets_for_new_state
                    
                    # Thay kết quả của hàm chuyển trạng thái cũ thành trạng thái mới
                    self.delta[current_state][symbol] = [new_state]

                    # Thêm trạng thái mới vào danh sách chờ
                    queue.append(new_state)

                # Nếu hàm chuyển trạng thái delta(current_state, symbol) đơn định thì thêm vào queue và không làm gì cả
                elif len(targets) == 1:
                    queue.append(targets[0])

        # Xóa các trạng thái thừa
        for state in self.S:
            if state not in visited:
                del self.delta[state]

        self.S = sorted(visited)

        # Thêm các trạng thái kết thúc mới
        for state in self.S:
            for f in self.F:
                if f in state:
                    if state not in self.F:
                        self.F.append(state)

        # Xóa các trạng thái kết thúc không tồn tại trong tập trạng thái mới
        for f in self.F:
            if f not in self.S:
                self.F.remove(f)

    '''
        Tối thiểu hóa otomat
    '''

    def fill_table(self):
        '''
            Điền bảng đánh dấu các trạng thái thỏa mãn: 
            table(A, B) = 1 nếu chỉ A hoặc B không thuộc F, hoặc tồn tại chữ cái e thỏa mãn table(delta(A, e), delta(B, e)) = 1
            Returns:
                table: Bảng đánh dấu trạng thái
        '''
        num_of_states = len(self.S)
        table = np.zeros((num_of_states, num_of_states), dtype=np.bool)
        while True:
            last = True
            for i in range(num_of_states):
                state_A = self.S[i]
                for j in range(num_of_states):
                    state_B = self.S[j]
                    if table[i][j]:
                        continue
                    if state_A in self.F and state_B not in self.F:
                        last = False
                        table[i][j] = 1
                    else:
                        for symbol in self.sigma:
                            next_state_A = self.delta[state_A][symbol][0]
                            next_state_B = self.delta[state_B][symbol][0]
                            if table[self.S.index(next_state_A)][self.S.index(next_state_B)] \
                              or table[self.S.index(next_state_B)][self.S.index(next_state_A)]:
                                last = False
                                table[i][j] = 1
                                break
            if last:
                break  
        return table

    def combine_unmarked_pairs(self, table):
        '''
            Ghép các cặp trạng thái không được đánh dấu
            Args:
                table: Bảng đánh dấu các cặp trạng thái
            Returns:
                unmarked_states_group: Tập hợp các nhóm trạng thái chưa được đánh dấu
        '''
        unmarked_states_group = []
        num_of_states = len(self.S)
        for i in range(num_of_states):
            for j in range(num_of_states):
                if i == j:
                    continue
                if not table[i][j]:
                    if [self.S[i], self.S[j]] not in unmarked_states_group\
                        and [self.S[j], self.S[i]] not in unmarked_states_group:
                        # [C, D], [D, E] -> [C, D, E]
                        flag = False
                        for k in range(len(unmarked_states_group)):
                            if self.S[i] in unmarked_states_group[k] or self.S[j] in unmarked_states_group[k]:
                                flag = True
                                unmarked_states_group[k] += [self.S[i], self.S[j]]
                                unmarked_states_group[k] = list(set(unmarked_states_group[k]))
                                break
                        if not flag:
                            unmarked_states_group.append([self.S[i], self.S[j]])
        return unmarked_states_group

    def minimize(self):
        '''
            Tối thiểu hóa otomat sử dụng phương pháp điền bảng
            https://www.youtube.com/watch?v=UiXkJUTkp44
        '''
        self.DFA()
        table = self.fill_table()
        unmarked_states_group = self.combine_unmarked_pairs(table)

        # Xây dựng otomat mới
        for group in unmarked_states_group:
            # Tạo trạng thái mới và thay thế trạng thái cũ
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

        # Thay thế trạng thái cũ trong bảng chuyển trạng thái
        for state in self.S:
            for symbol in self.sigma:
                for idx, trans_state in enumerate(self.delta[state][symbol]):
                    if trans_state not in self.S:
                        for new_state in self.S:
                            if trans_state in new_state:
                                self.delta[state][symbol][idx] = new_state
                self.delta[state][symbol] = list(set(self.delta[state][symbol]))    


        # Thay thế trạng thái cũ trong tập trạng thái kết
        for idx, final_state in enumerate(self.F):
            if final_state not in self.S:
                for state in self.S:
                    if final_state in state:
                        self.F[idx] = state
        self.F = list(set(self.F))

def parse_input_file(filepath):
    '''
        Đọc otomat từ 1 tệp và trả về otomat đó
        Args: 
            filepath: path to file that will be parsed
        Returns:
            Otomat
    '''
    f = open(filepath, 'r')
    S = f.readline()[:-1].split(',')
    sigma = f.readline()[:-1].split(',')
    S0 = f.readline()[:-1]
    if S0 not in S:
        print('Lỗi: Trạng thái bắt đầu không thuộc S')
        exit()
    F = f.readline()[:-1].split(',')
    for state in F:
        if state not in S:
            print('Lỗi: Trạng thái kết thúc {} không thuộc trạng thái S'.format(state))
            exit()
    delta = {}
    for line in f:
        tmp = []
        if line[-1] == '\n':
            tmp = line[:-1].split(',')
        else:
            tmp = line.split(',')

        if len(tmp) < 3:
            print('Lỗi: {}. Hàm chuyển trạng thái phải có dạng state,symbol,state1,state2,...'.format(line))
            exit()

        for i in range(len(tmp)):
            if i == 1:
                continue
            if tmp[i] not in S:
                print('Lỗi: Trạng thái {} không thuộc S'.format(tmp[0]))
                exit()
        if tmp[1] not in sigma and tmp != '$':
            print('Lỗi: {} không thuộc sigma'.format(tmp[1]))
            exit()
        else:
            if tmp[0] not in delta.keys():
                delta[tmp[0]] = {}
            delta[tmp[0]][tmp[1]] = tmp[2:]
    return Otomat(sigma, S, S0, F, delta)

def main():
    filepath = input('Nhập tên file đầu vào: ')
    otomat = parse_input_file(filepath)
    print('Tập trạng thái ban đầu: ', otomat.S)
    print('Tập trạng thái kết ban đầu: ', otomat.F)
    print('Bảng chuyển trạng thái ban đầu:')
    print('{:>10}'.format('delta'), end='')
    for symbol in otomat.sigma:
        print('{:>10}'.format(symbol), end='')
    print()

    for state in otomat.S:
        print('{:>10}'.format(state), end='')
        for symbol in otomat.sigma:
            if symbol not in otomat.delta[state]:
                print('{:>10}'.format('-'), end='')
            else:
                print('{:>10}'.format(','.join(otomat.delta[state][symbol])), end='')
        print()
    print('\n-------------------------------------------\n')

    # Đơn định hóa
    # otomat.DFA()

    # print('Tập trạng thái sau đơn định hóa: ', otomat.S)
    # print('Tập trạng thái kết sau đơn định hóa: ', otomat.F)
    # print('Bảng chuyển trạng thái sau đơn định hóa:')
    # print('{:>10}'.format('delta'), end='')
    # for symbol in otomat.sigma:
    #     print('{:>10}'.format(symbol), end='')
    # print()

    # for state in otomat.S:
    #     print('{:>10}'.format(state), end='')
    #     for symbol in otomat.sigma:
    #         if symbol not in otomat.delta[state]:
    #             print('{:>10}'.format('-'), end='')
    #         else:
    #             print('{:>10}'.format(otomat.delta[state][symbol][0]), end='')
    #     print()

    # Tối thiểu hóa
    otomat.minimize()
    print('Tập trạng thái sau tối thiểu hóa: ', otomat.S)
    print('Tập trạng thái kết sau tối thiểu hóa: ', otomat.F)
    print('Bảng chuyển trạng thái sau tối thiểu hóa:')
    print('{:>10}'.format('delta'), end='')
    for symbol in otomat.sigma:
        print('{:>10}'.format(symbol), end='')
    print()

    for state in otomat.S:
        print('{:>10}'.format(state), end='')
        for symbol in otomat.sigma:
            if symbol not in otomat.delta[state]:
                print('{:>10}'.format('-'), end='')
            else:
                print('{:>10}'.format(otomat.delta[state][symbol][0]), end='')
        print()

main()
                

    