#!/usr/bin/env python3
"""
This module defines the ZimContentExtractor class, responsible for extracting
content from ZIM files.
"""
import logging
from html.parser import HTMLParser
import uuid # For mock object generation

# Set up basic logging
logger = logging.getLogger(__name__)

# Attempt to import libzim
LIBZIM_AVAILABLE = False
zim = None

try:
    from libzim import zim as zim_from_libzim
    zim = zim_from_libzim
    LIBZIM_AVAILABLE = True
    logger.info("Successfully imported 'zim' from 'libzim'.")
except ImportError:
    logger.warning(
        "Failed to import 'zim' from 'libzim'. Attempting to import 'zim' directly."
    )
    try:
        import zim as zim_direct
        zim = zim_direct # type: ignore
        LIBZIM_AVAILABLE = True
        logger.info("Successfully imported 'zim' directly.")
    except ImportError:
        logger.warning(
            "Failed to import 'zim' directly. libzim library not found. "
            "Please ensure it is installed. Functionality will be limited."
        )
        # zim remains None

# Define a simple HTML stripper
class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

class ZimContentExtractor:
    """
    Extracts textual content from articles within a ZIM file.
    """

    def __init__(self, zim_file_path: str):
        """
        Initializes the ZimContentExtractor.

        Args:
            zim_file_path: The path to the ZIM file.
        """
        self.zim_file_path = zim_file_path
        logger.info("ZimContentExtractor initialized with file: %s", self.zim_file_path)
        if not LIBZIM_AVAILABLE:
            logger.warning(
                "libzim module was not successfully imported during setup. "
                "ZIM file processing will not be possible."
            )

    def _strip_html(self, html_content: str) -> str:
        """Strips HTML tags from a string."""
        stripper = HTMLStripper()
        stripper.feed(html_content)
        return stripper.get_data()

    def extract_all_articles_text(self) -> list[str]:
        """
        Extracts plain text content from all articles in the ZIM file.

        Returns:
            A list of strings, where each string is the plain text content of an article.
        """
        if not LIBZIM_AVAILABLE or zim is None: # Added zim is None check for clarity
            logger.error(
                "Cannot extract articles: libzim module is not available or not imported correctly."
            )
            return []

        logger.info("Attempting to extract articles from: %s", self.zim_file_path)
        texts: list[str] = []

        try:
            # Using zim.File, assuming this is the correct class from the imported module
            zimfile = zim.File(self.zim_file_path)
        except FileNotFoundError:
            logger.error("ZIM file not found at path: %s", self.zim_file_path)
            return []
        except AttributeError: # Handles if zim is None and zim.File is accessed
             logger.error("libzim is not available or zim.File is not callable (AttributeError).")
             return []
        except Exception as e: # Catching other generic libzim errors for opening
            logger.error(
                "Failed to open ZIM file '%s'. Error: %s: %s",
                self.zim_file_path, type(e).__name__, e
            )
            return []

        logger.info("Successfully opened ZIM file: %s (UUID: %s, Articles: %d)",
                    self.zim_file_path, zimfile.uuid, zimfile.article_count)

        article_count = 0
        processed_article_uuids = set()

        try:
            for uuid_val_bytes in zimfile.uuid_iter():
                # Ensure we don't process the same UUID twice if uuid_iter somehow yields duplicates
                if uuid_val_bytes in processed_article_uuids:
                    logger.debug("UUID %s already processed, skipping.", uuid_val_bytes.hex())
                    continue
                
                try:
                    entry = zimfile.get_entry_by_uuid(uuid_val_bytes)
                except Exception as e: 
                    try:
                        uuid_hex = uuid_val_bytes.hex()
                    except:
                        uuid_hex = str(uuid_val_bytes) 
                    logger.error("Error getting entry by UUID %s: %s. Skipping.", uuid_hex, e)
                    continue
                
                processed_article_uuids.add(uuid_val_bytes) # Add after successful retrieval

                if entry.is_redirect():
                    logger.debug("Skipping redirect entry: %s (UUID: %s)", entry.title, entry.uuid.hex())
                    continue

                if not entry.is_article():
                    logger.debug("Skipping non-article entry: %s (Namespace: %s, UUID: %s)",
                                 entry.title, entry.namespace, entry.uuid.hex())
                    continue
                
                article_count += 1
                try:
                    item = entry.get_item()
                    raw_html_bytes = item.get_data()
                    if not raw_html_bytes:
                        logger.warning("Article '%s' (UUID: %s) has no content. Skipping.",
                                       entry.title, entry.uuid.hex())
                        continue

                    try:
                        html_content = raw_html_bytes.decode('utf-8', errors='ignore')
                    except UnicodeDecodeError as ude:
                        logger.warning(
                            "UnicodeDecodeError for article '%s' (Path: %s, UUID: %s). Error: %s. Skipping.",
                            entry.title, entry.path, entry.uuid.hex(), ude
                        )
                        continue
                    
                    plain_text = self._strip_html(html_content)
                    texts.append(plain_text)
                    logger.debug("Successfully extracted text from article: %s (UUID: %s, Length: %d)",
                                 entry.title, entry.uuid.hex(), len(plain_text))

                except Exception as e: 
                    logger.error(
                        "Error processing article '%s' (Path: %s, UUID: %s). Error: %s: %s. Skipping article.",
                        entry.title, entry.path, entry.uuid.hex(), type(e).__name__, e
                    )
                    continue

        except Exception as e: 
            logger.error(
                "An error occurred during ZIM file article iteration for '%s'. Error: %s: %s",
                self.zim_file_path, type(e).__name__, e
            )
        finally:
            # zim.File objects in libzim do not typically require explicit close()
            # They are not context managers. Garbage collection handles closure.
            pass

        logger.info("Iterated %d UUIDs. Processed %d as articles. Extracted text from %d articles in %s.",
                    len(processed_article_uuids), article_count, len(texts), self.zim_file_path)
        return texts

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger.info("Starting ZIM Content Extractor example (main execution).")

    # --- Mocking libzim for local testing without the actual library ---
    if not LIBZIM_AVAILABLE or zim is None: # Check zim as well
        logger.warning("libzim is not available or not imported. Running with mock objects for demonstration.")

        class MockItem:
            def __init__(self, content_bytes):
                self._content_bytes = content_bytes
            def get_data(self):
                return self._content_bytes

        class MockEntry:
            def __init__(self, entry_uuid_obj, title, content_bytes, is_article=True, is_redirect=False):
                self.uuid = entry_uuid_obj # This is a uuid.UUID object
                self.title = title
                self._is_article = is_article
                self._is_redirect = is_redirect
                self.path = f"A/{title.replace(' ', '_')}.html"
                self._content_bytes = content_bytes

            def is_redirect(self):
                return self._is_redirect

            def is_article(self):
                return self._is_article
            
            @property
            def namespace(self):
                return 'A' if self._is_article else 'X'

            def get_item(self):
                return MockItem(self._content_bytes)

        class MockZimFile:
            def __init__(self, path):
                self.path = path
                self.uuid = uuid.uuid4() # Main ZIM file UUID
                self._entries_by_uuid_bytes = {} 

                # Create mock entries
                entry1_uuid = uuid.uuid4()
                self._entries_by_uuid_bytes[entry1_uuid.bytes] = MockEntry(
                    entry1_uuid, "Test Article 1", b"<html><body><h1>Article 1</h1><p>Content 1.</p></body></html>"
                )
                
                entry2_uuid = uuid.uuid4()
                self._entries_by_uuid_bytes[entry2_uuid.bytes] = MockEntry(
                    entry2_uuid, "Redirect Article", b"", is_redirect=True
                )

                entry3_uuid = uuid.uuid4()
                self._entries_by_uuid_bytes[entry3_uuid.bytes] = MockEntry(
                    entry3_uuid, "Test Article 2", b"<html><body><h2>Article 2</h2><p>Content 2 with entities &amp;.</p></body></html>"
                )
                
                entry4_uuid = uuid.uuid4()
                self._entries_by_uuid_bytes[entry4_uuid.bytes] = MockEntry(
                    entry4_uuid, "Non Article", b"metadata or something", is_article=False
                )
                
                entry5_uuid = uuid.uuid4() 
                self._entries_by_uuid_bytes[entry5_uuid.bytes] = MockEntry(
                    entry5_uuid, "Empty Article", b""
                )

                self.article_count = sum(1 for e in self._entries_by_uuid_bytes.values() if e.is_article() and not e.is_redirect())

            def uuid_iter(self):
                return iter(self._entries_by_uuid_bytes.keys())

            def get_entry_by_uuid(self, uuid_bytes_val):
                if uuid_bytes_val in self._entries_by_uuid_bytes:
                    return self._entries_by_uuid_bytes[uuid_bytes_val]
                # Real libzim raises KeyError or similar; mock should too.
                raise KeyError(f"Mock entry with UUID bytes {uuid_bytes_val.hex()} not found")


        # Replace the real zim.File with the mock if libzim is not available
        # This creates a mock 'zim' module object to hold the MockZimFile class
        class MockZimModule:
            File = MockZimFile
            # Add any other zim attributes/classes if they were used directly and zim is None
        
        zim_original_module_ref = zim # Store original (could be None or the imported module)
        zim = MockZimModule() # zim is now the mock module, its .File is MockZimFile
        logger.info("Patched 'zim' module and 'zim.File' with mock objects for testing.")
    # --- End of Mocking Block ---

    zim_file_to_test = "test.zim" 
    
    logger.info(f"Attempting to use ZIM file: {zim_file_to_test}")
    # This check relies on the global LIBZIM_AVAILABLE flag, which is accurate.
    if not LIBZIM_AVAILABLE and zim_file_to_test == "test.zim": 
        logger.info("Using MOCK ZimFile for 'test.zim' as libzim is not available (or not imported).")

    extractor = ZimContentExtractor(zim_file_to_test)
    articles_text = extractor.extract_all_articles_text()

    if articles_text:
        logger.info("Successfully extracted %d articles (mock data likely).", len(articles_text))
        for i, text_content in enumerate(articles_text):
            logger.info("Mock Article %d (first 100 chars): %s", i + 1, text_content[:100].replace("\n", " "))
    else:
        logger.info("No articles extracted. Check logs for details (mock data or actual run).")

    # Restore original zim module if it was monkeypatched by the mock setup
    if 'zim_original_module_ref' in locals() and zim != zim_original_module_ref:
        zim = zim_original_module_ref 
        logger.info("Restored original 'zim' module object.")
    
    logger.info("ZIM Content Extractor example finished.")
