#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/if_arp.h>


void printMac(const unsigned char *mac) {
  printf("%02x:%02x:%02x:%02x:%02x:%02x",
         mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

int incrementAndSetMac(const char *interfaceName){
  int sock;
  struct ifreq ifr;
  unsigned char currentMac[6];
  unsigned char newMac[6];
  int i;

  sock = socket(AF_INET, SOCK_DGRAM, 0);
  if (sock==-1){
    perror("Bad socket");
    return -1;
  }

  memset(&ifr, 0, sizeof(ifr));
  strncpy(ifr.ifr_name, interfaceName, IFNAMSIZ-1);

  if (ioctl(sock, SIOCGIFHWADDR, &ifr) == -1){
    perror("SIOCGIFHWADDR (get MAC)");
    close (sock);
    return -1;
  }

  memcpy(currentMac, ifr.ifr_hwaddr.sa_data, 6);

  printf("Actual MAC of interface %s: ",interfaceName);
  printMac(currentMac);
  printf("\n");

  memcpy(newMac, currentMac, 6);
  int carry = 1;
  for (i = 5; i>=0; i--){
    int sum = (unsigned char)newMac[i] +carry;
    newMac[i] = sum & 0xFF;
    carry = sum >> 8;
    if (carry == 0) break;
  }

  if (carry){
    /*OVERFLOW*/
    printf("Warning: MAC overflow, setting to 00:00:00:00:00:00\n");
    memset(newMac, 0, 6);
  }

  printf("New MAC: ");
  printMac(newMac);
  printf("\n");

  ifr.ifr_hwaddr.sa_family = ARPHRD_ETHER;
  memcpy(ifr.ifr_hwaddr.sa_data, newMac, 6);

  if (ioctl(sock, SIOCSIFHWADDR, &ifr)==-1){
    perror("SIOCGIFHWADDR (change MAC)");
    close(sock);
    return -1;
  }

  printf("MAC is changed");

  close(sock);
  return 0;

}


int setInterfaceState(const char *interfaceName, int state)
{
  int sock;
  struct ifreq ifr;

  sock = socket(AF_INET, SOCK_DGRAM, 0);
  if (sock == -1){
    perror("Bad socket");
    return -1;
  }
  
  memset(&ifr, 0, sizeof(ifr));
  strncpy(ifr.ifr_name, interfaceName, IFNAMSIZ-1);

  /*Current flags*/
  if (ioctl(sock, SIOCGIFFLAGS, &ifr) == -1){
    perror("SIOCGIFFLAGS");
    close(sock);
    return -1;
  }

  if (state)
    ifr.ifr_flags |= IFF_UP;
  else 
    ifr.ifr_flags &= ~IFF_UP;

  /*Set changes*/
  if (ioctl(sock, SIOCSIFFLAGS, &ifr) == -1){
    perror("SIOCSIFFLAGS");
    return -1;
  }

  close(sock);
  printf("Interface %s is now: %s\n", interfaceName, state ? "UP" : "DOWN");
  return 0;
}

int main(int argc, char *argv[]){
  if (argc != 2){
    fprintf(stderr, "Use: %s <interfaceName>\n", argv[0]);
    return 1;
  }

  const char *interfaceName = argv[1];


  if (setInterfaceState(interfaceName, 0) != 0)
    return 1;
  if (incrementAndSetMac(interfaceName) != 0)
    return 1;
  if (setInterfaceState(interfaceName, 1) != 0)
    return 1;

  printf("Ended program\n");

  return 0;
}
