import {useState,useEffect} from "react"
import { Link } from 'react-router-dom';

function SearchGame() {

  const [filter, setFilter] = useState('')
  const [titles, setTitles] = useState([])
  const [game, setGame] = useState('')

//   useEffect(() => {
//     getUserList()
//     .then(response => response.json())
//     .then(data => {
//         setTitles(data.users)
//     })
//   }, [])

  const findGame = (e) => {
    e.preventDefault()
      setGame({
        search_query: e.target.value,
      })
  }
  
  return(
    <div>
      <div>
        <form onSubmit={
            (e) => 
            {e.preventDefault();
        //     getUserInfo(game.search_query)
        //     .then(response => response.json())
        //     .then(data => {
        //         setGame({
        //         //   username: data.first_name,
        //         //   email: data.email,
        //         //   from_location: data.from_location
        //         }); setFilter('');
        //     })
          }
          }>
          <input
            value={filter}
            method="get"
            type='text'
            placeholder="Search Game"
            onChange={e => { findGame(e); setFilter(e.target.value) }}
          />
          <button type='submit'>Find</button>
        </form>
        <ul>
          {titles.filter(u => u.includes(filter) || filter === '')
            .map((g) => 
              <li>
                <Link to={{
                  pathname: '/games/' + g,
                //   state: {
                //   searched_email: u,
                //   },
                  }}
                >
                  {g}
                </Link>
              </li>
            
            )}
        </ul>
      </div>
      </div>
  )
}

export default SearchGame;