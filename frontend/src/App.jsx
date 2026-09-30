import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import GlobalBackground from "./components/GlobalBackground/GlobalBackground.jsx";
import Navbar from "./components/Navbar.jsx";

import Home from "./pages/Home";
import Matchmaker from "./pages/Matchmaker";
import Config from "./pages/Config";
import IssueDetails from "./pages/IssueDetails";

function App() {
  return (
    <Router>
      <GlobalBackground />
      <Navbar />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/match" element={<Matchmaker />} />
        <Route path="/config" element={<Config />} />

        <Route path="/contrib" element={<IssueDetails />} />
        <Route path="/contrib/issue/:id" element={<IssueDetails />} />
        <Route path="/issue/:id" element={<IssueDetails />} />
      </Routes>
    </Router>
  );
}

export default App;