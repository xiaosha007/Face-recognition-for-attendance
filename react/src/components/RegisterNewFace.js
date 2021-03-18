import React,{useState,useCallback,useRef} from 'react';
import CameraFrame from './CameraFrame';
import axios from 'axios';
import {TiTick} from 'react-icons/ti';
import {ImCross} from 'react-icons/im';
import { useHistory } from 'react-router-dom';
import { Button } from 'react-bootstrap';

const RegisterNewFace = () => {
    const [studentID,setStudentID] = useState("");
    const [cameraOn,setCameraOn] = useState(true);
    const [returnedResponse,setReturnedResponse] = useState();
    const [instruction,setInstruction] = useState("You are required to snap 6 photos to register.");
    const [responseStatus,setResponseStatus] = useState();
    const [studentName,setStudentName] = useState("");
    const [imageList,setImageList] = useState([]);
    const { innerWidth: width, innerHeight: height } = window;

        
    const webcamRef = useRef(null);
    const capture = useCallback(
        () => {
            const imageSrc = webcamRef.current.getScreenshot();
            return imageSrc;
        },
        [webcamRef]
    );

    const handleReturn = (e)=>{
        e.preventDefault();
        setCameraOn(true);
        setInstruction("You are required to snap 6 photos to register.");
    }
    const history = useHistory();
    const handleReturnToHome=(e)=>{
        history.push("/");
    }
    const requiredImgCount = 6;
    const handleSnap = (e)=>{
        e.preventDefault();
        if(imageList.length<6){
            let image = capture();
            imageList.push(image.replace("data:image/jpeg;base64,",""))
            setImageList(imageList);
            setInstruction((requiredImgCount-imageList.length)+" more images to snap.");
        }
    }
    const handleSubmitForRecog = (e)=>{
        console.log('test')
        e.preventDefault();
        if(imageList.length===requiredImgCount){
            setInstruction("Submitting...")
            axios.post('http://localhost:5000/register_face', {
                studentName:studentName,
                studentID: studentID,
                imageList: imageList,
            })
            .then(function (response) {
                setCameraOn(false);
                console.log(response);
                setResponseStatus(response.data.code);
                setReturnedResponse(response.data.message)
            })
            .catch(function (error) {
                console.log(error);
            });  
        }else{
            setInstruction("Please snap 6 photos to continue.")
        }
    }
    const handleStudentID =(e)=>{
        setStudentID(e.target.value);
    }
    const handleStudentName =(e)=>{
        setStudentName(e.target.value);
    }
    return (
        <div style={{textAlign:"center",padding:"20px",marginLeft:"60px",marginRight:"60px",background:"rgba(0, 0, 0, 0.3)",color:"white"}}>
            <h1 >Register a new face</h1>
            {cameraOn?<><CameraFrame webcamRef={webcamRef} capture={capture} windowDimensions={{width,height}}/>
            <br />
            <p>{instruction}</p>
            <Button variant="danger" onClick={handleSnap}>Snap</Button>
            <br />
            <br />
            <form style={{background:"rgba(0, 0, 0, 0.3)",padding:"5px"}}>
                <label>Student ID : </label><br/>
                <input type="text" onChange={handleStudentID} value={studentID}></input>
                <br/>
                <label>Student Name : </label><br/>
                <input type="text" onChange={handleStudentName} value={studentName}></input>
                <br/>
                <br/>
                <Button onClick={handleSubmitForRecog} variant="primary">Submit</Button>
            </form></>:(
                <>
                    {responseStatus===200?<TiTick style={{color:"green",fontSize:70}}/>:<ImCross style={{color:"red",fontSize:70}}/>}
                    <p>{returnedResponse}</p>
                    <br />
                    <Button variant="dark" onClick={handleReturn}>Return</Button>
                </>)}
                <br />
                <br />
                <Button variant="danger" onClick={handleReturnToHome}>Return to homepage</Button>
        </div>
    );
}
 
export default RegisterNewFace;