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
    
    def compress_image(self, input_path, output_path, quality):
        """Compress image while maintaining reasonable quality"""
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Save with compression
            img.save(output_path, 'JPEG', quality=quality, optimize=True)

    def batch_compress(self, directory='processed', quality=50):
        """Batch compress all images in a directory"""
        if not os.path.exists(directory):
            print(f"Directory {directory} does not exist")
            return
            
        compressed_files = []
        for filename in os.listdir(directory):
            if filename.lower().endswith('.png') and not filename.startswith('compressed_'):
                input_path = os.path.join(directory, filename)
                # Change extension to .jpg for compressed files
                base_name = os.path.splitext(filename)[0]
                output_path = os.path.join(directory, f"compressed_{base_name}.jpg")
                
                try:
                    self.compress_image(input_path, output_path, quality)
                    compressed_files.append(output_path)
                    print(f"Compressed {filename} -> {os.path.basename(output_path)}")
                except Exception as e:
                    print(f"Error compressing {filename}: {e}")
        
        return compressed_files

    def split_pdf(self, filepath: str, pages_per_group: int = 3, output_dir: str = "processed"):
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
        
        # # Compress images in the output directory
        # self.batch_compress(output_dir)

        # print(f"Compressed images saved in {output_dir}")
        print(f"Processed {len(created_files)} groups into PNG images in {output_dir}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Split PDF into grouped PNG images.")
    parser.add_argument("input_pdf", help="Path to input PDF file")
    args = parser.parse_args()

    splitter = PDFSplitter()
    splitter.split_pdf(args.input_pdf, output_dir="processed")

