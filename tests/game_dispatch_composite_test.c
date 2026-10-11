#include "psx_runtime.h"

#ifdef NDEBUG
#undef NDEBUG
#endif
#include <assert.h>
#include <stdint.h>

int psx_game_address_in_text(uint32_t addr);
int psx_game_text_native_ok(uint32_t addr);
int psx_game_text_native_ok_full(uint32_t addr);
int psx_dispatch_game_compiled(CPUState* cpu, uint32_t addr);
int psx_game_is_function_entry(uint32_t addr);

int boot_psx_game_address_in_text(uint32_t addr) {
    uint32_t phys = addr & 0x1fffffffu;
    return phys >= 0x00100000u && phys < 0x0010d800u;
}
int boot_psx_game_text_native_ok(uint32_t addr) { return addr == 0x80100000u ? 11 : 0; }
int boot_psx_game_text_native_ok_full(uint32_t addr) { return addr == 0x80100000u ? 12 : 0; }
int boot_psx_dispatch_game_compiled(CPUState* cpu, uint32_t addr) {
    (void)cpu;
    return addr == 0x80100000u ? 13 : 0;
}
int boot_psx_game_is_function_entry(uint32_t addr) { return addr == 0x80100000u; }

int usgam_psx_game_address_in_text(uint32_t addr) {
    uint32_t phys = addr & 0x1fffffffu;
    return phys >= 0x00010000u && phys < 0x00079000u;
}
int usgam_psx_game_text_native_ok(uint32_t addr) { return addr == 0x00010000u ? 21 : 0; }
int usgam_psx_game_text_native_ok_full(uint32_t addr) { return addr == 0x00010000u ? 22 : 0; }
int usgam_psx_dispatch_game_compiled(CPUState* cpu, uint32_t addr) {
    (void)cpu;
    return addr == 0x00010000u ? 23 : 0;
}
int usgam_psx_game_is_function_entry(uint32_t addr) { return addr == 0x00010000u; }

int main(void) {
    assert(psx_game_address_in_text(0x80100000u));
    assert(psx_game_text_native_ok(0x80100000u) == 11);
    assert(psx_game_text_native_ok_full(0x80100000u) == 12);
    assert(psx_dispatch_game_compiled(0, 0x80100000u) == 13);
    assert(psx_game_is_function_entry(0x80100000u));

    assert(psx_game_address_in_text(0x00010000u));
    assert(psx_game_text_native_ok(0x00010000u) == 21);
    assert(psx_game_text_native_ok_full(0x00010000u) == 22);
    assert(psx_dispatch_game_compiled(0, 0x00010000u) == 23);
    assert(psx_game_is_function_entry(0x00010000u));

    /* US.GAM is deliberately KUSEG-only even though its generated provider
     * normalizes aliases internally. The composite boundary owns that rule. */
    assert(!psx_game_address_in_text(0x80010000u));
    assert(!psx_game_text_native_ok(0x80010000u));
    assert(!psx_game_text_native_ok_full(0x80010000u));
    assert(!psx_dispatch_game_compiled(0, 0x80010000u));
    assert(!psx_game_is_function_entry(0x80010000u));

    assert(!psx_game_address_in_text(0x00079000u));
    assert(!psx_game_address_in_text(0x0010d800u));
    assert(!psx_game_address_in_text(0x00200000u));
    return 0;
}
