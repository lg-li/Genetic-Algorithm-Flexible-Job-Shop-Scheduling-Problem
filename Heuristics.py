class Heuristics:
	# 当可以在多个操作之间进行选择时始终选择第一个操作
	@staticmethod
	def select_first_operation(jobs_to_be_done, max_operations, _):
		best_candidates = {}

		for job in jobs_to_be_done:
			current_activity = job.current_activity
			best_operation = current_activity.shortest_operation

			if best_candidates.get(best_operation.id_machine) is None:
				best_candidates.update({best_operation.id_machine: [(current_activity, best_operation)]})
			elif len(best_candidates.get(best_operation.id_machine)) < max_operations:
				best_candidates.get(best_operation.id_machine).append((current_activity, best_operation))
			else:
				list_operations = best_candidates.get(best_operation.id_machine)

				for key, (_, operation) in enumerate(list_operations):
					if operation.duration < best_operation.duration:
						list_operations.pop(key)
						break

				if len(list_operations) < max_operations:
					list_operations.append((current_activity, best_operation))

		return best_candidates

	# LEPT 规则
	@staticmethod
	def longest_expected_processing_time_first(jobs_to_be_done, max_operations, current_time):
		pass

	# 剩余操作的最短剩余时间
	# S/RO = [(期限时间 - 当前时间) - 总工序完成剩余时间] / 剩余操作数
	@staticmethod
	def shortest_slack_per_remaining_operations(jobs_to_be_done, max_operations, current_time):
		pass

	# 最高临界比例
	# CR = 处理时间 / (期限时间 - 当前时间)
	@staticmethod
	def highest_critical_ratios(jobs_to_be_done, max_operations, current_time):
		best_candidates = {}
		critical_ratios = {}
		assignment = {}

		for job in jobs_to_be_done:
			current_activity = job.current_activity

			# 计算一个作业活动的每一个操作的临界比例
			for operation in current_activity.next_operations:
				critical_ratio = operation.duration / (job.total_shop_time - current_time)
				critical_ratios.update({job.id_job: (current_activity, operation, critical_ratio)})

			for id_job, current_activity, operation, critical_ratio in critical_ratios.items():
				if assignment.get(operation.id_machine) is None:
					assignment.update({operation.id_machine: (current_activity, operation, critical_ratio)})

				elif len(assignment.get(operation.id_machine)) < max_operations:
					list_operations = assignment.get(operation.id_machine)
					list_operations.append((current_activity, operation, critical_ratio))
					best_candidates.update({operation.id_machine: list_operations})

	# TODO: end that

	# 随机分配工件给机床
	@staticmethod
	def random_operation_choice(jobs_to_be_done, max_operations, _):
		import random
		best_candidates = {}
		dict_operations = {}

		for job in jobs_to_be_done:
			current_activity = job.current_activity
			for operation in current_activity.next_operations:
				if dict_operations.get(operation.id_machine) is None:
					dict_operations.update({operation.id_machine: [(current_activity, operation)]})
				else:
					dict_operations.get(operation.id_machine).append((current_activity, operation))

		for machine, list_operations in dict_operations.items():
			best_candidates.update({machine: list(
				set([list_operations[random.randint(0, len(list_operations) - 1)] for _ in range(max_operations)]))})

		return best_candidates

	## 创建机器分配和操作顺序列表（待改进）
	@staticmethod
	def initialisation_list(jobs_to_be_done):
		machine_assignment = []
		operation_sequence = []
		for job in jobs_to_be_done:
			for activity in job.activities_to_be_done:
				operation_sequence.append(job.id_job)
				machine_assignment.append(activity.next_operations[0].id_machine)
		print("已分配的机器 :")
		for machine in machine_assignment:
			print(str(machine))
		print("工序操作序列 :")
		for operation in operation_sequence:
			print(operation)
