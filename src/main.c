#include <stdio.h>
#include "interfaceManager.h"
#include "dhcpClient.h"

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Incorrect argument number, just one interface please\n");
        return 1;
    }

    changeMac(2, argv);
    dhcpClientRenew(2, argv); //set to 0.0.0.0
    dhcpClientRenew(2, argv); // get new IP addr
    return 0;
}
