"""Chunking simulator (educational, std-lib only)."""
def chunk(text, size, overlap):
    chunks = []; i = 0
    while i < len(text):
        chunks.append(text[i:i+size])
        if i + size >= len(text): break
        i += size - overlap
    return chunks
def main():
    doc = "The quick brown fox jumps over the lazy dog. " * 50
    for size, overlap in [(100, 0), (200, 50), (500, 100)]:
        c = chunk(doc, size, overlap)
        print(f"size={size:4} overlap={overlap:3} -> {len(c):3} chunks")
    print("\nSmaller chunks = more recall but more cost and noise.")
if __name__ == "__main__": main()
