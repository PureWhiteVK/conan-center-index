#define PFD_IMPLEMENTATION
#include "portable-file-dialogs.h"

#include <iostream>

int main()
{
    // Check that a backend is available
    if (!pfd::settings::available())
    {
        std::cout << "Portable File Dialogs are not available on this platform.\n";
        return 1;
    }

    // Set verbosity to true
    pfd::settings::verbose(true);
    return 0;
}