// Exports decompiler text for an explicit, bounded list of function addresses.
// @category HP1Recomp

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class ExportSelectedFunctions extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) {
            throw new IllegalArgumentException(
                "Usage: ExportSelectedFunctions.java <output.txt> <address> [address ...]");
        }

        File output = new File(args[0]);
        File parent = output.getParentFile();
        if (parent != null) {
            parent.mkdirs();
        }

        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);
        try (PrintWriter writer = new PrintWriter(output, StandardCharsets.UTF_8)) {
            for (int i = 1; i < args.length; i++) {
                monitor.checkCancelled();
                Address address = currentProgram.getAddressFactory()
                    .getDefaultAddressSpace().getAddress(args[i]);
                Function function = currentProgram.getFunctionManager().getFunctionAt(address);
                writer.println("=== " + args[i] + " ===");
                if (function == null) {
                    disassemble(address);
                    function = createFunction(address, null);
                }
                if (function == null) {
                    writer.println("Could not create a temporary function at this address.");
                    writer.println();
                    continue;
                }

                DecompileResults result = decompiler.decompileFunction(function, 60, monitor);
                if (!result.decompileCompleted()) {
                    writer.println("Decompilation failed: " + result.getErrorMessage());
                }
                else {
                    writer.println(result.getDecompiledFunction().getC());
                }
                writer.println();
            }
        }
        decompiler.dispose();
        println("Selected-function export written to " + output);
    }
}
