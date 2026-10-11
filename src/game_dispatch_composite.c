#include "psx_runtime.h"

/* The boot program and US.GAM are generated as independent static providers.
 * Their source files are compiled with provider-specific API names; this file
 * preserves the runtime's existing single-dispatch ABI and selects the owner
 * by its exact generated address table. */
int boot_psx_game_address_in_text(uint32_t addr);
int boot_psx_game_text_native_ok(uint32_t addr);
int boot_psx_game_text_native_ok_full(uint32_t addr);
int boot_psx_dispatch_game_compiled(CPUState* cpu, uint32_t addr);
int boot_psx_game_is_function_entry(uint32_t addr);

int usgam_psx_game_address_in_text(uint32_t addr);
int usgam_psx_game_text_native_ok(uint32_t addr);
int usgam_psx_game_text_native_ok_full(uint32_t addr);
int usgam_psx_dispatch_game_compiled(CPUState* cpu, uint32_t addr);
int usgam_psx_game_is_function_entry(uint32_t addr);

static int boot_owns_pc(uint32_t addr) {
    /* Preserve the established boot-provider contract: OpenBIOS may hand off
     * through the KUSEG alias before the generated boot code normalizes its
     * own control flow. Its physical range cannot overlap US.GAM. */
    return boot_psx_game_address_in_text(addr);
}

static int usgam_owns_pc(uint32_t addr) {
    return addr < 0x00800000u && usgam_psx_game_address_in_text(addr);
}

int psx_game_address_in_text(uint32_t addr) {
    return boot_owns_pc(addr) || usgam_owns_pc(addr);
}

int psx_game_text_native_ok(uint32_t addr) {
    if (boot_owns_pc(addr))
        return boot_psx_game_text_native_ok(addr);
    if (usgam_owns_pc(addr))
        return usgam_psx_game_text_native_ok(addr);
    return 0;
}

int psx_game_text_native_ok_full(uint32_t addr) {
    if (boot_owns_pc(addr))
        return boot_psx_game_text_native_ok_full(addr);
    if (usgam_owns_pc(addr))
        return usgam_psx_game_text_native_ok_full(addr);
    return 0;
}

int psx_dispatch_game_compiled(CPUState* cpu, uint32_t addr) {
    if (boot_owns_pc(addr)) return boot_psx_dispatch_game_compiled(cpu, addr);
    if (usgam_owns_pc(addr)) return usgam_psx_dispatch_game_compiled(cpu, addr);
    return 0;
}

int psx_game_is_function_entry(uint32_t addr) {
    return (boot_owns_pc(addr) && boot_psx_game_is_function_entry(addr)) ||
           (usgam_owns_pc(addr) && usgam_psx_game_is_function_entry(addr));
}
