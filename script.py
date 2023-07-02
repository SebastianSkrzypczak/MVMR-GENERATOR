from collections import namedtuple
from calendar import monthrange
import random
from operator import attrgetter
from datetime import datetime
from tabulate import tabulate



def dest(destinations): # A function to read data from .txt file and store it in destination list
    dest_tuple = namedtuple( #creating a namedtuple to store data in fixed order
        'destination',
        ['name', 'location', 'distance']
    )
    dest_list = [] #creating a list to store all of dest_tuple objects
    for line in destinations:
        line = line[:-1]  #deleting "/n" 
        separated = line.split("	")
        temp_line = dest_tuple(separated[1], separated[2], separated[3])
        dest_list.append(temp_line) 
    del dest_list[0]
    return dest_list


def fuel(refuelings): # A function to store all refuelings 
    fuel_tuple = namedtuple( # creating a namedtuple to store all informations about refuleing in fixed order
        'refueling',
        ['date', 'volume', 'name']
    )
    fuel_list = [] # a list to store all of fuel_tuple objects
    for line in refuelings:
        line = line[:-1]  # deleting "/n" 
        separated = line.split("	")
        temp_line = fuel_tuple(separated[0], separated[1], separated[2])
        fuel_list.append(temp_line) 
    return sorted(fuel_list, key=attrgetter('date'))

def recalculate(trips_list, prev_milage):
    trips_tuple = namedtuple(
        'trip',
        ['date', 'name', 'distance', 'location', 'milage_now']
    )
    last = prev_milage
    trip_recalc = []
    for trip in trips_list:
        date = trip.date
        name = trip.name
        distance = trip.distance
        location = trip.location
        milage_now = str(last + int(distance))
        last = last + int(distance)
        temp = trips_tuple(date, name, distance, location, milage_now)
        trip_recalc.append(temp)
    return trip_recalc

def trips(dest_list, fuel_list, prev_milage, current_milage, month, year, free_days): # A function to generate list of all trips in given month
    trips_tuple = namedtuple(
        'trip',
        ['date', 'name', 'distance', 'location', 'milage_now']
    )
    month_range = current_milage - prev_milage 
    days = monthrange(year, month)[1] # How many days in given month
    if month < 10:
        month = "0" + str(month)
    else:
        month = str(month)
    iteration = 0
    while(True):
        used_range = 0
        trips_list = []
        for fuel_tuple in fuel_list:
            fuel_name = fuel_tuple.name
            try:
                temp_destination = (dest for dest in dest_list if dest.name == fuel_name)
                next_destination = next(temp_destination)
                temp_name = next_destination.name
                temp_distance = next_destination.distance
                temp_location = next_destination.location
                temp = trips_tuple(
                    fuel_tuple.date,
                    temp_name,
                    temp_distance,
                    temp_location,
                    "0"
                )
                trips_list.append(temp)
            except StopIteration:
                continue
        day_iteration = 0  # safety variable to avoid too long looping
        while(used_range < month_range):
            if day_iteration < 30:
                random_day = random.randrange(1, days) # generating random day in range from 1 to days of given month
                if random_day < 10:
                    random_date = ('0' + str(random_day) + '.' + str(month) + '.' + str(year))
                else:
                    random_date = (str(random_day) + '.' + str(month) + '.' + str(year))
                if (not any([True for trip in trips_list if trip.date == random_date]) and # checking if generated day is allredy used in refueling 
                    not any([True for days in free_days if days == random_date])):  # checking if generated day is a free day
                    trip_iteration = 0 # safety variable to avoid too long looping
                    while(True):        
                        if trip_iteration < 30:
                            if ( month_range - used_range ) > 70:  # factor determining which trips should be taken first
                                factor_1 = 1
                                factor_2 = 15
                            else:
                                factor_1 = 15
                                factor_2 = len(dest_list)-1
                            random_destination = dest_list[random.randrange(factor_1, factor_2)] # picking random destionation from dest_list
                            if used_range + int(random_destination.distance) < month_range: 
                                ran_day_trip = trips_tuple(random_date, random_destination.name, str(random_destination.distance), random_destination.location, "0")
                                trips_list.append(ran_day_trip)
                                used_range = used_range + int(random_destination.distance)
                                trip_iteration += 1 
                                break 
                            else:
                                break                       
                        else:
                            break
                day_iteration += 1
            else:
                break
        if month_range - used_range <= 30: #if difference is greater than ... script should start again.
            break
        else:
            iteration += 1 
    trips_sorted = sorted(trips_list, key=attrgetter('date'))
    return(recalculate(trips_sorted, prev_milage), used_range, iteration)


def open_with_error_check(file_name):
    try:
        file = open("DESTINATIONS.TXT", "r", encoding="utf8")
    except FileNotFoundError:
        print(f'File {file_name} not found')
        return False
    except IOError:
        print(f'Error reading the {file_name} file')
        return False
    return file

def get_milage(prev_milage, message):
    while True:
        try:
            milage = int(input(f'Type milage from {message} month: ')) # 249897
            if milage <= 0:
                raise ValueError("Input must be a positive integer")
            if milage <= prev_milage:
                raise ValueError("Input must be larger that previous milage")
            return milage
        except TypeError as error:
            print(f'Type error: {error}')  
        except ValueError as error:
            print(f'Value error: {error}')


def main():
    prev_milage = get_milage(0, 'previous')
    current_milage = get_milage(prev_milage, 'current')
    destinations = open_with_error_check("DESTINATIONS.txt")
    refuelings = open_with_error_check("REFUELINGS.txt")
    dest_list = dest(destinations)
    fuel_list = fuel(refuelings)
    month = 4
    year = 2023
    trips_, range_, iteration_ = trips(
        dest_list,
        fuel_list,
        prev_milage,
        current_milage,
        month, year,
        free_days=[]
        )
    print(tabulate(
        trips_, 
        headers=["DATE", "NAME", "DISTANCE", "LOCATION", "MILAGE"],
        tablefmt="grid"
        ))
    print(f'range {range_}')
    print(f'iteration {iteration_}')
    destinations.close()
    refuelings.close()


if __name__ == "__main__":
    main()