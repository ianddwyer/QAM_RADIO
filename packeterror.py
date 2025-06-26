
import numpy as np

def readBinary(file_path, dtype=np.float32):
    try:
        data = np.fromfile(file_path, dtype=dtype)
        return data
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
         print(f"An error occurred: {e}")
         return None

file_path = 'totalpktcount.bin'
endvalue_all = readBinary(file_path)[-1]

file_path = 'successpktcount.bin'
endvalue_success = readBinary(file_path)[-1]

dropped = endvalue_all - endvalue_success
successrate =  (1-dropped/endvalue_all)*100
outagerate =  (dropped/endvalue_all)*100
print(f"Total TX Packets: {int(endvalue_all)}")
print(f"Dropped Packets: {int(dropped)}")
print(f"Success Rate: {successrate:.{6}g}")
print(f"Outage  Rate: {outagerate:.{4}g}")
