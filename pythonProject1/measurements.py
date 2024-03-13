class Measurements:
    def __int__(self, date, time, category, speed, air_temp, road_temp, wind_speed, la_max, octave):
        self.date = date
        self.time = time
        self.category = category
        self.speed = speed
        self.air_temp = air_temp
        self.road_temp = road_temp
        self.wind_speed = wind_speed
        self.la_max = la_max
        self.octave = octave

    def __str__(self):
        return f"{self.time}, {self.category}, {self.la_max}, {self.speed}, {self.air_temp}"
