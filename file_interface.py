import os
import json
import base64
from glob import glob


class FileInterface:
    def __init__(self):
        os.chdir('files/')

    def list(self,params=[]):
        try:
            filelist = glob('*.*')
            return dict(status='OK',data=filelist)
        except Exception as e:
            return dict(status='ERROR',data=str(e))

    def get(self,params=[]):
        try:
            filename = params[0]
            if (filename == ''):
                return dict(status='ERROR',data='nama file tidak boleh kosong')
            fp = open(f"{filename}",'rb')
            isifile = base64.b64encode(fp.read()).decode()
            fp.close()
            return dict(status='OK',data_namafile=filename,data_file=isifile)
        except Exception as e:
            return dict(status='ERROR',data=str(e))

    def upload(self,params=[]):
        try:
            if len(params) < 2:
                return dict(status='ERROR',data='parameter tidak lengkap (nama file dan konten base64)')
            
            filename = params[0]
            file_content_b64 = params[1]
            
            if (filename == '' or file_content_b64 == ''):
                return dict(status='ERROR',data='nama file dan konten tidak boleh kosong')
            
            # Decode base64 content
            file_content = base64.b64decode(file_content_b64)
            
            # Write file
            with open(filename, 'wb') as fp:
                fp.write(file_content)
            
            return dict(status='OK',data=f'file {filename} berhasil diupload')
        except Exception as e:
            return dict(status='ERROR',data=str(e))

    def delete(self,params=[]):
        try:
            if len(params) < 1:
                return dict(status='ERROR',data='nama file tidak boleh kosong')
                
            filename = params[0]
            if (filename == ''):
                return dict(status='ERROR',data='nama file tidak boleh kosong')
            
            if not os.path.exists(filename):
                return dict(status='ERROR',data='file tidak ditemukan')
            
            os.remove(filename)
            return dict(status='OK',data=f'file {filename} berhasil dihapus')
        except Exception as e:
            return dict(status='ERROR',data=str(e))


if __name__=='__main__':
    f = FileInterface()
    print(f.list())
    print(f.get(['pokijan.jpg']))
    
    # Test upload - create a test file
    test_content = "Hello World Test File"
    test_content_b64 = base64.b64encode(test_content.encode()).decode()
    print(f.upload(['test.txt', test_content_b64]))
    print(f.list())
    
    # Test delete
    print(f.delete(['test.txt']))
    print(f.list())