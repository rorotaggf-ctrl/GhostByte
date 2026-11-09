# GhostByte

> **Hack Club Crescent — Challenge: Weird Storage**  
> *"Store files in non-file formats"*

GhostByte is an unconventional steganographic storage engine that encodes arbitrary binary files (archives, executables, images) into innocent, human-readable UTF-8 text documents using invisible zero-width Unicode characters.

The carrier document remains 100% readable and visually identical when opened in any standard text editor, terminal viewer, or browser window, while silently storing full binary payloads embedded directly within its Unicode sequence.

---

## Technical Overview & How It Works

1. **Byte to 2-Bit Translation:**  
   Every single byte ($0\dots255$) of the target file is split into four 2-bit chunks (`00`, `01`, `10`, `11`).

2. **Invisible Homoglyph Mapping:**  
   Each 2-bit chunk is mapped to a specific zero-width Unicode character:
   - `00` $\rightarrow$ `\u200B` (Zero-Width Space)
   - `01` $\rightarrow$ `\u200C` (Zero-Width Non-Joiner)
   - `10` $\rightarrow$ `\u200D` (Zero-Width Joiner)
   - `11` $\rightarrow$ `\uFEFF` (Zero-Width No-Break Space)

3. **Framing & Payload Injection:**  
   The resulting zero-width stream is framed with magic start/stop byte signatures (`\u200B\u200D\u200B\u200D` and `\uFEFF\u200C\uFEFF\u200C`) and injected into the paragraph structure of any innocent host text file.

4. **Decoding & Extraction:**  
   The extraction engine parses the host document, filters out standard visible characters, locates the magic boundary markers, reconstructs the bitstream, and outputs the exact original binary payload bit-by-bit.

---

## Installation & Requirements

Requires **Python 3.8+**. Standard library only (no external pip dependencies).

```bash
git clone https://github.com/rorotaggf-ctrl/GhostByte.git
cd GhostByte
chmod +x ghostbyte.py
```

---

## CLI Usage

### 1. Hide a File Inside Text
Embed any arbitrary binary file into an innocent carrier document:
```bash
python3 ghostbyte.py hide carrier.txt secret.zip output.txt
```

### 2. Extract and Recover the File
Recover the hidden payload back to its original binary format:
```bash
python3 ghostbyte.py extract output.txt recovered_secret.zip
```

---

## Proof of Concept & Verification

Verify that the restored file is identical to the original input:

```bash
# Check cryptographic hash match
sha256sum secret.zip
sha256sum recovered_secret.zip
```

Inspect the hidden payload inside the carrier text file:
```bash
# Looks like regular text to standard tools
cat output.txt

# Reveals the invisible byte patterns
xxd output.txt | head -n 30
```

---

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0) or GNU Affero General Public License v3.0 (AGPL-3.0). See the `LICENSE` file for details.