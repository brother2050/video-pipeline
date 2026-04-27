/// <reference types="vite/client" />

declare module "*.css" {
  const content: { [className: string]: string };
  export default content;
}

declare module "*.svg" {
  import * as React from "react";
  export const ReactComponent: React.FunctionComponent<React.SVGAttributes<SVGElement>>;
  const content: React.FunctionComponent<React.SVGAttributes<SVGElement>>;
  export default content;
}