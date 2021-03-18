import React from 'react';
import FaceRecogHome from './components/FaceRecogHome';
import RegisterNewFace from './components/RegisterNewFace'
import background from './assets/background.jpg';
import {BrowserRouter,Route,Switch} from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <div className="App"  style={{ backgroundImage: `url(${background})`,width:'100%',minHeight:'100vh',backgroundSize:"cover",backgroundRepeat:"no-repeat" }}>
        <Switch>
          <Route exact path='/' component={FaceRecogHome}/>
          <Route path='/register-face' component={RegisterNewFace}/>
        </Switch>
      </div>
    </BrowserRouter>
  );
}

export default App;
