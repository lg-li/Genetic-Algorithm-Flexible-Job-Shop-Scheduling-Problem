# GA FJSSP 调度模型算法类
import copy
import random
import sys

from colorama import init
from deap import base, creator
from termcolor import colored

from Heuristics import Heuristics
from Scheduler import Scheduler

# 记录CNC所在列位置，RGV以列差进行平移并计算时耗
CNC_LOCATION_COLOMN = [0, 1, 1, 2, 2, 3, 3, 4, 4]

class GAScheduler:
    def __init__(self, machines, jobs, RGV_config):
        init()  # 初始化用于彩色显示的可视化命令行符号
        self.__original_stdout = sys.stdout
        self.__toolbox = base.Toolbox()
        self.__machines = machines
        self.__jobs = jobs
        self.__rgv_config = RGV_config  # RGV 运动配置

    # 约束顺序
    @staticmethod  # 静态方法
    def constraint_order_respected(individual):
        list = [(activity.id_job, activity.id_activity)
                for (activity, _) in individual]
        for key, (id_job, id_activity) in enumerate(list):
            if id_activity == 1:
                continue
            elif not list.index((id_job, id_activity - 1)) < key:
                return False
        return True

    # 初始化遗传算法的个体
    def init_individual(self, ind_class, size):
        temp_jobs_list = copy.deepcopy(self.__jobs)
        temp_machines_list = copy.deepcopy(self.__machines)

        # 运行调度器 传递RGV配置
        s = Scheduler(temp_machines_list, 1, temp_jobs_list, self.__rgv_config)
        s.run(Heuristics.random_operation_choice, verbose=True)

        # 搜索所有作业对象和完成的操作
        list_activities = []
        for temp_job in temp_jobs_list:
            for temp_activity in temp_job.activities_done:
                activity = self.__jobs[temp_activity.id_job -
                                       1].get_activity(temp_activity.id_activity)
                operation = activity.get_operation(
                    temp_activity.operation_done.id_operation)
                list_activities.append(
                    (temp_activity.operation_done.time, activity, operation))
        # print(str(list_activities))
        # 以时间排序作业对象
        list_activities = sorted(list_activities, key=lambda x: x[0])
        individual = [(activity, operation)
                      for (_, activity, operation) in list_activities]
        del temp_jobs_list, temp_machines_list
        return ind_class(individual)

    # 初始化种群
    def init_population(self, total_population):
        return [self.__toolbox.individual() for _ in range(total_population)]

    # 计算RGV移动时耗
    def calculate_RGV_movement_time_cost(self, from_CNC_id, to_CNC_id, verbose=False):
        # CNC ID = 0 则为初始状态
        col_from = CNC_LOCATION_COLOMN[from_CNC_id]
        col_to = CNC_LOCATION_COLOMN[to_CNC_id]
        diff = abs(col_to-col_from)
        if diff == 0:
            return 0
        elif diff == 1:
            # print(colored("RGV移动", "cyan"), "从CNC", from_CNC_id, "# 移动到 CNC", to_CNC_id, "#，耗时 ", self.__rgv_config.RGV_movement_1_time)
            return self.__rgv_config.RGV_movement_1_time
        elif diff == 2:
            # print(colored("RGV移动", "cyan"), "从CNC", from_CNC_id, "# 移动到 CNC", to_CNC_id, "#，耗时 ", self.__rgv_config.RGV_movement_2_time)
            return self.__rgv_config.RGV_movement_2_time
        elif diff == 3:
            # print(colored("RGV移动", "cyan"), "从CNC", from_CNC_id, "# 移动到 CNC", to_CNC_id, "#，耗时 ", self.__rgv_config.RGV_movement_3_time)
            return self.__rgv_config.RGV_movement_3_time

    # 计算个体所耗时：需要考虑RVG移动时间 和 CNC故障情况
    def compute_time(self, individual):
        # 列出与发生时间匹配的活动
        list_time = []
        # 调度存储 (以机器ID为索引)
        schedule = {}
        for machine in self.__machines:
            schedule.update({machine.id_machine: []})
        # 已完成操作存储对象 (以工件ID为索引)
        operations_done = {}
        for job in self.__jobs:
            operations_done.update({job.id_job: []})

        previous_machine_id = 1  # 从1开始
        extra_time_cost = 0
        previous_event_time = 0

        # 对于每个个体，在其将要被认为开始之时计算起实际耗时
        #  (包含RGV移动时间，若CNC故障的恢复时间。清洗时间和上下料时间在初始化时已经考虑)
        for activity, operation in individual:
            # 获取上一次操作完成的时间
            # print("操作时间 = ", operation.duration)
            time_last_operation, last_operation_job = operations_done.get(activity.id_job)[-1] if len(
                operations_done.get(activity.id_job)) > 0 else (0, None)
            time_last_machine, last_operation_machine = schedule.get(operation.id_machine)[-1] if len(
                schedule.get(operation.id_machine)) > 0 else (0, None)
            
            # 计算RGV额外耗时 RGV清洗时间 RGV移动时间 和 RGV对应设备上料下料时间
            extra_time_cost = self.__rgv_config.RGV_clean_time + \
                self.__machines[operation.id_machine-1].install_uninstall_time_cost + \
                self.calculate_RGV_movement_time_cost(
                    previous_machine_id, operation.id_machine)
            
            if operation.id_operation == -1:
                # 发生故障
                # print("故障发生于",  operation.id_machine)
                extra_time_cost = 0
            
            previous_machine_id = operation.id_machine  # 更新本次CNC机器ID

            # 不存在上一次的机床和工件
            if last_operation_machine is None and last_operation_job is None:
                # 首次启动，从起始位置开始
                time = extra_time_cost
            elif last_operation_machine is None:
                time = time_last_operation + last_operation_job.duration + extra_time_cost
            elif last_operation_job is None:
                time = time_last_machine + last_operation_machine.duration + extra_time_cost
            else: # 均非空 获取上次操作完成的时间
                time = max(time_last_operation + last_operation_job.duration,
                           time_last_machine + last_operation_machine.duration) + extra_time_cost
            # 校验RGV时间限制
            if time == previous_event_time:
                time = previous_event_time + extra_time_cost
            elif time > previous_event_time and (time - previous_event_time) < extra_time_cost:
                time = previous_event_time + extra_time_cost
            elif time < previous_event_time:
                for temp_time in list_time:
                    if time >= temp_time and time - temp_time < extra_time_cost:
                        time = temp_time + extra_time_cost
                        break
            
            #print("前序时间 = ", previous_event_time)
            previous_event_time = time
            list_time.append(time)
            #print("时间 = ", time)
            operations_done.update({activity.id_job: operations_done.get(
                activity.id_job) + [(time, operation)]})
            schedule.update({operation.id_machine: schedule.get(
                operation.id_machine) + [(time, operation)]})
            
        # 计算完成所有工件的总时间
        total_time = 0
        for machine in self.__machines:
            if len(schedule.get(machine.id_machine)) > 0:
                time, operation = schedule.get(machine.id_machine)[-1]
                if time + operation.duration > total_time:
                    total_time = time + operation.duration
        # print("总时间", total_time)
        return total_time, list_time

    # 评估个体的适应度，即计算每个个体消耗的总时间
    def evaluate_individual(self, individual):
        return self.compute_time(individual)[0],

    # 突变函数 根据输入个体创建突变体
    # 即在具有多个操作选择的作业中选择另一个操作
    @staticmethod
    def mutate_individual(individual):
        # 选择可能的候选项，表示在具有多个操作选项作业中选择其它选项(即同一工序有多个CNC机床可完成，则尝试选择其它机床)
        candidates = list(filter(lambda element: len(
            element[0].next_operations) > 1, individual))
        # 若存在候选项，随机选取一个
        if len(candidates) > 0:
            mutant_activity, previous_operation = candidates[random.randint(
                0, len(candidates) - 1)]
            id_mutant_activity = [element[0]
                                  for element in individual].index(mutant_activity)
            mutant_operation = previous_operation
            while mutant_operation.id_operation == previous_operation.id_operation:
                mutant_operation = mutant_activity.next_operations[
                    random.randint(0, len(mutant_activity.next_operations) - 1)]
            individual[id_mutant_activity] = (
                mutant_activity, mutant_operation)
        # 移除前次的适应度(需要重新计算)
        del individual.fitness.values
        # 返回突变个体
        return individual

    # 计算边界
    @staticmethod
    def compute_bounds(permutation, considered_index):
        considered_activity, _ = permutation[considered_index]
        min_index = key = 0
        max_index = len(permutation) - 1
        while key < max_index:
            activity, _ = permutation[key]
            if activity.id_job == considered_activity.id_job:
                if min_index < key < considered_index:
                    min_index = key
                if considered_index < key < max_index:
                    max_index = key
            key += 1
        return min_index, max_index

    # 置换个体
    # 在这里意味着选择一个作业活动并用另一个作业活动进行置换
    #  置换约束: 不能在同一作业中移动另一个活动之前或之后的活动
    def permute_individual(self, individual):
        permutation_possible = False
        considered_index = considered_permutation_index = 0
        while not permutation_possible:
            considered_index = min_index = max_index = 0
            # 循环直到可进行移动，即当 max_index - min_index> 2 时
            while max_index - min_index <= 2:
                considered_index = random.randint(0, len(individual) - 1)
                min_index, max_index = self.compute_bounds(
                    individual, considered_index)

            # 选择这些边界内的随机工序活动[activity类](不含边界)以进行置换
            considered_permutation_index = random.randint(
                min_index + 1, max_index - 1)
            min_index_permutation, max_index_permutation = self.compute_bounds(individual,
                                                                               considered_permutation_index)
            if min_index_permutation < considered_index < max_index_permutation:
                permutation_possible = considered_index != considered_permutation_index

        # 找到一个可能的个体进行置换
        individual[considered_index], individual[considered_permutation_index] = individual[
            considered_permutation_index], \
            individual[considered_index]
        return individual

    # 在调度程序内移动一个活动(不同于交换)
    def move_individual(self, individual):
        considered_index = min_index = max_index = 0
        # 循环直到可进行移动，即当max_index - min_index> 2时
        while max_index - min_index <= 2:
            considered_index = random.randint(0, len(individual) - 1)
            min_index, max_index = self.compute_bounds(
                individual, considered_index)
        # 循环直到找到要移动的不同索引
        new_index = random.randint(min_index + 1, max_index - 1)
        while considered_index == new_index:
            new_index = random.randint(min_index + 1, max_index - 1)
        # 在调度器内移动作业活动
        individual.insert(new_index, individual.pop(considered_index))
        return individual

    def evolve_individual(self, individual, mutation_probability, permutation_probability, move_probability):
        future_individual = copy.deepcopy(individual)
        if random.randint(0, 100) < mutation_probability:
            future_individual = self.mutate_individual(future_individual)
        if random.randint(0, 100) < permutation_probability:
            future_individual = self.permute_individual(future_individual)
        if random.randint(0, 100) < move_probability:
            future_individual = self.move_individual(future_individual)
        return future_individual

    # 在种群中的个体之间进行竞争以保留一部分
    @staticmethod
    def run_tournament(population, total=10):
        # 断言：不可指定大于竞争数量的剩余种群大小
        assert total <= len(population)
        new_population = []
        while len(new_population) < total:
            first_individual = population[random.randint(
                0, len(population) - 1)]
            second_individual = population[random.randint(
                0, len(population) - 1)]
            if first_individual.fitness.values[0] < second_individual.fitness.values[0]:
                new_population.append(first_individual)
                population.remove(first_individual)
            else:
                new_population.append(second_individual)
                population.remove(second_individual)
        del population
        return new_population

    # 模拟个体
    def run_simulation(self, individual):
        total_time, list_time = self.compute_time(individual)
        previous_machine_id = 1
        result_file_content = "加工物料序号, 加工CNC序号, 开始时间, 结束时间, 耗时"
        for key, (individual_activity, individual_operation) in enumerate(individual):
            activity = self.__jobs[individual_activity.id_job -
                                   1].get_activity(individual_activity.id_activity)
            operation = activity.get_operation(
                individual_operation.id_operation)
            operation.time = list_time[key]
            if(operation.id_operation == -1):
                print(colored("[故障]", "red"),"[时间", operation.time, "时], CNC", operation.id_machine,"# 机器故障 持续：", operation.duration)
            else:
                diff = abs(
                    CNC_LOCATION_COLOMN[operation.id_machine]-CNC_LOCATION_COLOMN[previous_machine_id])
                if diff == 0:
                    print(colored("[模拟]RGV", "cyan"), "RGV 无需移动")
                elif diff == 1:
                    print(colored("[模拟]RGV", "cyan"), "从CNC", operation.id_machine, "# 移动到 CNC",
                        previous_machine_id, "#，耗时 ", self.__rgv_config.RGV_movement_1_time)
                elif diff == 2:
                    print(colored("[模拟]RGV", "cyan"), "从CNC", operation.id_machine, "# 移动到 CNC",
                        previous_machine_id, "#，耗时 ", self.__rgv_config.RGV_movement_2_time)
                elif diff == 3:
                    print(colored("[模拟]RGV", "cyan"), "从CNC", operation.id_machine, "# 移动到 CNC",
                        previous_machine_id, "#，耗时 ", self.__rgv_config.RGV_movement_3_time)
                previous_machine_id = operation.id_machine
                print(colored("[模拟]加工", self.RUN_LABLE_COLOR), "[时间", operation.time, "时] 由CNC",
                    operation.id_machine, "#处理 物料工件", individual_activity.id_job, "#")
            operation.place_of_arrival = 0  # 完成此工作
            result_file_content = result_file_content + "\n" + str(individual_activity.id_job) + ", " + str(operation.id_machine) + ", " + str(operation.time) + "," + str(operation.time + operation.duration) + ", " + str(operation.duration)
            activity.terminate_operation(operation)
        return total_time, result_file_content

    RUN_LABLE = "[GA调度]"
    RUN_LABLE_COLOR = "blue"

    # 入口函数 运行GA算法调度
    def run_genetic(self, total_population=10, max_generation=100, verbose=False):
        assert total_population > 0, max_generation > 0

        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        # 禁用输出若开启静默
        if not verbose:
            sys.stdout = None

        self.__toolbox.register(
            "individual", self.init_individual, creator.Individual, size=1)
        self.__toolbox.register("mutate", self.mutate_individual)
        self.__toolbox.register("permute", self.permute_individual)
        self.__toolbox.register("evaluate", self.evaluate_individual)

        # 彩色提示字体
        print(colored(self.RUN_LABLE, self.RUN_LABLE_COLOR), "生成种群")

        # 初始化种群
        population = self.init_population(total_population)

        best = population[0]
        best.fitness.values = self.evaluate_individual(best)
        print(colored(self.RUN_LABLE, self.RUN_LABLE_COLOR),
              "将进化共", max_generation, "代种群")

        log_file_content = "代数, 变异数, 最优个体时间"
        for current_generation in range(max_generation):
            # 为下一代生成变异率、交叉率和置换率
            mutation_probability = random.randint(50, 100)
            permutation_probability = random.randint(50, 100)
            move_probability = random.randint(50, 100)
            # 进化种群
            print(colored("进化", "green"), "正在进化第", current_generation + 1, "代")
            mutants = list(set([random.randint(0, total_population - 1) for _ in
                                range(random.randint(1, total_population))]))
            print(colored("变异", "red"), "此代有", len(mutants), "只个体发生变异")
            for key in mutants:
                individual = population[key]
                population.append(
                    self.evolve_individual(individual, mutation_probability, permutation_probability, move_probability))
            # 通过适应度评价整体种群
            fitnesses = list(map(self.evaluate_individual, population))
            for ind, fit in zip(population, fitnesses):
                ind.fitness.values = fit
                if best.fitness.values[0] > ind.fitness.values[0]:
                    print(colored("优胜", "cyan"), "发现更优个体，当前最优时间为 ",
                          ind.fitness.values[0])
                    best = copy.deepcopy(ind)
            population = self.run_tournament(population, total=total_population)
            log_file_content = log_file_content + "\n" + str(current_generation + 1) + "," + str(len(mutants)) + "," + str(best.fitness.values[0])

        print(colored(self.RUN_LABLE, self.RUN_LABLE_COLOR), "进化完成")
        if self.constraint_order_respected(best):
            print(colored(self.RUN_LABLE, self.RUN_LABLE_COLOR),
                  "最优时间 = ", best.fitness.values[0])
            print(colored(self.RUN_LABLE, self.RUN_LABLE_COLOR),
                  "使用最优调度方案模拟RGV调度...")
            total_time, result_file_content = self.run_simulation(best)
            print(colored(self.RUN_LABLE, self.RUN_LABLE_COLOR), "模拟完成")
            print(colored(self.RUN_LABLE, self.RUN_LABLE_COLOR), "GA 调度计算完毕")
        else:
            print(colored(self.RUN_LABLE, self.RUN_LABLE_COLOR), "个体所给数据不满足算法约束条件")

        # 启用标准输出
        if not verbose:
            sys.stdout = self.__original_stdout

        return total_time, log_file_content, result_file_content
