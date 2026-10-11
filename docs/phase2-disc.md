# Phase 2 — HP1 source identity

Local evidence recorded on 2026-09-30. Filename: Harry Potter and the Sorcerer's Stone (USA) (En,Fr,Es). These hashes identify the local source; no independent catalogue comparison is claimed.

This document preserves the evidence and conclusions available at the end of Phase 2. Later executable-loading findings are recorded in [the research notes](../RESEARCH.md) and do not alter the source identity established here.

One CUE track: `TRACK 01 MODE2/2352`, `INDEX 01 00:00:00`. BIN contains 256146 sectors of 2352 bytes.

## BIN

- Bytes: 602455392
- MD5: `93013f503df634f8a0bc7714e9e17a1f`
- SHA-1: `e833ddac575f2c500c8e3a6774f13706a5c76c4e`
- SHA-256: `09f04cfcd92904e00e62134d34f272bf377513b50889367412cc069972e6c97e`

## CUE

- Bytes: 120
- MD5: `69bfb949787afcbd0ac0d5cbef585538`
- SHA-1: `7e19d49f6daeac8b7daa32a40c218e278dcb1e61`
- SHA-256: `f4414a5af0167355469d4740e8ffe536b4a98205dda19d502e382c873d054b17`

## SYSTEM.CNF

- Bytes: 62
- MD5: `bee6b279cd8fea9d338a4eabf6a2dd82`
- SHA-1: `bab8066e812de09ac71543bc582acec81179374d`
- SHA-256: `9b9fb948563914809d80b02e5c109ea2ffcd6859a8241b62221f08d5ce29aa97`

## SLUS_014.15

- Bytes: 57344
- MD5: `103c3528c6dbc4da14383d1031ca46a0`
- SHA-1: `7e2e13dbff7144656b9ba150ba68e31b4e1d7381`
- SHA-256: `753368b404119634fa1a8563af76ec79cb56617b0e5b27e198afd3f1b75efc43`

## POTTER.DAT

- Bytes: 492177408
- MD5: `04a5d28527427d0772d7bef3d616aa0d`
- SHA-1: `20237ef96ab1666bbfc9fdf174f03489d8177a4f`
- SHA-256: `5607ae60315b27deb183edb6a514d095973d060c2e46c5d78cfff40014ba58b1`

## POTTER.DIR

- Bytes: 4044
- MD5: `20ae5664f00bbfbe201f3299706bc9e0`
- SHA-1: `93e533b8b420fa468ca2c7a0372220f518bd1ff8`
- SHA-256: `1e7658d31afe9416a033ea9582749885818522b597fe8eb5784e0b3e9f248ba2`

## Boot and executable header

SYSTEM.CNF selects `cdrom:\SLUS_014.15;1`, TCB=4, EVENT=10, STACK=801fff00.

PS-X EXE signature verified. Entry PC=0x00103DDC; GP=0; load address=0x00100000; payload size=0xD800; BSS address/size=0; stack base=0x801FFFF0; stack offset=0.

The load interval is [0x00100000, 0x0010D800). Header plus payload equals 57344 bytes. Preserve the raw addresses; do not silently substitute cached aliases.

## Extracted inventory

| File | Bytes |
|---|---:|
| POTTER.DAT | 492177408 |
| POTTER.DIR | 4044 |
| SLUS_014.15 | 57344 |
| SYSTEM.CNF | 62 |
| US.GAM | 432128 |
| ZDUMMY.DAT | 30000000 |
| MOVIES/EA.STR | 1775360 |

Dumpsxiso also produced `license_data.dat` (28032 bytes); treat this as an extraction artifact, not a confirmed filesystem entry.

At the end of Phase 2, the small boot executable and presence of US.GAM motivated investigating the loading chain. US.GAM was confirmed to have a PS-X EXE header, but the loading relationship had not yet been established. Phase 3 subsequently identified and dynamically observed the `Load`/`Exec` path from `SLUS_014.15` to `US.GAM`. Its bounded overlay review found no additional ordinary headered executable; raw or compressed code remains a bring-up risk rather than a confirmed feature.

## Additional identity checks

| File | CRC32 |
|---|---|
| BIN | 4b747faa |
| CUE | 5b983920 |
| SYSTEM.CNF | 57140c35 |
| SLUS_014.15 | 3001e810 |
| POTTER.DAT | 8b17b1cf |
| POTTER.DIR | b7617af7 |
| US.GAM | 0a31089f |

US.GAM: 432128 bytes; MD5 `1d89052b2521660b4bd717c4d7c25038`; SHA-1 `3bf3b834827ee680123fe40e1bd527479b806153`; SHA-256 `3335dc9d6f0078bd683f6c5baa37cc21700b326fe72d2910652c5a6c1d39fa5f`.

Its first 64 bytes confirm PS-X EXE, entry PC=0x0005B2C8, GP=0, load address=0x00010000, payload size=0x00069000, BSS address/size=0, stack base=0x801FFFF0, stack offset=0. Header plus payload equals file size; load interval [0x00010000, 0x00079000).

Dumpsxiso XML reports volume HARRY_POTTER, system/application PLAYSTATION, publisher ELECTRONIC_ARTS and creation timestamp 2001100412000000+0. It records filesystem order SYSTEM.CNF, SLUS_014.15, US.GAM, POTTER.DIR, POTTER.DAT, MOVIES/EA.STR, ZDUMMY.DAT and 150 dummy sectors. The XML does not include LBA attributes. A direct read of ISO9660 directory records provided the extents below.

## Verified ISO9660 extents

LBA is relative to track start. ISO byte sizes use 2048-byte logical blocks.

| File | LBA | ISO bytes |
|---|---:|---:|
| SYSTEM.CNF | 23 | 62 |
| SLUS_014.15 | 24 | 57344 |
| US.GAM | 52 | 432128 |
| POTTER.DIR | 263 | 4044 |
| POTTER.DAT | 265 | 492177408 |
| MOVIES/EA.STR | 240587 | 1556480 |
| ZDUMMY.DAT | 241347 | 30000000 |

EA.STR occupies 760 sectors: ISO length 760 × 2048 = 1556480, while the mixed-sector extraction contains 760 × 2336 = 1775360 bytes. These lengths are consistent with different sector representations, not an observed extraction truncation.

Phase 2 is complete: local source identity, boot metadata, executable headers, archive hashes and disc extents have been recorded. Independent catalogue matching is not claimed.

Retail files and local layout remain outside Git. Earlier ZIP archive hashes are not disc-image hashes.
