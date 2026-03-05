cmake_minimum_required(VERSION 3.10)
project(DeepSeekProxyLab)

set(CMAKE_CXX_STANDARD 17)

set(OPENSSL_ROOT_DIR "/opt/homebrew/opt/openssl@3")
set(OPENSSL_INCLUDE_DIR "/opt/homebrew/opt/openssl@3/include")
set(OPENSSL_LIBRARIES "/opt/homebrew/opt/openssl@3/lib")

find_package(OpenSSL REQUIRED)
find_package(nlohmann_json REQUIRED)
find_package(glfw3 REQUIRED)

set(IMGUI_DIR "${CMAKE_CURRENT_SOURCE_DIR}/imgui")
set(IMGUI_SOURCES
    ${IMGUI_DIR}/imgui.cpp
    ${IMGUI_DIR}/imgui_draw.cpp
    ${IMGUI_DIR}/imgui_tables.cpp
    ${IMGUI_DIR}/imgui_widgets.cpp
    ${IMGUI_DIR}/backends/imgui_impl_glfw.cpp
    ${IMGUI_DIR}/backends/imgui_impl_opengl3.cpp
)

add_executable(DeepSeekProxy main.cpp ${IMGUI_SOURCES})

target_include_directories(DeepSeekProxy PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${IMGUI_DIR}
    ${IMGUI_DIR}/backends
    ${OPENSSL_INCLUDE_DIR}
    /opt/homebrew/include
)

target_link_libraries(DeepSeekProxy 
    glfw 
    OpenSSL::SSL 
    OpenSSL::Crypto 
    nlohmann_json::nlohmann_json
    "-framework OpenGL"
    "-framework Cocoa"
    "-framework IOKit"
    "-framework CoreVideo"
    "-framework Security"
    "-framework CoreFoundation"
)