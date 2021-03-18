import React,{useCallback,useRef} from 'react';
import Sketch from 'react-p5';
import Webcam from "react-webcam";


const videoConstraints = {
    facingMode: "user"
};



const CameraFrame = (props) => {
    return (
        <>
            <Webcam
                audio={false}
                height={300}
                ref={props.webcamRef}
                screenshotFormat="image/jpeg"
                width={props.windowDimensions.width/2}
                videoConstraints={videoConstraints}
            />
        </>
    );
}
 
export default CameraFrame;