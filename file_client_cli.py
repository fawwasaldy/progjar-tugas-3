import socket
import json
import base64
import logging
import os
import time

server_address=('0.0.0.0',6666)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        # Send data in chunks for large uploads
        command_bytes = command_str.encode()
        total_sent = 0
        chunk_size = 8192
        
        logging.warning(f"sending message of {len(command_bytes)} bytes...")
        
        # Send data in chunks
        while total_sent < len(command_bytes):
            chunk = command_bytes[total_sent:total_sent + chunk_size]
            sent = sock.send(chunk)
            total_sent += sent
            
            # Small delay for large uploads to ensure server can process
            if len(command_bytes) > 100000:  # For files > 100KB
                time.sleep(0.001)  # 1ms delay
        
        logging.warning(f"sent {total_sent} bytes total")
        
        # Receive response
        data_received = ""
        sock.settimeout(10.0)  # 10 second timeout for response
        
        while True:
            try:
                data = sock.recv(4096)
                if data:
                    data_received += data.decode()
                    if "\r\n\r\n" in data_received:
                        break
                else:
                    break
            except socket.timeout:
                logging.error("Timeout waiting for server response")
                return dict(status='ERROR', data='Server response timeout')
        
        # Remove the protocol ending
        data_received = data_received.replace("\r\n\r\n", "")
        
        # Parse JSON response
        hasil = json.loads(data_received)
        logging.warning("data received from server")
        return hasil
        
    except Exception as e:
        logging.error(f"error during communication: {e}")
        return dict(status='ERROR', data=str(e))
    finally:
        sock.close()


def remote_list():
    command_str=f"LIST"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print(f"Gagal: {hasil['data']}")
        return False

def remote_get(filename=""):
    command_str=f"GET {filename}"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        #proses file dalam bentuk base64 ke bentuk bytes
        namafile= hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        fp = open(namafile,'wb+')
        fp.write(isifile)
        fp.close()
        print(f"File {namafile} berhasil didownload")
        return True
    else:
        print(f"Gagal: {hasil['data']}")
        return False

def remote_upload(filename=""):
    if not os.path.exists(filename):
        print(f"File {filename} tidak ditemukan di local")
        return False
    
    try:
        # Check file size
        file_size = os.path.getsize(filename)
        print(f"Uploading file {filename} ({file_size} bytes)...")
        
        # Read and encode file
        with open(filename, 'rb') as fp:
            file_content = fp.read()
            file_content_b64 = base64.b64encode(file_content).decode()
        
        # Validate base64 encoding
        try:
            base64.b64decode(file_content_b64)
        except Exception as e:
            print(f"Error in base64 encoding: {e}")
            return False
        
        command_str = f"UPLOAD {filename} {file_content_b64}"
        print(f"Encoded to base64: {len(file_content_b64)} characters")
        
        hasil = send_command(command_str)
        if (hasil['status']=='OK'):
            print(f"Berhasil: {hasil['data']}")
            return True
        else:
            print(f"Gagal: {hasil['data']}")
            return False
            
    except Exception as e:
        print(f"Error during upload: {e}")
        return False

def remote_delete(filename=""):
    command_str=f"DELETE {filename}"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        print(f"Berhasil: {hasil['data']}")
        return True
    else:
        print(f"Gagal: {hasil['data']}")
        return False

def interactive_client():
    while True:
        print("\n=== FILE SERVER CLIENT ===")
        print("1. LIST - Tampilkan daftar file")
        print("2. GET - Download file")
        print("3. UPLOAD - Upload file")
        print("4. DELETE - Hapus file")
        print("0. EXIT")
        
        choice = input("Pilih operasi (0-4): ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            remote_list()
        elif choice == "2":
            filename = input("Masukkan nama file yang akan didownload: ").strip()
            if filename:
                remote_get(filename)
        elif choice == "3":
            filename = input("Masukkan nama file yang akan diupload: ").strip()
            if filename:
                remote_upload(filename)
        elif choice == "4":
            filename = input("Masukkan nama file yang akan dihapus: ").strip()
            if filename:
                confirm = input(f"Yakin ingin menghapus {filename}? (y/n): ").strip().lower()
                if confirm == 'y':
                    remote_delete(filename)
                else:
                    print("Penghapusan dibatalkan")
        else:
            print("Pilihan tidak valid!")


if __name__=='__main__':
    # Setup logging
    logging.basicConfig(level=logging.WARNING)
    
    # Set server address untuk testing local
    server_address=('127.0.0.1',6666)
    
    # Interactive mode
    interactive_client()