#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <net/if.h>



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
  if (ioctl(sock, SIOCGIFFLAGS, &ifr) == -1){
    perror("SIOCGIFFLAGS");
    return -1;
  }

  close(sock);
  printf("Interface %s is now: %s\n", interfaceName, state ? "UP" : "DOWN");
  return 0;
}

int main(int argc, char *argv[]){
  if (argc != 3){
    fprintf(stderr, "Use: %s <interfaceName> <up|down>\n", argv[0]);
    return 1;
  }

  const char *interfaceName = argv[1];
  int state = 0;

  if (strcmp(argv[2], "up") == 0){
    state = 1;
  }else if (strcmp(argv[2], "down")==0){
    state = 0;
  } else{
    fprintf(stderr, "Invalid interface state, choose 'up' or 'down'\n");
    return 1;
  }

  if (setInterfaceState(interfaceName, state) != 0)
    return 1;

  return 0;
}
