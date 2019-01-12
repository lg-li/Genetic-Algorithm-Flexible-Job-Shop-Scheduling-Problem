# 物料工件模拟类
class Job:
	def __init__(self, id_job):
		self.__id_job = id_job
		self.__activities_to_be_done = []
		self.__activities_done = []

	# toString 方法
	def __str__(self):
		output = "工件所属流程概述：\n"
		for activity in self.__activities_to_be_done:
			output += str(activity) + "\n"
		for activity in self.__activities_done:
			output += str(activity) + "\n"
		return output

	# 物料 ID
	@property
	def id_job(self):
		return self.__id_job

	# 物料是否为熟料(是否加工完成)
	@property
	def is_done(self):
		return len(self.activities_to_be_done) == 0
	
	# 添加活动到此物料
	def add_activity(self, activity):
		self.__activities_to_be_done.append(activity)
	
	# 此物料已完成的活动工序
	@property
	def activities_done(self):
		return self.__activities_done

	# 此物料需要进行的活动工序
	@property
	def activities_to_be_done(self):
		return self.__activities_to_be_done

	# 通知对象 其以完成加工
	def activity_is_done(self, activity):
		if not activity.is_done:
			raise EnvironmentError("This activity is not done")
		self.__activities_to_be_done = list(
			filter(lambda element: element.id_activity != activity.id_activity, self.__activities_to_be_done))
		self.__activities_done.append(activity)

	# 返回当前需要处理的活动
	@property
	def current_activity(self):
		if len(self.activities_to_be_done) == 0:
			raise EnvironmentError("All activities are already done")
		return self.__activities_to_be_done[0]

	@property
	def remaining_shop_time(self):
		return sum(map(lambda activity: activity.shop_time, self.activities_to_be_done))

	@property
	def total_shop_time(self):
		return sum(map(lambda activity: activity.shop_time, self.activities_to_be_done + self.activities_done))

	def check_if_previous_activity_is_done(self, activity_id):
		if activity_id == 1:
			return True
		for activity in self.__activities_done:
			if activity.id_activity == activity_id - 1:
				return True
		return False

	def get_activity(self, id_activity):
		for activity in self.__activities_to_be_done:
			if activity.id_activity == id_activity:
				return activity
