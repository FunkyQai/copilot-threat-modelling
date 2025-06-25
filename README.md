# Threat Modelling Automation with GitHub Copilot

## Objective
Perform comprehensive threat modelling on system/application architecture or implementation documents using GitHub Copilot.

## Rationale
Architectural documents come in many formats (docx, pptx, pdf, etc.), often containing diagrams and pictorial information that traditional OCR tools may not fully interpret. Leveraging LLMs' vision capabilities enables deeper understanding of both text and images, allowing for more thorough and context-rich threat modelling.

## Approach
1. **Sanitize the Document**
   - Redact sensitive information from the original PDF to protect company data before processing with LLMs.
2. **Split the Redacted PDF**
   - Convert the redacted PDF into PNG images, each containing approximately 3 pages (configurable). Images are stored in the `processed/` folder.
3. **Extract Content Using Copilot**
   - Sequentially interpret the PNG images with Copilot, extracting information and compiling it into a single markdown file (`architecture_extracted.md`). This step ensures all relevant content, including diagrams, is captured for analysis.
4. **Perform Threat Modelling**
   - Use the extracted markdown file as the context for Copilot to conduct threat modelling, following the provided guidelines and prompts.
5. **Generate the Threat Modelling Report**
   - Copilot produces a well-structured markdown report (`threat_model_report.md`) based on the extracted architecture and process information.

## How to Use
All instructions are provided in the `prompts/` folder. Each step has a dedicated markdown file:

1. **Redact and Split PDF**
   - Follow `1_process_pdf.md`. The agent will prompt for the document path and optional parameters, then run scripts to redact and split the PDF. Output images are saved in `processed/`.
2. **Extract Content from Images**
   - Due to platform limitations, manually drag and drop up to 4 image files at a time into the Copilot chat. Attach `2_extract_content.md` and instruct the agent to extract content. Repeat until all images are processed. The result is `architecture_extracted.md` in `processed/`.
3. **Threat Modelling**
   - Attach `architecture_extracted.md` and `3_threat_model_report_prompt.md` to the chat. Ask Copilot to perform threat modelling. The agent will generate `threat_model_report.md` following the standards in `threat_modelling_guideline.md`.
4. **Export the Report**
   - Optionally, convert the markdown report to PDF for presentation using an online tool.

## Strengths
- Enables comprehensive interpretation of both text and images in architectural documents.
- Consolidates all extracted information into a single file, maximizing LLM context and analysis quality.
- Provides granular control over each processing step, with intermediate files for transparency and reusability.
- Intermediate files can be referenced for Q&A or regenerating the threat modelling report.

## Limitations
- The process takes approximately 6 minutes and requires several manual actions (e.g., dragging/dropping images).
- Users should periodically start a new chat session to avoid memory issues during extended operations.

---
