from socket import *
import socket
import threading
import logging
import time
import sys

from file_protocol import FileProtocol
fp = FileProtocol()

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        try:
            while True:
                try:
                    # For large uploads, we need to receive all data
                    data_received = ""
                    buffer_size = 8192  # Larger buffer
                    
                    # First, try to determine if this is an upload by reading initial data
                    initial_data = self.connection.recv(buffer_size)
                    if not initial_data:
                        break
                    
                    data_received += initial_data.decode()
                    
                    # If it's an UPLOAD command, we need to receive all data
                    if data_received.upper().startswith('UPLOAD'):
                        # Keep receiving until we have complete data
                        # We'll use a simple approach: keep receiving until no more data comes
                        self.connection.settimeout(1.0)  # 1 second timeout
                        
                        while True:
                            try:
                                more_data = self.connection.recv(buffer_size)
                                if more_data:
                                    data_received += more_data.decode()
                                else:
                                    break
                            except socket.timeout:
                                # No more data received within timeout
                                break
                            except Exception as e:
                                logging.error(f"Error receiving more data: {e}")
                                break
                        
                        self.connection.settimeout(None)  # Reset timeout
                    
                    if data_received:
                        logging.warning(f"Processing command from {self.address}, data length: {len(data_received)}")
                        hasil = fp.proses_string(data_received.strip())
                        hasil = hasil + "\r\n\r\n"
                        self.connection.sendall(hasil.encode())
                    else:
                        break
                        
                except Exception as e:
                    logging.error(f"Error processing client {self.address}: {e}")
                    break
        finally:
            try:
                self.connection.close()
                logging.warning(f"Connection closed for {self.address}")
            except:
                pass

class Server:
    def __init__(self, ipaddress='0.0.0.0', port=8889):
        self.ipinfo = (ipaddress, port)
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = True

    def serve_forever(self):
        logging.warning(f"server berjalan di ip address {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(5)
        
        try:
            while self.running:
                try:
                    self.connection, self.client_address = self.my_socket.accept()
                    logging.warning(f"connection from {self.client_address}")

                    clt = ProcessTheClient(self.connection, self.client_address)
                    clt.daemon = True  # Make thread daemon so it doesn't prevent shutdown
                    clt.start()
                    self.the_clients.append(clt)
                    
                    # Clean up finished threads
                    self.the_clients = [t for t in self.the_clients if t.is_alive()]
                    
                except Exception as e:
                    if self.running:
                        logging.error(f"Error accepting connection: {e}")
        except KeyboardInterrupt:
            logging.warning("Server interrupted by user")
        finally:
            self.shutdown()

    def shutdown(self):
        self.running = False
        try:
            self.my_socket.close()
            logging.warning("Server socket closed")
        except:
            pass

def main():
    # Setup logging
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
    
    svr = Server(ipaddress='0.0.0.0', port=6666)
    
    try:
        svr.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server...")
        svr.shutdown()

if __name__ == "__main__":
    main()