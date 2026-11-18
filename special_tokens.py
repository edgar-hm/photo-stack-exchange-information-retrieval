import json
import re

# Dictionary of special photography terms and its standardized form
special_terms = {
        "full frame": "full-frame",
        "medium format": "medium-format",
        "micro 4/3": "micro four thirds",
        "mft": "micro four thirds",
        "depth of field": "depth-of-field",
        "dof": "depth-of-field",
        "wide angle": "wide-angle",
        "long exposure": "long-exposure",
        "tilt shift": "tilt-shift",
        "apsc": "aps-c",
        "aps c": "aps-c",
        "optical viewfinder": "ovf",
        "electronic viewfinder": "evf",
        "auto focus": "autofocus",
        "auto-focus": "autofocus",
        "dynamic-range": "dynamic range",
        "low light": "low-light",
        "chromatic aberration": "chromatic-aberration",
        "motion-blur": "motion blur",
        "color-correction": "color correction",
        "image-stabilization": "image stabilization",
        "image-processing": "image processing",
        "shutter-speed": "shutter speed",
        "focal-length": "focal length",
        "post processing": "postprocessing",
        "post-processing": "postprocessing",
        "natural-light": "natural light",
        "macro-photography": "macrophotography",
        "astro-photography": "astrophotography",
        "landscape-photography": "landscape",
        "landscape photography": "landscape",
        "portrait-photography": "portrait",
        "portrait photography": "portrait",
        "white-balance": "white balance",
        "manual focus": "manual-focus",
        "automatic focus": "autofocus",
        "automatic-focus": "autofocus",
        "image-quality": "image quality",
        "video-quality": "video quality",
        "macro-lens": "macro lens",
        "kit-lens": "kit lens",
        "prime-lens": "prime",
        "prime lens": "prime",
        "telephoto-lens": "telephoto",
        "telephoto lens": "telephoto",
        "zoom-lens": "zoom lens",
        "standard-zoom": "standard zoom",
        "time lapse": "time-lapse",
        "bokeh-effect": "bokeh effect",
        "lens-distiortion": "lens distortion",
        "noise-reduction": "noise reduction",
        "color-grading": "color grading",
        "res": "resolution",
        "low-res": "low resolution",
        "low-resolution": "low resolution",
        "high-res": "high resolution",
        "hi-res": "high resolution",
        "high-resolution": "high resolution",
        "hq": "high quality",
        "high-quality": "high quality",
        "full-res": "full resolution",
        "full-resolution": "full resolution",
        "high-definition": "hd",
        "hi-def": "hd",
        "high-def": "hd",
        "high definition": "hd",
        "standard definition": "standard-definition",
        "hdr": "high dynamic range",
        "full high-definition": "fhd",
        "full high definition": "fhd",
        "px": "pixel",
        "pic": "picture",
        "img": "image",
        "vid": "video",
        "jpeg": "jpg",
        "tif": "tiff",
        "zoom-in": "zoom in",
        "zoom-out": "zoom out",
        "optical-zoom": "optical zoom",
        "digital-zoom": "digital zoom",
        "photograph": "photo",
        "cellphone": "phone",
        "colour": "color",
        "720i": "hd",
        "720p": "hd",
        "1280x720": "hd",
        "1280 x 720": "hd",
        "1080p": "fhd",
        "1920x1080": "fhd",
        "1920 x 1080": "fhd",
        "1440p": "qhd",
        "2560x1440": "qhd",
        "2560 x 1440": "qhd",
        "3840x2160": "4k",
        "3840 x 2160": "4k",
        "7680x4320": "8k",
        "7680 x 4320": "8k",
        "low pass filter": "low-pass filter",
        "barrel-distorsion": "barrel distorsion",
        "ef-mount": "ef mount",
        "ef": "ef mount",
        "efs-mount": "ef-s mount",        
        "ef-s": "ef-s mount",
        "efm-mount": "ef-m mount",
        "ef-m": "ef-m mount",
        "rf-mount": "rf mount",
        "rf": "rf mount",
        "f mount": "f-mount",
        "z mount": "z-mount",
        "a mount": "a-mount",
        "e mount": "e-mount",
        "fe mount": "fe-mount",
        "x mount": "x-mount",
        "l mount": "l-mount",
        "s mount": "s-mount",
        "k mount": "k-mount",
        "q mount": "q-mount",
        "645 mount": "645-mount",
        "h mount": "h-mount",
        "xcd mount": "xcd-mount",
        "zf mount": "zf-mount",
        "ze mount": "ze-mount",
        "zf": "zf-mount",
        "ze": "ze-mount"
    }

# Save special terms dictionary
output_path = "special_terms.json"
with open(output_path, "w") as json_file:
    json.dump(special_terms, json_file, indent=1)

print(f"Special photography terms dictionary saved to {output_path}")


# Dictionary for camera model names and its possible name variations
file_path = "combined_camera_models.txt" # Path to the camera models list file

def generate_camera_models_dict(file_path):
    # Dictionary to store standardized models and variations
    camera_models_dict = {}

    # Roman numeral conversion mapping
    roman_to_int = {
        "I": "1", "II": "2", "III": "3", "IV": "4",
        "V": "5", "VI": "6", "VII": "7", "VIII": "8", "IX": "9"
    }

    # Open and process the file
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if not line:  # Skip empty lines
                continue

            # Extract brand and model
            match = re.match(r"^(.*?)\s(.+)$", line)
            if match:
                brand, model = match.groups()
                standardized_model = model.lower().strip()  # Use the original model in lowercase as the key
                variations = set()

                # Add the official name (strictly lowercase)
                variations.add(model.lower().strip())

                # Handle Roman numerals and standard numbers
                model_with_ints = model
                for roman, integer in roman_to_int.items():
                    model_with_ints = re.sub(rf"\b{roman}\b", integer, model_with_ints, flags=re.IGNORECASE)
                variations.add(model_with_ints.lower().strip())  # Standardized with numbers

                # Generate compact versions
                compact_model = re.sub(r"[\s-]", "", model_with_ints)  # Remove spaces and hyphens
                variations.add(compact_model.lower())

                # Variations with hyphen replaced by space
                space_model = model_with_ints.replace("-", " ")
                variations.add(space_model.lower())  # Lowercase with spaces

                # Add compacted versions of space-separated names
                variations.add(space_model.replace(" ", "").lower())  # Compact without spaces

                # Handle variations with and without "Mark"
                if "mark" in model.lower():
                    # Simplify "Mark II" → "II" and add variants
                    simplified = re.sub(r"mark\s+", "", model, flags=re.IGNORECASE)
                    simplified_with_ints = re.sub(rf"\b{roman_to_int.get('II', '2')}\b", "2", simplified, flags=re.IGNORECASE)
                    variations.add(simplified.lower())
                    variations.add(simplified_with_ints.lower())

                # Handle variations with spaces
                spaced_model = re.sub(r"(\d+)([a-zA-Z])", r"\1 \2", model_with_ints)
                variations.add(spaced_model.lower())

                # Add variations for both cases of hyphen removal
                variations.add(space_model.replace(" ", "").lower())
                variations.add(space_model.lower().replace(" ", ""))

                # Add combinations with Roman numeral and space-separated variants
                for roman, integer in roman_to_int.items():
                    spaced_roman = space_model.replace(roman, integer)
                    variations.add(spaced_roman.lower())

                # Add to the dictionary
                camera_models_dict[standardized_model] = list(sorted(variations))

    return camera_models_dict

# Generate the dictionary
camera_models_dict = generate_camera_models_dict(file_path)

# Save camera models dictionary
output_path = "camera_models_variations.json"
with open(output_path, "w") as json_file:
    json.dump(camera_models_dict, json_file, indent=1)

print(f"Camera models dictionary saved to {output_path}")
