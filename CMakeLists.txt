cmake_minimum_required(VERSION 3.20)
project(HP1Recomp LANGUAGES C CXX)

include(CTest)

set(PSXRECOMP_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/psxrecomp" CACHE PATH
    "Path to the pinned PSXRecomp framework checkout")
if(NOT EXISTS "${PSXRECOMP_ROOT}/runtime/runtime.cmake")
    message(FATAL_ERROR
        "PSXRecomp runtime is missing at ${PSXRECOMP_ROOT}.\n"
        "Initialize the pinned submodule or set -DPSXRECOMP_ROOT=<path>.")
endif()

# Keep the first bring-up headless/minimal. The optional launcher can be added
# after the native boot path is proven rather than becoming a Phase 4 dependency.
set(PSX_RECOMP_UI OFF CACHE BOOL "Build the optional recomp-ui launcher" FORCE)
include("${PSXRECOMP_ROOT}/runtime/runtime.cmake")

psxrecomp_add_game_runtime(psx-runtime
    WINDOW_TITLE "Harry Potter and the Sorcerer's Stone Recompiled"
    DEFAULT_GAME_CONFIG_PATH "game.toml"
    MAX_PLAYERS 1
    GEN_MARKER "generated/SLUS_014.15_dispatch.c"
    GEN_FULL_GLOB "generated/SLUS_014.15_full_*.c"
    PRELOADED_MODS_DIR "NONE"
)

# Phase 6: the boot EXE and guest-loaded US.GAM coexist as independent static
# providers. Generated retail-derived C remains ignored. Reconfigure after
# generating US.GAM with --runtime-code-segment kuseg.
file(GLOB HP1_BOOT_GENERATED CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/generated/SLUS_014.15_full_*.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/generated/SLUS_014.15_dispatch.c")
file(GLOB HP1_USGAM_GENERATED CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/generated/secondary/US.GAM_full_*.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/generated/secondary/US.GAM_dispatch.c")

if(HP1_USGAM_GENERATED)
    set(_boot_dispatch_defs
        psx_game_address_in_text=boot_psx_game_address_in_text
        psx_game_text_native_ok=boot_psx_game_text_native_ok
        psx_game_text_native_ok_full=boot_psx_game_text_native_ok_full
        psx_dispatch_game_compiled=boot_psx_dispatch_game_compiled
        psx_game_is_function_entry=boot_psx_game_is_function_entry)
    set(_usgam_dispatch_defs
        psx_game_address_in_text=usgam_psx_game_address_in_text
        psx_game_text_native_ok=usgam_psx_game_text_native_ok
        psx_game_text_native_ok_full=usgam_psx_game_text_native_ok_full
        psx_dispatch_game_compiled=usgam_psx_dispatch_game_compiled
        psx_game_is_function_entry=usgam_psx_game_is_function_entry)
    set_source_files_properties(${HP1_BOOT_GENERATED}
        PROPERTIES COMPILE_DEFINITIONS "${_boot_dispatch_defs}")
    set_source_files_properties(${HP1_USGAM_GENERATED}
        PROPERTIES GENERATED TRUE COMPILE_DEFINITIONS "${_usgam_dispatch_defs}")
    target_sources(psx-runtime PRIVATE
        ${HP1_USGAM_GENERATED}
        "${CMAKE_CURRENT_SOURCE_DIR}/src/game_dispatch_composite.c")
else()
    message(WARNING
        "US.GAM native provider is absent; runtime retains interpreted fallback. "
        "Generate it under generated/secondary with --runtime-code-segment kuseg.")
endif()

add_custom_command(TARGET psx-runtime POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${CMAKE_CURRENT_SOURCE_DIR}/game.toml"
        "$<TARGET_FILE_DIR:psx-runtime>/game.toml"
    COMMENT "Staging HP1 game configuration"
    VERBATIM)

if(BUILD_TESTING)
    add_executable(game-dispatch-composite-test
        tests/game_dispatch_composite_test.c
        src/game_dispatch_composite.c)
    target_include_directories(game-dispatch-composite-test PRIVATE
        "${CMAKE_CURRENT_SOURCE_DIR}/tests/support")
    add_test(NAME game-dispatch-composite COMMAND game-dispatch-composite-test)
endif()
