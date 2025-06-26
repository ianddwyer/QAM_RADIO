# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 21:52:01 2025

@author: Eian
"""





import socket
import time
import sys

UDP_IP = "127.0.0.1"  # Use local host gateway for routing (similar to how done in hosts file)
UDP_PORT = 5005       # Change this port if other app uses it
PACKET_SIZE = 252     # Fixed packet size, may wish to change later....

def messenger():

   # Create a UDP socket
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   print("Type 'exit' to exit messenger\n")
   while True:
       user_input = ""

       user_input = input("TX: ").strip()
       if user_input == "exit":
           
           print("Exiting...")
           sock.close()
           exit()
           break
       else:

           # Convert input to bytes
           data = user_input.encode()
    
           # Zero-pad or split to PACKET_SIZE
           if len(data) > PACKET_SIZE:
               data = data.ljust(len(data)+(252-len(data)%PACKET_SIZE), b'\x00')
               for i in range(int(len(data)/PACKET_SIZE)):
                   datasend = data[i*PACKET_SIZE:((i+1)*PACKET_SIZE)]
                   sock.sendto(datasend, (UDP_IP, int(UDP_PORT)))
           else:
               data = data.ljust(PACKET_SIZE, b'\x00')  # Zero-pad if too short
               sock.sendto(data, (UDP_IP, int(UDP_PORT)))




if __name__ == "__main__":
  messenger()