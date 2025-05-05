import { createContext, createSignal, useContext } from "solid-js";

const NotificationContext = createContext();

export function NotificationContextProvider(props) {
  const [displayStartGenerationNotification, setDisplayStartGenerationNotification] = createSignal(false);
  const [flashcardsTaskStatus, setFlashcardsTaskStatus] = createSignal();
  const [noteTaskStatus, setNoteTaskStatus] = createSignal();

  return (
    <NotificationContext.Provider value={{
      displayStartGenerationNotification,
      setDisplayStartGenerationNotification,

      flashcardsTaskStatus,
      setFlashcardsTaskStatus,
      
      noteTaskStatus,
      setNoteTaskStatus
    }}>
      {props.children}
    </NotificationContext.Provider>
  );
}

export function useNotificationContext() {
  return useContext(NotificationContext);
}