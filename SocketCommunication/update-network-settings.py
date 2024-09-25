import json

# File path to the settings file
settings_file = 'network-settings.json'

# Function to load the settings
def load_settings():
    with open(settings_file, 'r') as f:
        return json.load(f)

# Function to save the settings
def save_settings(settings):
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=4)
    print("Settings saved successfully.")

# Function to display current settings
def display_settings(settings):
    print("\nCurrent settings:")
    for key, value in settings.items():
        print(f"{key}: {value}")

# Function to update a specific setting
def update_settings(settings):
    key = input("\nWhich setting would you like to update? (host, port, password): ")
    if key in settings:
        new_value = input(f"Enter new value for {key} (current: {settings[key]}): ")
        settings[key] = new_value if key != 'port' else int(new_value)
        save_settings(settings)
    else:
        print(f"Invalid setting '{key}'.")

# Main loop
def main():
    settings = load_settings()
    display_settings(settings)

    while True:
        update = input("\nDo you want to update a setting? (y/n): ").lower()
        if update == 'y':
            update_settings(settings)
        else:
            print("Exiting...")
            break

if __name__ == "__main__":
    main()
