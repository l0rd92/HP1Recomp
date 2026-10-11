-- Read-only runtime observer for the HP1 US.GAM Strategy audio/zone handlers.
-- Requires PCSX-Redux's debugger and interpreter CPU. Load from the Lua console.

local ffi = require("ffi")
local bit = require("bit")

if HP1Trace ~= nil and HP1Trace.stop ~= nil then
    HP1Trace.stop()
end

local trace = {
    breakpoints = {},
    seen = {},
    eventCount = 0,
    eventLimit = 200,
    autoStart = os.getenv("HP1_TRACE_AUTO_START") == "1",
    autoStartHitCount = 0,
    autoStartNextHit = 1,
    autoInputTapCount = 0,
    autoStartRemainingHits = 0,
    autoInputButton = nil,
}
HP1Trace = trace

local memory = PCSX.getMemPtr()

local function emit(message)
    print(message)
    if PCSX.log ~= nil then
        PCSX.log(message)
    end
end

local function physical(address)
    return bit.band(tonumber(address), 0x007fffff)
end

local function u32(address)
    return tonumber(ffi.cast("uint32_t *", memory + physical(address))[0])
end

local function s32(address)
    return tonumber(ffi.cast("int32_t *", memory + physical(address))[0])
end

local function validRamPointer(address)
    local value = physical(address)
    return value >= 0x10000 and value <= 0x7ffffc
end

local function localValue(strategy, index)
    local locals = u32(strategy + 8)
    if not validRamPointer(locals) then
        return 0
    end
    return s32(locals + index * 4)
end

local function stackTop(strategy)
    local stack = u32(strategy + 4)
    if not validRamPointer(stack) then
        return 0
    end
    return s32(stack - 4)
end

local handlers = {
    { address = 0x00038ed0, name = "audio-start-class-2" }, -- opcode 153
    { address = 0x000391bc, name = "audio-start-class-1" }, -- opcode 157
    { address = 0x00038734, name = "audio-handle-command" }, -- opcode 152
    { address = 0x00038dec, name = "audio-query" }, -- opcode 289
    { address = 0x0003a76c, name = "zone-test-coordinates" }, -- opcode 353
    { address = 0x0003a854, name = "zone-test-registered-strategy" }, -- opcode 443
    { address = 0x0003ec78, name = "selected-local-store" }, -- opcode 65
    { address = 0x0003ec30, name = "selected-bytecode-write" }, -- opcode 64
}

local patchCheckpoints = {
    { address = 0x00010604, name = "instruction-patches-before" },
    { address = 0x00010618, name = "instruction-patches-after-first" },
    { address = 0x00010620, name = "instruction-patches-after-second" },
}

local function observeInstructionPatches(name)
    local first = u32(0x00056388)
    local second = u32(0x00057f20)
    local key = string.format("%s:%08x:%08x", name, first, second)
    if trace.seen[key] then
        return
    end
    trace.seen[key] = true
    trace.eventCount = trace.eventCount + 1
    emit(string.format(
        "HP1TRACE %03d %-31s word_56388=%08x word_57f20=%08x",
        trace.eventCount, name, first, second
    ))
end

local function serviceAutoStart(name)
    if not trace.autoStart then
        return
    end
    trace.autoStartHitCount = trace.autoStartHitCount + 1
    local pad = PCSX.SIO0.slots[1].pads[1]
    local sequence = {
        { button = PCSX.CONSTS.PAD.BUTTON.START, name = "Start" },
        { button = PCSX.CONSTS.PAD.BUTTON.START, name = "Start" },
        { button = PCSX.CONSTS.PAD.BUTTON.CROSS, name = "Cross" },
        { button = PCSX.CONSTS.PAD.BUTTON.CROSS, name = "Cross" },
    }
    if trace.autoStartRemainingHits > 0 then
        trace.autoStartRemainingHits = trace.autoStartRemainingHits - 1
        if trace.autoStartRemainingHits == 0 then
            pad.clearOverride(trace.autoInputButton.button)
            emit(string.format(
                "HP1TRACE automatic %s tap %d released",
                trace.autoInputButton.name, trace.autoInputTapCount
            ))
        end
        return
    end
    if name == "zone-test-registered-strategy" and
       trace.autoStartHitCount >= trace.autoStartNextHit and
       trace.autoInputTapCount < #sequence then
        trace.autoInputTapCount = trace.autoInputTapCount + 1
        trace.autoInputButton = sequence[trace.autoInputTapCount]
        trace.autoStartNextHit = trace.autoStartHitCount + 120
        trace.autoStartRemainingHits = 12
        pad.setOverride(trace.autoInputButton.button)
        emit(string.format(
            "HP1TRACE automatic %s tap %d pressed at handler hit %d",
            trace.autoInputButton.name, trace.autoInputTapCount,
            trace.autoStartHitCount
        ))
    end
end

local function observe(name)
    serviceAutoStart(name)
    local registers = PCSX.getRegisters()
    local strategy = tonumber(registers.GPR.n.a0)
    local argument = tonumber(registers.GPR.n.a1)
    if not validRamPointer(strategy) then
        return
    end
    if name == "selected-local-store" and argument ~= 7 and argument ~= 18 then
        return
    end
    if name == "selected-bytecode-write" and argument ~= 167 then
        return
    end

    local instruction = u32(strategy)
    local top = stackTop(strategy)
    local values = {
        localValue(strategy, 6),
        localValue(strategy, 7),
        localValue(strategy, 16),
        localValue(strategy, 17),
        localValue(strategy, 18),
    }
    local key = string.format(
        "%s:%08x:%08x:%d:%d:%d:%d:%d:%d:%d",
        name, strategy, instruction, argument, top,
        values[1], values[2], values[3], values[4], values[5]
    )
    if trace.seen[key] then
        return
    end
    trace.seen[key] = true
    trace.eventCount = trace.eventCount + 1
    emit(string.format(
        "HP1TRACE %03d %-31s strategy=%08x next_ip=%08x arg=%d top=%d " ..
        "l6=%d l7=%d l16=%d l17=%d l18=%d",
        trace.eventCount, name, strategy, instruction, argument, top,
        values[1], values[2], values[3], values[4], values[5]
    ))
    if trace.eventCount >= trace.eventLimit then
        emit("HP1TRACE event limit reached; disabling observers")
        trace.stop()
    end
end

for _, handler in ipairs(handlers) do
    local name = handler.name
    local breakpoint = PCSX.addBreakpoint(
        handler.address,
        "Exec",
        4,
        "HP1 Strategy " .. name,
        function()
            local ok, message = pcall(observe, name)
            if not ok then
                emit("HP1TRACE error: " .. tostring(message))
            end
        end
    )
    table.insert(trace.breakpoints, breakpoint)
end

for _, checkpoint in ipairs(patchCheckpoints) do
    local name = checkpoint.name
    local breakpoint = PCSX.addBreakpoint(
        checkpoint.address,
        "Exec",
        4,
        "HP1 " .. name,
        function()
            local ok, message = pcall(observeInstructionPatches, name)
            if not ok then
                emit("HP1TRACE error: " .. tostring(message))
            end
        end
    )
    table.insert(trace.breakpoints, breakpoint)
end

function trace.stop()
    for _, breakpoint in ipairs(trace.breakpoints) do
        breakpoint:remove()
    end
    trace.breakpoints = {}
    emit(string.format("HP1TRACE stopped after %d distinct events", trace.eventCount))
end

function trace.status()
    emit(string.format(
        "HP1TRACE active=%s events=%d/%d",
        tostring(#trace.breakpoints > 0), trace.eventCount, trace.eventLimit
    ))
end

emit("HP1TRACE ready: 11 read-only runtime observers, limit 200 events")
emit("HP1TRACE commands: HP1Trace.status()  HP1Trace.stop()")
if trace.autoStart then
    emit("HP1TRACE automatic Start/Cross mode enabled")
end
