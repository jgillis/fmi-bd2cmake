#include <stdio.h>
#include <math.h>

int main_function() {
    printf("FMI Version: %d\n", FMI_VERSION);
#ifdef DEBUG
    printf("Debug mode enabled\n");
#endif
#ifdef PLATFORM_LINUX
    printf("Platform: Linux\n");
#endif
    double result = sqrt(16.0);
    printf("sqrt(16) = %f\n", result);
    return 0;
}