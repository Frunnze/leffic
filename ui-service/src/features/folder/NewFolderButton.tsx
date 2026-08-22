import { Show, createSignal, type JSX } from "solid-js";
import { Icon } from "../../shared/ui/icons/Icon";
import { PromptDialog } from "../../shared/ui/PromptDialog";
import { useToasts } from "../../shared/notifications/ToastContext";
import { UnitsApi } from "./units-api";
import type { Unit } from "./unit-models";

type NewFolderButtonProps = {
  readonly folderId: string;
  readonly onFolderCreated: (created: readonly Unit[]) => void;
};

export function NewFolderButton(props: NewFolderButtonProps): JSX.Element {
  const toasts = useToasts();
  const [isDialogOpen, setDialogOpen] = createSignal(false);

  const createFolder = async (name: string): Promise<void> => {
    try {
      const created = await UnitsApi.createFolder(name, props.folderId);
      props.onFolderCreated([created]);
    } catch {
      toasts.show({
        tone: "failure",
        title: "Couldn't create the folder",
        detail: "The folder could not be created. Try again.",
      });
    }
  };

  return (
    <>
      <button
        class="btn"
        type="button"
        onClick={() => setDialogOpen(true)}
      >
        <Icon name="newFolder" size="sm" />
        New folder
      </button>

      <Show when={isDialogOpen()}>
        <PromptDialog
          title="Create a folder"
          description="Folders keep related study units together."
          label="Folder name"
          placeholder="e.g. Neuroanatomy"
          inputType="text"
          confirmLabel="Create"
          onCancel={() => setDialogOpen(false)}
          onConfirm={(name) => {
            setDialogOpen(false);
            void createFolder(name);
          }}
        />
      </Show>
    </>
  );
}
