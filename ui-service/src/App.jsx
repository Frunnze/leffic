import Home from "./components/Home";
import LeftNavBar from "./components/LeftNavBar";

function App() {
  return (
    <div class="flex text-tertiary-100">
      <LeftNavBar/>
      <Home/>
    </div>
  );
}

export default App;