import os
import cv2
import numpy as np
from PIL import Image
import pickle
from matplotlib import pyplot
from matplotlib.patches import Rectangle
from mtcnn.mtcnn import MTCNN
import tensorflow as tf # tensorflow is needed since we are using MTCNN, which is a deep learning model built on tensorflow
import cv2
from sklearn.model_selection import train_test_split
import random
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

#This function is used to perform evaluation on testing data
def prediction(recognizer,x_test,y_test):
    correct = 0
    wrong = 0
    correct_conf = 0
    wrong_conf = 0
    for i in range(len(x_test)):
        print("current: ",i)
        # use recognizer to predict the input face image
        id_, conf = recognizer.predict(x_test[i])
        print("id_",id_," conf:",conf, "y_test[i]: ",y_test[i])
        if id_ == y_test[i]:
            correct +=1
            correct_conf += conf
        else:
            print("=========wrong===========")
            print("At "+str(i)+"  Predicted: "+str(id_)+"   GroundTruth: "+str(y_test[i]))
            cv2.imwrite("predict_"+str(id_)+"_truth_"+str(y_test[i])+".jpg",x_test[i])
            wrong_conf += conf
            wrong += 1
    print("Correct count: ",correct)
    print("Wrong count: ",wrong)
    print("Average correct conf: ",(correct_conf/correct) if correct != 0 else 0)
    print("Average wrong conf: ",(wrong_conf/wrong) if wrong != 0 else 0)
    return correct,wrong

# choose not to use GPU
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
# set file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# set image path to "images"
image_dir = os.path.join(BASE_DIR, "images")
# create LBPH recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
# create MTCNN face detector
detector = MTCNN()
current_id = 0
label_ids = {}
# array to store face image
x_train = []
# array to store ground truth labels
y_labels = []
counter = 0

#loop the images folder
for root, dirs, files in os.walk(image_dir):
    for file in files:
        # check whetehr it is image
        if file.endswith("png") or file.endswith("jpg") or file.endswith("jpeg"):
            path = os.path.join(root,file)
            label = os.path.basename(os.path.dirname(path)).replace(" ","-").lower()
            print("current label = ",label, "  counter = ",counter)
            current = [key for key,value in label_ids.items() if value['name']==label]
            if len(current)>0:
                pass
            else:
                student_id = input("Please input student_id : ")
                label_ids[current_id] = {'name':label,'student_id':student_id}
                current_id += 1
            id_ = [key for key,value in label_ids.items() if value['name']==label][0]
            #read the image
            img_array = cv2.imread(path)
            # convert the image from BGR to RGB
            img_array=cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
            # use MTCNN to detect face in image
            faces = detector.detect_faces(img_array)
            # if face detected
            if len(faces)>0:
                # convert the image to grayscale
                gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
                # extract the (x,y) position of face, width and height of the box of face
                (x, y, w, h) = faces[0]['box']
                # extract the face from the image
                roi_gray = gray[y:y + h, x:x + w]
                # resize the image
                roi_gray = cv2.resize(roi_gray,(550,550))
                x_train.append(roi_gray)
                y_labels.append(id_)
            counter+=1
with open("labels.pickle",'wb') as f:
    pickle.dump(label_ids,f)
# split all the images into training and testing set
X_train, X_test, y_train, y_test = train_test_split(x_train, y_labels, test_size=0.25, random_state=10,stratify=y_labels)
temp_x = [] # temp array to store augmented data
temp_y = []
# perform data augmentation
for i in range(len(X_train)):
    temp_x.append(random_noise(X_train[i]))
    temp_x.append(horizontal_flip(X_train[i]))
    temp_x.append(random_rotation(X_train[i]))
    temp_y.append(y_train[i])
    temp_y.append(y_train[i])
    temp_y.append(y_train[i])

print("X_train length = ",len(X_train))
print("y_train length = ",len(y_train))
print("X_test length = ",len(X_test))
print("y_test length = ",len(y_test))
X_train = X_train + temp_x
y_train = y_train + temp_y
print("After augmented: ")
print("X_train length = ",len(X_train))
print("y_train length = ",len(y_train))

#train the LBPH recognizer
recognizer.train(X_train, np.array(y_train))
# evaluate using prediction function
correct,wrong = prediction(recognizer,X_test,y_test)
print("accuracy: ",float(correct)/float(len(X_test)),"%")
print("wrong: ",float(wrong)/float(len(X_test)),"%")
# use the testing data to update the recognizer in order to get better result
recognizer.update(X_test,np.array(y_test))
# extract the recognizer to yaml file
recognizer.write("trainner.yaml")
