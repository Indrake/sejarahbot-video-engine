import React from "react";
import { useCurrentFrame } from "remotion";
import { narration } from "./narration";

export const Caption: React.FC = () => {
  const frame = useCurrentFrame();
  const seconds = frame / 30;

  const current = narration.find(
    (item) => seconds >= item.start && seconds < item.end
  );

  if (!current) return null;

  return (
    <div
      style={{
        position: "absolute",
        bottom: "12%",
        width: "86%",
        left: "7%",
        textAlign: "center",
        color: "white",
        fontSize: 48,
        fontWeight: "bold",
        lineHeight: 1.3,
        textShadow: "2px 3px 5px #24180f",
        backgroundColor: "rgba(45, 31, 20, 0.72)",
        padding: 22,
        borderRadius: 18
      }}
    >
      {current.text}
    </div>
  );
};
