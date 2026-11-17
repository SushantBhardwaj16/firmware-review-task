#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define NAME_MAX_LEN 32
struct device_state { unsigned char name[NAME_MAX_LEN]; volatile uint8_t auth_required; };
/* Isolated reproduction of the S5 boundary condition; not device firmware. */
int main(void) {
    struct device_state dev;
    unsigned char packet_name[NAME_MAX_LEN];
    const unsigned int len = NAME_MAX_LEN;
    memset(&dev, 0, sizeof(dev));
    memset(packet_name, 'A', sizeof(packet_name));
    dev.auth_required = 1;
    if (len > NAME_MAX_LEN) return 1; /* flawed original boundary check */
    memcpy(dev.name, packet_name, len);
    ((volatile unsigned char *)&dev)[len] = '\0'; /* mirrors dev->name[len] */
    printf("len=%u, auth_required=%u\n", len, dev.auth_required);
    return dev.auth_required == 0 ? 0 : 2;
}
