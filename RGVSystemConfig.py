# RGV参数配置类
class RGVSystemConfig:
    def __init__(self, RGV_clean_time, RGV_movement_1_time, RGV_movement_2_time, RGV_movement_3_time):
        self.__RGV_clean_time = RGV_clean_time
        self.__RGV_movement_1_time = RGV_movement_1_time
        self.__RGV_movement_2_time = RGV_movement_2_time
        self.__RGV_movement_3_time = RGV_movement_3_time
    
    # 清洗耗时
    @property
    def RGV_clean_time(self):
        return self.__RGV_clean_time
    
    # RGV 移动一个单位耗时
    @property
    def RGV_movement_1_time(self):
        return self.__RGV_movement_1_time

    # RGV 移动两个单位耗时
    @property
    def RGV_movement_2_time(self):
        return self.__RGV_movement_2_time

    # RGV 移动三个单位耗时
    @property
    def RGV_movement_3_time(self):
        return self.__RGV_movement_3_time
