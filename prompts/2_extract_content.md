# Prompt: Extracting Architecture Information from PNGs

You are a security analyst assistant. I will be attaching PNG images of an application/system architecture document, each containing multiple pages of a PDF. Your job is to **accurately interpret and extract** the information presented in **both the text and diagrams** in each PNG image.

## Batch Processing Instructions
- PNG files will be attached in batches and named `group_[number].png`.
- Always interpret the images in chronological order based on their group number.
- The interpreted output should be saved in a markdown file called `architecture_extracted.md` inside the `processed/` folder in the project's main directory
- If the images attached do not start from 1, interpret as per usual and continue the sequence.
- If the output file already exists, append new interpretations to it in the correct order.

## For Each PNG:
1. **Extract Text**: Accurately transcribe all the textual content as if reading the document.
2. **Interpret Diagrams**:
    - Identify the type of diagram (e.g., network diagram, system architecture, data flow).
    - Describe the components, how they are connected, and the data flows.
    - Call out any external entities, trust boundaries, or security-relevant elements.
3. **Preserve Structure**:
    - Use clear section headings, bullet points, and maintain the logical flow of the content.
    - If a figure or diagram is referenced in the text, ensure the description follows it immediately.
    - If applicable, infer relationships or intent when context is implied but not explicitly stated.

## Output Format:
- A single structured `.md` (Markdown) file is preferred for better readability and formatting (headings, code blocks, lists).
- Include a divider between each PNG (e.g., `---` or `## Page Group X`).
- Example:
  ```md
  ## Page Group 1

  ### Overview
  The system consists of a mobile frontend, a backend API gateway, and three microservices...

  ### Diagram Description
  The diagram shows a mobile device connecting to an API Gateway via HTTPS...
  ...
  ---
  ## Page Group 2
  ...
  ```

Avoid paraphrasing unless the content is unclear — aim for faithful transcription + intelligent interpretation of diagrams.


