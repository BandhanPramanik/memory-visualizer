#include <stdio.h>

int main(void)
{
    unsigned int num = 0x12345678;
    char* c = (char*) &num;
    int lilendian = (*c == 0x78) ? 1 : 0;
    unsigned int b;
    for (int i = 0; i < 4; i++)
    {
        b = (num & (0x000000FF << (8 * i))) >> (8 * i);
        printf("Byte %d", i + 1);
        if (lilendian && i == 0 || !lilendian && i == 3)
            printf(" (LSB)");
        if (lilendian && i == 3 || !lilendian && i == 0)
            printf(" (MSB)");
        printf(": 0x%x\n", b);
    }
}

