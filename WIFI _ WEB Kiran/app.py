from flask import Flask, render_template, request, redirect, url_for
import subprocess
import re

app = Flask(__name__)

def get_wifi_profiles():
    command = ["netsh", "wlan", "show", "profiles"]
    result = subprocess.run(command, capture_output=True, text=True)
    profiles = re.findall(r"All User Profile\s*:\s*(.*)", result.stdout)
    return profiles

def get_wifi_password(profile):
    command = ["netsh", "wlan", "show", "profile", profile, "key=clear"]
    result = subprocess.run(command, capture_output=True, text=True)
    password_match = re.search(r"Key Content\s*:\s*(.*)", result.stdout)
    if password_match:
        return password_match.group(1)
    else:
        return None

@app.route('/')
def index():
    profiles = get_wifi_profiles()
    wifi_data = []
    for profile in profiles:
        password = get_wifi_password(profile)
        wifi_data.append({"profile": profile, "password": password if password else "No password found"})
    return render_template('index.html', wifi_data=wifi_data)

@app.route('/add-wifi', methods=['GET', 'POST'])
def add_wifi():
    if request.method == 'POST':
        ssid = request.form['ssid']
        password = request.form['password']
        command = ["netsh", "wlan", "add", "profile", "ssid="+ssid, "key="+password]
        result = subprocess.run(command, capture_output=True, text=True)
        if "successfully" in result.stdout:
            return redirect(url_for('index'))
        else:
            return "Failed to add WiFi profile."
    return render_template('add_wifi.html')

if __name__ == '__main__':
    app.run(debug=True)
