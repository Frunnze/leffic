import { createContext, useContext, type JSX } from "solid-js";
import { AskStoreFactory, type AskStore } from "./ask-store";

const AskContext = createContext<AskStore>();

type AskProviderProps = {
  readonly children: JSX.Element;
};

export function AskProvider(props: AskProviderProps): JSX.Element {
  const store = AskStoreFactory.create();

  return (
    <AskContext.Provider value={store}>{props.children}</AskContext.Provider>
  );
}

export function useAsk(): AskStore {
  const store = useContext(AskContext);

  if (store === undefined) {
    throw new Error("useAsk must be used inside an AskProvider");
  }

  return store;
}
