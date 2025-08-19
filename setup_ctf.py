#!/usr/bin/env python3
"""
Tulip CTF Configuration Script
Configures .env and configuration.py for custom Attack-Defense CTF
"""

import os
import sys
import subprocess
from datetime import datetime
import re

def get_user_input():
    """Gather CTF configuration from user"""
    print("=== Tulip CTF Configuration Setup ===")
    print()
    
    # Team configuration
    team_ip = input("Enter your team IP (e.g., 10.10.3.1): ").strip()
    if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', team_ip):
        print("Invalid IP format. Please try again.")
        sys.exit(1)
    
    team_id = input("Enter your team ID: ").strip()
    
    # Database configuration
    print("\n--- Database Configuration ---")
    db_user = input("Database username [tulip_user]: ").strip() or "tulip_user"
    db_password = input("Database password [your_password]: ").strip() or "your_password"
    db_host = input("Database host [timescale]: ").strip() or "timescale"
    db_port = input("Database port [5432]: ").strip() or "5432"
    db_name = input("Database name [tulip_db]: ").strip() or "tulip_db"
    
    # Game configuration
    print("\n--- Game Configuration ---")
    tick_start = input("CTF start time (ISO 8601, e.g., 2025-08-23T13:00:00Z): ").strip()
    if not tick_start:
        tick_start = "2025-08-23T13:00:00Z"
    
    tick_length = input("Tick length in ms [120000 = 2 minutes]: ").strip() or "120000"
    
    flag_regex = input("Flag regex [FLAG_[A-Za-z0-9/+]{32}]: ").strip() or "FLAG_[A-Za-z0-9/+]{32}"
    
    flag_lifetime = input("Flag lifetime in ticks [2]: ").strip() or "2"
    
    # Optional configurations
    print("\n--- Optional Configurations ---")
    pcap_dir = input("PCAP directory [./pcaps]: ").strip() or "./pcaps"
    
    visualizer_url = input("Visualizer URL [http://localhost:3000/]: ").strip() or "http://localhost:3000/"
    
    flagid_endpoint = input("Flag ID endpoint [https://x3ero0.dev/competition/teams.json]: ").strip() or "https://x3ero0.dev/competition/teams.json"
    
    flag_validator = input("Flag validator type (faust/enowars/eno/itad) [faust]: ").strip() or "faust"
    
    validator_team = input("Flag validator team number [42]: ").strip() or "42"
    
    return {
        'team_ip': team_ip,
        'team_id': team_id,
        'db_user': db_user,
        'db_password': db_password,
        'db_host': db_host,
        'db_port': db_port,
        'db_name': db_name,
        'tick_start': tick_start,
        'tick_length': tick_length,
        'flag_regex': flag_regex,
        'flag_lifetime': flag_lifetime,
        'pcap_dir': pcap_dir,
        'visualizer_url': visualizer_url,
        'flagid_endpoint': flagid_endpoint,
        'flag_validator': flag_validator,
        'validator_team': validator_team
    }

def create_env_file(config):
    """Create .env file with configuration"""
    env_content = f"""##############################
# Tulip config
##############################
# Timescale connection - Update with your actual database credentials
TIMESCALE="postgres://{config['db_user']}:{config['db_password']}@{config['db_host']}:{config['db_port']}/{config['db_name']}"

# The location of your pcaps as seen by the host - Update to your actual pcap directory
TRAFFIC_DIR_HOST="{config['pcap_dir']}"

# The location of your pcaps (and eve.json), as seen by the container
TRAFFIC_DIR_DOCKER="/traffic"

# Visualizer - Update with your actual scraper/visualizer URL
VISUALIZER_URL="{config['visualizer_url']}"

##############################
# Game config
##############################
# Start time of the CTF - Update to your event start time (ISO 8601 format)
TICK_START="{config['tick_start']}"

# Tick length in ms (3 minutes = 180000ms, adjust as needed)
TICK_LENGTH={config['tick_length']}

# The flag format in regex - Update to match your CTF's flag format
FLAG_REGEX="{config['flag_regex']}"

# VM IP (inside gamenet) - Update to your team's VM IP
VM_IP="{config['team_ip']}"

# Your team ID
TEAM_ID="{config['team_id']}"

##############################
# PCAP_OVER_IP CONFIGS
##############################
# Enable pcap-over-ip and choose server endpoint
# Uncomment and configure if you need real-time pcap streaming
PCAP_OVER_IP=
#PCAP_OVER_IP="host.docker.internal:1337"
# For multiple endpoints:
#PCAP_OVER_IP="host.docker.internal:1337,remote-host.com:5050"

##############################
# DUMP_PCAPS CONFIGS
##############################
# Enable pcap dumping to save captured traffic
# Uncomment if you want to save pcaps to disk
DUMP_PCAPS=
#DUMP_PCAPS="/traffic/dumps"

# Dumping interval (1m = 1 minute, 5m = 5 minutes, etc.)
DUMP_PCAPS_INTERVAL="5m"

# Filename format using Go time formatting
DUMP_PCAPS_FILENAME="2006-01-02_15-04-05.pcap"

##############################
# FLAGID CONFIGS
##############################
# Enable flagid scraping - Uncomment if your CTF uses flag IDs
FLAGID_SCRAPE=1
#FLAGID_SCRAPE=1

# Enable flagid scanning in traffic
FLAGID_SCAN=1
#FLAGID_SCAN=1

# Flag lifetime in ticks (how many rounds flags are valid)
FLAG_LIFETIME={config['flag_lifetime']}

# Flagid endpoint - Update to your actual flag ID service
FLAGID_ENDPOINT="{config['flagid_endpoint']}"

##############################
# FLAG_VALIDATOR CONFIGS
##############################
# Flag validation system - Choose: faust, enowars, eno, itad
# Uncomment and set based on your CTF platform
FLAG_VALIDATOR_TYPE={config['flag_validator']}
#FLAG_VALIDATOR_TYPE="enowars"

# Your team number for flag validation
FLAG_VALIDATOR_TEAM={config['validator_team']}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)

def update_configurations_py(team_ip):
    """Update services/api/configurations.py with team IP"""
    config_file = 'services/api/configurations.py'
    
    # Read current file
    with open(config_file, 'r') as f:
        content = f.read()
    
    # Update vm_ip line
    content = re.sub(
        r'vm_ip = os\.getenv\("VM_IP", "[^"]*"\)',
        f'vm_ip = os.getenv("VM_IP", "{team_ip}")',
        content
    )
    
    # Write back to file
    with open(config_file, 'w') as f:
        f.write(content)

def main():
    """Main configuration function"""
    try:
        # Get configuration from user
        config = get_user_input()
        
        print(f"\n=== Configuration Summary ===")
        print(f"Team IP: {config['team_ip']}")
        print(f"Team ID: {config['team_id']}")
        print(f"Database: {config['db_user']}@{config['db_host']}:{config['db_port']}/{config['db_name']}")
        print(f"CTF Start: {config['tick_start']}")
        print(f"Tick Length: {config['tick_length']}ms")
        print(f"Flag Regex: {config['flag_regex']}")
        
        confirm = input("\nProceed with this configuration? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Configuration cancelled.")
            sys.exit(0)
        
        # Create .env file
        print("\n=== Setting up .env file ===")
        create_env_file(config)
        print("✓ .env file created successfully")
        
        # Create pcap directory if it doesn't exist
        if not os.path.exists(config['pcap_dir']):
            os.makedirs(config['pcap_dir'], exist_ok=True)
            print(f"✓ Created pcap directory: {config['pcap_dir']}")
        
        # Update configuration.py
        print("\n=== Setting up configuration.py ===")
        update_configurations_py(config['team_ip'])
        print("✓ configuration.py updated successfully")
        
        print("\n=== Setup Complete ===")
        print("Your Tulip CTF environment is now configured!")
        print("You can start the services with: docker-compose up -d")
        
    except KeyboardInterrupt:
        print("\n\nConfiguration cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError during configuration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()