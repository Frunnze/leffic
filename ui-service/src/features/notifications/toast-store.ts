import { createSignal, type Accessor } from "solid-js";

export type ToastTone = "progress" | "success" | "failure";

export type Toast = {
  readonly id: string;
  readonly tone: ToastTone;
  readonly title: string;
  readonly detail: string;
};

export type ToastStore = {
  readonly toasts: Accessor<readonly Toast[]>;
  readonly show: (toast: Omit<Toast, "id">) => string;
  readonly dismiss: (id: string) => void;
};

export class ToastStoreFactory {
  private static counter = 0;

  static create(): ToastStore {
    const [toasts, setToasts] = createSignal<readonly Toast[]>([]);

    const show = (toast: Omit<Toast, "id">): string => {
      ToastStoreFactory.counter += 1;
      const id = `toast-${ToastStoreFactory.counter}`;
      setToasts((current) => [...current, { ...toast, id }]);

      return id;
    };

    const dismiss = (id: string): void => {
      setToasts((current) => current.filter((toast) => toast.id !== id));
    };

    return { toasts, show, dismiss };
  }
}
