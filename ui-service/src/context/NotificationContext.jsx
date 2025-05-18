import { createContext, createSignal, useContext } from "solid-js";

const NotificationContext = createContext();

export function NotificationContextProvider(props) {
  const [displayStartGenerationNotification, setDisplayStartGenerationNotification] = createSignal(false);
  const [flashcardsTaskStatus, setFlashcardsTaskStatus] = createSignal();
  const [noteTaskStatus, setNoteTaskStatus] = createSignal();
  const [testTaskStatus, setTestTaskStatus] = createSignal();

  return (
    <NotificationContext.Provider value={{
      displayStartGenerationNotification,
      setDisplayStartGenerationNotification,

      flashcardsTaskStatus,
      setFlashcardsTaskStatus,
      
      noteTaskStatus,
      setNoteTaskStatus,

      testTaskStatus,
      setTestTaskStatus
    }}>
      {props.children}
    </NotificationContext.Provider>
  );
}

export function useNotificationContext() {
  return useContext(NotificationContext);
}