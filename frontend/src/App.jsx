import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import GlobalBackground from "./components/GlobalBackground/GlobalBackground.jsx";
import Navbar from './components/Navbar';

// Import your pages
import Home from './pages/Home';
 import Matchmaker from './pages/Matchmaker'; 

function App() {
  return (
    <Router>
      {/* 1. Background sits behind everything */}
      <GlobalBackground />

      {/* 2. Navbar sits at the top of every page */}
      <Navbar />

      {/* 3. Routes render the specific page content below the navbar */}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path='/match' element={<Matchmaker/>}/>
        {/* Add your other routes here as you build them: */}
        {/* <Route path="/match" element={<Matchmaker />} /> */}
      </Routes>
    </Router>
  );
}

export default App;