import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import GlobalBackground from "./components/GlobalBackground/GlobalBackground.jsx";
import Navbar from './components/Navbar';

// Import your page components (they are in your pages folder)


function App() {
  return (
    <Router>
      {/* 1. Background sits behind everything */}
      <GlobalBackground />
      
      {/* 2. Navbar sits at the top of every page */}
      <Navbar />

      {/* 3. Routes render the specific page content below the navbar */}
    </Router>
  );
}

export default App;