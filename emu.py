#------------------------------------------------------------------------
# SOURCE FILE:    emu.py
# PROGRAM:        File transfer application (Network emulator)
# FUNCTIONS:      Using bit error rate and delay time to imitate different 
#                 network condition.
#                 Bit error rate (0 to 100); as number increasing, packets 
#                 have bigger chance being dropped.
#                 delay time (in ms)
#
# DATE:           December 4th, 2020
# REVISIONS:      N/A
#
# PROGRAMMER:     Hugh Song
#
# NOTES:
# Users need to input Bit error rate and delay time.
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
# transmitter's IP address
transIP = mcf.myInfo["transIP"]
# receiver's IP address
recvIP = mcf.myInfo["recvIP"]
# IP address for this machine
networkIP = mcf.myInfo["networkIP"]
# packets will be sent through port1 to transmitter
port1 = mcf.myInfo["port1"]
# port3 is bind on this machine
port2 = mcf.myInfo["port2"]
# packets will be sent through port3 to receiver
port3 = mcf.myInfo["port3"]
# UDP socket
sockobj3 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sockobj3.bind(("", port3))
# log file save all the prints  
emu_log = mcf.settings["emu_log"]
# start time of the program 
start = time.perf_counter()

#------------------------------------------------------------------------
# FUNCTION recv_packets
# ARGUMENTS: void
# RETURNS: void
# Description: Wait and receive packets from one side until receive 
#              EOT packet. Packet will be added into a temp list.
# NOTES:
# After get user input, this function will be invoked. (wait phase)
#------------------------------------------------------------------------
def recv_packets():
    # bit error rate(0 to 100)
    global ber
    # how long each packet will be delayed (in ms)
    global avg_dly
    # amount of packets that has received
    global ttl_packets
    # amount of packets that has dropped
    global ttl_drop
    # temp list
    global tmplist
    # totle Amount of data packets
    global ttl_data_pkt

    ber = int(bit_error_rate)
    avg_dly = int(average_delay)
    ttl_packets = 0
    ttl_data_pkt = 0
    ttl_drop = 0
    tmplist = []

    while 1:
        data, addr = sockobj3.recvfrom(1024)
        packet = ast.literal_eval(data.decode())
        print_packet(packet)
        ttl_packets += 1
        ip = addr[0]
        if packet[0] == "EOF":
            tmplist.append(packet)
        elif packet[0] == "EOT":
            tmplist.append(packet)
            forward_packet(ip, tmplist)
            tmplist=[]
        else:
            ttl_data_pkt += 1
            r = random.randint(0, 99)
            if r >= ber:
                tmplist.append(packet)
            else:
                ttl_drop += 1
                print('***** Packet dropped *****')
                with open(emu_log, 'a+') as f:
                    print("***** Packet dropped *****", file=f)

#------------------------------------------------------------------------
# FUNCTION forward_packet
# ARGUMENTS: String src, object packets
# RETURNS: void
# Description: 1.iterate temp list, randomlly drop packets according to BER
#              2.Use src ip to determine sending direction
#              3.Send out packets
# NOTES:
# When we get EOT packet, this function will be called.(send phase)
#------------------------------------------------------------------------
def forward_packet(src, packets):
    print("-------------------------------------------------------------------------------------")
    print("***** Start forwarding *****")
    with open(emu_log, 'a+') as f:
        print("-------------------------------------------------------------------------------------", file=f)
        print("***** Start forwarding *****", file=f)
    if src == transIP:
        for pkt in packets:
            time.sleep(avg_dly/1000)
            print_packet(pkt)
            sockobj3.sendto(str(pkt).encode(), (recvIP, port2))
    elif src == recvIP:
        for pkt in packets:
            time.sleep(avg_dly/1000)
            print_packet(pkt)
            sockobj3.sendto(str(pkt).encode(), (transIP, port1))

    print("-------------------------------------------------------------------------------------")
    print("Total packets received: %d, total packets forwarded %d, total packets dropped: %d, drop rate: %-4.2f%%" 
    % (ttl_packets, (ttl_packets-ttl_drop), ttl_drop, (ttl_drop*100)/ttl_data_pkt))
    print("-------------------------------------------------------------------------------------")
    print("***** Start receiving *****")
    with open(emu_log, 'a+') as f:
        print("-------------------------------------------------------------------------------------", file=f)
        print("Total packets received: %d, total packets forwarded %d, total packets dropped: %d, drop rate: %-4.2f%%" 
        % (ttl_packets, (ttl_packets-ttl_drop), ttl_drop, (ttl_drop*100)/ttl_data_pkt), file=f)
        print("-------------------------------------------------------------------------------------", file=f)
        print("***** Start receiving *****", file=f)

#------------------------------------------------------------------------
# FUNCTION print_packet
# ARGUMENTS: packet object
# RETURNS: void
# Description: print out packet content.
# NOTES:
# Packet content will be printed out on screen and written into log file.
#------------------------------------------------------------------------
def print_packet(packet):
    print("Flag: %s, SeqNum: %s, AckNum: %s, Data: %s, WinSize: %s, Timestamp: %-10.5f" 
    % (packet[0], packet[1], packet[2], packet[3], packet[4], time.perf_counter() - start))
    with open(emu_log, 'a+') as f:
        print("Flag: %s, SeqNum: %s, AckNum: %s, Data: %s, WinSize: %s, Timestamp: %-10.5f" 
        % (packet[0], packet[1], packet[2], packet[3], packet[4], time.perf_counter() - start), file=f)

#------------------------------------------------------------------------
# FUNCTION main
# ARGUMENTS: void
# RETURNS: void
# Description: this is my main application entry
# User need to enter bit_error_rate and average_delay time 
#------------------------------------------------------------------------
def main():
    global bit_error_rate
    global average_delay

    bit_error_rate = input("Please enter a number for bit error rate [0-100](%): ")
    average_delay = input("Please enter the average delay per packet (ms): ")
    print("-------------------------------------------------------------------------------------")
    print("Emulator is ready, IP: %s, waiting on port: %s" % (networkIP, port3))
    print("-------------------------------------------------------------------------------------")
    print("***** Start receiving *****")
    with open(emu_log, 'w') as f:
        print("***** Emulator Start *****", file=f)
        print("IP: %s, waiting on port: %s" % (networkIP, port3), file=f)
        print("Bit error rate: %s%%, Average delay: %sms" % (bit_error_rate, average_delay), file=f)
        print("-------------------------------------------------------------------------------------", file=f)
        print("***** Start receiving *****", file=f)

    recv_packets()


if __name__ == '__main__':
    main()



