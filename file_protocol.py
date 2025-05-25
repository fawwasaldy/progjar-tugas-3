import json
import logging
import base64
import os

from file_interface import FileInterface

"""
* class FileProtocol bertugas untuk memproses 
data yang masuk, dan menerjemahkannya apakah sesuai dengan
protokol/aturan yang dibuat

* data yang masuk dari client adalah dalam bentuk bytes yang 
pada akhirnya akan diproses dalam bentuk string

* class FileProtocol akan memproses data yang masuk dalam bentuk
string
"""

class FileProtocol:
    def __init__(self):
        self.file = FileInterface()
    
    def proses_string(self, string_datamasuk=''):
        logging.warning(f"Processing command: {string_datamasuk[:50]}...")
        
        # Handle UPLOAD command specially due to large base64 data
        if string_datamasuk.upper().startswith('UPLOAD'):
            try:
                # Find first space after UPLOAD
                first_space = string_datamasuk.find(' ')
                if first_space == -1:
                    return json.dumps(dict(status='ERROR', data='Invalid UPLOAD command format'))
                
                # Find second space (after filename)
                second_space = string_datamasuk.find(' ', first_space + 1)
                if second_space == -1:
                    return json.dumps(dict(status='ERROR', data='Missing file content for UPLOAD'))
                
                # Extract parts
                command = string_datamasuk[:first_space].strip().lower()
                filename = string_datamasuk[first_space+1:second_space].strip()
                base64_content = string_datamasuk[second_space+1:].strip()
                
                logging.warning(f"Upload request - filename: {filename}, content length: {len(base64_content)}")
                
                # Validate base64 content
                try:
                    # Test decode a small portion to validate format
                    test_decode = base64.b64decode(base64_content[:100] if len(base64_content) > 100 else base64_content)
                except Exception as e:
                    return json.dumps(dict(status='ERROR', data=f'Invalid base64 format: {str(e)}'))
                
                params = [filename, base64_content]
                result = getattr(self.file, command)(params)
                return json.dumps(result)
                
            except Exception as e:
                logging.error(f"Error processing upload: {e}")
                return json.dumps(dict(status='ERROR', data=f'Upload processing error: {str(e)}'))
        
        # Handle other commands normally
        try:
            parts = string_datamasuk.strip().split()
            if not parts:
                return json.dumps(dict(status='ERROR', data='Empty command'))
            
            command = parts[0].lower()
            params = parts[1:] if len(parts) > 1 else []
            
            logging.warning(f"Processing command: {command} with params: {params}")
            
            if hasattr(self.file, command):
                result = getattr(self.file, command)(params)
                return json.dumps(result)
            else:
                return json.dumps(dict(status='ERROR', data='Command not recognized'))
                
        except Exception as e:
            logging.error(f"Error processing command: {e}")
            return json.dumps(dict(status='ERROR', data='Request processing error'))


if __name__=='__main__':
    #contoh pemakaian
    fp = FileProtocol()
    print(fp.proses_string("LIST"))
    print(fp.proses_string("GET pokijan.jpg"))
    
    # Test upload
    test_content = "Hello World Test"
    test_b64 = base64.b64encode(test_content.encode()).decode()
    print(fp.proses_string(f"UPLOAD test.txt {test_b64}"))
    
    # Test delete
    print(fp.proses_string("DELETE test.txt"))