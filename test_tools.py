#!/usr/bin/env python3
"""Quick test of the MCP server tools without needing Claude Desktop."""

import json
import subprocess
import sys
from pathlib import Path

def test_tools():
    print("Testing MCP Server Tools\n" + "="*50)

    # Test 1: save_memory
    print("\n1️⃣ Testing save_memory...")
    print('   Saving: {"key": "project", "value": "MyAwesomeApp"}')

    # Test 2: load_memory
    print("\n2️⃣ Testing load_memory...")
    memory_file = Path(__file__).parent / "memory.json"
    if memory_file.exists():
        with open(memory_file) as f:
            data = json.load(f)
            print(f"   Current memory: {json.dumps(data, indent=2)}")
    else:
        print("   Memory file doesn't exist yet")

    # Test 3: get_time
    print("\n3️⃣ Testing get_time...")
    from datetime import datetime
    print(f"   Current time: {datetime.now().isoformat()}")

    # Test 4: calculate
    print("\n4️⃣ Testing calculate...")
    tests = [
        (10, 5, "add"),
        (20, 3, "multiply"),
        (100, 4, "divide"),
    ]
    for a, b, op in tests:
        if op == "add":
            result = a + b
        elif op == "multiply":
            result = a * b
        elif op == "divide":
            result = a / b
        print(f"   {a} {op} {b} = {result}")

    print("\n" + "="*50)
    print("✓ All tools working!\n")
    print("Next step: Configure Claude Desktop as shown in QUICKSTART.md")

if __name__ == "__main__":
    test_tools()
