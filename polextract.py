import os
import PyPDF2

def extract_proof_of_loss_page(input_folder, output_folder, search_text="Proof Of Loss"):
    """
    Extract the page containing `search_text` from each PDF in `input_folder` 
    and save it as a separate PDF in `output_folder`.
    """
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)

            try:
                # Open the PDF file with PyPDF2
                with open(pdf_path, "rb") as f:
                    pdf_reader = PyPDF2.PdfReader(f)

                    # Loop through each page in the PDF
                    for page_index in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_index]
                        # Extract text from the page
                        page_text = page.extract_text() or ""

                        # Check if the target text is found (case-insensitive)
                        if search_text.lower() in page_text.lower():
                            # Create a PdfWriter and add the matching page
                            pdf_writer = PyPDF2.PdfWriter()
                            pdf_writer.add_page(page)

                            # Construct output PDF filename
                            base_name = os.path.splitext(filename)[0]
                            output_filename = f"{base_name}_ProofOfLoss.pdf"
                            output_path = os.path.join(output_folder, output_filename)

                            # Write out the single-page PDF
                            with open(output_path, "wb") as out_f:
                                pdf_writer.write(out_f)

                            print(f"Extracted '{search_text}' page from '{filename}' to '{output_filename}'")
                            break  # Stop after extracting the first match

            except Exception as e:
                print(f"Error processing {filename}: {e}")


if __name__ == "__main__":
    # Example usage:
    input_folder_path = r"./pdf_files"
    output_folder_path = r"./extracted_pdfs"

    extract_proof_of_loss_page(input_folder_path, output_folder_path)
