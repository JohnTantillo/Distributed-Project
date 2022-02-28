import {useState,useEffect} from "react"

function App() {

  const [text,setText] = useState('')

  return (
    <div>
    <form action="/textbox" method="post">
        <input
          type="text"
          name="writer"
          placeholder="Enter a game title"
          maxLength='100'
          onChange={e => setText(e.target.value)}
        />
      <button type='submit'>Write</button>
      </form>
      <form action="/printfile" method="post">
        <button>Show written text</button>
      </form>
    </div>
  );
}

export default App;
