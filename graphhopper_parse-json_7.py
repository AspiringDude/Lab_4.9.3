# Group Name: Ahjin
# Facilitator: Cyril Arnoco
# Recorder: Shane Edward Tampus
# Team Member: Juden Baguio
# Team Member: Earl Rosaroso 
# Team Member:  Van Arjay Alcazar

import requests
import urllib.parse
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser


# Define API Key
key = "6666ec1d-f81a-4817-a5d2-8f6baedfd725"
route_url = "https://graphhopper.com/api/1/route?"

def geocoding(location, key):
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
    replydata = requests.get(url)
    json_status = replydata.status_code

    if json_status == 200:
        json_data = replydata.json()
        if "hits" in json_data and len(json_data["hits"]) > 0:
            point = json_data["hits"][0]["point"]
            name = json_data["hits"][0]["name"]
            state = json_data["hits"][0].get("state", "")
            country = json_data["hits"][0].get("country", "")
            location_name = ", ".join(filter(None, [name, state, country]))
            return 200, point["lat"], point["lng"], location_name
    return json_status, "null", "null", location

def get_directions():
    vehicle = vehicle_var.get()
    loc1 = start_entry.get()
    loc2 = end_entry.get()

    if not loc1 or not loc2:
        messagebox.showerror("Error", "Please enter both locations.")
        return

    orig = geocoding(loc1, key)
    dest = geocoding(loc2, key)

    if orig[0] == 200 and dest[0] == 200:
        op = f"&point={orig[1]},{orig[2]}"
        dp = f"&point={dest[1]},{dest[2]}"
        url = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()["paths"][0]
            km = data["distance"] / 1000
            miles = km / 1.61
            sec = int(data["time"] / 1000 % 60)
            mins = int(data["time"] / 1000 / 60 % 60)
            hrs = int(data["time"] / 1000 / 60 / 60)

            result = f"Directions from {orig[3]} to {dest[3]} by {vehicle}:\n"
            result += f"Distance: {km:.1f} km / {miles:.1f} miles\n"
            result += f"Duration: {hrs:02d}:{mins:02d}:{sec:02d}\n\nSteps:\n"

            for step in data["instructions"]:
                dist_km = step["distance"] / 1000
                result += f"- {step['text']} ({dist_km:.1f} km)\n"
            result += "Arrive at destination (0.0 km)"
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, result)

            webbrowser.open(f"https://www.google.com/maps/dir/{orig[1]},{orig[2]}/{dest[1]},{dest[2]}/")

        else:
            messagebox.showerror("Error", "Failed to fetch route data.")
    else:
        messagebox.showerror("Error", "Location not found.")

# Tkinter GUI setup
root = tk.Tk()
root.title("GraphHopper Route Finder")
root.geometry("600x500")

# Vehicle selection first
tk.Label(root, text="Vehicle:").pack()
vehicle_var = tk.StringVar(value="car")
vehicle_menu = ttk.Combobox(root, textvariable=vehicle_var, values=["car", "bike", "foot"])
vehicle_menu.pack()

# Then location inputs
tk.Label(root, text="Starting Location:").pack()
start_entry = tk.Entry(root, width=50)
start_entry.pack()

tk.Label(root, text="Destination:").pack()
end_entry = tk.Entry(root, width=50)
end_entry.pack()

tk.Button(root, text="Get Directions", command=get_directions).pack(pady=10)

output_text = tk.Text(root, wrap=tk.WORD)
output_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

root.mainloop()
