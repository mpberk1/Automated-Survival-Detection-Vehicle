#Importing Necessary Modules
import requests
from selenium import webdriver
import folium
import datetime
import time

# This method returns the actual coordinates using our IP address
def locationCoordinates():
    try:
        response = requests.get('https://ipinfo.io')
        data = response.json()
        loc = data['loc'].split(',')
        lat, long = float(loc[0]), float(loc[1])
        city = data.get('city', 'Unknown')
        state = data.get('region', 'Unknown')
        return lat, long, city, state
    except:
        # Displaying the error message
        print("Internet Not available")
        # closing the program
        exit()
        return False

# This method fetches our coordinates and creates an HTML file of the map
def gps_locator():
    obj = folium.Map(location=[0, 0], zoom_start=2)
    try:
        lat, long, city, state = locationCoordinates()
        print("You Are in {}, {}".format(city, state))
        print("Your latitude = {} and longitude = {}".format(lat, long))
        folium.Marker([lat, long], popup='Current Location').add_to(obj)
        return True
    except:
        return False

# Main method
if __name__ == "__main__":
    print("---------------GPS Using Python---------------\n")
    page = gps_locator()
