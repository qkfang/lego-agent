import type { Route } from "./+types/favicon";
import { TbSocial } from "react-icons/tb";
import { renderToString } from "react-dom/server";

export async function loader({ params }: Route.LoaderArgs) {
  return new Response(renderToString(<TbSocial size={32} />), {
    status: 200,
    headers: {
      "Content-Type": "image/svg+xml",
    },
  });
}
