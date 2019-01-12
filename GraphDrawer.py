# 甘特图绘图类
import os
import random

class GraphDrawer:
	@staticmethod
	def draw_schedule(number_machines, max_operations, jobs, filename=None):
		import matplotlib.pyplot as plt
		import matplotlib.patches as patches
		plt.rcParams['font.sans-serif'] = ['Microsoft YaHei '] # 指定图像默认字体 解决图例中文不识别之问题
		plt.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题
		# 操作条状图间的垂直距离
		operation_vertical_space = 1
		# 操作条状图高度
		operation_vertical_height = 2
		# 以machine id为索引 已完成的操作dict
		operations_done = {}
		for job in jobs:
			for activity in job.activities_done:
				# 添加所有操作
				operation = activity.operation_done
				# 初始化list（若首次添加到machine对象）
				if operations_done.get(operation.id_machine) is None:
					list_operations = []
				# 非首次添加直接获取已有的list
				else:
					list_operations = operations_done.get(operation.id_machine)

				# 以JobID和ActivityID为标识符新添一条记录
				list_operations.append((job.id_job, activity.id_activity, operation))
				# 更新字典
				operations_done.update({operation.id_machine: list_operations})

		# 生成随机颜色块用于显示不同物料对应工序的颜色条
		colors = ['#%06X' % random.randint(0, 256 ** 3 - 1) for _ in range(len(jobs))]
		# 画图
		plt.clf()
		plot = plt.subplot()
		for id_machine, list_operations in operations_done.items():
			for id_job, id_activity, operation in list_operations:
				# X 坐标对应操作时间，Y 坐标对应操作顺序
				x, y = operation.time, 1 + id_machine * max_operations * (
						operation_vertical_space + operation_vertical_height) + operation.place_of_arrival * (
							   operation_vertical_space + operation_vertical_height)
				# 根据 operation 时间长度绘制矩形
				if operation.id_operation == -1: # 故障黑块绘制
					plot.add_patch(
					patches.Rectangle(
						(x, y-1),
						operation.duration,
						operation_vertical_height+2,
						facecolor='#000000'
						)
					)
				else:
					plot.add_patch(
						patches.Rectangle(
							(x, y),
							operation.duration,
							operation_vertical_height,
							facecolor=colors[id_job - 1]
						)
					)

		# 以机器数量调整Y轴高度
		plt.yticks([1 + (i + 1) * max_operations * (operation_vertical_space + operation_vertical_height) + (
				max_operations * (operation_vertical_height + operation_vertical_space) - operation_vertical_space) / 2 for i in
					range(number_machines)], ["CNC" + str(i + 1) + "#" for i in range(number_machines)])
		# 自动缩放
		plot.autoscale()

		# 绘制JOB ID对应的图例
		handles = []
		handles.append(patches.Patch(color="#000000", label='Failure'))
		for id_job, color in enumerate(colors):
			handles.append(patches.Patch(color=color, label='Item' + str(id_job + 1)))
		plt.legend(handles=handles)

		print("图像已在新窗口打开，关闭图形窗口可继续")

		# 显示绘图
		plt.show()
		if not (filename is None):
			plt.savefig(os.path.join("output", filename), bbox_inches='tight')
			print("图像已保存")
