from calendar import monthrange
from datetime import datetime
from operator import attrgetter
import random
import data


class Generator:

    def __init__(self,
                 desinations: data.DestinationRepository,
                 refuelings: data.RefuelingRepository,
                 trips: data.TripsRepository,
                 previous_milage: int,
                 current_milage: int, start_date: datetime,
                 settings: dict) -> None:
        self.destinations = desinations
        self.refuelings = refuelings
        self.trips = trips
        self.previous_milage = previous_milage
        self.current_milage = current_milage
        self.month = int(start_date.strftime("%m"))
        self.year = int(start_date.strftime("%Y"))
        self.settings = settings

    def rewrite_refuelings(self):
        trips_list = []
        used_range = 0
        for refueling in self.refuelings:
            date = int(refueling.date.strftime("%m"))
            if date == self.month:
                trip = data.Trip(
                    id=0,
                    date=refueling.date,
                    destination=refueling.destination,
                    milage=refueling.destination.distance
                ) 
                trips_list.append(trip)
                used_range += trip.milage
        return trips_list, used_range

    def generate_random_date(self):
        days_in_month = monthrange(self.year, self.month)[1]
        random_day = random.randrange(1, days_in_month)
        random_date = datetime.strptime(
                f'{self.year}/{self.month}/{random_day}', "%Y/%m/%d"
                )
        return random_date

    def generate(self):
        range = self.current_milage - self.previous_milage
        iteration = 0
        while True:
            trips_list, used_range = self.rewrite_refuelings()        
            current_day_iterations = 0
            while used_range < range:
                if current_day_iterations < self.settings["day_iteration"]:
                    random_date = self.generate_random_date()
                    if not any(True for trip in trips_list if trip.date == random_date):
                        current_trip_iterations = 0
                        while True:
                            if current_trip_iterations < self.settings['trip_iteration']:
                                if range - used_range > self.settings['max_difference']:
                                    start_index = 1
                                    stop_index = self.settings['factor']
                                else:
                                    start_index = self.settings['factor']
                                    stop_index = len(self.destinations.elements_list)-1
                                random_destination = self.destinations.elements_list[random.randrange(start_index, stop_index)]
                                random_trip = data.Trip(0, random_date, random_destination, milage=random_destination.distance)
                                trips_list.append(random_trip)
                                used_range = used_range + float(random_trip.milage)
                                current_trip_iterations += 1
                                break
                            else:
                                break
                    current_day_iterations += 1
                else:
                    break
            if range - used_range <= self.settings['max_difference']:
                break
            else:
                iteration += 1
        sorted(trips_list, key=attrgetter('date')), iteration
        return self.recalculate_milage(trips_list)

    def recalculate_milage(self, trips_list):
        last_mialge = self.previous_milage
        for trip in trips_list:
            trip.milage += last_mialge
            last_mialge = trip.milage
        return trips_list


def main():
    pass

if __name__ == "__main__":
    main()
