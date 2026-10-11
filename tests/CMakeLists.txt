cmake_minimum_required(VERSION 3.20)
project(HP1RecompStandaloneTests LANGUAGES C)

include(CTest)

add_executable(game-dispatch-composite-test
    game_dispatch_composite_test.c
    ../src/game_dispatch_composite.c)
target_include_directories(game-dispatch-composite-test PRIVATE support)
add_test(NAME game-dispatch-composite COMMAND game-dispatch-composite-test)
