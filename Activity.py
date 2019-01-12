class Activity:
    def __init__(self, job, id_activity):
        self.__job = job
        self.__id_activity = id_activity
        self.__operations_to_be_done = []
        self.__operation_done = None

    # toString 方法
    def __str__(self):
        stringToReturn = "工件" + \
            str(self.id_job) + " [所属活动" + \
            str(self.__id_activity) + "]\n 待完成工序操作顺序\n"
        for operation in self.__operations_to_be_done:
            stringToReturn += str(operation) + "\n"
        stringToReturn += "已完成的工序操作：\n" + str(self.__operation_done) + "\n"
        return stringToReturn

    @property
    def shop_time(self):
        return self.operation_done.duration if self.is_done else max(self.__operations_to_be_done, key=lambda operation: operation.duration)

    @property
    def is_feasible(self):
        return self.__job.check_if_previous_activity_is_done(self.__id_activity)

    @property
    def is_pending(self):
        return len(list(filter(lambda element: element.is_pending, self.__operations_to_be_done))) > 0

    # 当前活动流对应的工件ID
    @property
    def id_job(self):
        return self.__job.id_job

    # 返回活动工序ID
    @property
    def id_activity(self):
        return self.__id_activity

    # 往活动添加待进行操作工序
    def add_operation(self, operation):
        self.__operations_to_be_done.append(operation)

    # 是否已完成此工件的加工
    @property
    def is_done(self):
        return not (self.__operation_done is None)

    # 返回待完成操作
    @property
    def next_operations(self):
        return self.__operations_to_be_done

    # 返回运行可能的最短工序顺序
    @property
    def shortest_operation(self):
        candidate_operation = None
        for operation in self.__operations_to_be_done:
            if candidate_operation is None or operation.duration < candidate_operation.duration:
                candidate_operation = operation
        return operation
    
    # 返回待完成的工序操作
    @property
    def operations_to_be_done(self):
        return self.__operations_to_be_done
    
    # 返回已完成的工序操作
    @property
    def operation_done(self):
        return self.__operation_done

    # 强行完成并终止一个操作
    def terminate_operation(self, operation):
        # 从待完成工序中删除
        self.__operations_to_be_done = list(
            filter(lambda element: element.id_operation != operation.id_operation, self.__operations_to_be_done))
        # 加入已完成工序
        self.__operation_done = operation
        self.__job.activity_is_done(self)

    def get_operation(self, id_operation):
        for operation in self.__operations_to_be_done:
            if operation.id_operation == id_operation:
                return operation
                