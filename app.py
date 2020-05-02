import dependencies

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

client = gspread.authorize(creds)

sheet = client.open("Database").sheet1  #Set Up you Google Sheets api and Change the name of the file here.

def get_time():
    india_tz= tz.gettz('Asia/Kolkata')
    now = datetime.now()
    now = now.replace(tzinfo = india_tz)
    now = now.astimezone(india_tz)
    time = now.isoformat()
    return time
#Function to update the google sheet with the data returned from the api for the 
#Particular media
def update_dataframe(im_url, im_type, prediction, location, From_No, Media_Type, bbox, score):
    time = get_time()
    """with open('Database.csv','a') as newRow:
        newRowWriter = csv.writer(newRow)
        newRowWriter.writerow([time, im_url, im_type, prediction, location, bbox, score])"""
    row = [str(time), str(im_type), str(prediction), str(location), str(From_No), str(Media_Type), str(bbox), str(score), str(im_url)]
    sheet.append_row(row)

#Convert pdf's to images (sometimes user also send the pdf's of the payment)
def pdf_url_to_base64(url):
    base_link = "https://s3-external-1.amazonaws.com/media.twiliocdn.com/"
    #Directly the twilio url for pdf does not open using urlopen
    #Using requests it can open directly, but returns the full pdf
    #in the form not required (cant be converted to images using
    # pdf2image converter)
    try:
        urllib.request.urlopen(url) #gives http 403 error
    except urllib.error.HTTPError as e:
        call_url = base_link + e.geturl().split('https://media.twiliocdn.com/')[1].split('?')[0]
        call_url_read = urllib.request.urlopen(call_url).read()
        try: #if not empty pdf
            pdf_images = pdf2image.convert_from_bytes(call_url_read, fmt='jpeg')
            #convert pdf images (1st page) (PIL type) into bytes 64
            buffered = BytesIO()
            pdf_images[0].save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue())
            return img_str
        except:
            print("Error opening pdf/empty pdf")
            return(1234567)  #return error code



#Encode the image to base-64 string from the url.
def get_as_base64(url):   #Function to convert the image url to base64 string

    return base64.b64encode(requests.get(url).content)


app = Flask(__name__)

#api's url where to send the image for processing
aws_post_url = "<YOUR-API-ENDPOINT-1 (Calculate for the Payment)>"
aws_post_url_app_download = "<YOUR-API-ENDPOINT-2- (Check Arogya Setu App)>"

@app.route("/", methods = ['GET'])
def home():
	html_content = '''<h1>Hello World!!</h1>
                      <h2>Nothing else here. Move to /whatsapp</h2>'''
	return html_content

#Whenevr an image is sent, this route is triggered by twilio.
@app.route("/whatsapp", methods=["GET", "POST"])
def reply_whatsapp():
    print("Request Received")
    response = MessagingResponse()
    num_media = int(request.values.get("NumMedia"))
    AccountSid = request.values.get("AccountSid")
    From_Mobile = request.values.get("From").split("whatsapp:")[1]
    Media_Type = request.values.get("MediaContentType0")
    #print(request.values)
    #print("Time of triggering is : {}".format(request.values.get(""))
    # print("Account SID is : {}".format(request.values.get("AccountSid")))
    # print(type(request.values.get("To")))
    #whatsapp_no_to = str(request.values.get("To").split("whatsapp:")[1])
    # print("from: {}".format(request.values.get("From"))
    if (str(AccountSid) == "<Twilio Account SID 1>"):
        loc_received = "Karnal"
    if (str(AccountSid) == "<Twilio Account SID 2>"):
        loc_received = "Gharaunda"
    if (str(AccountSid) == "<Twilio Account SID 3>"):
        loc_received = "Assandh"
    if (str(AccountSid) == "<Twilio Account SID 4>"):
        loc_received = "Indri City"
    if (str(AccountSid) == "<Twilio Account SID 5>"):
        loc_received = "Nilokheri"
    if (str(AccountSid) == "<Twilio Account SID 6>"):
        loc_received = "Panipat City"
    if (str(AccountSid) == "<Twilio Account SID 7>"):
        loc_received = "Panipat Rural"
    if (str(AccountSid) == "<Twilio Account SID 8>"):
        loc_received = "Israna"
    if (str(AccountSid) == "<Twilio Account SID 9>"):
        loc_received = "Samalkha" 
    #if the user does not send a media (image/pdf)
    if not num_media:
        msg = response.message("Send us the Screenshot!")
    else:
        #msg = response.message("Thanks for Waiting..")
        Media_url = request.values.get("MediaUrl0")
        #Check for media type Image
        if(Media_Type == 'image/jpeg'):
            Image_base64 = get_as_base64(Media_url)
            Image_base64_str = Image_base64.decode("utf-8")
        
        #Check for media type PDF
        elif(Media_Type == 'application/pdf'):
            Image_base64 = pdf_url_to_base64(Media_url)
            
            if(Image_base64 == 1234567):   #Empty pdf
                msg = response.message("Please send the Correct Media")
                return str(response)
            else:
                Image_base64_str = Image_base64.decode("utf-8")
        
        #If other media such as an audio was sent by the user.
        else:
            msg = response.message("Please send the Correct Media")
            return str(response)
  
        #Change according to your payload/ remove if you are processing the media here itself.
        payload = {
                    "Image": Image_base64_str ,
                    "Location": loc_received
                } 
        #Change according to your headers/ remove if you are processing the media here itself.
        headers = {
                    'Content-Type': 'application/json',
                    'x-api-key': 'iXS3orLX2h1UNB9GFSy1179zdT1NvCQi4ri5PWi6'
                }

        #Send Request to the Arogya Setu app Checking API
        response_if_app_download = requests.request("POST", aws_post_url_app_download, headers=headers, data = json.dumps({"Image": Image_base64_str, "Location": loc_received }))
        json_response_ = response_if_app_download.json()
        #print(json_response_)
        if_downloaded = json_response_["app_present"]
        #print("if_downloaded is :" + str(if_downloaded))
        if(if_downloaded):  # if the app is downloaded
           msg = response.message("Thankyou for Downloading the App" + " from Area {}".format(loc_received)) #This response will be sent back to the user
           update_dataframe(Media_url, "App_Download", if_downloaded, loc_received, From_Mobile, Media_Type, json_response_["bbox"], json_response_["score"])


        else:  # if Screenshot is not of the app / app is not downloaded, then check for payment
            response_loc_n_amount = requests.request("POST", aws_post_url, headers=headers, data = json.dumps(payload))
            json_response = response_loc_n_amount.json()
            #print(json_response)
            city = json_response["Location"]
            Inc_amount = json_response["Incremented Amount"]
            if(str(Inc_amount) != '0.0'):
                update_dataframe(Media_url, "Payment", str(Inc_amount), loc_received, From_Mobile, Media_Type, None, None)
                #print(f"City is {city}  and Amount Incremented is {Inc_amount}")
                msg = response.message("Thankyou for donating Rs " + str(Inc_amount) + " from Area {}".format(loc_received))
            
            #If nothing was detected in the image sent
            else:
                #print("Please send relevant SS")
                msg = response.message("Please send relevant Screenshot")
                update_dataframe(Media_url, "Null", str(Inc_amount), loc_received, From_Mobile, Media_Type, None, None)




    #return num_media
    print("Response Sent")
    return str(response)


if __name__ == "__main__":
    app.run(host = '0.0.0.0', debug = True, port = 80)
