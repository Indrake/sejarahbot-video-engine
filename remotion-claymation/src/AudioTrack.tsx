import React from "react";
import { Audio, staticFile } from "remotion";

export const AudioTrack: React.FC = () => {
  return (
    <Audio src={staticFile("narration.mp3")} />
  );
};
