import { createContext, useContext, type JSX } from "solid-js";
import { ToastStoreFactory, type ToastStore } from "./toast-store";

const ToastContext = createContext<ToastStore>();

type ToastProviderProps = {
  readonly children: JSX.Element;
};

export function ToastProvider(props: ToastProviderProps): JSX.Element {
  const store = ToastStoreFactory.create();

  return (
    <ToastContext.Provider value={store}>{props.children}</ToastContext.Provider>
  );
}

export function useToasts(): ToastStore {
  const store = useContext(ToastContext);

  if (store === undefined) {
    throw new Error("useToasts must be used inside a ToastProvider");
  }

  return store;
}
