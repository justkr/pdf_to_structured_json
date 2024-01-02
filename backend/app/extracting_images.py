from pdfminer.high_level import extract_pages
from pdfminer.layout import LTImage, LTFigure
from io import BytesIO
from PIL import Image

def extract_images_from_pdf(pdf_path):
    images = []

    # Extract pages from the PDF
    for page_layout in extract_pages(pdf_path):
        # Iterate through the layout objects on the page
        for element in page_layout:
            if isinstance(element, LTFigure):
                # If the element is a figure, iterate through its elements
                for figure_element in element:
                    if isinstance(figure_element, LTImage):
                        try:
                            # If the element is an image, extract it
                            image_data = figure_element.stream.get_rawdata()
                            image_stream = BytesIO(image_data)
                            image = Image.open(image_stream)

                            # Convert the image to RGB mode
                            if image.mode == 'CMYK':
                                image = image.convert('RGB')

                            # Invert the image if necessary
                            #image = Image.eval(image, lambda x: 255 - x)

                            images.append(image)
                        except Exception as e:
                            print(f"Error processing image: {e}")

    return images

# Example usage:
#pdf_name = 'Insurance_Handbook.pdf'
pdf_name = 'Factsheet Leben Risiko.pdf'
extracted_images = extract_images_from_pdf('data/input/' + pdf_name)

# Save the extracted images to files
for i, image in enumerate(extracted_images):
    # Save the image as PNG after converting to RGB mode and inverting
    image = image.convert('RGB')
    image.save(f'./data/images/{pdf_name.split('.pdf')[0]}_output_image_{i + 1}.png')