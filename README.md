# CubKar
Overview – The Cub Car timer is a project designed to run and manage cub car (pinewood derby) races to help run them in a fair and fun fashion.
The timer was developed using Raspberry PI v3 with a standard Raspbian Stretch install on it.  The project likely could run on a V2, however I don’t have one that I can validate / test on. 
All the sensors are directly connected via the GPIO port.   The program and controller is setup for 3 tracks, but could be expanded for 4 tracks.
The goal of the project is to build the entire solution for less than $100.00.
The solution can run headless (no screen or keyboard directly attached) or connected to a touchscreen or utilizing an external monitor.
The following is the circuit diagram and parts list.
15 - High Power LED’s	3 - 10K Light Dependent Resisters 	12 – 300 OHM Resisters
1 – Momentary Push Button	1 – Raspberry PI 3.0	1 - 40 PIN Header (Optional)
Strip Board or PCB	3 - DB 9 Connector 	1 - 2 wire Extension Wire (Length of Track) (Speaker Wire)
1 – RCA (track button Cable)	1 – Raspberry PI Touch Screen (Optional)	1 – MAX7219 LED Array (Optional)
1 – RC522 RFID Reader (Optional)	1 – 5 V PI compatible Relay board (Optional)	1 -  RS232 9 wire M-F cables (Length of Track)
		
