import numpy as np
import itertools


class Node:

    def __init__(self, term, level) -> None:
        self.level = level # '-'的个数
        self.term = term   # 二进制形式（含有-)
        self.covered = False

    def one_num(self):
        '''
        返回term中'1'的个数
        '''
        return self.term.count('1')

    def compare(self, node1):
        '''
        比较两个Node能否合并
        '''
        res = []
        for i in range(len(self.term)):
            if self.term[i] == node1.term[i]:
                continue
            elif self.term[i] == '-' or node1.term[i] == "-":
                return (False, None)
            else:
                res.append(i)
        if len(res) == 1:
            return (True, res[0])
        return (False, None)

    def term2logic(self):
        logic_term = ''
        for i in range(len(self.term)):
            if self.term[i] == "-":
                continue
            elif self.term[i] == "1":
                logic_term += f'A{i}'
            else:
                logic_term += f"A{i}'"
        return logic_term


class QM:

    def __init__(self, num, lst) -> None:
        self.max_bits = num
        self.minterm_list = sorted(lst) # sort from min to max.
        self.node_list = []
        self.PI = []

    def num2str(self, num):
        '''
        将十进制数num转成二进制字符串term
        '''
        str = format(num, "b").zfill(self.max_bits)
        return str

    def _comp_binary_same(self, term, number):
        '''
        比较一个term是否能cover一个二进制串number
        '''
        for i in range(len(term)):
            if term[i] != '-':
                if term[i] != number[i]:
                    return False
        return True

    def _initial(self):
        '''
        将所有最小项以节点的形式储存，并根据'1'的个数分组
        '''
        flag = True # 判断是否需要进行下一轮递归比较
        groups = [[] for i in range(self.max_bits + 1)]
        for minterm in self.minterm_list:
            tmp_node = Node(term=self.num2str(minterm), level=0)
            groups[tmp_node.one_num()].append(tmp_node)
            flag = True
        self.node_list.append(groups)
        return flag

    def merge(self, level):
        flag = False                                        # flag用于判断是否需要进行下一轮的递归比较
        if level == 0:
            flag = self._initial()
        else:
            groups = self.node_list[level - 1]
            new_groups = [[] for i in range(self.max_bits + 1)]
            term_set = set()                                # 用来判断某个形式是否已经存在
            for i in range(len(groups) - 1):
                for node0 in groups[i]:
                    for node1 in groups[i + 1]:
                        cmp_res = node0.compare(node1)
                        if cmp_res[0]:
                            node0.covered = True
                            node1.covered = True
                            new_term = '{}-{}'.format(
                                node0.term[:cmp_res[1]],
                                node0.term[cmp_res[1] + 1:]
                            )
                            tmp_node = Node(term=new_term, level=level)
                            if tmp_node.term not in term_set:
                                new_groups[tmp_node.one_num()].append(tmp_node)
                                term_set.add(tmp_node.term)
                                print(tmp_node.term)
                                flag = True
            self.node_list.append(new_groups)
        if flag:
            self.merge(level + 1)

    def backtracking(self):
        '''
        收集所有的PI
        '''
        for groups in self.node_list:
            for group in groups:
                for node in group:
                    if not node.covered:
                        self.PI.append(node)
        return self.PI

    def find_prime(self, Chart):
        pos = np.argwhere(Chart.sum(axis=0) == 1)
        prime = []
        for i in range(len(self.PI)):
            for j in range(len(pos)):
                if Chart[i][pos[j][0]] == 1:
                    prime.append(i)
        prime = list(set(prime)) # 去除重复
        return prime

    #multiply two terms (ex. (p1 + p2)(p1+p4+p5) )..it returns the product
    def multiplication(self, list1, list2):
        list_result = []
        #if empty
        if len(list1) == 0 and len(list2) == 0:
            return list_result
        #if one is empty
        elif len(list1) == 0:
            return list2
        #if another is empty
        elif len(list2) == 0:
            return list1

        #both not empty
        else:
            for i in list1:
                for j in list2:
                    #if two term same
                    if i == j:
                        #list_result.append(sorted(i))
                        list_result.append(i)
                    else:
                        #list_result.append(sorted(list(set(i+j))))
                        list_result.append(list(set(i + j)))

            #sort and remove redundant lists and return this list
            list_result.sort()
            return list(
                list_result
                for list_result, _ in itertools.groupby(list_result)
            )

        #petrick's method

    def petrick_method(self, Chart):
        #initial P
        P = []
        for col in range(len(Chart[0])):
            p = []
            for row in range(len(Chart)):
                if Chart[row][col] == 1:
                    p.append([row])
            P.append(p)
        #do multiplication
        for l in range(len(P) - 1):
            P[l + 1] = self.multiplication(P[l], P[l + 1])

        P = sorted(P[len(P) - 1], key=len)
        final = []
        #find the terms with min length = this is the one with lowest cost (optimized result)
        min = len(P[0])
        for i in P:
            if len(i) == min:
                final.append(i)
            else:
                break
        #final is the result of petrick's method
        return final

    def find_minimum_cost(self, Chart):
        P_final = []
        #essential_prime = list with terms with only one 1 (Essential Prime Implicants)
        essential_prime = self.find_prime(Chart)

        #modifiy the chart to exclude the covered terms
        for i in range(len(essential_prime)):
            for j in range(len(Chart[0])):
                if Chart[essential_prime[i]][j] == 1:
                    for row in range(len(Chart)):
                        Chart[row][j] = 0

        #if all zero, no need for petrick method
        if not np.sum(Chart):
            P_final = [essential_prime]
        else:
            #petrick's method（选完
            P = self.petrick_method(Chart)

            P_cost = []
            for prime in P:
                count = 0
                for i in range(len(self.PI)):
                    for j in prime:
                        if j == i:
                            count = count + self.PI[i].term.count('-')
                P_cost.append(count)

            for i in range(len(P_cost)):
                if P_cost[i] == min(P_cost):
                    P_final.append(P[i])

            for i in P_final:
                for j in essential_prime:
                    if j not in i:
                        i.append(j)

        return P_final

    def select(self):
        Chart = np.zeros([len(self.PI), len(self.minterm_list)])
        for i in range(len(self.PI)):
            for j in range(len(self.minterm_list)):
                if self._comp_binary_same(
                    self.PI[i].term, self.num2str(self.minterm_list[j])
                ):
                    Chart[i][j] = 1

        primes = self.find_minimum_cost(Chart)
        # primes = list(set(primes))
        for prime in primes:
            str = ''
            for i in range(len(self.PI)):
                for j in prime:
                    if i == j:
                        str = str + self.PI[i].term2logic() + '+'
            if str[-1] == '+':
                str = str[:-1]
            print(str)

    def run(self):
        self.merge(0)
        self.backtracking()
        self.select()


if __name__ == '__main__':
    # num = int(input("please input the bits of logic number:"))
    # groups = list(
    #     map(
    #         lambda x: int(x),
    #         input("please input the logic function(seq=' '):").split()
    #     )
    # )
    # myQM = QM(num, groups).run()
    myQM = QM(4, [1, 2, 3, 5, 7, 11, 13]).run()
