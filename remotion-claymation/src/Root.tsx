import React from "react";
import { Composition } from "remotion";
import { ForestFireScene } from "./ForestFireScene";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="DisasterShorts"
      component={ForestFireScene}
      durationInFrames={1500}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
