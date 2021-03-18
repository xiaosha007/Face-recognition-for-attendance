from flask import Flask,request
import base64
from flask_cors import CORS, cross_origin
from PIL import Image
import cv2
import io
import pickle
import pathlib
import os
import numpy as np
from mtcnn.mtcnn import MTCNN
import tensorflow as tf
import operator
import skimage as sk
from skimage import transform
from skimage import util
def random_rotation(image_array):
    # pick a random degree of rotation between 25% on the left and 25% on the right
    random_degree = random.uniform(-25, 25)
    return sk.transform.rotate(image_array, random_degree)

def random_noise(image_array):
    # add random noise to the image
    return sk.util.random_noise(image_array)

def horizontal_flip(image_array):
    # horizontal flip doesn't need skimage, it's easy as flipping the image array of pixels !
    return image_array[:, ::-1]

# set default not to use GPU
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
app = Flask(__name__)
if __name__ == '__main__':
    app.run(debug=True)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# face detector
detector = MTCNN()
# recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
# load the recognizer that we trained earlier
recognizer.read("trainner.yaml")
labels = {}
# load the labels (groundtruth)
with open("labels.pickle",'rb') as f:
    og_labels = pickle.load(f)
    labels = og_labels
print(labels)


@app.route('/')
@cross_origin()
def hello_world():
    return 'Hello, World1!'

#convert the base64 string to RGB image
def stringToRGB(base64_string):
    imgdata = base64.b64decode(str(base64_string))
    image = Image.open(io.BytesIO(imgdata))
    return np.array(image)

#convert the numpy image array into base64 string
def imgToBase64(img):
    retval, buffer = cv2.imencode('.jpg', img)
    pg_as_text = base64.b64encode(buffer)  
    return pg_as_text.decode("ascii")

#generate a response to return to api call
def generateResponse(code,data,message):
    return {
        "code":code,
        "data":data,
        "message":message        
    }

#take an input image and use MTCNN to detect face in that image
def detectFace(img):
    faces = detector.detect_faces(img)
    print(faces)
    if len(faces)==0:
        return None
    return faces[0]


def recognizeFace(img,face_coor,img_list):
    # extract the (x,y) position of face, width and height of box of face
    x,y,width,height = face_coor['box']
    # convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # extract out the face region in the image
    roi_gray = gray[y:y+height,x:x+width]
    roi_gray = cv2.resize(roi_gray,(550,550))
    # input the face extracted and use recognizer for prediction
    id_, conf = recognizer.predict(roi_gray)
    # draw a rectangle on the face region of original image and label with name
    cv2.rectangle(img, (x,y), (x+width,y+height),(255,0,0), 2)
    cv2.putText(img, labels[id_]['name']+"-"+str(round(conf,2)), (x-5,y-5), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.5, (0,0,255), 2, cv2.LINE_AA)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_list.append(imgToBase64(img))
    return id_,conf

# this function is used to regiser a new face to LBPH recognizer
# an image array contains all the faces is taken as input
def registerNewFace(imageList,studentName,studentID):
    new_x=[]
    new_y=[]
    new_id = len(labels)
    # only when the number of faces exceed 3, the user is allowed to register
    # face registered is used to store the number of faces deteced in the image array
    face_registered = 0
    for img in imageList:
        image = stringToRGB(img)
        faces = detector.detect_faces(image)
        if len(faces)>0:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            (x, y, w, h) = faces[0]['box']
            roi_gray = gray[y:y + h, x:x + w]
            roi_gray = cv2.resize(roi_gray,(550,550))
            # data augmentation
            new_x.append(random_noise(roi_gray))
            new_x.append(horizontal_flip(roi_gray))
            new_x.append(random_rotation(roi_gray))
            new_x.append(roi_gray)
            new_y.append(new_id)
            new_y.append(new_id)
            new_y.append(new_id)
            new_y.append(new_id)
            face_registered+=1
    # update the LBPH recognizer
    recognizer.update(new_x,np.array(new_y))
    recognizer.write("trainner.yaml")
    labels[new_id] = {'name':studentName,"student_id":studentID}
    print(labels)
    with open("labels.pickle",'wb') as f:
        pickle.dump(labels,f)
    return face_registered

@app.route('/register_face',methods = ['POST'])
@cross_origin()
def register_face():
    try:
        request_body = request.get_json()
        studentID = request_body['studentID']
        studentName = request_body['studentName']
        imageList = request_body['imageList']
        register_count = registerNewFace(imageList,studentName,studentID)
        if(register_count>3):
            return generateResponse(200,studentID,"Register successfully with student name = "+str(studentName)+". \n"+str(register_count)+" faces are detected")
        else:
            return generateResponse(400,studentID,"Only " + str(register_count)+ " faces are detected.\nPlease try again.")
    except:
        return generateResponse(500,None,"Failed to register.\nPlease try again")

@app.route('/sign_attendance',methods = ['POST'])
@cross_origin()
def sign_attendance():
    try:
        request_body = request.get_json()
        # take input from request body
        studentID = request_body['studentID']
        # the images are now in base64 format
        images = request_body['images']
        result = {}
        result_conf = []
        img_list = []
        # loop through the image array
        for index,img in enumerate(images):
            #convert the base64 string to numpy array image
            image = stringToRGB(img)
            #use MTCNN to detect face in image
            face_coor = detectFace(image)
            id_,conf = None,100
            # if face detected
            if face_coor:
                # use recognizeFace function to perform face prediction using LBPH recognizer
                id_,conf = recognizeFace(image,face_coor,img_list)
            print("id_: ",id_, "   Confidence: ",conf)
            result_conf.append([id_,conf])
            id_ = id_ if (id_ and conf<=40) else "Unknown"
            if not id_ in result:
                result[id_] = 0
            result[id_] += 1
        # get the final result by getting the highest occurance of predicted Label
        final_result = max(result.items(), key=operator.itemgetter(1))
        message = "Could not recognize face from the image.\nPlease try again."
        code = 400
        if final_result[0]!='Unknown' and final_result[1]>=2:
            student = labels[final_result[0]]
            message = "Student ID does not match with face ID.\nFailed to record attendance."
            if str(studentID) == str(student['student_id']):
                message = "Attendance recorded"+"\nThe user is: "+str(student['name'])+" with student id = "+str(student['student_id'])
                code = 200
        print(final_result)
        message += "\n\nPredicted details:\n"
        for index,item in enumerate(result_conf):
            message+= "Predicted face "+str(index+1)+" : "+str(labels[item[0]]['name']) + " with confidence = "+str(item[1])+"\n"
        return generateResponse(code,img_list,message)
    except Exception as err:
        print(err)
        return generateResponse(500,None,"Something went wrong.\nPlease try again later.")
