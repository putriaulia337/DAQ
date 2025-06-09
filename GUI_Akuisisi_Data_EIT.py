import tkinter as tk
from tkinter import messagebox, filedialog
import serial
import threading
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import csv

serial_open = False
serial_data = [0] * 100  # Buffer awal
ser = None

def adc_to_voltage(adc):
    return (adc / 1023.0) * 5.0  # 10-bit ADC, referensi 5V

def read_serial():
    global serial_open, ser, serial_data
    while serial_open:
        try:
            line = ser.readline().decode('utf-8').strip()
            if line.isdigit():
                value = int(line)
                serial_data.append(value)
                serial_data = serial_data[-buffer_size_var.get():]
        except Exception as e:
            print(f"Serial error: {e}")

def start_serial():
    global ser, serial_open
    try:
        port = port_var.get()
        if port == "--Select--":
            messagebox.showwarning("Warning", "Select a COM port")
            return
        ser = serial.Serial('COM' + port, 9600, timeout=1)
        serial_open = True
        threading.Thread(target=read_serial, daemon=True).start()
        status_label.config(text="Connected", fg="green")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to connect: {e}")
        status_label.config(text="Not Connected", fg="red")

def stop_serial():
    global ser, serial_open
    serial_open = False
    try:
        if ser:
            ser.close()
        status_label.config(text="Not Connected", fg="red")
    except:
        pass

def animate(i):
    if len(serial_data) == 0:
        return
    voltages = [adc_to_voltage(v) for v in serial_data]
    x = np.arange(len(voltages)) / 250  # sesuaikan jika sampling rate berubah
    ax.clear()
    ax.plot(x, voltages)
    ax.set_ylim(-0.5, 5.5)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage (V)")
    ax.grid(True)

    # Update label nilai ADC & Voltage terakhir
    latest_adc = serial_data[-1]
    latest_voltage = adc_to_voltage(latest_adc)
    adc_label_var.set(f"ADC Value: {float(latest_adc):.3f}")
    voltage_label_var.set(f"Voltage: {latest_voltage:.3f} V")

def save_data():
    if len(serial_data) == 0:
        messagebox.showwarning("Warning", "No data to save!")
        return
    
    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
    filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return
    
    try:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Index", "ADC Value", "Voltage (V)"])
            for i, adc_val in enumerate(serial_data):
                voltage = adc_to_voltage(adc_val)
                writer.writerow([i, f"{float(adc_val):.3f}", f"{voltage:.3f}"])
        messagebox.showinfo("Info", f"Data saved to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file:\n{e}")

def on_closing():
    stop_serial()
    root.destroy()

# GUI Setup
root = tk.Tk()
root.title("Live ADC Viewer - EIT Peak Detector")

default_font = ("Arial", 14)

frame = tk.Frame(root)
frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)

tk.Label(frame, text="COM Port:", font=default_font).pack()
port_var = tk.StringVar(value="--Select--")
ports = ["--Select--"] + [str(i) for i in range(20)]
port_menu = tk.OptionMenu(frame, port_var, *ports)
port_menu.config(font=default_font)
port_menu.pack()

tk.Button(frame, text="Open Serial", command=start_serial, font=default_font).pack(pady=10)
tk.Button(frame, text="Close Serial", command=stop_serial, font=default_font).pack(pady=10)

status_label = tk.Label(frame, text="Not Connected", fg="red", font=("Arial", 14, "bold"))
status_label.pack(pady=15)

tk.Label(frame, text="Buffer Size:", font=default_font).pack()
buffer_size_var = tk.IntVar(value=100)
tk.Spinbox(frame, from_=10, to=1000, textvariable=buffer_size_var, font=default_font, width=8).pack()

tk.Button(frame, text="Save Data to CSV", command=save_data, font=default_font).pack(pady=20)

# Matplotlib figure + canvas
fig = Figure(figsize=(7, 5), dpi=100)
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Label nilai ADC & tegangan live
bottom_frame = tk.Frame(root)
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

adc_label_var = tk.StringVar(value="ADC Value: -")
voltage_label_var = tk.StringVar(value="Voltage: -")

tk.Label(bottom_frame, textvariable=adc_label_var, font=("Arial", 16)).pack(side=tk.LEFT, padx=20)
tk.Label(bottom_frame, textvariable=voltage_label_var, font=("Arial", 16)).pack(side=tk.LEFT, padx=20)

ani = animation.FuncAnimation(fig, animate, interval=100)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
