
import os
import argparse
from redaction import PDFRedactor
from splitter import PDFSplitter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help="Path to input PDF file")
    parser.add_argument("--output-dir", default="processed", help="Output directory for PNG files (optional)")
    args = parser.parse_args()

    redactor = PDFRedactor()
    splitter = PDFSplitter()

    if not os.path.exists(args.filename):
        print(f"Error: Input file does not exist: {args.input_pdf}")
        return
    
    try:
        outpath = redactor.redact_pdf(args.filename)
        splitter.split_pdf(outpath, output_dir=args.output_dir)

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()