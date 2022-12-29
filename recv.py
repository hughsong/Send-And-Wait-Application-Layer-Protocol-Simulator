#------------------------------------------------------------------------
# SOURCE FILE:    recv.py
# PROGRAM:        File transfer application (Receiver)
# FUNCTIONS:      Receive packet from “unreliable network”. (UDP)
#                 Respond acks for each packets
#                 Store data into a datalist
#                 By the end of transmission, sort the dataList, and 
#                 write all of data into newFile.txt
#
# DATE:           December 4th, 2020
# REVISIONS:      N/A
#
# PROGRAMMER:     Hugh Song
#
# NOTES:
# Application will be automatically terminated after receive the whole 
# file.
#------------------------------------------------------------------------
import socket
import sys
import time
import threading
import myConfig as mcf
import Packet as pck
import ast 
import random

# window size 
winSize = mcf.settings["winSize"]
# log file save all the prints  
recv_log = mcf.settings["recv_log"]
# start time of the program (timestamp)
start = time.perf_counter()
# IP address for this machine
recvIP = mcf.myInfo["recvIP"]
# emulator's IP address
networkIP = mcf.myInfo["networkIP"]
# port2 is bind on this machine
port2 = mcf.myInfo["port2"]
# packets will be sent through port3
port3 = mcf.myInfo["port3"]
# UDP socket
sockobj2 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sockobj2.bind(("", port2))

print("***** Receiver Start *****")
print("IP: %s, Waiting on port: %s" % (recvIP, port2))
with open(recv_log, 'w') as f:
    print("***** Receiver Start *****", file=f)
    print("IP: %s, Waiting on port: %s" % (recvIP, port2), file=f)

#------------------------------------------------------------------------
# FUNCTION recvFile
# ARGUMENTS: void
# RETURNS: void
# Description: Loop(receive a packet then reply ack for it)
# NOTES:
# If the packet's type is DATA, and it is not duplicate, this packets 
# will be added into dataList.
# If it is a duplicate packet, only reply ack.
#------------------------------------------------------------------------
def recvFile():
    # amount of packets that has received
    global ttl_pkts
    # packet's sequence number
    global seqNum
    # counter to count received packets amount(deplicate packets would not be counted)
    counter = -1
    # signal for ternimation
    terminate = False
    # signal for EOF
    eof = False
    # dataList to store all of data
    dataList = []
    # signal for EOT.(record seq of EOT)
    eot = -1
    # packet's sequence number 
    seqNum = 0
    # packet's ack number 
    ackNum = 0
    ttl_pkts = 0
    recv_EOT = False

    # infinit loop to receive packets until get the whole file
    while 1:
        if terminate == True:
            print("***** File transfer complete *****")
            with open(recv_log, 'a+') as f:
                print("***** File transfer complete *****", file=f)
            break

        data = sockobj2.recv(1024)
        packet = ast.literal_eval(data.decode())
        ttl_pkts += 1
        print_packet(packet) 
        ackNum = packet[1]  	
        # if it is duplicate packet
        if packet in dataList:
            ack_packet = pck.Packet("ACK", seqNum, ackNum, "duplicate data packet", winSize)
            sockobj2.sendto(str(ack_packet.makeList()).encode(), (networkIP, port3))
            seqNum += 1
            continue
        # if the packet is not received before
        else: 
            # if it is a DATA packet
            if packet[0] == "DATA":
                recv_EOT = False
                message = ("sequence number %s OK" % (packet[1]))
                ack_packet = pck.Packet("ACK", seqNum, ackNum, message, winSize)
                sockobj2.sendto(str(ack_packet.makeList()).encode(), (networkIP, port3))
                seqNum += 1
                dataList.append(packet)
                eot = -1
            # if it is an EOT packet
            elif packet[0] == "EOT":
                recv_EOT = True
                ack_packet = pck.Packet("EOT", seqNum, ackNum, "Recv eot", winSize)
                sockobj2.sendto(str(ack_packet.makeList()).encode(), (networkIP, port3))
                seqNum += 1
            # if it is an EOF packet
            elif packet[0] == "EOF":
                recv_EOT = False
                ack_packet = pck.Packet("EOF", seqNum, ackNum, "end of File", winSize)
                sockobj2.sendto(str(ack_packet.makeList()).encode(), (networkIP, port3))
                seqNum += 1
                eof = True
            counter += 1
        
        if eof == True and packet[0] == "EOT":
            eot = packet[1]
        # if the whole file is received  
        if eof == True and counter == eot:
            terminate = True
            sortlist(dataList)

        print_packet(ack_packet.makeList())
        
        if recv_EOT == True: 
            print_receiver_status()

#------------------------------------------------------------------------
# FUNCTION print_packet
# ARGUMENTS: object packet
# RETURNS: void
# Description: print out packet content.
# NOTES:
# packet content will be printed out on screen and written into log file
#------------------------------------------------------------------------
def print_packet(packet):
    print("Flag: %s, SeqNum: %s, AckNum: %s, Data: %s, WinSize: %s, Timestamp: %-10.5f" 
    % (packet[0], packet[1], packet[2], packet[3], packet[4], time.perf_counter() - start))
    with open(recv_log, 'a+') as f:
        print("Flag: %s, SeqNum: %s, AckNum: %s, Data: %s, WinSize: %s, Timestamp: %-10.5f" 
        % (packet[0], packet[1], packet[2], packet[3], packet[4], time.perf_counter() - start), file=f)

#------------------------------------------------------------------------
# FUNCTION print_receiver_status
# ARGUMENTS: void
# RETURNS: void
# Description: print out recent condition
# NOTES:
# Information will be printed out on screen and written into log file
#------------------------------------------------------------------------
def print_receiver_status():
    print("-------------------------------------------------------------------------------------")
    print("Total packets received: %d, Total acks sent %d"
    % (ttl_pkts, seqNum))
    print("-------------------------------------------------------------------------------------")
    with open(recv_log, 'a+') as f:
        print("-------------------------------------------------------------------------------------", file=f)
        print("Total packets received: %d, Total acks sent %d"
        % (ttl_pkts, seqNum), file=f)
        print("-------------------------------------------------------------------------------------", file=f)

#------------------------------------------------------------------------
# FUNCTION save_in_file
# ARGUMENTS: List dataList
# RETURNS: void
# Description: iterate temp list, write data into a file
# NOTES:
# This function will be invoked after dataList being sorted
#------------------------------------------------------------------------
def save_in_file(dataList):
    file = open("newFile.txt", 'wb')
    for i in range(0,len(dataList)):
        file.write(dataList[i][3])
    file.close()

#------------------------------------------------------------------------
# FUNCTION sortlist
# ARGUMENTS: List dataList
# RETURNS: void
# Description: Using select sorting algorithm to sort the datalist
#------------------------------------------------------------------------
def sortlist(dataList):
    for i in range(0,len(dataList)):
        min_idx = i
        for j in range((i + 1), len(dataList)): 
            if dataList[min_idx][1] > dataList[j][1]: 
                min_idx = j 
        dataList[i], dataList[min_idx] = dataList[min_idx], dataList[i]
    save_in_file(dataList)
        
#------------------------------------------------------------------------
# FUNCTION main
# ARGUMENTS: void
# RETURNS: void
# Description: this is my main application entry
# User need to enter bit_error_rate and average_delay time 
#------------------------------------------------------------------------
def main():
    print("-------------------------------------------------------------------------------------")
    print("Server is ready to receive a file")
    print("-------------------------------------------------------------------------------------")
    with open(recv_log, 'a+') as f:
        print("-------------------------------------------------------------------------------------", file=f)
        print("Server is ready to receive a file", file=f)
        print("-------------------------------------------------------------------------------------", file=f)
    recvFile()

if __name__ == '__main__':
    main()

