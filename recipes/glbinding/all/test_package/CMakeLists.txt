cmake_minimum_required(VERSION 3.21)
project(test_package LANGUAGES CXX)

find_package(glbinding REQUIRED)
find_package(glfw3 REQUIRED)
find_package(GTest REQUIRED)

add_executable(${PROJECT_NAME})
target_sources(
    ${PROJECT_NAME} PRIVATE
    src/AllVersions_test.cpp
    src/Boolean_compilation_test.cpp
    src/main.cpp
    src/Regression_test_82.cpp
    src/Regression_test_185.cpp
    src/Regression_test_198.cpp
    src/RingBuffer_test.cpp
    src/SharedBitfield_test.cpp
)
target_link_libraries(
    ${PROJECT_NAME} PRIVATE 
    glfw::glfw
    gtest::gtest
    glbinding::KHRplatform 
    glbinding::glbinding 
    glbinding::glbinding-aux 
) 
target_compile_definitions(
    ${PROJECT_NAME} PRIVATE
 	BUILD_GPU_TESTS
)

set(CMAKE_INSTALL_BINDIR bin)
install(TARGETS ${PROJECT_NAME} RUNTIME)
install(FILES $<TARGET_RUNTIME_DLLS:${PROJECT_NAME}> TYPE BIN)
