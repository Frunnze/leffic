import type { JSX } from "solid-js";
import { Route, Router } from "@solidjs/router";
import AssessmentPage from "./features/assessment/AssessmentPage";
import FilePage from "./features/files/FilePage";
import FlashcardsPage from "./features/flashcards/FlashcardsPage";
import FolderPage from "./features/folder/FolderPage";
import LandingPage from "./features/landing/LandingPage";
import LoginPage from "./features/authentication/LoginPage";
import NotePage from "./features/notes/NotePage";
import SettingsPage from "./features/settings/SettingsPage";
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
        <Route
          path="/flashcard_deck/:id"
          component={() => <FlashcardsPage scope="flashcard_deck" />}
        />
        <Route
          path="/folder/:id/flashcards"
          component={() => <FlashcardsPage scope="folder" />}
        />
        <Route path="/test/:id" component={() => <AssessmentPage scope="test" />} />
        <Route
          path="/folder/:id/test"
          component={() => <AssessmentPage scope="folder" />}
        />
        <Route path="/note/:id" component={NotePage} />
        <Route path="/file/:id/:extension" component={FilePage} />
        <Route path="/settings" component={SettingsPage} />
      </Router>

      <Toasts toasts={toasts.toasts()} onDismiss={toasts.dismiss} />
    </>
  );
}
