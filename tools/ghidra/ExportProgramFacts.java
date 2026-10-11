/* ###
 * IP: HP1Recomp
 */
// Exports reusable structural facts from an already analyzed program.
// Run headless with -readOnly -noanalysis and one output-directory argument.
//@category HP1Recomp

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceManager;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;
import ghidra.program.model.symbol.SymbolTable;

public class ExportProgramFacts extends GhidraScript {

    private static String csv(String value) {
        if (value == null) {
            return "";
        }
        return "\"" + value.replace("\"", "\"\"").replace("\r", " ").replace("\n", " ") + "\"";
    }

    private static void row(BufferedWriter writer, String... values) throws IOException {
        for (int i = 0; i < values.length; i++) {
            if (i != 0) {
                writer.write(',');
            }
            writer.write(csv(values[i]));
        }
        writer.newLine();
    }

    private static String address(Address address) {
        return address == null ? "" : address.toString();
    }

    private static String functionName(Function function) {
        return function == null ? "" : function.getName(true);
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) {
            throw new IllegalArgumentException("Expected one argument: output directory");
        }

        Path outputDirectory = Paths.get(args[0]).toAbsolutePath().normalize();
        Files.createDirectories(outputDirectory);

        FunctionManager functionManager = currentProgram.getFunctionManager();
        ReferenceManager referenceManager = currentProgram.getReferenceManager();
        SymbolTable symbolTable = currentProgram.getSymbolTable();

        long symbolCount = 0;
        Path symbolsPath = outputDirectory.resolve("symbols.csv");
        try (BufferedWriter writer = Files.newBufferedWriter(symbolsPath, StandardCharsets.UTF_8)) {
            row(writer, "address", "name", "namespace", "type", "source", "primary");
            SymbolIterator symbols = symbolTable.getAllSymbols(true);
            while (symbols.hasNext() && !monitor.isCancelled()) {
                Symbol symbol = symbols.next();
                if (symbol.isDynamic()) {
                    continue;
                }
                row(writer,
                    address(symbol.getAddress()),
                    symbol.getName(),
                    symbol.getParentNamespace().getName(true),
                    symbol.getSymbolType().toString(),
                    symbol.getSource().toString(),
                    Boolean.toString(symbol.isPrimary()));
                symbolCount++;
            }
        }

        long functionCount = 0;
        Path functionsPath = outputDirectory.resolve("functions.csv");
        try (BufferedWriter writer = Files.newBufferedWriter(functionsPath, StandardCharsets.UTF_8)) {
            row(writer, "entry", "name", "namespace", "body_min", "body_max", "body_addresses",
                "signature", "source", "thunk", "external");
            FunctionIterator functions = functionManager.getFunctions(true);
            while (functions.hasNext() && !monitor.isCancelled()) {
                Function function = functions.next();
                row(writer,
                    address(function.getEntryPoint()),
                    function.getName(),
                    function.getParentNamespace().getName(true),
                    address(function.getBody().getMinAddress()),
                    address(function.getBody().getMaxAddress()),
                    Long.toString(function.getBody().getNumAddresses()),
                    function.getSignature().toString(),
                    function.getSymbol().getSource().toString(),
                    Boolean.toString(function.isThunk()),
                    Boolean.toString(function.isExternal()));
                functionCount++;
            }
        }

        long memoryBlockCount = 0;
        Path memoryMapPath = outputDirectory.resolve("memory-map.csv");
        try (BufferedWriter writer = Files.newBufferedWriter(memoryMapPath, StandardCharsets.UTF_8)) {
            row(writer, "name", "start", "end", "size", "type", "initialized", "read", "write",
                "execute", "volatile", "overlay", "source");
            for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
                row(writer,
                    block.getName(),
                    address(block.getStart()),
                    address(block.getEnd()),
                    Long.toUnsignedString(block.getSize()),
                    block.getType().toString(),
                    Boolean.toString(block.isInitialized()),
                    Boolean.toString(block.isRead()),
                    Boolean.toString(block.isWrite()),
                    Boolean.toString(block.isExecute()),
                    Boolean.toString(block.isVolatile()),
                    Boolean.toString(block.isOverlay()),
                    block.getSourceName());
                memoryBlockCount++;
            }
        }

        long referenceCount = 0;
        long callCount = 0;
        Path referencesPath = outputDirectory.resolve("references.csv");
        Path callsPath = outputDirectory.resolve("calls.csv");
        try (BufferedWriter referenceWriter = Files.newBufferedWriter(referencesPath, StandardCharsets.UTF_8);
             BufferedWriter callWriter = Files.newBufferedWriter(callsPath, StandardCharsets.UTF_8)) {
            row(referenceWriter, "from", "to", "type", "operand_index", "primary", "external",
                "from_function", "to_function");
            row(callWriter, "callsite", "caller_entry", "caller", "target", "target_entry", "callee",
                "type", "primary", "external");

            AddressIterator sources = referenceManager.getReferenceSourceIterator(currentProgram.getMemory(), true);
            while (sources.hasNext() && !monitor.isCancelled()) {
                Address source = sources.next();
                Function caller = functionManager.getFunctionContaining(source);
                for (Reference reference : referenceManager.getReferencesFrom(source)) {
                    Address target = reference.getToAddress();
                    Function callee = functionManager.getFunctionAt(target);
                    if (callee == null) {
                        callee = functionManager.getFunctionContaining(target);
                    }
                    row(referenceWriter,
                        address(source),
                        address(target),
                        reference.getReferenceType().toString(),
                        Integer.toString(reference.getOperandIndex()),
                        Boolean.toString(reference.isPrimary()),
                        Boolean.toString(reference.isExternalReference()),
                        functionName(caller),
                        functionName(callee));
                    referenceCount++;

                    if (reference.getReferenceType().isCall()) {
                        row(callWriter,
                            address(source),
                            caller == null ? "" : address(caller.getEntryPoint()),
                            functionName(caller),
                            address(target),
                            callee == null ? "" : address(callee.getEntryPoint()),
                            functionName(callee),
                            reference.getReferenceType().toString(),
                            Boolean.toString(reference.isPrimary()),
                            Boolean.toString(reference.isExternalReference()));
                        callCount++;
                    }
                }
            }
        }

        JsonObject program = new JsonObject();
        program.addProperty("name", currentProgram.getName());
        program.addProperty("domain_path", currentProgram.getDomainFile().getPathname());
        program.addProperty("executable_format", currentProgram.getExecutableFormat());
        program.addProperty("executable_sha256", currentProgram.getExecutableSHA256());
        program.addProperty("language", currentProgram.getLanguageID().getIdAsString());
        program.addProperty("compiler_spec", currentProgram.getCompilerSpec().getCompilerSpecID().getIdAsString());
        program.addProperty("image_base", address(currentProgram.getImageBase()));
        program.addProperty("min_address", address(currentProgram.getMinAddress()));
        program.addProperty("max_address", address(currentProgram.getMaxAddress()));
        program.addProperty("functions", functionCount);
        program.addProperty("symbols", symbolCount);
        program.addProperty("calls", callCount);
        program.addProperty("references", referenceCount);
        program.addProperty("memory_blocks", memoryBlockCount);
        program.addProperty("analysis_was_run", false);
        program.addProperty("project_was_writable", false);

        Gson gson = new GsonBuilder().setPrettyPrinting().create();
        try (BufferedWriter writer = Files.newBufferedWriter(outputDirectory.resolve("program.json"), StandardCharsets.UTF_8)) {
            gson.toJson(program, writer);
        }

        try (BufferedWriter writer = Files.newBufferedWriter(outputDirectory.resolve("summary.md"), StandardCharsets.UTF_8)) {
            writer.write("# Ghidra structural export: " + currentProgram.getName());
            writer.newLine();
            writer.newLine();
            writer.write("Generated from the saved Ghidra program with analysis disabled and the project opened read-only.");
            writer.newLine();
            writer.newLine();
            writer.write("| Item | Count |");
            writer.newLine();
            writer.write("|---|---:|");
            writer.newLine();
            writer.write("| Functions | " + functionCount + " |");
            writer.newLine();
            writer.write("| Non-dynamic symbols | " + symbolCount + " |");
            writer.newLine();
            writer.write("| Call references | " + callCount + " |");
            writer.newLine();
            writer.write("| All references | " + referenceCount + " |");
            writer.newLine();
            writer.write("| Memory blocks | " + memoryBlockCount + " |");
            writer.newLine();
        }

        println("Exported " + currentProgram.getName() + " to " + outputDirectory);
        println("Functions=" + functionCount + ", symbols=" + symbolCount + ", calls=" + callCount +
            ", references=" + referenceCount + ", memory blocks=" + memoryBlockCount);
    }
}
