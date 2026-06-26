cmake_minimum_required(VERSION 3.16)
project(setup_auditor CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

find_package(Threads REQUIRED)

add_executable(setup_auditor
  src/main.cpp
  src/audit.cpp
  src/parse.cpp
)

target_include_directories(setup_auditor PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(setup_auditor PRIVATE Threads::Threads)
