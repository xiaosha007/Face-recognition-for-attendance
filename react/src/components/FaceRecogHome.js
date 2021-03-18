import React,{useState,useCallback,useRef} from 'react';
import CameraFrame from './CameraFrame';
import axios from 'axios';
import {TiTick} from 'react-icons/ti';
import {ImCross} from 'react-icons/im'
import { useHistory } from 'react-router-dom';
import { Button } from 'react-bootstrap';


const FaceRecogHome = () => {
    const [studentID,setStudentID] = useState("");
    const [cameraOn,setCameraOn] = useState(true);
    const [returnedResponse,setReturnedResponse] = useState();
    const [instruction,setInstruction] = useState("Please dont move for 3 seconds after you clicked the submit button");
    const [responseStatus,setResponseStatus] = useState();
    const [returnImgList,setReturnImgList] = useState([]);
    const { innerWidth: width, innerHeight: height } = window;

        
    const webcamRef = useRef(null);
    const capture = useCallback(
        () => {
            const imageSrc = webcamRef.current.getScreenshot();
            return imageSrc;
        },
        [webcamRef]
    );

    const history = useHistory();

    const goToRegisterFace = () => {
        history.push("/register-face");
    }

    const handleReturn = (e)=>{
        e.preventDefault();
        setCameraOn(true);
        setInstruction("Please hold your position for 3 seconds after you clicked the submit button");
    }
    const handleSubmitForRecog = (e)=>{
        let images = [];
        let second = 2;
        e.preventDefault();
        const interval = setInterval(function() {
            // method to be executed;
            setInstruction(second + " seconds");
            let image = capture();
            images.push(image.replace("data:image/jpeg;base64,",""));
            if(second === 0){
                setInstruction("Submitting...")
                clearInterval(interval);
                axios.post('http://localhost:5000/sign_attendance', {
                    studentID: studentID,
                    images: images,
                })
                .then(function (response) {
                    setCameraOn(false);
                    console.log(response);
                    setResponseStatus(response.data.code);
                    setReturnedResponse(response.data.message.replace(/\n/g,'<br>'));
                    setReturnImgList(response.data.data);
                })
                .catch(function (error) {
                    console.log(error);
                });
            }
            second --;
        }, 1000); 
        
    }
    const handleChange =(e)=>{
        setStudentID(e.target.value);
    }
    return (
        <div style={{textAlign:"center",padding:"30px",marginLeft:"60px",marginRight:"60px",background:"rgba(0, 0, 0, 0.3)",color:"white"}}>
            <h1 >Attendance by Face Recognition</h1>
            {cameraOn?<><CameraFrame webcamRef={webcamRef} capture={capture} windowDimensions={{width,height}}/>
            <form>
                <br/>
                <label>Student ID : </label><br/>
                <input type="text" onChange={handleChange} value={studentID}></input>
                <br/><br/>
                <Button onClick={handleSubmitForRecog}>Submit</Button>
                <p>{instruction}</p>
            </form></>:(
                <>
                    {responseStatus===200?<TiTick style={{color:"green",fontSize:70}}/>:<ImCross style={{color:"red",fontSize:70}}/>}
                    <p dangerouslySetInnerHTML={{__html:returnedResponse}}></p>
                    <br />
                    {returnImgList.map((img)=>{
                        return <div><img src={`data:image/jpeg;base64,${img}`} width={width/2} alt=""/><br/></div>
                    })}
                    <br />
                    <Button variant="dark" onClick={handleReturn}>Return</Button>
                    <br />
                </>)}
            <br/>
            <Button variant="danger" onClick={goToRegisterFace}>Register new face</Button>
        </div>
    );
}
 
export default FaceRecogHome;