import {Routes,Route} from 'react-router-dom';
import Homepage from './Pages/Homepage';
import SearchGame from './Pages/SearchGame'
import Gamepage from './Pages/Gamepage'

const routeSetup = () => {
    return(
        <div>
            <Routes>
                <Route exact path = '/' element={<Homepage />}/>
                <Route exact path = '/games' element={<SearchGame />}/>
                <Route path='/games/:id' element={<Gamepage />}/>
            </Routes>
        </div>
    )
}

export default routeSetup;