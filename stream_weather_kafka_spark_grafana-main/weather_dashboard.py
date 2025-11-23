import tkinter as tk
from tkinter import ttk, messagebox
from flask import Flask, render_template, jsonify
import json
import threading
import time
from kafka import KafkaConsumer
from collections import defaultdict, deque
from datetime import datetime

app = Flask(__name__)

# Global data storage
weather_data_store = defaultdict(dict)
recent_data = deque(maxlen=50)  # Store recent data points for charts
cities_data = defaultdict(dict)  # Store data by city

# Kafka consumer thread
def consume_kafka_data():
    """Consume weather data from Kafka and update global storage"""
    try:
        consumer = KafkaConsumer(
            'weather_topic',
            bootstrap_servers=['127.0.0.1:9093'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='weather-dashboard-group-flask',
            api_version=(0, 10, 1)
        )
        
        print("Kafka consumer started, listening for weather data...")
        
        for message in consumer:
            try:
                data = message.value
                
                # Extract city information
                city_name = data.get('name', 'Unknown')
                if not city_name or city_name == 'Unknown':
                    # Use coordinates if name is not available
                    city_name = f"{data['coord']['lat']:.2f},{data['coord']['lon']:.2f}"
                
                # Convert temperature from Kelvin to Celsius
                temp_celsius = data['main']['temp'] - 273.15
                
                # Process weather data
                weather_info = {
                    'city': city_name,
                    'temperature': round(temp_celsius, 1),
                    'feels_like': round(data['main'].get('feels_like', temp_celsius) - 273.15, 1),
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'description': data['weather'][0]['description'].title(),
                    'main_condition': data['weather'][0]['main'],
                    'wind_speed': data.get('wind', {}).get('speed', 0),
                    'wind_direction': data.get('wind', {}).get('deg', 0),
                    'visibility': data.get('visibility', 0) / 1000,  # Convert to km
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'clouds': data.get('clouds', {}).get('all', 0),
                    'rain_1h': data.get('rain', {}).get('1h', 0),
                    'snow_1h': data.get('snow', {}).get('1h', 0)
                }
                
                # Update global storage
                weather_data_store[city_name] = weather_info
                recent_data.append(weather_info)
                cities_data[city_name] = weather_info
                
                print(f"Updated data for {city_name}: {weather_info['temperature']}°C, {weather_info['description']}")
                
            except Exception as e:
                print(f"Error processing message: {e}")
                continue
                
    except Exception as e:
        print(f"Error in Kafka consumer: {e}")

# Start Kafka consumer in background thread
consumer_thread = threading.Thread(target=consume_kafka_data, daemon=True)
consumer_thread.start()

@app.route('/')
def dashboard():
    """Render the main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/current')
def current_weather():
    """API endpoint to get current weather data"""
    # Return the most recent data for all cities
    return jsonify(dict(weather_data_store))

@app.route('/api/recent')
def recent_weather():
    """API endpoint to get recent weather data for charts"""
    return jsonify(list(recent_data))

@app.route('/api/cities')
def cities_list():
    """API endpoint to get list of monitored cities"""
    return jsonify(list(cities_data.keys()))

@app.route('/api/city/<city_name>')
def city_weather(city_name):
    """API endpoint to get weather data for a specific city"""
    if city_name in weather_data_store:
        return jsonify(weather_data_store[city_name])
    else:
        return jsonify({'error': 'City not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

class WeatherDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Weather Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')
        
        # Data storage
        self.weather_data = {}
        self.cities = []
        self.temperature_data = {}
        self.humidity_data = {}
        
        # For real-time charts
        self.max_data_points = 20
        self.temperature_history = {}
        self.humidity_history = {}
        self.pressure_history = {}
        self.wind_speed_history = {}
        
        # Kafka consumer
        self.consumer = None
        self.consumer_thread = None
        
        # Create the UI
        self.create_widgets()
        
        # Start data update thread
        self.stop_event = threading.Event()
        self.data_thread = threading.Thread(target=self.update_data, daemon=True)
        self.data_thread.start()
        
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#34495e', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="Real-Time Weather Dashboard", 
            font=("Arial", 24, "bold"), 
            bg='#34495e', 
            fg='white'
        )
        title_label.pack(pady=20)
        
        # Controls frame
        controls_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        controls_frame.pack_propagate(False)
        
        tk.Label(
            controls_frame, 
            text="City:", 
            font=("Arial", 12), 
            bg='#2c3e50', 
            fg='white'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.city_entry = tk.Entry(controls_frame, font=("Arial", 12), width=20)
        self.city_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        add_button = tk.Button(
            controls_frame, 
            text="Add City", 
            command=self.add_city,
            font=("Arial", 12),
            bg='#27ae60',
            fg='white',
            relief=tk.FLAT,
            padx=20
        )
        add_button.pack(side=tk.LEFT)
        
        # Status label
        self.status_label = tk.Label(
            controls_frame,
            text="Status: Connecting to Kafka...",
            font=("Arial", 10),
            bg='#2c3e50',
            fg='yellow'
        )
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg='#2c3e50')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Left panel - City list and details
        left_frame = tk.Frame(content_frame, bg='#34495e', width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        tk.Label(
            left_frame, 
            text="Monitored Cities", 
            font=("Arial", 16, "bold"), 
            bg='#34495e', 
            fg='white'
        ).pack(pady=10)
        
        # City listbox with scrollbar
        list_frame = tk.Frame(left_frame, bg='#34495e')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.city_listbox = tk.Listbox(
            list_frame, 
            font=("Arial", 12),
            bg='#2c3e50',
            fg='white',
            selectbackground='#3498db'
        )
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.city_listbox.yview)
        self.city_listbox.config(yscrollcommand=scrollbar.set)
        
        self.city_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # City details frame
        self.details_frame = tk.Frame(left_frame, bg='#34495e')
        self.details_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.details_label = tk.Label(
            self.details_frame,
            text="Select a city to view details",
            font=("Arial", 12),
            bg='#34495e',
            fg='white',
            wraplength=280,
            justify=tk.LEFT
        )
        self.details_label.pack()
        
        # Right panel - Charts and data
        right_frame = tk.Frame(content_frame, bg='#2c3e50')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Temperature tab
        self.temp_frame = tk.Frame(self.notebook, bg='#2c3e50')
        self.notebook.add(self.temp_frame, text="Temperature")
        self.create_temperature_chart()
        
        # Humidity tab
        self.humidity_frame = tk.Frame(self.notebook, bg='#2c3e50')
        self.notebook.add(self.humidity_frame, text="Humidity")
        self.create_humidity_chart()
        
        # Pressure tab
        self.pressure_frame = tk.Frame(self.notebook, bg='#2c3e50')
        self.notebook.add(self.pressure_frame, text="Pressure")
        self.create_pressure_chart()
        
        # Wind Speed tab
        self.wind_frame = tk.Frame(self.notebook, bg='#2c3e50')
        self.notebook.add(self.wind_frame, text="Wind Speed")
        self.create_wind_chart()
        
        # Alerts tab
        self.alerts_frame = tk.Frame(self.notebook, bg='#2c3e50')
        self.notebook.add(self.alerts_frame, text="Alerts")
        self.create_alerts_tab()
        
    def create_temperature_chart(self):
        self.temp_fig = Figure(figsize=(8, 4), dpi=100, facecolor='#2c3e50')
        self.temp_ax = self.temp_fig.add_subplot(111)
        self.temp_ax.set_facecolor('#2c3e50')
        self.temp_ax.tick_params(colors='white')
        self.temp_ax.spines['bottom'].set_color('white')
        self.temp_ax.spines['top'].set_color('white')
        self.temp_ax.spines['left'].set_color('white')
        self.temp_ax.spines['right'].set_color('white')
        
        self.temp_canvas = FigureCanvasTkAgg(self.temp_fig, self.temp_frame)
        self.temp_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def create_humidity_chart(self):
        self.humidity_fig = Figure(figsize=(8, 4), dpi=100, facecolor='#2c3e50')
        self.humidity_ax = self.humidity_fig.add_subplot(111)
        self.humidity_ax.set_facecolor('#2c3e50')
        self.humidity_ax.tick_params(colors='white')
        self.humidity_ax.spines['bottom'].set_color('white')
        self.humidity_ax.spines['top'].set_color('white')
        self.humidity_ax.spines['left'].set_color('white')
        self.humidity_ax.spines['right'].set_color('white')
        
        self.humidity_canvas = FigureCanvasTkAgg(self.humidity_fig, self.humidity_frame)
        self.humidity_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def create_pressure_chart(self):
        self.pressure_fig = Figure(figsize=(8, 4), dpi=100, facecolor='#2c3e50')
        self.pressure_ax = self.pressure_fig.add_subplot(111)
        self.pressure_ax.set_facecolor('#2c3e50')
        self.pressure_ax.tick_params(colors='white')
        self.pressure_ax.spines['bottom'].set_color('white')
        self.pressure_ax.spines['top'].set_color('white')
        self.pressure_ax.spines['left'].set_color('white')
        self.pressure_ax.spines['right'].set_color('white')
        
        self.pressure_canvas = FigureCanvasTkAgg(self.pressure_fig, self.pressure_frame)
        self.pressure_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def create_wind_chart(self):
        self.wind_fig = Figure(figsize=(8, 4), dpi=100, facecolor='#2c3e50')
        self.wind_ax = self.wind_fig.add_subplot(111)
        self.wind_ax.set_facecolor('#2c3e50')
        self.wind_ax.tick_params(colors='white')
        self.wind_ax.spines['bottom'].set_color('white')
        self.wind_ax.spines['top'].set_color('white')
        self.wind_ax.spines['left'].set_color('white')
        self.wind_ax.spines['right'].set_color('white')
        
        self.wind_canvas = FigureCanvasTkAgg(self.wind_fig, self.wind_frame)
        self.wind_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def create_alerts_tab(self):
        # Alerts listbox
        alerts_label = tk.Label(
            self.alerts_frame, 
            text="Weather Alerts", 
            font=("Arial", 16, "bold"), 
            bg='#2c3e50', 
            fg='white'
        )
        alerts_label.pack(pady=10)
        
        alerts_list_frame = tk.Frame(self.alerts_frame, bg='#2c3e50')
        alerts_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.alerts_listbox = tk.Listbox(
            alerts_list_frame, 
            font=("Arial", 12),
            bg='#34495e',
            fg='white',
            selectbackground='#3498db'
        )
        alerts_scrollbar = tk.Scrollbar(alerts_list_frame, orient=tk.VERTICAL, command=self.alerts_listbox.yview)
        self.alerts_listbox.config(yscrollcommand=alerts_scrollbar.set)
        
        self.alerts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        alerts_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def add_city(self):
        city = self.city_entry.get().strip()
        if city and city not in self.cities:
            self.cities.append(city)
            self.city_listbox.insert(tk.END, city)
            self.temperature_history[city] = deque(maxlen=self.max_data_points)
            self.humidity_history[city] = deque(maxlen=self.max_data_points)
            self.pressure_history[city] = deque(maxlen=self.max_data_points)
            self.wind_speed_history[city] = deque(maxlen=self.max_data_points)
            self.city_entry.delete(0, tk.END)
            
            # In a real implementation, we would send a request to the API to start monitoring this city
            # For now, we'll just add it to our list
            messagebox.showinfo("Success", f"City '{city}' added to monitoring list!")
        elif city in self.cities:
            messagebox.showwarning("Warning", f"City '{city}' is already being monitored!")
        else:
            messagebox.showwarning("Warning", "Please enter a valid city name!")
            
    def update_data(self):
        """Consume data from Kafka"""
        try:
            # Kafka Consumer
            self.consumer = KafkaConsumer(
                'weather_topic',
                bootstrap_servers=['localhost:9093'],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='weather-dashboard-group-python',
                api_version=(0, 10, 1)  # Explicitly set API version
            )
            
            self.root.after(0, lambda: self.status_label.config(text="Status: Connected to Kafka", fg='lightgreen'))
            
            for message in self.consumer:
                if self.stop_event.is_set():
                    break
                    
                data = message.value
                
                # Extract city name or use coordinates if name is not available
                city_name = data.get('name', f"{data['coord']['lat']:.2f},{data['coord']['lon']:.2f}")
                
                # Convert temperature from Kelvin to Celsius
                temp_celsius = data['main']['temp'] - 273.15
                
                # Store the data
                self.weather_data[city_name] = {
                    'temperature': round(temp_celsius, 1),
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'description': data['weather'][0]['description'],
                    'wind_speed': data.get('wind', {}).get('speed', 0),
                    'rainfall': data.get('rain', {}).get('1h', 0)
                }
                
                # Add to history for charts
                if city_name not in self.temperature_history:
                    self.temperature_history[city_name] = deque(maxlen=self.max_data_points)
                    self.humidity_history[city_name] = deque(maxlen=self.max_data_points)
                    self.pressure_history[city_name] = deque(maxlen=self.max_data_points)
                    self.wind_speed_history[city_name] = deque(maxlen=self.max_data_points)
                    
                self.temperature_history[city_name].append(round(temp_celsius, 1))
                self.humidity_history[city_name].append(data['main']['humidity'])
                self.pressure_history[city_name].append(data['main']['pressure'])
                self.wind_speed_history[city_name].append(data.get('wind', {}).get('speed', 0))
                
                # Check for alerts
                self.check_alerts(city_name, data)
                
                # Update the UI
                self.root.after(0, self.update_ui)
                
        except Exception as e:
            error_msg = f"Error connecting to Kafka: {str(e)}"
            self.root.after(0, lambda: self.status_label.config(text=error_msg, fg='red'))
            # Wait before retrying
            time.sleep(5)
        finally:
            if self.consumer:
                self.consumer.close()
                
    def check_alerts(self, city_name, data):
        """Check for weather alerts"""
        alerts = []
        
        # Temperature alerts
        temp_celsius = data['main']['temp'] - 273.15
        if temp_celsius > 35:
            alerts.append(f"HIGH TEMPERATURE ALERT: {city_name} is experiencing extreme heat ({round(temp_celsius, 1)}°C)")
        elif temp_celsius < 0:
            alerts.append(f"FREEZING ALERT: {city_name} is experiencing freezing conditions ({round(temp_celsius, 1)}°C)")
            
        # Rainfall alerts
        rainfall = data.get('rain', {}).get('1h', 0)
        if rainfall > 30:
            alerts.append(f"HEAVY RAINFALL ALERT: {city_name} has heavy rainfall ({rainfall}mm in the last hour)")
        elif rainfall > 15:
            alerts.append(f"MODERATE RAINFALL ALERT: {city_name} has moderate rainfall ({rainfall}mm in the last hour)")
            
        # Wind alerts
        wind_speed = data.get('wind', {}).get('speed', 0)
        if wind_speed > 20:
            alerts.append(f"HIGH WIND ALERT: {city_name} has high winds ({wind_speed} m/s)")
            
        # Pressure alerts
        pressure = data['main']['pressure']
        if pressure < 1000:
            alerts.append(f"LOW PRESSURE ALERT: {city_name} has low pressure ({pressure} hPa)")
            
        # Add alerts to the listbox
        for alert in alerts:
            self.root.after(0, lambda a=alert: self.alerts_listbox.insert(tk.END, a))
            
    def update_ui(self):
        """Update the UI with new data"""
        # Update city list
        current_cities = set(self.city_listbox.get(0, tk.END))
        for city in self.weather_data.keys():
            if city not in current_cities:
                self.city_listbox.insert(tk.END, city)
                
        # Update charts
        self.update_temperature_chart()
        self.update_humidity_chart()
        self.update_pressure_chart()
        self.update_wind_chart()
        
        # Update city details if a city is selected
        selection = self.city_listbox.curselection()
        if selection:
            city = self.city_listbox.get(selection[0])
            if city in self.weather_data:
                data = self.weather_data[city]
                details = f"City: {city}\n"
                details += f"Temperature: {data['temperature']}°C\n"
                details += f"Humidity: {data['humidity']}%\n"
                details += f"Pressure: {data['pressure']} hPa\n"
                details += f"Wind Speed: {data['wind_speed']} m/s\n"
                details += f"Condition: {data['description']}"
                self.details_label.config(text=details)
        
    def update_temperature_chart(self):
        self.temp_ax.clear()
        self.temp_ax.set_facecolor('#2c3e50')
        self.temp_ax.tick_params(colors='white')
        self.temp_ax.spines['bottom'].set_color('white')
        self.temp_ax.spines['top'].set_color('white')
        self.temp_ax.spines['left'].set_color('white')
        self.temp_ax.spines['right'].set_color('white')
        self.temp_ax.set_title('Temperature Over Time', color='white')
        self.temp_ax.set_ylabel('Temperature (°C)', color='white')
        
        # Plot data for each city
        has_data = False
        for city in self.weather_data.keys():
            if city in self.temperature_history and len(self.temperature_history[city]) > 0:
                data = list(self.temperature_history[city])
                self.temp_ax.plot(data, marker='o', label=city)
                has_data = True
                
        if has_data:
            self.temp_ax.legend(loc='upper left', facecolor='#34495e', edgecolor='white', labelcolor='white')
        else:
            # Show "No data" message
            self.temp_ax.text(0.5, 0.5, 'No temperature data available', 
                             horizontalalignment='center', verticalalignment='center',
                             transform=self.temp_ax.transAxes, color='white', fontsize=14)
            
        self.temp_canvas.draw()
        
    def update_humidity_chart(self):
        self.humidity_ax.clear()
        self.humidity_ax.set_facecolor('#2c3e50')
        self.humidity_ax.tick_params(colors='white')
        self.humidity_ax.spines['bottom'].set_color('white')
        self.humidity_ax.spines['top'].set_color('white')
        self.humidity_ax.spines['left'].set_color('white')
        self.humidity_ax.spines['right'].set_color('white')
        self.humidity_ax.set_title('Humidity Over Time', color='white')
        self.humidity_ax.set_ylabel('Humidity (%)', color='white')
        
        # Plot data for each city
        has_data = False
        for city in self.weather_data.keys():
            if city in self.humidity_history and len(self.humidity_history[city]) > 0:
                data = list(self.humidity_history[city])
                self.humidity_ax.plot(data, marker='s', label=city)
                has_data = True
                
        if has_data:
            self.humidity_ax.legend(loc='upper left', facecolor='#34495e', edgecolor='white', labelcolor='white')
        else:
            # Show "No data" message
            self.humidity_ax.text(0.5, 0.5, 'No humidity data available', 
                                 horizontalalignment='center', verticalalignment='center',
                                 transform=self.humidity_ax.transAxes, color='white', fontsize=14)
            
        self.humidity_canvas.draw()
        
    def update_pressure_chart(self):
        self.pressure_ax.clear()
        self.pressure_ax.set_facecolor('#2c3e50')
        self.pressure_ax.tick_params(colors='white')
        self.pressure_ax.spines['bottom'].set_color('white')
        self.pressure_ax.spines['top'].set_color('white')
        self.pressure_ax.spines['left'].set_color('white')
        self.pressure_ax.spines['right'].set_color('white')
        self.pressure_ax.set_title('Pressure Over Time', color='white')
        self.pressure_ax.set_ylabel('Pressure (hPa)', color='white')
        
        # Plot data for each city
        has_data = False
        for city in self.weather_data.keys():
            if city in self.pressure_history and len(self.pressure_history[city]) > 0:
                data = list(self.pressure_history[city])
                self.pressure_ax.plot(data, marker='^', label=city)
                has_data = True
                
        if has_data:
            self.pressure_ax.legend(loc='upper left', facecolor='#34495e', edgecolor='white', labelcolor='white')
        else:
            # Show "No data" message
            self.pressure_ax.text(0.5, 0.5, 'No pressure data available', 
                                 horizontalalignment='center', verticalalignment='center',
                                 transform=self.pressure_ax.transAxes, color='white', fontsize=14)
            
        self.pressure_canvas.draw()
        
    def update_wind_chart(self):
        self.wind_ax.clear()
        self.wind_ax.set_facecolor('#2c3e50')
        self.wind_ax.tick_params(colors='white')
        self.wind_ax.spines['bottom'].set_color('white')
        self.wind_ax.spines['top'].set_color('white')
        self.wind_ax.spines['left'].set_color('white')
        self.wind_ax.spines['right'].set_color('white')
        self.wind_ax.set_title('Wind Speed Over Time', color='white')
        self.wind_ax.set_ylabel('Wind Speed (m/s)', color='white')
        
        # Plot data for each city
        has_data = False
        for city in self.weather_data.keys():
            if city in self.wind_speed_history and len(self.wind_speed_history[city]) > 0:
                data = list(self.wind_speed_history[city])
                self.wind_ax.plot(data, marker='d', label=city)
                has_data = True
                
        if has_data:
            self.wind_ax.legend(loc='upper left', facecolor='#34495e', edgecolor='white', labelcolor='white')
        else:
            # Show "No data" message
            self.wind_ax.text(0.5, 0.5, 'No wind speed data available', 
                             horizontalalignment='center', verticalalignment='center',
                             transform=self.wind_ax.transAxes, color='white', fontsize=14)
            
        self.wind_canvas.draw()
        
    def on_closing(self):
        """Handle window closing"""
        self.stop_event.set()
        if self.consumer:
            self.consumer.close()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = WeatherDashboard(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()