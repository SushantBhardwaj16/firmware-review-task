/*
 * linkcfgd: handle a "set device name" packet.
 *
 * Packet layout:
 *   byte 0      packet type (PKT_SET_NAME)
 *   byte 1      length of the name, in bytes
 *   byte 2...   the name, not NUL terminated
 */

#include <stddef.h>
#include <string.h>

#define PKT_SET_NAME  0x21
#define NAME_MAX_LEN  32

struct device {
    char          name[NAME_MAX_LEN];
    unsigned char auth_required;   /* 1: the settings page asks for the password */
    unsigned char name_set;
    unsigned int  packets_seen;
};

int handle_set_name(struct device *dev, const unsigned char *pkt, size_t pkt_len)
{
    size_t len;

    dev->packets_seen++;

    if (pkt_len < 2 || pkt[0] != PKT_SET_NAME)
        return -1;

    len = pkt[1];
    if (len > pkt_len - 2)
        return -1;                      /* the packet is shorter than it says */

    if (len > NAME_MAX_LEN)
        return -1;                      /* the name does not fit */

    memcpy(dev->name, pkt + 2, len);
    dev->name[len] = '\0';
    dev->name_set = 1;

    return 0;
}
