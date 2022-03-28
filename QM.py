import numpy as np
import math
import queue


class Node:

    def __init__(self, term, level) -> None:
        '''
        项
        '''
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
        '''
        多次合并
        '''
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
        收集所有的主蕴含项PI
        '''
        for groups in self.node_list:
            for group in groups:
                for node in group:
                    if not node.covered:
                        self.PI.append(node)
        return self.PI

    def find_essential_prime(self, Chart):
        '''
        找到质主蕴含项
        '''
        pos = np.argwhere(Chart.sum(axis=0) == 1)
        essential_prime = []
        for i in range(len(self.PI)):
            for j in range(len(pos)):
                if Chart[i][pos[j][0]] == 1:
                    essential_prime.append(i)
        essential_prime = list(set(essential_prime)) # 去除重复
        return essential_prime

    def cover_left(self, Chart):
        '''
        用BFS（广度优先搜索）的方法遍历，找出项最少的方法
        '''
        list_result = []
        max_len = len(Chart)                           # 最大广度，也就是最多用到的项数
        myQueue = queue.Queue(math.factorial(max_len)) # 队列
        for i in range(max_len):
            myQueue.put([i])

        stop_flag = False                          # 停止搜索标志
        while not myQueue.empty():
            minterm_mark = np.zeros(len(Chart[0])) # 用于标记剩余的最小项是否被cover了
            choice = myQueue.get()
            if stop_flag and len(list_result[-1]) < len(choice):
                break

            for row in choice:
                minterm_mark += Chart[row]

            if all(minterm_mark): # 如果当前choice能cover所有minterm
                list_result.append(choice)
                stop_flag = True  # 设置标志但不马上退出，防止有多解

            for row in range(choice[-1] + 1, max_len):
                myQueue.put(choice + [row]) # 产生新节点，加入队列
        return list_result

    def find_minimum_cost(self, Chart):
        '''
        找到项数最少的方案
        '''
        QM_final = []
        essential_prime = self.find_essential_prime(Chart)

        # 更新Chart
        for i in range(len(essential_prime)):
            for j in range(len(Chart[0])):
                if Chart[essential_prime[i]][j] == 1:
                    for row in range(len(Chart)):
                        Chart[row][j] = 0

        # 如果Chart都是0，说明质主蕴含项已经覆盖所有最小项，已经得到最终结果了
        if not np.sum(Chart):
            QM_final = [essential_prime]
        # 否则找出未被质主蕴含项covered的minterm，以及那些能cover它们的PI（的行坐标）
        else:
            pos_col_left = np.argwhere(Chart.sum(axis=0) > 0) # 注意这一步得到的是二维数组
            pos_row_left = np.argwhere(Chart.sum(axis=1) > 0) # 注意这一步得到的是一维数组

            # 生成新的Chart，删去全为0的行列
            new_Chart = np.zeros([len(pos_row_left), len(pos_col_left)])
            for i in range(len(pos_row_left)):
                for j in range(len(pos_col_left)):
                    if Chart[pos_row_left[i]][pos_col_left[j][0]] == 1:
                        new_Chart[i][j] = 1

            list_result = self.cover_left(new_Chart)
            for lst in list_result:
                final_solution = essential_prime + list(
                    map(lambda x: pos_row_left[x], lst)
                )
                QM_final.append(final_solution)
        return QM_final

    def select(self):
        '''
        选择最终方案并输出
        '''
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
        '''
        运行入口
        '''
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
    # myQM = QM(4, [0, 1, 3, 5, 8, 14, 15]).run()
    myQM = QM(2, [0, 1, 2, 3]).run()
