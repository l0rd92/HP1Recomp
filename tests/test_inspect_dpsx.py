import struct
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import inspect_dpsx


class StrategyInspectionTests(unittest.TestCase):
    def test_compact_location_uses_decimal_digits_and_source_fallback(self) -> None:
        self.assertEqual(inspect_dpsx.compact_location_destination(0x72000), [1, 1, 4])
        destination = inspect_dpsx.compact_location_destination(0x5000)
        self.assertEqual(destination, [None, 0, 5])
        self.assertEqual(
            inspect_dpsx.location_wad_name(destination, 1), "T1L0M005.WAD"
        )

    def test_constant_fixed_predecessors_resolve_three_field_destination(self) -> None:
        cfg = {
            "nodes": [
                {"offset": 0, "opcode": 68, "immediate": 0x1000},
                {"offset": 4, "opcode": 68, "immediate": 0x2000},
                {"offset": 8, "opcode": 68, "immediate": 0x3000},
                {"offset": 12, "opcode": 370, "immediate": 0},
            ],
            "edges": [
                {"from": 0, "to": 4, "kind": "next"},
                {"from": 4, "to": 8, "kind": "next"},
                {"from": 8, "to": 12, "kind": "next"},
            ],
        }

        self.assertEqual(
            inspect_dpsx.constant_fixed_predecessors(cfg, 12, 3), [1, 2, 3]
        )

    def test_constant_fixed_predecessors_resolve_state_index_and_value(self) -> None:
        cfg = {
            "nodes": [
                {
                    "offset": 0,
                    "opcode": 69,
                    "immediate": 0,
                    "words": [69, 31 << 12],
                },
                {
                    "offset": 8,
                    "opcode": 68,
                    "immediate": 2 << 12,
                    "words": [68 | (2 << 28)],
                },
                {"offset": 12, "opcode": 373, "immediate": 0, "words": [373]},
            ],
            "edges": [
                {"from": 0, "to": 8, "kind": "next"},
                {"from": 8, "to": 12, "kind": "next"},
            ],
        }

        self.assertEqual(
            inspect_dpsx.constant_fixed_predecessors(cfg, 12, 2), [31, 2]
        )

        self.assertEqual(
            inspect_dpsx.state_byte_write_operands(cfg, 12),
            {
                "index_source": "constant",
                "index": 31,
                "value_source": "constant",
                "value": 2,
            },
        )

    def test_state_byte_write_resolves_state_copy_without_swapping_indices(self) -> None:
        nodes = [
            {"offset": 0, "opcode": 68, "immediate": 0, "words": [68]},
            {
                "offset": 4,
                "opcode": 69,
                "immediate": 0,
                "words": [69, 34 << 12],
            },
            {"offset": 12, "opcode": 371, "immediate": 0, "words": [371]},
            {"offset": 16, "opcode": 373, "immediate": 0, "words": [373]},
        ]
        cfg = {
            "nodes": nodes,
            "edges": [
                {"from": 0, "to": 4, "kind": "next"},
                {"from": 4, "to": 12, "kind": "next"},
                {"from": 12, "to": 16, "kind": "next"},
            ],
        }

        self.assertEqual(
            inspect_dpsx.state_byte_write_operands(cfg, 16),
            {
                "index_source": "constant",
                "index": 0,
                "value_source": "state-byte",
                "value_state_byte_index": 34,
            },
        )

    def test_state_byte_write_can_defer_index_resolution_to_actor_local(self) -> None:
        cfg = {
            "nodes": [
                {"offset": 0, "opcode": 4, "immediate": 9, "words": [4]},
                {"offset": 4, "opcode": 7, "immediate": 3, "words": [7]},
                {"offset": 8, "opcode": 373, "immediate": 0, "words": [373]},
            ],
            "edges": [
                {"from": 0, "to": 4, "kind": "next"},
                {"from": 4, "to": 8, "kind": "next"},
            ],
        }

        self.assertEqual(
            inspect_dpsx.state_byte_write_operands(cfg, 8),
            {
                "index_source": "local",
                "index_local_index": 9,
                "value_source": "property",
                "value_property_index": 3,
            },
        )

    def test_state_byte_write_resolves_global_minus_local_value(self) -> None:
        cfg = {
            "nodes": [
                {
                    "offset": 0,
                    "opcode": 69,
                    "immediate": 0,
                    "words": [69, 30 << 12],
                },
                {"offset": 8, "opcode": 6, "immediate": 120, "words": [6]},
                {"offset": 12, "opcode": 4, "immediate": 23, "words": [4]},
                {"offset": 16, "opcode": 74, "immediate": 0, "words": [74]},
                {"offset": 20, "opcode": 373, "immediate": 0, "words": [373]},
            ],
            "edges": [
                {"from": 0, "to": 8, "kind": "next"},
                {"from": 8, "to": 12, "kind": "next"},
                {"from": 12, "to": 16, "kind": "next"},
                {"from": 16, "to": 20, "kind": "next"},
            ],
        }

        self.assertEqual(
            inspect_dpsx.state_byte_write_operands(cfg, 20),
            {
                "index_source": "constant",
                "index": 30,
                "value_source": "global-minus-local",
                "value_global_index": 120,
                "value_local_index": 23,
            },
        )

    def test_state_byte_write_resolves_state_byte_increment(self) -> None:
        cfg = {
            "nodes": [
                {"offset": 0, "opcode": 4, "immediate": 24, "words": [4]},
                {"offset": 4, "opcode": 4, "immediate": 24, "words": [4]},
                {"offset": 8, "opcode": 371, "immediate": 0, "words": [371]},
                {"offset": 12, "opcode": 68, "immediate": 4096, "words": [68]},
                {"offset": 16, "opcode": 73, "immediate": 0, "words": [73]},
                {"offset": 20, "opcode": 373, "immediate": 0, "words": [373]},
            ],
            "edges": [
                {"from": 0, "to": 4, "kind": "next"},
                {"from": 4, "to": 8, "kind": "next"},
                {"from": 8, "to": 12, "kind": "next"},
                {"from": 12, "to": 16, "kind": "next"},
                {"from": 16, "to": 20, "kind": "next"},
            ],
        }

        self.assertEqual(
            inspect_dpsx.state_byte_write_operands(cfg, 20),
            {
                "index_source": "local",
                "index_local_index": 24,
                "value_source": "state-byte-plus-constant",
                "value_state_byte_index_source": "local",
                "value_state_byte_index_local_index": 24,
                "value_addend": 1,
            },
        )

    def test_state_byte_write_resolves_adjusted_state_byte_increment(self) -> None:
        cfg = {
            "nodes": [
                {"offset": 0, "opcode": 4, "immediate": 24, "words": [4]},
                {"offset": 4, "opcode": 4, "immediate": 24, "words": [4]},
                {"offset": 8, "opcode": 371, "immediate": 0, "words": [371]},
                {"offset": 12, "opcode": 4, "immediate": 33, "words": [4]},
                {"offset": 16, "opcode": 74, "immediate": 0, "words": [74]},
                {"offset": 20, "opcode": 68, "immediate": 4096, "words": [68]},
                {"offset": 24, "opcode": 73, "immediate": 0, "words": [73]},
                {"offset": 28, "opcode": 373, "immediate": 0, "words": [373]},
            ],
            "edges": [
                {"from": 0, "to": 4, "kind": "next"},
                {"from": 4, "to": 8, "kind": "next"},
                {"from": 8, "to": 12, "kind": "next"},
                {"from": 12, "to": 16, "kind": "next"},
                {"from": 16, "to": 20, "kind": "next"},
                {"from": 20, "to": 24, "kind": "next"},
                {"from": 24, "to": 28, "kind": "next"},
            ],
        }

        self.assertEqual(
            inspect_dpsx.state_byte_write_operands(cfg, 28),
            {
                "index_source": "local",
                "index_local_index": 24,
                "value_source": "state-byte-minus-local-plus-constant",
                "value_state_byte_index_source": "local",
                "value_state_byte_index_local_index": 24,
                "value_subtract_local_index": 33,
                "value_addend": 1,
            },
        )

    def test_state_byte_write_resolves_global_value(self) -> None:
        cfg = {
            "nodes": [
                {"offset": 0, "opcode": 69, "immediate": 0, "words": [69, 30 << 12]},
                {"offset": 8, "opcode": 6, "immediate": 118, "words": [6]},
                {"offset": 12, "opcode": 373, "immediate": 0, "words": [373]},
            ],
            "edges": [
                {"from": 0, "to": 8, "kind": "next"},
                {"from": 8, "to": 12, "kind": "next"},
            ],
        }

        self.assertEqual(
            inspect_dpsx.state_byte_write_operands(cfg, 12),
            {
                "index_source": "constant",
                "index": 30,
                "value_source": "global",
                "value_global_index": 118,
            },
        )

    def test_state_byte_write_resolves_state_byte_minus_local(self) -> None:
        cfg = {
            "nodes": [
                {"offset": 0, "opcode": 4, "immediate": 18, "words": [4]},
                {"offset": 4, "opcode": 4, "immediate": 18, "words": [4]},
                {"offset": 8, "opcode": 371, "immediate": 0, "words": [371]},
                {"offset": 12, "opcode": 4, "immediate": 11, "words": [4]},
                {"offset": 16, "opcode": 74, "immediate": 0, "words": [74]},
                {"offset": 20, "opcode": 373, "immediate": 0, "words": [373]},
            ],
            "edges": [
                {"from": 0, "to": 4, "kind": "next"},
                {"from": 4, "to": 8, "kind": "next"},
                {"from": 8, "to": 12, "kind": "next"},
                {"from": 12, "to": 16, "kind": "next"},
                {"from": 16, "to": 20, "kind": "next"},
            ],
        }

        self.assertEqual(
            inspect_dpsx.state_byte_write_operands(cfg, 20),
            {
                "index_source": "local",
                "index_local_index": 18,
                "value_source": "state-byte-minus-local",
                "value_state_byte_index_source": "local",
                "value_state_byte_index_local_index": 18,
                "value_subtract_local_index": 11,
            },
        )

    def test_state_byte_expression_formatter_handles_counter_patterns(self) -> None:
        self.assertEqual(
            inspect_dpsx.format_state_byte_write_value(
                {
                    "value_source": "state-byte-plus-constant",
                    "value_state_byte_index_local_index": 24,
                    "value_addend": 1,
                }
            ),
            "state[local[24]]+1",
        )
        self.assertEqual(
            inspect_dpsx.format_state_byte_write_value(
                {
                    "value_source": "state-byte-minus-local-plus-constant",
                    "value_state_byte_index_local_index": 24,
                    "value_subtract_local_index": 33,
                    "value_addend": 1,
                }
            ),
            "state[local[24]]-local[33]+1",
        )

    def test_state_byte_write_resolves_global_minus_global(self) -> None:
        cfg = {
            "nodes": [
                {"offset": 0, "opcode": 69, "immediate": 0, "words": [69, 30 << 12]},
                {"offset": 8, "opcode": 6, "immediate": 91, "words": [6]},
                {"offset": 12, "opcode": 6, "immediate": 90, "words": [6]},
                {"offset": 16, "opcode": 74, "immediate": 0, "words": [74]},
                {"offset": 20, "opcode": 373, "immediate": 0, "words": [373]},
            ],
            "edges": [
                {"from": 0, "to": 8, "kind": "next"},
                {"from": 8, "to": 12, "kind": "next"},
                {"from": 12, "to": 16, "kind": "next"},
                {"from": 16, "to": 20, "kind": "next"},
            ],
        }

        self.assertEqual(
            inspect_dpsx.state_byte_write_operands(cfg, 20)["value_source"],
            "global-minus-global",
        )

    def test_state_byte_write_resolves_property_minus_constant(self) -> None:
        cfg = {
            "nodes": [
                {"offset": 0, "opcode": 69, "immediate": 0, "words": [69, 30 << 12]},
                {"offset": 8, "opcode": 7, "immediate": 153, "words": [7]},
                {"offset": 12, "opcode": 68, "immediate": 4096, "words": [68]},
                {"offset": 16, "opcode": 74, "immediate": 0, "words": [74]},
                {"offset": 20, "opcode": 373, "immediate": 0, "words": [373]},
            ],
            "edges": [
                {"from": 0, "to": 8, "kind": "next"},
                {"from": 8, "to": 12, "kind": "next"},
                {"from": 12, "to": 16, "kind": "next"},
                {"from": 16, "to": 20, "kind": "next"},
            ],
        }

        self.assertEqual(
            inspect_dpsx.state_byte_write_operands(cfg, 20)["value_source"],
            "property-minus-constant",
        )

    def test_state_byte_write_resolves_relative_slot_value(self) -> None:
        cfg = {
            "nodes": [
                {"offset": 0x100, "opcode": 69, "immediate": 0, "words": [69, 30 << 12]},
                {"offset": 0x108, "opcode": 5, "immediate": -2, "words": [5]},
                {"offset": 0x10C, "opcode": 373, "immediate": 0, "words": [373]},
            ],
            "edges": [
                {"from": 0x100, "to": 0x108, "kind": "next"},
                {"from": 0x108, "to": 0x10C, "kind": "next"},
            ],
        }

        result = inspect_dpsx.state_byte_write_operands(cfg, 0x10C)
        self.assertEqual(result["index"], 30)
        self.assertEqual(result["value_relative_slot_offset"], 0x104)

    def test_state_byte_write_resolves_indirect_relative_slot_index(self) -> None:
        cfg = {
            "nodes": [
                {"offset": 0x100, "opcode": 5, "immediate": -1, "words": [5]},
                {"offset": 0x104, "opcode": 68, "immediate": 8192, "words": [68]},
                {"offset": 0x108, "opcode": 73, "immediate": 0, "words": [73]},
                {"offset": 0x10C, "opcode": 431, "immediate": 0, "words": [431]},
                {"offset": 0x110, "opcode": 68, "immediate": 12288, "words": [68]},
                {"offset": 0x114, "opcode": 373, "immediate": 0, "words": [373]},
            ],
            "edges": [
                {"from": 0x100, "to": 0x104, "kind": "next"},
                {"from": 0x104, "to": 0x108, "kind": "next"},
                {"from": 0x108, "to": 0x10C, "kind": "next"},
                {"from": 0x10C, "to": 0x110, "kind": "next"},
                {"from": 0x110, "to": 0x114, "kind": "next"},
            ],
        }

        result = inspect_dpsx.state_byte_write_operands(cfg, 0x114)
        self.assertEqual(result["index_source"], "relative-slot-dereference")
        self.assertEqual(result["index_relative_slot_offset"], 0x100)
        self.assertEqual(result["index_word_addend"], 2)
        self.assertEqual(result["value"], 3)

    def test_predecessor_constants_are_marked_as_candidates_only(self) -> None:
        cfg = {
            "nodes": [
                {
                    "offset": 0,
                    "opcode": 69,
                    "immediate": 0,
                    "words": [69, 31 << 12],
                },
                {"offset": 8, "opcode": 99, "immediate": 0, "words": [99]},
                {"offset": 12, "opcode": 373, "immediate": 0, "words": [373]},
            ],
            "edges": [
                {"from": 0, "to": 8, "kind": "next"},
                {"from": 8, "to": 12, "kind": "next"},
            ],
        }

        self.assertEqual(
            inspect_dpsx.predecessor_constant_candidates(cfg, 12),
            [{"offset": 0, "integer_value": 31}],
        )

    def test_unique_predecessor_tail_keeps_short_chain_before_merge(self) -> None:
        cfg = {
            "nodes": [
                {"offset": 0, "opcode": 4, "immediate": 1},
                {"offset": 4, "opcode": 4, "immediate": 2},
                {"offset": 8, "opcode": 74, "immediate": 0},
                {"offset": 12, "opcode": 373, "immediate": 0},
            ],
            "edges": [
                {"from": 0, "to": 8, "kind": "branch"},
                {"from": 4, "to": 8, "kind": "next"},
                {"from": 8, "to": 12, "kind": "next"},
            ],
        }

        self.assertEqual(
            [node["offset"] for node in inspect_dpsx.unique_predecessor_tail(cfg, 12, 8)],
            [8],
        )

    def test_direct_local_predecessor_requires_one_adjacent_local_load(self) -> None:
        cfg = {
            "nodes": [
                {"offset": 0, "opcode": 4, "immediate": 20},
                {"offset": 4, "opcode": 513, "immediate": 0},
            ],
            "edges": [{"from": 0, "to": 4, "kind": "next"}],
        }

        self.assertEqual(
            inspect_dpsx.direct_local_predecessor(cfg, 4),
            {"offset": 0, "local_index": 20},
        )

    def test_direct_local_predecessors_preserve_stack_order(self) -> None:
        cfg = {
            "nodes": [
                {"offset": 0, "opcode": 4, "immediate": 11},
                {"offset": 4, "opcode": 4, "immediate": 12},
                {"offset": 8, "opcode": 4, "immediate": 13},
                {"offset": 12, "opcode": 370, "immediate": 0},
            ],
            "edges": [
                {"from": 0, "to": 4, "kind": "next"},
                {"from": 4, "to": 8, "kind": "next"},
                {"from": 8, "to": 12, "kind": "next"},
            ],
        }

        self.assertEqual(
            inspect_dpsx.direct_local_predecessors(cfg, 12, 3),
            [
                {"offset": 0, "local_index": 11},
                {"offset": 4, "local_index": 12},
                {"offset": 8, "local_index": 13},
            ],
        )

    def test_direct_property_predecessors_preserve_stack_order(self) -> None:
        cfg = {
            "nodes": [
                {"offset": 0, "opcode": 7, "immediate": 87},
                {"offset": 4, "opcode": 7, "immediate": 88},
                {"offset": 8, "opcode": 7, "immediate": 89},
                {"offset": 12, "opcode": 370, "immediate": 0},
            ],
            "edges": [
                {"from": 0, "to": 4, "kind": "next"},
                {"from": 4, "to": 8, "kind": "next"},
                {"from": 8, "to": 12, "kind": "next"},
            ],
        }

        self.assertEqual(
            inspect_dpsx.direct_property_predecessors(cfg, 12, 3),
            [
                {"offset": 0, "property_index": 87},
                {"offset": 4, "property_index": 88},
                {"offset": 8, "property_index": 89},
            ],
        )

    def test_reachable_local_stores_are_root_specific(self) -> None:
        cfg = {
            "nodes": [
                {
                    "offset": 4,
                    "opcode": 65,
                    "immediate": 0,
                    "reachable_from_roots": [100],
                },
                {
                    "offset": 8,
                    "opcode": 65,
                    "immediate": 1,
                    "reachable_from_roots": [100],
                },
                {
                    "offset": 12,
                    "opcode": 65,
                    "immediate": 0,
                    "reachable_from_roots": [200],
                },
            ],
            "edges": [],
        }

        self.assertEqual(inspect_dpsx.reachable_local_stores(cfg, 100, 0), [4])

    def test_direct_full_width_constant_predecessor(self) -> None:
        cfg = {
            "nodes": [
                {"offset": 0, "opcode": 69, "immediate": 0, "words": [69, 528384]},
                {"offset": 8, "opcode": 65, "immediate": 0, "words": [65]},
            ],
            "edges": [{"from": 0, "to": 8, "kind": "next"}],
        }

        self.assertEqual(
            inspect_dpsx.direct_fixed_constant_predecessor(cfg, 8), 528384
        )

    def test_reachability_can_require_one_of_several_stores(self) -> None:
        cfg = {
            "nodes": [],
            "edges": [
                {"from": 0, "to": 4, "kind": "fallthrough"},
                {"from": 0, "to": 12, "kind": "branch"},
                {"from": 4, "to": 20, "kind": "next"},
                {"from": 12, "to": 20, "kind": "next"},
            ],
        }

        self.assertTrue(inspect_dpsx.is_reachable_avoiding(cfg, 0, 20, {4}))
        self.assertFalse(
            inspect_dpsx.is_reachable_avoiding(cfg, 0, 20, {4, 12})
        )

    def test_compact_triplet_source_local_recognizes_decimal_split(self) -> None:
        instructions = [
            (4, 1, None),
            (68, 40, None),
            (75, 0, None),
            (171, 0, None),
            (65, 11, None),
            (4, 1, None),
            (4, 11, None),
            (69, 0, 409600),
            (75, 0, None),
            (74, 0, None),
            (68, 409, None),
            (75, 0, None),
            (171, 0, None),
            (65, 12, None),
            (4, 1, None),
            (4, 11, None),
            (69, 0, 409600),
            (75, 0, None),
            (74, 0, None),
            (4, 12, None),
            (69, 0, 40960),
            (75, 0, None),
            (74, 0, None),
            (171, 0, None),
            (65, 13, None),
            (4, 11, None),
            (4, 12, None),
            (4, 13, None),
            (370, 0, None),
        ]
        nodes = []
        offsets = []
        offset = 0
        for opcode, immediate, full_value in instructions:
            offsets.append(offset)
            words = [opcode] if full_value is None else [opcode, full_value]
            next_offset = offset + 4 * len(words)
            nodes.append(
                {
                    "offset": offset,
                    "next_offset": next_offset,
                    "opcode": opcode,
                    "immediate": immediate,
                    "words": words,
                }
            )
            offset = next_offset
        cfg = {
            "nodes": nodes,
            "edges": [
                {"from": source, "to": destination, "kind": "next"}
                for source, destination in zip(offsets, offsets[1:])
            ],
        }
        operands = [
            {"offset": offsets[-4], "local_index": 11},
            {"offset": offsets[-3], "local_index": 12},
            {"offset": offsets[-2], "local_index": 13},
        ]

        self.assertEqual(
            inspect_dpsx.compact_triplet_source_local(cfg, offsets[-1], operands),
            1,
        )

    def test_state_byte_triplet_indices_recognizes_dynamic_tuple(self) -> None:
        instructions = []
        for local_index, state_index in zip((11, 12, 13), (31, 32, 33)):
            instructions.extend(
                [
                    (69, 0, state_index << 12),
                    (371, 0, None),
                    (65, local_index, None),
                ]
            )
        instructions.extend(
            [(4, 11, None), (4, 12, None), (4, 13, None), (370, 0, None)]
        )
        nodes = []
        offsets = []
        offset = 0
        for opcode, immediate, full_value in instructions:
            offsets.append(offset)
            words = [opcode] if full_value is None else [opcode, full_value]
            next_offset = offset + 4 * len(words)
            nodes.append(
                {
                    "offset": offset,
                    "next_offset": next_offset,
                    "opcode": opcode,
                    "immediate": immediate,
                    "words": words,
                }
            )
            offset = next_offset
        cfg = {
            "nodes": nodes,
            "edges": [
                {"from": source, "to": destination, "kind": "next"}
                for source, destination in zip(offsets, offsets[1:])
            ],
        }
        operands = [
            {"offset": offsets[-4], "local_index": 11},
            {"offset": offsets[-3], "local_index": 12},
            {"offset": offsets[-2], "local_index": 13},
        ]

        self.assertEqual(
            inspect_dpsx.state_byte_triplet_indices(
                cfg, offsets[-1], operands
            ),
            [31, 32, 33],
        )

    def test_unconfirmed_event_table_stops_only_that_path(self) -> None:
        data = bytearray(32)
        struct.pack_into("<II", data, 0, 2, 100)
        view = inspect_dpsx.View(bytes(data))

        extent = inspect_dpsx.strategy_extent(view, 0, len(data))
        cfg = inspect_dpsx.build_strategy_cfg(view, [0], len(data))

        self.assertIn("unconfirmed instruction layout", extent["boundary_reason"])
        self.assertFalse(cfg["truncated"])
        self.assertEqual(len(cfg["stops"]), 1)
        self.assertIn("unconfirmed instruction layout", cfg["stops"][0]["reason"])

    def test_strategy_destruction_opcode_has_no_successor(self) -> None:
        data = bytearray(8)
        struct.pack_into("<II", data, 0, 179, 68)
        view = inspect_dpsx.View(bytes(data))

        cfg = inspect_dpsx.build_strategy_cfg(view, [0], len(data))

        self.assertEqual([node["offset"] for node in cfg["nodes"]], [0])
        self.assertEqual(cfg["edges"], [])

    def test_recursive_call_context_is_pruned_without_losing_its_edge(self) -> None:
        data = bytearray(8)
        struct.pack_into("<II", data, 0, 17, 0xFFFE0016)
        view = inspect_dpsx.View(bytes(data))

        cfg = inspect_dpsx.build_strategy_cfg(view, [0], len(data))

        self.assertFalse(cfg["truncated"])
        self.assertEqual([node["offset"] for node in cfg["nodes"]], [0, 4])
        self.assertTrue(
            any(stop["reason"] == "recursive call context pruned" for stop in cfg["stops"])
        )
        self.assertIn(
            {"from": 0, "to": 4, "kind": "call"},
            cfg["edges"],
        )

    def test_cfg_context_limit_is_configurable(self) -> None:
        data = bytearray(12)
        struct.pack_into("<III", data, 0, 0, 0, 179)
        view = inspect_dpsx.View(bytes(data))

        cfg = inspect_dpsx.build_strategy_cfg(
            view, [0], len(data), max_context_states=1
        )

        self.assertTrue(cfg["truncated"])
        self.assertEqual(cfg["context_state_limit"], 1)

    def test_context_insensitive_upper_bound_links_return_to_continuation(self) -> None:
        data = bytearray(12)
        struct.pack_into("<III", data, 0, 0x00010011, 179, 178)
        view = inspect_dpsx.View(bytes(data))

        result = inspect_dpsx.context_insensitive_strategy_nodes(
            view, [0], len(data)
        )

        self.assertEqual(result["node_offsets"], [0, 4, 8])

    def test_unconfirmed_switch_table_keeps_the_default_path_bounded(self) -> None:
        data = bytearray(32)
        struct.pack_into("<III", data, 0, 23, 0, 100)
        view = inspect_dpsx.View(bytes(data))

        cfg = inspect_dpsx.build_strategy_cfg(view, [0], len(data))

        self.assertFalse(cfg["truncated"])
        self.assertTrue(
            any("unconfirmed switch layout" in stop["reason"] for stop in cfg["stops"])
        )


if __name__ == "__main__":
    unittest.main()
