import { Router, Route } from "@solidjs/router"
import Home from "./pages/Home";
import FlashcardsReview from "./pages/FlashcardsReview";


function App() {
  return (
    <Router>
      <Route path="/folder/:id" component={Home} />
      <Route path="/flashcard_deck/:id" component={FlashcardsReview} />
    </Router>
  );
}

export default App;