import type { JSX } from "solid-js";
import { Route, Router } from "@solidjs/router";
import AssessmentPage from "./features/assessment/AssessmentPage";
import FilePage from "./features/files/FilePage";
import FlashcardsPage from "./features/flashcards/FlashcardsPage";
import FolderPage from "./features/folder/FolderPage";
import LandingPage from "./features/landing/LandingPage";
import LoginPage from "./features/authentication/LoginPage";
import NotePage from "./features/notes/NotePage";
import SignUpPage from "./features/authentication/SignUpPage";
import { Toasts } from "./features/notifications/Toasts";
import { useToasts } from "./features/notifications/ToastContext";

export function App(): JSX.Element {
  const toasts = useToasts();

  return (
    <>
      <Router>
        <Route path="/" component={LandingPage} />
        <Route path="/login" component={LoginPage} />
        <Route path="/sign-up" component={SignUpPage} />
        <Route path="/folder/:id" component={FolderPage} />
        <Route path="/flashcard_deck/:id" component={FlashcardsPage} />
        <Route path="/test/:id" component={AssessmentPage} />
        <Route path="/note/:id" component={NotePage} />
        <Route path="/file/:id/:extension" component={FilePage} />
      </Router>

      <Toasts toasts={toasts.toasts()} onDismiss={toasts.dismiss} />
    </>
  );
}
