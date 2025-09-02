#include <stdio.h>
#include <stdint.h>

int main(void)
{
    uint32_t num = 0x12345678;
    char* c = (char*) &num;
    int lilendian = (*c == 0x78) ? 1 : 0;
    uint32_t b;
	char output[200];
	int len = 0;
	// The snprintf logic is not that important here...
    for (int i = 0; i < 4; i++)
    {
        b = (num & (0x000000FF << (8 * i))) >> (8 * i);
        len += snprintf(output + len, sizeof(output) - len, "Byte %d", i + 1);
        if (lilendian && i == 0 || !lilendian && i == 3)
            len += snprintf(output + len, sizeof(output) - len, " (LSB)");
        if (lilendian && i == 3 || !lilendian && i == 0)
            len += snprintf(output + len, sizeof(output) - len, " (MSB)");
        len += snprintf(output + len, sizeof(output) - len, ": 0x%x\n", b);
    }
}

