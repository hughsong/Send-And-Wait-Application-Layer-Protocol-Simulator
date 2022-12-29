#------------------------------------------------------------------------
# SOURCE FILE:    Packet.py
# PROGRAM:        File transfer application (Packet object)
# FUNCTIONS:      Create an object class for packet
#
# DATE:           December 4th, 2020
# REVISIONS:      N/A
#
# PROGRAMMER:     Hugh Song
#
# NOTES:
# All three machines must have this file.
#------------------------------------------------------------------------
class Packet:
	#Constructor
	def __init__(self, PacketType, SeqNum, AckNum, data, WindowSize):
		#String PacketType include ACK, DATA, EOF, EOT
		self.PacketType = PacketType
		#int
		self.SeqNum = SeqNum
		#int
		self.AckNum = AckNum
		#String
		self.data = data
		#int
		self.WindowSize = WindowSize

	#------------------------------------------------------------------------
	# FUNCTION getSeqNum
	# ARGUMENTS: void
	# RETURNS: int
	# Description: gettor
	#------------------------------------------------------------------------
	def getSeqNum(self):
		return self.SeqNum

	#------------------------------------------------------------------------
	# FUNCTION makeList
	# ARGUMENTS: void
	# RETURNS: list 
	# Description: return a list to contain all of its variables value
	#------------------------------------------------------------------------
	def makeList(self):
		data_list = [self.PacketType, self.SeqNum, self.AckNum, self.data, self.WindowSize]
		return data_list