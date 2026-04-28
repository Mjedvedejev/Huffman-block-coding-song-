"""Description: Main application for Huffman coding of WAV/MP3 files (PARALLEL VERSION)."""

import heapq
import os
from collections import Counter
from concurrent.futures import ProcessPoolExecutor


# ---------------- NODE ----------------
class Node:
    """A node in the Huffman tree."""
    def __init__(self, byte=None, freq=0, left=None, right=None):
        self.byte = byte
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


# ---------------- FILE LOADING ----------------
def file_to_byte_array(file_path) -> bytes:
    """Reads a file and returns its contents as a byte array."""
    with open(file_path, 'rb') as file:
        return file.read()


# ---------------- HUFFMAN TREE ----------------
def build_heap(byte_array):
    """Builds a min-heap of nodes based on byte frequencies."""
    freq = Counter(byte_array)

    heap = []
    for byte, f in freq.items():
        heapq.heappush(heap, Node(byte=byte, freq=f))

    return heap


def build_huffman_tree(byte_array):
    """Builds the Huffman tree from the byte array and returns the root node."""
    heap = build_heap(byte_array)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)

        merged = Node(
            byte=None,
            freq=left.freq + right.freq,
            left=left,
            right=right
        )

        heapq.heappush(heap, merged)

    return heap[0]


# ---------------- CODE GENERATION ----------------
def generate_codes(node, prefix="", codebook=None):
    """Recursively generates the Huffman codes for each byte and returns a codebook."""
    if codebook is None:
        codebook = {}

    if node is None:
        return codebook

    if node.byte is not None:
        codebook[node.byte] = prefix

    generate_codes(node.left, prefix + "0", codebook)
    generate_codes(node.right, prefix + "1", codebook)

    return codebook


# ---------------- ENCODING ----------------
def encode_data(byte_array, codes):
    """Encodes the byte array into a bitstring using the generated codes."""
    return "".join(codes[byte] for byte in byte_array)


def write_compressed_file(bitstring, output_path):
    """Pads the bitstring to a multiple of 8 bits and writes it as bytes to the output file."""
    padding = (8 - len(bitstring) % 8) % 8
    bitstring += "0" * padding

    with open(output_path, "wb") as f:
        for i in range(0, len(bitstring), 8):
            byte = bitstring[i:i+8]
            f.write(int(byte, 2).to_bytes(1, byteorder="big"))


# ---------------- WORKER (PARALLEL UNIT) ----------------
def compress_file(file_path):
    """
    Compresses a single file using Huffman coding and returns
    the original and compressed sizes.
    """
    file_name = os.path.basename(file_path)

    byte_array = file_to_byte_array(file_path)

    # Huffman pipeline
    root = build_huffman_tree(byte_array)
    codes = generate_codes(root)
    bitstring = encode_data(byte_array, codes)

    output_file = f"Algorithm/src/Compressed/{file_name}.bin"
    write_compressed_file(bitstring, output_file)

    return file_name, len(byte_array), os.path.getsize(output_file)


# ---------------- MAIN ----------------
def main():
    """Main function to execute the Huffman coding compression in parallel."""
    songs_folder = "Algorithm/src/Songs"

    files = [
        os.path.join(songs_folder, f)
        for f in os.listdir(songs_folder)
        if f.endswith((".wav", ".mp3", ".wave"))
    ]

    if not files:
        raise FileNotFoundError("No files found in Songs folder")

    print(f"Found {len(files)} files. Starting parallel compression...\n")

    # PARALLEL EXECUTION
    with ProcessPoolExecutor() as executor:
        results = executor.map(compress_file, files)

    # Results
    print("\n--- Compression Results ---")
    for file_name, original, compressed in results:
        print(f"\nFile: {file_name}")
        print("Original size:  ", original, "bytes")
        print("Compressed size:", compressed, "bytes")


if __name__ == "__main__":
    main()
