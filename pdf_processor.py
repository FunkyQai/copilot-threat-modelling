
import os
import argparse
from redaction import PDFRedactor
from splitter import PDFSplitter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", type=str, help="Path to input PDF file")
    parser.add_argument("--pages-per-group", type=int, default=4, help="The number of pdf pages in each png file (default: 4) (optional)")
    parser.add_argument("--output-dir", type=str, default="processed", help="Output directory for PNG files (optional)")
    args = parser.parse_args()

    redactor = PDFRedactor()
    splitter = PDFSplitter()

    if not os.path.exists(args.filepath):
        print(f"Error: Input file does not exist: {args.input_pdf}")
        return
    
    try:
        outpath = redactor.redact_pdf(args.filepath)
        splitter.split_pdf(outpath, pages_per_group=args.pages_per_group, output_dir=args.output_dir)

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()