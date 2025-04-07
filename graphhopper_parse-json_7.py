import requests
import urllib.parse

# Define API Key
key = "6666ec1d-f81a-4817-a5d2-8f6baedfd725"  # Replace with your API key
route_url = "https://graphhopper.com/api/1/route?"

# Define Geocoding Function
def geocoding(location, key):
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
    
    replydata = requests.get(url)
    json_status = replydata.status_code

    if json_status == 200:
        json_data = replydata.json()
        if "hits" in json_data and len(json_data["hits"]) > 0:
            lat = json_data["hits"][0]["point"]["lat"]
            lng = json_data["hits"][0]["point"]["lng"]
            name = json_data["hits"][0]["name"]
            value = json_data["hits"][0]["osm_value"]

            country = json_data["hits"][0].get("country", "")
            state = json_data["hits"][0].get("state", "")

            if state and country:
                new_loc = f"{name}, {state}, {country}"
            elif state:
                new_loc = f"{name}, {state}"
            elif country:
                new_loc = f"{name}, {country}"
            else:
                new_loc = name
            
            print(f"Geocoding API URL for {new_loc} (Location Type: {value})\n{url}")
            return json_status, lat, lng, new_loc
        else:
            print(f"No results found for {location}.")
            return json_status, "null", "null", location
    else:
        print(f"Error: Unable to fetch data for {location}.")
        return json_status, "null", "null", location

# Loop for user input
while True:
    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Vehicle profiles available on Graphhopper:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("car, bike, foot")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    
    # List of valid profiles
    profile = ["car", "bike", "foot"]
    
    # Get user input for vehicle profile
    vehicle = input("Enter a vehicle profile from the list above: ")
    
    # Check for 'quit' or 'q' to break the loop
    if vehicle == "quit" or vehicle == "q":
        break
    
    # Validate the vehicle input
    if vehicle in profile:
        vehicle = vehicle  # Valid input, assign to variable
    else:
        vehicle = "car"  # Default to "car" if invalid input
        print("No valid vehicle profile was entered. Using the car profile.")
    
    loc1 = input("Starting Location: ")
    while not loc1.strip():
        loc1 = input("Enter the location again: ")
    if loc1.lower() in ["q", "quit"]:
        break  # Exit program if user enters 'q' or 'quit'

    orig = geocoding(loc1, key)

    loc2 = input("Destination: ")
    while not loc2.strip():
        loc2 = input("Enter the location again: ")
    if loc2.lower() in ["q", "quit"]:
        break  # Exit program if user enters 'q' or 'quit'

    dest = geocoding(loc2, key)
    
    print("=================================================")
    if orig[0] == 200 and dest[0] == 200:
        op = "&point=" + str(orig[1]) + "%2C" + str(orig[2])
        dp = "&point=" + str(dest[1]) + "%2C" + str(dest[2])
        
        # Update the paths_url to include the vehicle type
        paths_url = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp
        
        # Make the request to GraphHopper
        paths_response = requests.get(paths_url)
        paths_status = paths_response.status_code
        paths_data = paths_response.json()
        
        print("Routing API Status: " + str(paths_status) + "\nRouting API URL:\n" + paths_url)
        print("=================================================")
        
        # Update the print statement with the vehicle type
        print(f"Directions from {orig[3]} to {dest[3]} by {vehicle}")
        print("=================================================")
        
        if paths_status == 200:
            miles = (paths_data["paths"][0]["distance"]) / 1000 / 1.61
            km = (paths_data["paths"][0]["distance"]) / 1000
            sec = int(paths_data["paths"][0]["time"] / 1000 % 60)
            min = int(paths_data["paths"][0]["time"] / 1000 / 60 % 60)
            hr = int(paths_data["paths"][0]["time"] / 1000 / 60 / 60)
            
            print(f"Distance Traveled: {miles:.1f} miles / {km:.1f} km")
            print(f"Trip Duration: {hr:02d}:{min:02d}:{sec:02d}")
            print("=================================================")

            for each in range(len(paths_data["paths"][0]["instructions"])):
                path = paths_data["paths"][0]["instructions"][each]["text"]
                distance = paths_data["paths"][0]["instructions"][each]["distance"]
                print(f"{path} ( {distance / 1000:.1f} km / {distance / 1000 / 1.61:.1f} miles )")
            
            print("Arrive at destination ( 0.0 km / 0.0 miles )")
            print("=================================================")
