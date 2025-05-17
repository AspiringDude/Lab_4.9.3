import requests
import urllib.parse
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from datetime import datetime
import os

# Define API Key
key = "6666ec1d-f81a-4817-a5d2-8f6baedfd725"
route_url = "https://graphhopper.com/api/1/route?"

fuel_efficiency = {"car": 12, "bike": 35, "foot": 0}  # km per liter
fuel_price_per_liter = 65  # PHP or your local currency

# Geocoding function
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

# Get directions function
def get_directions():
    vehicle = vehicle_var.get()
    loc1 = start_entry.get()
    loc2 = end_entry.get()
    user_max_distance = max_distance_entry.get()

    if not loc1 or not loc2:
        messagebox.showerror("Error", "Please enter both locations.")
        return

    try:
        user_max_distance = float(user_max_distance)
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number for max distance.")
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

            if km > user_max_distance:
                messagebox.showwarning("Distance Too Far", f"Trip is {km:.1f} km, exceeds your limit.")
                return

            result = f"Directions from {orig[3]} to {dest[3]} by {vehicle}:\n"
            result += f"Distance: {km:.1f} km / {miles:.1f} miles\n"
            result += f"Duration: {hrs:02d}:{mins:02d}:{sec:02d}\n"

            # Estimated fuel cost
            if fuel_efficiency[vehicle] > 0:
                liters_needed = km / fuel_efficiency[vehicle]
                estimated_cost = liters_needed * fuel_price_per_liter
                result += f"Estimated Fuel Cost: ₱{estimated_cost:.2f}\n"

            result += "\nSteps:\n"
            for step in data["instructions"]:
                dist_km = step["distance"] / 1000
                result += f"- {step['text']} ({dist_km:.1f} km)\n"
            result += "Arrive at destination (0.0 km)"

            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, result)

            # Open Google Maps
            webbrowser.open(f"https://www.google.com/maps/dir/{orig[1]},{orig[2]}/{dest[1]},{dest[2]}/")

            # Log to travel log
            with open("travel_log.txt", "a") as log:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log.write(f"{timestamp}: {orig[3]} to {dest[3]} by {vehicle} - {km:.1f} km, {hrs:02d}:{mins:02d}:{sec:02d}\n")

            # Save to favorites
            with open("favorite_routes.txt", "a") as fav:
                fav.write(f"{loc1},{loc2},{vehicle}\n")
        else:
            messagebox.showerror("Error", "Failed to fetch route data.")
    else:
        messagebox.showerror("Error", "Location not found.")

# Load favorites
def load_favorites():
    if not os.path.exists("favorite_routes.txt"):
        return
    with open("favorite_routes.txt", "r") as fav:
        lines = fav.readlines()
        if lines:
            favorites_menu["values"] = [line.strip() for line in lines[-5:]]

# Use selected favorite

def use_favorite(event):
    selected = favorite_var.get()
    if selected:
        parts = selected.split(",")
        if len(parts) == 3:
            start_entry.delete(0, tk.END)
            start_entry.insert(0, parts[0])
            end_entry.delete(0, tk.END)
            end_entry.insert(0, parts[1])
            vehicle_var.set(parts[2])

# Copy to clipboard
def copy_to_clipboard():
    directions = output_text.get(1.0, tk.END)
    root.clipboard_clear()
    root.clipboard_append(directions)
    messagebox.showinfo("Copied", "Directions copied to clipboard!")

# Clear all fields
def clear_all():
    start_entry.delete(0, tk.END)
    end_entry.delete(0, tk.END)
    max_distance_entry.delete(0, tk.END)
    output_text.delete(1.0, tk.END)

# Tkinter GUI setup
root = tk.Tk()
root.title("GraphHopper Route Finder")
root.geometry("600x600")

tk.Label(root, text="Vehicle:").pack()
vehicle_var = tk.StringVar(value="car")
vehicle_menu = ttk.Combobox(root, textvariable=vehicle_var, values=["car", "bike", "foot"])
vehicle_menu.pack()

tk.Label(root, text="Starting Location:").pack()
start_entry = tk.Entry(root, width=50)
start_entry.pack()

tk.Label(root, text="Destination:").pack()
end_entry = tk.Entry(root, width=50)
end_entry.pack()

tk.Label(root, text="Max Distance (km):").pack()
max_distance_entry = tk.Entry(root, width=50)
max_distance_entry.pack()

tk.Button(root, text="Get Directions", command=get_directions).pack(pady=5)
tk.Button(root, text="Clear All", command=clear_all).pack(pady=5)
tk.Button(root, text="Copy Directions", command=copy_to_clipboard).pack(pady=5)

tk.Label(root, text="Recent Favorite Routes:").pack()
favorite_var = tk.StringVar()
favorites_menu = ttk.Combobox(root, textvariable=favorite_var, postcommand=load_favorites)
favorites_menu.pack()
favorites_menu.bind("<<ComboboxSelected>>", use_favorite)

output_text = tk.Text(root, wrap=tk.WORD)
output_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

root.mainloop()