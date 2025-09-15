#include <iostream>
#include <string>

extern "C" {
    int cpp_model_function() {
        std::string message = "Hello from C++ FMI model!";
        std::cout << message << std::endl;
        return 0;
    }
}