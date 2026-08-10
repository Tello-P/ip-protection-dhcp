#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/if_arp.h>
#include <time.h>


void printMac(const unsigned char *mac) {
  printf("%02x:%02x:%02x:%02x:%02x:%02x",
         mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

/*
 * Draw a fresh MAC. Every byte is random, so the real OUI is not preserved and
 * two addresses cannot be linked. Octet 0 gets the locally-administered bit
 * (0x02) set and the multicast bit (0x01) cleared - the kernel refuses a
 * multicast source address.
 */
static void randomizeMac(unsigned char *mac){
  int i;

  for (i = 0; i < 6; i++)
    mac[i] = (unsigned char)(rand() & 0xFF);

  mac[0] = (mac[0] & 0xFC) | 0x02;
}

int randomizeAndSetMac(const char *interfaceName){
  int sock;
  struct ifreq ifr;
  unsigned char currentMac[6];
  unsigned char newMac[6];

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

  srand((unsigned int)(time(NULL) ^ getpid()));
  randomizeMac(newMac);

  printf("New MAC: ");
  printMac(newMac);
  printf("\n");

  ifr.ifr_hwaddr.sa_family = ARPHRD_ETHER;
  memcpy(ifr.ifr_hwaddr.sa_data, newMac, 6);

  if (ioctl(sock, SIOCSIFHWADDR, &ifr)==-1){
    perror("SIOCSIFHWADDR (change MAC)");
    close(sock);
    return -1;
  }

  printf("MAC is changed\n");

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
    close(sock);
    return -1;
  }

  close(sock);
  printf("Interface %s is now: %s\n", interfaceName, state ? "UP" : "DOWN");
  return 0;
}

int changeMac(int argc, char *argv[]){
  if (argc != 2){
    fprintf(stderr, "Use: %s <interfaceName>\n", argv[0]);
    return 1;
  }

  const char *interfaceName = argv[1];


  if (setInterfaceState(interfaceName, 0) != 0)
    return 1;
  if (randomizeAndSetMac(interfaceName) != 0){
    /* Bring the link back up so a failed rewrite does not leave it down */
    setInterfaceState(interfaceName, 1);
    return 1;
  }
  if (setInterfaceState(interfaceName, 1) != 0)
    return 1;

  printf("Ended program\n");

  return 0;
}
