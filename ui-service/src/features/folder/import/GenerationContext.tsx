import { createContext, useContext, type JSX } from "solid-js";
import {
  GenerationStoreFactory,
  type GenerationStore,
} from "./generation-store";
import { useToasts } from "../../notifications/ToastContext";

const GenerationContext = createContext<GenerationStore>();

export type GenerationProviderProps = {
  readonly children: JSX.Element;
};

export function GenerationProvider(
  props: GenerationProviderProps,
): JSX.Element {
  const store = GenerationStoreFactory.create(useToasts());

  return (
    <GenerationContext.Provider value={store}>
      {props.children}
    </GenerationContext.Provider>
  );
}

export function useGenerations(): GenerationStore {
  const store = useContext(GenerationContext);

  if (store === undefined) {
    throw new Error("useGenerations must be used inside a GenerationProvider");
  }

  return store;
}
