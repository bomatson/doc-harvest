"""
Google Docs Document ID Analyzer and Tester
Analyzes document ID patterns and tests incremental access
"""

import re
import string
import asyncio
import httpx
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentInfo:
    id: str
    url: str
    accessible: bool
    title: Optional[str] = None
    content_preview: Optional[str] = None
    content_hash: Optional[str] = None
    error: Optional[str] = None

class GoogleDocsAnalyzer:
    def __init__(self):
        self.base_urls = [
            "https://docs.google.com/document/d/{}/edit",
            "https://docs.google.com/document/d/{}/export?format=txt",
            "https://docs.google.com/document/d/{}/pub"
        ]
        self.known_ids = [
            "11ql80LUVCpuk-tyW0oZ0Pf-v0NmEbXuC5115fSAX-io",
            "1ctvfdHRoRxdH87W7GlfKqQWOn0PbtrMjToHvD0x7DQc", 
            "1kWuNeZzDg01f6nWDmFvpUdT646HZJxrSIJ7F8pwf0po"
        ]
        
    def analyze_id_structure(self, doc_id: str) -> Dict:
        """Analyze the structure of a document ID"""
        return {
            "length": len(doc_id),
            "character_counts": {char: doc_id.count(char) for char in set(doc_id)},
            "has_hyphens": "-" in doc_id,
            "has_underscores": "_" in doc_id,
            "alphanumeric_only": doc_id.replace("-", "").replace("_", "").isalnum(),
            "starts_with_digit": doc_id[0].isdigit() if doc_id else False,
            "pattern_analysis": self._analyze_patterns(doc_id)
        }
    
    def _analyze_patterns(self, doc_id: str) -> Dict:
        """Look for patterns in the document ID"""
        patterns = {
            "consecutive_digits": re.findall(r'\d+', doc_id),
            "consecutive_letters": re.findall(r'[a-zA-Z]+', doc_id),
            "special_chars": re.findall(r'[-_]', doc_id),
            "alternating_pattern": self._check_alternating_pattern(doc_id)
        }
        return patterns
    
    def _check_alternating_pattern(self, doc_id: str) -> bool:
        """Check if there's an alternating letter/digit pattern"""
        if len(doc_id) < 2:
            return False
        
        for i in range(len(doc_id) - 1):
            curr_is_digit = doc_id[i].isdigit()
            next_is_digit = doc_id[i + 1].isdigit()
            if curr_is_digit == next_is_digit and doc_id[i] not in '-_':
                continue
        return True
    
    def generate_incremented_ids(self, base_id: str, increment_strategies: Optional[List[str]] = None) -> List[str]:
        """Generate incremented versions of a document ID"""
        if increment_strategies is None:
            increment_strategies = ["last_char", "last_digit", "last_letter", "all_positions", "pattern_based"]
        
        incremented_ids = []
        
        for strategy in increment_strategies:
            if strategy == "last_char":
                incremented_ids.extend(self._increment_last_char(base_id))
            elif strategy == "last_digit":
                incremented_ids.extend(self._increment_last_digit(base_id))
            elif strategy == "last_letter":
                incremented_ids.extend(self._increment_last_letter(base_id))
            elif strategy == "all_positions":
                incremented_ids.extend(self._increment_all_positions(base_id))
            elif strategy == "pattern_based":
                incremented_ids.extend(self._generate_pattern_based_ids(base_id))
        
        return list(set(incremented_ids))  # Remove duplicates
    
    def _increment_last_char(self, doc_id: str, count: int = 5) -> List[str]:
        """Increment the last character of the document ID"""
        if not doc_id:
            return []
        
        results = []
        last_char = doc_id[-1]
        base = doc_id[:-1]
        
        for i in range(1, count + 1):
            if last_char.isdigit():
                new_digit = (int(last_char) + i) % 10
                results.append(base + str(new_digit))
            elif last_char.islower():
                new_char_ord = ord(last_char) + i
                if new_char_ord <= ord('z'):
                    results.append(base + chr(new_char_ord))
            elif last_char.isupper():
                new_char_ord = ord(last_char) + i
                if new_char_ord <= ord('Z'):
                    results.append(base + chr(new_char_ord))
        
        return results
    
    def _increment_last_digit(self, doc_id: str, count: int = 10) -> List[str]:
        """Find and increment the last digit in the document ID"""
        results = []
        
        last_digit_pos = -1
        for i in range(len(doc_id) - 1, -1, -1):
            if doc_id[i].isdigit():
                last_digit_pos = i
                break
        
        if last_digit_pos == -1:
            return results
        
        last_digit = int(doc_id[last_digit_pos])
        base_before = doc_id[:last_digit_pos]
        base_after = doc_id[last_digit_pos + 1:]
        
        for i in range(1, count + 1):
            new_digit = (last_digit + i) % 10
            results.append(base_before + str(new_digit) + base_after)
        
        return results
    
    def _increment_last_letter(self, doc_id: str, count: int = 5) -> List[str]:
        """Find and increment the last letter in the document ID"""
        results = []
        
        last_letter_pos = -1
        for i in range(len(doc_id) - 1, -1, -1):
            if doc_id[i].isalpha():
                last_letter_pos = i
                break
        
        if last_letter_pos == -1:
            return results
        
        last_letter = doc_id[last_letter_pos]
        base_before = doc_id[:last_letter_pos]
        base_after = doc_id[last_letter_pos + 1:]
        
        for i in range(1, count + 1):
            if last_letter.islower():
                new_char_ord = ord(last_letter) + i
                if new_char_ord <= ord('z'):
                    results.append(base_before + chr(new_char_ord) + base_after)
            elif last_letter.isupper():
                new_char_ord = ord(last_letter) + i
                if new_char_ord <= ord('Z'):
                    results.append(base_before + chr(new_char_ord) + base_after)
        
        return results
    
    def _increment_all_positions(self, doc_id: str, max_per_position: int = 2) -> List[str]:
        """Try incrementing each position in the document ID"""
        results = []
        
        for pos in range(len(doc_id)):
            char = doc_id[pos]
            base_before = doc_id[:pos]
            base_after = doc_id[pos + 1:]
            
            for i in range(1, max_per_position + 1):
                if char.isdigit():
                    new_digit = (int(char) + i) % 10
                    results.append(base_before + str(new_digit) + base_after)
                elif char.islower():
                    new_char_ord = ord(char) + i
                    if new_char_ord <= ord('z'):
                        results.append(base_before + chr(new_char_ord) + base_after)
                elif char.isupper():
                    new_char_ord = ord(char) + i
                    if new_char_ord <= ord('Z'):
                        results.append(base_before + chr(new_char_ord) + base_after)
        
        return results
    
    def _generate_pattern_based_ids(self, base_id: str, count: int = 20) -> List[str]:
        """Generate IDs based on structural patterns found in known working IDs"""
        results = []
        
        results.extend(self._test_hyphen_variations(base_id, count // 4))
        results.extend(self._test_digit_sequence_patterns(base_id, count // 4))
        results.extend(self._test_segment_boundaries(base_id, count // 4))
        results.extend(self._test_length_variations(base_id, count // 4))
        
        return results
    
    def _test_hyphen_variations(self, base_id: str, count: int = 5) -> List[str]:
        """Test variations with different hyphen positions based on known patterns"""
        results = []
        known_hyphen_positions = [[13, 23, 41], []]  # From analysis of known IDs
        
        for positions in known_hyphen_positions:
            if len(positions) == 0:
                new_id = base_id.replace('-', '')
                if len(new_id) == 44:
                    results.append(new_id)
            else:
                chars = list(base_id.replace('-', ''))
                if len(chars) >= max(positions):
                    for pos in sorted(positions, reverse=True):
                        if pos < len(chars):
                            chars.insert(pos, '-')
                    new_id = ''.join(chars)
                    if len(new_id) == 44:
                        results.append(new_id)
        
        return results[:count]
    
    def _test_digit_sequence_patterns(self, base_id: str, count: int = 5) -> List[str]:
        """Test variations in digit sequences based on patterns from known IDs"""
        results = []
        digit_sequences = re.findall(r'\d+', base_id)
        
        for i, seq in enumerate(digit_sequences):
            if len(seq) >= 2:
                try:
                    num = int(seq)
                    for delta in [-2, -1, 1, 2]:
                        new_num = max(0, num + delta)
                        new_seq = str(new_num).zfill(len(seq))
                        new_id = base_id.replace(seq, new_seq, 1)
                        if new_id != base_id:
                            results.append(new_id)
                except ValueError:
                    continue
        
        return results[:count]
    
    def _test_segment_boundaries(self, base_id: str, count: int = 5) -> List[str]:
        """Test variations at boundaries between letter and digit segments"""
        results = []
        
        for i in range(len(base_id) - 1):
            curr_char = base_id[i]
            next_char = base_id[i + 1]
            
            if curr_char.isalpha() and next_char.isdigit():
                chars = list(base_id)
                chars[i], chars[i + 1] = chars[i + 1], chars[i]
                results.append(''.join(chars))
            elif curr_char.isdigit() and next_char.isalpha():
                chars = list(base_id)
                chars[i], chars[i + 1] = chars[i + 1], chars[i]
                results.append(''.join(chars))
        
        return results[:count]
    
    def _test_length_variations(self, base_id: str, count: int = 5) -> List[str]:
        """Test slight length variations while maintaining structure"""
        results = []
        
        for i in range(0, len(base_id), len(base_id) // count):
            if base_id[i] not in '-_':
                new_id = base_id[:i] + base_id[i+1:]
                if len(new_id) == 43:  # One less than standard 44
                    results.append(new_id)
        
        for i in range(0, len(base_id), len(base_id) // count):
            if base_id[i].isalnum():
                new_id = base_id[:i] + base_id[i] + base_id[i:]
                if len(new_id) == 45:  # One more than standard 44
                    results.append(new_id)
        
        return results[:count]
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of document content for uniqueness detection using text-only extraction"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            title_elem = soup.find('title')
            title = title_elem.get_text().strip() if title_elem else ""
            
            for script in soup(["script", "style", "noscript"]):
                script.decompose()
            
            main_content = ""
            
            content_containers = [
                soup.find('div', {'class': lambda x: x and 'kix-page' in str(x)}),
                soup.find('div', {'id': 'contents'}),
                soup.find('div', {'class': lambda x: x and 'doc-content' in str(x)}),
                soup.find('body')
            ]
            
            for container in content_containers:
                if container:
                    main_content = container.get_text(separator=' ', strip=True)
                    break
            
            if not main_content:
                main_content = soup.get_text(separator=' ', strip=True)
            
            text_content = f"{title}\n{main_content}"
            
            normalized = re.sub(r'\s+', ' ', text_content.strip())
            
            normalized = re.sub(r'Loading\.\.\.', '', normalized)
            normalized = re.sub(r'Sign in.*?Google', '', normalized)
            normalized = re.sub(r'Last edit was.*?ago', '', normalized)
            normalized = re.sub(r'\d{1,2}:\d{2}:\d{2}\s*(AM|PM)', '', normalized)  # Remove timestamps
            normalized = re.sub(r'Page \d+ of \d+', '', normalized)  # Remove page numbers
            
            normalized = re.sub(r'\s+', ' ', normalized).strip()
            
            return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
            
        except ImportError:
            return self._calculate_content_hash_fallback(content)
        except Exception as e:
            logger.warning(f"Error in content hashing: {e}, falling back to regex approach")
            return self._calculate_content_hash_fallback(content)
    
    def _calculate_content_hash_fallback(self, content: str) -> str:
        """Fallback content hashing using comprehensive regex normalization"""
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else ""
        
        normalized = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        normalized = re.sub(r'<style[^>]*>.*?</style>', '', normalized, flags=re.DOTALL | re.IGNORECASE)
        normalized = re.sub(r'<noscript[^>]*>.*?</noscript>', '', normalized, flags=re.DOTALL | re.IGNORECASE)
        
        text_content = re.sub(r'<[^>]+>', '', normalized)
        
        full_text = f"{title}\n{text_content}"
        
        normalized = re.sub(r'\s+', ' ', full_text.strip())
        
        normalized = re.sub(r'var DOCS_timing.*?;', '', normalized)
        normalized = re.sub(r'nonce="[^"]*"', '', normalized)
        normalized = re.sub(r'sid=[^&"]*', '', normalized)
        normalized = re.sub(r'Loading\.\.\.', '', normalized)
        normalized = re.sub(r'Sign in.*?Google', '', normalized)
        normalized = re.sub(r'Last edit was.*?ago', '', normalized)
        normalized = re.sub(r'\d{1,2}:\d{2}:\d{2}\s*(AM|PM)', '', normalized)
        normalized = re.sub(r'Page \d+ of \d+', '', normalized)
        
        normalized = re.sub(r'DOCS_timing\[.*?\].*?;', '', normalized)
        normalized = re.sub(r'new Date\(\)\.getTime\(\)', '', normalized)
        normalized = re.sub(r'_reqid=[^&"]*', '', normalized)
        normalized = re.sub(r'authuser=[^&"]*', '', normalized)
        
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    async def test_document_access(self, doc_id: str) -> DocumentInfo:
        """Test if a document ID is accessible and extract basic info"""
        doc_info = DocumentInfo(id=doc_id, url="", accessible=False)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for url_template in self.base_urls:
                url = url_template.format(doc_id)
                doc_info.url = url
                
                try:
                    response = await client.get(url, follow_redirects=True)
                    
                    if response.status_code == 200:
                        doc_info.accessible = True
                        
                        content = response.text
                        
                        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                        if title_match:
                            doc_info.title = title_match.group(1).strip()
                        
                        text_content = re.sub(r'<[^>]+>', '', content)
                        text_content = re.sub(r'\s+', ' ', text_content).strip()
                        doc_info.content_preview = text_content[:200] + "..." if len(text_content) > 200 else text_content
                        
                        doc_info.content_hash = self._calculate_content_hash(content)
                        
                        logger.info(f"Successfully accessed document {doc_id} via {url}")
                        break
                        
                    elif response.status_code == 403:
                        doc_info.error = "Access forbidden - document may be private"
                    elif response.status_code == 404:
                        doc_info.error = "Document not found"
                    else:
                        doc_info.error = f"HTTP {response.status_code}"
                        
                except Exception as e:
                    doc_info.error = f"Request failed: {str(e)}"
                    logger.error(f"Error accessing {url}: {e}")
        
        return doc_info
    
    async def batch_test_documents(self, doc_ids: List[str], delay: float = 1.0) -> List[DocumentInfo]:
        """Test multiple document IDs with rate limiting and uniqueness detection"""
        results = []
        seen_hashes = set()
        unique_count = 0
        
        for i, doc_id in enumerate(doc_ids):
            logger.info(f"Testing document {i+1}/{len(doc_ids)}: {doc_id}")
            
            doc_info = await self.test_document_access(doc_id)
            results.append(doc_info)
            
            if doc_info.accessible and doc_info.content_hash:
                if doc_info.content_hash not in seen_hashes:
                    seen_hashes.add(doc_info.content_hash)
                    unique_count += 1
                    logger.info(f"Found unique document: {doc_id} (hash: {doc_info.content_hash[:8]}...)")
                else:
                    logger.info(f"Found duplicate document: {doc_id} (same content as previous)")
            
            if i < len(doc_ids) - 1:  # Don't delay after the last request
                await asyncio.sleep(delay)
        
        logger.info(f"Batch test complete: {len(results)} tested, {unique_count} unique documents found")
        return results
    
    def analyze_uniqueness(self, results: List[DocumentInfo]) -> Dict:
        """Analyze the uniqueness of discovered documents"""
        accessible_docs = [r for r in results if r.accessible]
        if not accessible_docs:
            return {
                "total_tested": len(results),
                "accessible_count": 0,
                "unique_count": 0,
                "duplicate_count": 0,
                "uniqueness_rate": 0.0,
                "unique_hashes": []
            }
        
        hash_counts = {}
        for doc in accessible_docs:
            if doc.content_hash:
                hash_counts[doc.content_hash] = hash_counts.get(doc.content_hash, 0) + 1
        
        unique_count = len(hash_counts)
        duplicate_count = len(accessible_docs) - unique_count
        
        return {
            "total_tested": len(results),
            "accessible_count": len(accessible_docs),
            "unique_count": unique_count,
            "duplicate_count": duplicate_count,
            "uniqueness_rate": unique_count / len(accessible_docs) if accessible_docs else 0.0,
            "unique_hashes": list(hash_counts.keys())
        }

async def main():
    analyzer = GoogleDocsAnalyzer()
    
    print("=== Document ID Structure Analysis ===")
    for i, doc_id in enumerate(analyzer.known_ids, 1):
        print(f"\nDocument {i}: {doc_id}")
        analysis = analyzer.analyze_id_structure(doc_id)
        print(f"Length: {analysis['length']}")
        print(f"Character distribution: {analysis['character_counts']}")
        print(f"Patterns: {analysis['pattern_analysis']}")
    
    print("\n=== Testing Known Documents ===")
    known_results = await analyzer.batch_test_documents(analyzer.known_ids)
    
    for result in known_results:
        print(f"\nDocument ID: {result.id}")
        print(f"Accessible: {result.accessible}")
        print(f"Title: {result.title}")
        print(f"Preview: {result.content_preview}")
        if result.error:
            print(f"Error: {result.error}")
    
    print("\n=== Testing Incremented IDs ===")
    base_id = analyzer.known_ids[0]
    incremented_ids = analyzer.generate_incremented_ids(base_id, ["last_char", "last_digit"])[:10]  # Limit to 10 for testing
    
    print(f"Generated {len(incremented_ids)} incremented IDs from base: {base_id}")
    for inc_id in incremented_ids[:5]:  # Show first 5
        print(f"  {inc_id}")
    
    incremented_results = await analyzer.batch_test_documents(incremented_ids[:5], delay=2.0)
    
    successful_finds = [r for r in incremented_results if r.accessible]
    print(f"\nFound {len(successful_finds)} accessible documents from incremented IDs!")
    
    for result in successful_finds:
        print(f"\n🎉 FOUND: {result.id}")
        print(f"Title: {result.title}")
        print(f"Preview: {result.content_preview}")

if __name__ == "__main__":
    asyncio.run(main())
