# GA FJSSP 主程序运行入口
import copy
import os
import sys
import timeit
import warnings

from DataReader import read
from GA import GAScheduler
from GraphDrawer import GraphDrawer
from Heuristics import Heuristics
from Scheduler import Scheduler

print("=== FJSSP 调度方案计算模拟程序 （基于遗传算法） ===")
# 数据文件路径
if len(sys.argv) == 1:
	path = input("输入数据文件路径（相对当前目录路径或绝对路径）") 
else:
	path = sys.argv[1] # 从命令行传参读取

warnings.simplefilter('ignore', RuntimeWarning)
# 文件数据解析
jobs_list, machines_list, number_max_operations, RGV_config = read(path)
number_total_machines = len(machines_list)
number_total_jobs = len(jobs_list)

# 循环交互询问
while True:
	temp_jobs_list = copy.deepcopy(jobs_list)
	temp_machines_list = copy.deepcopy(machines_list)
	# 显示当前数据
	print("已加载的数据:")
	print('\t指定共', number_total_jobs, "个物料工件需要加工")
	print('\t指定共', number_total_machines, "台CNC可用")
	print("\t每个CNC可允许同时进行", str(number_max_operations), "个操作")
	print("\tCNC故障率：", temp_machines_list[0].CNC_break_down_rate)
	print("\tCNC故障恢复时间：", temp_machines_list[0].CNC_recovery_time_cost)
	print("\n")
	choice = input("是否使用上述加载的数据使用 GA 生成 FJSSP 最优 RVG 调度策略? [y/n]: ")
	if choice == "y":
		string = input("设置总种群数量: ")
		total_population = int(string)
		string = input("设置最大代数: ")
		max_generation = int(string)
		start = timeit.default_timer() # 运算计时器
		s = GAScheduler(temp_machines_list, temp_jobs_list, RGV_config)
		total_time, log_file_content, result_file_content = s.run_genetic(total_population=total_population, max_generation=max_generation, verbose=True)
		stop = timeit.default_timer()
		print("本次计算程序耗时" + str(stop - start) + "秒")
		print("正在保存记录到磁盘...")
		file = open(path + ".log.csv", "w+")
		file.write(str(log_file_content))
		print("记录文件已保存到", path, ".log.csv")

		print("正在保存结果到磁盘...")
		file = open((path + ".result.csv"), "w+")
		file.write(str(result_file_content))
		print("结果文件已保存到", path, ".result.csv")

		draw = input("是否画出此模拟最优策略的甘特图 ? [y/n] ")
		if draw == "n" or draw == "N":
			continue
		else:
			print("绘图中...")
			GraphDrawer.draw_schedule(number_total_machines, 1, temp_jobs_list, filename=(path + ".result.png"))
		del s # 清空变量
	elif choice == "n":
		break
	else:
		print("不正确的输入，请重试。")
	del temp_jobs_list, temp_machines_list
