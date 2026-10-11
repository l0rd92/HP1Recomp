#!/usr/bin/env python3
"""Inspect HP1 PS1 DPSX actor records without extracting retail data.

The layout implemented here follows the bounded HP1 US.GAM loader at
0x00017754.  Offsets reported by this tool are relative to the WAD and to the
DPSX payload (the bytes immediately after the eight-byte chunk header).
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import struct
from collections import deque
from dataclasses import dataclass
from pathlib import Path


class FormatError(ValueError):
    pass


@dataclass(frozen=True)
class Chunk:
    tag: str
    header_offset: int
    payload_offset: int
    payload_size: int


class View:
    def __init__(self, data: bytes):
        self.data = data

    def require(self, offset: int, size: int, label: str) -> None:
        if offset < 0 or size < 0 or offset + size > len(self.data):
            raise FormatError(
                f"{label} exceeds DPSX payload: offset=0x{offset:X}, size=0x{size:X}"
            )

    def u16(self, offset: int, label: str = "u16") -> int:
        self.require(offset, 2, label)
        return struct.unpack_from("<H", self.data, offset)[0]

    def s16(self, offset: int, label: str = "s16") -> int:
        self.require(offset, 2, label)
        return struct.unpack_from("<h", self.data, offset)[0]

    def s32(self, offset: int, label: str = "s32") -> int:
        self.require(offset, 4, label)
        return struct.unpack_from("<i", self.data, offset)[0]

    def u32(self, offset: int, label: str = "u32") -> int:
        self.require(offset, 4, label)
        return struct.unpack_from("<I", self.data, offset)[0]

    def ascii_z(self, offset: int, limit: int, label: str = "ASCII string") -> str:
        if offset < 0 or offset >= limit:
            raise FormatError(f"{label} starts outside DPSX data: 0x{offset:X}")
        end = self.data.find(b"\0", offset, min(limit, offset + 128))
        if end < 0:
            raise FormatError(f"unterminated {label} at DPSX +0x{offset:X}")
        raw = self.data[offset:end]
        if not raw or any(byte < 0x20 or byte > 0x7E for byte in raw):
            raise FormatError(f"invalid {label} at DPSX +0x{offset:X}")
        return raw.decode("ascii")


MAX_HP1_STRATEGY_OPCODE = 520
ONE_WORD_PAYLOAD_OPCODES = {69, 177, 210, 350, 435}
TWO_WORD_PAYLOAD_OPCODES = {12, 207}
EVENT_TABLE_OPCODES = {2, 3}
EVENT_ENTRY_PAYLOAD_OPCODES = {69, 226}
CALL_OPCODES = {16, 17}
CONDITIONAL_BRANCH_OPCODES = {18, 19, 20, 21}
UNCONDITIONAL_BRANCH_OPCODES = {22, 43}
SWITCH_OPCODE = 23
RETURN_OPCODE = 178
YIELD_OPCODES = {16, 18, 19, 43, 138}
TERMINAL_OPCODES = {179}
DEFAULT_MAX_CFG_CONTEXT_STATES = 20000


def read_window(path: Path, offset: int, length: int | None) -> bytes:
    with path.open("rb") as source:
        source.seek(offset)
        return source.read() if length is None else source.read(length)


def chunks(data: bytes) -> list[Chunk]:
    result: list[Chunk] = []
    # HP1 WAD entries begin with a four-byte padded-size field.  Accept a
    # bare chunk stream as well so an already isolated WAD remains usable.
    cursor = 0
    if len(data) >= 8 and not all(0x20 <= byte <= 0x7E for byte in data[:4]):
        cursor = 4
    while cursor + 8 <= len(data):
        raw_tag, size = struct.unpack_from("<4sI", data, cursor)
        try:
            tag = raw_tag[::-1].decode("ascii")
        except UnicodeDecodeError as exc:
            raise FormatError(f"invalid chunk tag at WAD offset 0x{cursor:X}") from exc
        payload = cursor + 8
        if payload + size > len(data):
            raise FormatError(f"{tag} chunk at 0x{cursor:X} exceeds the WAD window")
        result.append(Chunk(tag, cursor, payload, size))
        cursor = payload + size
        if tag.strip() == "END":
            break
    return result


def skip_model_set(view: View, cursor: int) -> int:
    count = view.u32(cursor + 0x808, "initial model count")
    cursor += 0x80C
    for index in range(count):
        view.require(cursor, 0x68, f"initial model {index}")
        vertex_count = view.u32(cursor + 0x48)
        face_count = view.u32(cursor + 0x54)
        extra_count = sum(view.u16(cursor + item) for item in (0x5C, 0x5E, 0x60))
        cursor += 0x68 + vertex_count * 16 + face_count * 20 + extra_count * 32
    return cursor


def skip_animation_sets(view: View, cursor: int) -> int:
    set_count = view.u32(cursor, "animation-set count")
    cursor += 4
    for set_index in range(set_count):
        base = cursor
        view.require(base, 0x30, f"animation set {set_index}")
        entry_count = view.u32(base + 8)
        cursor = base + 0x30 + view.u32(base) * 4
        if view.u32(base + 0x0C) != 1:
            cursor += entry_count * 8
        has_aux = view.u32(base + 0x10)
        if has_aux:
            cursor += entry_count * 4
        cursor += entry_count * 4
        frame_set_count = view.u32(base + 0x20)
        if frame_set_count:
            cursor += frame_set_count * 4
        for entry_index in range(entry_count):
            if has_aux:
                cursor += has_aux * 8 if entry_index == 0 else (has_aux + (has_aux & 1)) * 2
            if frame_set_count == 0:
                cursor += view.u32(base + 0x18) * 24
        if frame_set_count:
            cursor += frame_set_count * view.u32(base + 0x18) * 16
    return cursor


def locate_level_header(view: View) -> tuple[int, int, int]:
    flags = view.u32(0, "DPSX flags")
    cursor = skip_model_set(view, 0)
    cursor = skip_animation_sets(view, cursor)

    if flags & 0x40000:
        cursor += 4 + (view.u32(cursor) & 0xFFFF) * 0xC00

    list_count = view.u32(cursor, "variable-list count")
    cursor += 4
    for _ in range(list_count):
        cursor += (view.u32(cursor) + 1) * 4

    model_count = view.u32(cursor, "secondary model count")
    cursor += 4
    records = cursor
    data_cursor = records + model_count * 0x68
    for index in range(model_count):
        record = records + index * 0x68
        view.require(record, 0x68, f"secondary model {index}")
        data_cursor += view.u32(record + 0x48) * 8
        data_cursor += view.u32(record + 0x54) * 12
        data_cursor += sum(view.u16(record + item) for item in (0x5C, 0x5E, 0x60)) * 32
    cursor = data_cursor

    if flags & 4:
        cursor += 4
    if flags & 0x10:
        cursor += 4

    if view.u32(cursor, "level-data marker") == 0:
        raise FormatError("DPSX has no level/actor block")
    level_header = cursor + 8 + view.u32(cursor + 4, "level-header displacement") * 4
    view.require(level_header, 0x98, "level header")
    return flags, cursor, level_header


def locate_actor_table(view: View, flags: int, level: int) -> tuple[int, int]:
    type_count = view.u32(level, "strategy-type count")
    actor_count = view.s16(level + 4, "actor count")
    if actor_count < 0:
        raise FormatError(f"negative actor count: {actor_count}")

    pointer_count = view.u32(level + 0x0C)
    cursor = level + 0x98 + pointer_count * 4 + type_count * 8
    if flags & 0x1000:
        view.require(cursor, 0x104, "extended visibility header")
        cursor += 0x104 + view.u32(cursor + 0x100) * 4
    else:
        cursor += type_count * 8

    if view.u32(cursor) == 0x00777666:
        cursor += 4 + (view.u32(level + 0x10) * view.u32(level + 0x14) // 2) * 4

    cursor += type_count * 24
    cursor += type_count * 4
    cursor += view.u16(level + 0x18) * 0x54
    cursor += view.u32(level + 0x20) * 0x24
    view.require(cursor, actor_count * 0x40, "actor table")
    return actor_count, cursor


def next_strategy_instruction(view: View, offset: int, limit: int) -> int:
    """Return the next sequential instruction offset using verified formats."""
    raw = view.u32(offset, "Strategy instruction")
    opcode = raw & 0xFFFF
    if opcode > MAX_HP1_STRATEGY_OPCODE:
        raise FormatError(f"invalid Strategy opcode {opcode} at DPSX +0x{offset:X}")

    if opcode in ONE_WORD_PAYLOAD_OPCODES:
        next_offset = offset + 8
    elif opcode in TWO_WORD_PAYLOAD_OPCODES:
        next_offset = offset + 12
    elif opcode in EVENT_TABLE_OPCODES:
        entry_count = view.u32(offset + 4, "Strategy event-table count")
        next_offset = offset + 8
        for entry_index in range(entry_count):
            entry = view.u32(next_offset, f"Strategy event-table entry {entry_index}")
            next_offset += 4
            if (entry & 0xFFFF) in EVENT_ENTRY_PAYLOAD_OPCODES:
                next_offset += 4
    else:
        next_offset = offset + 4

    if next_offset > limit:
        raise FormatError(f"Strategy instruction at +0x{offset:X} exceeds level-data boundary")
    return next_offset


def strategy_instruction_words(view: View, offset: int, limit: int) -> list[int]:
    """Return the complete verified instruction, including inline payload words."""
    next_offset = next_strategy_instruction(view, offset, limit)
    return [view.u32(cursor) for cursor in range(offset, next_offset, 4)]


def strategy_extent(view: View, root: int, limit: int) -> dict[str, object]:
    cursor = root
    instruction_count = 0
    while cursor + 4 <= limit:
        raw = view.u32(cursor, "Strategy instruction or boundary")
        if (raw & 0xFFFF) > MAX_HP1_STRATEGY_OPCODE:
            return {
                "root_dpsx_offset": root,
                "end_dpsx_offset": cursor,
                "byte_length": cursor - root,
                "instruction_count": instruction_count,
                "boundary_raw": raw,
                "boundary_reason": "low16 exceeds confirmed opcode range",
            }
        try:
            cursor = next_strategy_instruction(view, cursor, limit)
        except FormatError as exc:
            return {
                "root_dpsx_offset": root,
                "end_dpsx_offset": cursor,
                "byte_length": cursor - root,
                "instruction_count": instruction_count,
                "boundary_raw": raw,
                "boundary_reason": f"unconfirmed instruction layout: {exc}",
            }
        instruction_count += 1
    return {
        "root_dpsx_offset": root,
        "end_dpsx_offset": cursor,
        "byte_length": cursor - root,
        "instruction_count": instruction_count,
        "boundary_raw": 0,
        "boundary_reason": "level-data boundary",
    }


def signed_immediate(raw: int) -> int:
    return struct.unpack("<h", struct.pack("<H", raw >> 16))[0]


def strategy_root_name(view: View, root: int, limit: int) -> str | None:
    if (view.u32(root, "Strategy root") & 0xFFFF) != 207:
        return None
    string_offset = root + 12 + view.s32(root + 8, "Strategy name displacement")
    try:
        return view.ascii_z(string_offset, limit, "Strategy name")
    except FormatError:
        return None


def switch_targets(view: View, next_offset: int, immediate: int, limit: int) -> list[int]:
    table = next_offset + immediate * 4
    if table < 0 or table + 8 > limit:
        raise FormatError(f"switch table outside Strategy data at +0x{table:X}")
    entry_count = view.u32(table + 4, "Strategy switch entry count")
    cursor = table + 8
    targets: list[int] = []
    for entry_index in range(entry_count):
        case_word = view.u32(cursor, f"Strategy switch case {entry_index}")
        if (case_word & 0xFFFF) == 68:
            delta_offset = cursor + 4
            cursor += 8
        else:
            delta_offset = cursor + 8
            cursor += 12
        delta = view.s32(delta_offset, f"Strategy switch delta {entry_index}")
        targets.append(next_offset + delta * 4)
    return targets


def build_strategy_cfg(
    view: View,
    roots: list[int],
    limit: int,
    max_context_states: int = DEFAULT_MAX_CFG_CONTEXT_STATES,
) -> dict[str, object]:
    # Breadth-first traversal gives every actor root a fair chance before a
    # recursive call path can consume the bounded context-state budget.
    pending = deque((root, root, ()) for root in roots)
    visited: set[tuple[int, int, tuple[int, ...]]] = set()
    nodes: dict[int, dict[str, object]] = {}
    node_roots: dict[int, set[int]] = {}
    edges: set[tuple[int, int, str]] = set()
    stops: list[dict[str, object]] = []
    truncated = False

    while pending:
        origin, offset, return_stack = pending.popleft()
        state = (origin, offset, return_stack)
        if state in visited:
            continue
        visited.add(state)
        if len(visited) > max_context_states:
            stops.append({"offset": offset, "reason": "CFG state limit reached"})
            truncated = True
            break
        if offset < 0 or offset + 4 > limit or offset & 3:
            stops.append({"offset": offset, "reason": "target outside aligned Strategy data"})
            continue

        raw = view.u32(offset, "Strategy CFG instruction")
        opcode = raw & 0xFFFF
        if opcode > MAX_HP1_STRATEGY_OPCODE:
            stops.append(
                {"offset": offset, "reason": "low16 exceeds confirmed opcode range", "raw": raw}
            )
            continue
        immediate = signed_immediate(raw)
        try:
            next_offset = next_strategy_instruction(view, offset, limit)
            words = strategy_instruction_words(view, offset, limit)
        except FormatError as exc:
            stops.append(
                {
                    "offset": offset,
                    "reason": f"unconfirmed instruction layout: {exc}",
                    "raw": raw,
                }
            )
            continue
        nodes.setdefault(
            offset,
            {
                "offset": offset,
                "next_offset": next_offset,
                "raw": raw,
                "opcode": opcode,
                "immediate": immediate,
                "words": words,
            },
        )
        node_roots.setdefault(offset, set()).add(origin)

        successors: list[tuple[int, tuple[int, ...], str]] = []
        if opcode in CALL_OPCODES:
            kind = "call-yield" if opcode in YIELD_OPCODES else "call"
            target = next_offset + immediate * 4
            if next_offset in return_stack:
                # Re-entering the same call site only adds another identical
                # return address.  It cannot expose a new control location,
                # but it can make the abstract return stack grow forever.
                edges.add((offset, target, kind))
                stops.append(
                    {
                        "offset": offset,
                        "reason": "recursive call context pruned",
                        "target": target,
                    }
                )
            else:
                successors.append((target, return_stack + (next_offset,), kind))
        elif opcode == RETURN_OPCODE:
            if return_stack:
                successors.append((return_stack[-1], return_stack[:-1], "return"))
            else:
                stops.append({"offset": offset, "reason": "return with unknown caller"})
        elif opcode in TERMINAL_OPCODES:
            pass
        elif opcode in CONDITIONAL_BRANCH_OPCODES:
            suffix = "-yield" if opcode in YIELD_OPCODES else ""
            successors.append((next_offset, return_stack, f"fallthrough{suffix}"))
            successors.append((next_offset + immediate * 4, return_stack, f"branch{suffix}"))
        elif opcode in UNCONDITIONAL_BRANCH_OPCODES:
            kind = "jump-yield" if opcode in YIELD_OPCODES else "jump"
            successors.append((next_offset + immediate * 4, return_stack, kind))
        elif opcode == SWITCH_OPCODE:
            successors.append((next_offset, return_stack, "switch-default"))
            try:
                targets = switch_targets(view, next_offset, immediate, limit)
            except FormatError as exc:
                stops.append(
                    {
                        "offset": offset,
                        "reason": f"unconfirmed switch layout: {exc}",
                        "raw": raw,
                    }
                )
                targets = []
            for target in targets:
                successors.append((target, return_stack, "switch-case"))
        else:
            kind = "yield" if opcode in YIELD_OPCODES else "next"
            successors.append((next_offset, return_stack, kind))

        for target, stack, kind in successors:
            edges.add((offset, target, kind))
            pending.append((origin, target, stack))

    edge_rows = [
        {"from": source, "to": target, "kind": kind}
        for source, target, kind in sorted(edges)
    ]
    root_summaries = [
        {
            "root_dpsx_offset": root,
            "name": strategy_root_name(view, root, limit),
            "reachable_node_count": sum(root in origins for origins in node_roots.values()),
        }
        for root in roots
    ]
    for node in nodes.values():
        node["reachable_from_roots"] = sorted(node_roots[node["offset"]])
    return {
        "root_offsets": roots,
        "root_summaries": root_summaries,
        "node_count": len(nodes),
        "edge_count": len(edge_rows),
        "context_state_count": len(visited),
        "context_state_limit": max_context_states,
        "truncated": truncated,
        "nodes": [nodes[offset] for offset in sorted(nodes)],
        "edges": edge_rows,
        "stops": stops,
    }


def context_insensitive_strategy_nodes(
    view: View, roots: list[int], limit: int
) -> dict[str, object]:
    """Compute a finite over-approximation of reachable Strategy nodes.

    Every reached return may continue at every reached call site for the same
    actor root.  This deliberately admits impossible call/return pairings, so
    it is useful only as an upper bound for sites missed by bounded exact CFG
    traversal.
    """
    pending = deque((root, root) for root in roots)
    visited: set[tuple[int, int]] = set()
    node_roots: dict[int, set[int]] = {}
    continuations: dict[int, set[int]] = {root: set() for root in roots}
    reached_returns: dict[int, set[int]] = {root: set() for root in roots}
    stops: list[dict[str, object]] = []

    while pending:
        origin, offset = pending.popleft()
        state = (origin, offset)
        if state in visited:
            continue
        visited.add(state)
        if offset < 0 or offset + 4 > limit or offset & 3:
            stops.append(
                {"offset": offset, "reason": "target outside aligned Strategy data"}
            )
            continue

        raw = view.u32(offset, "Strategy upper-bound instruction")
        opcode = raw & 0xFFFF
        if opcode > MAX_HP1_STRATEGY_OPCODE:
            stops.append(
                {
                    "offset": offset,
                    "reason": "low16 exceeds confirmed opcode range",
                    "raw": raw,
                }
            )
            continue
        immediate = signed_immediate(raw)
        try:
            next_offset = next_strategy_instruction(view, offset, limit)
        except FormatError as exc:
            stops.append(
                {
                    "offset": offset,
                    "reason": f"unconfirmed instruction layout: {exc}",
                    "raw": raw,
                }
            )
            continue
        node_roots.setdefault(offset, set()).add(origin)

        targets: list[int] = []
        if opcode in CALL_OPCODES:
            targets.append(next_offset + immediate * 4)
            if next_offset not in continuations[origin]:
                continuations[origin].add(next_offset)
                if reached_returns[origin]:
                    targets.append(next_offset)
        elif opcode == RETURN_OPCODE:
            reached_returns[origin].add(offset)
            targets.extend(continuations[origin])
        elif opcode in TERMINAL_OPCODES:
            pass
        elif opcode in CONDITIONAL_BRANCH_OPCODES:
            targets.extend((next_offset, next_offset + immediate * 4))
        elif opcode in UNCONDITIONAL_BRANCH_OPCODES:
            targets.append(next_offset + immediate * 4)
        elif opcode == SWITCH_OPCODE:
            targets.append(next_offset)
            try:
                targets.extend(switch_targets(view, next_offset, immediate, limit))
            except FormatError as exc:
                stops.append(
                    {
                        "offset": offset,
                        "reason": f"unconfirmed switch layout: {exc}",
                        "raw": raw,
                    }
                )
        else:
            targets.append(next_offset)

        for target in targets:
            pending.append((origin, target))

    return {
        "node_offsets": sorted(node_roots),
        "node_roots": {
            str(offset): sorted(origins) for offset, origins in node_roots.items()
        },
        "stops": stops,
    }


def write_dot(path: Path, cfg: dict[str, object]) -> None:
    roots = set(cfg["root_offsets"])
    lines = ["digraph hp1_strategy {", "  rankdir=LR;", '  node [shape=box,fontname="Consolas"];']
    for node in cfg["nodes"]:
        offset = node["offset"]
        attributes = [f'label="+0x{offset:X}  op {node["opcode"]}  imm {node["immediate"]}"']
        if offset in roots:
            attributes.extend(['style="filled"', 'fillcolor="#DCEAF7"'])
        lines.append(f"  n{offset:X} [{','.join(attributes)}];")
    colors = {
        "call": "#3B82A0",
        "call-yield": "#3B82A0",
        "return": "#6B7280",
        "branch": "#B7791F",
        "branch-yield": "#B7791F",
        "jump": "#B7791F",
        "jump-yield": "#B7791F",
    }
    for edge in cfg["edges"]:
        color = colors.get(edge["kind"], "#94A3B8")
        lines.append(
            f'  n{edge["from"]:X} -> n{edge["to"]:X} '
            f'[label="{edge["kind"]}",color="{color}"];'
        )
    lines.append("}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_listing(path: Path, cfg: dict[str, object]) -> None:
    """Write a compact, diffable instruction and successor listing."""
    outgoing: dict[int, list[dict[str, object]]] = {}
    for edge in cfg["edges"]:
        outgoing.setdefault(edge["from"], []).append(edge)

    lines: list[str] = []
    for root in cfg["root_summaries"]:
        root_offset = root["root_dpsx_offset"]
        name = root["name"] or "unnamed"
        lines.append(f"# {name} root=0x{root_offset:X}")
        for node in cfg["nodes"]:
            if root_offset not in node["reachable_from_roots"]:
                continue
            words = " ".join(f"{word:08X}" for word in node["words"])
            targets = ", ".join(
                f"{edge['kind']}->0x{edge['to']:X}"
                for edge in outgoing.get(node["offset"], [])
            )
            lines.append(
                f"+0x{node['offset']:06X}  op={node['opcode']:3d} "
                f"imm={node['immediate']:6d}  words={words}  {targets}"
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def inspect_dpsx(
    payload: bytes,
    chunk: Chunk,
    max_cfg_states: int = DEFAULT_MAX_CFG_CONTEXT_STATES,
) -> dict[str, object]:
    view = View(payload)
    flags, level_block, level = locate_level_header(view)
    actor_count, actor_table = locate_actor_table(view, flags, level)
    actors = []
    for index in range(actor_count):
        record = actor_table + index * 0x40
        script = view.u32(record + 0x18, f"actor {index} script offset")
        local_count = view.u32(record + 0x1C, f"actor {index} initial-local count")
        local_displacement = view.s32(
            record + 0x20, f"actor {index} initial-local displacement"
        )
        local_offset = None
        local_values: list[int] = []
        if local_displacement != -1:
            local_offset = level_block + 8 + local_displacement
            view.require(local_offset, local_count * 4, f"actor {index} initial locals")
            local_values = [
                view.u32(local_offset + local_index * 4)
                for local_index in range(local_count)
            ]
        other = view.u32(record + 0x34, f"actor {index} auxiliary offset")
        actors.append(
            {
                "index": index,
                "record_dpsx_offset": record,
                "script_dpsx_offset": script,
                "script_wad_offset": chunk.payload_offset + script if script else None,
                "initial_local_count": local_count,
                "initial_local_dpsx_offset": local_offset,
                "initial_local_values": local_values,
                "aux_dpsx_offset": None if other == 0xFFFFFFFF else other,
            }
        )
    roots = sorted({item["script_dpsx_offset"] for item in actors if item["script_dpsx_offset"]})
    scripts = [strategy_extent(view, root, level_block) for root in roots]
    for script in scripts:
        root = script["root_dpsx_offset"]
        script["name"] = strategy_root_name(view, root, level_block)
        script["contained_in_roots"] = [
            other["root_dpsx_offset"]
            for other in scripts
            if other["root_dpsx_offset"] < root < other["end_dpsx_offset"]
        ]
    cfg = build_strategy_cfg(view, roots, level_block, max_cfg_states)
    return {
        "flags": flags,
        "chunk_wad_offset": chunk.header_offset,
        "payload_wad_offset": chunk.payload_offset,
        "payload_size": chunk.payload_size,
        "level_block_dpsx_offset": level_block,
        "level_header_dpsx_offset": level,
        "actor_table_dpsx_offset": actor_table,
        "actor_count": actor_count,
        "distinct_script_count": len(
            {item["script_dpsx_offset"] for item in actors if item["script_dpsx_offset"]}
        ),
        "actors": actors,
        "scripts": scripts,
        "cfg": cfg,
    }


def parse_int(value: str) -> int:
    return int(value, 0)


def parse_opcode_set(value: str) -> set[int]:
    opcodes = {parse_int(item.strip()) for item in value.split(",") if item.strip()}
    if not opcodes:
        raise argparse.ArgumentTypeError("at least one opcode is required")
    invalid = sorted(opcode for opcode in opcodes if not 0 <= opcode <= MAX_HP1_STRATEGY_OPCODE)
    if invalid:
        raise argparse.ArgumentTypeError(f"opcodes outside the confirmed HP1 range: {invalid}")
    return opcodes


def compact_location_destination(value: int) -> list[int | None]:
    integer = (value & 0xFFFFFFFF) >> 12
    hundreds = integer // 100
    tens = integer % 100 // 10
    ones = integer % 10
    return [hundreds or None, tens, ones]


def location_wad_name(destination: list[int | None], source_t: int) -> str:
    first = source_t if destination[0] is None else destination[0]
    return f"T{first}L{destination[1]}M{destination[2]:03d}.WAD"


def constant_fixed_predecessors(
    cfg: dict[str, object], target: int, count: int
) -> list[int] | None:
    nodes = {node["offset"]: node for node in cfg["nodes"]}
    incoming: dict[int, set[int]] = {}
    for edge in cfg["edges"]:
        incoming.setdefault(edge["to"], set()).add(edge["from"])

    values: list[int] = []
    cursor = target
    for _ in range(count):
        sources = incoming.get(cursor, set())
        if len(sources) != 1:
            return None
        source = next(iter(sources))
        node = nodes.get(source)
        if node is None:
            return None
        fixed_value = fixed_point_constant(node)
        if fixed_value is None:
            return None
        values.append((fixed_value & 0xFFFFFFFF) >> 12)
        cursor = source
    values.reverse()
    return values


def fixed_point_constant(node: dict[str, object]) -> int | None:
    """Return the raw 20.12 value pushed by a constant instruction."""
    if node["opcode"] == 68:
        return node["immediate"]
    if node["opcode"] == 69 and len(node["words"]) == 2:
        return node["words"][1]
    return None


def relative_slot_offset(node: dict[str, object]) -> int | None:
    """Return the DPSX slot addressed by opcode 5 relative to its next PC."""
    if node["opcode"] != 5:
        return None
    return node["offset"] + 4 + node["immediate"] * 4


def state_byte_write_operands(
    cfg: dict[str, object], target: int
) -> dict[str, object] | None:
    """Conservatively identify the index and simple value source for opcode 373.

    The handler pops the value first and the byte index second.  This recognizes
    only adjacent, unique stack producers: constants, locals, properties and a
    state-byte read.  More complex expressions remain explicitly unresolved.
    """
    chain = unique_predecessor_chain(cfg, target, 2)
    if chain is None:
        return None
    index_node, value_node = chain
    index_fixed = fixed_point_constant(index_node)
    if index_fixed is not None:
        index_info = {
            "index_source": "constant",
            "index": (index_fixed & 0xFFFFFFFF) >> 12,
        }
    elif index_node["opcode"] == 4:
        index_info = {
            "index_source": "local",
            "index_local_index": index_node["immediate"],
        }
    else:
        index_info = None
    value_fixed = fixed_point_constant(value_node)
    if index_info is not None:
        if value_fixed is not None:
            return {
                **index_info,
                "value_source": "constant",
                "value": (value_fixed & 0xFFFFFFFF) >> 12,
            }
        if value_node["opcode"] == 4:
            return {
                **index_info,
                "value_source": "local",
                "value_local_index": value_node["immediate"],
            }
        if value_node["opcode"] == 7:
            return {
                **index_info,
                "value_source": "property",
                "value_property_index": value_node["immediate"],
            }
        if value_node["opcode"] == 6:
            return {
                **index_info,
                "value_source": "global",
                "value_global_index": value_node["immediate"],
            }
        value_slot = relative_slot_offset(value_node)
        if value_slot is not None:
            return {
                **index_info,
                "value_source": "relative-slot",
                "value_relative_slot_offset": value_slot,
            }

    if index_node["opcode"] == 431 and value_fixed is not None:
        chain = unique_predecessor_chain(cfg, target, 3)
        if chain is not None:
            slot_node, dereference_node, constant_node = chain
            slot = relative_slot_offset(slot_node)
            if slot is not None and dereference_node["opcode"] == 431:
                return {
                    "index_source": "relative-slot-dereference",
                    "index_relative_slot_offset": slot,
                    "index_word_addend": 0,
                    "value_source": "constant",
                    "value": (value_fixed & 0xFFFFFFFF) >> 12,
                }
        chain = unique_predecessor_chain(cfg, target, 5)
        if chain is not None:
            slot_node, add_node, sum_node, dereference_node, constant_node = chain
            slot = relative_slot_offset(slot_node)
            add_fixed = fixed_point_constant(add_node)
            if (
                slot is not None
                and add_fixed is not None
                and sum_node["opcode"] == 73
                and dereference_node["opcode"] == 431
            ):
                return {
                    "index_source": "relative-slot-dereference",
                    "index_relative_slot_offset": slot,
                    "index_word_addend": (add_fixed & 0xFFFFFFFF) >> 12,
                    "value_source": "constant",
                    "value": (value_fixed & 0xFFFFFFFF) >> 12,
                }

    if value_node["opcode"] == 74:
        chain = unique_predecessor_chain(cfg, target, 4)
        if chain is not None:
            index_node, left_node, right_node, subtract_node = chain
            index_fixed = fixed_point_constant(index_node)
            if index_fixed is not None:
                index_info = {
                    "index_source": "constant",
                    "index": (index_fixed & 0xFFFFFFFF) >> 12,
                }
            elif index_node["opcode"] == 4:
                index_info = {
                    "index_source": "local",
                    "index_local_index": index_node["immediate"],
                }
            else:
                index_info = None
            if (
                index_info is not None
                and subtract_node["opcode"] == 74
                and left_node["opcode"] == 6
                and right_node["opcode"] == 4
            ):
                return {
                    **index_info,
                    "value_source": "global-minus-local",
                    "value_global_index": left_node["immediate"],
                    "value_local_index": right_node["immediate"],
                }
            if (
                index_info is not None
                and subtract_node["opcode"] == 74
                and left_node["opcode"] == 6
                and right_node["opcode"] == 6
            ):
                return {
                    **index_info,
                    "value_source": "global-minus-global",
                    "value_left_global_index": left_node["immediate"],
                    "value_right_global_index": right_node["immediate"],
                }
            right_fixed = fixed_point_constant(right_node)
            if (
                index_info is not None
                and subtract_node["opcode"] == 74
                and left_node["opcode"] == 7
                and right_fixed is not None
            ):
                return {
                    **index_info,
                    "value_source": "property-minus-constant",
                    "value_property_index": left_node["immediate"],
                    "value_subtract": (right_fixed & 0xFFFFFFFF) >> 12,
                }
        chain = unique_predecessor_chain(cfg, target, 5)
        if chain is not None:
            index_node, source_index_node, read_node, right_node, subtract_node = chain
            if (
                index_node["opcode"] == 4
                and source_index_node["opcode"] == 4
                and read_node["opcode"] == 371
                and right_node["opcode"] == 4
                and subtract_node["opcode"] == 74
            ):
                return {
                    "index_source": "local",
                    "index_local_index": index_node["immediate"],
                    "value_source": "state-byte-minus-local",
                    "value_state_byte_index_source": "local",
                    "value_state_byte_index_local_index": source_index_node[
                        "immediate"
                    ],
                    "value_subtract_local_index": right_node["immediate"],
                }

    if value_node["opcode"] == 73:
        chain = unique_predecessor_chain(cfg, target, 5)
        if chain is not None:
            index_node, source_index_node, read_node, add_node, sum_node = chain
            add_fixed = fixed_point_constant(add_node)
            if (
                index_node["opcode"] == 4
                and source_index_node["opcode"] == 4
                and read_node["opcode"] == 371
                and add_fixed is not None
                and sum_node["opcode"] == 73
            ):
                return {
                    "index_source": "local",
                    "index_local_index": index_node["immediate"],
                    "value_source": "state-byte-plus-constant",
                    "value_state_byte_index_source": "local",
                    "value_state_byte_index_local_index": source_index_node[
                        "immediate"
                    ],
                    "value_addend": (add_fixed & 0xFFFFFFFF) >> 12,
                }

        chain = unique_predecessor_chain(cfg, target, 7)
        if chain is not None:
            (
                index_node,
                source_index_node,
                read_node,
                subtract_node,
                difference_node,
                add_node,
                sum_node,
            ) = chain
            add_fixed = fixed_point_constant(add_node)
            if (
                index_node["opcode"] == 4
                and source_index_node["opcode"] == 4
                and read_node["opcode"] == 371
                and subtract_node["opcode"] == 4
                and difference_node["opcode"] == 74
                and add_fixed is not None
                and sum_node["opcode"] == 73
            ):
                return {
                    "index_source": "local",
                    "index_local_index": index_node["immediate"],
                    "value_source": "state-byte-minus-local-plus-constant",
                    "value_state_byte_index_source": "local",
                    "value_state_byte_index_local_index": source_index_node[
                        "immediate"
                    ],
                    "value_subtract_local_index": subtract_node["immediate"],
                    "value_addend": (add_fixed & 0xFFFFFFFF) >> 12,
                }

    if value_node["opcode"] != 371:
        return None
    chain = unique_predecessor_chain(cfg, target, 3)
    if chain is None:
        return None
    index_node, source_index_node, read_node = chain
    if read_node["opcode"] != 371:
        return None
    index_fixed = fixed_point_constant(index_node)
    source_index_fixed = fixed_point_constant(source_index_node)
    if source_index_fixed is None:
        return None
    if index_fixed is not None:
        index_info = {
            "index_source": "constant",
            "index": (index_fixed & 0xFFFFFFFF) >> 12,
        }
    elif index_node["opcode"] == 4:
        index_info = {
            "index_source": "local",
            "index_local_index": index_node["immediate"],
        }
    else:
        return None
    return {
        **index_info,
        "value_source": "state-byte",
        "value_state_byte_index": (source_index_fixed & 0xFFFFFFFF) >> 12,
    }


def predecessor_constant_candidates(
    cfg: dict[str, object], target: int, count: int = 64
) -> list[dict[str, int]]:
    """List constants on a short unique predecessor chain for diagnostics.

    These are candidates only: without a proven stack effect for every
    intervening opcode they must not be treated as opcode operands.
    """
    chain = unique_predecessor_tail(cfg, target, count)
    candidates = []
    for node in chain:
        fixed_value = fixed_point_constant(node)
        if fixed_value is not None:
            candidates.append(
                {
                    "offset": node["offset"],
                    "integer_value": (fixed_value & 0xFFFFFFFF) >> 12,
                }
            )
    return candidates


def format_state_byte_write_value(state_write: dict[str, object]) -> str:
    """Format a resolved opcode-373 value expression for the text report."""
    source = state_write["value_source"]
    if source == "constant":
        return str(state_write["value"])
    if source == "local":
        return f"local[{state_write['value_local_index']}]"
    if source == "property":
        return f"property[{state_write['value_property_index']}]"
    if source == "global":
        return f"global[{state_write['value_global_index']}]"
    if source == "global-minus-local":
        return (
            f"global[{state_write['value_global_index']}]"
            f"-local[{state_write['value_local_index']}]"
        )
    if source == "global-minus-global":
        return (
            f"global[{state_write['value_left_global_index']}]"
            f"-global[{state_write['value_right_global_index']}]"
        )
    if source == "property-minus-constant":
        return (
            f"property[{state_write['value_property_index']}]"
            f"-{state_write['value_subtract']}"
        )
    if source == "relative-slot":
        return f"relative-slot[0x{state_write['value_relative_slot_offset']:X}]"
    if source == "state-byte":
        return f"state[{state_write['value_state_byte_index']}]"
    state_value = (
        f"state[local[{state_write['value_state_byte_index_local_index']}]]"
    )
    if source == "state-byte-plus-constant":
        return f"{state_value}+{state_write['value_addend']}"
    if source == "state-byte-minus-local":
        return f"{state_value}-local[{state_write['value_subtract_local_index']}]"
    if source == "state-byte-minus-local-plus-constant":
        return (
            f"{state_value}-local[{state_write['value_subtract_local_index']}]"
            f"+{state_write['value_addend']}"
        )
    raise ValueError(f"unsupported state-byte value source: {source}")


def format_state_byte_write_index(state_write: dict[str, object]) -> str:
    """Format a resolved opcode-373 index expression for the text report."""
    source = state_write["index_source"]
    if source == "constant":
        return str(state_write["index"])
    if source == "local":
        return f"local[{state_write['index_local_index']}]"
    if source == "relative-slot-dereference":
        slot = state_write["index_relative_slot_offset"]
        addend = state_write["index_word_addend"]
        return f"*relative-slot[0x{slot:X}]+word[{addend}]"
    raise ValueError(f"unsupported state-byte index source: {source}")


def direct_local_predecessor(
    cfg: dict[str, object], target: int
) -> dict[str, int] | None:
    """Resolve a uniquely adjacent stLocal operand consumed by *target*.

    This deliberately does not look through arithmetic or merge points.  It is
    used only when the CFG proves that opcode 513 is immediately preceded by a
    single opcode-4 local load, keeping transition promotion conservative.
    """
    nodes = {node["offset"]: node for node in cfg["nodes"]}
    sources = {
        edge["from"] for edge in cfg["edges"] if edge["to"] == target
    }
    if len(sources) != 1:
        return None
    source = next(iter(sources))
    node = nodes.get(source)
    if node is None or node["opcode"] != 4:
        return None
    return {"offset": source, "local_index": node["immediate"]}


def direct_local_predecessors(
    cfg: dict[str, object], target: int, count: int
) -> list[dict[str, int]] | None:
    """Resolve a unique adjacent sequence of local loads feeding *target*."""
    nodes = {node["offset"]: node for node in cfg["nodes"]}
    incoming: dict[int, set[int]] = {}
    for edge in cfg["edges"]:
        incoming.setdefault(edge["to"], set()).add(edge["from"])
    operands: list[dict[str, int]] = []
    cursor = target
    for _ in range(count):
        sources = incoming.get(cursor, set())
        if len(sources) != 1:
            return None
        source = next(iter(sources))
        node = nodes.get(source)
        if node is None or node["opcode"] != 4:
            return None
        operands.append({"offset": source, "local_index": node["immediate"]})
        cursor = source
    operands.reverse()
    return operands


def direct_property_predecessors(
    cfg: dict[str, object], target: int, count: int
) -> list[dict[str, int]] | None:
    """Resolve a unique adjacent sequence of property loads feeding *target*."""
    nodes = {node["offset"]: node for node in cfg["nodes"]}
    incoming: dict[int, set[int]] = {}
    for edge in cfg["edges"]:
        incoming.setdefault(edge["to"], set()).add(edge["from"])
    operands: list[dict[str, int]] = []
    cursor = target
    for _ in range(count):
        sources = incoming.get(cursor, set())
        if len(sources) != 1:
            return None
        source = next(iter(sources))
        node = nodes.get(source)
        if node is None or node["opcode"] != 7:
            return None
        operands.append({"offset": source, "property_index": node["immediate"]})
        cursor = source
    operands.reverse()
    return operands


def unique_predecessor_chain(
    cfg: dict[str, object], target: int, count: int
) -> list[dict[str, object]] | None:
    """Return *count* uniquely connected nodes immediately before *target*."""
    nodes = {node["offset"]: node for node in cfg["nodes"]}
    incoming: dict[int, set[int]] = {}
    for edge in cfg["edges"]:
        incoming.setdefault(edge["to"], set()).add(edge["from"])
    chain: list[dict[str, object]] = []
    cursor = target
    for _ in range(count):
        sources = incoming.get(cursor, set())
        if len(sources) != 1:
            return None
        source = next(iter(sources))
        node = nodes.get(source)
        if node is None:
            return None
        chain.append(node)
        cursor = source
    chain.reverse()
    return chain


def unique_predecessor_tail(
    cfg: dict[str, object], target: int, count: int
) -> list[dict[str, object]]:
    """Return up to *count* uniquely connected nodes before *target*.

    Unlike ``unique_predecessor_chain``, this diagnostic helper preserves a
    shorter tail when it reaches a merge point or the start of a CFG.
    """
    nodes = {node["offset"]: node for node in cfg["nodes"]}
    incoming: dict[int, set[int]] = {}
    for edge in cfg["edges"]:
        incoming.setdefault(edge["to"], set()).add(edge["from"])
    chain: list[dict[str, object]] = []
    cursor = target
    for _ in range(count):
        sources = incoming.get(cursor, set())
        if len(sources) != 1:
            break
        cursor = next(iter(sources))
        node = nodes.get(cursor)
        if node is None:
            break
        chain.append(node)
    chain.reverse()
    return chain


def compact_triplet_source_local(
    cfg: dict[str, object], target: int, operands: list[dict[str, int]]
) -> int | None:
    """Recognize the Strategy decimal-split idiom feeding opcode 370."""
    if len(operands) != 3:
        return None
    hundreds, tens, ones = (operand["local_index"] for operand in operands)
    nodes = [
        node
        for node in cfg["nodes"]
        if node["offset"] < target and target - node["offset"] <= 0x200
    ]

    def matching_store(
        local_index: int, count: int, signature: list[tuple[int, int | None, int | None]]
    ) -> list[dict[str, object]] | None:
        matches = []
        for node in nodes:
            if node["opcode"] != 65 or node["immediate"] != local_index:
                continue
            chain = unique_predecessor_chain(cfg, node["offset"], count)
            if chain is None:
                continue
            valid = True
            for item, (opcode, immediate, full_value) in zip(chain, signature):
                if item["opcode"] != opcode:
                    valid = False
                    break
                if immediate is not None and item["immediate"] != immediate:
                    valid = False
                    break
                if full_value is not None and (
                    len(item["words"]) != 2 or item["words"][1] != full_value
                ):
                    valid = False
                    break
            if valid:
                matches.append(chain)
        return matches[0] if len(matches) == 1 else None

    hundreds_chain = matching_store(
        hundreds,
        4,
        [(4, None, None), (68, 40, None), (75, None, None), (171, None, None)],
    )
    tens_chain = matching_store(
        tens,
        8,
        [
            (4, None, None),
            (4, hundreds, None),
            (69, None, 409600),
            (75, None, None),
            (74, None, None),
            (68, 409, None),
            (75, None, None),
            (171, None, None),
        ],
    )
    ones_chain = matching_store(
        ones,
        10,
        [
            (4, None, None),
            (4, hundreds, None),
            (69, None, 409600),
            (75, None, None),
            (74, None, None),
            (4, tens, None),
            (69, None, 40960),
            (75, None, None),
            (74, None, None),
            (171, None, None),
        ],
    )
    if hundreds_chain is None or tens_chain is None or ones_chain is None:
        return None
    source_indices = {
        hundreds_chain[0]["immediate"],
        tens_chain[0]["immediate"],
        ones_chain[0]["immediate"],
    }
    return next(iter(source_indices)) if len(source_indices) == 1 else None


def state_byte_triplet_indices(
    cfg: dict[str, object], target: int, operands: list[dict[str, int]]
) -> list[int] | None:
    """Recognize three locals populated through opcode 371 state-byte reads."""
    if len(operands) != 3:
        return None
    nearby_nodes = [
        node
        for node in cfg["nodes"]
        if node["offset"] < target and target - node["offset"] <= 0x200
    ]
    indices: list[int] = []
    for operand in operands:
        matches: list[int] = []
        for store in nearby_nodes:
            if store["opcode"] != 65 or store["immediate"] != operand["local_index"]:
                continue
            chain = unique_predecessor_chain(cfg, store["offset"], 2)
            if chain is None or chain[1]["opcode"] != 371:
                continue
            constant = chain[0]
            if constant["opcode"] == 68:
                fixed_value = constant["immediate"]
            elif constant["opcode"] == 69 and len(constant["words"]) == 2:
                fixed_value = constant["words"][1]
            else:
                continue
            if fixed_value & 0xFFF:
                continue
            matches.append((fixed_value & 0xFFFFFFFF) >> 12)
        if len(matches) != 1:
            return None
        indices.append(matches[0])
    return indices


def reachable_local_stores(
    cfg: dict[str, object], root: int, local_index: int
) -> list[int]:
    """Return reachable opcode-65 stores to one local for a specific root."""
    return sorted(
        node["offset"]
        for node in cfg["nodes"]
        if root in node["reachable_from_roots"]
        and node["opcode"] == 65
        and node["immediate"] == local_index
    )


def direct_fixed_constant_predecessor(
    cfg: dict[str, object], target: int
) -> int | None:
    """Return a fixed-point constant directly and uniquely feeding *target*."""
    nodes = {node["offset"]: node for node in cfg["nodes"]}
    sources = {
        edge["from"] for edge in cfg["edges"] if edge["to"] == target
    }
    if len(sources) != 1:
        return None
    node = nodes.get(next(iter(sources)))
    if node is None:
        return None
    return fixed_point_constant(node)


def is_reachable_avoiding(
    cfg: dict[str, object], start: int, target: int, blocked: set[int]
) -> bool:
    """Return whether *target* is reachable without visiting blocked nodes."""
    if start in blocked or target in blocked:
        return False
    outgoing: dict[int, set[int]] = {}
    for edge in cfg["edges"]:
        source = edge["from"]
        destination = edge["to"]
        if source in blocked or destination in blocked:
            continue
        outgoing.setdefault(source, set()).add(destination)
    pending = [start]
    seen = {start}
    while pending:
        node = pending.pop()
        if node == target:
            return True
        for destination in outgoing.get(node, set()):
            if destination not in seen:
                seen.add(destination)
                pending.append(destination)
    return False


def inspect_archive_opcodes(
    dat_path: Path,
    index_path: Path,
    opcodes: set[int],
    max_cfg_states: int = DEFAULT_MAX_CFG_CONTEXT_STATES,
) -> dict[str, object]:
    with index_path.open(newline="", encoding="utf-8") as source:
        index_rows = list(csv.DictReader(source))
        rows = [
            row
            for row in index_rows
            if re.fullmatch(r"T\d+[LIBS]\d+M\d+\.WAD", row["name"])
        ]
    archive_names = {row["name"] for row in index_rows}

    occurrences: list[dict[str, object]] = []
    partial: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []
    recursive_call_prunes = 0
    truncated_opcode_bounds: list[dict[str, object]] = []
    inspected = 0
    for row in rows:
        try:
            wad = read_window(dat_path, int(row["offset"]), int(row["size"]))
            dpsx = next((item for item in chunks(wad) if item.tag == "DPSX"), None)
            if dpsx is None:
                errors.append({"name": row["name"], "reason": "DPSX chunk not found"})
                continue
            payload = wad[dpsx.payload_offset : dpsx.payload_offset + dpsx.payload_size]
            view = View(payload)
            result = inspect_dpsx(payload, dpsx, max_cfg_states)
            inspected += 1
            cfg = result["cfg"]
            recursive_call_prunes += sum(
                stop["reason"] == "recursive call context pruned"
                for stop in cfg["stops"]
            )
            if cfg["truncated"] or cfg["stops"]:
                partial.append(
                    {
                        "name": row["name"],
                        "truncated": cfg["truncated"],
                        "stop_count": len(cfg["stops"]),
                    }
                )
            if cfg["truncated"]:
                upper = context_insensitive_strategy_nodes(
                    view, cfg["root_offsets"], result["level_block_dpsx_offset"]
                )
                exact_sites = {
                    node["offset"]
                    for node in cfg["nodes"]
                    if node["opcode"] in opcodes
                }
                upper_sites = {
                    offset
                    for offset in upper["node_offsets"]
                    if (view.u32(offset, "upper-bound opcode") & 0xFFFF) in opcodes
                }
                truncated_opcode_bounds.append(
                    {
                        "name": row["name"],
                        "exact_selected_site_count": len(exact_sites),
                        "upper_selected_site_count": len(upper_sites),
                        "additional_upper_site_offsets": sorted(upper_sites - exact_sites),
                        "upper_bound_stop_count": len(upper["stops"]),
                    }
                )
            root_names = {
                script["root_dpsx_offset"]: script["name"] or "-"
                for script in result["scripts"]
            }
            actors_by_root: dict[int, list[dict[str, object]]] = {}
            for actor in result["actors"]:
                root = actor["script_dpsx_offset"]
                if root:
                    actors_by_root.setdefault(root, []).append(actor)
            for node in cfg["nodes"]:
                if node["opcode"] not in opcodes:
                    continue
                occurrence = {
                    "name": row["name"],
                    "dpsx_offset": node["offset"],
                    "opcode": node["opcode"],
                    "roots": [
                        root_names.get(root, f"0x{root:X}")
                        for root in node["reachable_from_roots"]
                    ],
                }
                source_match = re.match(r"T(\d+)", row["name"])
                source_t = int(source_match.group(1)) if source_match else 0
                if node["opcode"] == 370:
                    destination = constant_fixed_predecessors(
                        cfg, node["offset"], 3
                    )
                    occurrence["constant_destination"] = destination
                    if destination is not None:
                        target = location_wad_name(destination, source_t)
                        occurrence["target_name"] = target
                        occurrence["target_present"] = target in archive_names
                    else:
                        operands = direct_local_predecessors(cfg, node["offset"], 3)
                        occurrence["direct_local_operands"] = operands
                        if operands is not None:
                            source_local = compact_triplet_source_local(
                                cfg, node["offset"], operands
                            )
                            occurrence["compact_source_local"] = source_local
                            occurrence["state_byte_indices"] = (
                                state_byte_triplet_indices(
                                    cfg, node["offset"], operands
                                )
                            )
                            occurrence["local_destination_flows"] = [
                                {
                                    "root_dpsx_offset": root,
                                    "operands": [
                                        {
                                            **operand,
                                            "reachable_local_store_offsets": (
                                                reachable_local_stores(
                                                    cfg,
                                                    root,
                                                    operand["local_index"],
                                                )
                                            ),
                                        }
                                        for operand in operands
                                    ],
                                    "classification": "dynamic-local-triplet",
                                    "compact_source_stores": (
                                        reachable_local_stores(cfg, root, source_local)
                                        if source_local is not None
                                        else []
                                    ),
                                    "compact_source_candidates": (
                                        [
                                            {
                                                "actor_index": actor["index"],
                                                "fixed_value": actor[
                                                    "initial_local_values"
                                                ][source_local],
                                                "integer_value": (
                                                    actor["initial_local_values"][
                                                        source_local
                                                    ]
                                                    & 0xFFFFFFFF
                                                )
                                                >> 12,
                                                "destination": (
                                                    compact_location_destination(
                                                        actor["initial_local_values"][
                                                            source_local
                                                        ]
                                                    )
                                                ),
                                                "target_name": location_wad_name(
                                                    compact_location_destination(
                                                        actor["initial_local_values"][
                                                            source_local
                                                        ]
                                                    ),
                                                    source_t,
                                                ),
                                            }
                                            for actor in actors_by_root.get(root, [])
                                            if source_local
                                            < len(actor["initial_local_values"])
                                        ]
                                        if source_local is not None
                                        else []
                                    ),
                                }
                                for root in node["reachable_from_roots"]
                            ]
                        else:
                            occurrence["direct_property_operands"] = (
                                direct_property_predecessors(
                                    cfg, node["offset"], 3
                                )
                            )
                if node["opcode"] == 373:
                    occurrence["state_byte_write"] = state_byte_write_operands(
                        cfg, node["offset"]
                    )
                    state_write = occurrence["state_byte_write"]
                    if state_write is not None and state_write["index_source"] == "local":
                        local_index = state_write["index_local_index"]
                        index_flows = []
                        for root in node["reachable_from_roots"]:
                            stores = reachable_local_stores(cfg, root, local_index)
                            definitions = []
                            for store in stores:
                                predecessor = unique_predecessor_chain(cfg, store, 1)
                                source = predecessor[0] if predecessor else None
                                definitions.append(
                                    {
                                        "store_offset": store,
                                        "fixed_value": direct_fixed_constant_predecessor(
                                            cfg, store
                                        ),
                                        "source_opcode": (
                                            source["opcode"] if source is not None else None
                                        ),
                                        "source_immediate": (
                                            source["immediate"] if source is not None else None
                                        ),
                                    }
                                )
                            covers_all_paths = bool(stores) and not is_reachable_avoiding(
                                cfg, root, node["offset"], set(stores)
                            )
                            bounded = covers_all_paths and all(
                                item["fixed_value"] is not None for item in definitions
                            )
                            if not stores:
                                candidates = [
                                    {
                                        "actor_index": actor["index"],
                                        "integer_value": (
                                            actor["initial_local_values"][local_index]
                                            & 0xFFFFFFFF
                                        )
                                        >> 12,
                                    }
                                    for actor in actors_by_root.get(root, [])
                                    if local_index < len(actor["initial_local_values"])
                                ]
                                classification = "root-invariant"
                            elif bounded:
                                candidates = [
                                    {
                                        "store_offset": item["store_offset"],
                                        "integer_value": (
                                            item["fixed_value"] & 0xFFFFFFFF
                                        )
                                        >> 12,
                                    }
                                    for item in definitions
                                ]
                                classification = "root-bounded-constant"
                            else:
                                candidates = []
                                classification = "root-mutable"
                            index_flows.append(
                                {
                                    "root_dpsx_offset": root,
                                    "classification": classification,
                                    "reachable_local_store_offsets": stores,
                                    "initial_index_candidates": [
                                        {
                                            "actor_index": actor["index"],
                                            "integer_value": (
                                                actor["initial_local_values"][local_index]
                                                & 0xFFFFFFFF
                                            )
                                            >> 12,
                                        }
                                        for actor in actors_by_root.get(root, [])
                                        if local_index < len(actor["initial_local_values"])
                                    ],
                                    "store_definitions": definitions,
                                    "index_candidates": candidates,
                                }
                            )
                        occurrence["state_byte_index_flows"] = index_flows
                    if occurrence["state_byte_write"] is None:
                        occurrence["predecessor_constant_candidates"] = (
                            predecessor_constant_candidates(cfg, node["offset"])
                        )
                        occurrence["predecessor_signature"] = [
                            {
                                "opcode": item["opcode"],
                                "immediate": item["immediate"],
                            }
                            for item in unique_predecessor_tail(
                                cfg, node["offset"], 12
                            )
                        ]
                if node["opcode"] == 513:
                    operand = direct_local_predecessor(cfg, node["offset"])
                    occurrence["direct_local_operand"] = operand
                    candidates = []
                    local_flows = []
                    for root in node["reachable_from_roots"]:
                        local_stores = (
                            reachable_local_stores(cfg, root, operand["local_index"])
                            if operand is not None
                            else []
                        )
                        store_definitions = []
                        for store_offset in local_stores:
                            fixed_value = direct_fixed_constant_predecessor(
                                cfg, store_offset
                            )
                            definition = {
                                "store_offset": store_offset,
                                "fixed_value": fixed_value,
                            }
                            if fixed_value is not None:
                                integer = (fixed_value & 0xFFFFFFFF) >> 12
                                destination = compact_location_destination(fixed_value)
                                definition.update(
                                    {
                                        "integer_value": integer,
                                        "destination": destination,
                                        "zero_special": integer == 0,
                                    }
                                )
                                if integer != 0:
                                    target = location_wad_name(destination, source_t)
                                    definition["target_name"] = target
                                    definition["target_present"] = target in archive_names
                            store_definitions.append(definition)
                        stores_cover_all_paths = bool(local_stores) and not (
                            is_reachable_avoiding(
                                cfg, root, node["offset"], set(local_stores)
                            )
                        )
                        root_bounded_constant = stores_cover_all_paths and all(
                            definition["fixed_value"] is not None
                            for definition in store_definitions
                        )
                        local_flows.append(
                            {
                                "root_dpsx_offset": root,
                                "local_index": (
                                    operand["local_index"]
                                    if operand is not None
                                    else None
                                ),
                                "store_definitions": store_definitions,
                                "stores_cover_all_paths": stores_cover_all_paths,
                                "classification": (
                                    "root-invariant"
                                    if not local_stores
                                    else (
                                        "root-bounded-constant"
                                        if root_bounded_constant
                                        else "root-mutable"
                                    )
                                ),
                            }
                        )
                        for actor in actors_by_root.get(root, []):
                            values = actor["initial_local_values"]
                            if (
                                operand is None
                                or operand["local_index"] < 0
                                or operand["local_index"] >= len(values)
                            ):
                                continue
                            fixed_value = values[operand["local_index"]]
                            integer = (fixed_value & 0xFFFFFFFF) >> 12
                            destination = compact_location_destination(fixed_value)
                            candidate = {
                                "actor_index": actor["index"],
                                "root_dpsx_offset": root,
                                "local_index": operand["local_index"],
                                "fixed_value": fixed_value,
                                "integer_value": integer,
                                "destination": destination,
                                "zero_special": integer == 0,
                                "reachable_local_store_offsets": local_stores,
                                "value_origin": (
                                    "initial-root-invariant"
                                    if not local_stores
                                    else (
                                        "initial-overwritten"
                                        if root_bounded_constant
                                        else "initial-root-mutable"
                                    )
                                ),
                            }
                            if integer != 0:
                                target = location_wad_name(destination, source_t)
                                candidate["target_name"] = target
                                candidate["target_present"] = target in archive_names
                            candidates.append(candidate)
                    occurrence["initial_local_candidates"] = candidates
                    occurrence["local_flows"] = local_flows
                occurrences.append(occurrence)
        except (FormatError, OSError, KeyError, ValueError) as exc:
            errors.append({"name": row.get("name", "?"), "reason": str(exc)})

    counts = {
        str(opcode): sum(item["opcode"] == opcode for item in occurrences)
        for opcode in sorted(opcodes)
    }
    candidate_edges: set[tuple[str, str]] = set()
    confirmed_initial_edges: set[tuple[str, str]] = set()
    mutable_initial_edges: set[tuple[str, str]] = set()
    missing_edges: set[tuple[str, str]] = set()
    zero_special_sources: set[str] = set()
    direct_local_operand_counts: dict[str, int] = {}
    root_bounded_edges: set[tuple[str, str]] = set()
    derived_compact_edges: set[tuple[str, str]] = set()
    dynamic_compact_sources: set[tuple[str, int, int]] = set()
    dynamic_property_triplets: set[tuple[str, int, int, int]] = set()
    dynamic_state_byte_triplets: set[tuple[str, int, int, int]] = set()
    resolved_state_byte_writes: list[dict[str, object]] = []
    initial_local_value_counts: dict[str, int] = {}
    state_byte_write_index_source_counts: dict[str, int] = {}
    for occurrence in occurrences:
        operand = occurrence.get("direct_local_operand")
        if operand is not None:
            key = str(operand["local_index"])
            direct_local_operand_counts[key] = direct_local_operand_counts.get(key, 0) + 1
        if occurrence.get("target_name"):
            edge = (occurrence["name"], occurrence["target_name"])
            (candidate_edges if occurrence["target_present"] else missing_edges).add(edge)
        for candidate in occurrence.get("initial_local_candidates", []):
            origin = candidate["value_origin"]
            initial_local_value_counts[origin] = (
                initial_local_value_counts.get(origin, 0) + 1
            )
            if origin == "initial-overwritten":
                continue
            if candidate["zero_special"]:
                zero_special_sources.add(occurrence["name"])
                continue
            edge = (occurrence["name"], candidate["target_name"])
            (candidate_edges if candidate["target_present"] else missing_edges).add(edge)
            if candidate["target_present"]:
                if origin == "initial-root-invariant":
                    confirmed_initial_edges.add(edge)
                else:
                    mutable_initial_edges.add(edge)
        for flow in occurrence.get("local_flows", []):
            if flow["classification"] != "root-bounded-constant":
                continue
            for definition in flow["store_definitions"]:
                if definition.get("zero_special"):
                    zero_special_sources.add(occurrence["name"])
                    continue
                if definition.get("target_name"):
                    edge = (occurrence["name"], definition["target_name"])
                    (candidate_edges if definition["target_present"] else missing_edges).add(
                        edge
                    )
                    if definition["target_present"]:
                        root_bounded_edges.add(edge)
        for flow in occurrence.get("local_destination_flows", []):
            source_local = occurrence.get("compact_source_local")
            if source_local is None:
                continue
            if flow["compact_source_stores"]:
                dynamic_compact_sources.add(
                    (occurrence["name"], flow["root_dpsx_offset"], source_local)
                )
                continue
            for candidate in flow["compact_source_candidates"]:
                target = candidate["target_name"]
                candidate["target_present"] = target in archive_names
                edge = (occurrence["name"], target)
                (candidate_edges if candidate["target_present"] else missing_edges).add(
                    edge
                )
                if candidate["target_present"]:
                    derived_compact_edges.add(edge)
        properties = occurrence.get("direct_property_operands")
        if properties:
            dynamic_property_triplets.add(
                (
                    occurrence["name"],
                    properties[0]["property_index"],
                    properties[1]["property_index"],
                    properties[2]["property_index"],
                )
            )
        state_bytes = occurrence.get("state_byte_indices")
        if state_bytes:
            dynamic_state_byte_triplets.add(
                (
                    occurrence["name"],
                    state_bytes[0],
                    state_bytes[1],
                    state_bytes[2],
                )
            )
        state_write = occurrence.get("state_byte_write")
        if state_write is not None:
            source = state_write["index_source"]
            state_byte_write_index_source_counts[source] = (
                state_byte_write_index_source_counts.get(source, 0) + 1
            )
        if state_write is not None and state_write["index_source"] == "constant":
            resolved_state_byte_writes.append(
                {
                    "wad": occurrence["name"],
                    "dpsx_offset": occurrence["dpsx_offset"],
                    "roots": occurrence["roots"],
                    **state_write,
                }
            )
    return {
        "archive": str(dat_path),
        "index": str(index_path),
        "candidate_wad_count": len(rows),
        "context_state_limit_per_wad": max_cfg_states,
        "inspected_wad_count": inspected,
        "partial_wad_count": len(partial),
        "truncated_wad_count": sum(item["truncated"] for item in partial),
        "recursive_call_prune_count": recursive_call_prunes,
        "truncated_opcode_bounds": truncated_opcode_bounds,
        "error_count": len(errors),
        "opcode_counts": counts,
        "direct_local_operand_counts": direct_local_operand_counts,
        "initial_local_value_counts": initial_local_value_counts,
        "candidate_edges": [
            {"source": source, "target": target}
            for source, target in sorted(candidate_edges)
        ],
        "root_invariant_initial_local_edges": [
            {"source": source, "target": target}
            for source, target in sorted(confirmed_initial_edges)
        ],
        "root_mutable_initial_local_edges": [
            {"source": source, "target": target}
            for source, target in sorted(mutable_initial_edges)
        ],
        "root_bounded_constant_local_edges": [
            {"source": source, "target": target}
            for source, target in sorted(root_bounded_edges)
        ],
        "derived_compact_triplet_edges": [
            {"source": source, "target": target}
            for source, target in sorted(derived_compact_edges)
        ],
        "dynamic_compact_triplet_sources": [
            {"wad": wad, "root_dpsx_offset": root, "local_index": local_index}
            for wad, root, local_index in sorted(dynamic_compact_sources)
        ],
        "dynamic_property_triplets": [
            {
                "wad": wad,
                "property_indices": [first, second, third],
            }
            for wad, first, second, third in sorted(dynamic_property_triplets)
        ],
        "dynamic_state_byte_triplets": [
            {
                "wad": wad,
                "state_byte_indices": [first, second, third],
            }
            for wad, first, second, third in sorted(dynamic_state_byte_triplets)
        ],
        "resolved_state_byte_writes": resolved_state_byte_writes,
        "state_byte_write_index_source_counts": (
            state_byte_write_index_source_counts
        ),
        "missing_candidate_edges": [
            {"source": source, "target": target}
            for source, target in sorted(missing_edges)
        ],
        "zero_special_sources": sorted(zero_special_sources),
        "occurrences": occurrences,
        "partial_wads": partial,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="WAD file, or a DAT containing the WAD window")
    parser.add_argument("--offset", type=parse_int, default=0, help="WAD byte offset in input")
    parser.add_argument("--length", type=parse_int, help="WAD byte length")
    parser.add_argument("--json", type=Path, help="optional machine-readable output")
    parser.add_argument(
        "--archive-index",
        type=Path,
        help="inspect all level-like WAD windows listed in an archive-index CSV",
    )
    parser.add_argument(
        "--opcodes",
        type=parse_opcode_set,
        help="comma-separated Strategy opcodes to report in archive-index mode",
    )
    parser.add_argument("--dot", type=Path, help="optional Graphviz control-flow map")
    parser.add_argument(
        "--listing",
        type=Path,
        help="optional compact instruction and successor listing",
    )
    parser.add_argument(
        "--words",
        type=int,
        default=0,
        help="show this many raw 32-bit words at each distinct script root",
    )
    parser.add_argument(
        "--max-cfg-states",
        type=int,
        default=DEFAULT_MAX_CFG_CONTEXT_STATES,
        help="maximum context-sensitive CFG states per WAD (default: %(default)s)",
    )
    args = parser.parse_args()

    if args.max_cfg_states < 1:
        parser.error("--max-cfg-states must be positive")

    if args.archive_index:
        if not args.opcodes:
            parser.error("--archive-index requires --opcodes")
        if args.dot or args.listing or args.words or args.offset or args.length:
            parser.error(
                "--archive-index cannot be combined with --dot, --listing, --words, "
                "--offset or --length"
            )
        result = inspect_archive_opcodes(
            args.input,
            args.archive_index,
            args.opcodes,
            args.max_cfg_states,
        )
        print("=== HP1 ARCHIVE STRATEGY OPCODES ===")
        print(f"Archive: {args.input}")
        print(f"Index: {args.archive_index}")
        print(
            f"WADs: {result['inspected_wad_count']}/{result['candidate_wad_count']} inspected; "
            f"{result['partial_wad_count']} with bounded stops; "
            f"{result['truncated_wad_count']} state-limit truncations; "
            f"{result['error_count']} errors"
        )
        print(
            "Recursive call contexts pruned: "
            f"{result['recursive_call_prune_count']}"
        )
        if result["truncated_opcode_bounds"]:
            print(
                "Truncated-WAD opcode upper bounds: "
                + ", ".join(
                    f"{item['name']} exact={item['exact_selected_site_count']} "
                    f"upper={item['upper_selected_site_count']} "
                    f"additional={len(item['additional_upper_site_offsets'])}"
                    for item in result["truncated_opcode_bounds"]
                )
            )
        print(
            "Counts: "
            + ", ".join(
                f"{opcode}={count}" for opcode, count in result["opcode_counts"].items()
            )
        )
        print(
            f"Candidate edges: {len(result['candidate_edges'])} present; "
            f"{len(result['missing_candidate_edges'])} missing targets; "
            f"{len(result['zero_special_sources'])} zero-special sources"
        )
        print(
            "Initial-local classification: "
            f"{len(result['root_invariant_initial_local_edges'])} root-invariant edges; "
            f"{len(result['root_bounded_constant_local_edges'])} root-bounded edges; "
            f"{len(result['root_mutable_initial_local_edges'])} root-mutable edges"
        )
        print(
            "Expanded compact triplets: "
            f"{len(result['derived_compact_triplet_edges'])} derived edges; "
            f"{len(result['dynamic_compact_triplet_sources'])} dynamic sources"
        )
        print(
            "Dynamic property triplets: "
            f"{len(result['dynamic_property_triplets'])} unique WAD/property sets"
        )
        print(
            "Dynamic state-byte triplets: "
            f"{len(result['dynamic_state_byte_triplets'])} unique WAD/index sets"
        )
        if 373 in args.opcodes:
            resolved_writes = result["resolved_state_byte_writes"]
            source_counts = result["state_byte_write_index_source_counts"]
            print(
                "State-byte index sources: "
                f"constant={source_counts.get('constant', 0)}; "
                f"local={source_counts.get('local', 0)}; "
                "relative-slot-dereference="
                f"{source_counts.get('relative-slot-dereference', 0)}; "
                f"unresolved={result['opcode_counts']['373'] - sum(source_counts.values())}"
            )
        if result["direct_local_operand_counts"]:
            print(
                "Direct local operands: "
                + ", ".join(
                    f"local[{index}]={count}"
                    for index, count in sorted(
                        result["direct_local_operand_counts"].items(),
                        key=lambda item: int(item[0]),
                    )
                )
            )
            value_counts = result["initial_local_value_counts"]
            print(
                "Actor-local definitions: "
                + ", ".join(
                    f"{origin}={count}"
                    for origin, count in sorted(value_counts.items())
                )
            )
        for item in result["occurrences"]:
            roots = "|".join(item["roots"])
            details = ""
            if item.get("constant_destination") is not None:
                marker = "" if item["target_present"] else "[missing]"
                details = f" target={item['target_name']}{marker}"
            elif item.get("state_byte_write") is not None:
                state_write = item["state_byte_write"]
                value = format_state_byte_write_value(state_write)
                index = format_state_byte_write_index(state_write)
                details = f" state[{index}]={value}"
            elif item.get("direct_local_operands"):
                indices = ",".join(
                    str(operand["local_index"])
                    for operand in item["direct_local_operands"]
                )
                source_local = item.get("compact_source_local")
                source = (
                    f" compact-source=local[{source_local}]"
                    if source_local is not None
                    else ""
                )
                targets = sorted(
                    {
                        candidate["target_name"]
                        for flow in item.get("local_destination_flows", [])
                        if not flow["compact_source_stores"]
                        for candidate in flow["compact_source_candidates"]
                    }
                )
                target_text = f" targets={'|'.join(targets)}" if targets else ""
                details = (
                    f" dynamic-local-triplet=[{indices}]" + source + target_text
                )
            elif item.get("direct_property_operands"):
                indices = ",".join(
                    str(operand["property_index"])
                    for operand in item["direct_property_operands"]
                )
                details = f" dynamic-property-triplet=[{indices}]"
            elif any(
                flow["classification"] == "root-bounded-constant"
                for flow in item.get("local_flows", [])
            ):
                targets = sorted(
                    {
                        definition.get("target_name", "<zero-special>")
                        + (
                            ""
                            if definition.get("target_present", True)
                            else "[missing]"
                        )
                        for flow in item["local_flows"]
                        if flow["classification"] == "root-bounded-constant"
                        for definition in flow["store_definitions"]
                    }
                )
                local_index = item["direct_local_operand"]["local_index"]
                details = (
                    f" root-bounded-local[{local_index}]=" + "|".join(targets)
                )
            elif item.get("initial_local_candidates"):
                targets = sorted(
                    {
                        candidate.get("target_name", "<zero-special>")
                        + ("" if candidate.get("target_present", True) else "[missing]")
                        for candidate in item["initial_local_candidates"]
                    }
                )
                local_index = item["direct_local_operand"]["local_index"]
                details = (
                    f" initial-local[{local_index}]-candidates=" + "|".join(targets)
                )
            print(
                f"{item['name']} +0x{item['dpsx_offset']:X} "
                f"op={item['opcode']} roots={roots}{details}"
            )
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            print(f"JSON: {args.json}")
        return 0

    wad = read_window(args.input, args.offset, args.length)
    dpsx = next((item for item in chunks(wad) if item.tag == "DPSX"), None)
    if dpsx is None:
        raise FormatError("DPSX chunk not found")
    payload = wad[dpsx.payload_offset : dpsx.payload_offset + dpsx.payload_size]
    result = inspect_dpsx(payload, dpsx, args.max_cfg_states)

    print("=== HP1 DPSX INSPECTION ===")
    print(f"Input: {args.input}")
    print(f"WAD window: offset 0x{args.offset:X}, bytes {len(wad)}")
    print(f"DPSX: WAD 0x{dpsx.header_offset:X}, payload bytes {dpsx.payload_size}")
    print(f"Flags: 0x{result['flags']:08X}")
    print(f"Level block: DPSX payload +0x{result['level_block_dpsx_offset']:X}")
    print(f"Level header: DPSX payload +0x{result['level_header_dpsx_offset']:X}")
    print(f"Actor table: DPSX payload +0x{result['actor_table_dpsx_offset']:X}")
    print(f"Actors: {result['actor_count']} ({result['distinct_script_count']} distinct non-null scripts)")
    print("\n index  record+    script+    WAD offset")
    for actor in result["actors"]:
        script = actor["script_dpsx_offset"]
        wad_offset = actor["script_wad_offset"]
        print(
            f" {actor['index']:5d}  0x{actor['record_dpsx_offset']:06X}  "
            f"{'-' if not script else f'0x{script:06X}':>8}  "
            f"{'-' if wad_offset is None else f'0x{wad_offset:06X}':>10}"
        )

    print("\n=== VERIFIED SEQUENTIAL SCRIPT EXTENTS ===")
    print(" root+     end+      bytes  instructions  boundary     name")
    for script in result["scripts"]:
        name = script["name"] or "-"
        print(
            f" 0x{script['root_dpsx_offset']:06X}  0x{script['end_dpsx_offset']:06X}  "
            f"{script['byte_length']:5d}  {script['instruction_count']:12d}  "
            f"0x{script['boundary_raw']:08X}  {name}"
        )

    cfg = result["cfg"]
    print("\n=== STRATEGY CONTROL FLOW ===")
    print(f"Nodes: {cfg['node_count']}")
    print(f"Edges: {cfg['edge_count']}")
    print(f"Context states: {cfg['context_state_count']}")
    print(f"Stops requiring review: {len(cfg['stops'])}")
    print("\n root+     reachable nodes  name")
    for root in cfg["root_summaries"]:
        print(
            f" 0x{root['root_dpsx_offset']:06X}  {root['reachable_node_count']:15d}  "
            f"{root['name'] or '-'}"
        )

    if args.words:
        print("\n=== RAW SCRIPT ROOT WORDS ===")
        print("low16 is not necessarily an opcode: some instructions consume following payload words.")
        roots = sorted({item["script_dpsx_offset"] for item in result["actors"] if item["script_dpsx_offset"]})
        view = View(payload)
        for root in roots:
            print(f"\nDPSX +0x{root:06X} / WAD 0x{dpsx.payload_offset + root:06X}")
            for word_index in range(args.words):
                offset = root + word_index * 4
                raw = view.u32(offset, "script word")
                immediate = struct.unpack("<h", struct.pack("<H", raw >> 16))[0]
                print(
                    f"  {word_index:3d}  0x{raw:08X}  low16 {raw & 0xFFFF:5d}  high16 {immediate:6d}"
                )

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"\nJSON: {args.json}")
    if args.dot:
        write_dot(args.dot, cfg)
        print(f"DOT: {args.dot}")
    if args.listing:
        args.listing.parent.mkdir(parents=True, exist_ok=True)
        write_listing(args.listing, cfg)
        print(f"Listing: {args.listing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
