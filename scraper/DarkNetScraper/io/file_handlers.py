import chardet, json, sys, os
import json


def detect_encoding(file):
    """
    Detects the encoding of a file using the chardet library.

    Parameters:
    file (str): The path to the file whose encoding needs to be detected.

    Returns:
    dict: A dictionary containing encoding information, including 'encoding' (the detected encoding),
          'confidence' (confidence score of the detected encoding), and 'language' (detected language).
    """
    detector = chardet.universaldetector.UniversalDetector()
    with open(file, "rb") as f:
        for line in f:
            detector.feed(line)
            if detector.done:
                break
    detector.close()
    return detector.result


def read_file(file_name):
    """
    Reads the content of a file with auto-detected encoding.

    :param file_name: The path to the file to be read.
    :type file_name: str

    :return: The contents of the file as a string.
    :rtype: str

    :raises FileNotFoundError: If the specified file does not exist.
    """
    encoding = detect_encoding(file_name)['encoding']
    try:
        with open(file_name, 'r', encoding=encoding) as file:
            return file.read()
    except FileNotFoundError:
        print(f"File not found: {file_name}")
        sys.exit(1)

def write_to_file(file_name, data):
    """
    Writes data to a file, overwriting the existing content if the file already exists.

    :param file_name: The path to the file where data will be written.
    :type file_name: str

    :param data: The data to be written to the file.
    :type data: str
    """
    with open(file_name, "w") as file:
        file.write(data)
        file.close()

def read_json(file_name):
    """
    Reads and parses JSON data from a file.

    :param file_name: The path to the JSON file to be read and parsed.
    :type file_name: str

    :return: A Python data structure representing the JSON data.
    :rtype: dict or list

    :raises FileNotFoundError: If the specified file does not exist.
    :raises json.JSONDecodeError: If the JSON data cannot be decoded.
    """
    try:
        # Read the contents of the JSON file using the read_file function
        json_data = read_file(file_name)
        
        # Parse the JSON data into a Python data structure
        parsed_data = json.loads(json_data)
        
        return parsed_data
    except FileNotFoundError:
        print(f"File not found: {file_name}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in {file_name}: {e}")
        raise

def save_json(file_path,data):
    write_to_file(file_path,json.dumps(data,indent=4))
    
def join_path(file_directory, file_name):
    if file_directory == "":
        sys.exit(1)
    # Create data directory if it doesn't exist
    if not os.path.exists(file_directory):
        os.makedirs(file_directory)
    local_path = os.path.join(file_directory, file_name)

def find_files(directory):
    text_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            text_files.append(os.path.join(root, file))

    return text_files

if __name__ == "__main__":
    start_directory = input("Enter the directory to start the search: ")

    if os.path.exists(start_directory):
        text_files = find_files(start_directory)

        if text_files:
            print("Text files found:")
            for file_path in text_files:
                print(f"Reading file: {file_path}")
                content = read_file(file_path)
                print(content)
        else:
            print("No text files found in the directory and its subdirectories.")
    else:
        print("The specified directory does not exist.")
