# 基于启发式算法 (Heuristic, GA所属类别) 的调度外部控制类
import sys

from colorama import init
from termcolor import colored

# 记录CNC所在列位置，RGV以列差进行平移并计算时耗
CNC_LOCATION_COLOMN = [0, 1, 1,2,2,3,3,4,4]
class Scheduler:
	def __init__(self, machines, max_operations, jobs, RGV_config):
		init()  # 彩色显示标签初始化
		self.__original_stdout = sys.stdout
		self.__machines = machines
		self.__jobs_to_be_done = jobs
		self.__jobs_done = []
		self.__max_operations = max_operations
		self.__rgv_config = RGV_config

	
	# 计算RGV移动时耗
	def calculate_RGV_movement_time_cost(self, from_CNC_id, to_CNC_id):
		# CNC ID = 0 则为初始状态
		col_from = CNC_LOCATION_COLOMN[from_CNC_id]
		col_to = CNC_LOCATION_COLOMN[to_CNC_id]
		diff = abs(col_to-col_from)
		if diff == 0:
			return 0
		elif diff ==1:
			return self.__rgv_config.RGV_movement_1_time
		elif diff ==2:
			return self.__rgv_config.RGV_movement_2_time
		elif diff ==3:
			return self.__rgv_config.RGV_movement_3_time

	# 使用启发式运行调度程序
	def run(self, heuristic, verbose=True):
		# 禁用输出若处于静默模式
		if not verbose:
			sys.stdout = None
		current_step = 0
		RGV_pending_time = 0
		previous_machine_id = 1
		while len(self.__jobs_to_be_done) > 0:
			# print("当前步", current_step)
			current_step += 1
			if RGV_pending_time > 0: 
				RGV_pending_time = RGV_pending_time - 1
			else:
				best_candidates = heuristic(self.__jobs_to_be_done, self.__max_operations, current_step)
				for id_machine, candidates in best_candidates.items():
					machine = self.__machines[id_machine - 1]
					for activity, operation in candidates:
						# 运行约束条件 等待RGV 移动、清洗和上下料
						if not (machine.is_working_at_max_capacity() or activity.is_pending):
							machine.add_operation(activity, operation)
							rgv_movement_time_cost = int(self.calculate_RGV_movement_time_cost(previous_machine_id, operation.id_machine))
							# 计算等待RGV延迟时间
							RGV_pending_time = int(self.__rgv_config.RGV_clean_time + machine.install_uninstall_time_cost + rgv_movement_time_cost)
							# print("RGV Pending = ", RGV_pending_time, "step = ", current_step)
							break
					if RGV_pending_time > 0:
						break
						# else:
							# print("等待RGV动作结束 RGV Pending = ", RGV_pending_time)

			for machine in self.__machines:
				machine.work()

			for job in self.__jobs_to_be_done:
				if job.is_done:
					self.__jobs_to_be_done = list(
						filter(lambda element: element.id_job != job.id_job, self.__jobs_to_be_done))
					self.__jobs_done.append(job)
		print(colored("[个体调度初始化]", "cyan"), "新个体在 " + str(current_step) + " 单位时间内完成")

		# 启用输出
		if not verbose:
			sys.stdout = self.__original_stdout

		return current_step
