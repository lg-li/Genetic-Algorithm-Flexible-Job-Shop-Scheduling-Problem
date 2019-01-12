# 工序操作模拟类
class Operation:
	def __init__(self, id_operation, id_machine, duration):
		self.__id_operation = id_operation
		self.__duration = duration
		self.__id_machine = id_machine
		self.__time = None
		self.__is_pending = False
		self.__place_of_arrival = None

	# toString 方法
	def __str__(self):
		output = "操作" + str(self.__id_operation) + " [由CNC机器" + str(
			self.__id_machine) + "#处理]  耗时" + str(self.__duration) + "(单位时间)"
		if not (self.__time is None):
			output += ", 此操作作业开始于 " + str(self.__time)
		return output

	# 操作ID
	@property
	def id_operation(self):
		return self.__id_operation

	# 是否完成
	def is_done(self, t):
		return not (self.__time is None) and self.__time + self.__duration <= t

	# 是否等待
	@property
	def is_pending(self):
		return self.__is_pending

	# 设置等待状态
	@is_pending.setter
	def is_pending(self, value):
		self.__is_pending = value

	# 返回将被分配用于处理此操作的CNC机器ID
	@property
	def place_of_arrival(self):
		return self.__place_of_arrival

	# 设置用于处理此操作的CNC机器ID
	@place_of_arrival.setter
	def place_of_arrival(self, value):
		self.__place_of_arrival = value

	# 对应CNC机器ID
	@property
	def id_machine(self):
		return self.__id_machine

	# 操作耗时
	@property
	def duration(self):
		return self.__duration

	# 获取操作开始时间
	@property
	def time(self):
		return self.__time

	# 设置操作开始时间
	@time.setter
	def time(self, value):
		if value < 0:
			raise ValueError("[错误] 起始时间不可小于零")
		self.__time = value
