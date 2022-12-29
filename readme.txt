#-------------------------------------------------------------------------------------------
# PROGRAM:        COMP 7005 Final Project
# DATE:           December 4, 2020
# REVISIONS:      N/A
# PROGRAMMER:     Hugh Song
#-------------------------------------------------------------------------------------------

1. Source file distribution:

	Transmitter has to have: trans.py; Packet.py; myConfig.py
	Emulator has to have: emu.py; Packet.py; myConfig.py
	Receiver has to have: recv.py; Packet.py; myConfig.py
	(All the source files on each machine should be in the same directory)

2. Modify myConfig.py

	Requisite:
		Please modify the IP address before starting the application. (IPv4)
		Change port number and make sure that they are not bound with other programs.
	Optional:
		Change window size, data length and name of log files in the settings. 
                The timeout value would be assigned to the timer for the first round of the transmission.
		Please keep this value greater then one.

3. Use python3 to complie(run) the source code. (Might not work with lower edition)

4. Execution order:

	1> Run recv.py on receiver machine.
	2> Run emu.py on emulator machine, enter bit error rate(0-100) and delay(ms).
	3> Run trans.py on transmitter machine and enter filename.

5. After file transfer complete:

	Transmitter application will automatically terminate.
	Receiver application will automatically terminate.
	Emulator application has to be manually terminated.

	The process would be recorded in three log files on these three machines. 

	The name of the log file could be modified in myConfig.py
	The log files are stored in the same directory as the source code.
