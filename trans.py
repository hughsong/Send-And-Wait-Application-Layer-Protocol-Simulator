#------------------------------------------------------------------------
# SOURCE FILE:    trans.py
# PROGRAM:        File transfer application (Transmitter)
# FUNCTIONS:      send a file to server through “unreliable network”(UDP)
#                 Send and Wait protocol
#                 Implement sliding window
#                 Using socket timer to trigger retransmission 
#
# DATE:           December 4th, 2020
# REVISIONS:      N/A
#
# PROGRAMMER:     Hugh Song
#
# NOTES:
# Users need to input filename.
# Basic information we be implemented from config file:
# (IP addresses, port number, window size, logfile name)
#------------------------------------------------------------------------
import socket
import sys
import time
import threading
import myConfig as mcf
import Packet as pck
import ast 
import random
import select

# Window size 
winSize = mcf.settings["winSize"]
# Data length per packet
data_length = mcf.settings["dataLen"]
# Retransmit timer duration
timeout = mcf.settings["timeout"]
# Log file save all the prints  
trans_log = mcf.settings["trans_log"]
# Start time of the program 
start = time.perf_counter()
# IP address for this machine
transIP = mcf.myInfo["transIP"]
# emulator's IP address
networkIP = mcf.myInfo["networkIP"]
# port1 is bind on this machine
port1 = mcf.myInfo["port1"]
# packets will be sent through port3
port3 = mcf.myInfo["port3"]
# UDP socket
sockobj1 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sockobj1.setblocking(False)
sockobj1.bind(("", port1))

print("***** Transmitter Start *****")
print("IP: %s, Waiting on port: %s" % (transIP, port1))
with open(trans_log, 'w') as f:
    print("***** Transmitter Start *****", file=f)
    print("IP: %s, Waiting on port: %s" % (transIP, port1), file=f)

#------------------------------------------------------------------------
# FUNCTION sendFile
# ARGUMENTS: String filename
# RETURNS: void
# NOTES:
# After user enters filename, this function will be called
#------------------------------------------------------------------------
def sendFile(filename):
    # signal for wait
    global wait_for_acks
    # amount of acks that has received
    global ttl_acks
    # signal for EOF
    global end_of_file
    # packet's sequence number 
    global seqNum
    # packet's ack number 
    global ackNum
    # window list
    global window
    # signal for ack of EOF
    global recv_EOF
    # recent RTT
    global rtt1
    # estimate RTT
    global estRtt
    # estimate timer duration
    global devRtt
    
    # bytes read from a file
    data = ""
    ttl_acks = 0
    end_of_file = False
    wait_for_acks = False
    # packet's sequence number 
    seqNum = 0
    # packet's ack number 
    ackNum = 0
    # initialize sending window
    window = []
    recv_EOF = False
    rtt1 = True
    estRtt = 0
    devRtt = 0

    file = open(filename, 'rb')
    print("Start sending file ", filename)
    with open(trans_log, 'a+') as f:
            print("Start sending file %s" % filename, file=f)
    # read file until, whole file has be sent and all acks have be received
    while 1:
        # if sliding will is empty
        if not window:
            wait_for_acks = False
            print_window_status()
            if recv_EOF == True:
                break
            if end_of_file == True:
                eof_packet = pck.Packet("EOF", seqNum, ackNum, "file transfer complete", winSize)
                window.append(eof_packet.makeList())
                send_packet(eof_packet.makeList())
                print_packet(eof_packet.makeList())
                seqNum += 1
            else:
                for i in range (len(window), winSize):
                    data = file.read(data_length)

                    if not data:
                        end_of_file = True
                        continue

                    else: 
                        data_packet = pck.Packet("DATA", seqNum, ackNum, data, winSize)
                        window.append(data_packet.makeList())
                        send_packet(data_packet.makeList())
                        print_packet(data_packet.makeList())
                        seqNum += 1

            send_eot()

    file.close()
    print("***** File transfer complete *****")
    with open(trans_log, 'a+') as f:
        print("***** File transfer complete *****", file=f)

#------------------------------------------------------------------------
# FUNCTION send_eot
# ARGUMENTS: void
# RETURNS: void
# Description: to send a EOT packets to indicate that transimission has 
# temporarily finished
# NOTES:
# After send a full window of packets, this function will be called
# In the end of retransmission, this function will be called.
#------------------------------------------------------------------------
def send_eot():
    global wait_for_acks
    global recv_EOT
    global send_eot_time
    global seqNum

    # add an EOT packet to the end of the window    
    eot_packet = pck.Packet("EOT", seqNum, ackNum, "Trans eot", winSize)
    send_packet(eot_packet.makeList())
    print_packet(eot_packet.makeList())
    seqNum += 1
    recv_EOT = False
    send_eot_time = time.perf_counter()
    print_window_status()
    wait_for_acks = True
    getAck()

#------------------------------------------------------------------------
# FUNCTION send_packet
# ARGUMENTS: object packet
# RETURNS: void
# Description: send out one packet by using UDP socket
# NOTES:
# When we need to send out DATA, EOF, EOT packets, we will call this 
# function
#------------------------------------------------------------------------
def send_packet(packet):
    sockobj1.sendto(str(packet).encode(), (networkIP, port3))

#------------------------------------------------------------------------
# FUNCTION retransmit
# ARGUMENTS: void
# RETURNS: void
# Description: retransmit rest of Non-acked packets in window list
# NOTES:
# After timeout, this function will be invoked. 
#------------------------------------------------------------------------
def retransmit():
    global wait_for_acks
    # if there are still some packets in the window after timeout
    if window:
        wait_for_acks = False
        print_window_status()
        print("***** Timeout! Start retransmission *****")
        with open(trans_log, 'a+') as f:
            print("***** Timeout! Start retransmission *****", file=f)

        for packet in window:
            print_packet(packet)
            send_packet(packet)

        send_eot()

#------------------------------------------------------------------------
# FUNCTION getAck
# ARGUMENTS: void
# RETURNS: void
# Description: wait for ack
# NOTES:
# Once EOT packet is sent out, this function will be called.
# (transmitter in wait phase)
#------------------------------------------------------------------------
def getAck():
    global ttl_acks
    global wait_for_acks
    global ackNum
    global window
    global recv_eot_time
    global timeout
    global recv_EOT
    global recv_EOF
    global rtt1
    global estRtt
    global devRtt

    print("***** Waiting for ACK packets *****")
    with open(trans_log, 'a+') as f:
        print("***** Waiting for ACK packets *****", file=f)
    # start a timer
    sockobj1.settimeout(timeout)
    try:
        while wait_for_acks:
            data = sockobj1.recv(1024)
            ack = ast.literal_eval(data.decode())
            ttl_acks += 1
            print_packet(ack)
            if window:
                for packet in window:
                    if ack[2] == packet[1]:
                        window.remove(packet)
                       
            if ack[0] == "EOF":
                recv_EOF = True
            if ack[0] == "EOT":
                recv_EOT = True
                recv_eot_time = time.perf_counter()
                rtt = recv_eot_time - send_eot_time
                if rtt1:
                    estRtt = rtt
                    devRtt = rtt / 2
                    rtt1 = False
                else:
                    estRtt = (0.875 * estRtt) + (0.125 * rtt)
                    devRtt = (0.75 * devRtt) + 0.25 * abs(estRtt - rtt)
                timeout = round((estRtt + 4 * devRtt),5) 
                print("Sample RTT: %.5f" % rtt)
                print("Estimate RTT: %.5f" % estRtt)
                print("DevRTT: %.5f" % devRtt)
                print("RTO: %.5f" % timeout)
                with open(trans_log, 'a+') as f:
                    print("Sample RTT: %.5f" % rtt, file=f)
                    print("Estimate RTT: %.5f" % estRtt, file=f)
                    print("DevRTT: %.5f" % devRtt, file=f)
                    print("RTO: %.5f" % timeout, file=f)
                ackNum = ack[2]

            if not window and recv_EOT:
                wait_for_acks = False
                break

    except socket.timeout:
        wait_for_acks = False
        retransmit()

#------------------------------------------------------------------------
# FUNCTION print_packet
# ARGUMENTS: packet object
# RETURNS: void
# Description: print out packet content.
# NOTES:
# Packet content will be printed out on screen and written into log file
#------------------------------------------------------------------------
def print_packet(packet):
    print("Flag: %s, SeqNum: %s, AckNum: %s, Data: %s, WinSize: %s, Timestamp: %-10.5f" 
    % (packet[0], packet[1], packet[2], packet[3], packet[4], time.perf_counter() - start))
    with open(trans_log, 'a+') as f:
        print("Flag: %s, SeqNum: %s, AckNum: %s, Data: %s, WinSize: %s, Timestamp: %-10.5f" 
        % (packet[0], packet[1], packet[2], packet[3], packet[4], time.perf_counter() - start), file=f)

#------------------------------------------------------------------------
# FUNCTION print_window_status
# ARGUMENTS: void
# RETURNS: void
# Description: print out the condition of current window list
# NOTES:
# Show information on screen and written into log file
#------------------------------------------------------------------------
def print_window_status():
    print("-------------------------------------------------------------------------------------")
    print("Window size: %s, Packets in window: %d, Total packets sent: %d, Total acks received %d"
    % (winSize, len(window), seqNum, ttl_acks))
    print("-------------------------------------------------------------------------------------")
    with open(trans_log, 'a+') as f:
        print("-------------------------------------------------------------------------------------", file=f)
        print("Window size: %s, Packets in window: %d, Total packets sent: %d, Total acks received %d" 
        % (winSize, len(window), seqNum, ttl_acks), file=f)
        print("-------------------------------------------------------------------------------------", file=f)

#------------------------------------------------------------------------
# FUNCTION main
# ARGUMENTS: void
# RETURNS: void
# Description: this is my main application entry
#------------------------------------------------------------------------
def main():
    print("-------------------------------------------------------------------------------------")
    filename = input("Please enter the name of the file: ")
    sendFile(filename)

if __name__ == '__main__':
    main()

