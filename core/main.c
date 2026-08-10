#include <stdio.h>
#include "interfaceManager.h"
#include "dhcpClient.h"

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Incorrect argument number, just one interface please\n");
        return 1;
    }

    if (changeMac(2, argv) != 0) {
        fprintf(stderr, "MAC change failed, aborting\n");
        return 1;
    }

    /* DISCOVER, and retransmit once if the first attempt times out */
    if (dhcpClientRenew(2, argv) != 0 && dhcpClientRenew(2, argv) != 0) {
        fprintf(stderr, "No DHCP offer received\n");
        return 1;
    }

    return 0;
}
