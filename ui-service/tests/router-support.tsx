import {
  MemoryRouter,
  Route,
  createMemoryHistory,
  type MemoryHistory,
} from "@solidjs/router";
import { render } from "@solidjs/testing-library";
import type { JSX } from "solid-js";

type RenderedRoute = ReturnType<typeof render> & {
  readonly history: MemoryHistory;
};

export function renderAt(
  path: string,
  routePath: string,
  component: () => JSX.Element,
): RenderedRoute {
  const history = createMemoryHistory();
  history.set({ value: path });

  const rendered = render(() => (
    <MemoryRouter history={history}>
      <Route path={routePath} component={component} />
      <Route path="*" component={() => <span>elsewhere</span>} />
    </MemoryRouter>
  ));

  return { ...rendered, history };
}
