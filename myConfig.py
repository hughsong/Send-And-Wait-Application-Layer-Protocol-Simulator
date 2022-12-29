#------------------------------------------------------------------------
# SOURCE FILE:    myConfig.py
# PROGRAM:        File transfer application (configuration file)
# FUNCTIONS:      Store basic setup information 
#
# DATE:           December 4th, 2020
# REVISIONS:      N/A
#
# PROGRAMMER:     Hugh Song
#
# NOTES:
# All three machines must have this file.
#------------------------------------------------------------------------

# information for machines
myInfo = {
	"transIP" 	: "192.168.0.19",			# Transmitter IP
	"recvIP" 	: "192.168.0.12",			# Receiver IP
	"networkIP" : "192.168.0.16",			# Network Emulator IP
	"port1" 	: 7005,						# Transmitter Port
	"port2" 	: 7006,						# Receiver Port
	"port3" 	: 48575,					# Network Emulator - Transmitter
}
# information for settings
settings = {
	"winSize" 	: 9,						# Transmitter window size
	"dataLen"	: 15,						# The data length in each packet (byte)
	"timeout"	: 2,						# Set timer for retransmission 
	"trans_log" : "trans_log.txt",			# The log file that save all the prints in transmitter
	"emu_log"   : "emu_log.txt",			# The log file that save all the prints in emulator
	"recv_log"  : "recv_log.txt",			# The log file that save all the prints in receiver
}