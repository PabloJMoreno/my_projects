import crewai
import os
from datetime import datetime, timedelta
import google.generativeai as palm
from transformers import pipeline
import io  # For handling byte streams
import re  # Import the regular expression module

# Initialize CrewAI
crew = crewai.Crew()

# Set your Gemini API key (replace with your actual key)
palm.configure(api_key="YOUR_GEMINI_API_KEY")  # <--- IMPORTANT: Replace with your API Key

# Initialize GOT-OCR 2.0 pipeline
ocr_pipeline = pipeline("image-to-text", model="stepfun-ai/GOT-OCR-2.0-hf")

# Agent 1: PDF/Image Extractor (using GOT-OCR 2.0)
@crew.agent(name="document_extractor", tools=[])
def document_extractor(file_path: str) -> dict:
    """Extracts key details from a PDF or image using GOT-OCR 2.0."""
    try:
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif')):  # Image file
            with open(file_path, "rb") as image_file:
                extracted_text = ocr_pipeline(image_file)["generated_text"]
        elif file_path.lower().endswith('.pdf'):  # PDF file
            import fitz  # PyMuPDF for PDF handling
            doc = fitz.open(file_path)
            extracted_text = ""
            for page in doc:
                pix = page.get_pixmap()
                img_bytes = pix.tobytes()  # Convert to bytes
                extracted_text += ocr_pipeline(img_bytes)["generated_text"] + "\n"
            doc.close()
        else:
            return {"error": "Unsupported file type. Please provide a PDF or image file."}

        # ... (Your regular expressions - MUST BE CUSTOMIZED - These are EXAMPLES) ...
        order_number_match = re.search(r"Order Number:\s*(\d+)", extracted_text)
        product_name_match = re.search(r"Product:\s*(.+)", extracted_text)
        quantity_match = re.search(r"Quantity:\s*(\d+)", extracted_text)
        origin_country_match = re.search(r"Origin Country:\s*(.+)", extracted_text)
        destination_country_match = re.search(r"Destination Country:\s*(.+)", extracted_text)
        container_id_match = re.search(r"Container ID:\s*(.+)", extracted_text)
        other_goods_match = re.search(r"Other Goods:\s*(.+)", extracted_text)
        shipment_date_match = re.search(r"Shipment Date:\s*(.+)", extracted_text)


        extracted_data = {
            "order_number": order_number_match.group(1) if order_number_match else None,
            "product_name": product_name_match.group(1) if product_name_match else None,
            "quantity": int(quantity_match.group(1)) if quantity_match else None,
            "origin_country": origin_country_match.group(1) if origin_country_match else None,
            "destination_country": destination_country_match.group(1) if destination_country_match else None,
            "container_id": container_id_match.group(1) if container_id_match else None,
            "other_goods": other_goods_match.group(1) if other_goods_match else None,
            "shipment_date": shipment_date_match.group(1) if shipment_date_match else None,
        }

        return extracted_data

    except Exception as e:
        return {"error": f"Error processing document: {e}"}


# Agent 2: Shipment Aggregator
@crew.agent(name="shipment_aggregator", tools=[])
def shipment_aggregator(file_folder: str) -> dict:
    """Aggregates shipment details from multiple PDFs/Images in a folder."""
    all_shipments = {}
    for filename in os.listdir(file_folder):
        if filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif')):
            file_path = os.path.join(file_folder, filename)
            extracted_data = document_extractor(file_path)

            if "error" in extracted_data:
                print(extracted_data["error"])
                continue

            order_number = extracted_data.get("order_number")
            if order_number:
                if order_number not in all_shipments:
                    all_shipments[order_number] = []
                all_shipments[order_number].append(extracted_data)

    return all_shipments


# Agent 3: Shipment Validator
@crew.agent(name="shipment_validator", tools=[])
def shipment_validator(original_shipment_file: str, aggregated_shipments: dict) -> dict:
    """Validates if all goods from the original shipment are present in the aggregated shipments."""

    original_data = document_extractor(original_shipment_file)  # Use document_extractor for original file
    if "error" in original_data:
        return {"error": original_data["error"]} # Return the error from document_extractor


    missing_goods = {}
    for order_number, shipments in aggregated_shipments.items():
        missing_goods[order_number] = []
        original_quantities = {}

        for key, value in original_data.items():
            if key == "product_name":
                original_product = value
            if key == "quantity":
                original_quantity = value
                original_quantities[original_product] = original_quantity

        for product, quantity in original_quantities.items():
            total_shipped_quantity = 0
            for shipment in shipments:
                if shipment.get("product_name") == product:
                    total_shipped_quantity += shipment.get("quantity", 0)

            if total_shipped_quantity < quantity:
                missing_goods[order_number].append({
                    "product": product,
                    "original_quantity": quantity,
                    "shipped_quantity": total_shipped_quantity,
                    "difference": quantity - total_shipped_quantity
                })

    missing_goods = {k: v for k, v in missing_goods.items() if v}
    return {"original_shipment": original_data, "missing_goods": missing_goods}


# Agent 4: Shipment Report Generator (using Gemini)
@crew.agent(name="shipment_report_generator", tools=[])
def shipment_report_generator(original_shipment_data: dict, aggregated_shipments: dict, missing_goods: dict) -> str:

    prompt = f"""
    ## Shipment Summary Report

    ### Original Shipment Details
    {original_shipment_data}

    ### Shipment Breakdown
    {aggregated_shipments}

    ### Missing Goods
    {missing_goods}

    ### Instructions:
    1. Create a comprehensive summary of the shipment, including all details.
    2. Calculate estimated arrival times (ETAs) for each shipment.  Assume a default transit time of 7 days if no other information is available. If a shipment date is available, use it to calculate the ETA. Format the date as YYYY-MM-DD.
    3. Provide clear recommendations for improving shipping efficiency and addressing any missing goods.
    4. Include a "Human-in-the-Loop" section for any manual actions or instructions.
    5. Format the report clearly and concisely. Use Markdown formatting for headings, lists, and other elements to improve readability.
    """

    try:
        response = palm.generate_text(
            model="models/gemini-pro",
            prompt=prompt,
            temperature=0.2,
            max_output_tokens=2048
        )
        report = response.result

        return report

    except Exception as e:
        return f"Error generating report with Gemini: {e}"


# Example usage:
original_file = "path/to/your/original/shipment.pdf"  # <--- IMPORTANT: Replace with path (PDF or image)
file_directory = "path/to/your/file/folder"  # <--- IMPORTANT: Replace with your folder path (PDFs or images)

aggregated_shipments = shipment_aggregator(file_directory)

if "error" in aggregated_shipments:
    print(aggregated_shipments["error"])
else:
    validation_result = shipment_validator(original_file, aggregated_shipments)

    if "error" in validation_result:
        print(validation_result["error"])
    else:
        original_shipment_data = validation_result["original_shipment"]
        missing_goods_data = validation_result["missing_goods"]

        report = shipment_report_generator(original_shipment_data, aggregated_shipments, missing_goods_data)
        print(report)