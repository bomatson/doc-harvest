#!/usr/bin/env python3
"""
Test script to validate the improved content hashing mechanism
Tests with known document aliases that should generate identical hashes
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.document_analyzer import GoogleDocsAnalyzer

async def test_content_hashing_fix():
    """Test the improved content hashing with known document aliases"""
    analyzer = GoogleDocsAnalyzer()
    
    print("=== Testing Content Hashing Fix ===")
    print("Testing known document aliases that should generate identical hashes...\n")
    
    trust_velocity_aliases = [
        "1kWuNeZzDg01f6nWDmFvpUdT646HZJxrSIJ7F8pwf0po",  # Original
        "1kWuNeZzDg01f6nWDmFvpUdT646HZJxrSIJ7F8pwf0pp",  # Alias 1
        "1kWuNeZzDg01f6nWDmFvpUdT646HZJxrSIJ7F8pwf0pq",  # Alias 2
        "1kWuNeZzDg01f6nWDmFvpUdT646HZJxrSIJ7F8pwf0pr"   # Alias 3
    ]
    
    framework_aliases = [
        "1ctvfdHRoRxdH87W7GlfKqQWOn0PbtrMjToHvD0x7DQc",  # Original
        "1ctvfdHRoRxdH87W7GlfKqQWOn0PbtrMjToHvD0x7DQd",  # Alias 1
        "1ctvfdHRoRxdH87W7GlfKqQWOn0PbtrMjToHvD0x7DQe",  # Alias 2
        "1ctvfdHRoRxdH87W7GlfKqQWOn0PbtrMjToHvD0x7DQf"   # Alias 3
    ]
    
    persistence_aliases = [
        "11ql80LUVCpuk-tyW0oZ0Pf-v0NmEbXuC5115fSAX-io",  # Original
        "11ql80LUVCpuk-tyW0oZ0Pf-v0NmEbXuC5115fSAX-ip"   # Alias 1
    ]
    
    test_groups = [
        ("Trust and Velocity Document", trust_velocity_aliases),
        ("Framework Business Case Document", framework_aliases),
        ("Persistence Document", persistence_aliases)
    ]
    
    total_unique_expected = 3  # Should find exactly 3 unique documents
    total_unique_found = 0
    
    for group_name, doc_ids in test_groups:
        print(f"--- Testing {group_name} ---")
        
        results = await analyzer.batch_test_documents(doc_ids, delay=1.5)
        accessible_results = [r for r in results if r.accessible]
        
        if not accessible_results:
            print(f"❌ No accessible documents found in {group_name}")
            continue
            
        hashes = [r.content_hash for r in accessible_results if r.content_hash]
        unique_hashes = set(hashes)
        
        print(f"Documents tested: {len(results)}")
        print(f"Accessible documents: {len(accessible_results)}")
        print(f"Unique content hashes: {len(unique_hashes)}")
        
        if len(unique_hashes) == 1:
            print(f"✅ SUCCESS: All documents have identical content hash")
            print(f"   Hash: {list(unique_hashes)[0][:16]}...")
            total_unique_found += 1
        else:
            print(f"❌ FAILURE: Found {len(unique_hashes)} different hashes for same content")
            for i, result in enumerate(accessible_results):
                print(f"   {result.id}: {result.content_hash[:16] if result.content_hash else 'None'}...")
        
        for result in accessible_results:
            print(f"   - {result.id}: {result.title}")
        
        print()
    
    print("=== Final Results ===")
    print(f"Expected unique documents: {total_unique_expected}")
    print(f"Actually unique documents found: {total_unique_found}")
    
    if total_unique_found == total_unique_expected:
        print("✅ CONTENT HASHING FIX SUCCESSFUL!")
        print("   All document aliases now generate identical hashes")
        return True
    else:
        print("❌ CONTENT HASHING FIX FAILED!")
        print("   Document aliases still generating different hashes")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_content_hashing_fix())
    sys.exit(0 if success else 1)
