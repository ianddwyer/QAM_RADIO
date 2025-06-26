- In a cmd console, cd to the app directory (this one)
- Run chatUDPSMS (example using my directories):

cd C:\Users\Eian\Desktop\all_desktop_01092025\EE_References\School_S25\Digital_Comm\Project\RADIO\RADIO
py chatUDPSMS.py

- Open Anaconda Navigator as Admin and go to the 'radioconda' environment installed
- In Environments, press the play button on the left panel then select terminal
- Change to app directory (this one). Run the RADIO.py app to start streaming.
- Here is an example with my inputs for a localized half duplex echo version of radio (current used):

cd C:\Users\Eian\Desktop\all_desktop_01092025\EE_References\School_S25\Digital_Comm\Project\RADIO
python RADIO.py

- A goal is to have the input be taken as so:

cd C:\Users\Eian\Desktop\all_desktop_01092025\EE_References\School_S25\Digital_Comm\Project\RADIO
python RADIO.py 2420000000 5005 '11100001010110101110100010010011'

** syntax is python <file.py> <centerf> <UDPport> <CRC32KEY>

