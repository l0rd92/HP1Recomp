// Imports simple "address name" records from a PsyQ-style linker MAP file.
// @category HP1Recomp

import java.io.BufferedReader;
import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.HashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolUtilities;

public class ImportLinkerMap extends GhidraScript {
    private static final Pattern RECORD =
        Pattern.compile("^\\s*([0-9A-Fa-f]{8})\\s+([^\\s]+)\\s*$");

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        File mapFile = args.length > 0 ? new File(args[0]) : askFile("Select linker MAP", "Import");
        if (!mapFile.isFile()) {
            throw new IllegalArgumentException("MAP file not found: " + mapFile);
        }

        int records = 0;
        int functionsRenamed = 0;
        int labelsCreated = 0;
        int duplicates = 0;
        int existing = 0;
        int outsideMemory = 0;
        Set<String> seen = new HashSet<>();

        try (BufferedReader reader = Files.newBufferedReader(mapFile.toPath(), StandardCharsets.ISO_8859_1)) {
            String line;
            while ((line = reader.readLine()) != null) {
                monitor.checkCancelled();
                Matcher matcher = RECORD.matcher(line);
                if (!matcher.matches()) {
                    continue;
                }
                records++;

                Address address = currentProgram.getAddressFactory()
                    .getDefaultAddressSpace().getAddress(matcher.group(1));
                if (!currentProgram.getMemory().contains(address)) {
                    outsideMemory++;
                    continue;
                }

                String name = SymbolUtilities.replaceInvalidChars(matcher.group(2), true);
                if (!seen.add(address + "\n" + name)) {
                    duplicates++;
                    continue;
                }

                boolean alreadyPresent = false;
                for (Symbol symbol : currentProgram.getSymbolTable().getSymbols(address)) {
                    if (symbol.getName().equals(name)) {
                        alreadyPresent = true;
                        break;
                    }
                }
                if (alreadyPresent) {
                    existing++;
                    continue;
                }

                Function function = currentProgram.getFunctionManager().getFunctionAt(address);
                if (function != null) {
                    function.setName(name, SourceType.IMPORTED);
                    functionsRenamed++;
                }
                else {
                    createLabel(address, name, false, SourceType.IMPORTED);
                    labelsCreated++;
                }
            }
        }

        println("MAP import finished: " + mapFile);
        println("Records=" + records + ", functions renamed=" + functionsRenamed
            + ", labels created=" + labelsCreated + ", duplicate records=" + duplicates
            + ", existing symbols=" + existing + ", outside memory=" + outsideMemory);
    }
}
