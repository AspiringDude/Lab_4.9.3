import requests
import urllib.parse
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
from datetime import datetime
import os
import matplotlib.pyplot as plt

# Define API Key
key = "6666ec1d-f81a-4817-a5d2-8f6baedfd725"
route_url = "https://graphhopper.com/api/1/route?"

fuel_efficiency = {"car": 12, "bike": 35, "foot": 0}
fuel_price_per_liter = 65

# Geocoding function
def geocoding(location, key):
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
    replydata = requests.get(url)
    if replydata.status_code == 200:
        json_data = replydata.json()
        if "hits" in json_data and len(json_data["hits"]) > 0:
            point = json_data["hits"][0]["point"]
            name = json_data["hits"][0]["name"]
            state = json_data["hits"][0].get("state", "")
            country = json_data["hits"][0].get("country", "")
            location_name = ", ".join(filter(None, [name, state, country]))
            return 200, point["lat"], point["lng"], location_name
    return replydata.status_code, "null", "null", location

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
            sec = int(data["time"] / 1000 % 60)
            mins = int(data["time"] / 1000 / 60 % 60)
            hrs = int(data["time"] / 1000 / 60 / 60)

            if km > user_max_distance:
                messagebox.showwarning("Distance Too Far", f"Trip is {km:.1f} km, exceeds your limit.")
                return

            result = f"Directions from {orig[3]} to {dest[3]} by {vehicle}:\n"
            result += f"Distance: {km:.1f} km\nDuration: {hrs:02d}:{mins:02d}:{sec:02d}\n"

            if fuel_efficiency[vehicle] > 0:
                liters_needed = km / fuel_efficiency[vehicle]
                estimated_cost = liters_needed * fuel_price_per_liter
                result += f"Estimated Fuel Cost: ₱{estimated_cost:.2f}\n"
            else:
                estimated_cost = 0

            result += "\nSteps:\n"
            for step in data["instructions"]:
                dist_km = step["distance"] / 1000
                result += f"- {step['text']} ({dist_km:.1f} km)\n"
            result += "Arrive at destination (0.0 km)"

            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, result)

            webbrowser.open(f"https://www.google.com/maps/dir/{orig[1]},{orig[2]}/{dest[1]},{dest[2]}/")

            with open("travel_log.txt", "a") as log:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log.write(f"{timestamp},{orig[3]},{dest[3]},{vehicle},{km:.1f},{estimated_cost:.2f}\n")

            with open("favorite_routes.txt", "a") as fav:
                fav.write(f"{loc1},{loc2},{vehicle}\n")
        else:
            messagebox.showerror("Error", "Failed to fetch route data.")
    else:
        messagebox.showerror("Error", "Location not found.")

# View fuel summary chart
def view_summary_chart():
    if not os.path.exists("travel_log.txt"):
        messagebox.showerror("Error", "No travel log found.")
        return

    dates = []
    costs = []
    with open("travel_log.txt") as log:
        for line in log:
            try:
                parts = line.strip().split(',')
                date = parts[0].split()[0]
                cost = float(parts[-1])
                dates.append(date)
                costs.append(cost)
            except:
                continue

    if not dates:
        messagebox.showinfo("Info", "No cost data to show.")
        return

    plt.figure(figsize=(8, 4))
    plt.bar(dates, costs, color='teal')
    plt.xticks(rotation=45)
    plt.title("Fuel Cost Summary by Date")
    plt.ylabel("PHP")
    plt.tight_layout()
    plt.show()

# View route history
def view_route_history():
    if not os.path.exists("travel_log.txt"):
        messagebox.showerror("Error", "No travel log found.")
        return

    with open("travel_log.txt") as log:
        history = log.read()

    if history:
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "Route History:\n" + history)
    else:
        messagebox.showinfo("Info", "No route history available.")

# GUI setup
root = tk.Tk()
root.title("GraphHopper Route Finder")
root.geometry("650x650")

vehicle_var = tk.StringVar(value="car")

widgets = [
    ("Vehicle:", ttk.Combobox, {"textvariable": vehicle_var, "values": ["car", "bike", "foot"]}),
    ("Starting Location:", tk.Entry, {}),
    ("Destination:", tk.Entry, {}),
    ("Max Distance (km):", tk.Entry, {})
]

entries = []
for label, widget_type, opts in widgets:
    tk.Label(root, text=label).pack()
    w = widget_type(root, **opts)
    w.pack()
    entries.append(w)

vehicle_menu, start_entry, end_entry, max_distance_entry = entries

button_opts = [
    ("Get Directions", get_directions),
    ("Clear All", lambda: [e.delete(0, tk.END) for e in [start_entry, end_entry, max_distance_entry]] + [output_text.delete(1.0, tk.END)]),
    ("Copy Directions", lambda: [root.clipboard_clear(), root.clipboard_append(output_text.get(1.0, tk.END)), messagebox.showinfo("Copied", "Copied to clipboard!")]),
    ("View Route History", view_route_history),
    ("View Fuel Summary Chart", view_summary_chart)
]

for label, cmd in button_opts:
    tk.Button(root, text=label, command=cmd).pack(pady=2)

favorite_var = tk.StringVar()
tk.Label(root, text="Recent Favorite Routes:").pack()
favorites_menu = ttk.Combobox(root, textvariable=favorite_var, postcommand=lambda: load_favorites())
favorites_menu.pack()
favorites_menu.bind("<<ComboboxSelected>>", lambda e: use_favorite())

output_text = tk.Text(root, wrap=tk.WORD)
output_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

def load_favorites():
    if os.path.exists("favorite_routes.txt"):
        with open("favorite_routes.txt") as fav:
            lines = fav.readlines()
            if lines:
                favorites_menu["values"] = [line.strip() for line in lines[-5:]]

def use_favorite():
    selected = favorite_var.get()
    if selected:
        parts = selected.split(",")
        if len(parts) == 3:
            start_entry.delete(0, tk.END)
            start_entry.insert(0, parts[0])
            end_entry.delete(0, tk.END)
            end_entry.insert(0, parts[1])
            vehicle_var.set(parts[2])

root.mainloop()
