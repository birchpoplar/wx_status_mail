import smtplib      # To send email notification
import requests     # To get image from internet
import shutil       # To save image locally
from datetime import datetime     # For date/time data

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# To Dos
# - add comments
# - add debug function to print out the text of the message rather than execute

# Function: gets image from internet using URL
def get_image(image_url):
    # Extract the filename from the full URL
    filename = image_url.split("/")[-1]
    # Request the actual image from URL
    r = requests.get(image_url, stream=True)

    # Check on completion and open/save file if successful
    if r.status_code == 200:
        r.raw.decode_content = True
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        print('Image successfully Downloaded: ', filename)
    else:
        print('Image Couldn\'t be retrieved')

# Function: add an image to the MIMEMultipart object
def addImageToMsg (filename, image_id, msg):
    image = MIMEImage(open(filename, 'rb').read())
    image.add_header('Content-ID', image_id)
    msg.attach(image)

# Source access and from/to details from dedicated file
loginDetails = open('access.txt')
username = loginDetails.readline()
password = loginDetails.readline()
from_addr = loginDetails.readline().rstrip()
to_addr = loginDetails.readline().rstrip()

# Get current date/time info
now = datetime.now()

# Set Msg subject with date/time info
msg_subject = 'Weather @ ' + now.strftime("%B %d, %Y %H:%M:%S")

# Build Msg object
msg = MIMEMultipart('alternative')
msg['Subject'] = msg_subject
msg['From'] = from_addr
msg['To'] = to_addr

# Start the email text html string
msg_text = '<h2>Weather Update : ' + now.strftime("%B %d, %Y %H:%M:%S") + '</h2> <br>'

# Open the images list dedicated file
sites = open('images.txt')

# Set initial image ID
imageId = 1

# Cycle through the image list to add image ID to the email text html string and also download
# and save the image file from the internet
for line in sites:
    items = line.split()
    msg_text += '<h3> ' + items[0][0:len(items[0])-1] + '</h3> <br> <img src="cid:image' + str(imageId) + '"> <br>'
    for_download = items[1]
    filename = for_download.split("/")[-1]
    get_image(for_download)
    imageId += 1

# Finish up on the string and attach to the Msg object
msg_text += '<h3>FINISHED</h3>'
msg.attach(MIMEText(msg_text, 'html'))

# Reset file pointer to beginning, will need for downloading images
sites.seek(0,0)

# Set counter
count = 1

# Cycle through the image file again to extract the image IDs and
# add image to MIME format Msg object

for line in sites:
    items = line.split()
    for_download = items[1]
    filename = for_download.split("/")[-1]
    addImageToMsg(filename, '<image' + str(count) + '>', msg)
    count += 1

# Send the email
s = smtplib.SMTP('smtp.gmail.com', 587)
s.starttls()
s.login(username.rstrip(), password.rstrip())
s.sendmail(from_addr, to_addr, msg.as_string())
s.quit()