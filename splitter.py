import pymupdf
from PIL import Image
import io
import os
from typing import List

class PDFSplitter:
    def __init__(self):
        """
        Initialize the PDFSplitter class.
        This class is responsible for splitting PDF files into grouped PNG images.
        """
        pass

    def group_pdf_pages(self, filepath: str, pages_per_group: int = 5) -> List[List]:
        """
        Groups PDF pages into chunks of specified size.
        
        Args:
            filepath: Path to the PDF file
            pages_per_group: Number of pages per group (default: 5)
        
        Returns:
            List of groups, where each group contains pixmaps
        """
        doc = pymupdf.open(filepath)
        groupings = [[]]
        
        for page in doc:
            pix = page.get_pixmap()
            if len(groupings[-1]) < pages_per_group:
                groupings[-1].append(pix)
            else:
                groupings.append([pix])
        
        doc.close()
        return groupings

    def combine_group_to_png(self, group: List, group_number: int, output_dir: str) -> str:
        """
        Combines a group of pixmaps into a single vertical PNG image.
        
        Args:
            group: List of pixmaps to combine
            group_number: Group number for filename
            output_dir: Output directory (default: current directory)
        
        Returns:
            Output filename
        """
        if not group:
            return None
            
        # Convert pixmaps to PIL Images
        images = []
        for pix in group:
            img_data = pix.tobytes("png")
            pil_img = Image.open(io.BytesIO(img_data))
            images.append(pil_img)
        
        # Calculate total height and max width
        total_height = sum(img.height for img in images)
        max_width = max(img.width for img in images)
        
        # Create combined image
        combined_img = Image.new('RGB', (max_width, total_height), 'white')
        
        # Paste images vertically
        y_offset = 0
        for img in images:
            combined_img.paste(img, (0, y_offset))
            y_offset += img.height
        
        # Save combined image
        output_filename = f"{output_dir}/group_{group_number}.png"
        combined_img.save(output_filename)
        return output_filename

    def split_pdf(self, filepath: str, pages_per_group: int = 5, output_dir: str = "processed"):
        """
        Main function to split PDF into grouped PNG images.
        
        Args:
            filepath: Path to the PDF file
            pages_per_group: Number of pages per group (default: 5)
            output_dir: Output directory (default: current directory)
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Group the PDF pages
        groupings = self.group_pdf_pages(filepath, pages_per_group)
        
        # Combine each group into a PNG
        created_files = []
        for i, group in enumerate(groupings):
            output_filename = self.combine_group_to_png(group, i + 1, output_dir)
            if output_filename:
                created_files.append(output_filename)
                print(f"Saved {output_filename} with {len(group)} pages")
        
        print(f"Created {len(created_files)} group images")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Split PDF into grouped PNG images.")
    parser.add_argument("input_pdf", help="Path to input PDF file")
    args = parser.parse_args()

    splitter = PDFSplitter()
    splitter.split_pdf(args.input_pdf, pages_per_group=5, output_dir="processed")

