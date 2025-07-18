import spacy
import re
import os
import fitz  # PyMuPDF
from typing import List, Tuple
import argparse

class PDFRedactor:
    def __init__(self):
        # Load transformer model for better NER performance
        try:
            self.nlp = spacy.load("en_core_web_trf")
        except OSError:
            print("Error: spaCy transformer model 'en_core_web_trf' not found.")
            print("Please install it with: python -m spacy download en_core_web_trf")
            raise
        
        # Regex patterns for PII detection
        self.patterns = {
            'NRIC/FIN': re.compile(r'\b[FGMSTfgmst]\d{7}[A-Za-z]\b'),
            'SG_Passport': re.compile(r'\b[eE]\d{7}[A-Za-z]\b'),
            'SG_Phone': re.compile(r'\b[689]\d{3}[\s-]?\d{4}\b'),
            'INTL_PHONE': re.compile(r'\+\d{1,3}[\s-]?\d{4,}\b'),
            'EMAIL': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'IPV4': re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'),
            'IPV6': re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b|::1\b|::ffff:[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\b'),
            'CREDIT_CARD': re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
            'KRISFLYER_NUM': re.compile(r'\b\d{10}\b'),
            'FLIGHT_TICKET': re.compile(r'\b\d{3}-?\d{10,11}\b'),
            'PLANE_SEAT': re.compile(r'\b([1-9]\d?|\d{3})([A-HJ-K])\b'),
            'BOOKING_PNR': re.compile(r'\b[A-HJ-NP-Z0-9]{6}\b')
        }
    
    def find_regex_matches(self, text: str) -> List[Tuple[int, int, str]]:
        """
        Find all regex-based PII matches in text
        
        match.start() and match.end() give the start and end positions of the match
        """
        matches = []
        
        for pattern_name, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                matches.append((match.start(), match.end(), pattern_name))
        
        return matches
    
    def find_ner_matches(self, text: str) -> List[Tuple[int, int, str]]:
        """
        Find person names using NER
        
        Entity list can be found here: https://github.com/explosion/spaCy/discussions/9147
        """
        doc = self.nlp(text)
        matches = []
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                matches.append((ent.start_char, ent.end_char, "PERSON_NAME"))
            elif ent.label_ in ["GPE", "LOC", "FAC"]:
                matches.append((ent.start_char, ent.end_char, "ADDRESS"))
        
        return matches
    
    def merge_overlapping_matches(self, matches: List[Tuple[int, int, str]]) -> List[Tuple[int, int, str]]:
        """Keep only the largest match from each group of overlapping matches"""
        if not matches:
            return []
        
        # Sort by start position
        sorted_matches = sorted(matches, key=lambda x: x[0])
        result = []
        used = set()  # Track which matches we've already processed
        
        for i, match1 in enumerate(sorted_matches):
            if i in used:
                continue
                
            # Find all matches that overlap with match1
            overlapping_group = [match1]
            overlapping_indices = [i]
            
            for j, match2 in enumerate(sorted_matches):
                if j <= i or j in used:
                    continue
                    
                # Check if match1 and match2 overlap
                if (match1[0] < match2[1] and match1[1] > match2[0]):
                    overlapping_group.append(match2)
                    overlapping_indices.append(j)
            
            # Find the biggest match in this overlapping group
            biggest_match = max(overlapping_group, key=lambda x: x[1] - x[0])
            result.append(biggest_match)
            
            # Mark all overlapping matches as used
            used.update(overlapping_indices)
        
        return result
    
    def calculate_font_size(self, rect, text: str) -> int:
        """Calculate appropriate font size based on rectangle dimensions"""
        rect_width = rect.width
        rect_height = rect.height
        text_length = len(text)
        
        # Base font size on rectangle width and text length
        # Rough estimate: width per character should be about 0.7 * font_size
        max_font_by_width = int(rect_width / (text_length * 0.7))
        
        # Base font size on rectangle height (leave some padding)
        max_font_by_height = int(rect_height * 0.9)
        
        # Use the smaller of the two to ensure text fits
        font_size = min(max_font_by_width, max_font_by_height)
                
        return font_size
    
    
    def redact_pdf(self, input_path: str) -> str:
        """
        Main redaction function
        returns the output path
        """
        # Validate input file
        if not input_path.lower().endswith('.pdf'):
            raise ValueError("Input file must be a PDF")
        
        try:
            doc = fitz.open(input_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Input PDF file not found: {input_path}")
        except Exception as e:
            raise Exception(f"Failed to open PDF file: {str(e)}")
        
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text with position information
                full_text = page.get_text()
                
                # Find all PII matches
                regex_matches = self.find_regex_matches(full_text)
                ner_matches = self.find_ner_matches(full_text)
                
                # Combine and merge overlapping matches
                all_matches = regex_matches + ner_matches
                merged_matches = self.merge_overlapping_matches(all_matches)
                
                # Convert text positions to rectangles for redaction
                for start_pos, end_pos, match_type in merged_matches:
                    pii_text = full_text[start_pos:end_pos]
                    
                    # Find all occurrences of this text on the page
                    text_rects = page.search_for(pii_text)
                    
                    # Create redaction annotations
                    for rect in text_rects:
                        placeholder_text = f"[{match_type}]"
                        font_size = self.calculate_font_size(rect, placeholder_text)
                        # Add black rectangle to cover the text
                        page.add_redact_annot(rect, text=placeholder_text, fontsize=font_size)
                
                # Apply redactions
                page.apply_redactions()
            
            # Save redacted PDF
            try:
                filename = os.path.basename(input_path)
                output_path = f"processed/redacted_{filename}"
                doc.save(output_path)
                return output_path
            
            except Exception as e:
                raise Exception(f"Failed to save redacted PDF: {str(e)}")
                
        except Exception as e:
            raise Exception(f"Error during redaction process: {str(e)}")
        finally:
            doc.close()

def main():
    parser = argparse.ArgumentParser(description="Redact PII from PDF files")
    parser.add_argument("input_pdf", help="Path to input PDF file")
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not args.input_pdf or not args.input_pdf.strip():
        print("Error: Input PDF file path is required")
        return
    
    import os
    if not os.path.exists(args.input_pdf):
        print(f"Error: Input file does not exist: {args.input_pdf}")
        return
    
    try:
        redactor = PDFRedactor()
        redactor.redact_pdf(args.input_pdf)
        print("Redaction completed successfully!")
        
    except FileNotFoundError as e:
        print(f"File Error: {str(e)}")
    except ValueError as e:
        print(f"Validation Error: {str(e)}")
    except Exception as e:
        print(f"Error during redaction: {str(e)}")

if __name__ == "__main__":
    main()