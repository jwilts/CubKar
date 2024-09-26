# CubCar Timer

## Introduction
The **Cub Car Timer** is a project designed to manage CubCar (Pinewood Derby) races in a fair and efficient manner. It allows users to build race timers for multiple track configurations at an affordable price of under $75 (excluding optional RFID tags). The solution is easy to set up and flexible enough to support different track layouts, configurations, and future customizations. It is open-source and encourages collaboration and modification by other groups.

## Goals
- Build timers for < $75 per timer.
- Provide clear instructions for technically savvy individuals to build their own timers.
- Support multiple timers running concurrently at the same rally.
- Allow easy retrofitting of timers onto existing tracks with minimal invasiveness.
- Support tracks from 2-8 lanes (currently not met).
- Develop an open-source solution to encourage community collaboration.
- Future plans to transition the project from Raspberry Pi to Arduino for a more affordable solution.

## Solution Overview

### Components
1. **Registration Station**: A Raspberry Pi with an RFID pad that registers racer information in a database. Multiple stations can be used simultaneously.
2. **Timer**: The main unit that runs the races, built on a Raspberry Pi. 
3. **Race Management Station** (Optional): A Microsoft Access database linked to MariaDB for additional information and reporting.
4. **MariaDB**: Stores racer information and race results, allowing for easy reporting and analysis. It can be hosted on the timer or a separate machine.
5. **Raspberry Pi**: The core of the timer solution. Supports GPIO connections for sensors and controls, with optional integration of an LED matrix or RFID pad.

### Software and Setup
1. **Raspberry Pi Setup**:
   - Enable **SPI** for LED Matrix or RFID Card.
   - Enable **SSH** for remote access.
   - Enable **VNC** for remote keyboard/mouse interaction.

2. **Useful Software**:
   - **Filezilla**: For transferring files between the Pi and a PC.
   - **VNC Viewer**: For remote control of the Pi.
   - **Notepad++**: Recommended for editing configuration and code files.
   - **HeidiSQL**: A tool for managing MariaDB databases.
   - **MariaDB**: The database that stores race data.
   - **Microsoft Access**: Optional, for race management reporting.

### Circuit Diagram and Parts List
- **Components**: 
   - High-power LEDs, Light Dependent Resistors (LDRs), Raspberry Pi, DB9 connectors, and other components for GPIO connections.
   - **Optional**: MAX7219 LED array, RFID reader (RC522), relay board for external light tree countdown.

## Features
- **Supports 2-4 lanes**: Current version supports 3 lanes, with potential for future expansion.
- **RFID Pad and Database**: Optional integration for race management. If using RFID, a MariaDB database is required.
- **LED Indicators**: Display race results with lights showing 1st, 2nd, and 3rd places.
- **Multiple Configurations**: Timers can be configured to fit various track layouts.
- **Race Modes**: Allows for cumulative time tracking across multiple tracks to determine the winner.

## Wiring
- The solution uses Raspberry Pi GPIO pins for various components (LDRs, LEDs, switches).
- The RFID pad and MAX7219 matrix share the same pins, so only one can be used at a time.
- The project includes a color-coded wiring guide for easy reference.

## Future Enhancements
- Switch to Arduino for cost-effective timers.
- Improve the GUI for better race management.
- Explore RFID over I2C for better cable management.
- Investigate LED multiplexing for more advanced race visuals.
- Implement better threading and callback functionality to make the GUI more responsive.

## Installation Instructions
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/cubcar-timer.git
   cd cubcar-timer
