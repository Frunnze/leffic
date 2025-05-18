import { Route } from "@solidjs/router"
import Home from "./pages/Home";
import FlashcardsReview from "./pages/FlashcardsReview";
import StartNotification from "./components/notifications/StartNotification";
import SuccessNotification from "./components/notifications/SuccessNotification";
import FailureNotification from "./components/notifications/FailureNotification";
import NotesReview from "./pages/NotesReview";
import { useNotificationContext } from './context/NotificationContext';
import { Match, Switch } from "solid-js";
import Login from "./pages/Login";
import SignUp from "./pages/SignUp";
import LandingPage from "./pages/LandingPage";
import FileReview from "./pages/FileReview";
import TestReview from "./pages/TestReview";
import { Router } from "@solidjs/router"


function App() {
  const { 
    displayStartGenerationNotification, setDisplayStartGenerationNotification,
    flashcardsTaskStatus, setFlashcardsTaskStatus, noteTaskStatus, setNoteTaskStatus
  } = useNotificationContext();


  return (
    <>
      <Show when={displayStartGenerationNotification()}>
          <StartNotification 
              closeNotification={() => setDisplayStartGenerationNotification(false)}
              primaryLabel="The generation started!"
              secondaryLabel="You'll be notified when done."
          />
      </Show>
      <Switch>
        <Match when={flashcardsTaskStatus() === "SUCCESS"}>
          <SuccessNotification 
                closeNotification={() => setFlashcardsTaskStatus()}
                primaryLabel="Task completed"
                secondaryLabel="Flashcards successfully created!"
            />
        </Match>
        <Match when={flashcardsTaskStatus() === "FAILURE"}>
          <FailureNotification 
            closeNotification={() => setFlashcardsTaskStatus()}
            primaryLabel="Task failure"
            secondaryLabel="The flashcards were not created. Try again!"
          />
        </Match>
      </Switch>

      <Switch>
        <Match when={noteTaskStatus() === "SUCCESS"}>
          <SuccessNotification 
                closeNotification={() => setNoteTaskStatus()}
                primaryLabel="Task completed"
                secondaryLabel="Note successfully created!"
            />
        </Match>
        <Match when={noteTaskStatus() === "FAILURE"}>
          <FailureNotification 
            closeNotification={() => setNoteTaskStatus()}
            primaryLabel="Task failure"
            secondaryLabel="The note was not created. Try again!"
          />
        </Match>
      </Switch>

      <Router>
        <Route path="/folder/:id" component={Home} />
        <Route path="/flashcard_deck/:id" component={FlashcardsReview} />
        <Route path="/note/:id" component={NotesReview} />
        <Route path="/file/:id" component={FileReview} />
        <Route path="/test/:id" component={TestReview} />
        <Route path="/login" component={Login} />
        <Route path="/sign-up" component={SignUp} />
        <Route path="/" component={LandingPage} />
      </Router>
    </>
  );
}

export default App;