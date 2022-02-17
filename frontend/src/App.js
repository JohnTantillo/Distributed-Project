import {useState,useEffect} from "react"

function App() {

  const [text,setText] = useState('')

  return (
    <div>
    <form>
        <input
          method="post"
          type='text'
          placeholder="Write text here"
          maxLength='100'
          onChange={e => setText(e.target.value)}
        />
        <button type='submit'>Write</button>
      </form>

      <button>
        Show written text
      </button>
    </div>
  );
}

export default App;
