# 格式化数据读取函数
# 数据格式说明
# 在第一行中包含至少2个整数：
# 	第一个是全部作业数a，第二个是CNC机器数b(机器ID由1开始排列)，第三个参数c非必需，它是每个机器的同时进行操作容量(此算法通常为1)
#
# 在第二行中包含b个整数：
# 	分别表示RGV在对应顺序CNC机器一次上下料所需之单位时间
#
# 在第三行中包含4个整数：
# 	分别表示RGV 清洗作业时间 和 移动1、2和3个单位CNC机器间隔距离所需之时间
#
# 在第四行中包含2个参数：
# 	分别对应 故障率(小数) 和 故障恢复时间(整数，单位时间)。
# 	若故障率不为0，机器在开始前每次将以此概率随机发生故障并停止工作指定之故障时间，此后方才恢复进入加工序列
#
# 接下来的a行中行代表一个工件的作业(变量对应activity)：
# 	第一个整数是该次作业的操作工序(变量对应operation)之数量 k，
# 	第二个数字 (若k >= 1) 是可以处理第一个工序的机器(变量对应machine)数量;
# 		然后根据k，有k对(机器ID, 处理时间)的参数对以空格间隔，指定哪些机器可以处理本次工序及其处理时间;
# 		然后为第二次工序的数据，以此类推...

import os
import re

from Activity import Activity
from CNCMachine import Machine
from Job import Job
from Operation import Operation
from RGVSystemConfig import RGVSystemConfig


def read(path):  # 打开文件
    with open(os.path.join(os.getcwd(), path), "r") as data:
        # 第一行读取3个参数：全部作业数a，CNC机器数b，每个机器的同时进行操作容量c
        total_jobs, total_machines, max_operations = re.findall(
            '\S+', data.readline())
        # 转为数字
        number_total_jobs, number_total_machines, number_max_operations = int(total_jobs), int(total_machines), int(float(
            max_operations))

        # 生成机器数ID 和 最大操作数
        machines_list = []  # 机器表
        machines_install_uninstall_time_cost_list = []  # 机器上下料时间表
        # 第二行读取b个参数，RGV在对应顺序(b个)CNC机器一次上下料所需之单位时间
        machines_install_uninstall_time_cost_list = re.findall(
            '\S+', data.readline())
        # 第三行读取4个参数：RGV清洗作业时间，移动1个单位，2个单位，3个单位CNC机器间隔距离所需之时间
        RGV_clean_time, RGV_movement_1_time, RGV_movement_2_time, RGV_movement_3_time = re.findall(
            '\S+', data.readline())
        # 第四行读取2个参数： 故障率， 故障恢复时间(单位时间)
        CNC_break_down_rate, CNC_recovery_time_cost = re.findall(
            '\S+', data.readline())

        # 字符串数字化
        RGV_clean_time = int(RGV_clean_time)
        RGV_movement_1_time = int(RGV_movement_1_time)
        RGV_movement_2_time = int(RGV_movement_2_time)
        RGV_movement_3_time = int(RGV_movement_3_time)
        CNC_break_down_rate = float(CNC_break_down_rate)
        CNC_recovery_time_cost = int(CNC_recovery_time_cost)

        # 配置RGV车走动时间
        RGV_config = RGVSystemConfig(
            RGV_movement_1_time, RGV_movement_2_time, RGV_movement_3_time, RGV_clean_time)

        for id_machine in range(1, number_total_machines + 1):
            machines_list.append(
                Machine(
                    id_machine,
                    number_max_operations,
                    int(
                        machines_install_uninstall_time_cost_list[id_machine-1]),
                    CNC_break_down_rate,  # 机器故障率
                    CNC_recovery_time_cost  # 机器故障时间
                )
            )

        # 初始工件ID
        id_job = 1
        jobs_list = []
        for key, line in enumerate(data):
            if key >= number_total_jobs:
                break
            # 按空格分隔字符串
            parsed_line = re.findall('\S+', line)
            # 新建当前工件
            job = Job(id_job)
            # 当前作业活动
            id_activity = 1
            # 当前读取行从 第一行开始 按行解析
            i = 1
            import random
            while i < len(parsed_line):
                # 总待加工工件即等于剩余行数k
                number_operations = int(parsed_line[i])
                # 新建一道作业活动
                activity = Activity(job, id_activity)
                for id_operation in range(1, number_operations + 1):
                    # 插入操作到作业活动
                    machine_id_for_current_operation = int(
                        parsed_line[i + 2 * id_operation - 1])
                    activity.add_operation(
                        Operation(
                            id_operation,  # 顺序生成操作ID
                            machine_id_for_current_operation,  # 对应操作可选CNC机器ID
                            int(parsed_line[i + 2 * id_operation])
                            # 初始化操作耗时 = 输入原耗时
                        )
                    )

                # 随机插入故障占位
                if random.random() < CNC_break_down_rate:
                    # 随机指定故障CNC机器
                    activity.add_operation(
                        Operation(
                            -1, 
                            random.randint(1, number_total_machines), 
                            random.randint(10*60, 20*60) # 随机指定故障恢复时间 10-20分钟
                        )
                    )

                job.add_activity(activity)
                i += 1 + 2 * number_operations
                id_activity += 1
            jobs_list.append(job)
            id_job += 1

    return jobs_list, machines_list, number_max_operations, RGV_config
