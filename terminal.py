from datetime import datetime

from timezonefinder import TimezoneFinder
from geopy import geocoders
import pytz


def find_tz(lng, lat):
    '''
        Finds timezone info from coordinates
        Input:
            - lng: longitude of terminal
            - lat: latitude of terminal
        Output:
            - tz_info: timezone object based on provided coordinates
    '''
    time_finder = TimezoneFinder()
    tz_name = time_finder.timezone_at(lng=lng, lat=lat)
    tz_info = pytz.timezone(tz_name)
    return tz_info


def find_coord(city_name):
    '''
        Uses web service to calculate terminal coordinates
        from city name.
        Input:
            - city_name: City name from address_struct field
        Output:
            - lng: longitude of city
            - lat: latitude of city
    '''
    geo_code = geocoders.Nominatim(user_agent="terminal_status")
    _, (lat, lng) = geo_code.geocode(city_name)
    return lat, lng


class terminal:
    '''
    Class representing terminal data
    '''
    def __init__(self, init_json):
        '''
        Saves input json data and calls parse_input
        Input:
            init_json: json got from terminal web service
        Output:
            None
        '''
        self.json = init_json
        self.parse_input()

    def parse_input(self):
        '''
        Method to save json data to class variables.
        Requiered values is saved as is. Non-required is saved as None,
        if not found.
        '''
        self.id = self.json['id']
        self.status_code = self.json['status_code'] if 'status_code' in self.json.keys() else None
        self.status = self.json['status'] if 'status' in self.json.keys() else None
        self.address = self.json['address']
        self.address_struct = self.json['address_struct']
        self.name = self.json['name']
        self.type = self.json['type'] if 'type' in self.json.keys() else None
        self.lat = self.json['lat'] if 'lat' in self.json.keys() else None
        self.lng = self.json['lng'] if 'lng' in self.json.keys() else None
        self.working_hours = self.json['working_hours'] if 'working_hours' in self.json.keys() else None

    def get_json(self):
        return self.json

    def get_status(self):
        return self.status

    def get_address_struct(self):
        return self.address_struct

    def get_lat(self):
        return self.lat

    def get_lng(self):
        return self.lng

    def get_working_hours(self):
        return self.working_hours

    def is_working(self):
        '''
        Uses working hours data, city info and coordinates to calculate 
        if terminal is currently working.
        Input:
            None
        Output:
            - -1 in a case of an error
            - 1 if terminal is working
            - 0 if terminal is not working
        '''
        # If there is no working hours data, return error code
        if self.working_hours is None:
            return -1
        # Get current datetime and timezone
        today = datetime.now().astimezone()
        tz_info = today.tzinfo
        # If we dont have info on terminal coordinates, calculate them roughly
        if self.lat is None or self.lng is None:
            try:
                city_name = self.address_struct['city_name']
                self.lat, self.lng = find_coord(city_name)
                tz_info = find_tz(self.lng, self.lat)
            except KeyError:
                # If we dont have any info on terminal location, use local time
                print("Coordinates and city name not found, assuming local time.")
        # Calculate current time in terminal location
        with_timezone = today.astimezone(tz_info)
        # Get working hours data for current day of the week
        weekday_data = next((item for item in self.working_hours if item["dow"] == with_timezone.weekday()), None)
        if weekday_data is None:
            # If terminal is not working on current day of the week at all, return 0
            return 0
        else:
            # If current time is between opening and closing hours, return 1, else - 0
            current_time = with_timezone.time()
            time_open = datetime.strptime(weekday_data['time_open'], '%H:%M').time()
            time_close = datetime.strptime(weekday_data['time_close'], '%H:%M').time()
            if time_open <= current_time < time_close:
                return 1
            else:
                return 0
